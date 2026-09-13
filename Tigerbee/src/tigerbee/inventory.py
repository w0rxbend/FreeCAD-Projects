"""Keep committed CAD outputs associated with the source files that generated them."""

import hashlib
import json
from importlib.resources import files
from pathlib import Path


def source_digest() -> str:
    root = Path(str(files("tigerbee")))
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.suffix in (".py", ".json"):
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def write_inventory(directory: Path) -> None:
    current_source = source_digest()
    reports = list((directory / "parts").glob("*.json"))
    reports.append(directory / "assembly/assembly-report.json")
    for path in reports:
        report = json.loads(path.read_text())
        if report.get("source_sha256") != current_source:
            raise ValueError(
                f"{path} is stale; rebuild components and assembly before native export"
            )
        for name, expected in report.get("file_sha256", {}).items():
            if hashlib.sha256((path.parent / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"Generated file changed since build: {name}")
    included = {".step", ".stl", ".3mf", ".FCStd", ".svg", ".dxf", ".glb", ".json"}
    hashes = {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.suffix in included and path.name != "manifest.json"
    }
    manifest = {"source_sha256": current_source, "files": hashes}
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def verify_inventory(directory: Path) -> int:
    from tigerbee.models import PARTS

    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["source_sha256"] != source_digest():
        raise ValueError("CAD sources changed; regenerate and commit the exports")
    required = [f"parts/{name}.{suffix}" for name in PARTS for suffix in ("3mf", "stl", "FCStd")]
    required += [f"assembly/tigerbee-assembly.{suffix}" for suffix in ("3mf", "stl", "FCStd")]
    for name in required:
        if name not in manifest["files"]:
            raise ValueError(f"Required committed export missing from manifest: {name}")
    for name, expected in manifest["files"].items():
        path = directory / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Export is missing or changed: {name}; regenerate the output set")
    return len(manifest["files"])
