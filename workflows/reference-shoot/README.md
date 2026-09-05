# Krea 2 reference shoot · experimental v0.1

A small shooting set for one recognizable photographic character: **front,
profile, full-body and close-up**, each generated independently from one original
reference. Keep a good shot and rerun only the one you need.

**[Open the visual preview](index.html)**
· [Exact recipes](pack.json) · [Run receipts](runs.json)

## What is actually verified

As of **2026-09-05**, the free hosted pilot returned three images: one side-profile
shot passed visual review; two front-facing attempts did not meet the requested
viewpoint. The full-body and close-up requests returned a free-quota error, not
images. This is **one accepted shot out of four planned shots**, not a completed
four-shot consistency demonstration or a benchmark.

| Shot | Preset | Hosted sample | ComfyUI execution |
|---|---|---|---|
| Front | [front.json](front.json) | Needs a revised camera instruction | Not GPU-run here |
| Profile | [profile.json](profile.json) | [Visually accepted](examples/profile.webp) | Not GPU-run here |
| Full-body | [full-body.json](full-body.json) | Pending free quota | Not GPU-run here |
| Close-up | [close-up.json](close-up.json) | Pending free quota | Not GPU-run here |

The accepted image is the unchanged provider-returned WebP. The reference is the
repository's existing [synthetic adult portrait](../../images/portrait-001.webp),
not a real person's photograph. Review compared visible face shape, nose, mouth,
hair, viewpoint, clothing, light and obvious artifacts. It is qualitative, not
automated biometric matching. The 514-entry base-model catalog is unchanged.

## Choose an execution route

### Free community demo · no local model installation

