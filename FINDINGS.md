# What this model actually does

Everything below was measured while building this catalog, not quoted from the model card. 561 generations were run across eight batches. 475 are published, 65 are documented failures, and 21 additional generations were discarded without a surviving record. Each claim names the entries that demonstrate it; every published entry and documented failure carries its seed and batch number, so you can check it against the images in this repo.

Five of these findings replace earlier ones. Four were overturned by experiments built to confirm them, the last of those by a prediction written down before the images existed. The fifth was overturned by a reader on Reddit two hours after this was published, who counted fingers I had only glanced at.

Each finding below is measured against images committed to this repo.

|  | Finding | What it costs you if you don't know |
|---|---|---|
| **Text** | It renders any string you write out, at any count. It cannot invent one. | Menu rows left to the model came back `CAPEME`, `CABIELO`. Write every string. |
| **Text** | Small and rotated type is a second, independent limit. | Nine station names written out, four correct. |
| **Korean** | Mostly works, and the words that fail repeat the same misspelling at a different seed. | Rerolling the seed is the wrong fix. Change the wording. |
| **Hands** | **Withdrawn.** I claimed 7 of 8 sound. Two readers counted; three had six or four digits. | The whole category is in the failures now, with seeds. |
| **Identity** | A face does not survive into a new scene. 0.45 keeps the face and the old composition; 0.72 keeps neither. | There is no working value in between. Train a LoRA. |
| **Editing** | Medium conversion is reliable at strength 0.50, 0.60. Adding or removing objects is not. | Asked to remove steam, the steam came back. |
| **Counting** | Objects count correctly from 2 to 8. Attributes do not. | "Exactly two flat colours" returned four. |
| **Lighting** | Name the fixture and the fixture walks into frame. | Say what the light *does*, not what it is. |
| **Stationery** | Six for six, and not because the strings were short. | The one category that never failed. |
| **UI** | Layout always right, text only as good as your prompt. | Nine of ten mockups failed on invented labels. |
| **Letters** | Side by side is fine. Asking two letterforms to share strokes is not. | Interlocked `R`+`W` reads as a `P`. |
| **Patterns** | `seamless` does not tile. One of eight had a joinable edge. | Wallpaper and textile pipelines will show the seam. |
| **Aerial** | `straight down` is a request, not an instruction. | Five of eight came back oblique. |
| **Similes** | A size comparison can replace your subject. | "A beetle the size of a pony" returned a pony. |
| **Styles** | Name a style and it may draw the style as an *object*. Describe the whole scene as the medium and the frame converts. | Asked for children's-book style, it put a picture book on the table. "The whole scene drawn as ..." fixed it. |
| **Negatives** | **Measured, and weaker than the folklore.** Half of these prompts contain a "no X" clause; their failure rate is 12.4% against 11.6% for prompts without one. | 3 of 65 failures are a negative being ignored outright. Do not blame a negative before checking the rest of your prompt. |

### It renders text you write. It cannot invent text.

**This replaces the finding that stood here for three batches, and the replacement came from an experiment designed to confirm it.**

The old claim was that text fails by *count*: one sign holds, a list collapses, and somewhere between four strings and six there is a ceiling. To find the ceiling I built a ladder, the same brass nameplate, the same style, the same short word-like strings, varying only in how many share the frame. `stringcount-1` through `stringcount-8`.

**Every string I asked for rendered, at every rung.** VULCAN. 1938. MODEL 7. SHEFFIELD. SERIAL 4412. 440 VOLTS. 50 CYCLES. MADE IN ENGLAND. Legible, spelled correctly, on a plate, at eight independent strings.

**Two rungs also engraved something I did not ask for**, and this paragraph used to open with "all eight are correct", which is not the same claim and should never have been written. `stringcount-5` puts a spurious `7` beside SHEFFIELD, a sixth element on a five-string plate. And `stringcount-2` engraves the `/` I was using as a separator, so the plate literally reads `VULCAN / 1938`. A reader on r/StableDiffusion, **u/FotografoVirtual**, caught the first one by reading the plate against the prompt; the second turned up when I went back and checked all eight because of it.

