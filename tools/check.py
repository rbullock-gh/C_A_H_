#!/usr/bin/env python3
"""Validate the built site before publishing or handing it to a client.

    python3 tools/check.py              # static checks, no dependencies
    python3 tools/check.py --browser    # also render in Chromium (needs Playwright)

Static checks run anywhere. The browser pass catches the two classes of bug that
only show up once the page is laid out: horizontal overflow, and content left
invisible when JavaScript is off.

Exit code is 0 when everything passes, 1 when any check fails.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {"src", "tools", "docs", "demo", "assets", ".git"}
CANONICAL_ADDRESS = "1409 Hwy 98E"

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
    "path", "circle", "rect", "use", "stop", "line", "polygon", "polyline", "ellipse",
}

failures: list[str] = []
warnings: list[str] = []
ICONS_DEFINED: set[str] = set()
ICONS_USED: set[str] = set()


def fail(msg): failures.append(msg)
def warn(msg): warnings.append(msg)


def pages() -> list[str]:
    found = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS:
            continue
        found.append(str(rel))
    return found


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.problems.append(f"line {self.getpos()[0]}: unexpected </{tag}>")

    def report(self):
        return self.problems + [f"line {ln}: <{t}> never closed" for t, ln in self.stack]


def norm(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    for a, b in (("&rsquo;", "'"), ("&amp;", "&"), ("&mdash;", "—"), ("&ndash;", "–"),
                 ("&nbsp;", " "), ("&middot;", "·")):
        text = text.replace(a, b)
    return " ".join(text.split()).lower()


def check_page(page: str) -> None:
    path = ROOT / page
    html = path.read_text(encoding="utf-8")
    here = path.parent
    print(f"\n  {page}")

    # --- structured data -------------------------------------------------
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if not blocks and page != "404.html":
        warn(f"{page}: no structured data")
    for i, block in enumerate(blocks):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            fail(f"{page}: JSON-LD block {i} is invalid — {e}")
            continue
        graph = data.get("@graph", [data])
        print(f"    schema           {[n.get('@type') for n in graph]}")

        for node in graph:
            if "aggregateRating" in node:
                fail(f"{page}: aggregateRating in schema — third-party ratings are not "
                     f"first-party review markup")
            # Google requires every FAQ answer to be visible on the page, so the
            # schema questions must match the rendered ones exactly.
            if node.get("@type") == "FAQPage":
                visible = {norm(s) for s in re.findall(r"<summary>(.*?)</summary>", html, re.S)}
                asked = [q["name"] for q in node["mainEntity"]]
                missing = [q for q in asked if norm(q) not in visible]
                if missing:
                    fail(f"{page}: FAQ schema questions with no visible counterpart: {missing}")
                else:
                    print(f"    faq parity       {len(asked)} questions match the page")

    # --- local files actually exist --------------------------------------
    refs = {
        r for r in re.findall(r'(?:src|href)="((?!https?:|tel:|mailto:|#|data:)[^"]+)"', html)
        if r and not r.startswith("#")
    }
    # srcset carries real paths too, and nothing else here would catch a typo
    for value in re.findall(r'srcset="([^"]+)"', html):
        for candidate in value.split(","):
            path = candidate.strip().split(" ")[0]
            if path and not path.startswith(("http", "data:")):
                refs.add(path)
    missing = []
    for r in refs:
        bare = r.split("#", 1)[0]
        if not bare:
            continue
        target = (ROOT / bare.lstrip("/")) if bare.startswith("/") else (here / bare)
        if not target.exists():
            missing.append(r)
    if missing:
        fail(f"{page}: references missing files: {sorted(missing)}")
    print(f"    local refs       {len(refs)} checked, {len(missing)} missing")

    # --- icon sprite -----------------------------------------------------
    defined = set(re.findall(r'<symbol id="([^"]+)"', html))
    used = set(re.findall(r'<use href="#([^"]+)"', html))
    if used - defined:
        fail(f"{page}: <use> references undefined icons: {sorted(used - defined)}")
    ICONS_DEFINED.update(defined)
    ICONS_USED.update(used)

    # --- markup ----------------------------------------------------------
    balance = TagBalance()
    balance.feed(html)
    for problem in balance.report()[:10]:
        fail(f"{page}: {problem}")

    # --- images ----------------------------------------------------------
    imgs = re.findall(r"<img\s[^>]*>", html)
    no_alt = [i for i in imgs if "alt=" not in i]
    no_dims = [i for i in imgs if "width=" not in i or "height=" not in i]
    empty_alt = [i for i in imgs if 'alt=""' in i and 'aria-hidden' not in i]
    if no_alt:
        fail(f"{page}: {len(no_alt)} <img> without alt")
    if no_dims:
        warn(f"{page}: {len(no_dims)} <img> without width/height (causes layout shift)")
    if empty_alt:
        warn(f"{page}: {len(empty_alt)} <img alt=\"\"> not marked aria-hidden")
    print(f"    images           {len(imgs)}, {len(no_alt)} without alt")

    # --- headings --------------------------------------------------------
    levels = [int(m.group(1)) for m in re.finditer(r"<h([1-6])[\s>]", html)]
    h1s = levels.count(1)
    if h1s != 1:
        fail(f"{page}: expected exactly one <h1>, found {h1s}")
    jumps = [f"h{levels[i-1]}->h{levels[i]}" for i in range(1, len(levels)) if levels[i] > levels[i-1] + 1]
    if jumps:
        warn(f"{page}: heading level jumps: {jumps}")
    print(f"    headings         {h1s} h1, {len(jumps)} level jumps")

    # --- in-page links ---------------------------------------------------
    anchors = {a for a in re.findall(r'href="#([^"]+)"', html) if a}
    ids = set(re.findall(r'\sid="([^"]+)"', html))
    broken = sorted(anchors - ids)
    if broken:
        fail(f"{page}: anchors point at ids that do not exist: {broken}")

    # --- unfinished content ----------------------------------------------
    for marker in ("[ your", "lorem ipsum", "TODO:", "FIXME:", "xxx", "tbd", "coming soon"):
        if marker.lower() in norm(html):
            fail(f'{page}: unfinished placeholder text left in the page: "{marker}"')

    # --- search metadata, every page -------------------------------------
    title = re.search(r"<title>(.*?)</title>", html)
    desc = re.search(r'<meta name="description" content="(.*?)"', html)
    if not title:
        fail(f"{page}: no <title>")
    elif len(title.group(1)) > 65:
        warn(f"{page}: title is {len(title.group(1))} chars (search results cut off near 60)")
    if not desc:
        fail(f"{page}: no meta description")
    elif not 120 <= len(desc.group(1)) <= 165:
        warn(f"{page}: meta description is {len(desc.group(1))} chars (aim for 120-165)")
    if not re.search(r'rel="canonical"', html):
        fail(f"{page}: no canonical tag")
    og = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if og and not og.group(1).startswith("http"):
        fail(f"{page}: og:image must be an absolute URL or scrapers cannot fetch it")
    if "reveal" in html and "html:not(.js)" not in (ROOT / "assets/css/styles.css").read_text():
        fail(f"{page}: scroll-reveal is used with no no-JS fallback rule in the stylesheet")
    print(f"    title/desc       {len(title.group(1)) if title else 0} / "
          f"{len(desc.group(1)) if desc else 0} chars")

    # --- tap targets on the phone link -----------------------------------
    if 'href="tel:' not in html:
        fail(f"{page}: no tap-to-call link on the page")


def check_svgs() -> None:
    """A malformed SVG does not error — the browser just draws nothing."""
    import xml.etree.ElementTree as ET
    print("\n  svg assets")
    bad = []
    files = sorted((ROOT / "assets").rglob("*.svg"))
    for f in files:
        try:
            ET.parse(f)
        except ET.ParseError as e:
            bad.append(f"{f.relative_to(ROOT)}: {e}")
    for b in bad:
        fail(f"malformed SVG (browsers render nothing): {b}")
    print(f"    well-formed      {len(files) - len(bad)} of {len(files)}")


def check_consistency(page_list: list[str]) -> None:
    """The address and phone must be identical everywhere — local ranking depends on it."""
    print("\n  consistency")
    phones, addresses, count = set(), set(), 0
    for page in page_list:
        html = (ROOT / page).read_text(encoding="utf-8")
        phones |= set(re.findall(r"\(601\)\s*736-\d{4}", html))
        phones |= {p for p in re.findall(r"tel:\+?[\d-]+", html)}
        # anything that is not the one canonical form is a local-SEO problem
        found = [m.group(0) for m in re.finditer(r"1409\s+(?:Hwy|Highway)\.?\s*98\s*(?:E\b|East)", html)]
        addresses |= set(found)
        count += len(found)
    if len(phones) > 2:
        fail(f"phone number written inconsistently across pages: {sorted(phones)}")
    variants = {" ".join(a.split()) for a in addresses}
    bad = variants - {CANONICAL_ADDRESS}
    if bad:
        fail(f"address written as {sorted(bad)} somewhere — local ranking needs the single "
             f"form {CANONICAL_ADDRESS!r} everywhere")
    print(f"    phone            {sorted(phones)}")
    print(f"    address          {sorted(variants)}  ({count} occurrences across {len(page_list)} pages)")


def check_sitemap(page_list: list[str]) -> None:
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    listed = set(re.findall(r"<loc>(.*?)</loc>", sm))
    print(f"\n  sitemap\n    urls             {len(listed)}")
    for page in page_list:
        if page == "404.html":
            continue
        slug = page.replace("index.html", "")
        if not any(u.endswith("/" + slug) or u.endswith(slug) for u in listed):
            warn(f"sitemap.xml does not list {page}")


def check_browser(page_list: list[str]) -> None:
    print("\n  browser")
    script = r"""
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const urls = process.argv.slice(2);
const b = await chromium.launch();
const out = { overflow: [], hiddenNoJs: [], errors: [], smallTaps: [], brokenImages: [] };
for (const url of urls) {
  for (const w of [390, 820, 1440]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } });
    p.on('pageerror', e => out.errors.push(`${url} @${w}px: ${e.message}`));
    await p.goto(url, { waitUntil: 'load' });
    await p.evaluate(async () => { for (let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,15));} });
    await p.evaluate(() => [...document.images].forEach(i => (i.loading = 'eager')));
    await p.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : i.decode().catch(() => 0))));
    await p.waitForTimeout(350);
    if (w === 1440) {
      const broken = await p.evaluate(() => [...document.images]
        .filter(i => !i.complete || i.naturalWidth === 0)
        .map(i => i.getAttribute('src')));
      broken.forEach(src => out.brokenImages.push(`${url}: ${src}`));
    }
    const over = await p.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
    if (over) out.overflow.push(`${url} @${w}px`);
    if (w === 390) {
      // interactive targets smaller than 44px are hard to hit on a phone
      const small = await p.evaluate(() => {
        const bad = [];
        document.querySelectorAll('a, button, summary').forEach(el => {
          if (!el.offsetParent && el.tagName !== 'SUMMARY') return;
          const r = el.getBoundingClientRect();
          if (r.width === 0 || r.height === 0) return;
          if (r.height < 24 || r.width < 24) bad.push((el.textContent || el.className).trim().slice(0, 32) + ` ${Math.round(r.width)}x${Math.round(r.height)}`);
        });
        return bad.slice(0, 6);
      });
      small.forEach(s => out.smallTaps.push(`${url}: ${s}`));
    }
    await p.close();
  }
  const ctx = await b.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  const np = await ctx.newPage();
  await np.goto(url, { waitUntil: 'load' });
  await np.waitForTimeout(250);
  // isVisible() reports true for opacity:0, so assert on computed opacity instead
  const faded = await np.evaluate(() =>
    [...document.querySelectorAll('.reveal')].filter(e => parseFloat(getComputedStyle(e).opacity) < 0.99).length);
  if (faded) out.hiddenNoJs.push(`${url}: ${faded} blocks`);
  await ctx.close();
}
await b.close();
console.log(JSON.stringify(out));
"""
    if not pathlib.Path("/opt/node22/lib/node_modules/playwright/index.mjs").exists():
        warn("Playwright not found — skipped the browser pass")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(script)
        script_path = f.name
    urls = [(ROOT / p).as_uri() for p in page_list]
    try:
        res = subprocess.run(["node", script_path, *urls], capture_output=True, text=True, timeout=600)
        if res.returncode != 0:
            tail = res.stderr.strip().splitlines()[-1] if res.stderr.strip() else "?"
            warn(f"browser pass could not run: {tail}")
            return
        data = json.loads(res.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001
        warn(f"browser pass could not run: {e}")
        return
    finally:
        os.unlink(script_path)

    if data["overflow"]:
        for o in data["overflow"]:
            fail(f"horizontal overflow — {o}")
    else:
        print(f"    overflow         none at 390/820/1440px across {len(page_list)} pages")
    if data["hiddenNoJs"]:
        for h in data["hiddenNoJs"]:
            fail(f"reveal blocks stay transparent with JavaScript off — {h}")
    else:
        print("    javascript off   all content visible")
    if data["brokenImages"]:
        for b in data["brokenImages"]:
            fail(f"image failed to load — {b}")
    else:
        print("    images           every image decoded")
    if data["smallTaps"]:
        for t in data["smallTaps"][:8]:
            fail(f"tap target below the WCAG 24x24 minimum at 390px — {t}")
    else:
        print("    tap targets      all clear 24x24 at 390px (WCAG 2.5.8)")
    for e in data["errors"]:
        fail(f"page error {e}")


def main() -> int:
    page_list = pages()
    print(f"Checking site — {len(page_list)} pages")
    for page in page_list:
        check_page(page)
    check_svgs()
    check_consistency(page_list)
    check_sitemap(page_list)
    unused = ICONS_DEFINED - ICONS_USED
    if unused:
        warn(f"icon symbols defined but never used anywhere: {sorted(unused)}")
    if "--browser" in sys.argv:
        check_browser(page_list)

    print("\n" + "-" * 66)
    for w in warnings:
        print(f"  warn  {w}")
    for f_ in failures:
        print(f"  FAIL  {f_}")
    print("-" * 66)
    if failures:
        print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
        return 1
    print(f"All checks passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:      # output piped into head/less
        raise SystemExit(0)
