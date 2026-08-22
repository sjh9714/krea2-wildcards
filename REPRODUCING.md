# Reproducing these images

This catalog records two generation routes. The original fal batch carries seeds
for deterministic hosted re-runs. The newer Krea web batch carries the exact
Krea generation asset ID and aspect ratio because the web app does not expose a
seed. In both routes, the prompt text is the portable part for local workflows.

That is a limitation of how this catalog was built. It is written down here
rather than left for you to discover.

## fal route: exact call

The original 475 published images were produced by this call:

```
POST  https://queue.fal.run/fal-ai/krea-2/turbo

{
  "prompt": "<the prompt from prompts.json>",
  "seed": <the seed from prompts.json>,
  "image_size": "square_hd",
  "enable_safety_checker": true
}
```

Everything not listed was left at the endpoint default:

| field | value used | source |
|---|---|---|
| `image_size` | `square_hd` | set by us. Verified 1024x1024 on all 475 committed images |
| `enable_safety_checker` | `true` | set by us |
| `enable_prompt_expansion` | `false` | endpoint default. **No LLM rewrote these prompts** |
| `acceleration` | `none` | endpoint default |
| `output_format` | `png` | endpoint default. Committed here as WebP |
| `num_images` | `1` | endpoint default |

The five `editing-*` entries go to `fal-ai/krea-2/turbo/image-to-image` instead
and additionally pass a source image and a strength. Both are recorded on the
entry: `source` names the catalog entry the image came from, and `strength` is
0.50 to 0.60 across the five.

## Krea web route: asset provenance

The 24 entries in batch 9 were generated in the signed-in Krea web app with
Krea 2 Turbo. Each prompt returned four candidates. One candidate was selected
after visual review and the other three remain counted in the generation total.

These entries record:

- `params.provider: krea-web`
- the selected image's `params.generation_id`
- the requested `params.aspect_ratio`
- `creation_tool: Krea web app, Krea 2 Turbo`

The generation ID is the UUID in Krea's original asset URL. It identifies the
exact selected output without inventing a seed the interface never supplied.

## What the endpoint does not accept

Read from the published OpenAPI schema on 2026-08-06:

```
https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/krea-2/turbo
```

`Krea2TurboInput` accepts exactly nine fields: `prompt`, `seed`, `image_size`,
`num_images`, `output_format`, `acceleration`, `enable_prompt_expansion`,
`enable_safety_checker`, `sync_mode`.

There is **no** step count, **no** CFG or guidance scale, **no** sampler, **no**
scheduler and **no** negative prompt field. Those choices are made inside the
hosted endpoint and are not disclosed. We did not omit them from this catalog;
we never had them.

## What this means if you run it locally

The weights are open, so most people reading this are on ComfyUI rather than on
fal. For you:

- **The prompts transfer. The seeds do not.** A seed is only meaningful together
  with the sampler, scheduler, step count and guidance that consumed it. Your
  graph will not match an undisclosed hosted configuration, so the same seed
  produces a different image.
- **Use the prompts as prompts**, and pick your own seed. The
  [wildcards](wildcards/) folder is the whole catalog as one prompt per line for
  exactly this reason.
- **The findings still hold**, because they are about what the model does with
  language, not about pixel-level reproduction. Where a finding depends on a
  specific image, the image is committed here and you can look at it.
- **This catalog cannot recommend your settings.** Threads on r/StableDiffusion
  discuss turbo LoRA weight, step counts and VAE swaps for local Krea 2 work.
  That is real knowledge and none of it was measured here, so it is not repeated
  here as though it were.

## What was verified on fal

Regenerating two text-to-image entries and comparing against the committed files
gave a mean per-pixel difference of **1.3 and 1.5 out of 255**, which is WebP
re-encoding loss. The seed reproduces the generation; the repo stores the
re-encode.

```bash
python3 scripts/regen.py --id typography-012
```

The endpoint is deterministic: a repeat run at identical seed, strength, prompt
and input bytes came back pixel-identical, 0 of 1,048,576 pixels different.

The five `editing-*` entries are the exception and the number is much larger. An
image-to-image re-run from a clone is fed the WebP in this repo, not the original
PNG the edit was made from, and that input difference compounds. Regenerating
`editing-003` this way gives a mean per-pixel difference of **17.0 out of 255**.
The composition, palette and medium come back; the brush-level texture does not.
Read those five as reproducible edits, not as reproducible pixels.

## Cost

The fal runs cost $4.54 across 561 generations, about $0.0084 per image at the
time. Batch 9 used 192 included Krea web credits for 96 outputs and added no cash
spend. The catalog now accounts for 657 generations in total.
