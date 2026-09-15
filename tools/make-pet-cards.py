#!/usr/bin/env python3
"""Crop the service-card photographs.

    python3 tools/make-pet-cards.py

Each service card carries a real animal across the top of it. The crops are 4:3
and framed a little above centre, because a face centred in a 4:3 box sits too
low once the card's rounded top corners clip it.

Add one by adding a row to CARDS: source stem, output name, the centre of the
crop in source pixels, and half its width. Height follows from the 4:3 ratio.
"""
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
OUT = IMG / "pets"
W, H = 640, 480

# source stem, name, centre x, centre y, half crop width
CARDS = [
    # the trio sit shoulder to shoulder in the group photograph, so these three
    # are kept narrow enough not to catch a slice of the neighbouring dog
    ("hero-care",          "brindle",       330,  395, 250),
    ("hero-care",          "collie",        800,  330, 240),
    ("hero-care",          "terrier",      1250,  405, 245),
    ("reviews-dog",        "cocker",        400,  380, 340),
    # single-subject studio portraits: centred, so the crop just frames the head
    # and upper chest
    ("pet-shepherd",       "shepherd",      627,  520, 470),
    ("pet-kitten-ginger",  "kitten-ginger", 627,  560, 440),
    ("pet-kitten-tabby",   "kitten-tabby",  627,  560, 440),
    ("pet-cat-tuxedo",     "cat-tuxedo",    627,  540, 450),
    ("pet-cat-siamese",    "cat-siamese",   627,  520, 460),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for stem, name, cx, cy, half in CARDS:
        src = IMG / f"{stem}.webp"
        if not src.exists():
            sys.exit(f"make-pet-cards: {src.relative_to(ROOT)} is missing")
        im = Image.open(src).convert("RGBA")
        halfh = half * H / W
        box = (cx - half, cy - halfh, cx + half, cy + halfh)
        box = (max(0, box[0]), max(0, box[1]), min(im.width, box[2]), min(im.height, box[3]))
        face = im.crop(tuple(int(v) for v in box))
        # cut-outs are transparent behind the subject; flatten onto white so the
        # card does not show the page through the fur
        flat = Image.new("RGBA", face.size, (255, 255, 255, 255))
        flat.alpha_composite(face)
        out = flat.convert("RGB").resize((W, H), Image.LANCZOS)
        path = OUT / f"{name}.webp"
        out.save(path, "WEBP", quality=84, method=6)
        made.append(path)
        print(f"    {name:<10} {stem:<12} -> {W}x{H}  {path.stat().st_size/1024:5.1f} kB")

    print(f"\n{len(made)} card photos, {sum(p.stat().st_size for p in made)/1024:.0f} kB total")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
