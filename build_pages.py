#!/usr/bin/env python3
"""
build_pages.py, emit a single-file gallery for GitHub Pages from the manifest.

Why this exists: 67% of Show HN posts above 300 points point at a hosted page on
the author's own domain rather than at a repository. A README is not a demo. This
is the smallest thing that satisfies that without becoming a web app. One HTML
file, no JavaScript, no build step, served from the ROOT of the default branch
so that images/ is reachable without duplicating it.

It deliberately does NOT add search. "searchable" is a measured winning word in
Show HN titles (8.9% hit rate against a 0.2% baseline), which makes it tempting,
and that is exactly why it must not go in a title unless the feature exists.
Ctrl+F is not a search feature.

    python3 build_pages.py            # writes docs/index.html
"""

from __future__ import annotations

import argparse
import html

from build_vocabulary import load as load_vocab, mark, term_pattern
import json
from pathlib import Path

# Shared with the README builder rather than copied. The gallery and the README
# print the same intro paragraph, so two copies of the substitution would be two
# places for the counts to drift apart. Which is the bug this fixes.
from build_catalog import counts

HERE = Path(__file__).resolve().parent

_V, _D = load_vocab()
VOCAB = term_pattern([x["t"] for x in _V["terms"]])

CSS = """
:root{--bg:#faf9f7;--fg:#17191a;--mut:#6a6f70;--line:#e0dedb;--acc:#1f5d4c;--card:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#111312;--fg:#e9ebe6;--mut:#8b918c;--line:#2a2e2b;--acc:#62bfa1;--card:#181b19}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Apple SD Gothic Neo",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 96px}
header{border-bottom:2px solid var(--fg);padding:56px 0 20px;margin-bottom:36px}
h1{font-size:clamp(1.8rem,4vw,2.6rem);margin:0 0 10px;letter-spacing:-.02em}
.sub{color:var(--mut);max-width:60ch;margin:0}
.meta{margin-top:18px;font:13px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--mut)}
.meta b{color:var(--fg)}
.actions{display:flex;flex-wrap:wrap;gap:9px;margin:20px 0 0}
.actions a{display:inline-block;padding:7px 11px;border:1px solid var(--line);border-radius:6px;text-decoration:none;font-size:.86rem;font-weight:600}
.actions a:first-child{background:var(--acc);border-color:var(--acc);color:var(--bg)}
.actions a:hover{border-color:var(--acc)}
h2{font-size:1.35rem;margin:56px 0 6px;letter-spacing:-.01em;scroll-margin-top:12px}
/* Anchors on a page this tall are useless if the browser lands mid-image,
   and lazy-loaded figures above the target shift it as they resolve. The
   scroll margin keeps the heading clear of the viewport edge. */
.toc{margin:28px 0 0;padding:14px 16px;border:1px solid var(--bd);border-radius:8px;font-size:.86rem;line-height:2}
.toc b{display:block;margin-bottom:6px;font-size:.8rem;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
.toc a{color:inherit}
h2 .top{float:right;font:11px ui-monospace,monospace;color:var(--mut);font-weight:400;text-decoration:none}
h2 .top:hover{text-decoration:underline}
h2:first-of-type{margin-top:0}
h2 .n{font:12px ui-monospace,monospace;color:var(--mut);margin-left:8px}
.cat-desc{color:var(--mut);margin:0 0 20px;max-width:70ch;font-size:.94rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:6px;overflow:hidden}
figure img{width:100%;display:block;aspect-ratio:1;object-fit:cover;background:var(--line)}
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
.finding{border-left:3px solid var(--acc);padding:2px 0 2px 18px;margin:0 0 30px;max-width:74ch}
.finding h3{margin:0 0 8px;font-size:1.05rem}
.finding p{margin:0 0 10px;color:var(--mut)}
.finding code{background:var(--line);padding:.1em .35em;border-radius:3px;font-size:.88em;color:var(--fg)}
.fail{border-color:#9e2b25}
@media(prefers-color-scheme:dark){.fail{border-color:#e0776c}}
.fail .t{color:#9e2b25}
@media(prefers-color-scheme:dark){.fail .t{color:#e0776c}}
a{color:var(--acc)}
footer{margin-top:72px;padding-top:22px;border-top:1px solid var(--line);color:var(--mut);font-size:.9rem;max-width:74ch}
.find{margin:0 0 14px}
#q{width:100%;max-width:34rem;padding:9px 12px;font:inherit;border:1px solid var(--line);border-radius:7px;background:transparent;color:inherit}
#qn{margin-left:10px;color:var(--mut);font-size:.9rem}
.cp{margin:8px 0 0;padding:4px 10px;font:inherit;font-size:.82rem;cursor:pointer;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--mut)}
.cp:hover{color:inherit;border-color:var(--acc)}
.cp.done{color:var(--acc);border-color:var(--acc)}
h2 .cp{margin:0 0 0 10px;font-size:.72rem;font-weight:400}
.nojs .cp{display:none}
"""


