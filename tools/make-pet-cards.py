#!/usr/bin/env python3
"""Build the service-card photographs.

    python3 tools/make-pet-cards.py

Every service card carries a real animal above its heading. The cards show the
whole animal rather than a crop of its face, so each photograph is rebuilt here
as a square plate: the subject is measured, scaled to a common height, and set
on the page's own warm white with its feet on the bottom edge.

Two things make that work. The studio portraits were shot on a sweep within a
point or two of --warm-white, and the group photographs are cut-outs on
transparency, so once everything is flattened onto that same warm white the
edge of the image itself is invisible against the card. A point or two is still
a visible line on a good screen, though, so anything already within TONE_TOLERANCE
of the ground is pulled the rest of the way onto it — enough to close the seam,
too little to touch a pale kitten. And because every subject is scaled to the
same fraction of the plate, a kitten and a full-grown dog read at the same size
in the grid instead of one dwarfing the next.

Add a card with a Card row: the source stem, the output name, the region of the
source to look in, any shapes to rub out inside it, and a turn. The region and
the shapes matter for the group photographs, where the dogs stand shoulder to
shoulder: the region gets close to one dog, and the shapes trace the diagonal
seam a rectangle cannot follow — an ear leaning over the neighbour, a shoulder
pressed against one. The turn is for a dog photographed leaning into the frame:
standing it upright makes it a portrait like the rest instead of one animal
arriving from the side of its card. A photograph of one animal, shot square,
needs none of the three.

A turn happens first, so a region or a shape on a turned card is measured on the
turned picture, not the original.
"""
import collections
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
OUT = IMG / "pets"

SIDE = 620                      # the square plate, in pixels
SUBJECT_HEIGHT = 0.94           # of the plate, before the width cap applies
SUBJECT_WIDTH = 0.96
GROUND = (252, 251, 249)        # --warm-white
ALPHA_FLOOR = 24                # transparent-enough to be background
SWEEP_TOLERANCE = 12            # how far off the studio sweep a pixel must be
TONE_TOLERANCE = 18             # near enough the ground to be flattened onto it
EDGE_SHARE = 0.004              # of a row's pixels, before the row counts

# the seams between the three dogs in the group photograph, in source pixels:
# where one dog's fur gives way to the next. Traced off the photograph itself.
BRINDLE_COLLIE = [(555, 600), (620, 600), (620, 1016), (528, 1016), (535, 930),
                  (544, 880), (549, 830), (553, 730), (550, 680), (548, 640)]
# The collie's right ear leans out over the terrier and comes to a point in
# clear air above its head, so the line between the two runs well right of the
# collie's shoulders before dropping back. Traced down the white left between
# them, it is the single boundary both dogs are cut along: the collie keeps
# everything left of it, the terrier everything right, and the collie's ear
# stays whole instead of ending against the side of its card.
COLLIE_TERRIER = [
    (1080, 0), (1080, 140), (1068, 165), (1055, 180), (1046, 200), (1038, 220),
    (1026, 240), (1020, 262), (1020, 300), (1006, 330), (1000, 380), (1000, 580),
    (994, 620), (986, 660), (982, 700), (980, 760), (992, 790), (996, 830),
    (996, 940), (1000, 1000), (1000, 1016),
]
# Right of the seam, for the collie's frame; left of it, for the terrier's. Down
# at the shoulders the two coats interleave, so each side is pushed a few pixels
# into its own dog: better to shave one fur edge than to leave the neighbour's.
BITE = 4
TERRIER_SIDE = [(x - BITE, y) for x, y in COLLIE_TERRIER] + [(1120, 1016), (1120, 0)]
COLLIE_SIDE = [(x + BITE, y) for x, y in COLLIE_TERRIER] + [(940, 1016), (940, 0)]

Card = collections.namedtuple("Card", "stem name region erase turn")
Card.__new__.__defaults__ = (None, None, 0)

CARDS = [
    # the trio stand shoulder to shoulder, so each one has its neighbours cut away
    Card("hero-care", "brindle", (0, 120, 562, 1016), [BRINDLE_COLLIE]),
    Card("hero-care", "collie", (556, 0, 1092, 1016),
         [[(556, 130), (574, 130), (574, 255), (556, 255)], TERRIER_SIDE]),
    Card("hero-care", "terrier", (980, 120, 1536, 1016), [COLLIE_SIDE]),
    # single-subject studio portraits, already alone and square in the frame
    Card("pet-frenchie", "frenchie"),
    Card("pet-shepherd", "shepherd"),
    Card("pet-kitten-ginger", "kitten-ginger"),
    Card("pet-kitten-tabby", "kitten-tabby"),
    Card("pet-cat-tuxedo", "cat-tuxedo"),
    Card("pet-cat-siamese", "cat-siamese"),
]


