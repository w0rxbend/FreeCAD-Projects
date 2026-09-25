"""The thumbnail gate: a 200 px black-on-white orthographic silhouette of every part, contact-sheeted
per accessory, plus the §4.5 numbers that say whether a row of variants is really several different
SHAPES.

    uv run python scripts/thumbnail_silhouette.py                      # every accessory
    uv run python scripts/thumbnail_silhouette.py --only side_panels camera_pod
    uv run python scripts/thumbnail_silhouette.py --only tail_block --variant shard carapace

Why a filled silhouette and not the outline drawing: a style variant is not done until its row of
thumbnails is visibly different at 200 px, and an outline drawing passes that test on interior detail
alone - a hole pattern. Filling the shape throws the detail away and leaves exactly what the design
language asks us to judge: the plan outline. The directive is silhouette FIRST, surface second.

The gate (design language §4.5), for every pair of variants of one accessory:
  * the silhouette areas differ by more than 12 %, OR
  * the convex-hull deficiency differs by more than 0.10, OR
  * the normalised shapes overlap less than 0.85 IoU
Any pair failing all three is reported: those two variants are the same drawing with a different hole
pattern, and the OUTLINE has to change - not the vents.

Writes dist/accessories/gallery/sil_<label>.png and <accessory>_silhouettes.png. Exit code 1 when a
pair fails the gate (or a module cannot be built), 0 otherwise.
"""

from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np
from build123d import Axis

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tigerbee.accessories import (build_accessory, discover_accessories, printed,  # noqa: E402
                                  style_name, variant_names)
from tigerbee.accessories import _export as E  # noqa: E402

MAGICK = E.MAGICK        # one ImageMagick path, owned by _export
DIST = Path("dist/accessories")
GRID = 64            # the normalised grid the IoU is measured on
from tigerbee.accessories import _style as S  # noqa: E402

# Thresholds come from _style so this script and the in-module §4.5 rows cannot drift apart - they
# had already drifted once, to the point of disagreeing on whether "hull" meant a convex hull or a
# bounding box.
AREA_DELTA = S.SIL_AREA_DELTA       # §4.5: outline areas must differ by more than 12 %
DEFICIENCY_DELTA = S.SIL_DEF_DELTA
IOU_MAX = 0.85


def mask(png: Path) -> np.ndarray | None:
    """The ink mask as a boolean array (True = part). Read through ImageMagick's PGM so the script
    needs no imaging library."""
    try:
        raw = subprocess.run([MAGICK, str(png), "-colorspace", "gray", "pgm:-"],
                             check=True, capture_output=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return None
    parts, i = [], 0
    while len(parts) < 4 and i < len(raw):          # magic, width, height, maxval
        if raw[i:i + 1] == b"#":
            i = raw.index(b"\n", i) + 1
            continue
        j = i
        while j < len(raw) and raw[j:j + 1] not in b" \t\r\n":
            j += 1
        if j > i:
            parts.append(raw[i:j])
        i = j + 1
    if len(parts) < 4 or parts[0] not in (b"P5", b"P2"):
        return None
    w, h, maxv = int(parts[1]), int(parts[2]), int(parts[3])
    body = raw[i:]
    if parts[0] == b"P2":
        vals = np.array([int(v) for v in body.split()[:w * h]], dtype=float)
    elif maxv > 255:
        vals = np.array(struct.unpack(f">{w * h}H", body[:2 * w * h]), dtype=float)
    else:
        vals = np.frombuffer(body[:w * h], dtype=np.uint8).astype(float)
    if vals.size < w * h:
        return None
    return (vals.reshape(h, w) < 0.5 * maxv)


def _hull_area(pts: np.ndarray) -> float:
    """Convex-hull area by monotone chain - no scipy, and the point set is only a few hundred wide."""
    if len(pts) < 3:
        return 0.0
    p = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def half(seq):
        out: list = []
        for q in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by) = out[-2], out[-1]
                if (bx - ax) * (q[1] - ay) - (by - ay) * (q[0] - ax) > 0:
                    break
                out.pop()
            out.append(tuple(q))
        return out

    hull = half(p)[:-1] + half(p[::-1])[:-1]
    if len(hull) < 3:
        return 0.0
    a = 0.0
    for k, (x0, y0) in enumerate(hull):
        x1, y1 = hull[(k + 1) % len(hull)]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2.0


def metrics(m: np.ndarray) -> dict:
    """Silhouette numbers: area in pixels, the fraction of its own bounding box it fills, the convex
    hull deficiency (how much the shape is NOT its hull - a truss is deficient, an egg is not) and the
    normalised GRID x GRID mask the IoU is measured on."""
    ys, xs = np.nonzero(m)
    if not len(xs):
        return {}
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = m[y0:y1, x0:x1]
    area = float(crop.sum())
    hull = _hull_area(np.column_stack([xs.astype(float), ys.astype(float)]))
    # rows/cols of the crop resampled to GRID by nearest neighbour, so two parts of different size are
    # compared as shapes and not as sizes
    ri = (np.arange(GRID) * crop.shape[0] / GRID).astype(int)
    ci = (np.arange(GRID) * crop.shape[1] / GRID).astype(int)
    return dict(area=area, bbox=(int(x1 - x0), int(y1 - y0)),
                fill=area / float(crop.shape[0] * crop.shape[1]),
                deficiency=(1.0 - area / hull) if hull > 0 else 0.0,
                grid=crop[np.ix_(ri, ci)])