So the ladder answers the question it was built to answer, count is not the limit. And it does not license the sentence "the plates are flawless". What is added is not a failure of the strings, it is a failure to suppress everything else.

So count was never the variable. Going back through every text failure in this repo, the split is exact and it is about **who wrote the string**:

- The chalkboard menu specified `FILTER 4.50`, `CORTADO 4.00` and `OAT +0.60` and asked the model to fill the rest of the board. **Those three rendered correctly.** The unspecified rows came back `CAPEME`, `CABIELO`, `PANSRUR`.
- The twelve book spines said "invent plausible titles". Twelve failures.
- The transit map asked for "legible station names" without naming any. Thirty failures.
- The timeline fixed the range at 1970, 2030 and left the labels free. **The years rendered. The labels did not.**
- The terminal specified `$ make install` and asked for "three lines of plausible build output". **The command rendered. The output did not.**
- Of ten UI mockups, the one that worked is `ui-004`, where every string was written out: `Sign in`, `Email`, `Password`, `Continue`. In the cuts, `ui-007` got `Add to cart` exactly right beside an invented product title of pure noise, and `ui-010`, given no column names at all, headed all three columns with the word `Kanban`: reaching for the nearest word in the prompt.

Non-Latin script is a partial exception and it is about the script rather than about authorship. Four of six specified Korean strings render exactly and two fail repeatably. See the next finding.

**Practical rule: write out every string you want to see, in the prompt, exactly. Never ask this model to make up a word.** Eight strings is not a limit. It is just where I stopped testing.

**Batch five tested this on purpose.** If the rule is right, a category built entirely on written-out strings should work. Ten poster and packaging layouts, every string specified: `KLANG` / `14 MARCH` / `HALLE 7`; `ALPINA` / `BY RAIL`; `LOWLIGHT` / `SIDE A`; `WORKS ON PAPER` / `GALLERY NINE`; `STATIC` / `FRIDAY`; `EYE PROTECTION` / `AREA 4`; `CLOS MARIN` / `2019` / `MIS EN BOUTEILLE`; `MEND IT` / `DON'T END IT`. **All correct.** `poster-008` carries five strings across a book cover and its spine, including the title repeated vertically, and every one of them is right.

One of the ten failed, and not by count: `poster-004` renders `NORTHERN LIGHT` with **both R's mirrored**. The string is right and the glyph is drawn backwards. So specifying the text buys you the text, not a guarantee about every letterform in it: read the output.

**Batch six went back to the original failures and changed one thing.** The chalkboard menu, the twelve book spines and the transit map are the three scenes this catalog's first text finding was built on. All three were re-run with every string written out and nothing else altered:

- `respecify-menu`, **all ten rows are real, correctly spelled words**, against `CAPEME`, `CABIELO`, `PANSRUR` the first time. The item-to-price pairing drifted (MOCHA and OAT share a line) but there is no invented text anywhere on the board.
- `respecify-spines`, **ten of twelve titles correct**, against twelve unreadable spines the first time. The one clear error merges `THE QUARRY` and `DUST` onto one spine and drops an R.
- `respecify-map`, only **four of nine** stations correct. `MILL LANE` came back `MILLLANYNE`, `CENTRAL` came back `EECTFRAL`.

So specifying the strings is necessary and it is not always sufficient, and what separates the three is not how many strings there are. The menu is large horizontal type on a flat board. The spines are large but rotated ninety degrees. The map is small type set at several angles at once. **The second constraint is how small and how rotated the type is**, and it is independent of the first.

### Korean mostly works, and the words that fail, fail the same way every time

**This replaces a finding built on a single Korean image.** It said Korean fails even when written out. Six Korean strings later, that is too strong.

