#!/usr/bin/env python3
"""Crop circular pet portraits for the service card bubbles.

    python3 tools/make-pet-bubbles.py

The service cards carry a real animal's face rather than a line icon. Each one
is cut from a photograph the client supplied, squared on the face, masked to a
circle at 4x and downsampled so the edge stays smooth, and written to
assets/img/pets/ as WebP with an alpha channel.

Add a face by adding a row to FACES: the source image stem, a name, the centre
of the face in source pixels, and half the crop width. Run it and check the
contact sheet it prints the path to.
"""
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
OUT = IMG / "pets"
SIZE = 200          # 60px tile at just over 3x

# source stem, name, centre x, centre y, half crop width
FACES = [
    ("hero-care",   "brindle",  355,  430, 250),
    ("hero-care",   "collie",   800,  360, 260),
    ("hero-care",   "terrier", 1215,  430, 250),
    ("reviews-dog", "cocker",   400,  330, 300),
    ("cta-dog",     "shiba",    360,  330, 300),
    ("welcome-dog", "aussie",   490,  300, 270),
]


def circle(im: Image.Image, size: int) -> Image.Image:
    """Mask to a circle at 4x, then downsample — a 1x mask leaves a jagged rim."""
    im = im.convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for stem, name, cx, cy, half in FACES:
        src = IMG / f"{stem}.webp"
        if not src.exists():
            sys.exit(f"make-pet-bubbles: {src.relative_to(ROOT)} is missing")
        im = Image.open(src).convert("RGBA")
        box = (max(0, cx - half), max(0, cy - half),
               min(im.width, cx + half), min(im.height, cy + half))
        face = im.crop(box)
        # the cut-outs are transparent behind the subject; flatten onto white so
        # the circle is opaque and does not show the page through the fur
        flat = Image.new("RGBA", face.size, (255, 255, 255, 255))
        flat.alpha_composite(face)
        out = circle(flat, SIZE)
        path = OUT / f"{name}.webp"
        out.save(path, "WEBP", quality=88, method=6)
        made.append(path)
        print(f"    {name:<10} {stem:<12} {box} -> {SIZE}x{SIZE}  {path.stat().st_size/1024:5.1f} kB")

    total = sum(p.stat().st_size for p in made)
    print(f"\n{len(made)} pet bubbles, {total/1024:.0f} kB total")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
