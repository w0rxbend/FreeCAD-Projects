# Tigerbee mounting interfaces and equipment handoff

This schedule describes the nominal CAD at commit `00fb945`, using the current
[assembly report](../exports/assembly/assembly-report.json),
[shared interface definitions](../src/tigerbee/layout.py) and accessory reports.
Dimensions are in millimeters. X=0 is the symmetry plane, positive Y is the
camera/front end, and Z=0 is the underside of the lower rear plate. Coordinates
below are rounded for reading; STEP, source definitions and the JSON reports
retain full precision. Structural coordinates are under
`geometry_audit.fastener_axes` in the assembly report.

## Components already modeled

| Component | Quantity | Current nominal interface |
| --- | ---: | --- |
| Arm type 1 | 2 | Front mirrored pair; 5 mm stock |
| Arm type 2 | 2 | Rear mirrored pair; 5 mm stock |
| Camera, rear and top plates | 1 each | 3 mm stock |
| Short standoffs | 6 | Length 24; outside Ø6; modeled through bore Ø3.2 |
| Long standoffs | 2 | Length 32; outside Ø6; modeled through bore Ø3.2 |
| Protector feet | 4 | One of each exported type/hand; 2 mm additional motor-screw grip |
| GoPro holder | 1 | Four M3 base axes; one transverse M5 pivot |

The standoffs are modeled as tubes. Internal threads, threaded inserts, studs,
screw heads, nuts and washers have not been modeled or selected.

## Frame axes and Z stack

Each `±X` row below represents two axes. The first four rows are the eight arm
mounting axes; four of these also carry standoffs. Thus there are twelve distinct
structural XY axes in total, plus the four central electronics axes.

| Interface | X | Y | Modeled layers along axis | Full Z span |
| --- | ---: | ---: | --- | ---: |
| Front inner arm clamp | ±25.596122 | 21.715560 | Rear plate 0–3; arm 3–8; camera plate 8–11 | 11 |
| Front outer arm clamp / standoffs 03–04 | ±23.732967 | 35.309444 | Rear plate 0–3; arm 3–8; camera plate 8–11; standoff 11–35; top plate 35–38 | 38 |
| Rear inner arm clamp | ±26.556280 | −20.043250 | Rear plate 0–3; arm 3–8; camera plate 8–11 | 11 |
| Rear outer arm clamp / standoffs 05–06 | ±24.756016 | −33.086401 | Rear plate 0–3; arm 3–8; camera plate 8–11; standoff 11–35; top plate 35–38 | 38 |
| Front-tip standoffs 01–02 | ±19.250000 | 108.750000 | Camera plate 8–11; standoff 11–35; top plate 35–38 | 30 |
| Rear-tip standoffs 07–08 | ±16.500000 | −94.000000 | Rear plate 0–3; standoff 3–35; top plate 35–38 | 38 |
| Central electronics, four axes | ±15.250000 | ±15.250000 | Rear plate 0–3; open gap 3–8; camera plate 8–11 | 11 |

Every structural bore above is Ø3.2 in the current model; the fit validator uses
a Ø3 shaft witness. The negative-X member has the first ID in each standoff pair.

**The full Z span is not a screw-length specification.** A bolt passing through
a tube and nut, and separate screws engaging a threaded standoff, have different
grip and engagement requirements. The 11 mm arm clamp contains 3+5+3 mm of
material. At the electronics axes, the same 11 mm envelope contains only two
3 mm plates and a 5 mm gap. The existing root notches prove clearance for the
shaft; they do not establish clearance for a spacer, nut or screw head there.
Define the electronics fastening arrangement before tightening across that gap.

## Accessory interfaces

| Interface | Existing CAD dimensions | Information still needed |
| --- | --- | --- |
| GoPro base | Axes (±28,58) and (±27,91); Ø3.3 bores; Ø6.6 counterbores; 2 mm base floor above 3 mm carbon; Ø4.8 locating bosses enter carbon 2 mm | Actual M3 head, washer and nut envelopes and selected engagement |
| GoPro pivot | Axis along X at Y=74.5, Z=56 in the default assembly; Ø5.5 bore; three fingers with 3.2 mm gaps; nominal 8 mm AF metal nut in an 8.4 mm AF × 4.2 mm pocket | Exact camera body or cage; actual pivot bolt and nut; required tilt range |
| Protector feet | Four source motor slots retained; 2 mm mounting floor below 5 mm carbon; 6.6 mm recessed head-access channels | Motor model, screw pattern, thread depth and head dimensions |
| Forward large equipment pattern | X=±15.25; Y=45.75/76.75; 30.5 × 31 mm spacing; camera plate Z=8–11 | Board pattern, underside components and fastener access |
| Forward small equipment pattern | X=±10; Y=51.25/71.25; 20 × 20 mm spacing; camera plate Z=8–11 | Board pattern, underside components and fastener access |
| FPV-camera mount | Front supports at X=±19.25, Y=108.75; space between plate faces Z=11–35 | Camera width/height/depth; side-hole positions and thread; lens protrusion; tilt range; rear cable exit |
| Rear equipment mount | Rear supports at X=±16.5, Y=−94; space between plate faces Z=3–35 | Antenna/connector model, attachment envelope, locknut and cable-exit clearance; power connector type and retention method |

The 24/32 mm face separation is a local frame dimension, not proof that a camera
or connector fits the entire opening. Their bodies may reach into plate outlines,
standoffs or cables. Registration-boss length overlaps the carbon thickness and
must not be added again to the GoPro base screw grip. Protector screw grip is
7 mm before motor thread engagement, excluding any additional washer.
The source motor slots are not a verified catalogue bolt pattern; compare the
selected motor drawing with its corresponding exported arm and protector.

## Next input and work

The next equipment-dependent modeling step needs the selected **FPV camera,
motor, antenna and power connector**. Manufacturer model names are sufficient
when their drawings give the relevant dimensions; otherwise the dimensions in
the table above are needed. For the GoPro holder, identify the camera/cage too.

With those interfaces known, model camera/end brackets and the selected hardware,
then check body tilt, cable exits, screw/nut access and interference in the full
assembly. Material/layup, machining tolerances and a manufactured fit/load trial
remain required for the physical production objective recorded in
[the design contract](../tasks/plan.md). No screw lengths or material strength
are inferred from the photographs.
