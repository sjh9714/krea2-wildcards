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

**Failures are welcome too.** Sixty-five of them are kept here with the reason
each one was cut, and several findings only exist because a generation went
wrong in a way worth writing down. Say so in the notes and it goes in the
failures rather than the catalog.

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
`FINDINGS.md`, `VOCABULARY.md`, `TEMPLATES.md`, `docs/gallery*.md`, `docs/comparison.md`, `wildcards/` and `index.html`
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
python3 build_catalog.py --build --lang zh --lang ko
python3 build_pages.py
python3 verify.py
```

## What CI checks

`verify.py` runs 190 checks that tie the prose to the data. Every count quoted in
a document against the manifest, every seed present, every category anchored and
reachable, the download table's file sizes against the files, the vocabulary
rule, and that the generated files are in sync. It is not a linter. It exists
because this catalog contradicted itself twice in public, once in two paragraphs
of the same page.

## About the seeds

Seeds here were recorded against fal's hosted `krea-2/turbo`, which publishes no
step count, CFG, sampler or scheduler. **They do not reproduce in a local ComfyUI
graph**, and that is not a bug in your setup. If you contribute from a local
graph, say so and include whatever settings your setup exposes; those are worth
more to a local reader than a seed is. [REPRODUCING.md](REPRODUCING.md) has the
detail.

## What gets rejected

- Prompts that are really just a style name with no content
- Near-duplicates of an existing entry
- Images with visible artefacts presented as successes
- Anything where the model clearly failed and the caption pretends otherwise
- Entries lifted from someone else without credit
