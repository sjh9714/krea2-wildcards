# Wildcards

499 prompts from [this catalog](https://github.com/sjh9714/krea2-wildcards),
one per line, ready for a wildcard or dynamic-prompt node.

- `all.txt`. Every prompt, 499 lines
- one file per category (63 of them), if you want to sample within a style

[Download every category as one zip](https://github.com/sjh9714/krea2-wildcards/releases/latest/download/krea2-wildcards.zip).

## ComfyUI

This repository provides prompt files, not a custom node. No custom node from
this repository is required.

Drop this folder into `ComfyUI/wildcards/`, then reference it from a dynamic
prompt node:

```
__all__
__photography__
__typography__
```

## Format notes

**The seeds, and you probably do not want them anyway.** A wildcard file is one
prompt per line and has nowhere to put a seed. More to the point, the seeds in
this catalog were recorded against fal's hosted `krea-2/turbo`, which publishes
no step count, CFG, sampler or scheduler. In your own graph the same seed gives
a different image. Take the prompts, pick your own seed, and read
[REPRODUCING.md](../REPRODUCING.md) before you try to match a specific frame.

The wildcard files contain the published prompt collection only. The repository's
research records stay separate so every random line is ready to use.

Regenerate with `python3 build_wildcards.py`.
