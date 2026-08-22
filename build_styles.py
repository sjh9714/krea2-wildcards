#!/usr/bin/env python3
"""
build_styles.py, generate styles/README.md and the wildcards files from data.

The public page is a compact recipe book: the whole-scene phrasing rule, eight
copyable clauses with their images, a style-friendly subject structure, and the
larger wildcard set. Raw experiment records remain in the JSON files.

Generated, not hand-written: a page that prints prompt text has to print the
text that was actually sent. These clauses lived only in shell history once and
had to be recovered from a session transcript.

    python3 build_styles.py
"""

from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "styles/data.json"
SWEEP = HERE / "styles/sweep.json"

GOODS_ORDER = ["manga", "storybook", "comicink", "chibi",
               "poster", "retroanime", "popart", "sixties"]


def main() -> int:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))

    missing = [k for k in GOODS_ORDER if k not in d["goods"]] + \
              [k for k in d["goods"] if k not in GOODS_ORDER]
    if missing:
        print(f"GOODS_ORDER and data.json disagree: {missing}")
        return 1

    L = [
        "# Krea 2 whole-scene style recipes",
        "",
        "[← back to the catalog](../README.md)",
        "",
        f"Eight tested style clauses from [the original Reddit thread]({d['post']}), "
        "each shown with the image it generated and ready to copy into a prompt "
        "or wildcard file.",
        "",
        "## The rule",
        "",
        "**Put the medium first and make it describe the whole scene. Then add "
        "the subject, composition, and details that belong to that medium.**",
        "",
        "Same subject and seed, two ways to phrase the style. The first names a "
        "picture-book style; the second tells the model how the whole scene is drawn:",
        "",
        f'<img src="{d["hook"]["named_image"]}" width="330" alt="named: a picture book appears on the table">',
        f'<img src="{d["hook"]["rephrased_image"]}" width="330" alt="rephrased: the whole frame converts">',
        "",
        f"- named, `{d['hook']['named_clause']}`",
        f"- rephrased, `{d['hook']['rephrased_clause']}`",
        "",
        "## Eight whole-scene clauses",
        "",
        f"One subject, seed `{d['seed']}`, the clause is the only variable. "
        "Each is about 100 characters; they are plain English and carry nothing "
        "model-specific.",
        "",
    ]
    for k in GOODS_ORDER:
        g = d["goods"][k]
        L += [f'<img src="{g["image"]}" width="330" alt="{g["label"]}">', "",
              f"**{g['label']}**, `{g['clause']}`", ""]
    L += [
        "All eight, one per line, for a ComfyUI wildcard or dynamic-prompt node: "
        "[`wildcards/styles.txt`](../wildcards/styles.txt)",
        "",
        "## A subject prompt that leaves room for style",
        "",
        "Use this order:",
        "",
        "`[whole-scene medium] + [subject and setting] + [composition] + "
        "[medium-specific detail]`",
        "",
        "A clean base subject:",
        "",
        "```",
        "A young woman sitting at an outdoor cafe table, holding an iced drink "
        "near her face. She has long dark hair, a thin white summer top, and "
        "small hoop earrings. Composed as a waist-up view, directly facing the "
        "viewer, with the street behind her.",
        "```",
        "",
        "Three useful substitutions when moving from photography to illustration:",
        "",
        "- `facing the camera` becomes `facing the viewer`",
        "- `shallow depth of field` becomes `simplified background detail`",
        "- lens and studio-light terms become mark-making, palette, paper, ink, "
        "paint, or print terms from the target medium",
        "",
        "## More style recipes",
        "",
        f"The earlier sweep contributes {len(sweep['kept'])} more reusable clauses in "
        "[`wildcards/styles-extra.txt`](../wildcards/styles-extra.txt). Its raw "
        "generation record remains in [`sweep.json`](sweep.json).",
        "",
        f"For a larger community style list, see [the wildcards thread]({d['their_thread']}).",
        "",
        "The prompt text and source records used to build this page are kept in "
        "[`data.json`](data.json) and [`sweep.json`](sweep.json).",
        "",
    ]
    (HERE / "styles/README.md").write_text("\n".join(L), encoding="utf-8")

    wc = HERE / "wildcards"
    wc.mkdir(exist_ok=True)
    (wc / "styles.txt").write_text(
        "\n".join(d["goods"][k]["clause"] for k in GOODS_ORDER) + "\n",
        encoding="utf-8")
    (wc / "styles-extra.txt").write_text(
        "\n".join(v["clause"] for v in sweep["kept"].values()) + "\n",
        encoding="utf-8")

    print(f"styles/README.md      {len(chr(10).join(L)):,} chars")
    print(f"wildcards/styles.txt  {len(GOODS_ORDER)} whole-scene clauses")
    print(f"wildcards/styles-extra.txt  {len(sweep['kept'])} clauses (earlier sweep)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
