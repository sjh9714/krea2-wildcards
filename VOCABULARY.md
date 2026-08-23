# The vocabulary

The words in these prompts that carry the technique rather than the subject. These are the parts you can lift out and paste into a prompt about something else. Each term recurs across several subjects and categories, and the precision notes show how to phrase the most context-sensitive ones.

*A term is in this file only if it appears in at least 3 entries across at least 2 categories. Below that it is subject vocabulary, not transferable vocabulary. build_vocabulary.py enforces the rule and refuses to build if a term stops meeting it.*

62 terms. 379 of 511 prompts carry at least one of them.

## Precision notes for 7 terms

These recurring terms work best with an extra composition or medium cue.

| term | practical note | guide |
|---|---|---|
| `shallow depth of field` | Background goes soft and reads as photography. For a drawn or painted style, use simplified background detail instead. | [prompt field guide](FINDINGS.md) |
| `straight down` | Asks for a true plan view. Pair it with a flat subject, symmetrical layout, and no visible horizon. | [prompt field guide](FINDINGS.md) |
| `window light` | Creates soft directional daylight and may include the window. Use broad side light when you want only the effect. | [prompt field guide](FINDINGS.md) |
| `fluorescent` | Creates cool, even overhead light. Mention ceiling tubes only when they belong in the composition. | [prompt field guide](FINDINGS.md) |
| `seamless` | Creates a repeat-inspired surface motif. Use a tiling post-process when you need production-ready edges. | [prompt field guide](FINDINGS.md) |
| `limited palette` | Restricts the palette. Name the exact hues for the clearest visual direction. | [prompt field guide](FINDINGS.md) |
| `monochrome` | Builds the image around one hue. Add grayscale or black-and-white when that is the intended treatment. | [prompt field guide](FINDINGS.md) |

## lens

*what the glass is doing*

| term | entries | what it does |
|---|---|---|
| `macro` | **51** in 20 categories | Pulls in to subject-fills-frame distance. The most reliable single word in this catalog for changing scale. |
| `shallow focus` | **18** in 14 categories | Same idea, phrased as a result rather than a setting. |
| `long exposure` | **15** in 10 categories | Moving things smear, still things stay sharp. Water and cloud respond most. |
| `35mm` | **14** in 11 categories | Reportage width. Keeps the surroundings in the story. |
| `shallow depth of field` ⚠️ | **13** in 11 categories | Background goes soft and reads as photography. For a drawn or painted style, use simplified background detail instead. |
| `50mm` | **10** in 7 categories | Roughly what the eye does. The neutral choice. |
| `long lens` | **7** in 7 categories | Flattens distance and stacks the background against the subject. |
| `85mm` | **6** in 5 categories | Compresses and separates. Portrait glass. |
| `24mm` | **3** in 2 categories | Wide. Expect converging verticals and a stretched foreground. |

## framing

*where the camera is and how the frame is cut*

| term | entries | what it does |
|---|---|---|
| `overhead` | **28** in 18 categories | Camera above the subject looking down, not necessarily square to it. |
| `three-quarter` | **22** in 15 categories | Turned partly away. The default product and portrait angle. |
| `straight down` ⚠️ | **17** in 10 categories | Asks for a true plan view. Pair it with a flat subject, symmetrical layout, and no visible horizon. |
| `isometric` | **12** in 3 categories | Parallel projection, no vanishing point. Reliable enough to be its own category here. |
| `symmetrical` | **11** in 8 categories | Mirrors the composition about a centre line. Holds well. |
| `top-down` | **5** in 4 categories | A concise way to request an overhead plan view. Add flat lay or no visible horizon when the angle matters. |
| `low angle` | **5** in 5 categories | Camera below eye level. Makes the subject loom. |
| `centred` | **5** in 4 categories | Subject on the axis. Useful when a layout keeps drifting. |
| `exploded` | **5** in 4 categories | Parts separated along their assembly axes. |
| `cutaway` | **5** in 4 categories | Section removed to show the inside. |
| `close-up` | **4** in 3 categories | Tight on the subject without the optical character of macro. |
| `flat lay` | **3** in 2 categories | Objects arranged on a plane, seen from above. More reliable than asking for the angle directly. |

