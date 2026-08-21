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

    print("seeds")
    seed = lambda e: (e.get("params") or {}).get("seed")
    missing = [e["id"] for e in both if seed(e) is None]
    c(not missing, f"all {len(both)} generations carry a seed", f"missing on {missing[:5]}")

    print("\nimages")
    named = {e["image"] for e in both}
    absent = sorted(p for p in named if not (HERE / p).exists())
    c(not absent, f"all {len(named)} manifest images exist", f"{absent[:5]}")

    on_disk = {str(p.relative_to(HERE)) for p in HERE.glob("images/**/*.webp")}
    orphans = sorted(on_disk - named - {"hero.webp"})
    c(not orphans, f"no orphan images among {len(on_disk)} on disk", f"{orphans[:5]}")

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
      and re.fullmatch(r"\d+\.\d+\.\d+", schema_version) is not None,
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

    # A reader who lands here wants to see output. The findings prose used to sit
    # between the hero image and the catalog as 48,527 unbroken characters: about
    # 24 screens with no image in them, against 6,172-11,318 for the three repos
    # in the comparison table below. It now lives in FINDINGS.md behind a summary
    # table. If it creeps back, this fails.
    findings = HERE / "FINDINGS.md"
    findings_md = findings.read_text(encoding="utf-8") if findings.exists() else ""
    # "Fourteen findings" sat in the summary while there were 15, for as long as
    # the negatives finding had existed. counts() substitutes {findings}; a number
    # spelled as a word walks straight past it and past every count check here.
    WORDS = r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|" \
            r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b"
    head = findings_md[:400] if findings.exists() else ""
    spelled = re.findall(WORDS + r"\s+findings", head, re.I)
    c(not spelled, "the findings intro counts in digits, not words",
      f"found {spelled}")
    c(findings.exists(), "FINDINGS.md exists", "the long-form evidence has to live somewhere")
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
          f"move the long form into FINDINGS.md")
        c("FINDINGS.md" in text, f"{name} links to FINDINGS.md")

    # Deleted 2026-08-07. This required every translation to carry the findings
    # between the header and the catalog, which is exactly the shape the README
    # was rewritten out of. What matters now is that each one reaches the
    # evidence, and that is checked with the other per-language checks above.

    # The comparison table describes this repo to a reader who is deciding
    # between it and a 13,000-star competitor, and it is written by hand. It sat
    # at "85 prompts / 93 images / 8 failures / $1.26 / 150 gens", the first
    # batch, for five batches, understating the catalog roughly five-fold in the
    # one place built to argue it is worth using. Nothing above catches that,
    # because every other check reads the generated prose.
    # Moved out of the README on 2026-08-06: seven of seven reference repos carry
    # no comparison section, and a table scoring us on columns we chose is an
    # argument with other catalogs rather than an answer to the visitor.
    cmp_p = HERE / "docs/comparison.md"
    c(cmp_p.exists(), "docs/comparison.md is built")
    cmp_text = cmp_p.read_text(encoding="utf-8") if cmp_p.exists() else ""
    c("docs/comparison.md" in readme or "docs/comparison.md" in findings_md, "README links the comparison")
    row = re.search(r"^\|\s*\*\*this repo\*\*\s*\|(.+)$", cmp_text, re.M)
    if row is None:
        c(False, "comparison table has a 'this repo' row")
    else:
        cells = [x.strip() for x in row.group(1).split("|") if x.strip()]
        images_on_disk = len(list((HERE / "images").rglob("*.webp")))
        # Checked per cell, not against the row as a whole: the first version of
        # this check searched the whole row, so replacing the prompt count with a
        # stale 85 still passed because "all 475" two cells over kept 475 present.
        # A tamper test caught it. Column order matches the header above.
        want = [
            ("Prompts", len(entries)),
            ("Images in repo", images_on_disk),
            ("Seeds / params", len(entries)),
            ("Failures shown", len(failures)),
            ("Measured cost", gens),
        ]
        bad = []
        for i, (col, expect) in enumerate(want):
            got = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", cells[i])] \
                if i < len(cells) else []
            if expect not in got:
                bad.append(f"{col}: expected {expect}, cell reads {cells[i]!r}"
                           if i < len(cells) else f"{col}: cell missing")
        c(not bad, "docs/comparison.md matches the manifest, cell by cell",
          "; ".join(bad))
        spend = d.get("spend")
        c(spend is None or f"{spend}" in cells[-1],
          f"comparison table quotes the real spend (${spend})",
          f"cost cell reads {cells[-1]!r}" if cells else "")

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
    if not page.exists():
        c(False, "index.html exists")
    else:
        h = page.read_text(encoding="utf-8")
        cats = sorted({e["category"] for e in entries})
        missing = [x for x in cats if f'id="{x}"' not in h]
        c(not missing, f"every one of the {len(cats)} categories has an anchor",
          f"{missing[:5]}")
        untargeted = [x for x in cats if f'href="#{x}"' not in h]
        c(not untargeted, "every category is reachable from the jump list",
          f"{untargeted[:5]}")
        c('id="top"' in h and 'href="#top"' in h,
          "the page has a top anchor and links back to it")
        c('id="failures"' in h, "the failures section has an anchor")
        c("scroll-margin-top" in h,
          "headings carry a scroll margin",
          "without it an anchor lands under the viewport edge")

    print("\nnegatives row")
    NEG = re.compile(r"\b(no|nothing|nobody|without|never)\b\s+\w", re.I)
    IGN = re.compile(r"asked for (no|nobody|nothing)|no face in frame|"
                     r"nobody in the reflection|hangers showing", re.I)
    with_neg = [r for r in both if NEG.search(r["prompt"])]
    fail_neg = [r for r in failures if NEG.search(r["prompt"])]
    rate_with = len(fail_neg) / len(with_neg) * 100
    rate_without = ((len(failures) - len(fail_neg))
                    / (len(both) - len(with_neg)) * 100)
    outright = [r for r in failures if IGN.search(r.get("claim", ""))]

    # The findings table left the README on 2026-08-07; the numbers still
    # have to be checkable, they are just checked where they now live.
    row = re.search(r"^\|\s*\*\*Negatives\*\*\s*\|(.+)$", findings_md, re.M)
    c(row is not None, "FINDINGS.md has a Negatives row")
    if row:
        cell = row.group(1)
        for want, label in ((f"{rate_with:.1f}%", "the with-negative failure rate"),
                            (f"{rate_without:.1f}%", "the without-negative rate"),
                            (f"{len(outright)} of {len(failures)}",
                             "the count of outright ignored negatives")):
            c(want in cell, f"Negatives row quotes {label} ({want})",
              f"row reads {cell.strip()[:120]}")
    c((HERE / "scripts/measure_negatives.py").exists(),
      "the script that produces those numbers is published")

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

        # The refusals are the finding; losing them turns this back into a
        # pretty gallery. And a refusal must never migrate into the goods.
        c(len(sd.get("refusals", [])) >= 3, "the page still publishes its refusals")
        c(not set(sd.get("refusals", [])) & set(sd["goods"]),
          "no refusal is listed among the goods")

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
        shown = sum(1 for e in dd3["entries"] + dd3.get("failures", {}).get("entries", [])
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
            c(f"Read these {len(warned)} before you use them" in vtext,
              f"VOCABULARY.md counts its {len(warned)} warnings correctly")
            # Assert the disclaimer is present rather than that the word "caused"
            # is absent; the disclaimer itself contains it, and the first version
            # of this check failed on the sentence it was written to protect.
            c("Nothing here is a claim that a term caused a particular image" in vtext,
              "VOCABULARY.md still disclaims the causal reading")
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
    zip_path = HERE / "wildcards/krea2-wildcards.zip"
    c(zip_path.exists(), "wildcards/krea2-wildcards.zip is built")
    # The first screen advertises one file, not three. A visitor who wants the
    # category split or the zip follows the wildcards/ link; a first screen that
    # lists every artefact is an inventory again, which is what this repo was
    # rewritten to stop doing.
    c(RAW + "all.txt" in readme, "README.md links the raw all.txt")
    c("](wildcards/)" in readme, "README.md links the wildcards folder")
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
        c(all("seed" in e.get("params", {}) for e in d["entries"]),
          "every entry carries a seed")

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
    c("docs/gallery-failures.md" in readme or "docs/gallery-failures.md" in findings_md, "README links where the failures live")
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
    # than any of the corrections. The prose here carries none. The 29 inside
    # prompt strings stay, because a prompt is the exact text that produced its
    # image and editing it would break the one thing this catalog sells.
    DASH = ("—", "–")
    dd2 = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    in_prompts = sum(p.count(x) for e in dd2["entries"]
                     + dd2.get("failures", {}).get("entries", [])
                     for p in [e["prompt"]] for x in DASH)
    prose = ["README.md", "FINDINGS.md", "VOCABULARY.md", "TEMPLATES.md",
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
        for b in ("build_gallery.py", "build_vocabulary.py"):
            c(b in ct, f"CONTRIBUTING.md lists {b} in the build order")

    # The number of checks is quoted in CONTRIBUTING.md, so it is a claim like any
    # other in this repo and it drifts the moment a check is added.
    if contrib.exists():
        total = c.passed + len(c.failures) + 1
        claimed = re.search(r"runs (\d+) checks", contrib.read_text(encoding="utf-8"))
        c(bool(claimed) and int(claimed.group(1)) == total,
          f"CONTRIBUTING.md says {claimed.group(1) if claimed else '?'} checks "
          f"and there are {total}")

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
