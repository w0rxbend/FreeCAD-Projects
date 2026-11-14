"""Tiger Beetle 7": the owner's frame, rebuilt from the A4 sheets it was traced on.

trace.py     scans -> data/reconstruction.json (outlines, cut-outs, holes, how well they agree)
model.py     the decisions on top of the tracing (datum, hole sizes, matched bolts, arm placement)
frame.py     the carbon parts and standoffs as solids
overlay.py   the model drawn back onto the scans
checks.py    fidelity to the tracing, and whether the parts go together
accessories  the printed kit

The renders, exports and print rules are shared with the other frames of this repository (the
`zhalo` package); the geometry is this frame's own.
"""

from zhalo import design

design.NAME = "Tiger Beetle 7-inch"
design.SLUG = "tigerbeetle"
design.DOCUMENT = "Tigerbeetle-7inch"
design.EXTRA_COLORS.update(
    accent=(0.98, 0.55, 0.05),  # tiger orange
    tpu=(0.12, 0.12, 0.13),
    aluminium=(0.80, 0.55, 0.10),
)
