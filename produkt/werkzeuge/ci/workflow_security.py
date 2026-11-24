"""Strict public-workflow allowlist, with no privileged or upload path."""
from __future__ import annotations
from pathlib import Path
import re
import yaml

CHECKOUT = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
PYTHON = "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1"
SOURCE = "${{ github.event.pull_request.head.sha || github.sha }}"
INSTALL = "python -m pip install -r produkt/werkzeuge/ci/requirements.txt -r produkt/werkzeuge/referenz/requirements.txt"
BIND = 'test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_SHA"\npython produkt/werkzeuge/ci/snapshot.py\n'
COMMANDS = {
    INSTALL, BIND, "python produkt/werkzeuge/ci/preflight.py",
    "python produkt/werkzeuge/ci/review_gate.py",
    "python produkt/werkzeuge/ci/run_suite.py produkt/werkzeuge/steuerung/tests",
    "bash produkt/werkzeuge/ci/native.sh",
}


def validate_workflow(text: str) -> dict:
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    if set(workflow) != {"name", "on", "permissions", "env", "concurrency", "jobs"}:
        raise ValueError("Unerwartete Workflowfelder")
    if workflow["on"] != {"pull_request": "", "merge_group": "", "push": {"branches": ["main"]}}:
        raise ValueError("Unerwartete Workflow-Ausloeser")
    if workflow["permissions"] != {"contents": "read"}:
        raise ValueError("Unzulaessige Workflowrechte")
    if workflow["env"] != {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1", "EXPECTED_SOURCE_SHA": SOURCE}:
        raise ValueError("Unerwartete Workflowumgebung")
    if workflow["concurrency"] != {"group": "chnobel-development-${{ github.event.pull_request.number || github.ref }}", "cancel-in-progress": "false"}:
        raise ValueError("Historische Laeufe duerfen nicht abgebrochen werden")
    if re.search(r"secrets\s*[.\[]|upload-artifact|pull_request_target|workflow_run|id-token|self-hosted", text, re.I):
        raise ValueError("Privilegierter Zugriff oder Artefaktpfad")
    jobs = workflow["jobs"]
    if set(jobs) != {"preflight", "product-check", "recovery-drill", "integration-review-block"}:
        raise ValueError("Pflichtjob fehlt oder unerwarteter Job")
    required_commands = {
        "preflight": {INSTALL, BIND, "python produkt/werkzeuge/ci/preflight.py"},
        "product-check": {BIND, "bash produkt/werkzeuge/ci/native.sh"},
        "recovery-drill": {BIND, "python produkt/werkzeuge/ci/run_suite.py produkt/werkzeuge/steuerung/tests"},
        "integration-review-block": {BIND, "python produkt/werkzeuge/ci/review_gate.py"},
    }
    for name, job in jobs.items():
        if set(job) != {"name", "runs-on", "timeout-minutes", "steps"}:
            raise ValueError("Jobabhaengigkeiten, Bedingungen und Rechte-Overrides unzulaessig")
        expected_runner = "xcode-27" if name == "product-check" else "ubuntu-24.04"
        if job["runs-on"] != expected_runner:
            raise ValueError("Falscher Runnervertrag")
        if job["timeout-minutes"] != ("40" if name == "product-check" else "15"):
            raise ValueError("Unerwartetes Jobzeitlimit")
        actions, commands = [], []
        for step in job["steps"]:
            if set(step) - {"name", "uses", "with", "run"}:
                raise ValueError("Schrittbedingung, Soft-Fail oder Umgebungsinjektion")
            if "uses" in step:
                if "run" in step:
                    raise ValueError("Mehrdeutiger Schritt")
                action = step["uses"]
                actions.append(action)
                expected_with = ({"persist-credentials": "false", "ref": SOURCE} if action == CHECKOUT
                                 else {"python-version": "3.14"} if action == PYTHON else None)
                if expected_with is None or step.get("with") != expected_with:
                    raise ValueError("Ungepinnte/unbekannte Action oder Checkout-Credentials")
            elif set(step) <= {"name", "run"} and step.get("run") in COMMANDS:
                commands.append(step["run"])
            else:
                raise ValueError("Unerlaubter Shellbefehl oder externe Aktion")
        if actions != [CHECKOUT, PYTHON] or len(commands) != len(required_commands[name]) or set(commands) != required_commands[name]:
            raise ValueError("Pflichtschritte fehlen/verdoppelt")
        if commands.index(BIND) != 0:
            raise ValueError("Quellbindung muss zuerst laufen")
    return {"jobs": sorted(jobs), "permissions": "contents:read", "artifactUploads": 0,
            "privilegedTriggers": 0, "nativeIndependent": True}


def check_workflows(root: Path) -> dict:
    paths = sorted([*(root / ".github/workflows").glob("*.yml"), *(root / ".github/workflows").glob("*.yaml")])
    if [p.name for p in paths] != ["development.yml"]:
        raise ValueError("Ungepruefte zusaetzliche Workflowdatei")
    return validate_workflow(paths[0].read_text(encoding="utf-8"))
