#!/usr/bin/env python3
"""
build_wildcards.py, emit the catalog as ComfyUI-consumable wildcard files.

Why this exists: measured, not assumed. Pulling 6,670 r/StableDiffusion posts
from 2026-05-01 onward, the single highest-scoring post in the subreddit over
that window is "Krea 2 : styles (wildcards txt)" at 1,717 points, with its
update at 979. A resource that drops straight into a workflow outscores a
resource you have to browse, in a subreddit that is 13% Krea 2 posts right now.

This catalog already holds the prompts. What it did not have was the one-line
form a wildcard node can read. That is a formatting gap, not a content gap, so
it costs nothing to close.

    python3 build_wildcards.py          # writes wildcards/

Emits one file per category plus all.txt, every line a complete prompt with
newlines collapsed. Failures are excluded, a wildcard file that randomly
serves you a known-broken prompt is worse than no wildcard file.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZIP_NAME = "krea2-wildcards.zip"


def one_line(s: str) -> str:
    """Wildcard nodes read line by line, so a prompt containing a newline
    becomes two broken prompts. Collapse whitespace and strip separators that
    would split a line further."""
    return re.sub(r"\s+", " ", s).replace("\n", " ").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default="prompts.json")
    ap.add_argument("--out", default="wildcards")
    args = ap.parse_args()

    d = json.loads((HERE / args.manifest).read_text(encoding="utf-8"))
    out = HERE / args.out
    out.mkdir(parents=True, exist_ok=True)
    by: OrderedDict[str, list[str]] = OrderedDict()
    for e in d["entries"]:
        by.setdefault(e["category"], []).append(one_line(e["prompt"]))

    # Delete only what this script owns. `styles.txt` and `styles-extra.txt` are
    # written by build_styles.py and live in the same folder; a blanket
    # `glob("*.txt")` unlink silently destroyed them, and the repo only stayed
    # correct as long as the two builds ran in the right order.
    owned = {f"{c}.txt" for c in by} | {"all.txt"}
    for f in out.glob("*.txt"):
        if f.name in owned:
            f.unlink()
    (out / ZIP_NAME).unlink(missing_ok=True)

    total = 0
    for cat, prompts in by.items():
        (out / f"{cat}.txt").write_text("\n".join(prompts) + "\n", encoding="utf-8")
        total += len(prompts)

    everything = [p for ps in by.values() for p in ps]
    (out / "all.txt").write_text("\n".join(everything) + "\n", encoding="utf-8")
    repo_url = d.get("repo") and "https://github.com/" + d["repo"] or ".."
    release_zip = f"{repo_url}/releases/latest/download/{ZIP_NAME}"

    # The seeds live in prompts.json, and a wildcard file cannot carry them.
    # Say so here rather than letting someone think a re-roll should match.
    (out / "README.md").write_text(f"""# Wildcards

{total} prompts from [this catalog]({repo_url}),
one per line, ready for a wildcard or dynamic-prompt node.

- `all.txt`. Every prompt, {len(everything)} lines
- one file per category ({len(by)} of them), if you want to sample within a style

[Download every category as one zip]({release_zip}).

## ComfyUI

This repository provides prompt files, not a custom node. No custom node from
this repository is required.

Drop this folder into `ComfyUI/wildcards/`, then reference it from a dynamic
prompt node:

```
__all__
__photography__
__typography__
```

## Format notes

**The seeds, and you probably do not want them anyway.** A wildcard file is one
prompt per line and has nowhere to put a seed. More to the point, the seeds in
this catalog were recorded against fal's hosted `krea-2/turbo`, which publishes
no step count, CFG, sampler or scheduler. In your own graph the same seed gives
a different image. Take the prompts, pick your own seed, and read
[REPRODUCING.md](../REPRODUCING.md) before you try to match a specific frame.

The wildcard files contain the published prompt collection only. The repository's
research records stay separate so every random line is ready to use.

Regenerate with `python3 build_wildcards.py`.
""", encoding="utf-8")

    # One click, not sixty-three. The highest-scoring post this format has ever
    # had was a plain text file, and a commenter still had to mirror it to
    # pastebin because the original was two clicks away. A repository folder is
    # further away than that, so ship the folder as one file as well.
    # Fixed timestamps, or the archive has different bytes on every build and the
    # CI check that generated files already match the manifest can never pass.
    # 1980-01-01 is the earliest a zip entry can carry.
    zpath = out / ZIP_NAME
    stamp = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.glob("*.txt")) + [out / "README.md"]:
            info = zipfile.ZipInfo(f.name, date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, f.read_bytes())

    print(f"wrote {out}/ - {len(by)} category files + all.txt ({total} prompts)")
    print(f"wrote {zpath.relative_to(HERE)}  {zpath.stat().st_size // 1024} KB")
    longest = max(everything, key=len)
    print(f"longest line: {len(longest)} chars")
    assert not any("\n" in p for p in everything), "a prompt still contains a newline"
    print("no embedded newlines: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
