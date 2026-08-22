# Templates

Slot-and-fill recipes, the way a reader actually reuses a catalog. Every one of them is here because something in this repository measured it, and each names that evidence. Nothing was turned into a template because it looked like it would generalise.

*A template is a shape, not a guarantee. The evidence column says what was tested and how widely; a recipe measured on one subject at one seed is an observation, not a rate.*

6 of them. Every prompt in the catalog is a finished sentence; these are the shapes underneath the ones that were tested.

## 1. Convert the whole frame to a drawn medium

```text
[medium] of [subject]
```

| slot | what goes in it |
|---|---|
| `[medium]` | hand-drawn black and white manga · a watercolour storybook illustration · a mosaic fresco |
| `[subject]` | what is in the picture, with no lens, focus, camera or lighting words in it |

Leading with the medium and keeping the subject vocabulary consistent applies one visual language across the subject and background.

**Related guide** [the styles page](styles/README.md)
 · **ready-made** [`wildcards/styles.txt`](wildcards/styles.txt)

---

## 2. Make a texture visible

```text
[subject], raking light across [the surface]
```

| slot | what goes in it |
|---|---|
| `[the surface]` | the thing whose texture you want: the plaster, the fabric, the solder joint |

Light skimming at a shallow angle is the most reused lighting phrase in this catalog.

**Related guide** [`raking light`](VOCABULARY.md)

---

## 3. Ask for light without summoning the fixture

```text
[subject], [what the light does], never [the name of the lamp]
```

| slot | what goes in it |
|---|---|
| `[what the light does]` | soft even light · hard light from frame right · overcast light |
| `[the name of the lamp]` | softbox, ring light, window |

Describing the visible light effect gives you direct control over direction, softness, colour, and contrast.

**Related guide** [prompt field guide](FINDINGS.md)

---

## 4. Change the medium of an image you already have

```text
Re-render this [subject] as [medium]: [what the medium looks like]
```

| slot | what goes in it |
|---|---|
| `[medium]` | a gouache painting · a cyanotype blueprint |
| `[what the medium looks like]` | visible brush loading, paper tooth, no photographic grain |

Image-to-image at strength 0.50 to 0.60 is a useful starting range for changing the rendering medium while preserving the composition.

**Related guide** [prompt field guide](FINDINGS.md)

---

## 5. Put text in the image

```text
[subject] reading exactly "[the string]"
```

| slot | what goes in it |
|---|---|
| `[the string]` | every character you want, written out exactly |

Writing every visible string gives posters, packaging, signs, and interfaces a clear typographic target.

**Related guide** [prompt field guide](FINDINGS.md)

---

## 6. Constrain the palette

```text
[subject], limited palette: [name each colour]
```

| slot | what goes in it |
|---|---|
| `[name each colour]` | ink black, bone white, and ochre |

Naming each hue directly creates a clearer palette instruction than describing the palette only by size.

**Related guide** [prompt field guide](FINDINGS.md)

---

## How to extend these

Start with the template closest to your use case. Change the subject first, then the setting, and then one visual slot such as lighting or medium. Save each useful version so you can compare the effect of one change at a time.
