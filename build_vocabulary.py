#!/usr/bin/env python3
"""
build_vocabulary.py - turn vocabulary.json into a term index, and mark the terms.

Why this exists. A prompt in this catalog is 222 characters of description and
nothing in it is marked, so a reader cannot see which words are doing the work.
The highest-scoring prompting guide in this subreddit does exactly one thing
differently: it bolds the phrase that produces the effect. That is the gap.

What this is not. Bolding a phrase and calling it the cause would be a claim
this catalog never tested, one prompt at a time, 475 times over. So the claim
here is deliberately weaker and checkable: these terms recur across the catalog
and travel between subjects. The rule is 3 or more entries across 2 or more
categories, enforced below. A term that stops meeting it fails the build.

Some terms carry an extra usage note because they benefit from more precise
phrasing. Those cross-references are checked against the source data so the
generated guide stays current.

    python3 build_vocabulary.py

Writes VOCABULARY.md. build_pages.py imports mark() from here.
"""

from __future__ import annotations

import html
import json
import re
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent

MIN_ENTRIES = 3
MIN_CATEGORIES = 2


def load() -> tuple[dict, dict]:
    v = json.loads((HERE / "vocabulary.json").read_text(encoding="utf-8"))
    d = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    return v, d


def term_pattern(terms: list[str]) -> re.Pattern:
    """Longest first, so "shallow depth of field" wins over "depth of field" and
    "soft even light" over "even light". Word-bounded at both ends so "warm" in
    "warmth" and "worn" in "sworn" do not match."""
    ordered = sorted(terms, key=len, reverse=True)
    # Trailing s optional: the catalog writes "long shadows" and "soft shadows"
    # as often as the singular, and a term that only matched one of them fell
    # under the rule for a spelling reason rather than a real one.
    return re.compile(r"\b(" + "|".join(re.escape(t) for t in ordered) + r")s?\b",
                      re.IGNORECASE)


def usage(v: dict, d: dict) -> "OrderedDict[str, dict]":
    pat = term_pattern([t["t"] for t in v["terms"]])
    by: OrderedDict[str, dict] = OrderedDict(
        (t["t"], {**t, "entries": [], "categories": set()}) for t in v["terms"])
    lookup = {t.lower(): t for t in by}
    for e in d["entries"]:
        for m in set(x.lower() for x in pat.findall(e["prompt"])):
            key = lookup[m]
            by[key]["entries"].append(e["id"])
            by[key]["categories"].add(e["category"])
    return by


def mark(prompt: str, pat: re.Pattern, fmt: str = "html") -> str:
    """Wrap every vocabulary term in the prompt. `fmt` html for the gallery,
    md for anything rendered by GitHub."""
    if fmt == "html":
        return pat.sub(lambda m: f"<mark>{m.group(0)}</mark>", html.escape(prompt))
    return pat.sub(lambda m: f"**{m.group(0)}**", prompt)


def main() -> int:
    v, d = load()
    by = usage(v, d)

    finding_titles = {f["title"] for f in d["findings"]["items"]}
    problems = []
    for t, row in by.items():
        if len(row["entries"]) < MIN_ENTRIES or len(row["categories"]) < MIN_CATEGORIES:
            problems.append(f"{t!r}: {len(row['entries'])} entries in "
                            f"{len(row['categories'])} categories, below the rule")
        if row["g"] not in v["groups"]:
            problems.append(f"{t!r}: group {row['g']!r} is not declared")
        ref = row.get("finding")
        if ref and ref not in finding_titles:
            problems.append(f"{t!r}: cites a finding that does not exist: {ref!r}")
    if problems:
        print("vocabulary.json does not hold up:")
        for p in problems:
            print("  " + p)
        return 1

    marked = sum(1 for e in d["entries"]
                 if term_pattern([t["t"] for t in v["terms"]]).search(e["prompt"]))

    L = ["# The vocabulary", "", v["_intro"], "", f"*{v['_rule']}*", "",
         f"{len(by)} terms. {marked} of {len(d['entries'])} prompts carry at least "
         f"one of them.", ""]

    warned = [t for t, r in by.items() if r.get("finding")]
    if warned:
        L += [f"## Precision notes for {len(warned)} terms", "",
              "These recurring terms work best with an extra composition or medium cue.",
              "", "| term | practical note | guide |", "|---|---|---|"]
        for t in warned:
            r = by[t]
            L.append(f"| `{t}` | {r['n']} | [prompt field guide](FINDINGS.md) |")
        L.append("")

    for g, blurb in v["groups"].items():
        rows = [(t, r) for t, r in by.items() if r["g"] == g]
        L += [f"## {g}", "", f"*{blurb}*", "",
              "| term | entries | what it does |", "|---|---|---|"]
        for t, r in sorted(rows, key=lambda kv: -len(kv[1]["entries"])):
            flag = " ⚠️" if r.get("finding") else ""
            L.append(f"| `{t}`{flag} | **{len(r['entries'])}** in "
                     f"{len(r['categories'])} categories | {r['n']} |")
        L.append("")

    L += ["## Where each term is used", "",
          "Entry ids, so you can pull the prompt and the image for any of them.", ""]
    for t, r in by.items():
        L.append(f"- **`{t}`** ({len(r['entries'])}): "
                 + ", ".join(f"`{i}`" for i in sorted(r["entries"])))
    L.append("")

    (HERE / "VOCABULARY.md").write_text("\n".join(L), encoding="utf-8")
    print(f"VOCABULARY.md  {len(by)} terms, {marked}/{len(d['entries'])} prompts marked")
    print(f"  {len(warned)} carry an extra usage note")
    thin = sorted(by.items(), key=lambda kv: len(kv[1]["entries"]))[:3]
    print("  thinnest: " + ", ".join(f"{t} ({len(r['entries'])})" for t, r in thin))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