## light

*what the light does, and where it comes from*

| term | entries | what it does |
|---|---|---|
| `raking light` | **27** in 14 categories | Light skimming across a surface at a shallow angle. The single best phrase in this catalog for making texture visible. |
| `overcast light` | **26** in 20 categories | Soft, sourceless, no hard shadow. Names what the light does rather than what makes it. |
| `backlit` | **22** in 13 categories | Source behind the subject. Edges glow, front goes dark. |
| `soft even light` | **18** in 7 categories | Flat and shadowless. What you want when the subject is the thing, not the mood. |
| `hard light` | **13** in 9 categories | Sharp-edged shadows, small source. |
| `silhouette` | **13** in 10 categories | Subject dark against a bright field. Removes surface detail on purpose. |
| `window light` ⚠️ | **10** in 9 categories | Creates soft directional daylight and may include the window. Use broad side light when you want only the effect. |
| `side light` | **9** in 6 categories | From one side. Modelling and shadow across the form. |
| `warm light` | **8** in 8 categories | Colour temperature as an instruction. Note that a colour word in a black-and-white prompt will fight it. |
| `directional light` | **7** in 6 categories | Says there is an axis without naming a fixture. |
| `fluorescent` ⚠️ | **7** in 7 categories | Creates cool, even overhead light. Mention ceiling tubes only when they belong in the composition. |
| `even light` | **6** in 5 categories | The shorter form. |
| `flat light` | **6** in 6 categories | Frontal, minimal modelling. |
| `light source` | **6** in 4 categories | Used to place the origin explicitly. |
| `long shadow` | **5** in 5 categories | Implies a low source without naming one. |
| `soft shadow` | **5** in 4 categories | Large source, diffuse edge. |
| `warm side` | **3** in 3 categories | Direction and temperature together. |
| `tungsten` | **3** in 2 categories | Creates a strong warm cast with an indoor evening feel. |
| `single light` | **3** in 3 categories | One source. Constrains the shadow story. |

## surface

*how the material reads up close*

| term | entries | what it does |
|---|---|---|
| `grain` | **25** in 15 categories | Film grain, wood grain or screenprint grain depending on the noun it sits next to. All three work. |
| `matte` | **14** in 8 categories | No specular highlight. |
| `polished` | **13** in 10 categories | Specular, reflective. Brings the surroundings into the surface. |
| `weathered` | **13** in 10 categories | Exposure damage, fading, oxidisation. |
| `seamless` ⚠️ | **11** in 5 categories | Creates a repeat-inspired surface motif. Use a tiling post-process when you need production-ready edges. |
| `worn` | **9** in 7 categories | Use damage: rubbed edges, thinned paint, softened corners. |
| `patina` | **6** in 6 categories | Aged metal specifically. |
| `frosted` | **6** in 5 categories | Diffusing, translucent rather than transparent. |

## process

*the physical medium being imitated*

| term | entries | what it does |
|---|---|---|
| `engraved` | **15** in 7 categories | Cut line, most reliable on metal and stone. |
| `letterpress` | **5** in 3 categories | Impression into the paper, ink sitting in the debossed area. |
| `watercolour` | **4** in 4 categories | Transparent washes, paper showing through. |
| `cyanotype` | **3** in 3 categories | Prussian blue, white line work. |
| `gouache` | **3** in 3 categories | Opaque water paint, visible brush loading. |
| `risograph` | **3** in 3 categories | Spot colour, misregistration, visible screen. |

## colour

*how the palette is constrained*

