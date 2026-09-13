# Reference fidelity review — 2026-09-13

Independent agents compared the four original user images, the preserved CAD and
traced profiles, and current generated geometry. The review found and restored
four omitted top-plate side tabs. Their nominal centers are Y=−15 and 12 mm;
each projects 3 mm from X=±22 mm, with an R2 crown and R1 tangent root arcs.
The original asymmetric tracing remains preserved as reference evidence.

| Requirement | Current evidence | Result |
| --- | --- | --- |
| Retain the reference shapes while enforcing symmetry | [Before/after and tracing comparison](top-tabs-comparison.svg), inspected visually against original images | Four missing tabs restored; other departures follow the saved CAD authority and 305 mm revision |
| Preserve existing holes and interfaces | [Top Boolean audit](top-tabs-review.json) | All 30 openings unchanged; zero material removed; four equal additions totaling 128.548668 mm³ |
| Exact plate symmetry and smooth analytic outlines | 25 plate tests, complete-solid reflection and perimeter tangent checks | Pass |
| True-X 305 mm layout, shared axes, stock and root fit | Fresh [assembly report](../../exports/assembly/assembly-report.json) from `tigerbee assembly --require-fit` | Pass; no positive-volume component interference |
| Preserve the complete assembly and accessories | [Reopened 20-solid STEP comparison](top-tabs-assembly-audit.json) | Every solid valid; only the top plate changed; other 19 solids have zero difference within 0.0001 mm³ |
| Functional GoPro pivot geometry | [Holder fit report](../../exports/accessories/top-plate-gopro-holder.json), removed-bearing and blocked-nut mutation tests | All three bearing bands and nut wall required; nominal nut and axle remain clear |
| Deliver complete, current export set | [Manifest](../../exports/manifest.json), `tigerbee verify-exports`, independent missing-file tests | All 87 files present and hashed against current sources; all 87 individually tested for omission from disk and manifest |
| Reopen native deliverables | [Native report](../../exports/native-report.json) | All 13 FCStd documents valid, with expected solid counts |
| Software checks | `uv run pytest -q --junitxml=build/fidelity-audit/tests.xml`, Ruff lint/format, mypy, `uv build` | 270 tests passed; all other checks passed |

The two acceptance defects found during review are now guarded: the inventory
previously permitted 35 deliverables to be absent from both disk and manifest,
and the holder audit previously accepted a base with every pivot finger removed.
Both were reproduced with failing tests before correction.

Actual-CAD accessory previews were regenerated and inspected after the final
rebuild. The original `Tigerbee.FCStd`, original 3MF files and scans are unchanged.

## Work still requiring equipment or physical evidence

The overall objective remains active. FPV-camera and end-bracket geometry needs
the selected camera, antenna and power-connector envelopes and mounting dimensions;
these were requested from the user during this review. Bolts/nuts and their actual
engagement, material/layup, machining tolerances and manufactured fit/load tests
remain unresolved as recorded in [the design contract](../../tasks/plan.md).
The CAD results above do not establish physical load performance. Remote GitHub
Actions execution also remains unverified; all listed command results are local.
