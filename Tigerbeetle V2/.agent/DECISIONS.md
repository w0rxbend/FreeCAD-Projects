# Decisions

- 2026-09-13: Implement the referenced plan with its required specialist swarm.
  The four available slots permit three specialists plus the orchestrator.
- Use explicit non-overlapping file ownership in the shared workspace. The
  parent Git repository and protected local metadata prevent unapproved worktree
  mutations; specialists must not commit or modify another owner's files.
- Preserve raster observations separately from inferred physical dimensions.
  A familiar-looking bolt pattern is a hypothesis until reconciled/reviewed.
- Use Python 3.12 and build123d 0.11 with a uv lock; keep build123d authoritative.
- 2026-09-13: User confirmed arm thickness 5 mm and plate thickness 2 mm.
- 2026-09-13: User assembly photo is authoritative for interpreting plate order;
  preserve at references/assembly/user-assembly.png. Its perspective is not an
  exact standoff-length measurement.
- 2026-09-13: Independent review supports provisional reconstruction at roughly
  11.8 px/mm using nested 20/30.5 mm hypothesis. Motor marks support a 19 mm
  opposite-hole distance (bolt circle), not a 19 mm square.
- 2026-09-13: Reconciliation corrects earlier standards orientation hypothesis:
  all three plates map in the same longitudinal scan direction.
- 2026-09-13: Git metadata is writable in current environment; bootstrap committed
  in parent feature branch, restricted to V2 files. Earlier metadata blocker is
  superseded by successful git add/commit evidence.
- 2026-09-13: A4 tracing provenance supersedes the earlier unknown-scale status.
  Retain independent raw observations while using full-page calibration.
- 2026-09-13: One shared layout owns all four handed arm placements, structural
  holes and eight support axes. Bottom Z0; reference plate ranges 0–2, 7–9, 34–36.
- 2026-09-13: Canonical root envelope35×29mm is an explicit engineering change
  from traced≈38×31mm; original dimensions remain in measurement evidence.
- 2026-09-13: Purchased standoffs use hardware_wall_minimum1.0mm; carbon profiles
  retain edge_minimum1.5mm. Runtime enforces actual arm-to-arm general clearance.
- 2026-09-13: Default assembly validation includes parameterized nominal equipment
  solids; categories and their evidence remain explicit, with side panels N/A.
- 2026-09-13: Drawing and selected-part CLI defaults use separate output directories
  to preserve a prior complete export. Manifest snapshots include parameter hashes.
