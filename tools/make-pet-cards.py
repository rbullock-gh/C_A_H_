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

Add a card by adding a row to CARDS: source stem, output name, the region of the
source to look in, and any shapes to rub out inside it. Those two matter for the
group photographs, where the dogs stand shoulder to shoulder: the region gets
close to one dog, and the shapes trace the diagonal seam a rectangle cannot
follow — an ear leaning over the neighbour, a shoulder pressed against one. Pass
None for a photograph with one animal in it.
"""
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
# the collie leans its ear over the terrier, so the seam is a diagonal above the
# shoulders and close to vertical below them; each dog is cut on its own side
COLLIE_SIDE = [(980, 100), (1068, 100), (1068, 175), (1062, 195), (1032, 245),
               (1014, 330), (1006, 380), (1000, 600), (992, 750), (986, 1016),
               (980, 1016)]
TERRIER_SIDE = [(996, 340), (1030, 340), (1030, 1016), (978, 1016), (984, 750),
                (990, 600), (999, 380)]

# source stem, name, region to look in, shapes to rub out inside it
CARDS = [
    # the trio stand shoulder to shoulder, so each one has its neighbours cut away
    ("hero-care",          "brindle",       (0, 120, 562, 1016),    [BRINDLE_COLLIE]),
    ("hero-care",          "collie",        (556, 0, 1016, 1016),
     [[(556, 130), (574, 130), (574, 255), (556, 255)], TERRIER_SIDE]),
    ("hero-care",          "terrier",       (980, 120, 1536, 1016), [COLLIE_SIDE]),
    ("reviews-dog",        "cocker",        None,                   None),
    # single-subject studio portraits, already alone in the frame
    ("pet-shepherd",       "shepherd",      None,                   None),
    ("pet-kitten-ginger",  "kitten-ginger", None,                   None),
    ("pet-kitten-tabby",   "kitten-tabby",  None,                   None),
    ("pet-cat-tuxedo",     "cat-tuxedo",    None,                   None),
    ("pet-cat-siamese",    "cat-siamese",   None,                   None),
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
    for stem, name, region, erase in CARDS:
        src = IMG / f"{stem}.webp"
        if not src.exists():
            sys.exit(f"make-pet-cards: {src.relative_to(ROOT)} is missing")
        im = Image.open(src).convert("RGBA")
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
