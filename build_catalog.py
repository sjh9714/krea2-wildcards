#!/usr/bin/env python3
"""
build_catalog.py, assemble a T+0 prompt/asset catalog README from a manifest.

The window for this play is 72 hours from a frontier model shipping. Measured
outcomes for the same slot, five payouts in nine months:

    YouMind-OpenLab/awesome-nano-banana-pro-prompts   12,949   created 2025-11-23
    ZeroLu/awesome-nanobanana-pro                     10,186   created 2025-11-10
    YouMind-OpenLab/awesome-gpt-image-2                8,761   created 2026-04-16
    freestylefly/awesome-gpt-image-2                   8,678   created 2026-04-25
    jamez-bondos/awesome-gpt4o-images                  8,097   created 2025-04-13

Two structural facts most people get wrong about this slot:

  1. It is NON-RIVAL. nano-banana produced 12,949 AND 10,186. gpt-image-2 produced
     8,761 AND 8,678 nine days apart. Second place is paid.
  2. Late is fatal in a way second-place is not. ZeroLu/awesome-gpt-image, launched
     two weeks after the same author's own hit, sits at 1,928: 22% of it.

So: ship inside 72 hours, do not agonize about someone beating you by a day, and
do not ship at all if you are two weeks late.

This script does the assembly so that on launch day you are only doing the part
that cannot be automated: curation. Generation is a separate step you own , 
`--gen-cmd` shells out to whatever CLI your provider gives you.

Usage
-----
    python3 build_catalog.py --init                     # scaffold prompts.json
    python3 build_catalog.py --generate                 # run gen-cmd for missing images
    python3 build_catalog.py --build                    # write README.md + index
    python3 build_catalog.py --build --lang zh          # also emit README_ZH.md
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Every catalog above 8,000 stars in this niche ships translations; the
# largest ships twelve. The body evidence stays in English, so these are
# the navigation and the framing, not the findings.
# Every catalog above 8,000 stars in this niche puts an emoji on its headings.
# Restrained on purpose: one per top-level section in the README and nowhere
# else. The evidence documents stay plain, because this repo's whole claim is
# that it measures things the emoji-heavy catalogs do not, and it was called
# "worthless LLM slop" on the subreddit it launched in. Decorated evidence reads
# like the thing that accusation was about. Set EMOJI = {} to drop them.
EMOJI = {
    "copy": "📋",
    "all": "📥",
    "toc": "🗂",
    "sample": "",
    "i2i": "🔁",
    "check": "✅",
    "failures": "❌",
    "compare": "📊",
    "contrib": "🤝",
    "license": "⚖",
}


def h2(key: str, text: str) -> str:
    e = EMOJI.get(key)
    return f"## {e} {text}\n" if e else f"## {text}\n"


LANGS = ["en", "zh", "ko", "ja", "es", "fr", "de", "pt"]

from build_vocabulary import load as _load_vocab, mark, term_pattern
VOCAB_MD = term_pattern([x["t"] for x in _load_vocab()[0]["terms"]])
MANIFEST = HERE / "prompts.json"
IMAGES = HERE / "images"

SCAFFOLD = {
    "model": "REPLACE-ME (exact model name and version, e.g. 'Nano Banana Pro')",
    "model_url": "",
    "launched": "2026-01-01",
    "repo": "yourname/awesome-<model>-prompts",
    "gen_cmd": "echo 'replace with your provider CLI: {prompt} -> {out}'",
    "categories": OrderedDict([
        ("photography", "Photoreal scenes, lighting, lens behaviour"),
        ("illustration", "Stylised and painterly output"),
        ("typography", "Text rendering, posters, logotype"),
        ("product", "Product shots, packaging, studio lighting"),
        ("infographic", "Charts, diagrams, explanatory layouts"),
        ("character", "Character consistency across generations"),
        ("text-in-image", "Legible text, multiple languages"),
        ("editing", "Inpainting, object removal, relighting"),
        ("3d-isometric", "Isometric scenes, dioramas, game assets"),
        ("brand", "Logos, marks, identity systems"),
    ]),
    "entries": [
        {
            "id": "photography-001",
            "category": "photography",
            "title": "Golden hour portrait, 85mm",
            "prompt": "A portrait of ...",
            "image": "images/photography-001.png",
            "params": {"aspect_ratio": "3:4", "seed": 1234},
            "notes": "Reproduces reliably. Seed matters for the rim light.",
        }
    ],
}


def load() -> dict:
    if not MANIFEST.exists():
        print(f"no {MANIFEST.name}; run --init first", file=sys.stderr)
        raise SystemExit(2)
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def cmd_init() -> int:
    if MANIFEST.exists():
        print(f"{MANIFEST.name} already exists; not overwriting", file=sys.stderr)
        return 1
    MANIFEST.write_text(json.dumps(SCAFFOLD, indent=2, ensure_ascii=False), encoding="utf-8")
    IMAGES.mkdir(exist_ok=True)
    print(f"wrote {MANIFEST.name} and images/\n")
    print("Now, in this order:")
    print("  1. Set `model`, `repo`, `launched`, `gen_cmd`.")
    print("  2. Draft 20-25 prompts per category into `entries`. 8-12 categories.")
    print("  3. --generate, then throw away 40-50% of the output. That is the job.")
    print("  4. --build")
    return 0


def cmd_generate(force: bool) -> int:
    data = load()
    tmpl = data.get("gen_cmd", "")
    if not tmpl or tmpl.startswith("echo 'replace"):
        print("set `gen_cmd` in prompts.json first (use {prompt} and {out} placeholders)",
              file=sys.stderr)
        return 2

    IMAGES.mkdir(exist_ok=True)
    todo = [e for e in data["entries"] if force or not (HERE / e["image"]).exists()]
    if not todo:
        print("nothing to generate; every entry already has an image")
        return 0

    print(f"generating {len(todo)} image(s)\n")
    failed = []
    for i, e in enumerate(todo, 1):
        out = HERE / e["image"]
        out.parent.mkdir(parents=True, exist_ok=True)
        # shell=True is deliberate: `gen_cmd` is a user-authored command line from
        # their own prompts.json, and provider CLIs routinely need pipes and
        # redirects. The injection surface is closed by shlex.quote on both
        # interpolated values, so prompt text cannot escape into the shell no
        # matter what a contributor puts in a PR.
        cmd = tmpl.replace("{prompt}", shlex.quote(e["prompt"])).replace("{out}", shlex.quote(str(out)))
        print(f"[{i}/{len(todo)}] {e['id']}", end=" ", flush=True)
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa: S602
        if p.returncode != 0 or not out.exists():
            failed.append((e["id"], (p.stderr or p.stdout)[:200]))
            print("FAIL")
        else:
            print(f"ok ({out.stat().st_size // 1024} KB)")

    if failed:
        print(f"\n{len(failed)} failed:", file=sys.stderr)
        for eid, why in failed:
            print(f"  {eid}: {why}", file=sys.stderr)
    print("\nNow curate. Delete every image you would not put in a portfolio.\n"
          "Target: keep 50-60% of what you generated. One bad image in a catalog\n"
          "discredits the whole catalog, and this format's only moat is taste.")
    return 0


def gh_anchor(text: str) -> str:
    """GitHub's heading-anchor rule: lowercase, drop anything that is not
    alphanumeric/space/hyphen, then spaces to hyphens. Source links must be built
    from the target entry's TITLE, because that is what becomes the heading: an
    earlier version linked to the entry id and produced five dead anchors."""
    import re as _re
    return _re.sub(r"[^a-z0-9 -]", "", text.lower()).strip().replace(" ", "-")


def counts(data: dict, s: str) -> str:
    """Substitute count placeholders from the manifest.

    These numbers drifted once and it was the worst possible kind of drift. The
    hands category was withdrawn, the subtitle and the findings were updated to
    476 kept / 64 cut, and this paragraph went on saying 483 and 78. So a
    document whose entire argument is that the counts were checked contradicted
    itself two paragraphs apart, on the page a public post was pointing at.

    A count that has to be retyped when the data changes will eventually be
    wrong. Substituted, it cannot be. str.replace rather than str.format so a
    stray brace in prose cannot raise."""
    for token, value in (("{generations}", data.get("generations", 0)),
                         ("{kept}", len(data.get("entries", []))),
                         ("{failures}", len(data.get("failures", {}).get("entries", []))),
                         ("{discarded}", data.get("discarded_generations", 0)),
                         ("{findings}", len(data.get("findings", {}).get("items", [])))):
        s = s.replace(token, f"{value:,}" if value >= 10000 else str(value))
    return s


def render_readme(data: dict, lang: str = "en") -> str:
    entries = data["entries"]
    cats: OrderedDict[str, list] = OrderedDict()
    for e in entries:
        cats.setdefault(e["category"], []).append(e)

    kept = [e for e in entries if (HERE / e["image"]).exists()]
    n, ncat = len(kept), len(cats)
    nfail = len((data.get('failures') or {}).get('entries', []))
    model = data.get("model", "the model")

    T = {
        "en": {
            "gallery_link": "Browse the gallery →",
            "copy_h": "Copy one",
            "all_h": "Or take all 475",
            "toc_entries": "prompts, every one with its seed",
            "tagline": f"{n} {model} prompts, each with the picture it made. Click to copy.",
            "toc": "Categories",
            "prompt": "Prompt",
            "contrib": "Contributing",
            "contrib_body": "Open a PR adding an entry to `prompts.json` plus your output image. Two rules: the prompt must reproduce, and the image must be the unedited output.",
            "license": "License",
            "license_body": ("Prompts are MIT, take them.\n\n"
                "**The images are AI-generated.** They were produced with Krea 2 Turbo and are "
                "presented as model output, not as photographs or human artwork. Under the Krea 2 "
                "Community License you own outputs you generate yourself; commercial use is "
                "permitted below $1M annual company revenue, and the licence separately requires "
                "content filtering, which was left enabled for every image here. One entry was "
                "dropped after the safety checker flagged it.\n\n"
                "Nothing here was retouched, upscaled or cropped. Every seed is recorded so you "
                "can regenerate the exact file."),
        },
        "zh": {
            "gallery_link": "浏览画廊 →",
            "copy_h": "复制一条",
            "all_h": "或者全部拿走",
            "toc_entries": "条提示词，每条都有 seed",
            "tagline": f"{n} 条 {model} 提示词，每条都配着它生成的图。点一下就复制。",
            "toc": "类别",
            "prompt": "提示词",
            "contrib": "参与贡献",
            "contrib_body": "提交 PR，在 `prompts.json` 中添加条目并附上你的输出图片。两条规则：提示词必须可复现，图片必须是未经编辑的原始输出。",
            "license": "许可",
            "license_body": "提示词采用 MIT 许可。生成的图片受模型提供方条款约束，商用前请自行确认。",
        },
        "ko": {
            "gallery_link": "갤러리 보기 →",
            "copy_h": "하나만 복사",
            "all_h": "아니면 전부 가져가기",
            "toc_entries": "개 프롬프트, 전부 시드 기록",
            "tagline": f"{model} 프롬프트 {n}개, 각각 그걸로 나온 사진까지. 눌러서 복사.",
            "toc": "카테고리",
            "prompt": "프롬프트",
            "contrib": "기여하기",
            "contrib_body": "`prompts.json`에 항목을 추가하고 출력 이미지를 첨부해 PR을 보내주세요. 규칙 두 개: 프롬프트는 재현 가능해야 하고, 이미지는 편집하지 않은 원본이어야 합니다.",
            "license": "라이선스",
            "license_body": "프롬프트는 MIT입니다. 생성된 이미지는 모델 제공자의 약관을 따릅니다, 상업적 사용 전 확인하세요.",
        },
        "ja": {
            "gallery_link": "ギャラリーを見る →",
            "copy_h": "1 つコピー",
            "all_h": "まとめて持っていく",
            "toc_entries": "件のプロンプト、すべてシード付き",
            "tagline": f"{model} プロンプト {n} 件、それぞれ生成された画像つき。押せばコピー。",
            "toc": "カテゴリ",
            "prompt": "プロンプト",
            "contrib": "コントリビュート",
            "contrib_body": "`prompts.json` にエントリを追加し、出力画像を添えて PR を送ってください。ルールは 2 つ、プロンプトは再現可能であること、画像は未編集の出力であることです。",
            "license": "ライセンス",
            "license_body": "プロンプトは MIT です。生成画像はモデル提供者の規約に従います。商用利用の前に確認してください。",
        },
        "es": {
            "gallery_link": "Ver la galería →",
            "copy_h": "Copia uno",
            "all_h": "O llévatelos todos",
            "toc_entries": "prompts, cada uno con su semilla",
            "tagline": f"{n} prompts de {model}, cada uno con la imagen que produjo. Pulsa y copia.",
            "toc": "Categorías",
            "prompt": "Prompt",
            "contrib": "Contribuir",
            "contrib_body": "Añade una entrada a `prompts.json` con tu imagen de salida y abre un PR. Dos reglas: el prompt tiene que reproducirse y la imagen tiene que ser la salida sin editar.",
            "license": "Licencia",
            "license_body": "Los prompts son MIT. Las imágenes generadas se rigen por los términos del proveedor del modelo; compruébalos antes de un uso comercial.",
        },
        "fr": {
            "gallery_link": "Voir la galerie →",
            "copy_h": "Copier un prompt",
            "all_h": "Ou prenez les 475",
            "toc_entries": "prompts, chacun avec sa graine",
            "tagline": f"{n} prompts {model}, chacun avec l'image qu'il a produite. Un clic pour copier.",
            "toc": "Catégories",
            "prompt": "Prompt",
            "contrib": "Contribuer",
            "contrib_body": "Ajoutez une entrée à `prompts.json` avec votre image de sortie et ouvrez une PR. Deux règles : le prompt doit être reproductible et l'image doit être la sortie non retouchée.",
            "license": "Licence",
            "license_body": "Les prompts sont sous MIT. Les images générées relèvent des conditions du fournisseur du modèle ; vérifiez-les avant tout usage commercial.",
        },
        "de": {
            "gallery_link": "Zur Galerie →",
            "copy_h": "Einen kopieren",
            "all_h": "Oder alle mitnehmen",
            "toc_entries": "Prompts, jeder mit seinem Seed",
            "tagline": f"{n} {model}-Prompts, jeder mit dem Bild, das er erzeugt hat. Klicken und kopieren.",
            "toc": "Kategorien",
            "prompt": "Prompt",
            "contrib": "Mitmachen",
            "contrib_body": "Füge einen Eintrag in `prompts.json` hinzu, leg dein Ausgabebild dazu und öffne einen PR. Zwei Regeln: Der Prompt muss reproduzierbar sein, und das Bild muss die unbearbeitete Ausgabe sein.",
            "license": "Lizenz",
            "license_body": "Die Prompts stehen unter MIT. Für die erzeugten Bilder gelten die Bedingungen des Modellanbieters; prüfe sie vor kommerzieller Nutzung.",
        },
        "pt": {
            "gallery_link": "Ver a galeria →",
            "copy_h": "Copiar um",
            "all_h": "Ou leve os 475",
            "toc_entries": "prompts, cada um com a sua seed",
            "tagline": f"{n} prompts do {model}, cada um com a imagem que gerou. Clique para copiar.",
            "toc": "Categorias",
            "prompt": "Prompt",
            "contrib": "Contribuir",
            "contrib_body": "Adicione uma entrada em `prompts.json` com a sua imagem de saída e abra um PR. Duas regras: o prompt tem de reproduzir e a imagem tem de ser a saída sem edição.",
            "license": "Licença",
            "license_body": "Os prompts são MIT. As imagens geradas seguem os termos do fornecedor do modelo; confirme antes de uso comercial.",
        },
    }[lang]

    L: list[str] = []
    title = data.get("repo", "catalog").split("/")[-1]
    L.append(f"<h1 align=\"center\">{title}</h1>")
    L.append(f"<p align=\"center\">{T['tagline']}</p>\n")

    # A static hero inside the first 1500 chars appeared in 32/32 of the
    # fastest-moving repos measured. A composite that states the three findings
    # beats a thumbnail grid: the grid says "here are images", the composite says
    # "here is what I found". Do not build a GIF, measured lift was zero.
    if (HERE / "hero.webp").exists():
        L.append('<p align="center">')
        # Alt text is regenerated with the hero. It has now been wrong twice: the
        # first version outlived its own claims by three batches, and the second
        # went on describing a success-over-failure grid for weeks after
        # build_hero.py stopped drawing one. Read the image before editing this.
        L.append('  <img src="hero.webp" width="912" '
                 'alt="Twelve Krea 2 Turbo outputs in a four by three grid, under the heading '
                 '475 tested Krea 2 Turbo prompts: a loft under renovation, a desert dune '
                 'ridge at first light, a backlit seed head, an aurora over snow, ice '
                 'diving seen from below, a shelf cloud, a barn owl in flight, a prism '
                 'spectrum on a wall, an icebreaker bow, a quartz point, cut stems in '
                 'water, and moss with sporophytes.">')
        L.append("</p>\n")
    else:
        L.append('<p align="center">')
        for e in kept[:8]:
            L.append(f'  <img src="{e["image"]}" width="180" alt="{e["title"]}">')
        L.append("</p>\n")

    # Badges and a language switcher directly under the title, then a gallery
    # link. Both of the highest-star catalogs in this exact niche do this in the
    # first three lines (nano-banana-pro at 12,956 stars, gpt4o-images at 8,097),
    # and the repo's About website field carries the same URL.
    repo_slug = data.get("repo", "")
    site = f"https://{repo_slug.split('/')[0]}.github.io/{repo_slug.split('/')[-1]}/" if "/" in repo_slug else ""
    L.append('<p align="center">')
    if repo_slug:
        L.append(f'<a href="https://github.com/{repo_slug}/stargazers">'
                 f'<img src="https://img.shields.io/github/stars/{repo_slug}?style=flat&color=1f5d4c" alt="stars"></a>')
    if site:
        L.append(f'<a href="{site}">'
                 '<img src="https://img.shields.io/badge/gallery-browse%20all-1f5d4c" alt="gallery"></a>')
    L.append('<a href="LICENSE"><img src="https://img.shields.io/badge/prompts-MIT-1f5d4c" alt="license"></a>')
    L.append("</p>\n")

    others = [x for x in LANGS if x != lang]
    links = " · ".join(
        f'<a href="README.md">{x.upper()}</a>' if x == "en"
        else f'<a href="README_{x.upper()}.md">{x.upper()}</a>'
        for x in others
    )
    nav = links + (f' · <a href="{site}"><b>{T["gallery_link"]}</b></a>' if site else "")
    if nav:
        L.append(f"<p align=\"center\">{nav}</p>\n")

    # The single highest-scoring Krea 2 post in this subreddit is a wildcards txt
    # at 2,242 points, and a commenter still had to mirror it to pastebin because
    # the original was two clicks away. This repo already had the same artefact,
    # sixty-three files deep in a subfolder. Distance was the whole problem.
    if repo_slug:
        raw = f"https://raw.githubusercontent.com/{repo_slug}/main/wildcards/"
        release_zip = (f"https://github.com/{repo_slug}/releases/latest/download/"
                       "krea2-wildcards.zip")
        alltxt = HERE / "wildcards/all.txt"
        # Two things, ordered by how many people can do them. The old version gave
        # three paths equal weight and spent its longest paragraph on __wildcard__
        # syntax, dynamic prompt nodes and which extension to install. Most people
        # who land here are not on ComfyUI and never will be.
        L.append(h2("copy", T["copy_h"]))
        L.append(f"Open the [gallery]({site}), press **copy** under any picture, paste "
                 "it wherever you generate. Nothing to install, no account, and the "
                 "search box finds the ones you want.\n")
        L.append(f'<a href="{site}"><b>Open the gallery →</b></a>\n')

        L.append(h2("all", T["all_h"]))
        if alltxt.exists():
            L.append(f"**[Download all.txt]({raw}all.txt)** "
                     f"({round(alltxt.stat().st_size / 1024)} KB), one prompt per line. "
                     "Paste any of them into anything.\n")
        L.append(f"**[Download the wildcard zip]({release_zip})** for all category "
                 "files in one archive.\n")
        L.append("On ComfyUI you can wire it up instead: put "
                 "[wildcards/](wildcards/) in `ComfyUI/wildcards/` and write `__all__` "
                 "in a prompt. That needs a dynamic prompts node, which ComfyUI does not "
                 "come with, so install "
                 "[comfyui-dynamicprompts](https://github.com/adieyal/comfyui-dynamicprompts) "
                 "first or the underscores end up in your picture.\n")

    # The catalog used to be printed here in full: 475 entries, 195 KB of README.
    # GitHub lazy-loads a file that size, so every image above a deep anchor
    # resolved late and the anchor landed in the wrong place. The gallery renders
    # the same 475 entries and 65 failures in one page that does not do that, so
    # the index points there and the README keeps one entry to show the shape.
    by_cat: dict[str, int] = {}
    for e in kept:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + 1
    L.append(h2("toc", T["toc"]))
    # Every catalog above 8,000 stars in this niche keeps its prompts inside the
    # repository. Pages is the nicer surface but it is the second one: a visitor
    # who does not click through has to be able to read prompts here.
    gmap = json.loads((HERE / "docs/gallery-map.json").read_text(encoding="utf-8"))
    where = gmap["where"]
    if lang == "en":
        L.append(f"All **{len(kept)}** entries are in the repository at "
                 f"[docs/gallery.md](docs/gallery.md), and on the "
                 f"[web gallery]({site}) if you would rather scroll one page. "
                 f"The category links below go straight to the right section.\n")
    L.append(" · ".join(
        f"[{c}](docs/{where[c]}#{c.lower().replace(' ', '-')}) {n}"
        for c, n in by_cat.items() if c in where) + "\n")

    if lang == "en" and kept:
        sample = next((e for e in kept if e["id"] == "photography-001"), kept[0])
        L.append("### What one entry looks like\n")
        L.append(f'<img src="{sample["image"]}" width="420" alt="{sample["title"]}">\n')
        L.append("```text")
        L.append(sample["prompt"].strip())
        L.append("```")
        if sample.get("params"):
            L.append("")
            L.append(" · ".join(f"`{k}: {v}`" for k, v in sample["params"].items()))
        L.append("")
        # Printing the marked prompt here repeated the whole thing twice on the
        # screen. The useful part was never the repetition, it was which terms
        # were in it, so name those and link what each one does.
        found = sorted(set(m.lower() for m in VOCAB_MD.findall(sample["prompt"])))
        if found:
            L.append("The gallery highlights the words that recur across this catalog and "
                     "travel to other subjects. This one carries "
                     + ", ".join(f"`{m}`" for m in found)
                     + f". [What each of them does → VOCABULARY.md](VOCABULARY.md)\n")
        L.append(f"[**All {len(kept)} in the repo →**](docs/gallery.md)"
                 f" · [**as a web page →**]({site})\n")

    # Everything that used to sit here was evidence: the image-to-image follow-up,
    # the reproduction numbers, 65 failures and a comparison table. All of it is
    # true and none of it is why anyone opened this page. Fifteen of fifteen
    # comparable repos carry no failures section and seven of seven carry no
    # comparison; the failures were also a verbatim duplicate of two other files
    # in this repo. It is moved, not deleted, and linked from one line.
    if True:            # every language gets the way back to the evidence
        nfail = len((data.get("failures") or {}).get("entries", []))
        # One line at the bottom for the reader who wants to check us. This was a
        # 4,064-character findings table under a friendlier heading, and it opened
        # by listing which of my own findings I had withdrawn.
        L.append(f"<sub>What this model does and does not do, the {nfail} generations "
                 "that were cut, how it was run and what the seeds are worth: "
                 "**[FINDINGS.md](FINDINGS.md)** · [REPRODUCING.md](REPRODUCING.md) "
                 "· [VOCABULARY.md](VOCABULARY.md) · [TEMPLATES.md](TEMPLATES.md) "
                 "· [styles/](styles/README.md) · [comparison](docs/comparison.md) "
                 "· [the cut generations](docs/gallery-failures.md)</sub>\n")

    L.append("\n" + h2("contrib", T["contrib"]) + f"\n{T['contrib_body']}\n")
    L.append(h2("license", T["license"]) + f"\n{T['license_body']}\n")
    return "\n".join(L)


def render_findings(data: dict) -> str:
    """FINDINGS.md from the manifest.

    This file used to be maintained by hand next to a prompts.json that holds the
    same findings, and they drifted: the negatives result was measured, written
    into the README table and into scripts/measure_negatives.py, and never reached
    the document the README tells you to read. Generating it removes the gap."""
    f = data["findings"]
    L = ["# What this model actually does", ""]
    if f.get("_intro"):
        L += [counts(data, f["_intro"]), ""]
    L += ["Each finding below is measured against images committed to this repo.", ""]
    tbl = f.get("table")
    if tbl:
        # The summary table used to render only into the README, so moving the
        # section out of the README would have dropped it entirely.
        L += ["| " + " | ".join(tbl["cols"]) + " |",
              "|---" * len(tbl["cols"]) + "|"]
        for r in tbl["rows"]:
            L.append("| " + " | ".join(r) + " |")
        L.append("")
    for item in f["items"]:
        L += [f"### {item['title']}", "", counts(data, item["body"]), ""]
    L += ["## Reproducing any of it", "",
          "See [REPRODUCING.md](REPRODUCING.md) for the exact call, the measured "
          "per-pixel differences, and the reason these seeds do not transfer to a "
          "local graph.", ""]
    return "\n".join(L)


def render_comparison(data: dict) -> str:
    """docs/comparison.md from the manifest.

    This used to be 3,245 characters in the README. Seven of the seven reference
    repositories checked on 2026-08-06 carry no comparison section at all, and a
    table scoring us on the columns we happen to win is an argument with the
    other catalogs rather than an answer to the visitor. It is still true, so it
    is still here, one link away."""
    cmp = data["comparison"]
    L = ["# How this compares", "", cmp["_intro"], "",
         "| | " + " | ".join(cmp["cols"]) + " |",
         "|---" * (len(cmp["cols"]) + 1) + "|"]
    for r in cmp["rows"]:
        L.append("| " + " | ".join(r) + " |")
    L.append("")
    for n in cmp.get("_notes", []):
        L.append(f"- {n}")
    L += ["", "Back to [the catalog](../README.md).", ""]
    return "\n".join(L)


def cmd_build(langs: list[str]) -> int:
    data = load()
    kept = [e for e in data["entries"] if (HERE / e["image"]).exists()]
    missing = len(data["entries"]) - len(kept)

    for lang in langs:
        name = "README.md" if lang == "en" else f"README_{lang.upper()}.md"
        (HERE / name).write_text(render_readme(data, lang), encoding="utf-8")
        print(f"wrote {name}")

    (HERE / "FINDINGS.md").write_text(render_findings(data), encoding="utf-8")
    print("wrote FINDINGS.md")
    (HERE / "docs").mkdir(exist_ok=True)
    (HERE / "docs/comparison.md").write_text(render_comparison(data), encoding="utf-8")
    print("wrote docs/comparison.md")

    ncat = len({e["category"] for e in kept})
    print(f"\n{len(kept)} entries across {ncat} categories"
          + (f" ({missing} entries skipped, no image on disk)" if missing else ""))

    print("\nSet the repo description field to exactly this, and nothing longer:")
    print(f'  "{len(kept)} reproducible {data.get("model","")} prompts across {ncat} categories"')
    print("\nThe description field. Not the README body, is what appears in GitHub search,")
    print("Trending, and every social card. A quantified claim in the first ten words is the")
    print("single highest-leverage asset in this whole play.")

    if any(not (HERE / e["image"]).exists() for e in data["entries"]):
        print("\nNote: entries without an image on disk were omitted rather than rendered broken.")
    print("\nBefore you push: host the images IN THIS REPO or on your own R2/S3.")
    print("External CDN links are the one reliable way this format dies, link rot")
    print("turns a 10k-star catalog into a wall of broken images 18 months later.")

    # The README the build just wrote is the thing that goes public, so it is
    # checked here rather than left to whoever remembers. A guard nobody runs is
    # not a guard: the count contradiction that prompted verify.py sat live for
    # five hours precisely because checking was optional.
    print()
    sys.stdout.flush()  # the child writes straight to the tty; without this its
                        # output lands above ours and reads as a different run
    rc = subprocess.call([sys.executable, str(HERE / "verify.py")])
    if rc:
        print("\nverify.py failed, the README that was just written contradicts the data.",
              file=sys.stderr)
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--generate", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--force", action="store_true", help="regenerate images that already exist")
    ap.add_argument("--lang", action="append", default=[],
                    help="extra language for README (zh, ko). repeatable")
    args = ap.parse_args()

    if args.init:
        return cmd_init()
    if args.generate:
        return cmd_generate(args.force)
    if args.build:
        return cmd_build(["en"] + args.lang)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
