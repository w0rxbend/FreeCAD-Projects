# Motor interface study for the supplied 2807 1300KV specification

The user specified motor size and KV, without a manufacturer/model. These data
do not select a mounting pattern or permissible screw engagement. As an example,
[FT's own 2807 1300KV page](https://ft.systems/en/motor-for-fpv-drone-2807-1300kv/)
describes four M3 fasteners on a Ø19 mm pattern. This example is not an equipment
selection for Tigerbee, and a 19 mm bolt circle differs from a 19 mm square.

The [STEP-based geometric study](motor-2807-study.json) samples a hypothetical
four-shaft Ø19 mm bolt circle, with Ø3 mm shafts, through each existing arm's
actual motor openings. Rotation phases 40–50° were sampled at 0.25° intervals.
The best sampled phase still leaves some shaft area outside the openings:
0.133386 mm² maximum for type 1, and 0.091180 mm² for type 2.

These results do not prove incompatibility with an unidentified motor or every
possible placement. They show why the traced motor openings alone cannot certify
an ideal four-screw mounting interface. The original source slots have small
positional irregularities and nominal 3 mm width. Confirm the selected motor
drawing before regularizing the axes or adding machining clearance; then repeat
the actual-solid shaft/head tests through both carbon and protector.

The current arm and protector geometry remains unchanged. The protector adds
2 mm grip to the 5 mm arm; actual motor thread engagement is still needed to
select screw length.
