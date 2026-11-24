"""Fail-closed Strukturpruefung; KEIN authentisierender Freigabedienst."""

from dataclasses import dataclass

from .contracts import Invalid, digest, fields, integer, text


# Vollstaendiger Phase-0-Schlussnachweis, nicht eine Vorab-Upload-Erlaubnis.
MANDATORY_JOBS = frozenset({
    "preflight", "product-check", "freeze-build", "independent-check",
    "issue-verdict", "release-internal", "reconcile", "recovery-drill",
})


@dataclass(frozen=True)
class JobRequirement:
    name: str
    issuer: str
    cases: int


@dataclass(frozen=True)
class Policy:
    candidate_digest: str
    archive_digest: str
    rules_digest: str
    issuer: str
    jobs: tuple[JobRequirement, ...]

    def __post_init__(self):
        for name in ("candidate_digest", "archive_digest", "rules_digest"):
            digest(getattr(self, name), name)
        text(self.issuer, "Erwarteter Aussteller")
        if type(self.jobs) is not tuple or not all(isinstance(j, JobRequirement) for j in self.jobs):
            raise Invalid("Unveraenderlicher Pflichtjobplan erforderlich")
        for job in self.jobs:
            text(job.name, "Pflichtjobname")
            text(job.issuer, "Erwartete Jobidentitaet")
            integer(job.cases, "Erwartete Fallzahl", 1)
        if len(self.jobs) != len(MANDATORY_JOBS) or {j.name for j in self.jobs} != MANDATORY_JOBS:
            raise Invalid("Jeder Phase-0-Pflichtjob muss vorab im Regelplan stehen")

    @classmethod
    def from_dict(cls, value):
        fields(value, {"candidate_digest", "archive_digest", "rules_digest", "issuer", "jobs"})
        if not isinstance(value["jobs"], list):
            raise Invalid("Pflichtjobplan muss eine Liste sein")
        jobs = []
        for row in value["jobs"]:
            fields(row, {"name", "issuer", "cases"})
            jobs.append(JobRequirement(row["name"], row["issuer"], row["cases"]))
        return cls(value["candidate_digest"], value["archive_digest"], value["rules_digest"],
                   value["issuer"], tuple(jobs))


@dataclass(frozen=True)
class Validation:
    checks_valid: bool
    errors: tuple[str, ...]
    release_authorized: bool = False
    authentication: str = "not_verified"

    def as_dict(self):
        return {"checks_valid": self.checks_valid, "errors": list(self.errors),
                "release_authorized": False, "authentication": "not_verified"}


def validate_report(report, policy):
    """Regelplan muss separat vertrauenswuerdig und vor dem Lauf fixiert sein.

    Gleiche Ausstellertexte sind keine Signatur-/OIDC-Pruefung. Selbst ein
    strukturell vollstaendiger Bericht autorisiert in diesem Werkzeug nichts.
    """
    if not isinstance(policy, Policy):
        raise Invalid("Expliziter vorab fixierter Regelplan erforderlich")
    errors = []
    try:
        fields(report, {"schema_version", "kind", "issuer", "candidate_digest", "archive_digest",
                        "rules_digest", "status", "executed", "jobs"})
        if type(report["schema_version"]) is not int or report["schema_version"] != 1:
            raise Invalid("Unbekannte Belegversion")
        if report["kind"] != "ci_attestation":
            raise Invalid("Lokale Simulation ist kein echter Freigabebeleg")
        if report["issuer"] != policy.issuer:
            errors.append("Unerwarteter Belegaussteller")
        for key in ("candidate_digest", "archive_digest", "rules_digest"):
            digest(report[key], key)
            if report[key] != getattr(policy, key):
                errors.append(f"Falsche Bindung: {key}")
        if report["status"] != "passed" or report["executed"] is not True:
            errors.append("Beleg ist nicht tatsaechlich ausgefuehrt und bestanden")
        if not isinstance(report["jobs"], list):
            raise Invalid("Pflichtlaufliste fehlt")
        seen = set()
        expected = {job.name: job for job in policy.jobs}
        for row in report["jobs"]:
            fields(row, {"name", "issuer", "candidate_digest", "archive_digest", "rules_digest",
                         "status", "executed", "expected_cases", "executed_cases", "passed_cases"})
            name = text(row["name"], "Jobname")
            if name in seen or name not in expected:
                raise Invalid("Doppelter oder unerwarteter Pflichtjob")
            seen.add(name)
            requirement = expected[name]
            if row["issuer"] != requirement.issuer:
                errors.append(f"{name}: falsche CI-Identitaet")
            for key in ("candidate_digest", "archive_digest", "rules_digest"):
                digest(row[key], key)
                if row[key] != getattr(policy, key):
                    errors.append(f"{name}: falsche Bindung {key}")
            if row["status"] != "passed" or row["executed"] is not True:
                errors.append(f"{name}: nicht ausgefuehrt/bestanden")
            for key in ("expected_cases", "executed_cases", "passed_cases"):
                integer(row[key], f"{name}.{key}", 1)
                if row[key] != requirement.cases:
                    errors.append(f"{name}: {key} weicht vom fixierten Regelplan ab")
        if seen != set(expected):
            errors.append("Pflichtjobs fehlen: " + ", ".join(sorted(set(expected) - seen)))
    except Invalid as exc:
        errors.append(str(exc))
    return Validation(not errors, tuple(errors))
