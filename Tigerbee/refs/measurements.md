# Confirmed design dimensions

The user's latest instruction specifies:

- **305 mm wheelbase** between opposite motor-bore centers.
- Symmetric **X** arrangement. The current design uses a square motor layout with
  perpendicular diagonals intersecting at frame (0, 0).
- **5 mm arm thickness** for both types.
- **3 mm thickness for every other plate** (camera, rear and top).
- **6 mm outside diameter for the mounting standoffs**.

Motor centers therefore lie at **(±107.833784131, ±107.833784131) mm**. Their spacing
along each side is 215.667568262 mm. These are derived nominal dimensions, not
claims about measuring precision. The geometry audit reads the actual exported
bores, thicknesses and standoff surfaces to verify this contract.

The 305 mm design target supersedes the earlier approximate **303–304 mm** reading
of the physical frame and the previous 303.5 mm reconstructed layout. The original
reading is retained as historical evidence, alongside the superseded 330 mm and
295 mm photo labels. It no longer acts as the current wheelbase acceptance gate.

Tigerbee.FCStd and the supplied arm/camera 3MF files remain the foundation for
shapes and openings, above the pen scans. New mounting locations and localized
root/plate relief implement the user's explicit 305 mm X revision.

The top-plate underside remains at the existing nominal Z=35 mm because no new
height was specified. With 3 mm lower plate, 5 mm arms and 3 mm camera plate, six
standoffs are **24 mm** long and two are **32 mm**. Their 3.2 mm bore is the modeled
clearance for nominal M3 axes; thread and end-bracket details are not included.

## Equipment information supplied after the mounting handoff

The user has now specified a **21 mm FPV camera**, **2807 1300KV motors**,
an **analog FPV VTX antenna**, and a **915 MHz receiver antenna**. The 21 mm
camera dimension is being used as housing width for the mounting study; camera
height, depth, lens envelope and side-screw details have not been supplied.

Motor manufacturer/model, mounting pattern and allowed screw engagement remain
unconfirmed. Antenna frequency/type does not yet specify a mounting envelope:
VTX connector style and RX antenna shape/dimensions are still needed. These
equipment choices supersede the earlier request for all equipment categories,
while their remaining mechanical details are still open.
