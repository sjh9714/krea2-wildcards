---
license: mit
pretty_name: Krea 2 Turbo Prompt and Output Catalog
language:
  - en
task_categories:
  - text-to-image
size_categories:
  - n<1K
tags:
  - krea-2
  - krea-2-turbo
  - image-generation
  - prompt-engineering
  - prompt-dataset
  - comfyui
  - comfyui-workflow
configs:
  - config_name: default
    data_files:
      - split: train
        path: prompts.jsonl
---

# Krea 2 Turbo Prompt and Output Catalog

This dataset contains 511 usable English prompts across 63 active categories. Every row keeps the exact prompt, the URL of its generated Krea 2 output, and generation provenance for filtering, retrieval, and prompt reuse.

It is the row-oriented export of the open [Krea 2 Wildcards](https://github.com/sjh9714/krea2-wildcards) catalog. This is a community dataset, not an official Krea release.

## Start here

- [Browse prompts beside their generated outputs](https://sjh9714.github.io/krea2-wildcards/).
- [Open the native six-node starter in Comfy Cloud](https://cloud.comfy.org/?share=78d328f1548e).
- [Download the versioned v1.2.0 prompt pack and both ComfyUI workflows](https://github.com/sjh9714/krea2-wildcards/releases/tag/v1.2.0).

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

## Provenance and limitations

The images are AI-generated Krea 2 outputs and may contain typical generative-image artifacts. Prompts were retained only after their corresponding output was generated; the dataset does not add untested prompt text to inflate its size. The export contains no model weights and does not imply endorsement by Krea.

The prompt catalog, metadata, and repository assets are published under the source repository's MIT license. Krea states that compliant users own the outputs they generate; use of the Krea 2 model remains subject to the [Krea 2 license](https://www.krea.ai/krea-2-licensing) and [acceptable use policy](https://www.krea.ai/krea-2-use-policy).

## Maintenance

`prompts.json` in the source repository is canonical. `dataset/prompts.jsonl` is generated with:

```bash
python3 scripts/build_dataset.py
```

Report data issues in the [source repository](https://github.com/sjh9714/krea2-wildcards/issues).