| term | entries | what it does |
|---|---|---|
| `palette` | **20** in 10 categories | The general handle. Almost always worth naming explicitly. |
| `muted` | **19** in 18 categories | Pulls saturation down across the frame. |
| `limited palette` ⚠️ | **8** in 4 categories | Restricts the palette. Name the exact hues for the clearest visual direction. |
| `high contrast` | **8** in 8 categories | Widens the tonal range, crushes the middle. |
| `monochrome` ⚠️ | **6** in 6 categories | Builds the image around one hue. Add grayscale or black-and-white when that is the intended treatment. |
| `muted palette` | **5** in 5 categories | The same, stated as a constraint on the whole palette. |
| `warm grey` | **5** in 5 categories | A named neutral. Neutrals drift unless you say which way. |
| `desaturated` | **4** in 4 categories | Stronger than muted. |

## Where each term is used

Entry ids, so you can pull the prompt and the image for any of them.

- **`macro`** (51): `abstract-002`, `abstract-003`, `automotive-008`, `brand-mark-003`, `brand-mark-005`, `collectible-002`, `collectible-007`, `fashion-002`, `fashion-006`, `food-006`, `glass-002`, `glass-004`, `jewellery-001`, `jewellery-002`, `jewellery-004`, `jewellery-006`, `jewellery-007`, `jewellery-008`, `macro-nature-001`, `macro-nature-002`, `macro-nature-003`, `macro-nature-004`, `macro-nature-005`, `mineral-001`, `mineral-002`, `mineral-004`, `mineral-005`, `mineral-006`, `mineral-007`, `miniature-004`, `miniature-008`, `monogram-002`, `photography-005`, `photography-015`, `photography-017`, `product-001`, `product-006`, `product-012`, `product-015`, `product-018`, `product-022`, `seasonal-008`, `stationery-005`, `tattoo-005`, `tool-004`, `tool-007`, `tool-008`, `typography-008`, `typography-013`, `typography-015`, `underwater-004`
- **`24mm`** (3): `interior-001`, `photography-003`, `photography-013`
- **`35mm`** (14): `automotive-007`, `exterior-003`, `fashion-009`, `food-007`, `interior-005`, `isometric-3d-005`, `landscape-010`, `photography-002`, `photography-007`, `photography-014`, `portrait-004`, `portrait-009`, `still-life-004`, `street-001`
- **`50mm`** (10): `animal-003`, `exterior-005`, `fashion-010`, `fashion-013`, `fashion-017`, `fashion-023`, `photography-004`, `portrait-005`, `product-011`, `street-005`
- **`85mm`** (6): `fashion-014`, `fashion-020`, `landscape-003`, `photography-001`, `portrait-001`, `product-013`
- **`shallow depth of field`** (13): `animal-001`, `collectible-002`, `collectible-005`, `fashion-002`, `food-006`, `jewellery-001`, `macro-nature-002`, `miniature-002`, `photography-001`, `portrait-001`, `stationery-002`, `typography-015`, `typography-022`
- **`shallow focus`** (18): `automotive-008`, `fantasy-007`, `fashion-005`, `food-010`, `glass-002`, `jewellery-003`, `jewellery-007`, `macro-nature-005`, `macro-nature-007`, `miniature-007`, `photography-017`, `plant-004`, `sculpture-002`, `tool-007`, `tool-008`, `typography-016`, `weather-002`, `weather-005`
- **`long lens`** (7): `crowd-001`, `fantasy-007`, `night-005`, `seasonal-007`, `street-008`, `vehicle-002`, `weather-003`
- **`long exposure`** (15): `automotive-005`, `exterior-006`, `interior-003`, `interior-009`, `landscape-004`, `night-001`, `night-003`, `night-004`, `night-006`, `period-005`, `period-008`, `photography-006`, `scifi-005`, `vehicle-004`, `weather-008`
- **`overhead`** (28): `automotive-001`, `fashion-001`, `fashion-019`, `food-002`, `food-010`, `interior-007`, `interior-009`, `isometric-3d-002`, `jewellery-004`, `mirror-007`, `packaging-003`, `photography-003`, `photography-009`, `photography-014`, `plant-007`, `portrait-009`, `product-007`, `product-010`, `product-013`, `scifi-005`, `sport-001`, `stationery-003`, `stationery-004`, `stationery-006`, `still-life-002`, `still-life-008`, `street-007`, `vehicle-009`
- **`straight down`** (17): `abstract-005`, `aerial-002`, `aerial-004`, `aerial-006`, `anatomy-008`, `food-004`, `knolling-003`, `knolling-005`, `knolling-006`, `knolling-007`, `knolling-008`, `mineral-008`, `pattern-004`, `plant-010`, `seasonal-002`, `seasonal-008`, `still-life-008`
- **`top-down`** (5): `fashion-006`, `food-010`, `packaging-004`, `product-003`, `product-016`
- **`flat lay`** (3): `product-003`, `product-010`, `stationery-003`
- **`low angle`** (5): `automotive-003`, `macro-nature-003`, `miniature-007`, `mirror-007`, `photography-002`
- **`three-quarter`** (22): `anatomy-006`, `architecture-001`, `architecture-003`, `automotive-001`, `brand-mark-006`, `collectible-006`, `fashion-013`, `fashion-017`, `fashion-027`, `isometric-3d-004`, `isometric-3d-008`, `landscape-008`, `miniature-003`, `packaging-003`, `portrait-007`, `poster-008`, `product-017`, `product-019`, `product-020`, `product-022`, `reference-sheet-001`, `scifi-002`
- **`close-up`** (4): `animal-007`, `fashion-004`, `fashion-022`, `typography-020`
- **`symmetrical`** (11): `coloring-page-003`, `exterior-004`, `food-008`, `interior-002`, `interior-006`, `interior-008`, `interior-013`, `photography-003`, `silhouette-001`, `still-life-003`, `street-006`
- **`centred`** (5): `brand-mark-001`, `infographic-006`, `poster-003`, `poster-005`, `ui-004`
- **`isometric`** (12): `infographic-010`, `isometric-3d-001`, `isometric-3d-002`, `isometric-3d-003`, `isometric-3d-004`, `isometric-3d-005`, `isometric-3d-006`, `isometric-3d-007`, `isometric-3d-008`, `isometric-3d-009`, `isometric-3d-010`, `pixel-art-003`
- **`exploded`** (5): `editing-008`, `isometric-3d-005`, `isometric-3d-009`, `product-005`, `technical-drawing-002`
- **`cutaway`** (5): `illustration-005`, `infographic-003`, `isometric-3d-002`, `isometric-3d-006`, `technical-drawing-005`
- **`raking light`** (27): `abstract-003`, `brand-mark-003`, `collectible-002`, `fashion-002`, `material-001`, `material-008`, `mineral-005`, `mineral-008`, `monogram-002`, `monogram-003`, `poster-007`, `product-011`, `sculpture-001`, `sculpture-004`, `stringcount-1`, `stringcount-2`, `stringcount-3`, `stringcount-4`, `stringcount-5`, `stringcount-6`, `stringcount-7`, `stringcount-8`, `tattoo-004`, `tool-007`, `typography-008`, `typography-015`, `typography-018`
- **`overcast light`** (26): `aerial-002`, `animal-004`, `automotive-007`, `crowd-008`, `fantasy-005`, `fashion-005`, `food-007`, `hangul-001`, `hangul-002`, `knolling-006`, `landscape-004`, `landscape-006`, `macro-nature-006`, `plant-008`, `plant-010`, `portrait-004`, `sculpture-002`, `sculpture-005`, `seasonal-006`, `sport-005`, `still-life-006`, `tool-005`, `typography-012`, `typography-023`, `vehicle-003`, `vehicle-006`
- **`soft even light`** (18): `abstract-006`, `fashion-001`, `knolling-008`, `objectcount-2`, `objectcount-3`, `objectcount-4`, `objectcount-5`, `objectcount-6`, `objectcount-7`, `objectcount-8`, `product-017`, `tool-006`, `weave-1`, `weave-2`, `weave-3`, `weave-5`, `weave-6`, `weave-7`
- **`even light`** (6): `anatomy-008`, `material-002`, `material-006`, `mineral-003`, `product-008`, `reference-sheet-001`
- **`flat light`** (6): `aerial-004`, `landscape-010`, `seasonal-008`, `sport-002`, `stationery-006`, `weather-002`
- **`hard light`** (13): `automotive-008`, `fashion-003`, `food-005`, `food-009`, `glass-001`, `glass-005`, `jewellery-005`, `mineral-002`, `mineral-006`, `portrait-002`, `product-016`, `still-life-004`, `still-life-007`
- **`side light`** (9): `animal-007`, `fashion-004`, `fashion-008`, `fashion-010`, `fashion-026`, `food-001`, `landscape-007`, `plant-001`, `typography-011`
- **`directional light`** (7): `jewellery-006`, `miniature-003`, `miniature-005`, `packaging-004`, `still-life-005`, `tattoo-006`, `tool-004`
- **`backlit`** (22): `abstract-001`, `abstract-002`, `abstract-007`, `animal-002`, `collectible-007`, `glass-002`, `glass-004`, `jewellery-004`, `macro-nature-002`, `macro-nature-007`, `macro-nature-008`, `material-005`, `mineral-004`, `mineral-007`, `photography-015`, `plant-006`, `plant-009`, `portrait-003`, `product-009`, `product-014`, `still-life-003`, `still-life-006`
- **`warm light`** (8): `fashion-021`, `miniature-004`, `mirror-003`, `portrait-007`, `poster-008`, `street-008`, `tool-002`, `weather-004`
- **`warm side`** (3): `sculpture-007`, `stationery-002`, `tool-001`
- **`window light`** (10): `collectible-005`, `fashion-014`, `fashion-022`, `interior-003`, `packaging-001`, `photography-004`, `plant-003`, `portrait-005`, `product-002`, `tattoo-002`
- **`fluorescent`** (7): `editing-002`, `hangul-004`, `illustration-006`, `night-003`, `photography-003`, `poster-006`, `typography-003`
- **`tungsten`** (3): `photography-010`, `photography-014`, `portrait-005`
- **`single light`** (3): `infographic-010`, `mineral-001`, `stationery-005`
- **`light source`** (6): `automotive-005`, `editing-002`, `night-004`, `night-007`, `photography-007`, `photography-010`
- **`long shadow`** (5): `editing-001`, `photography-009`, `scifi-004`, `sport-007`, `still-life-004`
- **`soft shadow`** (5): `fashion-015`, `infographic-002`, `infographic-010`, `product-022`, `still-life-008`
- **`silhouette`** (13): `animal-010`, `childrens-book-008`, `exterior-006`, `fashion-024`, `illustration-012`, `illustration-014`, `night-001`, `pattern-008`, `silhouette-003`, `silhouette-005`, `silhouette-007`, `still-life-006`, `street-008`
- **`matte`** (14): `brand-mark-006`, `collectible-001`, `fashion-017`, `fashion-021`, `isometric-3d-005`, `isometric-3d-007`, `isometric-3d-009`, `mineral-008`, `packaging-003`, `product-002`, `product-011`, `product-020`, `still-life-005`, `still-life-007`
- **`polished`** (13): `collectible-002`, `interior-004`, `interior-009`, `jewellery-001`, `mineral-003`, `mirror-007`, `monogram-002`, `pattern-004`, `photography-003`, `product-001`, `product-006`, `product-020`, `tool-001`
- **`grain`** (25): `brand-mark-003`, `childrens-book-008`, `comic-008`, `fashion-009`, `fashion-011`, `fashion-015`, `fashion-017`, `fashion-024`, `illustration-001`, `illustration-004`, `illustration-006`, `illustration-011`, `interior-011`, `material-001`, `mirror-007`, `pattern-006`, `period-007`, `period-008`, `photography-004`, `portrait-005`, `portrait-009`, `product-006`, `product-015`, `sculpture-007`, `tool-001`
- **`weathered`** (13): `brand-mark-005`, `exterior-004`, `fantasy-005`, `hangul-001`, `hangul-002`, `knolling-006`, `material-002`, `poster-007`, `sculpture-002`, `street-004`, `typography-011`, `typography-017`, `typography-023`
- **`worn`** (9): `brand-mark-007`, `fantasy-008`, `fashion-005`, `interior-001`, `product-013`, `scifi-001`, `tool-002`, `tool-005`, `tool-006`
- **`patina`** (6): `automotive-004`, `brand-mark-005`, `material-006`, `sculpture-002`, `still-life-002`, `typography-022`
- **`frosted`** (6): `animal-001`, `brand-mark-008`, `glass-003`, `illustration-010`, `product-004`, `product-019`
- **`seamless`** (11): `brand-mark-006`, `fashion-016`, `fashion-019`, `fashion-026`, `pattern-001`, `pattern-002`, `pattern-005`, `pattern-007`, `pattern-008`, `portrait-002`, `product-005`
- **`letterpress`** (5): `isometric-3d-007`, `stationery-001`, `stationery-005`, `typography-008`, `typography-018`
- **`engraved`** (15): `anatomy-001`, `brand-mark-005`, `monogram-002`, `poster-009`, `stringcount-1`, `stringcount-2`, `stringcount-3`, `stringcount-4`, `stringcount-5`, `stringcount-6`, `stringcount-7`, `stringcount-8`, `technical-drawing-004`, `typography-019`, `typography-022`
- **`cyanotype`** (3): `editing-008`, `illustration-012`, `pattern-008`
- **`gouache`** (3): `childrens-book-001`, `editing-003`, `illustration-002`
- **`watercolour`** (4): `anatomy-003`, `childrens-book-004`, `comic-007`, `illustration-005`
- **`risograph`** (3): `comic-008`, `illustration-006`, `poster-006`
- **`muted`** (19): `animal-009`, `childrens-book-004`, `exterior-005`, `fantasy-001`, `fashion-023`, `illustration-009`, `illustration-015`, `interior-008`, `jewellery-003`, `miniature-003`, `mirror-001`, `period-008`, `photography-001`, `portrait-007`, `poster-002`, `product-017`, `still-life-006`, `tattoo-007`, `vehicle-002`
- **`muted palette`** (5): `abstract-006`, `comic-007`, `fantasy-002`, `pixel-art-003`, `stationery-003`
- **`limited palette`** (8): `childrens-book-002`, `illustration-001`, `isometric-3d-004`, `pixel-art-001`, `pixel-art-004`, `pixel-art-005`, `pixel-art-007`, `pixel-art-008`
- **`palette`** (20): `editing-005`, `fashion-009`, `fashion-011`, `fashion-014`, `fashion-015`, `fashion-017`, `fashion-019`, `fashion-024`, `illustration-007`, `infographic-010`, `interior-008`, `interior-013`, `photography-001`, `photography-003`, `photography-006`, `photography-013`, `portrait-007`, `seasonal-004`, `still-life-008`, `weather-003`
- **`desaturated`** (4): `exterior-002`, `food-007`, `period-006`, `photography-003`
- **`monochrome`** (6): `animal-009`, `exterior-005`, `fashion-011`, `photography-011`, `scifi-002`, `still-life-006`
- **`high contrast`** (8): `fashion-006`, `jewellery-005`, `landscape-001`, `period-007`, `photography-002`, `plant-005`, `street-004`, `underwater-004`
- **`warm grey`** (5): `fashion-009`, `portrait-001`, `poster-003`, `product-010`, `seasonal-004`
