#!/usr/bin/env python3
"""Build the two supported ComfyUI Krea 2 starter workflows.

The base graph is pinned to Comfy-Org's official workflow template. One output
uses only the official graph; the other adds the Dynamic Prompts random
generator and wires this repository's ``__product__`` wildcard into it.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workflows"
OFFICIAL_COMMIT = "e95e3b20567bea8df16510c8390b7f897b7e6d4b"
OFFICIAL_URL = (
    "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/"
    f"{OFFICIAL_COMMIT}/templates/image_krea2_turbo_t2i.json"
)
EXAMPLE_ID = "product-019"

MODELS_NOTE = """## Required Krea 2 model files

Update ComfyUI first. Download the following files from
[Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2):

- `krea2_turbo_fp8_scaled.safetensors` to `ComfyUI/models/diffusion_models/`
- `qwen3vl_4b_fp8_scaled.safetensors` to `ComfyUI/models/text_encoders/`
- `qwen_image_vae.safetensors` to `ComfyUI/models/vae/`

The graph uses Krea 2 Turbo's official eight-step subgraph. No LoRA is enabled.
"""


def load_official() -> dict:
    with urlopen(OFFICIAL_URL) as response:
        return json.load(response)


def catalog_entry(entry_id: str) -> dict:
    data = json.loads((ROOT / "prompts.json").read_text(encoding="utf-8"))
    return next(entry for entry in data["entries"] if entry["id"] == entry_id)


def node(graph: dict, node_id: int) -> dict:
    return next(item for item in graph["nodes"] if item["id"] == node_id)


def prepare_base(graph: dict, prompt: str) -> dict:
    graph["id"] = "d66a15f5-c948-41ab-b9d5-c65419f78f8f"
    graph["revision"] = 1
    graph["extra"]["krea2_wildcards"] = {
        "source_template": OFFICIAL_URL,
        "source_commit": OFFICIAL_COMMIT,
        "catalog_entry": EXAMPLE_ID,
    }

    pipeline = node(graph, 30)
    pipeline["widgets_values"][0] = prompt
    pipeline["widgets_values"][1] = False  # catalog prompts are already complete
    pipeline["widgets_values"][7] = False  # no optional LoRA for a starter graph
    pipeline["widgets_values"][8] = "None"
    pipeline["widgets_values"][9] = 0.0
    pipeline["widgets_values"][10] = ""

    node(graph, 29)["widgets_values"] = ["krea2_wildcards"]
    node(graph, 47)["widgets_values"] = [
        "## About this starter\n\n"
        "This graph starts with a tested prompt from "
        "[sjh9714/krea2-wildcards](https://github.com/sjh9714/krea2-wildcards). "
        "Prompt enhancement is off so the text is sent unchanged. Change the prompt, "
        "resolution, or seed, then queue the graph."
    ]
    node(graph, 48)["widgets_values"] = [MODELS_NOTE]
    node(graph, 50)["widgets_values"] = [
        "## Prompt choice\n\n"
        "The included prompt is `product-019`, selected because its single subject, "
        "camera angle, light direction, surface, and text constraint are explicit. "
        "Browse and copy more tested prompts at "
        "[the visual catalog](https://sjh9714.github.io/krea2-wildcards/)."
    ]
    return graph


def add_dynamic_prompts(graph: dict) -> dict:
    graph["id"] = "c48af98a-1bd6-4e79-ae41-7603c22bd2cb"
    graph["revision"] = 1
    graph["last_node_id"] = 51
    graph["last_link_id"] = 87

    pipeline = node(graph, 30)
    pipeline["pos"] = [30, -110]
    pipeline["order"] = 5
    node(graph, 29)["order"] = 6
    node(graph, 49)["order"] = 4
    prompt_input = {
        "label": "prompt",
        "name": "value",
        "type": "STRING",
        "widget": {"name": "value", "config": ["STRING", {"multiline": True}]},
        "link": 87,
    }
    pipeline["inputs"].insert(0, prompt_input)

    # Inserting the prompt at input slot zero moves the existing linked width
    # and height inputs one slot to the right.
    for link in graph["links"]:
        if link[3] == 30:
            link[4] += 1

    random_node = {
        "id": 51,
        "type": "DPRandomGenerator",
        "pos": [-520, -110],
        "size": {"0": 400, "1": 200},
        "flags": {},
        "order": 3,
        "mode": 0,
        "outputs": [
            {
                "name": "STRING",
                "type": "STRING",
                "links": [87],
                "shape": 3,
                "slot_index": 0,
            }
        ],
        "properties": {"Node name for S&R": "DPRandomGenerator"},
        "widgets_values": ["__product__"],
        "color": "#2a363b",
        "bgcolor": "#3f5159",
        "shape": 4,
    }
    graph["nodes"].append(random_node)
    graph["links"].append([87, 51, 0, 30, 0, "STRING"])
    graph["extra"]["krea2_wildcards"]["custom_node"] = (
        "https://github.com/adieyal/comfyui-dynamicprompts"
    )
    node(graph, 29)["widgets_values"] = ["krea2_wildcards_random"]
    node(graph, 47)["widgets_values"] = [
        "## Wildcard starter\n\n"
        "This version adds the `DPRandomGenerator` custom node. Install "
        "[ComfyUI-DynamicPrompts](https://github.com/adieyal/comfyui-dynamicprompts), "
        "copy this repository's `wildcards/product.txt` into its `wildcards` folder, "
        "then queue the graph. The random node expands one tested product prompt per run."
    ]
    node(graph, 50)["widgets_values"] = [
        "## Change the prompt pool\n\n"
        "Replace `__product__` with any filename from this repository, such as "
        "`__fashion__`, `__interior__`, or `__all__`. Keep prompt enhancement off "
        "when you want the selected wildcard text to reach Krea 2 unchanged."
    ]
    return graph


def write(graph: dict, name: str) -> Path:
    path = OUT / name
    path.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="rebuild portable JSON only; useful in cross-platform CI",
    )
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    entry = catalog_entry(EXAMPLE_ID)
    native = prepare_base(load_official(), entry["prompt"])
    native_path = write(native, "krea2-native-starter.json")
    if not args.json_only:
        from embed_workflow_png import embed
        embed(native_path, ROOT / entry["image"], OUT / "krea2-native-starter.png", announce=False)
        print("workflows/krea2-native-starter.png")

    wildcard = add_dynamic_prompts(prepare_base(load_official(), entry["prompt"]))
    wildcard_path = write(wildcard, "krea2-wildcards-starter.json")
    if not args.json_only:
        from embed_workflow_png import embed
        embed(wildcard_path, ROOT / entry["image"], OUT / "krea2-wildcards-starter.png", announce=False)
        print("workflows/krea2-wildcards-starter.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
