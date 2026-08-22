# Contributing

**The short path: [open an issue with the form](https://github.com/sjh9714/krea2-wildcards/issues/new?template=add_entry.yml).**
Paste the prompt, drop the image, name the seed. You do not have to touch a
file, and a maintainer adds it. Credit stays on the entry with a link to you.

Two rules, and they are the whole quality bar:

1. **The prompt must reproduce.** Paste it verbatim, run it, get something
   recognisably like the image. If it only worked once with a seed you lost,
   it does not belong here.
2. **The image must be the unedited model output.** No upscaling, no retouching,
   no cherry-picked crop. This catalog is a record of what the model does, not
   of what you can make it do with an hour in Photoshop.

## If you would rather send a pull request

Add an object to `prompts.json`:

```json
{
  "id": "photography-042",
  "category": "photography",
  "title": "Short descriptive title",
  "prompt": "The full prompt, exactly as you ran it",
  "image": "images/photography-042.webp",
  "params": {"seed": 1234},
  "prompt_author": "@yourname",
  "prompt_author_link": "https://github.com/yourname",
  "source_links": ["https://x.com/yourname/status/..."],
  "license": "CC-BY-4.0",
  "notes": "Anything a reader needs to reproduce it"
}
```

Drop the image at that path and open the PR. The attribution fields are required
on anything that did not come from this repo's own runs, and `verify.py`
enforces that.

**Do not edit the generated files.** `README.md`, `README_ZH.md`, `README_KO.md`,
`FINDINGS.md`, `VOCABULARY.md`, `TEMPLATES.md`, `docs/gallery*.md`,
`docs/comparison.md`, `wildcards/`, `workflows/`, `guides/`, `index.html`,
`sitemap.xml`, `robots.txt` and `EDITING_RECIPES.md`
are all built from `prompts.json` and `vocabulary.json`. A workflow rebuilds them
when the manifest changes, and CI fails a pull request whose generated files do
not match its data.

To build them yourself:

```bash
python3 build_styles.py
python3 build_wildcards.py
python3 build_vocabulary.py
python3 build_gallery.py
python3 build_templates.py
python3 scripts/build_workflows.py
python3 build_pages.py
python3 build_site.py
python3 build_social.py
python3 build_catalog.py --build --lang zh --lang ko --lang ja --lang es --lang fr --lang de --lang pt
python3 scripts/audit_prompts.py
python3 verify.py
```

## What CI checks

`verify.py` checks that the prose matches the data, every seed is present, every
category anchor is reachable, download sizes match the files, vocabulary rules
hold, and generated files are in sync. It keeps every published surface aligned
with the catalog as new prompts arrive.

## About the seeds

Seeds here were recorded against fal's hosted `krea-2/turbo`. If you contribute
from a local graph, include the sampler, scheduler, steps, CFG, and model version
your setup exposes so another user can follow the same recipe.
[REPRODUCING.md](REPRODUCING.md) has the hosted generation details.

## Submission checklist

- The prompt describes a subject as well as its visual treatment
- The entry adds a distinct composition, medium, use case, or style
- The image is the original model output and clearly demonstrates the prompt
- The generation settings needed to repeat it are included
- Work from another creator carries their name, source link, and license
