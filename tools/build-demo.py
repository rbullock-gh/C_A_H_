#!/usr/bin/env python3
"""Bundle the whole site into one self-contained HTML file.

    python3 tools/build-demo.py

The output, demo/columbia-animal-hospital-preview.html, has the stylesheet, the
script, both fonts and every image inlined as data URIs. Double-click it and it
opens — no server, no assets folder, nothing to install. Email it, drop it in a
shared folder, or open it on a phone.

All sixteen pages are in the one file. The header and footer appear once; each
page's <main> is stored alongside, and a small router swaps them when a link is
clicked, so navigation works from file:// exactly as it does on a server.

The live map iframe becomes a static panel — a frame needs a real page — and
the footer is relabelled so a forwarded copy is never mistaken for the live site.
"""
import base64
import mimetypes
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "demo" / "columbia-animal-hospital-preview.html"
SKIP_DIRS = {"src", "tools", "docs", "demo", "assets", ".git"}


def data_uri(path: pathlib.Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if path.suffix == ".woff2":
        mime = "font/woff2"
    elif path.suffix == ".svg":
        mime = "image/svg+xml"
    return f"data:{mime or 'application/octet-stream'};base64," + base64.b64encode(path.read_bytes()).decode()


def inline_css(css: str) -> str:
    def swap(m):
        rel = m.group(1).strip("'\"")
        target = (ROOT / "assets" / "css" / rel).resolve()
        if not target.exists():
            return m.group(0)
        return f"url('{data_uri(target)}')"
    return re.sub(r"url\(([^)]+)\)", swap, css)


def page_key(rel: str) -> str:
    return rel.replace("\\", "/")


def main() -> int:
    pages = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS:
            continue
        pages.append(page_key(str(rel)))
    if "index.html" not in pages:
        sys.exit("build-demo: index.html has not been built — run tools/build.py first")

    shell = (ROOT / "index.html").read_text(encoding="utf-8")

    # ---- inline the stylesheet, the script and every image -----------------
    css = inline_css((ROOT / "assets/css/styles.css").read_text(encoding="utf-8"))
    js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")

    images = {}
    for img in sorted((ROOT / "assets/img").glob("*")):
        if img.is_file():
            images[img.name] = data_uri(img)

    def swap_src(html: str) -> str:
        def repl(m):
            attr, path = m.group(1), m.group(2)
            name = path.rsplit("/", 1)[-1]
            return f'{attr}="{images[name]}"' if name in images else m.group(0)
        return re.sub(r'(src|href)="((?:\.\./)*assets/img/[^"]+)"', repl, html)

    # ---- collect each page's <main> ---------------------------------------
    mains, titles = {}, {}
    for rel in pages:
        html = (ROOT / rel).read_text(encoding="utf-8")
        m = re.search(r'<main id="main">(.*?)</main>', html, re.S)
        if not m:
            sys.exit(f"build-demo: {rel} has no <main id=\"main\">")
        body = swap_src(m.group(1))
        # links inside a subdirectory page point up a level; flatten them
        body = re.sub(r'href="\.\./([^"]+)"', r'href="\1"', body)
        body = re.sub(r'href="(?!https?:|tel:|mailto:|#|data:)([a-z0-9\-/]+\.html)"',
                      lambda mm: f'href="#/{mm.group(1)}"', body)
        # a live map cannot load from file://; leave the static panel in place
        body = body.replace('data-map="', 'data-map-disabled="')
        mains[rel] = body
        t = re.search(r"<title>(.*?)</title>", html)
        titles[rel] = t.group(1) if t else "Columbia Animal Hospital"

    # ---- assemble the shell ------------------------------------------------
    doc = shell
    doc = re.sub(r'<link rel="stylesheet" href="[^"]+">', f"<style>\n{css}\n</style>", doc)
    doc = re.sub(r'<script src="[^"]+" defer></script>', "", doc)
    doc = re.sub(r'<link rel="preload"[^>]*>', "", doc)
    doc = re.sub(r'<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>', "", doc)
    doc = swap_src(doc)
    doc = re.sub(r'href="(?!https?:|tel:|mailto:|#|data:)([a-z0-9\-/]+\.html)"',
                 lambda mm: f'href="#/{mm.group(1)}"', doc)

    body_main = f'<main id="main">{mains["index.html"]}</main>'
    doc = re.sub(r'<main id="main">.*?</main>', lambda _: body_main, doc, flags=re.S)

    store = "\n".join(
        f'<script type="text/html" data-page="{rel}" data-title="{titles[rel]}">{mains[rel]}</script>'
        for rel in pages if rel != "index.html"
    )

    router = """
<script>
(function () {
  var store = {};
  document.querySelectorAll('script[data-page]').forEach(function (s) {
    store[s.getAttribute('data-page')] = { html: s.textContent, title: s.getAttribute('data-title') };
  });
  store['index.html'] = { html: document.getElementById('main').innerHTML, title: document.title };

  function show(route) {
    var page = store[route] || store['index.html'];
    document.getElementById('main').innerHTML = page.html;
    document.title = page.title;
    document.querySelectorAll('.nav__link, .nav-panel__link').forEach(function (a) {
      var href = (a.getAttribute('href') || '').replace('#/', '');
      if (href === route) { a.setAttribute('aria-current', 'page'); }
      else { a.removeAttribute('aria-current'); }
    });
    window.scrollTo(0, 0);
    if (window.__cahInit) window.__cahInit();
  }

  window.addEventListener('hashchange', function () {
    var h = location.hash;
    if (h.indexOf('#/') === 0) { show(h.slice(2)); }
    else if (h.length > 1) {
      var el = document.getElementById(h.slice(1));
      if (el) el.scrollIntoView();
    }
  });
  if (location.hash.indexOf('#/') === 0) show(location.hash.slice(2));
})();
</script>
"""

    banner = """
<div style="background:#143026;color:#C7A57E;font:600 12px/1.5 Inter,system-ui,sans-serif;
letter-spacing:.14em;text-transform:uppercase;text-align:center;padding:10px 16px">
Preview build &middot; not the live site &middot; photography is placeholder
</div>
"""

    doc = doc.replace("<body ", "<body data-preview ", 1)
    doc = re.sub(r"(<body[^>]*>)", r"\1" + banner, doc, count=1)
    # main.js exposes window.__cahInit for exactly this: the router calls it
    # after swapping <main>, so no surgery on the script is needed here.
    doc = doc.replace("</body>", f"{store}\n<script>\n{js}\n</script>\n{router}\n</body>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc, encoding="utf-8")
    print(f"  {OUT.relative_to(ROOT)}")
    print(f"  {len(pages)} pages, {len(images)} images inlined, {OUT.stat().st_size / 1024:.0f} kB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
