#!/usr/bin/env python3
"""
build_pages.py, emit a single-file gallery for GitHub Pages from the manifest.

This stays deliberately small: one generated HTML file, no framework, no CDN,
and no separate build tool. It is served from the root of the default branch so
that the existing images/ directory remains reachable without duplication.

    python3 build_pages.py            # writes docs/index.html
"""

from __future__ import annotations

import argparse
import html

from build_vocabulary import load as load_vocab, mark, term_pattern
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

_V, _D = load_vocab()
VOCAB = term_pattern([x["t"] for x in _V["terms"]])

CSS = """
:root{--bg:#f6f5f1;--fg:#171918;--mut:#656b68;--line:#d9d8d2;--acc:#175c49;--card:#fff;--panel:#eeede8}
@media(prefers-color-scheme:dark){:root{--bg:#101210;--fg:#e9ebe7;--mut:#929892;--line:#30342f;--acc:#6dc9a8;--card:#191c19;--panel:#202420}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 96px}
header{border-bottom:2px solid var(--fg);padding:56px 0 20px;margin-bottom:36px}
h1{font-size:clamp(1.8rem,4vw,2.6rem);margin:0 0 10px;letter-spacing:-.02em}
.sub{color:var(--mut);max-width:60ch;margin:0}
.meta{margin-top:18px;font:13px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mut)}
.meta b{color:var(--fg)}
.actions{display:flex;flex-wrap:wrap;gap:9px;margin:20px 0 0}
.actions a{display:inline-block;padding:7px 11px;border:1px solid var(--line);border-radius:5px;text-decoration:none;font-size:.86rem;font-weight:600}
.actions a:first-child{background:var(--acc);border-color:var(--acc);color:var(--bg)}
.actions a:hover{border-color:var(--acc)}
.actions a:active,.cp:active,.fav:active,.select:active,.cardshare:active,.toolbtn:active,#favonly:active,#close:active,#closecompare:active{transform:translateY(1px)}
h2{font-size:1.35rem;margin:56px 0 6px;letter-spacing:-.01em;scroll-margin-top:12px}
/* Anchors on a page this tall are useless if the browser lands mid-image,
   and lazy-loaded figures above the target shift it as they resolve. The
   scroll margin keeps the heading clear of the viewport edge. */
h2 .top{float:right;font:11px ui-monospace,monospace;color:var(--mut);font-weight:400;text-decoration:none}
h2 .top:hover{text-decoration:underline}
h2:first-of-type{margin-top:0}
h2 .n{font:12px ui-monospace,monospace;color:var(--mut);margin-left:8px}
.cat-desc{color:var(--mut);margin:0 0 20px;max-width:70ch;font-size:.94rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:6px;overflow:hidden;transition:border-color .16s ease}
figure:hover{border-color:var(--acc)}
figure.selected{border-color:var(--acc);box-shadow:0 0 0 2px color-mix(in srgb,var(--acc) 28%,transparent)}
figure.linked{animation:linked 1.8s ease}
@keyframes linked{0%,35%{box-shadow:0 0 0 4px color-mix(in srgb,var(--acc) 55%,transparent)}100%{box-shadow:none}}
figure img{width:100%;display:block;aspect-ratio:1;object-fit:cover;background:var(--line)}
.zoom{display:block;width:100%;padding:0;border:0;background:none;cursor:zoom-in}
.zoom:focus-visible{outline:3px solid var(--acc);outline-offset:-3px}
figcaption{padding:12px 14px}
mark{background:#e8f0ec;color:inherit;padding:0 1px;border-radius:2px}
@media(prefers-color-scheme:dark){mark{background:#24413a}}
.t{font-weight:640;font-size:.93rem;margin-bottom:7px}
pre{margin:0;background:transparent;color:var(--mut);font:11.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;word-break:break-word;overflow:hidden;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3}
figure.open pre{display:block;-webkit-line-clamp:none}
.more{margin:6px 8px 0 0;padding:0;font:inherit;font-size:.78rem;cursor:pointer;border:0;background:none;color:var(--acc);text-decoration:underline}
.nojs .more{display:none}
.nojs pre{display:block;-webkit-line-clamp:none}
.seed{margin-top:8px;font:11px ui-monospace,monospace;color:var(--mut)}
a{color:var(--acc)}
footer{margin-top:72px;padding-top:22px;border-top:1px solid var(--line);color:var(--mut);font-size:.9rem;max-width:74ch}
.tools{position:sticky;top:0;z-index:5;display:grid;grid-template-columns:minmax(15rem,1fr) minmax(11rem,15rem) auto auto;gap:9px;align-items:center;margin:0 -8px 14px;padding:10px 8px;background:var(--bg);border-bottom:1px solid var(--line)}
.collection-tools{grid-column:1/-1;display:flex;flex-wrap:wrap;align-items:center;gap:7px;padding-top:2px}
.toolbtn,.import-label{min-height:34px;padding:6px 9px;font:inherit;font-size:.78rem;font-weight:600;line-height:1.2;cursor:pointer;border:1px solid var(--line);border-radius:5px;background:var(--card);color:inherit}
.toolbtn:hover,.import-label:hover{border-color:var(--acc)}
.toolbtn[aria-pressed=true]{color:var(--bg);background:var(--acc);border-color:var(--acc)}
.toolbtn:disabled{cursor:not-allowed;opacity:.42}
.import-label input{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}
#toolstatus{margin-left:auto;color:var(--mut);font-size:.78rem;min-height:1.2em}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
#q,#category,#favonly{min-height:42px;padding:8px 11px;font:inherit;border:1px solid var(--line);border-radius:5px;background:var(--card);color:inherit}
#q{width:100%}
#category{width:100%}
#favonly{cursor:pointer;font-weight:600;white-space:nowrap}
#favonly[aria-pressed=true]{color:var(--bg);background:var(--acc);border-color:var(--acc)}
#qn{color:var(--mut);font-size:.86rem;white-space:nowrap;text-align:right}
#empty{margin:70px auto;text-align:center;color:var(--mut)}
.cp{margin:8px 0 0;padding:4px 10px;font:inherit;font-size:.82rem;cursor:pointer;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--mut)}
.cp:hover{color:inherit;border-color:var(--acc)}
.cp.done{color:var(--acc);border-color:var(--acc)}
.fav{float:right;margin:8px 0 0;padding:4px 9px;font:inherit;font-size:.82rem;cursor:pointer;border:1px solid transparent;border-radius:5px;background:transparent;color:var(--mut)}
.fav:hover{color:inherit;border-color:var(--line)}
.fav[aria-pressed=true]{color:var(--acc);border-color:var(--acc);font-weight:650}
.select,.cardshare{float:right;margin:8px 5px 0 0;padding:4px 9px;font:inherit;font-size:.82rem;cursor:pointer;border:1px solid transparent;border-radius:5px;background:transparent;color:var(--mut)}
.select:hover,.cardshare:hover{color:inherit;border-color:var(--line)}
.select[aria-pressed=true]{color:var(--bg);background:var(--acc);border-color:var(--acc);font-weight:650}
h2 .cp{margin:0 0 0 10px;font-size:.72rem;font-weight:400}
.nojs .cp{display:none}
.nojs .fav,.nojs .select,.nojs .cardshare,.nojs #favonly,.nojs .collection-tools{display:none}
dialog{width:min(92vw,980px);padding:0;border:1px solid var(--line);border-radius:7px;background:var(--card);color:var(--fg);box-shadow:0 24px 80px #0008}
dialog::backdrop{background:#000b}
#viewer img{display:block;width:100%;max-height:82vh;object-fit:contain;background:#080908}
.viewerbar{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:10px 12px}
#viewtitle{margin:0;font-size:.9rem;color:var(--mut);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#close{padding:6px 10px;border:1px solid var(--line);border-radius:5px;background:transparent;color:inherit;cursor:pointer}
#compareviewer{width:min(94vw,1180px);max-height:90vh;overflow:auto;padding:18px}
.dialoghead{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:14px}
.dialoghead h2{margin:0;font-size:1.15rem}
#closecompare{padding:6px 10px;border:1px solid var(--line);border-radius:5px;background:transparent;color:inherit;cursor:pointer}
.comparegrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}
.comparecard{min-width:0;border:1px solid var(--line);border-radius:6px;overflow:hidden;background:var(--bg)}
.comparecard img{display:block;width:100%;aspect-ratio:1;object-fit:cover;background:var(--line)}
.comparebody{padding:10px 11px}
.comparebody h3{margin:0 0 6px;font-size:.9rem}
.comparebody p{margin:0;color:var(--mut);font:11px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
.comparNote{color:var(--mut);font-size:.82rem;margin:0 0 12px}
@media(max-width:760px){.tools{grid-template-columns:1fr 1fr;position:static}.find{grid-column:1/-1}#qn{text-align:left}.collection-tools{gap:6px}#toolstatus{width:100%;margin-left:0}.toolbtn,.import-label{flex:1 0 auto}.comparegrid{grid-template-columns:1fr 1fr}}
@media(max-width:460px){.comparegrid{grid-template-columns:1fr}}
"""


