# Krea 2 market launch implementation plan

> Required execution skill is superpowers executing plans. Apply each task in order and stop on failed verification.

**Goal**

Publish a trustworthy `v1.0.0`, improve the repository and gallery conversion paths, then launch it through the approved communities.

**Architecture**

Keep `prompts.json` as the only catalog contract. Extend existing Python builders and the existing verifier. Use GitHub native releases, Pages, traffic, and release download counts. Do not add dependencies or services.

**Tech stack**

Python standard library, generated Markdown and HTML, GitHub CLI, logged in Chrome.

## Global constraints

- Preserve all existing manifest fields and generated formats
- Use `schema_version` value `1.0.0`
- Use `discarded_generations` value `21`
- Enforce `561 = 475 + 65 + 21` from live manifest counts
- Use `https://sjh9714.github.io/krea2-wildcards/` as the canonical gallery URL
- Use `https://github.com/sjh9714/krea2-wildcards/releases/latest/download/krea2-wildcards.zip` as the stable zip URL
- Do not claim that starring a repository sends notifications
- Do not add a custom node, dependency, backend, or analytics service
- Exclude Hacker News

### Task 1  Version the catalog and reconcile generation accounting

**Files**

- Modify `verify.py`
- Modify `prompts.json`
- Modify generated `FINDINGS.md`
- Create `DATA_FORMAT.md`
- Create `CHANGELOG.md`
- Create `ROADMAP.md`

**Step 1  Write failing contract checks**

Add verifier checks that reject a missing or malformed semantic `schema_version`, reject a negative or non integer `discarded_generations`, and require total generations to equal kept entries plus documented failures plus discarded generations.

**Step 2  Prove the red state**

Run `python3 verify.py`.

Expected result is failure because the two new manifest fields do not exist and 561 does not yet reconcile exactly.

**Step 3  Add the minimum contract fields**

Add these top level manifest fields without changing existing fields.

```json
"schema_version": "1.0.0",
"discarded_generations": 21
```

Update the generated findings source text so it says that 21 additional generations were discarded without a surviving record. Correct the stale failure description to say the failures are not part of the 475 entry catalog.

**Step 4  Document the public boundary**

Create `DATA_FORMAT.md` with the stable top level fields, stable entry and failure fields, compatibility rule, and one minimal consumer example using Python standard library JSON.

Create `CHANGELOG.md` with `v1.0.0` and the release date. Create `ROADMAP.md` with Local validation, Editorial fashion, and Krea 2 Edit only.

**Step 5  Build and prove green**

Run `python3 build_catalog.py --build --lang zh --lang ko --lang ja --lang es --lang fr --lang de --lang pt`.

Run `python3 verify.py`.

Expected result is exit code 0 with the exact accounting check passing.

**Step 6  Commit**

Commit with subject `feat publish versioned catalog contract`.

### Task 2  Add release conversion paths and social metadata

**Files**

- Modify `verify.py`
- Modify `build_catalog.py`
- Modify `build_pages.py`
- Modify `build_wildcards.py`
- Regenerate `README.md`
- Regenerate translated README files
- Regenerate `index.html`
- Regenerate `wildcards/README.md`
- Regenerate `wildcards/krea2-wildcards.zip`

**Step 1  Write failing surface checks**

Add verifier checks for the stable latest release zip URL in the README and wildcard README. Add checks for canonical URL, Open Graph title, description, URL, and image in `index.html`. Add checks that the gallery exposes download, repository, and releases destinations.

**Step 2  Prove the red state**

Run `python3 verify.py`.

Expected result is failure because the links, metadata, and actions do not yet exist.

**Step 3  Implement the smallest builder changes**

In `build_catalog.py`, keep the copy path first and add the stable zip download beside the existing `all.txt` path.

In `build_wildcards.py`, add the stable zip link and state that the repository needs no custom node. Keep the existing dynamic prompts dependency note.

In `build_pages.py`, add canonical and Open Graph metadata and a compact action group below the subtitle. Reuse the existing repository slug and derived site URL. Do not alter gallery cards or JavaScript.