Open [conradlocke's Krea 2 Identity Edit Space](https://huggingface.co/spaces/conradlocke/krea2-identity-edit).
Upload the original reference and paste one instruction from the preview.
Set likeness to **2.5**, grounding to **768**, steps to **10**, guidance to **0**,
and turn random seed **off**. Use the shot's recorded seed. LoRA strength is
already fused at **1.0**. These are the pilot's settings, not universal optima.

The demo supplies shared free ZeroGPU time; availability and quotas can change.
Stop when the free quota runs out. Do not buy credits or a plan to run this pack.
An upload goes to a third-party public demo: do not send private client images
or personal photographs without the subject's consent and suitable data terms.

This is **not** Krea web's Style Transfer input. The sample uses Krea 2 Turbo
**plus an unofficial identity-edit adapter**, not the base text-to-image model.

### Local ComfyUI · bring your own GPU

1. Use an up-to-date ComfyUI with Krea 2 support. Install
   [lbouaraba/comfyui-krea2edit](https://github.com/lbouaraba/comfyui-krea2edit)
   following its installation instructions, then restart ComfyUI. The graph's
   socket layout was checked against revision
   [`86f886d`](https://github.com/lbouaraba/comfyui-krea2edit/tree/86f886dac23013d88996e3a2e99093ba44d322fb).
2. Install the model files below. No weights or custom-node implementation are
   bundled with this pack, and the builder does not download or run them.
3. Copy [portrait-001.webp](../../images/portrait-001.webp) to `ComfyUI/input/`, or
   upload your own source through **LoadImage**. Drag one shot JSON onto the canvas.
4. For your own subject, replace the appearance sentence in the positive
   instruction: the example's green eyes, brown bun and charcoal sweater are
   **specific to this character**. Preserve only traits visible in your source.
5. Queue one shot. Review it against the original. Open another shot JSON only
   when ready; never use the last output as the next reference.

| File | ComfyUI folder |
|---|---|
| [krea2_turbo_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_fp8_scaled.safetensors) | `models/diffusion_models/` |
| [qwen3vl_4b_fp8_scaled.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors) | `models/text_encoders/` |
| [qwen_image_vae.safetensors](https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors) | `models/vae/` |
| [krea2_identity_edit_v1_2.safetensors](https://huggingface.co/conradlocke/krea2-identity-edit/resolve/89e9e7a09ee2e5c9331e952063d79b1b8a703280/krea2_identity_edit_v1_2.safetensors) | `models/loras/` |

Defaults: **992 × 992**, batch **1**, **10** steps, Euler/simple, denoise **1**,
ComfyUI CFG **1**, reference strength **2.5**, grounding **768**, LoRA **1**.
The hosted demo's guidance **0** and ComfyUI CFG **1** both mean guidance off
in their respective implementations; do not copy the numeric value blindly.
The hosted demo reduces the 1024-square source to a 992-square output under its
1-megapixel cap. That happens during inference, not by cropping the saved sample.

The graph connects the source to **both** `Krea2EditGroundedEncode` and
`Krea2EditModelPatch`, including the negative's image input. The same empty target
latent feeds the patch and sampler, and the VAE + source pixels are connected
with `fit` mode. A text-only encoder or plain style-reference node is not a
drop-in replacement.

The ComfyUI graphs are **structurally tested, not GPU-executed here**. Hosted
examples use a different Diffusers implementation and checkpoint precision;
matching prompt and seed do not imply identical pixels. No cloud share link,
minimum VRAM claim or guaranteed runtime is provided without a real test.

## Keep / rerun checklist

- Face, hair and distinctive visible traits remain recognizable.
- The requested viewpoint and framing actually change as specified.
- Visible eyes, ears, hands, limbs and clothing have no obvious structural errors.
- Materials, lighting and floor contact remain plausible.

The full-body preset **invents** trousers, shoes and anatomy outside the source
crop. It cannot recover unseen body dimensions. The profile also synthesizes
previously unseen geometry. Avoid treating either as a faithful identity record.

For the front shot, try a lower reference strength or shorter angle instruction
on the next available free run; both are **untested hypotheses**, not fixes already
demonstrated. Record a new attempt instead of replacing its history. Only a full
passing visual review promotes an output to the preview.

## Scope and next validation

First finish the other three shots, then repeat the four-shot test on at least
three visibly different consenting or synthetic adult subjects. Only after
that should this be described as a reusable consistency pack. A GPU smoke test
of the downloadable ComfyUI graph is a separate requirement. Video, multiple
people, outfit transfer and automatic likeness scores are outside v0.1.

## Development

`pack.json` and `runs.json` are source records; `*.json` shot graphs and
`index.html` are generated. Accepted originals live in `examples/`. Unselected
outputs may be retained locally under the ignored `raw/reference-shoot/` folder;
their hashes and provider event IDs remain in the run receipts.

```bash
python3 scripts/build_reference_shoot.py
python3 scripts/build_reference_shoot.py --check
python3 -m unittest discover -s scripts/tests -p 'test_reference_shoot.py' -v
```

The builder performs no inference or upload. It rejects accepted receipts whose
prompt, seed, settings, source hash, output hash, dimensions or required review
checks do not match. CI also tests the reference links and individual-shot graph
structure. Do not add these adapter outputs to the plain Turbo catalog count.

## Attribution and terms

These small graphs are newly authored against the documented interfaces of
[ComfyUI-Krea2Edit](https://github.com/lbouaraba/comfyui-krea2edit), an Apache-2.0
dependency by lbouaraba. The identity-edit LoRA is by
[conradlocke](https://huggingface.co/conradlocke/krea2-identity-edit).
The hosted pilot used the [Space code observed at `3a1adc0`](https://huggingface.co/spaces/conradlocke/krea2-identity-edit/tree/3a1adc03a1b083e61e98105034f09f7aa407242c).
That app loads unpinned model revisions, so exact loaded weight hashes were not
exposed. The pinned LoRA download above improves local reproducibility but does
not retrospectively establish the hosted runtime's weight hashes.

Our scripts, prompts and metadata use this repository's MIT license. Model
weights have separate [Krea 2 Community License terms](https://www.krea.ai/krea-2-licensing);
MIT does not relicense them. This pack is not affiliated with or endorsed by Krea.
