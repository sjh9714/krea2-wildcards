#!/usr/bin/env python3
"""Build focused search landing pages, sitemap, and robots directives."""

from __future__ import annotations

import html
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SITE = "https://sjh9714.github.io/krea2-wildcards/"
REPO = "https://github.com/sjh9714/krea2-wildcards"
CAMPAIGN = "utm_source=pages&utm_medium=website&utm_campaign=v1_2_launch"

CSS = """
:root{--bg:#f6f5f1;--fg:#171918;--mut:#606762;--line:#d7d6d0;--acc:#175c49;--card:#fff;--panel:#eae9e4}
@media(prefers-color-scheme:dark){:root{--bg:#101210;--fg:#e9ebe7;--mut:#969c97;--line:#30342f;--acc:#71cfad;--card:#191c19;--panel:#202420}}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo",Roboto,sans-serif}a{color:var(--acc)}
.wrap{max-width:1120px;margin:auto;padding:0 22px 90px}.topbar{display:flex;justify-content:space-between;gap:24px;align-items:center;padding:22px 0;border-bottom:1px solid var(--line)}.brand{font-weight:750;text-decoration:none;color:var(--fg)}.topbar nav{display:flex;gap:16px;flex-wrap:wrap}.topbar nav a{font-size:.86rem;text-decoration:none}.crumb{margin:44px 0 12px;color:var(--mut);font-size:.84rem}.hero{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(260px,.65fr);gap:60px;align-items:end;padding:0 0 54px;border-bottom:2px solid var(--fg)}h1{font-size:clamp(2.3rem,6vw,4.9rem);line-height:.98;letter-spacing:-.055em;margin:0;max-width:15ch}.lede{font-size:1.08rem;color:var(--mut);margin:22px 0 0;max-width:61ch}.heroaside{border-top:1px solid var(--fg);padding-top:16px}.eyebrow{font:700 12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;text-transform:uppercase;letter-spacing:.08em;color:var(--acc)}.metric{font-size:2.9rem;line-height:1;font-weight:760;margin:8px 0}.small{color:var(--mut);font-size:.9rem}.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}.button{display:inline-block;padding:10px 15px;border:1px solid var(--acc);font-size:.9rem;font-weight:700;text-decoration:none}.button.primary{background:var(--acc);color:var(--bg)}.button:hover{outline:2px solid color-mix(in srgb,var(--acc) 25%,transparent);outline-offset:2px}
main section{padding:58px 0;border-bottom:1px solid var(--line)}h2{font-size:clamp(1.7rem,3.2vw,2.55rem);line-height:1.08;letter-spacing:-.035em;margin:0 0 14px;max-width:22ch}h3{font-size:1.05rem;margin:0 0 8px}.sectionintro{max-width:66ch;color:var(--mut);margin:0 0 28px}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.step{background:var(--bg);padding:24px}.step b{display:block;color:var(--acc);font:700 12px ui-monospace,monospace;margin-bottom:12px}.step p{margin:0;color:var(--mut);font-size:.93rem}.formula{font:14px/1.7 ui-monospace,SFMono-Regular,Menlo,monospace;padding:22px;border-left:4px solid var(--acc);background:var(--panel);overflow-wrap:anywhere}.gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{margin:0;background:var(--card);border-top:3px solid var(--fg)}.card img{width:100%;aspect-ratio:1;object-fit:cover;display:block}.cardbody{padding:15px}.card h3{font-size:.94rem}.prompt{font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mut);display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}.copy{margin-top:12px;padding:6px 10px;border:1px solid var(--line);background:transparent;color:var(--fg);font:700 12px inherit;cursor:pointer}.copy:hover{border-color:var(--acc)}.recipes{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.recipe{padding:22px;border:1px solid var(--line);background:var(--card)}.recipe code{display:block;margin:10px 0;color:var(--acc);white-space:normal}.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.fact{border-top:2px solid var(--acc);padding-top:12px}.fact strong{display:block;font-size:1.4rem}.fact span{color:var(--mut);font-size:.86rem}.callout{background:var(--acc);color:var(--bg);padding:34px;display:grid;grid-template-columns:1fr auto;gap:30px;align-items:center}.callout h2{margin:0;max-width:20ch}.callout p{margin:10px 0 0;color:color-mix(in srgb,var(--bg) 82%,transparent)}.callout .button{border-color:var(--bg);color:var(--bg)}footer{padding-top:30px;color:var(--mut);font-size:.85rem;max-width:75ch}
@media(max-width:820px){.hero{grid-template-columns:1fr;gap:34px}.steps,.gallery{grid-template-columns:repeat(2,1fr)}.facts{grid-template-columns:repeat(2,1fr)}.callout{grid-template-columns:1fr}.recipes{grid-template-columns:1fr}}
@media(max-width:540px){.topbar{align-items:flex-start}.topbar nav{justify-content:flex-end}.steps,.gallery{grid-template-columns:1fr}h1{font-size:2.65rem}.wrap{padding-inline:16px}.hero{padding-bottom:40px}main section{padding:44px 0}.facts{gap:12px}.fact strong{font-size:1.15rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

PAGES = [
    {
        "slug": "comfyui-krea2-workflow",
        "title": "Krea 2 ComfyUI workflows you can drag in",
        "description": "Download a native Krea 2 Turbo ComfyUI workflow or a Dynamic Prompts wildcard version, both based on Comfy-Org's official template.",
        "eyebrow": "ComfyUI starter",
        "metric": "2 graphs",
        "metric_note": "Native paste mode and randomized wildcard mode",
        "categories": ["product", "fashion", "interior"],
        "formula": "prompt -> optional wildcard expansion -> official Krea 2 Turbo subgraph -> Save Image",
        "steps": [
            ("01", "Download the graph", "Use the JSON file, or drag the PNG example directly onto the ComfyUI canvas."),
            ("02", "Place three model files", "Put the official diffusion model, text encoder, and VAE in their matching ComfyUI model folders."),
            ("03", "Queue at eight steps", "The official Turbo subgraph already carries the sampler settings. Change the prompt, size, or seed."),
        ],
        "primary": ("Download native JSON", f"{REPO}/releases/latest/download/krea2-native-starter.json?{CAMPAIGN}&utm_content=workflow_native"),
        "secondary": ("Download wildcard JSON", f"{REPO}/releases/latest/download/krea2-wildcards-starter.json?{CAMPAIGN}&utm_content=workflow_wildcard"),
    },
    {
        "slug": "krea2-product-photography-prompts",
        "title": "Krea 2 product photography prompts with real outputs",
        "description": "Copy tested Krea 2 Turbo prompts for product photography, beauty packaging, studio light, materials, and commercial compositions.",
        "eyebrow": "Commercial image prompts",
        "metric": "Product",
        "metric_note": "Generated examples, prompt text, and reusable structure",
        "categories": ["product", "packaging"],
        "formula": "[one precise product] + [supporting surface] + [camera angle] + [light direction and hardness] + [background] + [material detail] + [text constraint]",
        "steps": [
            ("01", "Name one hero object", "Write the count, container type, material, and whether readable text should appear."),
            ("02", "Describe visible light", "Specify hard or soft light, its direction, and the shadow shape instead of naming studio equipment."),
            ("03", "Control the set", "Give the surface, backdrop, camera angle, and only the supporting objects that should remain in frame."),
        ],
    },
    {
        "slug": "krea2-editorial-fashion-prompts",
        "title": "Krea 2 fashion prompts for editorial images",
        "description": "Tested Krea 2 Turbo fashion prompts for campaigns, fabrics, runway compositions, editorial portraits, and controlled color palettes.",
        "eyebrow": "Fashion prompt guide",
        "metric": "Editorial",
        "metric_note": "Wardrobe, pose, crop, location, and light in a stable order",
        "categories": ["fashion"],
        "formula": "[garment and material] + [model action] + [crop and viewpoint] + [location] + [light behavior] + [editorial finish]",
        "steps": [
            ("01", "Lead with the garment", "Describe silhouette, construction, fabric behavior, and the exact color before the location."),
            ("02", "Use a simple action", "A clear stance or walk is easier to preserve than several simultaneous gestures."),
            ("03", "Finish with the frame", "Set the crop, viewpoint, background, contrast, and campaign or magazine treatment."),
        ],
    },
    {
        "slug": "krea2-interior-architecture-prompts",
        "title": "Krea 2 interior and architecture prompts",
        "description": "Copy Krea 2 Turbo prompts for interiors, materials, architectural exteriors, daylight, night scenes, and camera placement.",
        "eyebrow": "Spatial image prompts",
        "metric": "Space",
        "metric_note": "Explicit geometry, viewpoint, material, and light",
        "categories": ["interior", "architecture", "exterior"],
        "formula": "[space type] + [dominant geometry] + [camera position and lens character] + [three key materials] + [time and light direction] + [occupancy constraint]",
        "steps": [
            ("01", "Anchor the camera", "Say where the camera stands and whether the view is frontal, corner-to-corner, low, or elevated."),
            ("02", "Limit the material list", "Name the few surfaces that define the scene so finishes do not compete for attention."),
            ("03", "Describe daylight in space", "State the opening, direction, softness, and shadow length. Add people only when scale needs them."),
        ],
    },
    {
        "slug": "krea2-prompt-guide",
        "title": "How to write Krea 2 prompts that stay controllable",
        "description": "A practical Krea 2 Turbo prompt guide derived from hundreds of generated examples: order, text, light, style, counts, and constraints.",
        "eyebrow": "Prompt field guide",
        "metric": "499 runs",
        "metric_note": "Published prompts with matching generated images",
        "categories": ["typography", "objectcount", "photography", "illustration"],
        "formula": "[medium or image type] + [main subject] + [composition] + [visible light] + [materials and palette] + [exact text] + [one final constraint]",
        "steps": [
            ("01", "Write what can be seen", "Use concrete nouns, positions, surfaces, and light behavior before mood words."),
            ("02", "Write every visible string", "If text matters, include each word exactly. Do not ask the model to invent labels or titles."),
            ("03", "Change one variable", "When a result misses, alter the failing clause instead of stacking more adjectives onto the whole prompt."),
        ],
    },
    {
        "slug": "krea2-image-editing-recipes",
        "title": "Krea 2 image editing recipes for controlled changes",
        "description": "Positive Krea 2 image editing recipes for relighting, recoloring, medium conversion, cleanup, material changes, and composition-safe variations.",
        "eyebrow": "Image editing recipes",
        "metric": "12 recipes",
        "metric_note": "Describe the change, then state what must stay fixed",
        "categories": ["editing"],
        "formula": "[change only this property] + [specific target state] + [preserve these named elements] + [preserve framing and geometry]",
        "steps": [
            ("01", "Name one change", "Relight, recolor, restyle, replace a material, or remove one distraction per edit."),
            ("02", "State the target visibly", "Describe the new light direction, exact palette, surface response, or rendering medium."),
            ("03", "Lock the rest", "List the geometry, subject identity, crop, perspective, and edges that must remain unchanged."),
        ],
    },
]

EDIT_RECIPES = [
    ("Relight without moving the scene", "Replace the flat light with [direction, hardness, color]. Keep subject placement, camera, horizon, and framing identical."),
    ("Change the time of day", "Change only the time to [dawn, blue hour, night]. Preserve every building, opening, surface, and camera position."),
    ("Convert the rendering medium", "Re-render the whole image as [gouache, cyanotype, ink]. Keep every contour, object, and spacing unchanged."),
    ("Recolor a fixed design", "Recolor the image to [named palette]. Keep all outlines, field boundaries, typography, and layout unchanged."),
    ("Replace one material", "Change only [target surface] from [old material] to [new material]. Preserve its shape, seams, scale, and reflections elsewhere."),
    ("Remove one distraction", "Remove [single object]. Reconstruct the surface behind it consistently. Keep all other objects and the crop unchanged."),
    ("Add one grounded object", "Add [object] at [precise position], matching the scene perspective, contact shadow, and light direction. Change nothing else."),
    ("Clean a background", "Replace the background with [plain surface or setting]. Preserve the subject outline, pose, scale, and edge detail."),
    ("Seasonal variation", "Change only the environment to [season and weather]. Keep architecture, camera, path geometry, and main colors recognizable."),
    ("Commercial cleanup", "Remove dust, dents, fingerprints, and stray reflections from [product]. Preserve label geometry, material finish, and lighting direction."),
    ("Wardrobe recolor", "Change only the garment from [old color] to [new color]. Preserve fabric texture, folds, body, face, pose, and background."),
    ("Composition-safe variation", "Create a variation of surface detail and small props while keeping the main subject, silhouette, viewpoint, negative space, and crop fixed."),
]


def escape(value: object, quote: bool = False) -> str:
    return html.escape(str(value), quote=quote)


def event_url(url: str, content: str) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{CAMPAIGN}&utm_content={content}"


def cards(entries: list[dict], up: str = "../../") -> str:
    output = ['<div class="gallery">']
    for entry in entries[:9]:
        output.append(
            f'<article class="card"><img loading="lazy" src="{up}{escape(entry["image"], True)}" '
            f'alt="{escape(entry["title"], True)}"><div class="cardbody">'
            f'<h3>{escape(entry["title"])}</h3><div class="prompt">{escape(entry["prompt"])}</div>'
            f'<button class="copy" type="button" data-prompt="{escape(entry["prompt"], True)}">Copy prompt</button>'
            '</div></article>'
        )
    output.append('</div>')
    return "".join(output)


def json_ld(spec: dict, entries: list[dict], url: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": spec["title"],
        "description": spec["description"],
        "url": url,
        "isPartOf": {"@type": "WebSite", "name": "Krea 2 Wildcards", "url": SITE},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(entries),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "url": f"{SITE}?id={entry['id']}#prompt-{entry['id']}",
                    "name": entry["title"],
                }
                for index, entry in enumerate(entries, 1)
            ],
        },
    }
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def build_page(spec: dict, all_entries: list[dict]) -> str:
    entries = [entry for entry in all_entries if entry["category"] in spec["categories"]]
    canonical = f"{SITE}guides/{spec['slug']}/"
    primary = spec.get("primary") or (
        "Browse every matching prompt",
        f"{SITE}?category={spec['categories'][0]}&{CAMPAIGN}&utm_content={spec['slug']}_browse",
    )
    secondary = spec.get("secondary") or (
        "Download all wildcards",
        f"{REPO}/releases/latest/download/krea2-wildcards.zip?{CAMPAIGN}&utm_content={spec['slug']}_zip",
    )
    steps = "".join(
        f'<article class="step"><b>{escape(number)}</b><h3>{escape(title)}</h3><p>{escape(body)}</p></article>'
        for number, title, body in spec["steps"]
    )
    facts = [
        (str(len(entries)), "matching generated examples in the catalog"),
        (str(len(all_entries)), "prompts in the full catalog"),
        (str(len({e['category'] for e in all_entries})), "published categories"),
        ("2", "ComfyUI starter workflows"),
    ]
    fact_html = "".join(
        f'<div class="fact"><strong>{escape(value)}</strong><span>{escape(label)}</span></div>'
        for value, label in facts
    )
    recipe_html = ""
    if spec["slug"] == "krea2-image-editing-recipes":
        recipe_html = (
            '<section><h2>12 positive edit recipes</h2><p class="sectionintro">'
            'Each recipe asks for a visible target state and names the elements that should stay fixed. '
            'Replace the bracketed slots with details from your source image.</p><div class="recipes">'
            + "".join(
                f'<article class="recipe"><h3>{escape(name)}</h3><code>{escape(template)}</code></article>'
                for name, template in EDIT_RECIPES
            )
            + '</div></section>'
        )

    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(spec['title'])}</title>
<meta name="description" content="{escape(spec['description'], True)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website"><meta property="og:title" content="{escape(spec['title'], True)}">
<meta property="og:description" content="{escape(spec['description'], True)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}social-preview.webp"><meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(spec['title'], True)}"><meta name="twitter:description" content="{escape(spec['description'], True)}">
<meta name="twitter:image" content="{SITE}social-preview.webp"><script type="application/ld+json">{json_ld(spec, entries, canonical)}</script>
<style>{CSS}</style></head><body><div class="wrap">
<header class="topbar"><a class="brand" href="{SITE}">Krea 2 Wildcards</a><nav aria-label="Primary"><a href="{SITE}">Catalog</a><a href="{SITE}guides/comfyui-krea2-workflow/">Workflow</a><a href="{REPO}">GitHub</a></nav></header>
<div class="crumb"><a href="{SITE}">Catalog</a> / Guides / {escape(spec['eyebrow'])}</div>
<header class="hero"><div><p class="eyebrow">{escape(spec['eyebrow'])}</p><h1>{escape(spec['title'])}</h1><p class="lede">{escape(spec['description'])}</p><div class="actions"><a class="button primary" href="{primary[1]}">{escape(primary[0])}</a><a class="button" href="{secondary[1]}">{escape(secondary[0])}</a></div></div><aside class="heroaside"><div class="metric">{escape(spec['metric'])}</div><div class="small">{escape(spec['metric_note'])}</div></aside></header>
<main><section><h2>A repeatable prompt order</h2><p class="sectionintro">Start with the part that defines the image, then move from the large composition to visible surface detail. The order below is short enough to edit without losing track of the variable you changed.</p><div class="formula">{escape(spec['formula'])}</div></section>
<section><h2>Use it in three moves</h2><div class="steps">{steps}</div></section>
<section><h2>Generated examples, prompt included</h2><p class="sectionintro">These are catalog entries with the exact prompt and generated output kept together. Copy a prompt, then change one clause at a time.</p>{cards(entries)}</section>
{recipe_html}<section><h2>What is in the library</h2><div class="facts">{fact_html}</div></section>
<section><div class="callout"><div><h2>Take the prompts into your own workflow</h2><p>Download the wildcard pack, or use the starter graph to render a prompt in ComfyUI.</p></div><a class="button" href="{event_url(REPO, spec['slug'] + '_github')}">View the repository</a></div></section></main>
<footer>Prompts are MIT. Images are AI-generated Krea 2 output and are published with generation provenance in the repository. The workflows derive from Comfy-Org's official Krea 2 template.</footer>
</div><script>
document.addEventListener('click',function(event){{var button=event.target.closest('.copy');if(!button)return;var value=button.dataset.prompt;var done=function(){{var old=button.textContent;button.textContent='Copied';setTimeout(function(){{button.textContent=old}},1000)}};var fallback=function(){{var area=document.createElement('textarea');area.value=value;document.body.appendChild(area);area.select();var ok=false;try{{ok=document.execCommand('copy')}}catch(error){{ok=false}}area.remove();if(ok)done()}};if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(value).then(done,fallback);else fallback()}});
</script></body></html>'''


def main() -> int:
    manifest = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    entries = [entry for entry in manifest["entries"] if (HERE / entry["image"]).exists()]
    for spec in PAGES:
        output = HERE / "guides" / spec["slug"] / "index.html"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(build_page(spec, entries), encoding="utf-8")
        print(output.relative_to(HERE))

    urls = [SITE] + [f"{SITE}guides/{spec['slug']}/" for spec in PAGES]
    modified = manifest.get("updated", manifest.get("launched"))
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap.extend(f"  <url><loc>{url}</loc><lastmod>{modified}</lastmod></url>" for url in urls)
    sitemap.append('</urlset>')
    (HERE / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (HERE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
    print(f"sitemap.xml ({len(urls)} URLs)")
    print("robots.txt")

    editing = [entry for entry in entries if entry["category"] == "editing"]
    recipe_lines = [
        "# Krea 2 image editing recipes",
        "",
        "Use one visible change per pass, then name the parts of the source image that must stay fixed. "
        "The five generated edits below used strengths from 0.50 to 0.60, which is the tested starting "
        "range in this repository for relighting, recoloring, and medium conversion.",
        "",
        f"[Browse the illustrated editing guide]({SITE}guides/krea2-image-editing-recipes/)",
        "",
        "## 12 reusable recipes",
        "",
    ]
    for index, (name, template) in enumerate(EDIT_RECIPES, 1):
        recipe_lines.extend([f"### {index}. {name}", "", f"`{template}`", ""])
    recipe_lines.extend([
        "## Generated editing examples",
        "",
        "| Edit | Source | Strength | Result |",
        "|---|---|---:|---|",
    ])
    for entry in editing:
        recipe_lines.append(
            f"| {entry['title']} | [{entry['source']}](docs/gallery.md#{entry['source']}) | "
            f"{entry['strength']:.2f} | [{entry['id']}]({entry['image']}) |"
        )
    recipe_lines.extend([
        "",
        "## A compact edit order",
        "",
        "1. Name the part of the image that changes.",
        "2. Describe its target color, light, material, object, or medium in visible terms.",
        "3. Name the geometry, identity, camera, crop, and edges that remain fixed.",
        "4. Inspect the unchanged areas as carefully as the changed area before accepting the result.",
        "",
    ])
    (HERE / "EDITING_RECIPES.md").write_text("\n".join(recipe_lines), encoding="utf-8")
    print("EDITING_RECIPES.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
