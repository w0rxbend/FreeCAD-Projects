# CAD automation and release packaging

The three workflows implement the plan's quality, CAD build and tagged release
pipelines. They use Python 3.12, pinned uv 0.12.11 and `uv sync --frozen`.

## Repository placement

**GitHub discovers workflows only in the repository root's `.github/workflows`.**
This workspace lives in `FreeCAD-Projects/Tigerbeetle V2`, inside the parent Git
repository. Its `.github/workflows/{ci,cad,release}.yml` files are standalone-project
templates. The installed parent-repository workflows are:

| Template | Active repository path |
| --- | --- |
| `ci.yml` | `../.github/workflows/tigerbeetle-v2-ci.yml` |
| `cad.yml` | `../.github/workflows/tigerbeetle-v2-cad.yml` |
| `release.yml` | `../.github/workflows/tigerbeetle-v2-release.yml` |

The parent copies use distinct names and matching reusable-workflow references;
the existing sibling `tigerbee.yml` is preserved. Both arrangements automatically
locate the project's working directory. Keep template and parent copies synchronized
when editing workflow steps. Local installation makes their paths discoverable
once committed and pushed; it does not establish a successful hosted run or enabled
branch protection. No remote publication has been performed.

## Quality and CAD jobs

`ci.yml` runs lint, strict type checking, every pytest test, and assembly validation
for `reference`, `default`, `minimum_supported`, `maximum_supported`, and
`tolerance_test`. Pytest includes unit, geometry, symmetry, shared interface,
assembly, blueprint and export tests. Failures stop the job and reports are retained.

`cad.yml` installs the official, checksum-pinned FreeCAD 1.1.3 AppImage and runs the full build,
all five preset validations, every export format, an independent drawing command,
both scan overlays, and parameter serialization. FreeCAD export must reopen its
saved document successfully. The bundle is extracted so runners do not require
FUSE. The CAD job enables `FPV_TEST_FREECAD=1` for native conversion regression
tests before exporting. The independent drawing output uses its own directory
so that exporting SVG cannot replace the complete multi-format inventory.

CAD upload layout:

```text
cad-artifacts/
  step/ stl/ 3mf/ freecad/ svg/
  overlays/ reports/
  parameters.json
  export-manifest.json
  manifest.json
  SHA256SUMS
```

The original export manifest records provenance, component inventory and exporter
mesh settings. The package manifest covers CAD files, parameter data, overlays and
reports. `SHA256SUMS` also covers both manifest files. The package tool checks the
export checksums before copying files and refuses an existing output directory.

Local equivalent, from the project root with a supported FreeCAD runtime installed:

```bash
uv sync --frozen
uv run --frozen ruff check .
uv run --frozen mypy
uv run --frozen pytest
mkdir -p artifacts/reports
uv run --frozen fpv-frame build > artifacts/reports/build.json
for preset in reference default minimum_supported maximum_supported tolerance_test; do
  uv run --frozen fpv-frame --preset "$preset" validate > "artifacts/reports/validate-$preset.json"
done
uv run --frozen fpv-frame export > artifacts/reports/export.json
uv run --frozen fpv-frame drawing --output artifacts/drawing-check
uv run --frozen fpv-frame overlay scan-1
uv run --frozen fpv-frame overlay scan-2
uv run --frozen fpv-frame parameters > artifacts/parameters.json
uv run --frozen python tools/package_release.py --output artifacts/package
```

Choose a new `--output` directory for each subsequent package. Reports are evidence
from the current command sequence; use a clean checkout for reproducible release
builds. The package tool requires every validation report to identify its preset and
include a parameter snapshot with a correct canonical SHA-256 hash. Each snapshot
must match that preset's current definition; the selected preset must also match
the exported CAD metadata, wheelbase, component count, and parameters JSON. The
native reopen report must contain exactly the exported component names and solids.
This rejects reports copied between
presets and stale reports after parameter changes. Checksums cannot establish when
a report was generated or authenticate an externally forged report. CI generates
everything in its fresh checkout before packaging.

## Tagged publication

`release.yml` triggers for pushed `v*` tags. It first calls the entire CI workflow,
then the CAD workflow, downloads their verified release assets, rechecks SHA-256,
and creates the GitHub Release for the existing tag. It publishes:

```text
STEP.zip STL.zip 3MF.zip FreeCAD.zip SVG.zip
overlays.zip reports.zip parameters.zip manifest.json SHA256SUMS
```

ZIPs contain their named directory. `parameters.zip` contains the exact parameter
JSON used for the exported CAD. Archive entry times are fixed to avoid timestamp
noise. Release `SHA256SUMS` covers the downloadable ZIPs and manifest; the CAD
bundle's checksums instead cover its individual files.

Only the final publication job has `contents: write`. PR and build jobs have read
access and checkout does not retain credentials. No secrets beyond GitHub's job
token are needed. Releases are created with `--verify-tag`; an existing release is
not silently overwritten. A failed release is corrected with a new tag rather than
replacing assets consumers may already have downloaded.

Require the quality and CAD status checks in repository branch protection before
relying on them to block merges. No remote run or tagged publication is implied
by generating these workflow files.

Action interfaces were checked against the official repositories:
[checkout](https://github.com/actions/checkout),
[setup-uv](https://github.com/astral-sh/setup-uv),
[upload-artifact](https://github.com/actions/upload-artifact),
[download-artifact](https://github.com/actions/download-artifact), and
[GitHub CLI release creation](https://cli.github.com/manual/gh_release_create).

The pinned native runtime and its published digest were verified against the
[official FreeCAD 1.1.3 release](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3).
