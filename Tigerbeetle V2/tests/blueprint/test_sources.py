"""Changes to source evidence must be caught before geometry generation."""

from pathlib import Path

import pytest

from fpv_frame.blueprint.measurements import inspect_sources, verify_sources

ROOT = Path(__file__).resolve().parents[2]


def test_original_scans_are_preserved_and_have_native_dimensions() -> None:
    report = inspect_sources(ROOT)
    assert set(report) == {"Scan_1.jpeg", "Scan_2.jpeg"}
    assert all(scan["size_px"] == [2480, 3508] for scan in report.values())
    for name in report:
        assert (ROOT / name).read_bytes() == (ROOT / "references/source" / name).read_bytes()


def test_source_corruption_is_fatal(tmp_path: Path) -> None:
    source = tmp_path / "references/source"
    source.mkdir(parents=True)
    (source / "Scan_1.jpeg").write_bytes(b"damaged")
    with pytest.raises(ValueError, match="checksum"):
        verify_sources(tmp_path)


def test_missing_source_is_fatal(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing"):
        verify_sources(tmp_path)