**Four of six came back exactly right**: `국수`, `도서관`, `3번 출구`: Hangul mixed with a numeral. And `오늘의 추천 메뉴`, six syllables across three words. Length is not the variable, which is the first thing to go: the two-syllable and the six-syllable both worked and a four-syllable failed.

Two failed:

- `정직한 국수` came back `정적한 국수`. One vowel wrong in the second syllable. This is the original failure, and it **reproduced at a different seed** (1167746582 against the first attempt's 1910572019). Same string, same error, twice. That is a property of the string, not a bad roll.
- `한밭식당` came back `한뾃식당`, where `밭` has become a syllable that does not exist in Korean.

What the two failures share is a less common 받침, the final consonant. `직` and `밭` both carry one; so do `국` and `늘` and `천`, which all rendered. Two failures is not enough to name the mechanism, and that is where it is left.

Practical rule, and it is better news than the old one: **Korean is usable, and you must read the output.** If a string comes back wrong it will come back wrong again, so change the wording rather than re-rolling the seed.

### I said hands were solved here. Two readers counted, and I have withdrawn the whole category.

**This is the finding this catalog got most wrong, and it was corrected from outside within three hours.**

What it said: eight prompts on one table under one light, seven anatomically sound, the only miss a gesture rather than the anatomy. "AI can't do hands" does not survive a controlled test. It was the most shareable sentence in the repository and it was built on inspecting the outputs at 1.5-2x.

Within two hours of posting to r/StableDiffusion, **u/sickmartian**: *"well, exactly 3 fingers has a total of 6 fingers 😅 also 6 on handshake, harder to see thou"*. At 4x they are right on both. Twenty minutes later **u/wikid24** on the clasped pair: *"clasped is also incorrect, only 4 fingers"*.

Three of eight, found by two people who did the one thing I did not: count.

**So the entire category is withdrawn.** Not graded image by image, withdrawn. The instrument that failed is my own inspection, and using it to arbitrate which of the remaining five survive would be the same mistake a third time. All eight are in the failures with their seeds; they are evidence now, not examples.

**What is left, stated narrowly.** `hands-5` asked for fully interlaced fingers and returned a clasp. It declined the gesture rather than mangling it, and that is a claim about behaviour, not anatomy. `hands-8` did raise exactly three fingers, so the count instruction landed, on a hand that has too many digits.

**Why it happened.** Every other finding here was built by holding one variable fixed and varying another, the string ladder, the count ladder, the weave ladder with its prediction committed first. This one was built by looking at pictures. Looking is the weakest instrument in this repository and it went on the claim most likely to travel, which is exactly the wrong place to put your weakest instrument.

### Character identity does not survive across generations

A reference sheet of a specific person renders well, see **reference-sheet-001**. Reusing that person in a new scene does not work, and image-to-image does not rescue it, because the two useful settings fail in opposite directions:

- `strength 0.72`, genuinely new scene, but a different person. Only the sweater and the palette carry over.
- `strength 0.45`, recognisably the same person, but the source composition comes with her. A three-view studio sheet became the same three views at a harbour.

There is no middle setting that gives the same face in a different photograph. If you need a consistent character, train a LoRA; prompting cannot do it. This is why there is no character-consistency category here.

### It changes medium willingly and scene content reluctantly

Image-to-image is reliable when you ask for a different *rendering* of the same scene. Rice terraces became a convincing gouache painting with the terrace contours intact (**editing-003**); a woodblock wave took a dusk palette while every keyblock outline stayed put (**editing-005**); an exploded camera diagram became a clean cyanotype blueprint with every component in place (**editing-008**).

It is unreliable when you ask it to add or remove *things*. Three attempts failed and were cut rather than shipped with captions that did not match the images: removing the steam from a mug returned the steam; adding snow and sea ice to a coastline returned the same coastline slightly cooler; darkening a sauna's window returned the window still lit.

`strength` between 0.50 and 0.60 preserved composition while allowing the medium to change. No value made object-level edits work.

### It counts objects. It does not count attributes.

**This is the second finding in this catalog overturned by an experiment built to confirm it.**

It used to say numbers were treated as flavour: I had asked for "exactly two flat colours" and got four, and for a map "divided into five regions" and got eight. To find where counting breaks I ran a ladder. One slate shelf, one white ceramic egg, `exactly N` of them, N from two to eight, nothing else changed. `objectcount-2` through `objectcount-8`.

**All seven are correct.** Two eggs, three, four, five, six, seven, eight. Counted straight off the shelf. Elsewhere in the same batch, `still-life-003` asked for five pieces of glassware and delivered five, `still-life-005` asked for six ceramics and delivered six, `still-life-007` asked for three pears and delivered three.

So the split is not numbers versus no numbers. It is **objects versus attributes**:

- **Discrete separable things that are the subject of the frame get counted.** Eggs, pears, columns, markers, table rows, cake layers.
- **Attributes and emergent divisions do not.** "Exactly two flat colours" is a property of the rendering, not a set of objects, and came back as four with shading (`portrait-008`). "Five regions" on a watercolour map are boundaries that emerge from where the pigment stops, not things you could point at one at a time, and came back as eight (`infographic-007`). "One light source" is not a visible object either, and produced two lamps.

Practical rule: if you can point at each one, ask for a number and expect to get it. If you are counting colours, zones, materials or light sources, count the output yourself.

Batches seven and eight kept confirming it without being asked to. A hand held up showing **exactly 3 fingers** (`hands-8`) came back with exactly three. A comic page asked for **exactly 6 panels** (`comic-005`) came back with six. A grid of **sixteen** pixel food icons (`pixel-art-005`) came back four by four. Four bird wings, three hyacinth bulbs, three hammers, six chisels, three wine glasses. All correct. The rule has now held on eight independent occasions across five batches, and it has never once held for a colour count, a region count or a light count.

### Name a light and you get the light. Name the softbox and you get the softbox.

Twice in one batch, naming the physical lighting equipment put that equipment in the frame as a subject.

`portrait-012` asked for a corporate headshot with a **large softbox front and slightly above** against a seamless grey background, and returned a portrait with two large white softboxes flanking the subject. `collectible-008` asked for a rubber duck under **a single large softbox above and behind** and returned a duck with a full lighting umbrella open behind it, filling half the frame.

The prompts that worked describe the *light*, not the *fixture*: "hard low-angle late afternoon sun from frame right", "single hard light high and to camera left", "soft directional daylight". All three rendered the lighting condition with nothing extra in shot.

Practical rule: say what the light does, never what makes it.

### Stationery went six for six, and the reason turned out not to be brevity

The six `stationery-*` entries all rendered their text correctly on the first attempt, `NORTHFIELD & CO`, `FRAGILE`, `ADMIT ONE`, `PAID`: with nothing cut. It is still the cleanest text result in the catalog.

I originally read that as evidence for a brevity rule: one short string in one frame is the shape the model is good at. The `stringcount` ladder says otherwise. Those six succeeded because **every one of them was written out in the prompt**, not because there was only one of them.

`stationery-006` is still the entry to look at. The red `PAID` impression on the paper is correct, and the rubber stamp lying beside it carries the same word **mirrored**, which is what a real stamp face does. Nobody asked for that.

### Interface mockups: the layout is always right, and the words are only as good as your prompt

I added ten UI mockups to batch three expecting nine of them to fail, and nine of them failed. That was the point: a limit you only predict is not a measured limit.

What is striking is *which* half breaks. The structure is consistently correct: `ui-002` has three grouped sections of three rows with a toggle on each, some on and some off, hairlines between; `ui-008` has alternating chat bubbles with avatars, timestamps and a pinned input; `ui-010` has three kanban columns with count badges, tag pills and avatars. Every one of those is exactly what was asked for.

The strings are not. `ui-002` renders the first section header as `Settings` and then degrades to `Sectings` for the next two. `ui-006` fails at the day headers *and* at the dates, the first week reads 5, 6, 51, 13, which is not a week.

The one that worked is **ui-004**, the login screen, and it worked because it has four short real strings: `Sign in`, `Email`, `Password`, `Continue`. All four are letter-perfect. The same effect shows in the cuts, `ui-007` got `Add to cart` exactly right while inventing gibberish for the product title.

At the time I read this as a hard limit on interface work. The `stringcount` ladder shows it is not: **the strings failed because I did not write them.** `ui-004` proves it from inside the same category. Four written-out strings, four correct renders. And `ui-010` proves it from the other side, heading all three columns `Kanban` because that was the only word I had given it.

Practical rule: mock up an interface by writing out every label you want to see. What you leave to the model comes back as noise; what you specify comes back correct.

### Letters are fine. A bespoke interlocked monogram is not.

**Third correction, same cause: a claim built on one failure.**

Batch four asked for a monogram of the letters `KJ` interlocked in a circle, got three letterforms, and concluded that the model renders words and not arbitrary letters, reasoning that `COOPERAGE` at nine letters worked while `KJ` at two did not.

Batch five put three more arbitrary letter pairs through. `monogram-002` asked for an A and an E joined into a ligature and returned a clean, correct engraved Æ. `monogram-003` asked for H and B side by side, blind-embossed, and returned exactly that. Both are arbitrary pairs and neither is a word.

The one that failed again is `monogram-001`, R and W **interlocked**. And where the two forms overlap, the R reads as a P.

So it was never about words. Letters render.

This was originally written as a rule about **fusing forms so they share strokes**, and batch eight killed that reading: chain links, basketry and Celtic knotwork all interlace heavily and all came back correct. What is left is the narrow observation: `AE` is a ligature that already exists as a glyph and `HB` is two letters set side by side, while an interlocked `KJ` is a bespoke mark that does not exist anywhere.

Practical rule: set letters side by side, or ask for a ligature that actually exists. An invented interlock is the one that failed twice.

### "Seamless" produces a pattern that does not tile

All eight `pattern-*` prompts asked for a seamless repeat. I tiled the outputs and measured the seam by comparing each image's left edge column against its right, and its top row against its bottom, against the baseline difference between two arbitrary interior columns of the same image.

**One of the eight tiles.** That one is `pattern-007`, vertical hand-drawn stripes, where the edges match because vertical stripes match trivially, structural luck, not the instruction being followed. `pattern-005` tiles horizontally and not vertically. The remaining six have edge differences at or above their own interior baseline, meaning the two edges are as unrelated as two random slices.

The images are good. Several are genuinely beautiful surface designs. They are just not repeat tiles, and if you drop one into a wallpaper or textile pipeline expecting it to run, it will seam.

Practical rule: treat these as one-off surfaces. Making them actually tile is a post-process, not a prompt.

### "Straight down" is a request, not an instruction

Eight aerial prompts, every one of them opening with *straight down on…*. **Five came back oblique.** `aerial-003` shows the container cranes standing up in frame; `aerial-008` is at bridge height; `aerial-005`, asked for a suburb from directly above, came back **from the pavement**. Not an aerial at all.

**The fifth was mine, and it sat inside the explanation for four batches.** This finding used to say four held, and described them as "a braided river, salt evaporation ponds, the edge of a reef, a terraced hillside. All four flat subjects whose whole content is pattern". A terraced hillside is not a flat subject. Re-checked against this repository's own test for the failures, are verticals visible in frame, `aerial-007` fails it: the terrace risers are visible, the hillside recedes toward the upper left, and there is aerial haze along that axis. It is a high oblique of the same kind as `aerial-001`, and it has moved to the failures.

**Three held**, and all three are genuinely flat: a braided river, salt evaporation ponds, the edge of a reef. Nothing in any of them stands up. Where the scene contains anything with obvious verticality, cranes, houses, bales, terrace risers: the camera tilts back down to a view that shows those verticals.

Practical rule: ask for nadir only on subjects that have no useful vertical, and check the angle before you accept the frame. Naming the altitude or the lens does not help; the pull is in the subject.

A note on how this was caught, because it matters more than the entry. Two findings here were overturned by readers who looked harder than I did, the hands claim and a nameplate. This one I found by going back through every finding that rests on looking at a picture and applying the test the finding itself had written down. The picture had not changed. The sentence "all four are flat subjects" was the counterexample, in the same paragraph, the whole time.

### A size comparison can replace your subject with the thing you compared it to

`fantasy-009` asked for **a beetle the size of a pony** wearing a worn leather harness. It returned a pony wearing a worn leather harness. No beetle, no chitin, nothing insect about it. Every other detail of the prompt was honoured on the wrong animal.

The comparison was doing scale work and the model read it as identity. Every other creature prompt in the same batch landed: a hare with moth wings, an invented bioluminescent fish, a feathered theropod in snow. None of those contains a simile.

Practical rule: give scale with a measurement or with something inert in the frame, "a beetle a metre long", "a beetle beside a fence post". Do not give scale by naming another animal, because the other animal can win.

### A rule this catalog built, tested and had to throw away

Two findings above once shared an explanation: letters asked to interlock failed, fingers asked to interlace failed, so the model must be unable to render forms that **pass through each other**. Two domains agreeing is persuasive, and it was wrong.

Batch eight tested it in a third domain, rope and chain, with the per-entry prediction written down **before the images were generated**. Four entries were predicted to fail. All four succeeded: `weave-5` two interlocked chain links, `weave-6` a whole chain with every link through its neighbours, `weave-7` a willow basket wall with the weavers passing correctly in front of and behind each stake, and `weave-8` a Celtic knotwork panel interlacing continuously without a break. Chain and basketry interpenetrate far more than fingers do.

The rule is dead. What it leaves behind is an observation, and it is only that: in every failure across all these batches, **what came back was the more common neighbour of what was asked for**. Interlaced fingers returned a clasp. An interlocked `KJ` returned a generic monogram. A figure-eight *knot* (`weave-4`) returned a figure-eight *shape*. A beetle the size of a pony returned a pony. Chains and baskets are among the most photographed objects there are, and they came out right.

That reading is not promoted to a finding here. Promoting a two-domain coincidence is precisely the mistake that just cost this catalog a rule, and the replacement being a better story is not a reason to trust it. It needs its own experiment with its own prediction written first.

The prediction and the result are in the toolkit repo at `playbooks/weave-prediction.md`, timestamped by the commits either side of the generation run.

### A negative clause costs you almost nothing, and I said the opposite

**This one was added because I asserted it in public before I had counted it.** A reader on r/StableDiffusion pointed out that a prompt of mine said `no colour anywhere`, and that a model does not read negative language in a positive prompt as one instruction. I replied that this repo already documented that behaviour. It did not. I had seen negatives in a lot of the failures and filled in the rest.

So I counted, and the folklore is weaker than either of us assumed.

| | prompts | failure rate |
|---|---|---|
| with a `no X` clause | 290 | **12.4%** |
| without one | 250 | **11.6%** |

Odds ratio **1.08**. The reason 38 of the 65 failures contain a negative is that **290 of the 540 prompts contain a negative**. The denominator was doing the work and I had only looked at the numerator.

What survives is narrower and worth knowing: **3 of the 65 failures are a negative being ignored outright** (`fashion-007`, `mirror-004`, `sport-003`). Three. Do not reach for the negative as the explanation before you have checked the rest of the prompt.

None of this makes a negative the best phrasing. `monochrome` still beats `no colour`, because the antonym states what you want and the negative states what you do not. It just is not the failure cause it gets blamed for.

Reproduce the three numbers with `python3 scripts/measure_negatives.py`; the script re-reads the manifest, so if the catalog grows and the numbers drift, it says so.

## Reproducing any of it

See [REPRODUCING.md](REPRODUCING.md) for the exact call, the measured per-pixel differences, and the reason these seeds do not transfer to a local graph.
