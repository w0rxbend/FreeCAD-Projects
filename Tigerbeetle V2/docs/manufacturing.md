# Manufacturing assumptions

The user confirms 5 mm arms and 2 mm for all three carbon plates. These are the
reference stock dimensions. Regression presets deliberately vary stock and
clearances; their evidence does not claim the altered stock was measured.

The photo-supported lower stack is rear plate 0–2 mm, arms 2–7 mm, and camera
plate 7–9 mm. Top-deck underside is 9 + H mm. H is an adjustable face clearance,
provisionally 25 mm. Six supports have length H; two rear supports have length
H + 7 mm, derived from the arm and camera-plate stock. Perspective photography
establishes arrangement, not exact standoff length.

Nominal fasteners, machining clearance, printed fit clearance and minimum edge
ligament are separate engineering parameters. Clearance is applied once. Slot
clearance denotes total width addition, so a centered joint receives half on
each side. A valid CAD solid alone does not establish fit or carbon strength.

Reference carbon minimum ligament is 1.5 mm. Purchased tubular standoffs use a
separate 1.0 mm minimum wall: the nominal 5 mm outside diameter and 3 mm bore give
exactly 1.0 mm radial wall. Carbon and tubular hardware use their respective
rules; a purchased metal tube is not assessed as a carbon cutout. Nominal M3
fastener diameter and 0.2 mm hole allowance produce 3.2 mm carbon clearance bores.

The arm root is a deliberate reconstruction departure: 35 × 29 mm instead of
the approximately 38 × 31 mm traced envelope. The larger traced envelope
intersects adjacent arms at the reconciled mounting axes. The local reduction
preserves those axes and the remaining arm dimensions. Original observations
remain unchanged, and the departure requires physical confirmation. The configured
0.2 mm arm-to-arm gap is checked against actual placed solids; a parameter change
must not assume that the nominal reference gap persists.

STEP is the canonical interchange geometry. STL and 3MF are tessellations with
explicit tolerances. Planar manufacturing SVG must remain 1:1 millimeters and
come from the same profile used for extrusion. FreeCAD documents are generated
from STEP and reopened for topology/solid-count verification.

Default tessellation uses 0.05 mm linear deflection and 0.1 radians angular
deflection. The manifest records the actual mesh settings. A dimensioned SVG is a
review drawing; use the corresponding plain profile for the manufacturing outline.
The raised deck and arm handedness must be retained when interpreting assembly
views. The Python parameter tree remains the editable model behind imported
FreeCAD solids.

Manufacturing acceptance requires valid single-solid parts, non-self-intersecting
closed profiles, correct feature counts, exact intended symmetry, aligned mounting
axes, adequate edge distances and clearance envelopes, and no unintended assembly
intersections. Any allowed contact must name its participating components and
must not excuse material overlap that would prevent physical assembly.

Default equipment checks use explicit nominal solids: 40 × 40 × 8 mm FC and ESC,
20 × 20 × 20 mm camera, and four 5 mm stack-hardware envelopes with 6 mm PCB
keepouts. Positions follow the shared stack axes and plate elevations. These
envelopes are configurable in `EquipmentParameters`; their dimensions, placement
and omissions are documented in [equipment.md](equipment.md). Side panels are not
part of the supplied three-plate reconstruction. Unmeasured camera mounts,
connectors, cabling and screw engagement require additional geometry or evidence.

The scans do not specify carbon layup, material strength, cutter process, actual
motor screw engagement or complete electronics/camera envelopes. Reports must
name the modeled assumptions and supported envelope rather than claiming
universal equipment compatibility. Physical manufacturing qualification is not
established by a software-only test run.
