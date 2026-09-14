#!/usr/bin/env python3
"""Generate the brand mark, favicons and the social share card.

    python3 tools/make-brand.py

The practice has no logo file that could be obtained — every image host was
blocked by the network policy — so this draws a restrained paw mark in the
brand green. If the client supplies real artwork, replace the outputs here and
delete this script rather than trying to match it.
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
ICO = ROOT / "assets" / "favicon"

FOREST = (30, 64, 52)
FOREST_DEEP = (20, 48, 38)
CREAM = (250, 247, 241)
TAN = (199, 165, 126)
SAGE = (126, 156, 136)

MARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" role="img" aria-label="Columbia Animal Hospital">
  <rect width="96" height="96" rx="24" fill="#1E4034"/>
  <rect x="4.5" y="4.5" width="87" height="87" rx="20" fill="none" stroke="#C7A57E" stroke-opacity="0.55" stroke-width="1.6"/>
  <g fill="#FAF7F1">
    <ellipse cx="30" cy="38" rx="7.4" ry="9.6"/>
    <ellipse cx="48" cy="31.5" rx="7.8" ry="10.2"/>
    <ellipse cx="66" cy="38" rx="7.4" ry="9.6"/>
    <path d="M48 49.5c-9.9 0-18.4 8.1-18.4 16.6 0 6.3 5.2 10.2 11.3 9.5 3.1-.4 5.4-1.6 7.1-1.6s4 1.2 7.1 1.6c6.1.7 11.3-3.2 11.3-9.5C66.4 57.6 57.9 49.5 48 49.5Z"/>
  </g>
</svg>
"""


def paw(draw: ImageDraw.ImageDraw, size: int, fill) -> None:
    """Draw the paw at 96-unit design scale, mapped onto `size` pixels."""
    k = size / 96.0
    def ell(cx, cy, rx, ry):
        draw.ellipse([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k], fill=fill)
    ell(30, 38, 7.4, 9.6)
    ell(48, 31.5, 7.8, 10.2)
    ell(66, 38, 7.4, 9.6)
    # main pad — an ellipse plus a squared lower half approximates the SVG path
    ell(48, 63, 18.4, 13.5)
    draw.rounded_rectangle(
        [(29.6) * k, (60) * k, (66.4) * k, (76) * k], radius=9 * k, fill=fill
    )


def icon(size: int, radius_ratio: float = 0.25, ring: bool = True) -> Image.Image:
    ss = 4  # supersample for clean edges
    img = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(size * ss * radius_ratio)
    d.rounded_rectangle([0, 0, size * ss - 1, size * ss - 1], radius=r, fill=FOREST)
    if ring and size >= 64:
        inset = int(size * ss * 0.047)
        d.rounded_rectangle(
            [inset, inset, size * ss - 1 - inset, size * ss - 1 - inset],
            radius=int(r * 0.82), outline=TAN + (140,), width=max(2, int(size * ss * 0.017)),
        )
    paw(d, size * ss, CREAM)
    return img.resize((size, size), Image.LANCZOS)


def font(px: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, px)
    return ImageFont.load_default(px)


def share_card() -> Image.Image:
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), FOREST_DEEP)
    d = ImageDraw.Draw(img)
    # a soft radial-ish wash so the card is not a flat rectangle
    for i in range(h):
        t = i / h
        d.line([(0, i), (w, i)], fill=(
            int(FOREST_DEEP[0] + (FOREST[0] - FOREST_DEEP[0]) * (1 - t) * 0.8),
            int(FOREST_DEEP[1] + (FOREST[1] - FOREST_DEEP[1]) * (1 - t) * 0.8),
            int(FOREST_DEEP[2] + (FOREST[2] - FOREST_DEEP[2]) * (1 - t) * 0.8),
        ))
    mark = icon(132, ring=False)
    img.paste(mark, (84, 96), mark)

    d.text((84, 268), "Columbia Animal Hospital", font=font(70, bold=True), fill=CREAM)
    d.text((84, 356), "Veterinary care in Columbia, Mississippi since 1975", font=font(34), fill=TAN)
    d.line([(84, 436), (400, 436)], fill=TAN, width=3)
    d.text((84, 470), "1409 Hwy 98E, Columbia, MS 39429", font=font(30), fill=(214, 226, 214))
    d.text((84, 516), "(601) 736-3041", font=font(38, bold=True), fill=CREAM)
    return img


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    ICO.mkdir(parents=True, exist_ok=True)

    (IMG / "logo-mark.svg").write_text(MARK_SVG, encoding="utf-8")
    (ICO / "favicon.svg").write_text(MARK_SVG, encoding="utf-8")

    icon(512).save(ICO / "icon-512.png")
    icon(192).save(ICO / "icon-192.png")
    icon(180).save(ICO / "apple-touch-icon.png")
    icon(32, radius_ratio=0.2, ring=False).save(ICO / "favicon-32.png")
    icon(256).save(IMG / "logo-mark.png")
    share_card().save(IMG / "og-image.png")

    for p in sorted(list(ICO.glob("*")) + [IMG / "og-image.png", IMG / "logo-mark.png", IMG / "logo-mark.svg"]):
        print(f"    {p.relative_to(ROOT)!s:<42} {p.stat().st_size / 1024:6.1f} kB")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:      # output piped into head/less
        raise SystemExit(0)
