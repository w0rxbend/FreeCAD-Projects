# Current state

Updated 2026-09-13. Milestone: complete local model and export integration; final
independent acceptance review, clean-checkout rebuild and hosted CI remain open.

User evidence: A4 paper tracings; arms5mm, all3plates2mm. Original hashes preserved.
One source-reconciled coordinate system: +Xright,+Yfront,+Zup; motor-centroid XY.
Plate Z ranges0–2,7–9,34–36mm; top face clearanceH25mm remains photo-inferred.

Implemented: immutable parameters; shared root/stack/support interfaces; canonical
handed arm; 3 analytical symmetric plate profiles; 15 named assembled components;
actual BREP bores, symmetry, interference, arm gaps, ligaments and equipment gates;
CAD/source overlays, quantitative fit report; full CLI; all5formats and FreeCAD
save/reopen; parameter/checksum manifest; release packaging; active parent workflows.

Validation evidence so far:
- 29 assembly tests pass, including all5presets and nominal equipment envelopes.
- 54 component geometry tests passed earlier; new full-suite run in progress.
- Full actual export84artifacts, all15parts,34SVGs,FCStd15solids reopened in FreeCAD1.1.3.
- Ruff and strict mypy pass after integration fixes.
- Packaging20tests and both workflow sets pass actionlint (release agent evidence).
- Both overlays inspected. Directed source outline max1.53–3.90mm depending on part;
  circular mark max0.70mm. Root35×29 is a documented departure from traced38×31.

Latest reviewers/export/CI handoffs record exact evidence. Agent runtime status must
be re-read; listed historical names do not imply active ownership. Current goal is
full PLAN, not merely passing individual solids. No remote publication yet.

Git root is parent FreeCAD-Projects. Active workflows use tigerbeetle-v2-* names;
existing sibling tigerbee.yml preserved. Current filesystem unrestricted.
