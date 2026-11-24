"""Fail-closed binding of diagnostic inputs; never imports moving branches."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = Path(__file__).with_name("native-contract.json")
OWNED = (".github/workflows/", "produkt/werkzeuge/ci/")


def git(*args: str, root: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def check_paths(paths: list[str]) -> None:
    for path in paths:
        if path != "docs/rechteverzeichnis.md" and not path.startswith(OWNED):
            raise ValueError(f"Schreibgrenze verletzt: {path}")
        if ".." in Path(path).parts or "\\" in path:
            raise ValueError("Nichtkanonischer Pfad")


def verify_sources(binding: dict, root: Path = ROOT) -> dict:
    verified = []
    for source in binding["sources"]:
        path = source["path"]
        tree = git("rev-parse", "HEAD:" + path, root=root).decode().strip()
        if tree != source["tree"]:
            raise ValueError(f"Snapshot-Tree abweichend: {path}")
        entries = git("ls-tree", "-rz", "HEAD", "--", path, root=root).split(b"\0")
        expected_files = set()
        for entry in filter(None, entries):
            metadata, name = entry.split(b"\t", 1)
            mode, kind, oid = metadata.decode().split()
            rel = name.decode("utf-8")
            expected_files.add(rel)
            p = root / rel
            if kind != "blob" or mode not in {"100644", "100755"} or p.is_symlink():
                raise ValueError(f"Unerwarteter Snapshot-Dateityp: {rel}")
            raw = p.read_bytes()
            actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if actual != oid:
                raise ValueError(f"Snapshot-Bytes abweichend: {rel}")
        actual_files = {p.relative_to(root).as_posix() for p in (root / path).rglob("*") if p.is_file()}
        if actual_files != expected_files:
            raise ValueError(f"Snapshot-Dateiinventar abweichend: {path}")
        verified.append({**source, "verifiedFiles": len(expected_files)})
    return {"sources": verified}


def inventory(root: Path = ROOT) -> dict:
    groups = {}
    for lane, directory, pattern in (
        ("packages", "produkt/Packages/Tests", r"@Test\s+(?:@MainActor\s+)?func\s+(\w+)\s*\("),
        ("swiftdata", "produkt/App/ChnobelTests", r"@Test\s+(?:@MainActor\s+)?func\s+(\w+)\s*\("),
        ("ui", "produkt/App/ChnobelUITests", r"\bfunc\s+(test\w+)\s*\("),
    ):
        files = {}
        names = []
        for path in sorted((root / directory).rglob("*.swift")):
            text = path.read_text(encoding="utf-8")
            selected = re.findall(pattern, text)
            if selected:
                files[path.relative_to(root).as_posix()] = selected
                names.extend(selected)
        if not names or len(set(names)) != len(names):
            raise ValueError(f"Leeres/mehrdeutiges Testinventar: {lane}")
        groups[lane] = {"expected": len(names), "files": files, "names": sorted(names)}
    return groups


def verify(binding: dict | None = None, root: Path = ROOT) -> dict:
    binding = contract() if binding is None else binding
    report = verify_sources(binding, root)
    actual = inventory(root)
    if actual != binding["tests"]:
        raise ValueError("Vorab gebundenes natives Testinventar abweichend")
    report["expected"] = {key: value["expected"] for key, value in actual.items()}
    report["checkoutSha"] = git("rev-parse", "HEAD", root=root).decode().strip()
    return report


def check_local_scope(binding: dict, root: Path = ROOT) -> None:
    if git("branch", "--show-current", root=root).decode().strip() != binding["branch"]:
        raise ValueError("Falscher Arbeitsbranch")
    paths = git("diff", "--name-only", binding["candidate"], root=root)
    paths += git("ls-files", "--others", "--exclude-standard", root=root)
    check_paths(paths.decode("utf-8").splitlines())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-inputs", type=Path)
    args = parser.parse_args()
    binding = contract()
    if args.local_inputs:
        original = json.loads(args.local_inputs.read_text(encoding="utf-8"))
        if any(binding.get(k) != v for k, v in original.items()):
            raise ValueError("Abweichung vom extern gebundenen Snapshotinput")
        check_local_scope(binding)
    print(json.dumps(verify(binding), sort_keys=True))
