#!/usr/bin/env python3
"""Fail on prompt-library defects that are easy to measure before publishing."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path


WORD = re.compile(r"\b\w+(?:[-']\w+)*\b", re.UNICODE)


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def audit(path: Path) -> tuple[list[str], dict[str, int | float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    errors: list[str] = []
    seen: dict[str, list[str]] = defaultdict(list)
    counts: list[int] = []

    for entry in entries:
        entry_id = entry.get("id", "<missing id>")
        prompt = entry.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{entry_id}: prompt is empty or not text")
            continue
        words = len(WORD.findall(prompt))
        counts.append(words)
        if not 12 <= words <= 120:
            errors.append(f"{entry_id}: {words} words, expected 12 to 120")
        if any(ord(char) < 32 and char not in "\n\t" for char in prompt):
            errors.append(f"{entry_id}: prompt contains a control character")
        if "PENDING" in prompt.upper():
            errors.append(f"{entry_id}: prompt still contains a pending marker")
        seen[normalized(prompt)].append(entry_id)

    for ids in seen.values():
        if len(ids) > 1:
            errors.append(f"duplicate prompt text: {', '.join(ids)}")

    ordered = sorted(counts)
    summary: dict[str, int | float] = {
        "prompts": len(entries),
        "unique": len(seen),
        "min_words": min(ordered, default=0),
        "median_words": statistics.median(ordered) if ordered else 0,
        "p95_words": ordered[max(0, int(len(ordered) * .95) - 1)] if ordered else 0,
        "max_words": max(ordered, default=0),
    }
    return errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=Path("prompts.json"))
    args = parser.parse_args()
    errors, summary = audit(args.manifest)
    print(
        f"{summary['prompts']} prompts, {summary['unique']} unique; words "
        f"min {summary['min_words']}, median {summary['median_words']}, "
        f"p95 {summary['p95_words']}, max {summary['max_words']}"
    )
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        print(f"{len(errors)} prompt quality check(s) failed")
        return 1
    print("all prompt quality checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
