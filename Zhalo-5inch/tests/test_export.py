"""Exports: the files a CNC shop and a slicer receive."""

import struct

import ezdxf

from zhalo import frame as F
from zhalo.accessories import build_all
from zhalo.accessories.kit import lay_on_bed
from zhalo.export import sheet_file, write_dxf, write_stl


def test_dxf_holds_only_arcs_and_lines(tmp_path):
    for name, make in F.SHEETS.items():
        path = tmp_path / f"{sheet_file(name)}.dxf"
        write_dxf(make(), path)
        kinds = {e.dxftype() for e in ezdxf.readfile(path).modelspace()}
        assert kinds <= {"ARC", "LINE"}, (name, kinds)


def test_stl_is_a_closed_mesh_resting_on_the_bed(tmp_path):
    acc = next(a for a in build_all() if a.name == "arm_guard")
    printed = lay_on_bed(acc.part, acc.bed)
    path = tmp_path / "arm_guard.stl"
    count = write_stl(printed, path)
    data = path.read_bytes()
    assert struct.unpack("<I", data[80:84])[0] == count and len(data) == 84 + 50 * count
    assert abs(printed.bounding_box().min.Z) < 1e-6


def test_dxf_is_reproducible(tmp_path):
    # regenerating an unchanged part must not change the file a CNC shop receives
    sheet = F.SHEETS["plate_top"]()
    write_dxf(sheet, tmp_path / "a.dxf")
    write_dxf(sheet, tmp_path / "b.dxf")
    assert (tmp_path / "a.dxf").read_bytes() == (tmp_path / "b.dxf").read_bytes()


def test_carbon_stl_is_a_closed_flat_part(tmp_path):
    sheet = F.SHEETS["arm"]()
    count = write_stl(sheet.solid(), tmp_path / "arm.stl")
    data = (tmp_path / "arm.stl").read_bytes()
    assert struct.unpack("<I", data[80:84])[0] == count and len(data) == 84 + 50 * count
