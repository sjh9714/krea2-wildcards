#!/usr/bin/env python3
"""Build the compact JSONL export used by dataset hubs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def export_entry(entry: dict[str, Any], repo_slug: str, ref: str) -> dict[str, Any]:
    image_path = entry["image"]
    result = {
        "id": entry["id"],
        "category": entry["category"],
        "title": entry["title"],
        "prompt": entry["prompt"],
        "image_url": f"https://raw.githubusercontent.com/{repo_slug}/{ref}/{image_path}",
        "params": entry["params"],
        "batch": entry["batch"],
    }
    for field in ("source", "strength", "attribution"):
        if field in entry:
            result[field] = entry[field]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=Path("prompts.json"))
    parser.add_argument(
        "output", nargs="?", type=Path, default=Path("dataset/prompts.jsonl")
    )
    parser.add_argument("--ref", default="main", help="Git ref used in image URLs")
    args = parser.parse_args()

    catalog = json.loads(args.manifest.read_text(encoding="utf-8"))
    entries = catalog["entries"]
    repo_slug = catalog["repo"].removesuffix(".git")
    repo_slug = repo_slug.removeprefix("https://github.com/").strip("/")
    lines = [
        json.dumps(
            export_entry(entry, repo_slug, args.ref), ensure_ascii=False, sort_keys=True
        )
        for entry in entries
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
