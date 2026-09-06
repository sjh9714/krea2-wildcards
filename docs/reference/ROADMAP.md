# Roadmap

## Published baseline

The main catalog contains **514** prompts, including the completed **30-image
editorial fashion pack**. Its Hugging Face export also has 514 rows. The official
text-to-image starter workflows and focused usage guides are published. Do not
repeat these completed additions or mix adapter outputs into this catalog count.
Release **v1.2.1** now publishes the matching 514-prompt ZIP; v1.2.0 and its
original 499-prompt archive are preserved.

## Reference-image shooting pack: validation before general claims

The separate [reference-shoot pilot](../../workflows/reference-shoot/README.md)
contains four visually accepted hosted shots of one synthetic adult character,
with original files, exact instructions, settings and run receipts. It uses Krea
2 Turbo plus a community identity-edit LoRA, not the base model alone.

The [2026-09-06 transfer check](../../workflows/reference-shoot/validation.html)
adds three selected shots from a second synthetic adult. Its four-shot test
returned four outputs; the close-up needs a framing refinement. The next free
request was blocked, so the other two planned sources remain ungenerated.
All four original ComfyUI graphs were actually imported with custom nodes
registered. A queue attempt stopped at missing model weights before inference.

Next validation:

1. Finish the three-additional-source protocol: refine and test the close-up for
   `portrait-002`, then generate four independent shots each for `portrait-003`
   and `portrait-004` when free quota permits. Preserve every attempt's receipt.
2. GPU-run the imported ComfyUI graphs when model storage and suitable compute
   are available. Required weights total about 20.5 GB; downloading them into
   the test machine's roughly 21 GiB free disk would leave inadequate headroom.
   Import checks and hosted Diffusers samples are not substitutes for inference.
3. Observe whether independent users can produce their own shooting set using
   the guide. Downloads and stars alone do not establish repeat use.

Use free quota or an already available GPU only. No paid APIs, model subscriptions
or credit purchases are part of this validation plan.

## Base-model local validation

The original 30-prompt local Krea 2 comparison remains unrun. It is a separate
test from the identity-edit pilot: publish the actual workflow, settings,
outputs and measured differences from hosted fal results when a compatible GPU
environment is available. Do not claim it was completed by the hosted pilot.

Only generated and verified evidence moves from this roadmap into the catalog.
