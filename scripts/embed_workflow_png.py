#!/usr/bin/env python3
"""Embed generated ComfyUI workflow JSON in PNG drag-and-drop examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, PngImagePlugin


ROOT = Path(__file__).resolve().parents[1]


def embed(workflow: Path, image: Path, output: Path, announce: bool = True) -> None:
    graph = json.loads(workflow.read_text(encoding="utf-8"))
    info = PngImagePlugin.PngInfo()
    # ASCII escaping keeps the payload in the plain PNG tEXt chunk that ComfyUI
    # uses for its own drag-and-drop workflow images.
    info.add_text("workflow", json.dumps(graph, ensure_ascii=True, separators=(",", ":")))
    info.add_text("krea2-wildcards", "https://github.com/sjh9714/krea2-wildcards")

    with Image.open(image) as source:
        rgb = source.convert("RGB")
        output.parent.mkdir(parents=True, exist_ok=True)
        rgb.save(output, format="PNG", optimize=True, pnginfo=info)
    if announce:
        print(output.resolve().relative_to(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    parser.add_argument("image", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    embed(args.workflow, args.image, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
