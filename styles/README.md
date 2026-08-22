# Krea 2 whole-scene style recipes

[← back to the catalog](../README.md)

Eight tested style clauses from [the original Reddit thread](https://www.reddit.com/r/StableDiffusion/comments/1vco6ra/), each shown with the image it generated and ready to copy into a prompt or wildcard file.

## The rule

**Put the medium first and make it describe the whole scene. Then add the subject, composition, and details that belong to that medium.**

Same subject and seed, two ways to phrase the style. The first names a picture-book style; the second tells the model how the whole scene is drawn:

<img src="images/cafe/book-named.webp" width="330" alt="named: a picture book appears on the table">
<img src="images/cafe/book-rephrased.webp" width="330" alt="rephrased: the whole frame converts">

- named, `Children's picture book drawing, soft crayon and gouache, simple rounded shapes, gentle flat colour.`
- rephrased, `Drawn the way a children's picture book is drawn: soft crayon and gouache, simple rounded shapes, flat gentle colour.`

## Eight whole-scene clauses

One subject, seed `77220`, the clause is the only variable. Each is about 100 characters; they are plain English and carry nothing model-specific.

<img src="images/cafe/manga.webp" width="330" alt="Manga">

**Manga**, `The whole scene drawn as black-and-white manga: ink linework, screentone shading, no colour anywhere.`

<img src="images/cafe/storybook.webp" width="330" alt="Watercolour storybook">

**Watercolour storybook**, `The whole scene as a watercolour storybook illustration: soft washes, gentle linework, painted background.`

<img src="images/cafe/comicink.webp" width="330" alt="Comic book">

**Comic book**, `The whole scene as comic-book art: bold ink outlines, flat colour, halftone dots, drawn background.`

<img src="images/cafe/chibi.webp" width="330" alt="Chibi">

**Chibi**, `The whole scene drawn chibi: super-deformed proportions, huge head, tiny body, flat cel colour throughout.`

<img src="images/cafe/poster.webp" width="330" alt="Gouache travel poster">

**Gouache travel poster**, `The whole scene as a vintage gouache travel poster: flat opaque paint, simplified shapes, limited warm palette.`

<img src="images/cafe/retroanime.webp" width="330" alt="70s cel anime">

**70s cel anime**, `The whole scene as a 1970s cel anime frame: hand-painted cels, muted palette, film grain, painted background.`

<img src="images/cafe/popart.webp" width="330" alt="Pop art">

**Pop art**, `Printed the way pop art is printed: bold black outlines, flat primary colour, visible halftone dots.`

<img src="images/cafe/sixties.webp" width="330" alt="Mid-century cartoon">

**Mid-century cartoon**, `The whole scene as a 1960s limited-animation cartoon: angular flat shapes, off-register colour, painted backdrop.`

All eight, one per line, for a ComfyUI wildcard or dynamic-prompt node: [`wildcards/styles.txt`](../wildcards/styles.txt)

## A subject prompt that leaves room for style

Use this order:

`[whole-scene medium] + [subject and setting] + [composition] + [medium-specific detail]`

A clean base subject:

```
A young woman sitting at an outdoor cafe table, holding an iced drink near her face. She has long dark hair, a thin white summer top, and small hoop earrings. Composed as a waist-up view, directly facing the viewer, with the street behind her.
```

Three useful substitutions when moving from photography to illustration:

- `facing the camera` becomes `facing the viewer`
- `shallow depth of field` becomes `simplified background detail`
- lens and studio-light terms become mark-making, palette, paper, ink, paint, or print terms from the target medium

## More style recipes

The earlier sweep contributes 15 more reusable clauses in [`wildcards/styles-extra.txt`](../wildcards/styles-extra.txt). Its raw generation record remains in [`sweep.json`](sweep.json).

For a larger community style list, see [the wildcards thread](https://www.reddit.com/r/StableDiffusion/comments/1uzdj7o/krea_2_styles_wildcards_txt/).

The prompt text and source records used to build this page are kept in [`data.json`](data.json) and [`sweep.json`](sweep.json).
