"""Read-only access to the immutable blueprint evidence."""

from hashlib import sha256
from pathlib import Path
from typing import TypedDict

from PIL import Image

SOURCE_HASHES = {
    "Scan_1.jpeg": "bf26be9035026002362046d18933f9032b9989aa3b0f0557132eea178eb3017e",
    "Scan_2.jpeg": "dc9a162303b5aac7b0e97a9b7a69105cf389d0419af6249525085e45f4241556",
}


class SourceInfo(TypedDict):
    sha256: str
    size_px: list[int]
    bytes: int


def verify_sources(root: Path) -> None:
    """Reject missing or altered originals before interpreting any measurements."""
    for name, expected in SOURCE_HASHES.items():
        path = root / "references" / "source" / name
        if not path.is_file():
            raise ValueError(f"Blueprint source missing: {path}")
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Blueprint source checksum mismatch: {path}")


def inspect_sources(root: Path) -> dict[str, SourceInfo]:
    """Return verified native raster metadata, without assuming a physical scale."""
    verify_sources(root)
    result: dict[str, SourceInfo] = {}
    for name, digest in SOURCE_HASHES.items():
        path = root / "references" / "source" / name
        with Image.open(path) as source:
            result[name] = {
                "sha256": digest,
                "size_px": list(source.size),
                "bytes": path.stat().st_size,
            }
    return result
