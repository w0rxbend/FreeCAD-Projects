"""Source-fitting TPU motor-pad bumpers with integral flat landing feet.

The arm underside is Z=0 and the motor axis is X=Y=0. All offsets are in
millimeters. Print exports translate the foot to Z=0 without rotating the part.
"""

from dataclasses import dataclass
from math import isfinite

from build123d import Face, Part, Plane, Pos, Rectangle, extrude, loft, offset

from tigerbee.models import build_profile
from tigerbee.references import ARM_THICKNESS_MM


@dataclass(frozen=True)
class ProtectorParameters:
    drop: float = 12.0
    clearance: float = 0.25
    wall: float = 2.0
    flange: float = 2.0

    def validate(self) -> None:
        ranges = {"drop": (8, 20), "clearance": (0.1, 0.6), "wall": (1.5, 3), "flange": (1.5, 3)}
        for name, (low, high) in ranges.items():
            value = getattr(self, name)
            if not isfinite(value) or not low <= value <= high:
                raise ValueError(f"{name} must be finite and between {low} and {high} mm")


DEFAULT_PROTECTOR = ProtectorParameters()
PROTECTORS = tuple(
    f"arm-type-{kind}-protector-{side}" for kind in (1, 2) for side in ("right", "left")
)


def _up(face: Face) -> Face:
    return face if face.normal_at().Z > 0 else -face


def _offset(face: Face, distance: float) -> Face:
    faces = offset(_up(face), amount=distance).faces()
    if len(faces) != 1 or not faces[0].is_valid:
        raise ValueError("Protector offset must form one valid face")
    return _up(faces[0])


def motor_openings(arm: str) -> list[Face]:
    """Six actual source openings: four motor slots, shaft bore and tip window."""
    return [_up(Face(w)) for w in build_profile(arm).inner_wires() if w.center().Y > -30]


def build_protector(
    arm: str, parameters: ProtectorParameters = DEFAULT_PROTECTOR, *, mirror: bool = False
) -> Part:
    parameters.validate()
    if arm not in ("arm-type-1", "arm-type-2"):
        raise ValueError("A protector requires arm-type-1 or arm-type-2")
    profile = build_profile(arm)
    filled = _up(Face(profile.outer_wire()))
    # Clip behind the motor pad, leaving an open throat for the unchanged shaft.
    cropped = filled & (Pos(0, 33) * Rectangle(200, 100))
    if cropped is None or len(cropped.faces()) != 1:
        raise ValueError("Motor pad crop must form one face")
    pad = _up(cropped.faces()[0])
    outer = _offset(pad, parameters.clearance + parameters.wall)
    bottom = _offset(pad, parameters.clearance)
    shoulder_z = -parameters.flange - 2
    body = loft([Pos(0, 0, -parameters.drop) * bottom, Pos(0, 0, shoulder_z) * outer], ruled=True)
    body += Pos(0, 0, shoulder_z) * extrude(outer, amount=ARM_THICKNESS_MM - 0.2 - shoulder_z)
    # Clearance follows the complete arm, so the rear wall cannot block insertion.
    cavity = extrude(_offset(filled, parameters.clearance), amount=6)
    body -= cavity
    for hole in motor_openings(arm):
        center = hole.center()
        is_slot = abs(center.X) > 4 and abs(center.Y) < 10
        throat = _offset(hole, 0.2 if is_slot else 0.25)
        body -= Pos(0, 0, -parameters.drop) * extrude(throat, amount=parameters.drop + 6)
        if is_slot:
            # Original 3 mm slot + 1.8 mm each side = 6.6 mm head/tool channel.
            head = _offset(hole, 1.8)
            body -= Pos(0, 0, -parameters.drop) * extrude(
                head, amount=parameters.drop - parameters.flange
            )
    if mirror:
        body = body.mirror(Plane.YZ)
    body.label = f"{arm}-protector-{'left' if mirror else 'right'}"
    if not body.is_valid or len(body.solids()) != 1 or body.volume <= 0:
        raise ValueError("Protector must be one valid connected solid")
    return body
