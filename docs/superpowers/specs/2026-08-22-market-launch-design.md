# Krea 2 market launch design

## Goal

Turn the existing catalog into a trustworthy versioned release, make the main user actions obvious, and launch it through channels where image generation and ComfyUI users already gather.

## Current behavior

The repository already publishes 475 prompts, 65 documented failures, images, a static gallery, wildcard files, translations, and reproducibility notes. It has no release, no declared data contract, no direct release download on the main surfaces, and no canonical or social metadata on the gallery. The manifest says 561 generations while only 540 survive in the repository. Git history shows that the remaining 21 were discarded without a surviving record.

## Product decisions

### Trust and data contract

`prompts.json` remains the only machine readable catalog. A duplicate export would add drift without adding a real format.

The manifest gains `schema_version` with value `1.0.0` and `discarded_generations` with value `21`. Verification enforces this equation.

```text
generations = entries + documented failures + discarded generations
561 = 475 + 65 + 21
```

The findings introduction states the same accounting plainly. The stale failure description is corrected from an 85 entry catalog to the current 475 entry catalog.

`DATA_FORMAT.md` documents the stable fields and compatibility rule. `CHANGELOG.md` records the first public release. `ROADMAP.md` names only the three planned evidence packs already chosen.

### Conversion surfaces

The README keeps the existing copy first path and adds a direct latest release download for the wildcard zip. The wildcard README links to the same release artifact and states that no custom node from this repository is required.

The gallery adds three visible actions near the title.

- Download wildcards
- View the GitHub repository and star it there
- Open releases and use GitHub Watch for release notifications

The gallery adds a canonical URL and Open Graph title, description, URL, and image. Existing copy, search, category navigation, and lazy images stay unchanged.

### Release

GitHub release `v1.0.0` contains four assets.

- `krea2-wildcards.zip`
- `all.txt`
- `prompts.json`
- `CHECKSUMS.sha256`

The repository description uses the measured catalog size. The homepage stays on the working GitHub Pages URL.

### Promotion

The launch uses different messages for different audiences.

- r/StableDiffusion receives the correction and failure data story
- r/comfyui receives the one file wildcard workflow
- X receives a visual evidence thread
- GeekNews receives a Korean maker submission
- Krea and ComfyUI Discord communities receive a focused feedback request
- Civitai receives a resource page
- Ten small creators receive short personal messages tied to their existing work

Hacker News is excluded. Stars are never described as notifications. Release notifications are tied to GitHub Watch.

### Explicit exclusions

No custom node, backend, account system, favorites system, newsletter, new Discord server, or third party analytics script is added. GitHub release download counts, repository traffic, and campaign links cover the first launch. Add event analytics only after traffic is large enough that copy behavior cannot be inferred from downloads and stars.

## Verification

The existing `verify.py` remains the single acceptance command. New checks cover manifest accounting, contract version format, release links, gallery metadata, and gallery actions. Every builder is run before the final verification and generated files must produce a clean git diff.