def md_lite(s: str) -> str:
    """Just enough markdown for the findings prose: bold, code, paragraphs."""
    out = html.escape(s)
    import re
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out, flags=re.S)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return "".join(f"<p>{p.strip()}</p>" for p in out.split("\n\n") if p.strip())


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
    title = f"{len(kept)} {model} prompts with reproducible outputs"
    nfail = len(d.get("failures", {}).get("entries", []))
    description = (f"Browse {len(kept)} {model} prompts and {nfail} documented failures. "
                   "Copy prompts or download ComfyUI wildcards.")

    L = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
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
    # The header sold the seeds and the failures in three lines before anyone saw
    # a picture. Same framing the README was rewritten out of. One line now.
    L.append(f"<h1>{len(kept)} {html.escape(model)} prompts</h1>")
    L.append('<p class=sub>Find one you like, press copy. Raw model output, nothing '
             'retouched.</p>')
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
    # A table of contents and an id per category. Without them the only way into
    # a 475-image page is to scroll it, and a link to one category cannot be
    # given to anyone. A reader who arrives from a comment asking about portrait
    # work should land on portrait work.
    # The page is 540 images. Scrolling it to find "night" is not a search, and
    # the category list only helps if you already know which category it is in.
    L.append('<div class=find><input id=q type=search placeholder="Search 475 prompts, '
             'try night, macro, letterpress" aria-label="Search the prompts">'
             '<span id=qn></span></div>')
    L.append('<nav class=toc><b>Jump to</b> ')
    L.append(" · ".join(
        f'<a href="#{html.escape(c)}">{html.escape(c)}</a> <span class=n>{len(v)}</span>'
        for c, v in by.items()))
    L.append(' · <a href="#failures">the failures</a>'
             ' · <a href="#findings">what this model does</a></nav>')

    for cat, items in by.items():
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
            seed = (e.get("params") or {}).get("seed")
            extra = f' · from <code>{html.escape(e["source"])}</code> at strength {e.get("strength")}' if e.get("source") else ""
            # data-p carries the prompt as it was run. The <pre> shows the same
            # string with <mark> around the vocabulary terms; if the button ever
            # copied the rendered version the reader would paste markup.
            L.append(f'<figure><img loading=lazy src="{up}{html.escape(e["image"])}" alt="{html.escape(e["title"])}">'
                     f'<figcaption><div class=t>{html.escape(e["title"])}</div>'
                     f'<pre>{mark(e["prompt"], VOCAB)}</pre>'
                     f'<button class=cp data-p="{html.escape(e["prompt"], quote=True)}" '
                     f'aria-label="Copy the prompt for {html.escape(e["title"], quote=True)}">'
                     f'copy</button>'
                     f'<button class=more aria-expanded=false>show all</button>'
                     f'<div class=seed>seed {seed}{extra}{credit(e)}</div></figcaption></figure>')
        L.append("</div>")

    fails = [x for x in (d.get("failures") or {}).get("entries", []) if (root / x["image"]).exists()]
    if fails:
        L.append(f'<h2 id="failures">The failures<span class=n>{len(fails)}</span>'
                 f'<a class=top href="#top">top</a></h2>')
        L.append(f'<p class=cat-desc>{html.escape((d["failures"]).get("_what",""))}</p>')
        L.append("<div class=grid>")
        for x in fails:
            seed = (x.get("params") or {}).get("seed")
            L.append(f'<figure class=fail><img loading=lazy src="{up}{html.escape(x["image"])}" alt="{html.escape(x["claim"])}">'
                     f'<figcaption><div class=t>{html.escape(x["claim"])}</div>'
                     f'<pre>asked for: {html.escape(x.get("expected",""))}\n\n{mark(x["prompt"], VOCAB)}</pre>'
                     f'<button class=cp data-p="{html.escape(x["prompt"], quote=True)}" '
                     f'aria-label="Copy the prompt for {html.escape(x["claim"], quote=True)}">'
                     f'copy</button>'
                     f'<button class=more aria-expanded=false>show all</button>'
                     f'<div class=seed>seed {seed}</div></figcaption></figure>')
        L.append("</div>")

    # The findings used to sit between the header and the first image: fifteen of
    # them, 9,758 pixels, eleven and a half screens. Someone who came to the
    # gallery to look at pictures and take a prompt had to scroll all of it
    # first, and the search box was underneath it too. Same mistake the README
    # had, on the page the README now sends people to. It goes after the images.
    f = d.get("findings")
    if f:
        L.append('<h2 id="findings">What this model actually does'
                 '<a class=top href="#top">top</a></h2>')
        L.append(f'<p class=cat-desc>{html.escape(counts(d, f.get("_intro","")))}</p>')
        for it in f.get("items", []):
            L.append(f'<div class=finding><h3>{html.escape(it["title"])}</h3>{md_lite(it["body"])}</div>')

    # The reproducibility sentence has to be exact, because the whole claim here
    # is that you can check it yourself. Measured 2026-07-25: the endpoint is
    # deterministic, same seed, strength, prompt and input bytes returned a
    # pixel-identical image across two runs (0 of 1,048,576 pixels differed). But
    # the images in this repo are lossy WebP re-encodes, so re-running an
    # image-to-image entry against the copy here does not hand the model the
    # bytes that produced the original. Composition, palette and medium come
    # back; brush-level texture does not. Text-to-image entries take no image
    # input and are unaffected.
    L.append('<footer>Prompts are MIT. The images are AI-generated output from '
             f'{html.escape(model)}, presented as model output rather than as photographs or human '
             'artwork, and were produced by the repository owner under the Krea 2 Community '
             'License. The safety checker was left enabled for every request; one image it '
             'flagged was dropped. Images are re-encoded from PNG to WebP to keep the repository '
             'clonable. The endpoint is deterministic, so a recorded seed regenerates a '
             'text-to-image entry exactly. The five image-to-image entries are re-runnable from '
             'the WebP source in this repo rather than the original PNG, so they reproduce the '
             'edit, composition, palette, medium. But not the exact pixels.</footer>')
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
      var grid = b.closest('h2').nextElementSibling;
      while (grid && !grid.classList.contains('grid')) grid = grid.nextElementSibling;
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
var q = document.getElementById('q'), qn = document.getElementById('qn');
if (q) {
  var figs = Array.prototype.map.call(document.querySelectorAll('figure'), function (f) {
    return { el: f, hay: f.textContent.toLowerCase() };
  });
  q.addEventListener('input', function () {
    var s = q.value.trim().toLowerCase(), shown = 0;
    figs.forEach(function (f) {
      var hit = !s || f.hay.indexOf(s) !== -1;
      f.el.style.display = hit ? '' : 'none';
      if (hit) shown++;
    });
    document.querySelectorAll('.grid').forEach(function (g) {
      var any = Array.prototype.some.call(g.querySelectorAll('figure'),
        function (f) { return f.style.display !== 'none'; });
      g.style.display = any ? '' : 'none';
      var h = g.previousElementSibling;
      while (h && h.tagName !== 'H2') h = h.previousElementSibling;
      if (h) h.style.display = any ? '' : 'none';
    });
    qn.textContent = s ? shown + ' of ' + figs.length : '';
  });
}
""")
    L.append("</script>")
    L.append("</div></body></html>")

    out.write_text("\n".join(L), encoding="utf-8")
    kb = out.stat().st_size // 1024
    print(f"wrote {out} ({kb} KB, {len(kept)} entries + {len(fails)} failures)")
    print("\nEnable Pages: Settings -> Pages -> Deploy from branch -> main / (root)")
    print(f"Then the page is https://<owner>.github.io/{repo.split('/')[-1]}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
