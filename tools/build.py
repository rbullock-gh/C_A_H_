#!/usr/bin/env python3
"""Assemble the static site from src/ into plain HTML at the repo root.

    python3 tools/build.py

Why a build step for a static site: every page repeats the header, the footer,
the phone number, the address and the opening hours. For local SEO those have to
match character-for-character everywhere, and hand-maintaining them across
fifteen pages is how they drift. src/data.json is the single source of truth;
this script is 200 lines of string substitution with no dependencies, and the
output is ordinary HTML that any host will serve and any developer can read.

Template syntax:
    {{ key }}            value from data.json (dotted paths allowed)
    {{ key | raw }}      same, without HTML escaping
    {{> partial }}       inline src/partials/<partial>.html
    {{# PAGEVAR }}       value from the page's own front matter
Front matter is a JSON object in an HTML comment at the top of each page file.
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

FRONT_MATTER = re.compile(r"^\s*<!--json\s*(\{.*?\})\s*-->\s*", re.S)
TOKEN = re.compile(r"\{\{\s*([#>]?)\s*([a-zA-Z0-9_.\-]+)\s*(\|\s*raw\s*)?\}\}")


def load_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"build: {path.name} is not valid JSON — {e}")


def dig(data: dict, path: str):
    node = data
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def render(text: str, data: dict, page: dict, depth: int = 0) -> str:
    """Substitute tokens. Partials are expanded recursively."""
    if depth > 8:
        sys.exit("build: partial include nested more than 8 deep — probably a loop")

    def swap(m: re.Match) -> str:
        kind, key, raw = m.group(1), m.group(2), m.group(3)
        if kind == ">":
            part = SRC / "partials" / f"{key}.html"
            if not part.exists():
                sys.exit(f"build: missing partial src/partials/{key}.html")
            return render(part.read_text(encoding="utf-8"), data, page, depth + 1)
        value = page.get(key) if kind == "#" else dig(data, key)
        if value is None:
            sys.exit(f"build: no value for {{{{ {kind}{key} }}}} (page: {page.get('slug', '?')})")
        if isinstance(value, (dict, list)):
            sys.exit(f"build: {key} is a {type(value).__name__}, not a string (page: {page.get('slug','?')})")
        value = str(value)
        return value if raw else html.escape(value, quote=True)

    return TOKEN.sub(swap, text)


def build_page(src_path: pathlib.Path, data: dict, layout: str) -> pathlib.Path:
    text = src_path.read_text(encoding="utf-8")
    m = FRONT_MATTER.match(text)
    if not m:
        sys.exit(f"build: {src_path.name} has no <!--json ... --> front matter")
    page = json.loads(m.group(1))
    body = text[m.end():]

    required = ("slug", "title", "description", "out")
    for key in required:
        if key not in page:
            sys.exit(f"build: {src_path.name} front matter is missing '{key}'")

    # Pages in a subdirectory need ../ on every asset and link.
    depth = page["out"].count("/")
    page.setdefault("base", "../" * depth)
    page.setdefault("schema", "")
    page.setdefault("bodyclass", "")
    page.setdefault("ogtype", "website")

    # The header marks the current page. Front matter sets nav to one of the keys
    # below; every other key resolves to an empty attribute.
    current = page.get("nav", "")
    for key in ("Home", "About", "Vets", "Services", "Faq", "Contact"):
        page[f"nav{key}"] = ' aria-current="page"' if current == key else ""

    # Same idea for the "other services" list in the service-page sidebar.
    svc = page.get("service", "")
    for key in ("Surgery", "Dental", "Radiography", "Heartworm", "Dermatology",
                "Grooming", "Boarding", "Microchipping", "Reproductive"):
        page[f"is{key}"] = ' aria-current="page"' if svc == key else ""
    page["canonical"] = data["site"]["url"].rstrip("/") + "/" + page["out"].replace("index.html", "")

    rendered_body = render(body, data, page)
    doc = render(layout, data, page).replace("<!--BODY-->", rendered_body)

    out = ROOT / page["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


def build_sitemap(data: dict, pages: list[dict]) -> None:
    base = data["site"]["url"].rstrip("/")
    urls = []
    for p in pages:
        loc = base + "/" + p["out"].replace("index.html", "")
        priority = p.get("priority", "0.7")
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>{priority}</priority>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")

    robots = f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


def main() -> int:
    data = load_json(SRC / "data.json")
    layout = (SRC / "layout.html").read_text(encoding="utf-8")

    sources = sorted((SRC / "pages").rglob("*.html"))
    if not sources:
        sys.exit("build: no pages in src/pages/")

    print("Building site")
    built, metas = [], []
    for src_path in sources:
        out = build_page(src_path, data, layout)
        page = json.loads(FRONT_MATTER.match(src_path.read_text(encoding="utf-8")).group(1))
        if page.get("sitemap", True):
            metas.append(page)
        built.append(out)
        print(f"    {out.relative_to(ROOT)!s:<42} {out.stat().st_size / 1024:6.1f} kB")

    metas.sort(key=lambda p: (-float(p.get("priority", 0.7)), p["out"]))
    build_sitemap(data, metas)
    print(f"    sitemap.xml / robots.txt                    {len(metas)} urls")
    print(f"\n{len(built)} pages built")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:      # output piped into head/less
        raise SystemExit(0)