**Step 4  Regenerate artifacts**

Run `python3 build_wildcards.py`.

Run `python3 build_catalog.py --build --lang zh --lang ko --lang ja --lang es --lang fr --lang de --lang pt`.

Run `python3 build_pages.py`.

**Step 5  Prove green and deterministic output**

Run `python3 verify.py`.

Run `python3 build_styles.py`.

Run `python3 build_wildcards.py`.

Run `python3 build_vocabulary.py`.

Run `python3 build_gallery.py`.

Run `python3 build_templates.py`.

Run `python3 build_catalog.py --build --lang zh --lang ko --lang ja --lang es --lang fr --lang de --lang pt`.

Run `python3 build_pages.py`.

Run `git diff --exit-code` after staging the intended changes with `git diff --exit-code --cached` used for review.

Expected result is every command exiting 0 and a second build creating no unstaged diff.

**Step 6  Commit**

Commit with subject `feat add release paths and social cards`.

### Task 3  Review, merge, and publish GitHub release

**Files**

- Create temporary `CHECKSUMS.sha256` outside the tracked tree
- No further product files unless review finds a defect

**Step 1  Review the complete branch**

Review the branch diff against this plan. Fix only critical or important findings. Run the full builder and verifier sequence again after fixes.

**Step 2  Push and merge**

Push `codex/market-launch-impl`, open a pull request with the trust and download changes, wait for GitHub checks, and merge only after they pass.

**Step 3  Update repository metadata**

Set the description to `475 reproducible Krea 2 Turbo prompts across 61 categories` and the homepage to `https://sjh9714.github.io/krea2-wildcards/`.

**Step 4  Create checksums and release**

Create SHA 256 checksums for `wildcards/krea2-wildcards.zip`, `wildcards/all.txt`, and `prompts.json` from the merged commit. Publish GitHub release `v1.0.0` with those three files and `CHECKSUMS.sha256` as assets.

**Step 5  Verify the public release**

Verify the release API, each asset URL, the repository homepage, and the Pages gallery return successful responses. Verify the canonical and Open Graph metadata from the live page.

### Task 4  Prepare and publish promotion

**Files**

- Keep drafts outside the tracked repository

**Step 1  Repair existing references**

Open the existing Reddit, X, and GeekNews items that contain the retired Pages URL. Edit them where the platform permits. Where editing is unavailable, add one concise update with the current gallery and release URLs.

**Step 2  Prepare channel specific drafts**

Prepare the r/StableDiffusion correction story, r/comfyui workflow post, X evidence thread, Korean GeekNews submission, Krea Discord feedback request, ComfyUI Discord workflow request, Civitai resource, and ten creator messages. Use campaign parameters that name the source and launch.

**Step 3  Stage browser actions**

Fill every available form in logged in Chrome. Stop immediately before the final publish, submit, save, or send controls. Present one grouped action confirmation for all staged representational actions.

**Step 4  Publish and verify**

After confirmation, publish the staged actions. Open every resulting public URL and verify the correct gallery and release links. Record blocked channels separately with the exact cause.

### Task 5  Attempt the evidence pack roadmap

**Files**

- Create no tracked files until generation capability is verified

**Step 1  Check local capability**

Check for a local ComfyUI installation, Krea 2 model weights, sufficient GPU memory, and an existing generation environment without downloading paid or large assets.

**Step 2  Run the local validation pack when available**

Run 30 prompts across the published categories using fixed local settings. Record outputs and settings in a new clearly named validation directory. Do not present hosted fal seeds as locally reproducible.

**Step 3  Prepare the next two pack manifests**

Draft bounded prompt lists for Editorial fashion and Krea 2 Edit. Do not spend money or download large model weights without a separate financial or resource decision.

**Step 4  Publish only verified evidence**

Add generated outputs and findings only when every referenced image exists and the verifier can cover the new counts. Otherwise leave the roadmap items open with the measured blocker.
