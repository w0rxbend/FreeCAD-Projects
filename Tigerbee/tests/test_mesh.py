import pytest

from tigerbee.mesh import audit_mesh

VERTICES = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
FACES = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]


def test_closed_tetrahedron_passes():
    assert audit_mesh(VERTICES, FACES)["valid"]


def test_missing_face_is_not_watertight():
    report = audit_mesh(VERTICES, FACES[:-1])
    assert not report["valid"]
    assert report["boundary_edges"] == 3


def test_reversed_face_is_detected():
    report = audit_mesh(VERTICES, [FACES[0][::-1], *FACES[1:]])
    assert not report["valid"]
    assert report["winding_errors"] == 3


def test_degenerate_face_is_detected():
    report = audit_mesh(VERTICES, [*FACES, (0, 0, 1)])
    assert not report["valid"]
    assert report["degenerate_faces"] == 1


def test_two_disconnected_solids_fail_component_contract():
    vertices = VERTICES + [(x + 3, y, z) for x, y, z in VERTICES]
    faces = FACES + [tuple(i + 4 for i in face) for face in FACES]
    report = audit_mesh(vertices, faces)
    assert not report["valid"]
    assert report["components"] == 2


def test_invalid_indices_fail_with_useful_error():
    with pytest.raises(ValueError, match="vertex index"):
        audit_mesh(VERTICES, [(0, 1, 99)])