def flatten_ground(plate: Image.Image) -> Image.Image:
    """Pull every near-ground pixel exactly onto the ground.

    The sweep a portrait was shot on is a point or two off --warm-white and
    carries a faint gradient of its own; both draw a rectangle on the card where
    the photograph ends. Pixels far enough from the ground — the animal — are
    left alone, and the ones between fade across so no hard edge replaces it.
    """
    arr = np.asarray(plate.convert("RGB"), dtype=np.float32)
    ground = np.array(GROUND, dtype=np.float32)
    distance = np.sqrt(((arr - ground) ** 2).sum(axis=2))
    pull = np.clip(1.0 - distance / TONE_TOLERANCE, 0.0, 1.0)[..., None]
    arr = arr * (1.0 - pull) + ground * pull
    return Image.fromarray(arr.round().astype(np.uint8), "RGB")


def subject_mask(im: Image.Image) -> Image.Image:
    """A black-and-white mask of the animal, however its source marks it."""
    alpha = im.getchannel("A")
    if alpha.getextrema()[0] < ALPHA_FLOOR:           # a cut-out on transparency
        return alpha.point(lambda v: 255 if v > ALPHA_FLOOR else 0)
    # a studio sweep: anything far enough off the backdrop colour is the animal
    rgb = im.convert("RGB")
    bands = rgb.split()
    diff = None
    for band, ground in zip(bands, GROUND):
        d = band.point(lambda v, g=ground: min(255, abs(v - g)))
        diff = d if diff is None else Image.blend(diff, d, 0.5).point(lambda v: min(255, v * 2))
    return diff.point(lambda v: 255 if v > SWEEP_TOLERANCE else 0)


def subject_box(mask: Image.Image) -> tuple[int, int, int, int]:
    """The subject's bounds, ignoring stray specks along an edge."""
    w, h = mask.size
    px = mask.load()
    rows = [sum(1 for x in range(w) if px[x, y]) for y in range(h)]
    cols = [sum(1 for y in range(h) if px[x, y]) for x in range(w)]
    ymin = next((y for y, n in enumerate(rows) if n > w * EDGE_SHARE), 0)
    ymax = next((y for y in range(h - 1, -1, -1) if rows[y] > w * EDGE_SHARE), h - 1)
    xmin = next((x for x, n in enumerate(cols) if n > h * EDGE_SHARE), 0)
    xmax = next((x for x in range(w - 1, -1, -1) if cols[x] > h * EDGE_SHARE), w - 1)
    return xmin, ymin, xmax + 1, ymax + 1


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for stem, name, region, erase, turn in CARDS:
        src = IMG / f"{stem}.webp"
        if not src.exists():
            sys.exit(f"make-pet-cards: {src.relative_to(ROOT)} is missing")
        im = Image.open(src).convert("RGBA")
        if turn:
            im = im.rotate(turn, resample=Image.BICUBIC, expand=True)
        if erase:
            alpha = im.getchannel("A")
            pen = ImageDraw.Draw(alpha)
            for shape in erase:
                pen.polygon(shape, fill=0)
            im.putalpha(alpha)
        if region:
            im = im.crop(region)

        box = subject_box(subject_mask(im))
        animal = im.crop(box)
        scale = min(SIDE * SUBJECT_HEIGHT / animal.height,
                    SIDE * SUBJECT_WIDTH / animal.width)
        size = (max(1, round(animal.width * scale)), max(1, round(animal.height * scale)))
        animal = animal.resize(size, Image.LANCZOS)

        plate = Image.new("RGBA", (SIDE, SIDE), (*GROUND, 255))
        plate.alpha_composite(animal, ((SIDE - size[0]) // 2, SIDE - size[1]))
        path = OUT / f"{name}.webp"
        flatten_ground(plate).save(path, "WEBP", quality=82, method=6)
        made.append(path)
        print(f"    {name:<14} {stem:<18} subject {box[2]-box[0]:>4}x{box[3]-box[1]:<4}"
              f" -> {size[0]}x{size[1]} on {SIDE}  {path.stat().st_size/1024:5.1f} kB")

    print(f"\n{len(made)} card photos, {sum(p.stat().st_size for p in made)/1024:.0f} kB total")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
