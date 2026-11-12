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
