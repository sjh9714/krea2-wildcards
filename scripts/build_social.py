#!/usr/bin/env python3
"""Build the 1200 by 630 social preview from published Krea 2 output."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parents[1]
PICKS = ["product-019", "fashion-011", "interior-010"]


def font(size: int, bold: bool = False):
    names = ["Arial Bold.ttf", "Helvetica.ttc"] if bold else ["Arial.ttf", "Helvetica.ttc"]
    for name in names:
        for folder in ("/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/"):
            path = Path(folder + name)
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), size)
                except OSError:
                    pass
    return ImageFont.load_default()


def square(path: Path, size: int) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGB")
        side = min(image.size)
        left = (image.width - side) // 2
        top = (image.height - side) // 2
        return image.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)


def main() -> int:
    manifest = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in manifest["entries"]}
    missing = [entry_id for entry_id in PICKS if entry_id not in by_id]
    if missing:
        raise SystemExit(f"missing social preview entries: {missing}")

    canvas = Image.new("RGB", (1200, 630), "#f6f5f1")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 448, 630), fill="#123f34")
    draw.text((52, 55), "KREA 2 TURBO", fill="#a9d4c2", font=font(20, True))
    draw.text((52, 112), str(len(manifest["entries"])), fill="#ffffff", font=font(96, True))
    draw.text((55, 215), "tested prompts", fill="#ffffff", font=font(34, True))
    draw.text((55, 274), "Images, ComfyUI wildcards,\nand starter workflows.",
              fill="#d5e8e0", font=font(25), spacing=12)
    draw.line((55, 401, 390, 401), fill="#6f9e8d", width=2)
    draw.text((55, 433), "sjh9714/krea2-wildcards", fill="#ffffff", font=font(22, True))
    draw.text((55, 480), "Browse. Copy. Render.", fill="#a9d4c2", font=font(20))

    size = 360
    positions = [(448, 0), (808, 0), (628, 270)]
    for entry_id, position in zip(PICKS, positions):
        image = square(HERE / by_id[entry_id]["image"], size)
        canvas.paste(image, position)

    draw.rectangle((448, 0, 1199, 629), outline="#f6f5f1", width=4)
    draw.line((808, 0, 808, 270), fill="#f6f5f1", width=4)
    draw.line((628, 270, 628, 630), fill="#f6f5f1", width=4)
    draw.line((988, 270, 988, 630), fill="#f6f5f1", width=4)

    output = HERE / "social-preview.webp"
    canvas.save(output, "WEBP", quality=90, method=6)
    print(f"{output.name} {canvas.width}x{canvas.height} {output.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
