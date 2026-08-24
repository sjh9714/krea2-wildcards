# Krea 2 image editing recipes

Use one visible change per pass, then name the parts of the source image that must stay fixed. The five generated edits below used strengths from 0.50 to 0.60, which is the tested starting range in this repository for relighting, recoloring, and medium conversion.

[Browse the illustrated editing guide](https://sjh9714.github.io/krea2-wildcards/guides/krea2-image-editing-recipes/)

## 12 reusable recipes

### 1. Relight without moving the scene

`Replace the flat light with [direction, hardness, color]. Keep subject placement, camera, horizon, and framing identical.`

### 2. Change the time of day

`Change only the time to [dawn, blue hour, night]. Preserve every building, opening, surface, and camera position.`

### 3. Convert the rendering medium

`Re-render the whole image as [gouache, cyanotype, ink]. Keep every contour, object, and spacing unchanged.`

### 4. Recolor a fixed design

`Recolor the image to [named palette]. Keep all outlines, field boundaries, typography, and layout unchanged.`

### 5. Replace one material

`Change only [target surface] from [old material] to [new material]. Preserve its shape, seams, scale, and reflections elsewhere.`

### 6. Remove one distraction

`Remove [single object]. Reconstruct the surface behind it consistently. Keep all other objects and the crop unchanged.`

### 7. Add one grounded object

`Add [object] at [precise position], matching the scene perspective, contact shadow, and light direction. Change nothing else.`

### 8. Clean a background

`Replace the background with [plain surface or setting]. Preserve the subject outline, pose, scale, and edge detail.`

### 9. Seasonal variation

`Change only the environment to [season and weather]. Keep architecture, camera, path geometry, and main colors recognizable.`

### 10. Commercial cleanup

`Remove dust, dents, fingerprints, and stray reflections from [product]. Preserve label geometry, material finish, and lighting direction.`

### 11. Wardrobe recolor

`Change only the garment from [old color] to [new color]. Preserve fabric texture, folds, body, face, pose, and background.`

### 12. Composition-safe variation

`Create a variation of surface detail and small props while keeping the main subject, silhouette, viewpoint, negative space, and crop fixed.`

## Generated editing examples

| Edit | Source | Strength | Result |
|---|---|---:|---|
| Relight this coastline | [photography-006](../gallery.md#photography-006) | 0.55 | [editing-001](../../images/editing-001.webp) |
| Keep this corridor's geometry and perspective exactly. Chang | [photography-003](../gallery.md#photography-003) | 0.50 | [editing-002](../../images/editing-002.webp) |
| Re-render these terraced fields as a gouache painting with v | [photography-009](../gallery.md#photography-009) | 0.60 | [editing-003](../../images/editing-003.webp) |
| Recolour this woodblock wave to a dusk palette, deep violet | [illustration-004](../gallery.md#illustration-004) | 0.55 | [editing-005](../../images/editing-005.webp) |
| Blueprint version of the exploded camera | [isometric-3d-005](../gallery.md#isometric-3d-005) | 0.60 | [editing-008](../../images/editing-008.webp) |

## A compact edit order

1. Name the part of the image that changes.
2. Describe its target color, light, material, object, or medium in visible terms.
3. Name the geometry, identity, camera, crop, and edges that remain fixed.
4. Inspect the unchanged areas as carefully as the changed area before accepting the result.
