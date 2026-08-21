# Data format

`prompts.json` is the canonical machine readable catalog. The current schema version is `1.0.0`.

## Compatibility

Readers should accept new unknown fields. A change to the meaning or required shape of an existing field increments the major schema version. New optional fields increment the minor version. Corrections that do not change structure increment the patch version.

## Top level fields

- `schema_version` is the semantic version of this contract
- `model` and `model_url` identify the generator
- `repo` identifies the source repository
- `categories` maps category names to descriptions
- `entries` contains published prompt records
- `failures.entries` contains documented failed generations
- `generations` is every generation run across the eight batches
- `discarded_generations` is the count discarded without a surviving record
- `spend` is the measured total generation cost in US dollars

The accounting invariant is shown below.

```text
generations = len(entries) + len(failures.entries) + discarded_generations
```

## Published entry fields

Every published entry has `id`, `category`, `title`, `prompt`, `image`, `params.seed`, and `batch`. Editing entries also have `source` and `strength`. Attribution fields appear only when an entry does not use the catalog default.

## Failure fields

Every documented failure has `id`, `claim`, `expected`, `prompt`, `image`, `params.seed`, and `batch`.

## Minimal reader

```python
import json
from pathlib import Path

catalog = json.loads(Path("prompts.json").read_text())
assert catalog["schema_version"].split(".")[0] == "1"
for entry in catalog["entries"]:
    print(entry["prompt"])
```
