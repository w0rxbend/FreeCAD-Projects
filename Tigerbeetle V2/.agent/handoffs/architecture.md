# Architecture foundation handoff

STATUS: Foundation implemented and frozen for independent review; detailed profile and mechanical-layout work remains.

FILES CHANGED:
- `docs/architecture.md`
- `src/fpv_frame/parameters/{__init__,_validation,evidence,frame,arms,plates,mounting,hardware,manufacturing,presets}.py`
- `src/fpv_frame/geometry/{datums,patterns,interfaces}.py`
- `tests/unit/test_parameters.py`
- `tests/interfaces/test_shared_interfaces.py`
- `.agent/handoffs/architecture.md`

RESULT:
Immutable parameter hierarchy for the actual three source-identified plates and one canonical arm; semantic profile dimension contracts; pure planar transforms with actual reflection; shared hole, arm-root, plate and tab-slot interface primitives; five explicit development presets. Per-part independent profile scaling was removed before review because mating interfaces must own their positions.

MEASUREMENTS/DECISIONS:
- Confirmed user values: arm thickness 5 mm, plate thickness 2 mm, with known/direct_measurement evidence.
- Source IDs: scan1_body, scan2_broad, scan2_long. Physical roles from reviewed user photo: main/camera plate, rear bottom plate, raised lattice deck respectively.
- Vertical lower faces: rear plate=0; arm=rear thickness; main=rear+arm; top=main upper face+H.
- H=25 mm is an explicit engineering assumption, not a photo measurement. Six short supports H, two rear supports H+main thickness+arm thickness.
- +Y front is camera fork/decreasing source v; final XY pixel-to-frame transform belongs to combined calibration/mechanical layout.
- Canonical arm origin=root-hole midpoint; +Y toward motor. Reflect local X then rotate then translate. No longitudinal arm symmetry asserted.
- 19 mm motor bolt-circle diameter remains a hypothesis; it never means 19 mm square side.
- Slot clearance is total dimension addition, not per-side offset.

ASSUMPTIONS:
Unverified fastener diameter, motor pattern/bore, fit allowances and top clearance remain provisional. A4 provenance is known; calibration still assumes whole-page image and no later per-component resizing. Thickness variants in min/max presets explicitly reset their measurement evidence. Dataclass replacement of a known dimension must update provenance.

VALIDATION EXECUTED:
- Wrote tests first; initial 2 missing-module collection failures, then green implementation.
- Added thickness/vertical/profile tests first; observed 3 failures before implementing them.
- `uv run pytest -q`: 47 passed (includes prior calibration tests).
- `uv run ruff check src/fpv_frame/parameters src/fpv_frame/geometry tests/unit tests/interfaces`: passed.
- `uv run mypy src/fpv_frame/parameters src/fpv_frame/geometry`: passed (13 source files).
- Inspected user photo and read both independent scan handoffs, standards handoff and reconciler updates.

KNOWN LIMITATIONS:
Profile parameters deliberately remain None in presets until geometry specialists populate semantic dimensions from combined measurements. No placeholder solid fallback is allowed. AssemblyLayout remains None until concrete shared XY relationships are accepted. This is a tested foundation, not proof of geometric fidelity or assembly/manufacturing readiness. No commits or pyproject changes made.

FOLLOW-UP TASKS:
1. Independent architecture review and acceptance.
2. Mechanical specialist owns concrete shared XY definition: one nominal root pitch, four canonical-arm placements, plate feature membership, and eight standoff axes/elevations. Primitives here are infrastructure, not acceptance of unresolved pixel-hole mappings.
3. Geometry specialists populate ArmProfileParameters / PlateProfileParameters from named reconciled observations, with minimal analytical geometry; no raw raster contour fallback. Extend profile fields if the actual outline requires semantic transitions.
4. Test shared interfaces under changed primary dimensions; add collision/clearance checks to establish supported parameter ranges.
5. Implement profiles/parts/assembly/exporters downstream and verify full PLAN gates.


## Retrospective handoff audit — 2026-09-13

This addendum was written after the original task. It preserves the observations
and test results above; it does not attribute later knowledge to the original
reviewer. Current disposition is indexed in [handoff-index.md](handoff-index.md).
Later evidence is in [acceptance-review.md](acceptance-review.md), the maintained
[reconstruction guide](../../docs/blueprint-reconstruction.md), and
[current state](../STATE.md). Historical follow-ups are not automatically current
blockers; use those records to determine which were completed or remain open.

The original foundation-stage `None` profile/placement statements describe that earlier implementation. The concrete model now builds named shared layouts and manufacturing profiles; see current state and acceptance review. The legacy `assembly` override remains unused, distinct from the implemented derived layout.
