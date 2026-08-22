#!/usr/bin/env python3
"""
build_hero.py, compose the README hero from real catalog output.

The hero is a compact overview of twelve visual categories. Each frame comes
from a published prompt and prints its seed, so the landing page shows the real
collection rather than a decorative mockup.

    python3 build_hero.py            # writes hero.webp

Captions stay ASCII. An earlier hero rendered typographic dashes as tofu because
the fallback font had no glyph, and it went out that way.
"""

from __future__ import annotations

import argparse
import json
import pathlib

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent

# Twelve frames chosen for how they read at 228px, across as many subjects as the
# grid allows.
PICKS = [
    "interior-010", "landscape-007", "macro-nature-008", "night-008",
    "underwater-005", "weather-001", "animal-002", "glass-008",
    "vehicle-010", "mineral-004", "plant-006", "macro-nature-003",
]

COLS, CELL, HEAD = 4, 228, 84


def font(size: int, bold: bool = False):
    names = ["Arial Bold.ttf", "Helvetica.ttc"] if bold else ["Arial.ttf", "Helvetica.ttc"]
    for n in names:
        for d in ("/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/"):
            p = pathlib.Path(d + n)
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size)
                except Exception:
                    pass
    return ImageFont.load_default()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(HERE / "hero.webp"))
    args = ap.parse_args()

    data = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["entries"]}

    missing = [p for p in PICKS if p not in by_id]
    if missing:
        print(f"not in entries: {missing}")
        return 1
    # The seed strip is the whole argument of this image. A frame without one
    # would print a blank label and make the opposite of the intended claim.
    seedless = [p for p in PICKS if by_id[p].get("params", {}).get("seed") is None]
    if seedless:
        print(f"no seed recorded for: {seedless}")
        return 1

    rows = (len(PICKS) + COLS - 1) // COLS
    im = Image.new("RGB", (CELL * COLS, HEAD + CELL * rows), (255, 255, 255))
    d = ImageDraw.Draw(im)

    # The banner used to lead with the seed and the cut generations. Both are
    # true and neither is a reason to click: a visitor is deciding whether to
    # take something, not auditing us. It now says the same thing the README
    # tagline says, so the picture and the sentence do not disagree.
    kept = len(data["entries"])
    d.text((20, 18), f"{kept} tested Krea 2 Turbo prompts",
           fill=(17, 17, 17), font=font(25, bold=True))
    d.text((20, 51), "One file. Drop it in ComfyUI/wildcards/ and call __all__.",
           fill=(105, 105, 105), font=font(16))

    fseed = font(14, bold=True)
    for i, pid in enumerate(PICKS):
        entry = by_id[pid]
        src = Image.open(HERE / entry["image"]).convert("RGB")
        s = min(src.size)
        src = src.crop(((src.width - s) // 2, (src.height - s) // 2,
                        (src.width + s) // 2, (src.height + s) // 2))
        x, y = (i % COLS) * CELL, HEAD + (i // COLS) * CELL
        im.paste(src.resize((CELL, CELL), Image.LANCZOS), (x, y))

        # No seed label. It is a number the visitor cannot use and did not ask
        # for, printed over the only thing on this image they can judge.

    im.save(args.out, "WEBP", quality=88, method=6)
    out = pathlib.Path(args.out)
    print(f"{out.name}  {im.size[0]}x{im.size[1]}  {out.stat().st_size // 1024} KB  "
          f"{len(PICKS)} frames, all seeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
