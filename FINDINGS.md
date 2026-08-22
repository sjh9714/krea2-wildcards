# Krea 2 prompt field guide

A practical starting point drawn from **475 prompt-and-image pairs across 61 categories**.

## A prompt order that is easy to adapt

```text
medium or style + subject + setting + composition + lighting effect + mood + texture or camera detail
```

Keep the subject and setting concrete. Then change one visual decision at a time so you can tell which phrase moved the image.

## Put the medium first when style is the goal

Open with the visual medium, then describe the subject in language that belongs to that medium. For an illustration, prefer linework, painted background, flat colour, paper grain, ink, wash, or brush texture. For a photo, use lens, depth, exposure, and lighting language.

The [style recipe book](styles/README.md) includes eight whole-scene clauses and a neutral base subject you can copy directly.

## Describe the light you want to see

Use the visible result: soft wraparound light, a narrow rim, hard noon shadows, broad window-shaped highlights, or cool overhead light. Name the fixture only when the fixture itself belongs in the frame.

## Write visible text explicitly

For posters, packaging, signs, and interfaces, include every word that must appear. Keep important type large, front-facing, and separated from busy detail. The typography, poster, packaging, and UI categories give you copy-ready starting points.

## Make composition instructions observable

Prefer instructions you can see immediately: waist-up, centered, one object, three-quarter view, generous negative space on the left, or a top-down grid. If a layout matters, state the number and position of the major elements.

## Build controlled variations

1. Copy a nearby prompt from the gallery.
2. Replace the subject while keeping composition and medium fixed.
3. Replace the medium while keeping subject and composition fixed.
4. Save the versions you want to compare, then move only one more slot.

Use [TEMPLATES.md](TEMPLATES.md) for fill-in-the-blank structures and [VOCABULARY.md](VOCABULARY.md) for recurring visual terms.

## Use the library in ComfyUI

1. Download the current release and copy `wildcards/` into `ComfyUI/wildcards/`.
2. Install `comfyui-dynamicprompts` or another node that supports wildcard syntax.
3. Use `__all__` for the full library or a category name such as `__fashion__`, `__product__`, `__photography__`, or `__illustration__`.
4. Keep the prompt text and choose local sampler, scheduler, steps, and seed for your own graph.

See [REPRODUCING.md](REPRODUCING.md) for the hosted generation settings and the distinction between hosted and local seeds.
