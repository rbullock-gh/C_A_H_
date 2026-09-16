#!/usr/bin/env python3
"""Render real client reviews into the home page.

    python3 tools/make-reviews.py

Reads src/reviews.json and writes the quotes between the markers in the reviews
section of src/pages/index.html. An empty list writes nothing and leaves the
section exactly as it is, which is the correct behaviour until there is
something real to show.

Two rules this tool exists to enforce.

**Nothing here may be written by us.** Every quote is somebody's own words about
a business they actually used. A testimonial we composed on a practice's website
is a lie told in a client's name, and the people reading it live in the same
town. The file has no field for a review we invented because there must not be
one.

**The rating is displayed, never marked up.** Google does not show review rich
results for a business's own reviews of itself, and putting a third party's
rating into the page's own aggregateRating is a structured-data policy
violation. tools/check.py fails the build if aggregateRating ever appears. The
star count can be printed as text all day; it just cannot be a claim in the
schema.
"""
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "reviews.json"
PAGE = ROOT / "src" / "pages" / "index.html"
OPEN, CLOSE = "<!-- reviews:start -->", "<!-- reviews:end -->"


def card(review: dict) -> str:
    quote = html.escape(review["quote"].strip())
    who = html.escape(review["name"].strip())
    when = html.escape(review.get("date", "").strip())
    about = html.escape(review.get("about", "").strip())
    meta = " &middot; ".join(p for p in (when, about) if p)
    return (
        '      <figure class="review">\n'
        f"        <blockquote>{quote}</blockquote>\n"
        f"        <figcaption>{who}"
        + (f"<span>{meta}</span>" if meta else "")
        + "</figcaption>\n      </figure>"
    )


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    reviews = data.get("reviews", [])
    src = data.get("source", {})
    page = PAGE.read_text(encoding="utf-8")

    if OPEN not in page or CLOSE not in page:
        sys.exit(f"make-reviews: {PAGE.name} has no {OPEN} / {CLOSE} markers")

    if not reviews:
        body = ""
        print("  no reviews yet — the section keeps its current treatment")
    else:
        for i, r in enumerate(reviews):
            for field in ("quote", "name"):
                if not r.get(field, "").strip():
                    sys.exit(f"make-reviews: review {i} has no {field}")
        cards = "\n".join(card(r) for r in reviews)
        tail = ""
        if src.get("count"):
            where = html.escape(src.get("name", "Google"))
            line = f'Read all {src["count"]} reviews on {where}'
            if src.get("url"):
                inner = (f'<a class="btn btn--outline" href="{html.escape(src["url"])}" '
                         f'target="_blank" rel="noopener">{line}</a>')
            else:
                inner = line
            tail = f'\n    <p class="review-source">{inner}</p>'
        body = f'\n    <div class="review-grid reveal">\n{cards}\n    </div>{tail}\n  '
        print(f"  {len(reviews)} review(s) rendered")

    start = page.index(OPEN) + len(OPEN)
    end = page.index(CLOSE)
    PAGE.write_text(page[:start] + body + page[end:], encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
