#!/usr/bin/env python3
"""Build the small, experimental Krea 2 reference-shoot pack, without inference.

The graphs are authored here against the pinned ComfyUI-Krea2Edit interfaces.
No model weights, third-party code, uploads or paid APIs are executed. The
hosted Diffusers pilot and these structurally checked ComfyUI graphs are
different runtimes; a matching seed does not promise pixel-identical output.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "workflows/reference-shoot"
REVIEW_CHECKS = ("likeness", "shot", "anatomy", "materials_light")


def load_pack() -> dict:
    return json.loads((PACK / "pack.json").read_text(encoding="utf-8"))


def instruction(pack: dict, shot: dict) -> str:
    return " ".join((shot["direction"], pack["identity"], shot["framing"],
                     pack["finish"][0].lower() + pack["finish"][1:]))


def settings_for(pack: dict, shot: dict) -> dict:
    return pack["settings"] | shot.get("settings", {})


def workflow(pack: dict, shot: dict) -> dict:
    """One shot per graph; every graph reads the same original reference."""
    settings = settings_for(pack, shot)
    nodes, links = [], []

    def add(kind, title, pos, widgets, inputs=(), outputs=(), size=(320, 140)):
        nid = len(nodes) + 1
        node = dict(id=nid, type=kind, title=title, pos=list(pos), size=list(size),
                    flags={}, order=nid - 1, mode=0,
                    inputs=[dict(name=n, type=t, link=None) for n, t in inputs],
                    outputs=[dict(name=t, type=t, links=[]) for t in outputs],
                    properties={"Node name for S&R": kind}, widgets_values=widgets)
        nodes.append(node)
        return node

    def wire(source, target, name, slot=0):
        target_slot = next(i for i, x in enumerate(target["inputs"]) if x["name"] == name)
        output = source["outputs"][slot]
        link_id = len(links) + 1
        links.append([link_id, source["id"], slot, target["id"], target_slot, output["type"]])
        output["links"].append(link_id)
        target["inputs"][target_slot]["link"] = link_id

    model = add("UNETLoader", "1 · Krea 2 Turbo", (40, 40),
                ["krea2_turbo_fp8_scaled.safetensors", "default"], outputs=["MODEL"])
    clip = add("CLIPLoader", "Krea 2 vision text encoder", (40, 230),
               ["qwen3vl_4b_fp8_scaled.safetensors", "krea2", "default"], outputs=["CLIP"])
    vae = add("VAELoader", "Krea 2 VAE", (40, 420),
              ["qwen_image_vae.safetensors"], outputs=["VAE"], size=(320, 90))
    lora = add("LoraLoaderModelOnly", "2 · Community identity-edit v1.2", (40, 560),
               [pack["dependency"]["adapter_filename"], settings["lora_strength"]],
               [("model", "MODEL")], ["MODEL"])
    source = add("LoadImage", "3 · Your original reference (never a previous shot)", (430, 40),
                 [pack["reference"]["filename"], "image"], outputs=["IMAGE", "MASK"], size=(400, 410))
    encoded = add("VAEEncode", "Reference appearance", (430, 510), [],
                  [("pixels", "IMAGE"), ("vae", "VAE")], ["LATENT"])
    target = add("EmptySD3LatentImage", "4 · Output size · batch 1", (430, 730),
                 [settings["width"], settings["height"], 1], outputs=["LATENT"])
    ground_inputs = [("clip", "CLIP"), ("image", "IMAGE"), ("image_b", "IMAGE")]
    positive = add("Krea2EditGroundedEncode", f"5 · {shot['title']}", (920, 40),
                   [instruction(pack, shot), settings["grounding_px"], ""],
                   ground_inputs, ["CONDITIONING"], size=(510, 380))
    negative = add("Krea2EditGroundedEncode", "Empty negative · same reference", (920, 490),
                   ["", settings["grounding_px"], ""], ground_inputs, ["CONDITIONING"])
    patch = add("Krea2EditModelPatch", "6 · Reference conditioning", (1520, 40),
                [settings["ref_boost"], 1.0, "fit"],
                [("model", "MODEL"), ("source_latent", "LATENT"),
                 ("source_latent_b", "LATENT"), ("ref_boost_mask", "MASK"),
                 ("vae", "VAE"), ("source_image", "IMAGE"),
                 ("source_image_b", "IMAGE"), ("target_latent", "LATENT")],
                ["MODEL"], size=(330, 330))
    sampler = add("KSampler", "7 · Run this shot only", (1940, 40),
                  [shot["seed"], "fixed", settings["steps"], settings["cfg"],
                   settings["sampler"], settings["scheduler"], 1.0],
                  [("model", "MODEL"), ("positive", "CONDITIONING"),
                   ("negative", "CONDITIONING"), ("latent_image", "LATENT")],
                  ["LATENT"], size=(320, 330))
    decoded = add("VAEDecode", "Decode", (1940, 470), [],
                  [("samples", "LATENT"), ("vae", "VAE")], ["IMAGE"])
    saved = add("SaveImage", "8 · Review before accepting", (2350, 40),
                [f"krea2-reference-shoot/{shot['id']}"], [("images", "IMAGE")], size=(430, 600))
    add("Note", "Experimental · read README before running", (920, 740),
        ["Needs lbouaraba/comfyui-krea2edit and conradlocke identity-edit v1.2 LoRA. "
         "NOT Krea web Style Transfer. Hosted examples use a different Diffusers runtime; "
         "this ComfyUI graph is structurally tested, not GPU-run here.\n\n"
         "Replace LoadImage and edit the appearance sentence for your own consenting adult "
         "or synthetic character. Keep the ORIGINAL reference in every shot. "
         "Retry only the unsatisfactory shot.\n\nReview: " + shot["acceptance"]], size=(510, 260))

    for src, dst, name in ((model, lora, "model"), (lora, patch, "model"),
                           (source, encoded, "pixels"), (vae, encoded, "vae"),
                           (encoded, patch, "source_latent"), (vae, patch, "vae"),
                           (source, patch, "source_image"), (target, patch, "target_latent"),
                           (patch, sampler, "model"), (positive, sampler, "positive"),
                           (negative, sampler, "negative"), (target, sampler, "latent_image"),
                           (sampler, decoded, "samples"), (vae, decoded, "vae"),
                           (decoded, saved, "images")):
        wire(src, dst, name)
    for grounded in (positive, negative):
        wire(clip, grounded, "clip")
        wire(source, grounded, "image")
        grounded["inputs"][1]["shape"] = 7
        grounded["inputs"][2]["shape"] = 7
    for optional in patch["inputs"][2:]:
        optional["shape"] = 7
    return dict(id=f"{pack['id']}-{shot['id']}", revision=1, last_node_id=len(nodes),
                last_link_id=len(links), nodes=nodes, links=links, groups=[], config={},
                extra={"krea2_reference_shoot": {
                    "pack": pack["id"], "shot": shot["id"],
                    "reference": pack["reference"]["catalog_id"],
                    "nodes_revision": pack["dependency"]["nodes_revision"],
                    "runtime_validation": "structural-only"}}, version=0.4)


def accepted_runs(pack: dict, runs: list[dict]) -> dict:
    """Do not promote a generated file or a pending/partial review as a success."""
    selected = {}
    shots = {s["id"]: s for s in pack["shots"]}
    source_hash = hashlib.sha256((ROOT / pack["reference"]["image"]).read_bytes()).hexdigest()
    for run in runs:
        if run["review"]["status"] != "accepted":
            continue
        if run.get("status") != "completed" or run.get("randomize_seed") is not False:
            raise ValueError(f"Accepted run must be completed with its recorded seed: {run['id']}")
        shot = shots[run["shot"]]
        if shot["id"] in selected:
            raise ValueError(f"More than one accepted run for {shot['id']}")
        if any(run["review"].get(key) != "pass" for key in REVIEW_CHECKS):
            raise ValueError(f"Incomplete visual review: {run['id']}")
        if not run["review"].get("notes"):
            raise ValueError("Review notes are required")
        if run["instruction"] != instruction(pack, shot) or run["seed"] != shot["seed"]:
            raise ValueError(f"Recipe/receipt mismatch: {run['id']}")
        settings = settings_for(pack, shot)
        for key in ("ref_boost", "grounding_px", "steps", "space_guidance_scale", "lora_strength"):
            if run["settings"][key] != settings[key]:
                raise ValueError(f"Setting mismatch: {run['id']} / {key}")
        if run["reference_sha256"] != source_hash:
            raise ValueError(f"Missing/mismatched provenance: {run['id']}")
        asset_id = run.get("provider_asset_id")
        event_id = run.get("event_id")
        if asset_id is not None:
            expected_url = ("https://conradlocke-krea2-identity-edit.hf.space/"
                            f"gradio_api/file=/tmp/gradio/{asset_id}/image.webp")
            if not re.fullmatch(r"[0-9a-f]{64}", asset_id) or run.get("output_url") != expected_url:
                raise ValueError(f"Mismatched provider asset: {run['id']}")
            if not run.get("reference_input"):
                raise ValueError(f"Missing actual browser input: {run['id']}")
        if not asset_id and not re.fullmatch(r"[0-9a-f]{32}", event_id or ""):
            raise ValueError(f"Missing provider provenance: {run['id']}")
        from PIL import Image
        if actual_input := run.get("reference_input"):
            input_path = (PACK / actual_input["path"]).resolve()
            if not input_path.is_relative_to((PACK / "reference").resolve()):
                raise ValueError("Preserved browser inputs must be inside reference/")
            if hashlib.sha256(input_path.read_bytes()).hexdigest() != actual_input["sha256"]:
                raise ValueError(f"Input bytes changed: {run['id']}")
            if not actual_input.get("transport"):
                raise ValueError(f"Input transport note required: {run['id']}")
            with Image.open(input_path) as input_image, Image.open(ROOT / pack["reference"]["image"]) as source:
                if input_image.size != source.size:
                    raise ValueError(f"Input dimensions differ: {run['id']}")
        path = (PACK / run["output"]).resolve()
        if not path.is_relative_to((PACK / "examples").resolve()):
            raise ValueError("Accepted outputs must be inside examples/")
        if hashlib.sha256(path.read_bytes()).hexdigest() != run["sha256"]:
            raise ValueError(f"Output bytes changed: {run['id']}")
        with Image.open(path) as output:
            if list(output.size) != [settings["width"], settings["height"]]:
                raise ValueError(f"Output dimensions differ: {run['id']}")
        selected[shot["id"]] = run
    return selected


def render_page(pack: dict, runs: list[dict]) -> str:
    from build_site import CSS
    escape = lambda value: html.escape(str(value), quote=True)
    accepted = accepted_runs(pack, runs)
    first_sample = next(iter(accepted.values()), None)
    result_figure = (f'<figure><img class="reference" src="{escape(first_sample["output"])}" '
                     f'alt="Reviewed reference-edit result"><figcaption>Reviewed result · '
                     f'<a href="{escape(first_sample["output"])}" download>Original file</a>'
                     '</figcaption></figure>' if first_sample else '')
    cards = []
    for shot in sorted(pack["shots"], key=lambda item: item["id"] not in accepted):
        run = accepted.get(shot["id"])
        settings = settings_for(pack, shot)
        preview = (f'<img src="{escape(run["output"])}" alt="{escape(shot["title"])}" loading="lazy">'
                   if run else '<p class="pending">Not visually accepted yet. No sample claimed.</p>')
        original_link = (f' · <a href="{escape(run["output"])}" download>Original image</a>'
                         if run else '')
        cards.append(f'<article class="card">{preview}<div class="cardbody">'
                     f'<h3>{escape(shot["title"])}</h3><p>{escape(run["review"]["notes"] if run else shot["acceptance"])}</p>'
                     f'<details><summary>Exact instruction · seed {shot["seed"]} · likeness {settings["ref_boost"]}</summary>'
                     f'<pre>{escape(instruction(pack, shot))}</pre></details>'
                     f'<button class="copy" data-prompt="{escape(instruction(pack, shot))}">Copy instruction</button> '
                     f'<a href="{shot["id"]}.json" download>Download workflow</a>{original_link}</div></article>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(pack['title'])} · Krea 2 reference shoot</title>
<meta name="description" content="An experimental Krea 2 identity-edit shooting pack with original reference, exact instructions, reviewed output and individual ComfyUI graphs.">
<style>{CSS}
.gallery{{grid-template-columns:repeat(2,minmax(0,1fr))}}.card img{{object-fit:contain}}.cardbody p{{font-size:.9rem;color:var(--mut)}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 ui-monospace,monospace}}.pending{{padding:32px}}.reference-pair{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.reference-pair figure{{margin:0}}.reference-pair figcaption{{font-size:.8rem}}.reference{{width:100%;height:auto}}details{{margin:18px 0}}summary{{cursor:pointer}}@media(max-width:600px){{.gallery{{grid-template-columns:1fr}}}}</style></head>
<body><div class="wrap"><header class="topbar"><a class="brand" href="../../">Krea 2 Wildcards</a><nav><a href="README.md">Setup & limitations</a><a href="runs.json">Run receipts</a></nav></header>
<main><section class="hero"><div><p class="eyebrow">Experimental · community identity-edit v1.2</p>
<h1>One reference.<br>A new angle.</h1>
<p class="lead">Keep a character recognizable while changing the camera. Start every shot from the same original; rerun only the shot you need.</p>
<p><strong>{len(accepted)} of {len(pack['shots'])} shots visually accepted</strong> in a one-character hosted pilot. This is not a multi-person consistency benchmark.</p>
<p>Samples: Krea 2 Turbo + community identity-edit LoRA, hosted Diffusers. Downloadable ComfyUI graphs: structural checks only; local GPU execution is not yet verified.</p>
<a class="button" href="README.md">Use your own reference →</a></div>
<div class="reference-pair"><figure><img class="reference" src="../../{escape(pack['reference']['image'])}" alt="Original synthetic reference: adult woman in charcoal sweater"><figcaption>Synthetic reference · <a href="../../{escape(pack['reference']['image'])}" download>Download</a></figcaption></figure>{result_figure}</div></section>
<section><h2>The shooting set</h2><p class="sectionintro">Original provider-returned files. No post-generation retouching, crop or upscale. Visual review is qualitative, not a biometric identity score.</p><div class="gallery">{''.join(cards)}</div></section>
<section><h2>Make it yours</h2><ol><li>Install the model and node dependencies in the setup guide, or use the linked community demo.</li><li>Replace the reference and appearance sentence. Use your own consenting adult subject or a synthetic character.</li><li>Run one shot, check face, pose, hands, clothing and light, then keep or rerun it. Never feed a generated shot into the next one.</li></ol>
<p>One person, one wardrobe, still images only. The full-body shot invents trousers, shoes and body details absent from the head-and-shoulders reference. No identity guarantee, automatic face matching or video consistency claim.</p></section></main>
<footer>Unofficial Krea 2 community workflow. <a href="{escape(pack['dependency']['nodes'])}">Nodes by lbouaraba</a> · <a href="https://huggingface.co/{escape(pack['dependency']['adapter'])}">LoRA by conradlocke</a>. Model terms are separate from this repository's MIT scripts and prompts.</footer></div>
<script>document.querySelectorAll('[data-prompt]').forEach(button=>button.addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(button.dataset.prompt);button.textContent='Copied';}}catch{{button.closest('article').querySelector('details').open=true;button.textContent='Select the instruction above';}}}}));</script></body></html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated files without writing")
    args = parser.parse_args()
    pack = load_pack()
    runs = json.loads((PACK / "runs.json").read_text(encoding="utf-8"))["runs"]
    outputs = {f"{shot['id']}.json": json.dumps(workflow(pack, shot), indent=2) + "\n"
               for shot in pack["shots"]}
    outputs["index.html"] = render_page(pack, runs)
    for name, contents in outputs.items():
        path = PACK / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != contents:
                raise ValueError(f"Out of date: {path.relative_to(ROOT)}")
        else:
            path.write_text(contents, encoding="utf-8")
    print(f"{'Checked' if args.check else 'Built'} {len(outputs)} reference-shoot files; "
          f"visually accepted samples: {len(accepted_runs(pack, runs))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
