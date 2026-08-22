# Krea 2 workflows for ComfyUI

These are loadable ComfyUI workflow files built from Comfy-Org's official Krea
2 Turbo template. Download a JSON file and drag it onto the ComfyUI canvas, or
drag in the matching PNG example; the complete workflow is embedded in the PNG.

## Choose the right workflow

| Workflow | Extra node | Best for |
|---|---|---|
| [`krea2-native-starter.json`](krea2-native-starter.json) | None | Paste one prompt and render it unchanged |
| [`krea2-wildcards-starter.json`](krea2-wildcards-starter.json) | [`ComfyUI-DynamicPrompts`](https://github.com/adieyal/comfyui-dynamicprompts) | Sample a different prompt from a wildcard file on every run |

The same graphs are embedded in
[`krea2-native-starter.png`](krea2-native-starter.png) and
[`krea2-wildcards-starter.png`](krea2-wildcards-starter.png).

## Open in Comfy Cloud

[Open the native six-node starter in Comfy Cloud](https://cloud.comfy.org/?share=78d328f1548e)
to copy it into your workspace without downloading a file. The wildcard graph
is intended for local ComfyUI with `ComfyUI-DynamicPrompts` installed.

## Model files

Update ComfyUI, then download the official files from
[`Comfy-Org/Krea-2`](https://huggingface.co/Comfy-Org/Krea-2):

| File | Put it in |
|---|---|
| `krea2_turbo_fp8_scaled.safetensors` | `ComfyUI/models/diffusion_models/` |
| `qwen3vl_4b_fp8_scaled.safetensors` | `ComfyUI/models/text_encoders/` |
| `qwen_image_vae.safetensors` | `ComfyUI/models/vae/` |

The starter uses the official eight-step Turbo subgraph, a 1024 by 1024
resolution, and no optional LoRA. Prompt enhancement is disabled because the
catalog prompts already specify the subject, composition, light, surface, and
constraints.

## Wildcard setup

Install `ComfyUI-DynamicPrompts` with ComfyUI Manager or follow its
[manual installation instructions](https://github.com/adieyal/comfyui-dynamicprompts#installation).
Copy the wildcard files you want into:

```text
ComfyUI/custom_nodes/comfyui-dynamicprompts/wildcards/
```

The included graph starts with `__product__`. Replace it with `__fashion__`,
`__interior__`, `__all__`, or any other filename in this repository's
[`wildcards/`](../wildcards/) folder.

## Provenance

The graph source is Comfy-Org's official `image_krea2_turbo_t2i` template,
pinned to commit
[`e95e3b2`](https://github.com/Comfy-Org/workflow_templates/commit/e95e3b20567bea8df16510c8390b7f897b7e6d4b).
The preview image is the catalog's `product-019` Krea web generation. Rebuild
the JSON files with `python3 scripts/build_workflows.py`.
