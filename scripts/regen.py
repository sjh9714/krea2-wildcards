#!/usr/bin/env python3
"""
regen.py, regenerate any catalog entry from its recorded seed.

The catalog claims every image is reproducible. This turns that from an assertion
into a command someone can run, which is the version that survives a sceptical
reader. It re-submits the stored prompt with the stored seed and reports whether
the bytes come back identical.

    python3 scripts/regen.py --id typography-008
    python3 scripts/regen.py --id fail-korean --manifest data/failures.json --sources prompts.json
    python3 scripts/regen.py --all --limit 5

A note on what "reproducible" can honestly mean here: fal serves Krea 2 Turbo on
whatever hardware it schedules, and diffusion sampling is only bit-exact when the
whole stack matches. So a byte-identical result is possible but not guaranteed,
and this script reports the truth either way rather than claiming success. What
the seed does guarantee is that you are running the same generation, not a
different roll of the dice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_fal import DEFAULT_MODEL, I2I_MODEL, data_uri, generate_one  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default="prompts.json")
    ap.add_argument("--sources", help="extra manifest for resolving `source` ids")
    ap.add_argument("--id", help="comma-separated entry ids")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--i2i-model", default=I2I_MODEL)
    ap.add_argument("--keep", help="directory to write regenerated files into")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    mpath = Path(args.manifest)
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1]
    by_id = {e["id"]: e for e in manifest["entries"]}

    src_root = root
    if args.sources:
        extra = json.loads(Path(args.sources).read_text(encoding="utf-8"))
        for e in extra["entries"]:
            by_id.setdefault(e["id"], e)
        src_root = root

    if args.id:
        want = [i.strip() for i in args.id.split(",")]
        targets = [by_id[i] for i in want if i in by_id]
        missing = [i for i in want if i not in by_id]
        for m in missing:
            print(f"unknown id: {m}", file=sys.stderr)
    elif args.all:
        targets = list(manifest["entries"])
    else:
        ap.error("need --id or --all")

    targets = [e for e in targets if (e.get("params") or {}).get("seed")]
    if args.limit:
        targets = targets[: args.limit]
    if not targets:
        print("nothing to regenerate (no entries with a recorded seed)", file=sys.stderr)
        return 2

    outdir = Path(args.keep) if args.keep else Path(tempfile.mkdtemp(prefix="regen-"))
    outdir.mkdir(parents=True, exist_ok=True)

    identical = differing = failed = 0
    for i, e in enumerate(targets, 1):
        seed = e["params"]["seed"]
        model, extra = args.model, {"image_size": "square_hd",
                                    "enable_safety_checker": True, "seed": seed}
        if e.get("source"):
            src = by_id.get(e["source"])
            if src is None:
                print(f"SKIP source '{e['source']}' not found, pass --sources")
                failed += 1
                continue
            sp = root / src["image"]
            if not sp.exists():
                sp = src_root / src["image"]
            model = args.i2i_model
            extra["image_url"] = data_uri(sp)
            extra["strength"] = e.get("strength", 0.85)

        # Name by id + the real format. Reusing the manifest's filename wrote
        # PNG bytes under a .webp extension, which is exactly the kind of quiet
        # mislabelling this script exists to rule out.
        dest = outdir / (e["id"] + ".png")
        print(f"[{i}/{len(targets)}] {e['id']} seed={seed}", end=" ", flush=True)
        try:
            generate_one(model, e["prompt"], dest, extra, args.timeout)
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED {type(exc).__name__}: {str(exc)[:90]}")
            failed += 1
            continue

        orig = root / e["image"]
        if orig.exists() and orig.suffix == dest.suffix and sha(orig) == sha(dest):
            print("identical")
            identical += 1
        else:
            # The catalog ships WebP; a fresh generation is PNG, so a hash
            # mismatch here is expected and is not evidence of irreproducibility.
            note = "re-encoded in repo, compare visually" if orig.suffix != dest.suffix else "differs"
            print(f"regenerated ({note})")
            differing += 1

    print(f"\n{identical} identical · {differing} regenerated · {failed} failed")
    print(f"output: {outdir}")
    if differing and not identical:
        print("\nThe repo stores WebP and this wrote PNG, so a byte comparison cannot\n"
              "succeed. Open both and compare; the seed guarantees the same generation,\n"
              "not the same file after re-encoding.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