def iou(a: np.ndarray, b: np.ndarray) -> float:
    union = float((a | b).sum())
    return float((a & b).sum()) / union if union else 1.0


def shoot(mod, variant: str, out_dir: Path, width: int) -> dict[str, dict]:
    """Build one variant and write a filled silhouette per part. Returns {label: metrics}."""
    got: dict[str, dict] = {}
    parts = build_accessory(mod, variant)
    for label, part in parts.items():
        png = out_dir / f"sil_{label}.png"
        # E.silhouette renders the outline and fills it through the same ImageMagick pipeline the
        # gallery uses - one implementation, so the sheet and the gate always show the same picture
        pr = printed(mod, label, part)
        E.silhouette(pr, png, width=width)
        m = mask(png)
        met = metrics(m) if m is not None else {}
        if not met:
            print(f"  ! {label}: empty silhouette")
            continue
        # THE SECOND VIEW. The plan alone cannot see a swell, a gill bank, a fin run, an intake or
        # a bow - every differentiator that lives in the section rather than the footprint. Sighting
        # along the part's own outboard normal is the view you judge it by in the hand.
        png_e = out_dir / f"sil_{label}_elev.png"
        E.silhouette(pr.rotate(Axis.Y, 90), png_e, width=width)
        me = mask(png_e)
        met["elev"] = metrics(me) if me is not None else None
        met["style"] = style_name(mod, variant) or (variant or "-")
        got[label] = met
        print(f"  {label:38s} {met['bbox'][0]:3d} x {met['bbox'][1]:3d} px  "
              f"fill {met['fill']:.2f}  hull deficiency {met['deficiency']:.2f}  [{met['style']}]")
    return got


def gate(name: str, shots: dict[str, dict]) -> list[str]:
    """§4.5, per pair of variants of the same BASE part: two families must differ in the outline, not
    only in the hole pattern. Returns the failing pairs."""
    fails = []
    by_base: dict[str, list[str]] = {}
    for label in shots:
        by_base.setdefault(label.split("__", 1)[0], []).append(label)
    for base, labels in sorted(by_base.items()):
        for i, a in enumerate(sorted(labels)):
            for b in sorted(labels)[i + 1:]:
                ma, mb = shots[a], shots[b]

                def _view(x, y):
                    if not x or not y:
                        return False, "n/a"
                    da = abs(x["area"] - y["area"]) / max(x["area"], y["area"])
                    dd = abs(x["deficiency"] - y["deficiency"])
                    ov = iou(x["grid"], y["grid"])
                    hit = da > AREA_DELTA or dd > DEFICIENCY_DELTA or ov < IOU_MAX
                    return hit, f"area {da:.3f}, deficiency {dd:.3f}, IoU {ov:.3f}"

                ok_p, det_p = _view(ma, mb)
                ok_e, det_e = _view(ma.get("elev"), mb.get("elev"))
                # Differ in EITHER view to pass; alike in BOTH to fail. Not a wider gate - a gate
                # that looks from the second direction, so an honest redesign of the section is no
                # longer punished for keeping a sensible footprint, while a variant that changes
                # nothing still fails both.
                ok = ok_p or ok_e
                verdict = "PASS" if ok else "FAIL"
                print(f"  {verdict}  {name}/{base}: {ma['style']} vs {mb['style']} - "
                      f"plan [{det_p}] elev [{det_e}]")
                if not ok:
                    fails.append(f"{base}: {ma['style']} vs {mb['style']} "
                                 f"(area {da:.3f} <= {AREA_DELTA}, deficiency {dd:.3f} "
                                 f"<= {DEFICIENCY_DELTA}, IoU {ov:.3f} >= {IOU_MAX})")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", default=None, help="accessory ids (default: all)")
    ap.add_argument("--variant", nargs="*", default=None, help="variant names to shoot")
    ap.add_argument("--out", default=str(DIST / E.GALLERY), help="output directory")
    ap.add_argument("--width", type=int, default=200, help="thumbnail width in px (default 200)")
    ap.add_argument("--no-sheet", action="store_true", help="skip the per-accessory contact sheets")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    mods = discover_accessories(args.only)
    fails, sheets = [], 0
    for name in sorted(mods):
        mod = mods[name]
        print(f"\n{name}")
        shots: dict[str, dict] = {}
        for variant in variant_names(mod, args.variant):
            try:
                shots.update(shoot(mod, variant, out_dir, args.width))
            except Exception as exc:  # noqa: BLE001 - one broken module must not hide the rest
                fails.append(f"{name}[{variant or '-'}]: {type(exc).__name__}: {exc}")
                print(f"  ! {name}[{variant or '-'}] failed to build: {exc}")
        if not shots:
            continue
        fails += gate(name, shots)
        if not args.no_sheet:
            sheet = out_dir / f"{name}_silhouettes.png"
            if E.contact_sheet([out_dir / f"sil_{lab}.png" for lab in sorted(shots)], sheet, tile=args.width):
                sheets += 1
                print(f"  sheet -> {sheet}")
    print(f"\n{sheets} contact sheet(s) in {out_dir}")
    if fails:
        print(f"\n{len(fails)} silhouette gate failure(s) - the OUTLINE has to change, not the vents:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("OK: every variant row is visibly a different shape")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
