#!/usr/bin/env python3
"""
build_gallery.py - the whole catalog as markdown, inside the repository.

Why this exists. The 475 entries used to be printed in README.md, which made it
192 KB; GitHub lazy-loads a file that long, so deep anchors landed in the wrong
place and the catalog was the last thing anyone reached. Moving it to the Pages
gallery fixed both problems and created a worse one: a visitor who lands on the
repo and does not click through now sees a single sample entry.

Checked against the five prompt catalogs above 8,000 stars in this niche on
2026-08-06. All five keep the prompts inside the repository. Four print them in
the README (290 KB, 371 KB, 96 KB, 83 KB). The fifth, freestylefly at 9,344
stars, does exactly what this script does: a short README that points at gallery
markdown split into parts, 287 KB and 586 KB. None of them rely on a Pages site
alone.

So the catalog comes back into the repo, just not into the landing page.

    python3 build_gallery.py

Writes docs/gallery.md, plus docs/gallery-part-N.md if one file would be too
long to render comfortably.
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path

from build_vocabulary import load as load_vocab, term_pattern

HERE = Path(__file__).resolve().parent
DOCS = HERE / "docs"

# freestylefly splits at 287 KB and 586 KB. GitHub renders more than that, but
# every image above your anchor still has to resolve before the browser knows
# where the anchor is, and that drift is the exact bug this repo shipped once
# already, in a 192 KB README. So split harder than the reference does: a reader
# following a category link should land on a page that is mostly the thing they
# clicked, not a page with four hundred images above it.
SPLIT_BYTES = 110_000

VOCAB = term_pattern([x["t"] for x in load_vocab()[0]["terms"]])


def slug(s: str) -> str:
    return s.lower().replace(" ", "-")


def entry_block(e: dict, entries: list[dict], nth: int, home: str) -> list[str]:
    L = [f"### {nth}. {e['title']}", ""]
    L.append(f'<img src="../{e["image"]}" width="420" alt="{e["title"]}">')
    L.append("")
    L.append("```text")
    L.append(e["prompt"].strip())
    L.append("```")
    L.append("")

    bits = []
    params = e.get("params") or {}
    seed = params.get("seed")
    if seed is not None:
        bits.append(f"`seed: {seed}`")
    elif params.get("generation_id"):
        bits.append(f"`Krea asset: {params['generation_id']}`")
        if params.get("aspect_ratio"):
            bits.append(f"`aspect: {params['aspect_ratio']}`")
    if e.get("source"):
        src = next((x for x in entries if x["id"] == e["source"]), None)
        label = src["title"] if src else e["source"]
        bits.append(f"image-to-image from **{label}** · `strength: {e.get('strength')}`")
    bits.append(f"`{e['id']}`")
    L.append(" · ".join(bits))

    terms = sorted(set(m.lower() for m in VOCAB.findall(e["prompt"])))
    if terms:
        L.append("")
        L.append("<sub>vocabulary: " + ", ".join(f"`{t}`" for t in terms)
                 + " · [what each one does](../VOCABULARY.md)</sub>")

    # Attribution, when the entry did not come from this repository's own runs.
    who = e.get("prompt_author")
    if who:
        link = e.get("prompt_author_link")
        who_s = f"[{who}]({link})" if link else who
        src_links = " · ".join(f"[source]({u})" for u in e.get("source_links", []))
        lic = e.get("license")
        L.append("")
        L.append(f"<sub>prompt by {who_s}"
                 + (f" · {src_links}" if src_links else "")
                 + (f" · {lic}" if lic else "") + "</sub>")

    if e.get("notes"):
        L.append("")
        L.append(f"> {e['notes']}")
    L.append("")
    L.append(f"<sub>[back to the categories]({home})</sub>")
    L.append("")
    return L


def main() -> int:
    d = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    entries = [e for e in d["entries"] if (HERE / e["image"]).exists()]
    cats: OrderedDict[str, list] = OrderedDict()
    for e in entries:
        cats.setdefault(e["category"], []).append(e)

    DOCS.mkdir(exist_ok=True)
    for old in DOCS.glob("gallery*.md"):
        old.unlink()

    # Render each category once, then decide how many files they go in.
    # The index lives in gallery.md whether or not the entries are split, so the
    # per-entry link home has to name the file, not just the anchor. The first
    # version linked #categories and every one of them was dead in a split build.
    home = "gallery.md#categories"
    blocks: list[tuple[str, str]] = []
    for cat, items in cats.items():
        L = [f"## {cat}", ""]
        desc = (d.get("categories") or {}).get(cat)
        if desc:
            L += [f"_{desc}_", ""]
        for i, e in enumerate(items, 1):
            L += entry_block(e, entries, i, home)
        blocks.append((cat, "\n".join(L)))

    parts: list[list[tuple[str, str]]] = [[]]
    size = 0
    for cat, body in blocks:
        if size and size + len(body) > SPLIT_BYTES:
            parts.append([])
            size = 0
        parts[-1].append((cat, body))
        size += len(body)

    multi = len(parts) > 1
    where: dict[str, str] = {}
    for n, part in enumerate(parts, 1):
        fname = f"gallery-part-{n}.md" if multi else "gallery.md"
        for cat, _ in part:
            where[cat] = fname

    head = ["# The catalog", "",
            f"All **{len(entries)}** ready-to-use prompts, each paired with its generated "
            "image and provenance.", "",
            "Every image is the original model output, so you can compare the prompt "
            "and result directly.",
            "Earlier fal runs record seeds; Krea web runs record generation asset IDs. "
            "[REPRODUCING.md](../REPRODUCING.md) explains both routes.", "",
            "This file is generated by `build_gallery.py`. Edit `prompts.json`, not this.", "",
            "## Categories", ""]
    head.append(" · ".join(
        f"[{c}]({where[c]}#{slug(c)} ) {len(v)}".replace(" )", ")")
        if multi else f"[{c}](#{slug(c)}) {len(v)}"
        for c, v in cats.items()))
    head += ["", "[Browse the same collection as a web page]"
                 "(https://sjh9714.github.io/krea2-wildcards/)", ""]

    written = []
    if not multi:
        text = "\n".join(head) + "\n" + "\n".join(b for _, b in parts[0]) + "\n"
        (DOCS / "gallery.md").write_text(text, encoding="utf-8")
        written.append(("gallery.md", len(text)))
    else:
        (DOCS / "gallery.md").write_text("\n".join(head), encoding="utf-8")
        written.append(("gallery.md", len("\n".join(head))))
        for n, part in enumerate(parts, 1):
            nav = [f"[← the categories](gallery.md)", ""]
            text = "\n".join(nav) + "\n".join(b for _, b in part)
            (DOCS / f"gallery-part-{n}.md").write_text(text, encoding="utf-8")
            written.append((f"gallery-part-{n}.md", len(text)))
    # build_catalog.py links each category straight at the file it landed in, so
    # the split has to be discoverable rather than guessed.
    (DOCS / "gallery-map.json").write_text(
        json.dumps({"multi": multi, "where": where}, indent=2) + "\n",
        encoding="utf-8")

    for name, n in written:
        print(f"docs/{name}  {n // 1024} KB")
    print(f"{len(entries)} entries across {len(cats)} categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
