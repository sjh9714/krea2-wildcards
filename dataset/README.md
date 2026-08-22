---
license: mit
language:
  - en
task_categories:
  - text-to-image
tags:
  - krea-2
  - image-generation
  - prompt-engineering
  - comfyui
configs:
  - config_name: default
    data_files:
      - split: train
        path: prompts.jsonl
---

# Krea 2 Wildcards

This dataset contains 499 curated English prompts across 63 active categories, each paired with the URL of its generated Krea 2 output. It is a compact, row-oriented export of the open [Krea 2 Wildcards](https://github.com/sjh9714/krea2-wildcards) catalog for filtering, analysis, and prompt retrieval.

This is a community dataset, not an official Krea release.

## Fields

- `id`, `category`, and `title` identify the catalog record.
- `prompt` is the exact text used for the shown generation.
- `image_url` points to the corresponding generated WebP output in the source repository.
- `params` preserves generation provenance such as seed or hosted generation ID.
- `batch` records the curation batch.
- Editing records may also include `source`, `strength`, or `attribution`.

## Use

```python
from datasets import load_dataset

dataset = load_dataset("sjh9714/krea2-wildcards", split="train")
product_prompts = dataset.filter(lambda row: row["category"] == "product")
print(product_prompts[0]["prompt"])
```

For visual browsing, exact prompt-to-output comparison, downloadable ComfyUI workflows, and category wildcard files, use the [project gallery](https://sjh9714.github.io/krea2-wildcards/) or the [v1.2.0 release](https://github.com/sjh9714/krea2-wildcards/releases/tag/v1.2.0).

## Provenance and limitations

The images are AI-generated Krea 2 outputs and may contain typical generative-image artifacts. Prompts were retained only after their corresponding output was generated; the dataset does not add untested prompt text to inflate its size. The export contains no model weights and does not imply endorsement by Krea.

The prompt catalog, metadata, and repository assets are published under the source repository's MIT license. Krea states that compliant users own the outputs they generate; use of the Krea 2 model remains subject to the [Krea 2 license](https://www.krea.ai/krea-2-licensing) and [acceptable use policy](https://www.krea.ai/krea-2-use-policy).

## Maintenance

`prompts.json` in the source repository is canonical. `dataset/prompts.jsonl` is generated with:

```bash
python3 scripts/build_dataset.py
```

Report data issues in the [source repository](https://github.com/sjh9714/krea2-wildcards/issues).