def credit(e: dict) -> str:
    """Attribution, rendered only when an entry did not come from this repo's own
    runs. Whoever wrote a prompt keeps their name on it and a link off it."""
    who = e.get("prompt_author")
    if not who:
        return ""
    link = e.get("prompt_author_link")
    s = (f' · prompt by <a href="{html.escape(link)}">{html.escape(who)}</a>'
         if link else f" · prompt by {html.escape(who)}")
    for u in e.get("source_links", []):
        s += f' · <a href="{html.escape(u)}">source</a>'
    if e.get("license"):
        s += f' · {html.escape(e["license"])}'
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default="prompts.json")
    ap.add_argument("--out", default="index.html")
    args = ap.parse_args()

    d = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    root = Path(args.manifest).parent
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Pages serves /docs AS THE SITE ROOT, so "../images/..." escapes the served
    # tree and every image 404s. Copy them in instead, 10 MB duplicated is the
    # price of a self-contained page that the Pages CDN can serve under load,
    # and it avoids leaning on raw.githubusercontent.com, which is rate-limited.
    # Served from the branch ROOT, not /docs. Pages treats the configured
    # directory as the site root, so a page in /docs cannot reach ../images and
    # every image 404s, the earlier fix was to copy the whole image set into
    # docs/, which duplicated 23 MB and would have been ~100 MB at the size this
    # catalog is heading for. Serving from the root makes images/ reachable as
    # it sits and deletes the duplicate entirely.
    up = ""

    kept = [e for e in d["entries"] if (root / e["image"]).exists()]
    model = d.get("model", "the model")
    repo = d.get("repo", "")
    repo_url = f"https://github.com/{repo}"
    site_url = f"https://{repo.split('/')[0]}.github.io/{repo.split('/')[-1]}/"
    release_zip = f"{repo_url}/releases/latest/download/krea2-wildcards.zip"
    title = f"{len(kept)} {model} prompts with images"
    description = (f"Browse {len(kept)} {model} prompts with generated examples. "
                   "Search, save favorites, copy prompts, or download ComfyUI wildcards.")

    L = ['<!doctype html><html lang="en" class=nojs><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         f"<title>{html.escape(title)}</title>",
         f'<meta name="description" content="{html.escape(description, quote=True)}">',
         f'<link rel="canonical" href="{site_url}">',
         '<meta property="og:type" content="website">',
         f'<meta property="og:title" content="{html.escape(title, quote=True)}">',
         f'<meta property="og:description" content="{html.escape(description, quote=True)}">',
         f'<meta property="og:url" content="{site_url}">',
         f'<meta property="og:image" content="{site_url}hero.webp">',
         f"<style>{CSS}</style></head><body><div class=wrap>"]

    L.append('<header id="top">')
    L.append(f"<h1>{len(kept)} {html.escape(model)} prompts</h1>")
    L.append('<p class=sub>Browse by category, save the ones you like, and copy any '
             'prompt. Every card includes the image it generated.</p>')
    L.append('<nav class=actions aria-label="Project actions">'
             f'<a href="{release_zip}">Download wildcards</a>'
             f'<a href="{repo_url}">Star on GitHub</a>'
             f'<a href="{repo_url}/subscription">Watch releases</a></nav>')
    L.append(f'<p class=meta><a href="{repo_url}">'
             f'github.com/{html.escape(repo)}</a></p>')
    L.append("</header>")

    by = {}
    for e in kept:
        by.setdefault(e["category"], []).append(e)
    L.append('<div class=tools>')
    L.append(f'<div class=find><label class=sr for=q>Search prompts</label>'
             f'<input id=q type=search placeholder="Search {len(kept)} prompts" '
             'aria-label="Search the prompts"></div>')
    L.append('<label class=sr for=category>Filter by category</label>'
             '<select id=category aria-label="Filter by category">'
             '<option value="">All categories</option>')
    for cat in by:
        L.append(f'<option value="{html.escape(cat, quote=True)}">{html.escape(cat)}</option>')
    L.append('</select><button id=favonly type=button aria-pressed=false>Saved only</button>'
             f'<span id=qn aria-live=polite>{len(kept)} prompts</span>')
    L.append('<div class=collection-tools aria-label="Saved and selection tools">'
             '<button class=toolbtn id=share type=button>Copy filter link</button>'
             '<button class=toolbtn id=exportsaved type=button>Export saved</button>'
             '<label class=import-label for=importsaved>Import saved'
             '<input id=importsaved type=file accept="application/json"></label>'
             '<button class=toolbtn id=selectvisible type=button>Select visible</button>'
             '<button class=toolbtn id=compareselected type=button disabled>Compare 0</button>'
             '<button class=toolbtn id=downloadselected type=button disabled>Download 0</button>'
             '<button class=toolbtn id=clearselection type=button disabled>Clear</button>'
             '<span id=toolstatus aria-live=polite></span></div></div>')
    for cat, items in by.items():
        L.append(f'<section class=category data-cat="{html.escape(cat, quote=True)}">')
        L.append(f'<h2 id="{html.escape(cat)}">{html.escape(cat)}'
                 f'<span class=n>{len(items)}</span>'
                 f'<button class="cp all" data-cat="{html.escape(cat, quote=True)}" '
                 f'aria-label="Copy all {len(items)} prompts in {html.escape(cat, quote=True)}">'
                 f'copy all {len(items)}</button>'
                 f'<a class=top href="#top" title="back to the category list">top</a></h2>')
        desc = (d.get("categories") or {}).get(cat)
        if desc:
            L.append(f"<p class=cat-desc>{html.escape(desc)}</p>")
        L.append("<div class=grid>")
        for e in items:
            params = e.get("params") or {}
            seed = params.get("seed")
            asset = params.get("generation_id")
            if seed is not None:
                provenance = f"seed {seed}"
            elif asset:
                ratio = params.get("aspect_ratio")
                ratio_s = f" · {html.escape(str(ratio))}" if ratio else ""
                provenance = (f'Krea asset <span title="{html.escape(str(asset), quote=True)}">'
                              f'{html.escape(str(asset)[:8])}</span>{ratio_s}')
            else:
                provenance = "generation recorded"
            extra = f' · from <code>{html.escape(e["source"])}</code> at strength {e.get("strength")}' if e.get("source") else ""
            # data-p carries the prompt as it was run. The <pre> shows the same
            # string with <mark> around the vocabulary terms; if the button ever
            # copied the rendered version the reader would paste markup.
            L.append(f'<figure data-id="{html.escape(e["id"], quote=True)}" '
                     f'id="prompt-{html.escape(e["id"], quote=True)}" '
                     f'data-cat="{html.escape(cat, quote=True)}">'
                     f'<button class=zoom type=button data-src="{up}{html.escape(e["image"], quote=True)}" '
                     f'data-title="{html.escape(e["title"], quote=True)}" '
                     f'aria-label="View full-size image for {html.escape(e["title"], quote=True)}">'
                     f'<img loading=lazy src="{up}{html.escape(e["image"])}" '
                     f'alt="{html.escape(e["title"])}"></button>'
                     f'<figcaption><div class=t>{html.escape(e["title"])}</div>'
                     f'<pre>{mark(e["prompt"], VOCAB)}</pre>'
                     f'<button class=cp data-p="{html.escape(e["prompt"], quote=True)}" '
                     f'aria-label="Copy the prompt for {html.escape(e["title"], quote=True)}">'
                     f'copy</button>'
                     f'<button class=more aria-expanded=false>show all</button>'
                     f'<button class=fav type=button aria-pressed=false '
                     f'aria-label="Save {html.escape(e["title"], quote=True)}">save</button>'
                     f'<button class=select type=button aria-pressed=false '
                     f'aria-label="Select {html.escape(e["title"], quote=True)} for comparison">select</button>'
                     f'<button class=cardshare type=button '
                     f'aria-label="Copy a link to {html.escape(e["title"], quote=True)}">link</button>'
                     f'<div class=seed>{provenance}{extra}{credit(e)}</div></figcaption></figure>')
        L.append("</div></section>")

    L.append('<p id=empty hidden>No prompts match these filters. Try another search or category.</p>')
    L.append('<dialog id=viewer aria-label="Full-size prompt image">'
             '<img id=viewimage alt="">'
             '<div class=viewerbar><p id=viewtitle></p>'
             '<button id=close type=button aria-label="Close image viewer">close</button>'
             '</div></dialog>')
    L.append('<dialog id=compareviewer aria-label="Compare selected prompts">'
             '<div class=dialoghead><h2>Compare selected prompts</h2>'
             '<button id=closecompare type=button aria-label="Close comparison">close</button></div>'
             '<p class=comparNote id=comparenote></p><div class=comparegrid id=comparegrid></div>'
             '</dialog>')

    L.append('<footer>Prompts are MIT. The images are AI-generated output from '
             f'{html.escape(model)}, presented as model output rather than as photographs or human '
             'artwork, and were produced by the repository owner under the Krea 2 Community '
             'License. Recorded seeds or Krea generation asset IDs are included in the repository. '
             'Images are re-encoded from PNG to WebP to keep the repository easy to clone.</footer>')
    # No framework, no CDN, no build step. The page has to keep working as a
    # plain file, so this is one inline script and it degrades by hiding itself:
    # a copy button that does nothing when the clipboard API is unavailable is
    # worse than no copy button.
    L.append("<script>")
    L.append("""
document.documentElement.classList.remove('nojs');
// Two ways to copy. navigator.clipboard is the right one and needs both a
// secure context and user activation; execCommand is deprecated but works on
// plain http, in older browsers, and anywhere the async path is refused. The
// button is only hidden when neither exists, because a button that silently
// does nothing is worse than no button.
function fallbackCopy(text) {
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.setAttribute('readonly', '');
  ta.style.cssText = 'position:fixed;top:0;left:-9999px';
  document.body.appendChild(ta);
  ta.select();
  var ok = false;
  try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
  document.body.removeChild(ta);
  return ok;
}
function flash(b) {
  var was = b.textContent;
  b.textContent = 'copied';
  b.classList.add('done');
  setTimeout(function () { b.textContent = was; b.classList.remove('done'); }, 1200);
}
if (!navigator.clipboard && !document.queryCommandSupported) {
  document.documentElement.classList.add('nojs');
} else {
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('.cp');
    if (!b) return;
    var text;
    if (b.dataset.cat) {
      var grid = b.closest('.category').querySelector('.grid');
      text = Array.prototype.map.call(grid.querySelectorAll('.cp[data-p]'),
        function (x) { return x.dataset.p; }).join('\\n');
    } else {
      text = b.dataset.p;
    }
    var done = false;
    if (navigator.clipboard && window.isSecureContext) {
      // Resolve the label optimistically only if the write actually lands, but
      // do not leave the reader staring at a dead button if it hangs: the
      // async path stays pending forever in an unfocused document.
      var settled = false;
      navigator.clipboard.writeText(text).then(
        function () { settled = true; flash(b); },
        function () { if (!settled && fallbackCopy(text)) { settled = true; flash(b); } });
      setTimeout(function () {
        if (!settled && fallbackCopy(text)) { settled = true; flash(b); }
      }, 400);
      done = true;
    }
    if (!done && fallbackCopy(text)) flash(b);
  });
}
document.addEventListener('click', function (ev) {
  var m = ev.target.closest('.more');
  if (!m) return;
  var fig = m.closest('figure');
  var open = fig.classList.toggle('open');
  m.textContent = open ? 'show less' : 'show all';
  m.setAttribute('aria-expanded', open ? 'true' : 'false');
});
// A three-line clamp on a prompt that fits in three lines leaves a button that
// does nothing, so drop it where there is nothing to expand.
document.querySelectorAll('figure .more').forEach(function (m) {
  var pre = m.closest('figcaption').querySelector('pre');
  if (pre.scrollHeight <= pre.clientHeight + 2) m.remove();
});
var q = document.getElementById('q');
var category = document.getElementById('category');
var favonly = document.getElementById('favonly');
var qn = document.getElementById('qn');
var empty = document.getElementById('empty');
var toolstatus = document.getElementById('toolstatus');
var figs = Array.prototype.map.call(document.querySelectorAll('figure'), function (f) {
  return {
    el: f,
    id: f.dataset.id,
    cat: f.dataset.cat,
    title: f.querySelector('.t').textContent,
    prompt: f.querySelector('.cp[data-p]').dataset.p,
    src: f.querySelector('.zoom').dataset.src,
    hay: f.textContent.toLowerCase()
  };
});
var storageKey = 'krea2-favorites';
var saved = new Set();
var selectedIds = new Set();
try {
  saved = new Set(JSON.parse(localStorage.getItem(storageKey) || '[]'));
} catch (e) {
  saved = new Set();
}
var initialState = new URLSearchParams(location.search);
if (initialState.has('q')) q.value = initialState.get('q');
if (initialState.has('category')) category.value = initialState.get('category');
if (initialState.get('saved') === '1') favonly.setAttribute('aria-pressed', 'true');
function storeSaved() {
  try { localStorage.setItem(storageKey, JSON.stringify(Array.from(saved))); } catch (e) {}
}
function setStatus(text) {
  toolstatus.textContent = text;
  clearTimeout(setStatus.timer);
  setStatus.timer = setTimeout(function () { toolstatus.textContent = ''; }, 3200);
}
function paintFavorite(fig) {
  var b = fig.querySelector('.fav');
  var on = saved.has(fig.dataset.id);
  var title = fig.querySelector('.t').textContent;
  b.setAttribute('aria-pressed', on ? 'true' : 'false');
  b.setAttribute('aria-label', (on ? 'Remove saved ' : 'Save ') + title);
  b.textContent = on ? 'saved' : 'save';
}
function syncUrl() {
  if (!history.replaceState) return;
  var u = new URL(location.href);
  if (q.value.trim()) u.searchParams.set('q', q.value.trim());
  else u.searchParams.delete('q');
  if (category.value) u.searchParams.set('category', category.value);
  else u.searchParams.delete('category');
  if (favonly.getAttribute('aria-pressed') === 'true') u.searchParams.set('saved', '1');
  else u.searchParams.delete('saved');
  history.replaceState(null, '', u.pathname + u.search + u.hash);
}
function applyFilters() {
  var s = q.value.trim().toLowerCase();
  var selected = category.value;
  var onlySaved = favonly.getAttribute('aria-pressed') === 'true';
  var shown = 0;
  figs.forEach(function (f) {
    var hit = (!s || f.hay.indexOf(s) !== -1)
      && (!selected || f.cat === selected)
      && (!onlySaved || saved.has(f.id));
    f.el.style.display = hit ? '' : 'none';
    if (hit) shown++;
  });
  document.querySelectorAll('.category').forEach(function (section) {
    var any = Array.prototype.some.call(section.querySelectorAll('figure'),
      function (f) { return f.style.display !== 'none'; });
    section.style.display = any ? '' : 'none';
  });
  qn.textContent = shown === figs.length ? shown + ' prompts' : shown + ' of ' + figs.length;
  empty.hidden = shown !== 0;
  syncUrl();
}
figs.forEach(function (f) { paintFavorite(f.el); });
q.addEventListener('input', applyFilters);
category.addEventListener('change', applyFilters);
favonly.addEventListener('click', function () {
  var on = favonly.getAttribute('aria-pressed') === 'true';
  favonly.setAttribute('aria-pressed', on ? 'false' : 'true');
  applyFilters();
});
document.addEventListener('click', function (ev) {
  var b = ev.target.closest('.fav');
  if (!b) return;
  var fig = b.closest('figure'), id = fig.dataset.id;
  if (saved.has(id)) saved.delete(id); else saved.add(id);
  storeSaved();
  paintFavorite(fig);
  applyFilters();
});
function downloadText(name, text, type) {
  var blob = new Blob([text], {type: type || 'text/plain;charset=utf-8'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(function () { URL.revokeObjectURL(url); }, 0);
}
function copyWithFeedback(b, text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(function () { flash(b); }, function () {
      if (fallbackCopy(text)) flash(b);
    });
  } else if (fallbackCopy(text)) {
    flash(b);
  }
}
document.getElementById('share').addEventListener('click', function () {
  copyWithFeedback(this, location.href);
});
document.getElementById('exportsaved').addEventListener('click', function () {
  var payload = {
    format: 'krea2-wildcards-favorites',
    version: 1,
    exported_at: new Date().toISOString(),
    saved: Array.from(saved)
  };
  downloadText('krea2-favorites.json', JSON.stringify(payload, null, 2) + '\\n',
    'application/json;charset=utf-8');
  setStatus('Exported ' + saved.size + ' saved prompts');
});
document.getElementById('importsaved').addEventListener('change', function () {
  var input = this, file = input.files && input.files[0];
  if (!file) return;
  file.text().then(function (raw) {
    var parsed = JSON.parse(raw);
    var ids = Array.isArray(parsed) ? parsed : parsed.saved;
    if (!Array.isArray(ids)) throw new Error('missing saved list');
    var known = new Set(figs.map(function (f) { return f.id; }));
    var valid = ids.filter(function (id) { return typeof id === 'string' && known.has(id); });
    valid.forEach(function (id) { saved.add(id); });
    storeSaved();
    figs.forEach(function (f) { paintFavorite(f.el); });
    applyFilters();
    setStatus('Imported ' + valid.length + ' saved prompts');
  }).catch(function () {
    setStatus('Import needs a favorites JSON file');
  }).finally(function () { input.value = ''; });
});
function paintSelection(f) {
  var b = f.el.querySelector('.select');
  var on = selectedIds.has(f.id);
  f.el.classList.toggle('selected', on);
  b.setAttribute('aria-pressed', on ? 'true' : 'false');
  b.setAttribute('aria-label', (on ? 'Remove ' : 'Select ') + f.title + ' for comparison');
  b.textContent = on ? 'selected' : 'select';
}
function updateSelectionTools() {
  var n = selectedIds.size;
  var compare = document.getElementById('compareselected');
  var down = document.getElementById('downloadselected');
  var clear = document.getElementById('clearselection');
  compare.disabled = n < 2;
  down.disabled = n === 0;
  clear.disabled = n === 0;
  compare.textContent = 'Compare ' + n;
  down.textContent = 'Download ' + n;
}
document.addEventListener('click', function (ev) {
  var b = ev.target.closest('.select');
  if (!b) return;
  var f = figs.find(function (item) { return item.el === b.closest('figure'); });
  if (selectedIds.has(f.id)) selectedIds.delete(f.id); else selectedIds.add(f.id);
  paintSelection(f);
  updateSelectionTools();
});
document.getElementById('selectvisible').addEventListener('click', function () {
  var visible = figs.filter(function (f) { return f.el.style.display !== 'none'; });
  var remove = visible.length && visible.every(function (f) { return selectedIds.has(f.id); });
  visible.forEach(function (f) { if (remove) selectedIds.delete(f.id); else selectedIds.add(f.id); paintSelection(f); });
  updateSelectionTools();
  setStatus((remove ? 'Cleared ' : 'Selected ') + visible.length + ' visible prompts');
});
document.getElementById('clearselection').addEventListener('click', function () {
  selectedIds.clear();
  figs.forEach(paintSelection);
  updateSelectionTools();
});
document.getElementById('downloadselected').addEventListener('click', function () {
  var chosen = figs.filter(function (f) { return selectedIds.has(f.id); });
  downloadText('krea2-selected-prompts.txt', chosen.map(function (f) { return f.prompt; }).join('\\n') + '\\n');
  setStatus('Downloaded ' + chosen.length + ' prompts');
});
document.addEventListener('click', function (ev) {
  var b = ev.target.closest('.cardshare');
  if (!b) return;
  var id = b.closest('figure').dataset.id;
  var u = new URL(location.href);
  u.search = '';
  u.searchParams.set('id', id);
  u.hash = 'prompt-' + id;
  copyWithFeedback(b, u.href);
});
var compareviewer = document.getElementById('compareviewer');
var comparegrid = document.getElementById('comparegrid');
document.getElementById('compareselected').addEventListener('click', function () {
  var chosen = figs.filter(function (f) { return selectedIds.has(f.id); });
  comparegrid.replaceChildren();
  chosen.slice(0, 4).forEach(function (f) {
    var card = document.createElement('article');
    card.className = 'comparecard';
    var img = document.createElement('img');
    img.src = f.src; img.alt = f.title; img.loading = 'lazy';
    var body = document.createElement('div'); body.className = 'comparebody';
    var h = document.createElement('h3'); h.textContent = f.title;
    var p = document.createElement('p'); p.textContent = f.prompt;
    body.append(h, p); card.append(img, body); comparegrid.append(card);
  });
  document.getElementById('comparenote').textContent = chosen.length > 4
    ? 'Showing the first 4 of ' + chosen.length + ' selected prompts. The download keeps all of them.'
    : 'Compare composition, light, material, and wording side by side.';
  if (compareviewer.showModal) compareviewer.showModal(); else compareviewer.setAttribute('open', '');
});
document.getElementById('closecompare').addEventListener('click', function () { compareviewer.close(); });
compareviewer.addEventListener('click', function (ev) { if (ev.target === compareviewer) compareviewer.close(); });
var viewer = document.getElementById('viewer');
var viewimage = document.getElementById('viewimage');
var viewtitle = document.getElementById('viewtitle');
document.addEventListener('click', function (ev) {
  var b = ev.target.closest('.zoom');
  if (!b) return;
  viewimage.src = b.dataset.src;
  viewimage.alt = b.dataset.title;
  viewtitle.textContent = b.dataset.title;
  if (viewer.showModal) viewer.showModal(); else viewer.setAttribute('open', '');
});
document.getElementById('close').addEventListener('click', function () { viewer.close(); });
viewer.addEventListener('click', function (ev) { if (ev.target === viewer) viewer.close(); });
figs.forEach(paintSelection);
updateSelectionTools();
applyFilters();
var linkedId = initialState.get('id');
if (linkedId) {
  var linked = figs.find(function (f) { return f.id === linkedId; });
  if (linked) requestAnimationFrame(function () {
    linked.el.classList.add('linked');
    linked.el.scrollIntoView({behavior: 'smooth', block: 'center'});
  });
}
""")
    L.append("</script>")
    L.append("</div></body></html>")

    out.write_text("\n".join(L), encoding="utf-8")
    kb = out.stat().st_size // 1024
    print(f"wrote {out} ({kb} KB, {len(kept)} entries)")
    print("\nEnable Pages: Settings -> Pages -> Deploy from branch -> main / (root)")
    print(f"Then the page is https://<owner>.github.io/{repo.split('/')[-1]}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
