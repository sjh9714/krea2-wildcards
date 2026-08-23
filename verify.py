#!/usr/bin/env python3
"""
verify.py, check the catalog against itself.

This exists because of one bug. The hands category was withdrawn, the subtitle
and the findings were corrected to 476 kept and 64 cut, and the paragraph that
introduces the findings kept saying 483 and 78. Two paragraphs of the same page
disagreed about the count for five hours, in a document whose entire argument is
that the counts were checked, while a public post pointed at it.

Nothing caught that, because nothing was looking. A repository that asks readers
to verify its claims should be able to verify its own, so this runs the checks
that would have caught it:

  - every entry and every failure carries a seed
  - every image the manifest names exists, and every image on disk is named
  - every image the READMEs and the gallery reference exists
  - every `seed: N` printed in the README is a seed that is actually in the data
  - the counts add up, and no document contradicts the manifest

    python3 verify.py            # exits non-zero if anything fails

Run it before pushing. It is fast and it has no dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Check:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passed = 0

    def __call__(self, ok: bool, label: str, detail: str = "") -> None:
        if ok:
            self.passed += 1
            print(f"  ok    {label}")
        else:
            self.failures.append(f"{label}{', ' + detail if detail else ''}")
            print(f"  FAIL  {label}{', ' + detail if detail else ''}")


def png_text(path: Path) -> dict[str, str]:
    """Read the uncompressed tEXt chunks used by ComfyUI workflow PNGs."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return {}
    found: dict[str, str] = {}
    pos = 8
    while pos + 12 <= len(data):
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + size]
        pos += size + 12
        if kind == b"tEXt" and b"\0" in payload:
            key, value = payload.split(b"\0", 1)
            found[key.decode("latin-1")] = value.decode("latin-1")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default="prompts.json")
    args = ap.parse_args()

    d = json.loads((HERE / args.manifest).read_text(encoding="utf-8"))
    entries = d["entries"]
    failures = d.get("failures", {}).get("entries", [])
    both = entries + failures
    c = Check()

    print("generation provenance")
    seed = lambda e: (e.get("params") or {}).get("seed")
    asset = lambda e: (e.get("params") or {}).get("generation_id")
    missing = [e["id"] for e in both if seed(e) is None and not asset(e)]
    c(not missing, f"all {len(both)} generations carry a seed or asset ID",
      f"missing on {missing[:5]}")
    web = [e for e in entries if (e.get("params") or {}).get("provider") == "krea-web"]
    web_bad = [e["id"] for e in web if not asset(e) or not e["params"].get("aspect_ratio")]
    c(not web_bad, f"all {len(web)} Krea web entries carry asset ID and aspect ratio",
      f"missing on {web_bad[:5]}")

    print("\nimages")
    named = {e["image"] for e in both}
    absent = sorted(p for p in named if not (HERE / p).exists())
    c(not absent, f"all {len(named)} manifest images exist", f"{absent[:5]}")

    on_disk = {str(p.relative_to(HERE)) for p in HERE.glob("images/**/*.webp")}
    orphans = sorted(on_disk - named - {"hero.webp"})
    c(not orphans, f"no orphan images among {len(on_disk)} on disk", f"{orphans[:5]}")

    print("\ndataset export")
    dataset_path = HERE / "dataset/prompts.jsonl"
    dataset_card = HERE / "dataset/README.md"
    c(dataset_path.exists(), "the JSONL dataset export exists")
    if dataset_path.exists():
        try:
            rows = [json.loads(line) for line in
                    dataset_path.read_text(encoding="utf-8").splitlines()]
        except json.JSONDecodeError as error:
            rows = []
            c(False, "every dataset row is valid JSON", str(error))
        else:
            c(True, "every dataset row is valid JSON")
        c(len(rows) == len(entries),
          f"the dataset contains all {len(entries)} published prompts",
          f"found {len(rows)}")
        c({row.get("id") for row in rows} == {entry["id"] for entry in entries},
          "dataset IDs match the canonical catalog")
        c(all(str(row.get("image_url", "")).startswith("https://") for row in rows),
          "every dataset row links its generated output")
    dataset_card_text = (
        dataset_card.read_text(encoding="utf-8") if dataset_card.exists() else ""
    )
    c(dataset_card.exists() and "community dataset" in dataset_card_text.lower(),
      "the dataset card identifies this as a community resource")
    c(f"This dataset contains {len(entries)} usable English prompts" in
      dataset_card_text,
      "the dataset card count matches the canonical catalog")
    c(f"{len(entries)} JSONL prompt records." in
      (HERE / "README.md").read_text(encoding="utf-8"),
      "the README Hugging Face count matches the canonical catalog")

    print("\nComfyUI workflows")
    workflow_dir = HERE / "workflows"
    expected = {
        "krea2-native-starter": False,
        "krea2-wildcards-starter": True,
    }
    for stem, wants_dynamic in expected.items():
        json_path = workflow_dir / f"{stem}.json"
        png_path = workflow_dir / f"{stem}.png"
        c(json_path.exists(), f"{stem}: JSON exists")
        c(png_path.exists(), f"{stem}: drag-and-drop PNG exists")
        if not json_path.exists():
            continue
        graph = json.loads(json_path.read_text(encoding="utf-8"))
        types = {node.get("type") for node in graph.get("nodes", [])}
        c("SaveImage" in types and len(graph.get("definitions", {}).get("subgraphs", [])) == 1,
          f"{stem}: carries the official Krea 2 subgraph and output")
        c(("DPRandomGenerator" in types) is wants_dynamic,
          f"{stem}: custom wildcard node matches its label")
        source = graph.get("extra", {}).get("krea2_wildcards", {}).get("source_commit")
        c(source == "e95e3b20567bea8df16510c8390b7f897b7e6d4b",
          f"{stem}: official template revision is pinned", f"got {source!r}")
        if png_path.exists():
            embedded = png_text(png_path).get("workflow")
            c(bool(embedded), f"{stem}: PNG embeds a workflow text chunk")
            try:
                same = json.loads(embedded) == graph if embedded else False
            except json.JSONDecodeError:
                same = False
            c(same, f"{stem}: embedded PNG workflow matches its JSON")
    upstream_license = workflow_dir / "UPSTREAM_LICENSE"
    notice = (HERE / "NOTICE.md").read_text(encoding="utf-8")
    c(upstream_license.exists() and "Copyright (c) 2023-present Comfy Org" in
      (upstream_license.read_text(encoding="utf-8") if upstream_license.exists() else ""),
      "the official workflow template's MIT licence is included")
    c("e95e3b20567bea8df16510c8390b7f897b7e6d4b" in notice,
      "NOTICE.md identifies the pinned upstream workflow revision")

    print("\ndocuments")
    import build_catalog as _bc0
    docs = [("README.md" if x == "en" else f"README_{x.upper()}.md")
            for x in _bc0.LANGS] + ["index.html"]
    for name in docs:
        p = HERE / name
        if not p.exists():
            c(False, f"{name} exists")
            continue
        t = p.read_text(encoding="utf-8")
        refs = set(re.findall(r'(?:src="|\]\()((?:images|wildcards)/[^")\s]+)', t))
        broken = sorted(r for r in refs if not (HERE / r).exists())
        c(not broken, f"{name}: {len(refs)} image references resolve", f"{broken[:4]}")

    print("\nseeds quoted in prose")
    # A finding that cites `seed: N` is making a checkable claim. If N is not in
    # the data the claim is not checkable, which is the same as not being true.
    known = {seed(e) for e in both}
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    quoted = {int(s) for s in re.findall(r"seed:\s*(\d+)", readme)}
    unknown = sorted(quoted - known)
    c(not unknown, f"all {len(quoted)} seeds quoted in README are in the manifest",
      f"not found: {unknown[:5]}")

    print("\ncounts")
    schema_version = d.get("schema_version")
    c(isinstance(schema_version, str)
      and re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)",
                       schema_version) is not None,
      "manifest declares a semantic schema version",
      f"got {schema_version!r}")

    gens = d.get("generations")
    c(isinstance(gens, int) and gens >= len(both),
      f"generations ({gens}) >= kept + documented failures ({len(both)})",
      "a total lower than what is on disk cannot be right")
    discarded = d.get("discarded_generations")
    c(isinstance(discarded, int) and not isinstance(discarded, bool) and discarded >= 0,
      "discarded generations is a non-negative integer",
      f"got {discarded!r}")
    c(isinstance(gens, int) and isinstance(discarded, int)
      and not isinstance(discarded, bool) and gens == len(both) + discarded,
      "total generations reconcile with published, documented, and discarded records",
      f"{gens!r} != {len(entries)} + {len(failures)} + {discarded!r}")

    declared = set(d.get("categories") or {})
    used = {e["category"] for e in entries}
    c(not (used - declared), "every category in use is declared",
      f"undeclared: {sorted(used - declared)}")
    # A declared category with no entries is allowed, but only if it says why , 
    # that is how the withdrawn hands category is represented.
    silent = [k for k in declared - used if len(str((d["categories"] or {}).get(k, ""))) < 20]
    c(not silent, "declared-but-empty categories explain themselves", f"{silent}")

    # The intro is generated from these numbers now, so the literals that were
    # wrong must not come back.
    for stale in ("483 are here", "78 were cut"):
        c(stale not in readme, f"README no longer says {stale!r}")

    # GitHub does not process Markdown inside an HTML block, so a link written as
    # [ZH](README_ZH.md) inside <p align="center"> renders as literal brackets.
    # All three language switchers shipped that way and nobody could reach the
    # translations at all. Which made the work of putting findings into them
    # pointless. Nothing else here would have caught it; it only shows on render.
    # Derived from the generator rather than listed here, so adding a language
    # cannot quietly ship a README nobody checks. Five did exactly that once.
    import build_catalog as _bc
    names = {x: ("README.md" if x == "en" else f"README_{x.upper()}.md")
             for x in _bc.LANGS}
    c(all((HERE / f).exists() for f in names.values()),
      f"all {len(names)} language READMEs are built")
    for lang, name in names.items():
        path = HERE / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        raw = re.findall(r'<(p|div|h\d)[^>]*>[^<]*\[[^\]]+\]\([^)]+\)', text)
        c(not raw, f"{name}: no Markdown links inside HTML blocks",
          f"{len(raw)} would render as literal brackets, e.g. {raw[:1]}")
        missing = [o for l2, o in names.items()
                   if l2 != lang and f'href="{o}"' not in text]
        c(not missing, f"{name} links to every other translation"
                       + (f", missing {missing}" if missing else ""))
        c("hero.webp" in text, f"{name} carries the hero")
        c("docs/gallery" in text, f"{name} points into the repo gallery")

    # The hero has gone stale twice by carrying findings that later moved: it led
    # with "one sign holds, a list collapses" after the stringcount ladder
    # disproved it, and then with hands and interlocking after the hands category
    # was withdrawn and the interlocking rule was thrown away. Its own docstring
    # said to regenerate it whenever a finding changed, and nobody did. It now
    # shows output with seeds instead, and every frame it names must still be a
    # kept entry with a seed. So it cannot quietly start citing a withdrawn one.
    hero_src = (HERE / "build_hero.py")
    if hero_src.exists():
        # Scope to the PICKS literal. Matching ids across the whole file also
        # caught the string "utf-8", which looks exactly like an entry id.
        block = re.search(r'^PICKS = \[(.*?)^\]', hero_src.read_text(encoding="utf-8"),
                          re.S | re.M)
        picks = re.findall(r'"([a-z0-9-]+-\d+)"', block.group(1)) if block else []
        c(bool(picks), "build_hero.py declares a PICKS list")
        by_id = {e["id"]: e for e in entries}
        gone = [p for p in picks if p not in by_id]
        c(not gone, "every hero frame is still a kept entry",
          f"withdrawn or missing: {gone}")
        unseeded = [p for p in picks if p in by_id
                    and by_id[p].get("params", {}).get("seed") is None]
        c(not unseeded, "every hero frame has a seed to print", f"{unseeded}")

    # The long-form guide belongs beside the catalog, not between the hero and the
    # first image. Keep the landing page short and verify the guide separately.
    findings = HERE / "FINDINGS.md"
    findings_md = findings.read_text(encoding="utf-8") if findings.exists() else ""
    c(findings.exists(), "the Krea 2 prompt field guide is built")
    c("# Krea 2 prompt field guide" in findings_md,
      "the field guide has its practical title")
    guide_sections = ("A prompt order that is easy to adapt",
                      "Put the medium first when style is the goal",
                      "Write visible text explicitly",
                      "Use the library in ComfyUI")
    c(all(section in findings_md for section in guide_sections),
      "the field guide covers prompt structure, style, text, and ComfyUI")
    guide_old = [term for term in ("withdrawn", "correction", "the failures")
                 if term in findings_md.lower()]
    c(not guide_old, "the field guide stays focused on reusable instructions",
      f"found legacy framing: {guide_old}")
    # The catalog heading is localised, so read it out of the generator's own
    # translation table instead of hard-coding one string per language.
    for lang in _bc0.LANGS:
        name = "README.md" if lang == "en" else f"README_{lang.upper()}.md"
        path = HERE / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # The catalog heading is localised and now carries an emoji, so find it
        # by position: the last "## " before the first link into the gallery.
        # Matching on the heading text needed one hard-coded string per language
        # and broke the moment the headings changed.
        gi = text.find("](docs/gallery")
        heads = [l for l in text[:gi].splitlines() if l.startswith("## ")] if gi > 0 else []
        anchor = heads[-1] if heads else None
        if anchor is None or "hero.webp" not in text:
            c(False, f"{name} has a hero image and a catalog heading")
            continue
        gap = text.index(anchor) - text.index("</p>", text.index("hero.webp"))
        c(gap < 8000, f"{name}: hero to catalog is scannable",
          f"{gap:,} characters of prose before the first catalog entry: "
          f"move the long form into the prompt field guide")
        resources = ("FINDINGS.md", "VOCABULARY.md", "TEMPLATES.md", "styles/README.md",
                     "REPRODUCING.md")
        c(all(resource in text for resource in resources),
          f"{name} links to the practical prompt resources")

    # Deleted 2026-08-07. This required every translation to carry the findings
    # between the header and the catalog, which is exactly the shape the README
    # was rewritten out of. What matters now is that each one reaches the
    # evidence, and that is checked with the other per-language checks above.

    # The format chooser gives a reader a useful next action without scoring
    # other projects on hand-picked columns.
    cmp_p = HERE / "docs/comparison.md"
    c(cmp_p.exists(), "the library format chooser is built")
    cmp_text = cmp_p.read_text(encoding="utf-8") if cmp_p.exists() else ""
    chooser_links = ("sjh9714.github.io/krea2-wildcards", "gallery.md", "../wildcards/")
    c(all(link in cmp_text for link in chooser_links),
      "the format chooser links the web, GitHub, and ComfyUI surfaces")
    c("Failures shown" not in cmp_text and "Measured cost" not in cmp_text,
      "the format chooser describes usage instead of a scorecard")

    # The styles page is generated from styles/data.json and mirrors the Reddit
    # post of 2026-08-01. Its whole promise is that a reader arriving from the
    # post finds the exact clauses the post printed. A previous version of this
    # page drifted to a different subject and a superseded conclusion, which is
    # why this block exists: the page and the wildcards file must both match the
    # canonical data, and the older sweep must stay published as the appendix.
    # The negatives row quotes three numbers straight out of the manifest. The
    # row exists because the folklore ("models ignore negative prompts") was
    # about to go into the table as settled, and counting showed the effect is
    # nearly nothing. If the catalog grows and the numbers drift, the row is
    # wrong and this should fail before anyone reads it.
    # The gallery is 475 images on one page. Without an id per category and a
    # list to jump from, the only way to reach anything is to scroll, and a link
    # to one category cannot be handed to anyone who asks about it. Someone did
    # ask, in the thread, and the answer was a README anchor into a 6,000-line
    # page that lands mid-image while the lazy figures above it resolve.
    print("\ngallery anchors")
    page = HERE / "index.html"
    repo_url = f"https://github.com/{d['repo']}"
    site_url = f"https://{d['repo'].split('/')[0]}.github.io/{d['repo'].split('/')[-1]}/"
    release_zip = f"{repo_url}/releases/latest/download/krea2-wildcards.zip"
    if not page.exists():
        c(False, "index.html exists")
    else:
        h = page.read_text(encoding="utf-8")
        c(f'<link rel="canonical" href="{site_url}">' in h,
          "the gallery declares its canonical URL")
        og_tags = [
            '<meta property="og:type" content="website">',
            '<meta property="og:title"',
            '<meta property="og:description"',
            f'<meta property="og:url" content="{site_url}">',
            f'<meta property="og:image" content="{site_url}social-preview.webp">',
        ]
        missing_og = [tag for tag in og_tags if tag not in h]
        c(not missing_og, "the gallery publishes a complete Open Graph card",
          f"missing {missing_og}")
        actions = [release_zip, repo_url, f"{repo_url}/subscription",
                   "Download wildcards", "Star on GitHub", "Watch releases"]
        missing_actions = [action for action in actions if action not in h]
        c(not missing_actions, "the gallery exposes download, star, and release actions",
          f"missing {missing_actions}")
        cats = sorted({e["category"] for e in entries})
        missing = [x for x in cats if f'id="{x}"' not in h]
        c(not missing, f"every one of the {len(cats)} categories has an anchor",
          f"{missing[:5]}")
        untargeted = [x for x in cats if f'<option value="{x}">' not in h]
        c(not untargeted, "every category is reachable from the category filter",
          f"{untargeted[:5]}")
        c('id="top"' in h and 'href="#top"' in h,
          "the page has a top anchor and links back to it")
        c('id="failures"' not in h, "the main gallery contains only usable prompts")
        c("scroll-margin-top" in h,
          "headings carry a scroll margin",
          "without it an anchor lands under the viewport edge")

    print("\nsearch landing pages")
    import build_site as _site
    expected_urls = [site_url] if page.exists() else []
    for spec in _site.PAGES:
        guide = HERE / "guides" / spec["slug"] / "index.html"
        canonical = f"{site_url}guides/{spec['slug']}/" if page.exists() else ""
        expected_urls.append(canonical)
        c(guide.exists(), f"{spec['slug']}: landing page exists")
        if not guide.exists():
            continue
        text = guide.read_text(encoding="utf-8")
        needed = (f'<link rel="canonical" href="{canonical}">',
                  '<meta name="description"',
                  '<meta name="twitter:card" content="summary_large_image">',
                  '<script type="application/ld+json">',
                  "social-preview.webp")
        missing = [item for item in needed if item not in text]
        c(not missing, f"{spec['slug']}: search and social metadata is complete",
          f"missing {missing}")
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', text)
        try:
            schema = json.loads(match.group(1)) if match else {}
        except json.JSONDecodeError:
            schema = {}
        c(schema.get("@type") == "CollectionPage",
          f"{spec['slug']}: structured data parses as a collection")
        refs = set(re.findall(r'src="((?:\.\./)+images/[^"\s]+)', text))
        broken = [ref for ref in refs if not (guide.parent / ref).resolve().exists()]
        c(bool(refs) and not broken,
          f"{spec['slug']}: {len(refs)} generated example images resolve",
          f"broken {broken[:3]}")

    sitemap = HERE / "sitemap.xml"
    robots = HERE / "robots.txt"
    social = HERE / "social-preview.webp"
    sitemap_text = sitemap.read_text(encoding="utf-8") if sitemap.exists() else ""
    c(sitemap.exists() and all(f"<loc>{url}</loc>" in sitemap_text for url in expected_urls),
      f"sitemap publishes all {len(expected_urls)} public URLs")
    c(robots.exists() and f"Sitemap: {site_url}sitemap.xml" in
      (robots.read_text(encoding="utf-8") if robots.exists() else ""),
      "robots.txt points crawlers to the sitemap")
    c(social.exists() and social.stat().st_size > 20_000,
      "the large social preview image is built")

    print("\nstyles page")
    dpath = HERE / "styles/data.json"
    if not dpath.exists():
        c(False, "styles/data.json exists")
    else:
        sd = json.loads(dpath.read_text(encoding="utf-8"))
        page = HERE / "styles/README.md"
        c(page.exists(), "styles/README.md is built")
        text = page.read_text(encoding="utf-8") if page.exists() else ""

        imgs = [sd["hook"]["named_image"], sd["hook"]["rephrased_image"]]
        imgs += [g["image"] for g in sd["goods"].values()]
        imgs += [sd["never"]["rubberhose"]["image"], sd["never"]["doodle"]["image"]]
        imgs += sd["never"]["mosaic"]["images"]
        gone = sorted(i for i in imgs if not (HERE / "styles" / i).exists())
        c(not gone, f"all {len(imgs)} post images exist", f"{gone[:4]}")

        c(isinstance(sd.get("seed"), int) and len(sd.get("subject", "")) > 100,
          "the page records the pinned seed and the subject prompt")

        missing = [k for k, g in sd["goods"].items() if g["clause"] not in text]
        c(not missing, f"styles/README.md prints all {len(sd['goods'])} clauses verbatim",
          f"{missing[:4]}")
        c(sd["hook"]["named_clause"] in text and sd["hook"]["rephrased_clause"] in text,
          "the picture-book pair prints both phrasings verbatim")

        wc = HERE / "wildcards/styles.txt"
        if not wc.exists():
            c(False, "wildcards/styles.txt exists")
        else:
            lines = [l for l in wc.read_text(encoding="utf-8").splitlines() if l.strip()]
            want = [g["clause"] for g in sd["goods"].values()]
            c(len(lines) == len(want),
              f"wildcards/styles.txt is exactly the post's {len(want)} clauses",
              f"file has {len(lines)}")
            c(sorted(lines) == sorted(want),
              "every wildcard line is a clause the post printed")

        c("The ones that never converted" not in text and "Correction from" not in text,
          "the public style guide stays focused on reusable recipes")
        c("facing the viewer" in text and "simplified background detail" in text,
          "the style guide teaches a medium-friendly subject structure")

        # The appendix keeps the earlier sweep honest instead of deleting it.
        sw = HERE / "styles/sweep.json"
        c(sw.exists(), "the earlier sweep is still published (styles/sweep.json)")
        c("sweep.json" in text and "styles-extra.txt" in text,
          "styles/README.md links the appendix data and the extra wildcards")
        extra = HERE / "wildcards/styles-extra.txt"
        if sw.exists() and extra.exists():
            old = json.loads(sw.read_text(encoding="utf-8"))
            lines = [l for l in extra.read_text(encoding="utf-8").splitlines() if l.strip()]
            kept = [v["clause"] for v in old["kept"].values()]
            c(sorted(lines) == sorted(kept),
              f"styles-extra.txt is exactly the earlier sweep's {len(kept)} clauses")
        else:
            c(extra.exists(), "wildcards/styles-extra.txt exists")

        c(sd.get("post", "").startswith("https://www.reddit.com/"),
          "the page records which post it mirrors")
        c("README.md" in text or "../README.md" in text, "styles/README.md links back")
        c("styles/README.md" in readme or "styles/README.md" in findings_md, "README.md links to the styles page")
        c("](wildcards/)" in readme or "wildcards/styles.txt" in readme,
          "README.md reaches the wildcards files")

    # The catalog has to be readable without leaving GitHub. All five prompt
    # catalogs above 8,000 stars in this niche keep their prompts in the repo;
    # this one briefly did not, and a visitor who never clicked through to Pages
    # saw exactly one sample entry.
    gmap_p = HERE / "docs/gallery-map.json"
    c(gmap_p.exists(), "docs/gallery-map.json is built")
    if gmap_p.exists():
        gmap = json.loads(gmap_p.read_text(encoding="utf-8"))
        d = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
        cats = {e["category"] for e in d["entries"]
                if (HERE / e["image"]).exists()}
        c(cats == set(gmap["where"]),
          f"the gallery covers all {len(cats)} categories")
        dead = []
        for cat, fname in gmap["where"].items():
            f = HERE / "docs" / fname
            if not f.exists() or f"## {cat}" not in f.read_text(encoding="utf-8"):
                dead.append(cat)
        c(not dead, "every category link lands on its section"
                    + (f", but {dead} do not" if dead else ""))
        c("docs/gallery.md" in readme, "README.md points into the repo gallery")
        for cat in list(gmap["where"])[:5]:
            c(f"docs/{gmap['where'][cat]}#{cat}" in readme,
              f"README.md links {cat} to the file it is actually in")
        # Entries are printed once each; a duplicated or dropped category during
        # the split would be invisible without counting.
        shown = sum(f.read_text(encoding="utf-8").count("```text")
                    for f in (HERE / "docs").glob("gallery*.md"))
        c(shown == len(d["entries"]),
          f"the gallery prints every entry exactly once ({shown} of {len(d['entries'])})")
        back = sum(f.read_text(encoding="utf-8").count("](gallery.md#categories)")
                   for f in (HERE / "docs").glob("gallery-part-*.md"))
        if gmap["multi"]:
            c(back == len(d["entries"]),
              f"every entry links back to the index ({back})")

    # The gallery is now the path the README sends most readers down, so the copy
    # button is load-bearing. Three things can quietly break it: a button without
    # a prompt, a prompt that arrives with <mark> markup in it because someone
    # copied the rendered version, and an icon button with no accessible name.
    idx = HERE / "index.html"
    if idx.exists():
        html_t = idx.read_text(encoding="utf-8")
        dd3 = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
        shown = sum(1 for e in dd3["entries"]
                    if (HERE / e["image"]).exists())
        btns = len(re.findall(r'<button class=cp data-p=', html_t))
        c(btns == shown, f"every one of the {shown} gallery entries has a copy button"
                         + (f", found {btns}" if btns != shown else ""))
        cats = len({e["category"] for e in dd3["entries"]
                    if (HERE / e["image"]).exists()})
        alls = len(re.findall(r'class="cp all" data-cat=', html_t))
        c(alls == cats, f"every one of the {cats} categories has a copy-all button"
                        + (f", found {alls}" if alls != cats else ""))
        # Look for the tag, not the word: "felt-tip marker", "brand-mark" and
        # "landmark" are all real prompt text and the first version of this check
        # flagged 32 of them.
        dirty = [m for m in re.findall(r'data-p="([^"]*)"', html_t)
                 if "&lt;mark&gt;" in m or "<mark>" in m or "&lt;/mark" in m]
        c(not dirty, "no copy button carries display markup into the clipboard",
          f"{len(dirty)} do")
        noname = len(re.findall(r'<button class=cp(?![^>]*aria-label)', html_t))
        c(not noname, "every copy button has an accessible name",
          f"{noname} have none")
        c('id=q' in html_t and 'aria-label="Search the prompts"' in html_t,
          "the gallery has a labelled search box")
        c('id=category' in html_t and 'aria-label="Filter by category"' in html_t,
          "the gallery has a labelled category filter")
        c('id=favonly' in html_t and 'aria-pressed=false' in html_t
          and "localStorage" in html_t,
          "the gallery can save prompts locally and filter to saved prompts")
        favs = len(re.findall(r'<button class=fav[^>]*aria-label=', html_t))
        c(favs == shown, f"every one of the {shown} entries has an accessible save button"
                         + (f", found {favs}" if favs != shown else ""))
        stable = len(re.findall(r'<figure[^>]*data-id="[^"]+"[^>]*data-cat=', html_t))
        c(stable == shown, f"every one of the {shown} entries has a stable browser-save id"
                           + (f", found {stable}" if stable != shown else ""))
        c('<dialog id=viewer' in html_t and 'aria-label="Close image viewer"' in html_t,
          "the gallery has an accessible full-size image viewer")
        selects = len(re.findall(r'<button class=select[^>]*aria-label=', html_t))
        c(selects == shown, f"every one of the {shown} entries can be selected for comparison"
                             + (f", found {selects}" if selects != shown else ""))
        c('<dialog id=compareviewer' in html_t and 'id=compareselected' in html_t
          and 'id=downloadselected' in html_t,
          "the gallery compares and downloads selected prompts")
        c('id=exportsaved' in html_t and 'id=importsaved' in html_t
          and 'krea2-wildcards-favorites' in html_t,
          "saved prompts can be exported and imported")
        c('URLSearchParams' in html_t and 'history.replaceState' in html_t
          and 'id=share' in html_t and 'cardshare' in html_t,
          "filters and individual cards have shareable URLs")
        c('id=empty' in html_t, "the gallery has an empty state for combined filters")
        c('id="failures"' not in html_t and 'class=fail' not in html_t,
          "the prompt gallery stays focused on usable prompts")
        meta = re.search(r'<meta name="description" content="([^"]+)', html_t)
        c(bool(meta) and "failure" not in meta.group(1).lower(),
          "the gallery description leads with practical value")
        # The findings prose sat between the header and the first image: 9,758
        # pixels, eleven and a half screens, on the page the README points at.
        first_fig = html_t.find("<figure")
        c(0 < first_fig < 20_000,
          f"the first image is {first_fig:,} characters in, not behind the findings")

    # The vocabulary is the one place in this repo that points at specific words and
    # says they matter. That is exactly the kind of claim this catalog has had to
    # retract before, so the rule behind it (3+ entries, 2+ categories) is enforced
    # here as well as in the builder, and every warning has to still name a real
    # finding. If a term drifts below the rule the index quietly becomes an opinion.
    voc = HERE / "vocabulary.json"
    c(voc.exists(), "vocabulary.json exists")
    if voc.exists():
        import build_vocabulary as bv
        v, dd = bv.load()
        by = bv.usage(v, dd)
        thin = [t for t, r in by.items()
                if len(r["entries"]) < bv.MIN_ENTRIES
                or len(r["categories"]) < bv.MIN_CATEGORIES]
        c(not thin, f"all {len(by)} vocabulary terms meet the 3-entry 2-category rule"
                    + (f", but {thin} do not" if thin else ""))
        titles = {f["title"] for f in dd["findings"]["items"]}
        bad = [t for t, r in by.items() if r.get("finding") and r["finding"] not in titles]
        c(not bad, "every vocabulary warning names a finding that exists"
                   + (f", but {bad} do not" if bad else ""))
        vm = HERE / "VOCABULARY.md"
        c(vm.exists(), "VOCABULARY.md is built")
        if vm.exists():
            vtext = vm.read_text(encoding="utf-8")
            c(f"{len(by)} terms." in vtext,
              f"VOCABULARY.md is current at {len(by)} terms")
            warned = [t for t, r in by.items() if r.get("finding")]
            c(f"Precision notes for {len(warned)} terms" in vtext,
              f"VOCABULARY.md counts its {len(warned)} precision notes correctly")
            c("Each term recurs across several subjects and categories" in vtext,
              "VOCABULARY.md explains why the terms are transferable")
            c("at least 3 entries across at least 2 categories" in vtext,
              "VOCABULARY.md states the rule its terms had to meet")
        idx = HERE / "index.html"
        if idx.exists():
            n = idx.read_text(encoding="utf-8").count("<mark>")
            c(n > 300, f"the gallery marks the vocabulary ({n} marks)")

    # The download block is the first thing a reader from that subreddit sees, and
    # the format it advertises is the one that outscored everything else there. A
    # dead link or a wrong file size in it costs more than a wrong sentence lower
    # down, so the sizes are checked against the files rather than trusted.
    slug = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))["repo"]
    RAW = f"https://raw.githubusercontent.com/{slug}/main/wildcards/"
    RELEASE_ZIP = f"https://github.com/{slug}/releases/latest/download/krea2-wildcards.zip"
    zip_path = HERE / "wildcards/krea2-wildcards.zip"
    c(zip_path.exists(), "wildcards/krea2-wildcards.zip is built")
    # The first screen advertises one file, not three. A visitor who wants the
    # category split or the zip follows the wildcards/ link; a first screen that
    # lists every artefact is an inventory again, which is what this repo was
    # rewritten to stop doing.
    c(RAW + "all.txt" in readme, "README.md links the raw all.txt")
    c(RELEASE_ZIP in readme, "README.md links the stable release zip")
    c("](wildcards/)" in readme, "README.md links the wildcards folder")
    wildcard_readme = (HERE / "wildcards/README.md").read_text(encoding="utf-8")
    c(RELEASE_ZIP in wildcard_readme and "no custom node" in wildcard_readme.lower(),
      "the wildcard README links the release and requires no custom node")
    for f in ("all.txt", "krea2-wildcards.zip", "styles.txt"):
        c((HERE / "wildcards" / f).exists(), f"wildcards/{f} exists to be linked")
    for f, claimed in re.findall(
            r"\[([a-z0-9._-]+)\]\(" + re.escape(RAW) + r"[a-z0-9._-]+\)[^|]*\|[^|]*?(\d+) KB",
            readme):
        actual = round((HERE / "wildcards" / f).stat().st_size / 1024)
        c(abs(actual - int(claimed)) <= 2,
          f"README.md says {f} is {claimed} KB and it is {actual} KB")
    if zip_path.exists():
        import zipfile as _z
        names = set(_z.ZipFile(zip_path).namelist())
        c("all.txt" in names and "styles.txt" in names,
          f"the zip carries all.txt and styles.txt ({len(names)} files)")
        # build_wildcards.py used to unlink every *.txt in the folder, which
        # deleted build_styles.py's output whenever it ran second.
        c((HERE / "wildcards/styles.txt").exists()
          and (HERE / "wildcards/styles-extra.txt").exists(),
          "build_wildcards.py left the styles files alone")

    # REPRODUCING.md exists because the headline claim ("every entry carries its
    # seed") reads as a promise of reproducibility that the hosted endpoint cannot
    # keep. The endpoint publishes no step count, CFG, sampler or scheduler, so the
    # seed is good on fal and worthless in a local graph. If that caveat ever falls
    # out of the README, the repo goes back to overselling the one column it wins.
    rep = HERE / "REPRODUCING.md"
    c(rep.exists(), "REPRODUCING.md exists")
    if rep.exists():
        rtext = rep.read_text(encoding="utf-8")
        c("REPRODUCING.md" in readme or "REPRODUCING.md" in findings_md, "README.md links to REPRODUCING.md")
        c("reproduce" in rtext and "local" in rtext,
          "REPRODUCING.md states the seeds do not reproduce locally")
        for term in ("fal-ai/krea-2/turbo", "square_hd", "enable_prompt_expansion",
                     "openapi.json"):
            c(term in rtext, f"REPRODUCING.md names {term}")
        for absent in ("guidance scale", "sampler", "scheduler"):
            c(absent in rtext,
              f"REPRODUCING.md says the endpoint has no {absent}")
        # The payload documented there has to be the payload the generator sends.
        gen = (HERE / "scripts/gen_fal.py").read_text(encoding="utf-8")
        c('"image_size": args.image_size, "enable_safety_checker": True' in gen
          or "'image_size': args.image_size" in gen,
          "gen_fal.py still sends the payload REPRODUCING.md documents")
        d = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
        edits = [e for e in d["entries"] if e["category"] == "editing"]
        c(all("strength" in e and "source" in e for e in edits),
          f"all {len(edits)} editing entries carry source and strength")
        c(all("seed" in e.get("params", {}) or "generation_id" in e.get("params", {})
              for e in d["entries"]),
          "every entry carries a seed or Krea generation asset ID")

    # The README carried 19,605 characters of failure table, 56% of the file and a
    # verbatim duplicate of docs/gallery-failures.md and index.html, while the
    # section on how to use the thing was 406 characters. Fifteen of fifteen
    # comparable repos have no failures section; the three biggest winners spend
    # their largest section on install or configuration. These three guards keep
    # that inversion from coming back, because writing evidence is the easy part.
    rd_bytes = len(readme.encode("utf-8"))
    c(rd_bytes < 8_000,
      f"README is {rd_bytes // 1024} KB, under the 8 KB ceiling")
    c("images/failures/" not in readme,
      "the README does not re-inline the failures",
      f"{readme.count('images/failures/')} failure images are back in it")
    for token in ("ComfyUI/wildcards/", "__all__"):
        c(token in readme, f"the usage section names {token}")
    # __wildcard__ is not a ComfyUI feature. Someone without the extension gets
    # the literal string "__all__" in their image and no error explaining it, so
    # naming the extension is not politeness, it is the difference between the
    # instructions working and silently not.
    c("comfyui-dynamicprompts" in readme,
      "the usage section names the extension the wildcard syntax needs")
    c(any(x in readme for x in ("not built into", "not a ComfyUI feature",
                                "does not come with")),
      "the README says the wildcard syntax is not something ComfyUI ships")
    # And the path most readers take has to be first.
    gal = readme.find("press **copy** under any picture")
    wc = readme.find("On ComfyUI you can wire it up")
    c(0 < gal < wc, "the README leads with the path that needs no install")

    # The first screen sells what you take away. It used to sell how rigorous we
    # were: a 109-character tagline listing 475 prompts, 65 failures and 61
    # categories, then a three-row download table and two paragraphs of caveats
    # about seeds that do not transfer. None of that is a reason to click.
    # These two guards exist because that framing is the comfortable one to write
    # and it will creep back the moment nobody is looking.
    FIRST = 1500
    BANNED = ("seed", "failed", "measured")
    for lang in _bc0.LANGS:
        name = "README.md" if lang == "en" else f"README_{lang.upper()}.md"
        path = HERE / name
        if not path.exists():
            continue
        head = path.read_text(encoding="utf-8")[:FIRST]
        # Strip HTML attributes first. Alt text has to describe the image
        # truthfully, including the seeds printed on it, and no sighted visitor
        # reads it. The rule is about visible prose.
        visible = re.sub(r'<[^>]*>', ' ', head).lower()
        found = [w for w in BANNED if w in visible]
        c(not found, f"{name}: the first screen sells the takeaway, not the rigour"
                     + (f", found {found}" if found else ""))

    tag = re.search(r'<p align="center">([^<]{10,200})</p>',
                    (HERE / "README.md").read_text(encoding="utf-8"))
    if tag:
        n_tag = len(tag.group(1).strip())
        c(n_tag <= 80, f"the tagline is {n_tag} characters, at or under 80")

    # An em dash in a reply to the subreddit this repo launched in got the account
    # labelled "worthless LLM slop" inside four minutes, and the label stuck harder
    # than any of the corrections. The prose here carries none. The ones inside
    # prompt strings stay, because a prompt is the exact text that produced its
    # image and editing it would break the one thing this catalog sells.
    DASH = ("—", "–")
    dd2 = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    in_prompts = sum(p.count(x) for e in dd2["entries"]
                     for p in [e["prompt"]] for x in DASH)
    prose = ["README.md", "FINDINGS.md", "VOCABULARY.md", "TEMPLATES.md",
             "EDITING_RECIPES.md",
             "REPRODUCING.md", "CONTRIBUTING.md", "styles/README.md",
             "wildcards/README.md"] + [f"README_{x.upper()}.md"
                                       for x in _bc0.LANGS if x != "en"]
    dirty = []
    for name in prose:
        p2 = HERE / name
        if p2.exists() and any(x in p2.read_text(encoding="utf-8") for x in DASH):
            dirty.append(name)
    c(not dirty, f"no em or en dash in any of the {len(prose)} prose documents"
                 + (f", but {dirty} carry one" if dirty else ""))
    for name in ("index.html", "docs/gallery-part-1.md", "docs/gallery-part-2.md",
                 "docs/gallery-part-3.md"):
        p2 = HERE / name
        if not p2.exists():
            continue
        body = p2.read_text(encoding="utf-8")
        # The gallery now carries every prompt twice: once rendered inside <pre>
        # with the vocabulary marked, once verbatim in the copy button's data-p.
        # Counting both doubled the total and failed a guard that was right.
        body_nodup = re.sub(r'data-p="[^"]*"', "", body)
        found = sum(body_nodup.count(x) for x in DASH)
        if name == "index.html":
            c(found == in_prompts,
              f"index.html's {found} dashes are all inside prompt text "
              f"({in_prompts} in the manifest)")
    # And nothing in the source may reintroduce one, including as an escape.
    src_dirty = []
    for p2 in list(HERE.glob("build_*.py")) + list(HERE.glob("scripts/*.py")) \
            + [HERE / "vocabulary.json", HERE / "styles/data.json"]:
        s2 = p2.read_text(encoding="utf-8")
        if any(x in s2 for x in DASH) or "u2014" in s2 or "u2013" in s2:
            src_dirty.append(p2.name)
    c(not src_dirty, "no builder emits a dash"
                     + (f", but {src_dirty} do" if src_dirty else ""))

    # Templates are the one place this repo hands out a shape instead of a
    # measurement, so each one has to keep naming the measurement it came from.
    tpl_p = HERE / "TEMPLATES.md"
    c(tpl_p.exists(), "TEMPLATES.md is built")
    if tpl_p.exists():
        import build_templates as bt
        dd = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
        vv = json.loads((HERE / "vocabulary.json").read_text(encoding="utf-8"))
        items = dd["templates"]["items"]
        unresolved = [i["name"] for i in items
                      if not bt.resolve(i["evidence"], dd, vv)[0]]
        c(not unresolved, f"all {len(items)} templates cite evidence that exists"
                          + (f", but {unresolved} do not" if unresolved else ""))
        tt = tpl_p.read_text(encoding="utf-8")
        c(all(i["name"] in tt for i in items), "TEMPLATES.md is current")
        c(all(f"[{s}]" in i["template"] for i in items for s in i["slots"]),
          "every declared slot appears in its template")
        c("TEMPLATES.md" in readme or "TEMPLATES.md" in findings_md, "README.md links TEMPLATES.md")

    print("\nprompt quality and editing recipes")
    from scripts.audit_prompts import audit as audit_prompts
    prompt_errors, prompt_summary = audit_prompts(HERE / "prompts.json")
    c(not prompt_errors,
      f"all {prompt_summary['prompts']} prompts pass duplicate and length checks",
      f"{prompt_errors[:3]}")
    c(prompt_summary["prompts"] == prompt_summary["unique"],
      "every published prompt is unique after whitespace normalization")
    recipes = HERE / "EDITING_RECIPES.md"
    recipe_text = recipes.read_text(encoding="utf-8") if recipes.exists() else ""
    c(recipes.exists(), "EDITING_RECIPES.md is built")
    c(all(f"### {index}. {name}" in recipe_text
          for index, (name, _) in enumerate(_site.EDIT_RECIPES, 1)),
      f"the editing guide publishes all {len(_site.EDIT_RECIPES)} reusable recipes")
    edit_ids = [e["id"] for e in entries if e["category"] == "editing"]
    c(all(entry_id in recipe_text for entry_id in edit_ids),
      f"the editing guide links all {len(edit_ids)} generated editing examples")
    c("EDITING_RECIPES.md" in readme, "README.md links the editing recipes")

    # Credit is a growth loop and a debt at the same time. The reference catalog
    # in this niche credits every prompt to whoever wrote it and links the post it
    # came from, and those people carry it further. The debt is that a half-filled
    # credit is worse than none: a name with no link is unverifiable, and an entry
    # borrowed from someone with no licence is a problem rather than a credit.
    d = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    att = d.get("attribution")
    c(bool(att), "prompts.json declares how attribution works")
    if att:
        c(bool(att.get("owner") and att.get("owner_link")),
          "the default author is named and linked")
        bad = []
        for e in d["entries"] + d.get("failures", {}).get("entries", []):
            who = e.get("prompt_author")
            if who and not e.get("prompt_author_link"):
                bad.append(f"{e['id']} names an author with no link")
            if who and not e.get("license"):
                bad.append(f"{e['id']} is someone else's with no licence")
            if e.get("source_links") and not who:
                bad.append(f"{e['id']} links a source but credits nobody")
            for u in e.get("source_links", []):
                if not str(u).startswith("http"):
                    bad.append(f"{e['id']} has a source_link that is not a URL")
        c(not bad, "every credited entry is completely credited"
                   + (f": {bad[:4]}" if bad else ""))
        credited = [e for e in d["entries"] if e.get("prompt_author")]
        c(True, f"{len(credited)} of {len(d['entries'])} entries carry their own "
                f"attribution; the rest are the owner's own runs")
        c("prompt_author" in (HERE / "build_gallery.py").read_text(encoding="utf-8")
          and "prompt_author" in (HERE / "build_pages.py").read_text(encoding="utf-8"),
          "both renderers print attribution when it is there")

    # Contribution is a machine or it does not happen. The reference case in this
    # niche has 1,807 forks and no push in fourteen months because an issue form,
    # a validating workflow and a regenerating workflow do the work. Ours only
    # holds if the three files are actually there.
    gh = HERE / ".github"
    c((gh / "ISSUE_TEMPLATE/add_entry.yml").exists(),
      "there is an issue form for adding an entry")
    c((gh / "workflows/verify.yml").exists(), "CI runs verify.py")
    c((gh / "workflows/rebuild.yml").exists(),
      "a workflow regenerates the documents when the manifest changes")
    contrib = HERE / "CONTRIBUTING.md"
    if contrib.exists():
        ct = contrib.read_text(encoding="utf-8")
        c("template=add_entry.yml" in ct, "CONTRIBUTING.md leads with the issue form")
        c("prompt_author" in ct, "CONTRIBUTING.md documents the attribution fields")
        for b in ("build_gallery.py", "build_vocabulary.py", "build_site.py",
                  "build_social.py", "scripts/build_workflows.py",
                  "scripts/build_dataset.py", "scripts/audit_prompts.py"):
            c(b in ct, f"CONTRIBUTING.md lists {b} in the build order")

    print()
    if c.failures:
        print(f"{len(c.failures)} failed, {c.passed} passed")
        for f in c.failures:
            print(f"  - {f}")
        return 1
    print(f"all {c.passed} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
