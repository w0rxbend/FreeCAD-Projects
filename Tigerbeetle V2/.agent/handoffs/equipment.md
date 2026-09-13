# Equipment clearance implementation handoff

Implemented in owned files only:

- `src/fpv_frame/parameters/equipment.py`: immutable configurable nominal FC, ESC,
  camera, board spacing, stack hardware, PCB keepouts and required clearance.
  Dimensions are finite positive; PCB keepout must provide radial clearance.
  Provenance explicitly says engineering assumption, not user-confirmed hardware.
- `src/fpv_frame/validation/equipment.py`: API
  `design_equipment_envelopes(model, parameters) -> tuple[ClearanceEnvelope, ...]`.
  Generates FC/ESC/camera plus four named stack hardware proxies. Board bore and
  hardware axes derive from shared `central_stack_square`. PCB footprint must
  contain full keepout circles. Z comes from the camera plate upper face, and XY
  from shared layout datums. Geometry is assessed by the existing solid-distance
  and overlap clearance gate; this factory does not alter frame production parts.
- `tests/assembly/test_equipment.py`: 12 passing tests covering nominal fit,
  reference elevations, oversized FC/camera collisions, lowered-top collision,
  changed stack pitch and bore/hardware separation, invalid dimensions, radial
  clearance and mounting-keepout containment.
- `docs/equipment.md`: baseline values, provenance, assessment bounds and explicit
  side-panel N/A justification (no scanned side-panel part supplied).

Root integration remaining: add `FrameParameters.equipment` default factory;
invoke envelope factory in normal clearance reporting; report the design-envelope
qualification and side panels as N/A instead of claiming measured compatibility.
No git operations performed.

Validation: `.venv/bin/pytest -q tests/assembly/test_equipment.py` → 12 passed in
11.55 seconds. Ruff on all three Python files passed. Mypy on both source files
passed. Root runs final full integration suite.

Collision tests use FC 80×80 and camera 50×40 footprints. Width-only enlargement
does not reach longitudinal standoffs and can legitimately fit the open frame.
