#!/usr/bin/env python3
"""Generate labelled photo placeholders at the real dimensions.

    python3 tools/make-placeholders.py

No real photography of the practice could be obtained — the network policy
blocked every image host. Rather than substitute stock photography, which is
exactly what visitors scroll past, each image slot gets a placeholder in the
brand palette that states what shot belongs there.

Two variants, and the difference matters:
  labelled  standalone content images — carries the slot description
  plain     images sitting BEHIND headline copy, where a label ghosts through
            the text and reads as a rendering bug

Swap in real photos with tools/apply-photos.sh once the client supplies them.
"""
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"

# slot: (width, height, variant, description shown on the placeholder)
SLOTS = {
    "hero-care": (1536, 1016, "plain", "Three dogs, cut out on transparency (client supplied)"),
    "closer-community": (1800, 900, "plain", "Owner with their dog outside the hospital"),
    "why-exam": (1200, 900, "labelled", "Technician holding a cat during an exam"),
    "about-hospital": (1200, 900, "labelled", "Exterior of the hospital on Hwy 98E, signage visible"),
    "about-history": (1000, 1200, "labelled", "Older photograph of the practice, or the building today"),
    "vet-loper": (800, 1000, "labelled", "Dr. Janelle Loper — portrait, chest up"),
    "vet-sanford": (800, 1000, "labelled", "Dr. Pat Sanford — portrait, chest up"),
    "vet-williams": (800, 1000, "labelled", "Dr. Bridgett Williams — portrait, chest up"),
    "svc-surgery": (1200, 800, "labelled", "Surgical suite, prepped and clean"),
    "svc-dental-care": (1200, 800, "labelled", "Dental cleaning in progress, or a dog's teeth"),
    "svc-digital-radiography": (1200, 800, "labelled", "Digital x-ray image on a monitor"),
    "svc-heartworm-testing": (1200, 800, "labelled", "Blood draw or in-house test being run"),
    "svc-dermatology": (1200, 800, "labelled", "Skin or ear examination close up"),
    "svc-grooming": (1200, 800, "labelled", "Groomer working with a dog on the table"),
    "svc-boarding": (1200, 800, "labelled", "Clean boarding run, or a dog on its daily walk"),
    "svc-microchipping": (1200, 800, "labelled", "Scanner being passed over a pet's shoulders"),
    "svc-reproductive-services": (1200, 800, "labelled", "Puppies or a nursing mother, calm setting"),
    "contact-building": (1400, 900, "labelled", "The building and car park from the road"),
    "gallery-welcome": (1200, 1200, "labelled", "A dog greeted at the front desk"),
    "gallery-reception": (1000, 1000, "labelled", "Reception and waiting area"),
    "gallery-exam": (1000, 1000, "labelled", "An exam room, clean and well lit"),
    "gallery-treatment": (1000, 1000, "labelled", "Treatment area or laboratory bench"),
    "gallery-boarding": (1000, 1000, "labelled", "A boarding run, or a dog on its daily walk"),
    "reviews-dog": (804, 1112, "plain", "Cut-out dog for the reviews panel (client supplied)"),
    "cta-dog": (717, 1197, "plain", "Cut-out dog for the closing call to action (client supplied)"),
    "welcome-dog": (977, 855, "plain", "Cut-out dog with paws over an edge (client supplied)"),
    "team-photo": (2000, 669, "labelled", "The team at the Highway 98 East sign (client supplied)"),
}

CREAM = "#F0E9DC"
SAGE_PALE = "#DCE6DC"
FOREST = "#1E4034"
SAGE = "#7E9C88"
TAN = "#C7A57E"
SAGE_TEXT = "#456052"


def paw(x: float, y: float, scale: float, opacity: float) -> str:
    return (
        f'<g transform="translate({x} {y}) scale({scale})" fill="{FOREST}" fill-opacity="{opacity}">'
        f'<ellipse cx="30" cy="38" rx="7.4" ry="9.6"/>'
        f'<ellipse cx="48" cy="31.5" rx="7.8" ry="10.2"/>'
        f'<ellipse cx="66" cy="38" rx="7.4" ry="9.6"/>'
        f'<path d="M48 49.5c-9.9 0-18.4 8.1-18.4 16.6 0 6.3 5.2 10.2 11.3 9.5 3.1-.4 5.4-1.6 7.1-1.6'
        f's4 1.2 7.1 1.6c6.1.7 11.3-3.2 11.3-9.5C66.4 57.6 57.9 49.5 48 49.5Z"/></g>'
    )


def build(name: str, w: int, h: int, variant: str, desc: str) -> str:
    # A scattered paw texture, deterministic so rebuilds do not churn the file.
    seed = sum(ord(c) for c in name)
    paws = []
    for i in range(9):
        px = ((seed * (i + 3) * 37) % 100) / 100 * w - 40
        py = ((seed * (i + 7) * 53) % 100) / 100 * h - 40
        scale = 0.5 + ((seed * (i + 2)) % 60) / 100
        rot = (seed * (i + 5)) % 60 - 30
        paws.append(
            f'<g transform="rotate({rot} {px + 48 * scale} {py + 48 * scale})">'
            + paw(px, py, scale, 0.05 if variant == "plain" else 0.07)
            + "</g>"
        )

    label = ""
    if variant == "labelled":
        box_w = min(w - 80, 620)
        box_h = 132
        bx, by = (w - box_w) / 2, (h - box_h) / 2
        size_text = f"PHOTO PLACEHOLDER \u00b7 {w}\u00d7{h}"
        label = (
            f'<g><rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" rx="14" '
            f'fill="#FAF7F1" fill-opacity="0.94" stroke="{SAGE}" stroke-width="1.5"/>'
            f'<text x="{w/2}" y="{by + 44}" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" '
            f'font-size="15" font-weight="700" letter-spacing="2.2" fill="{SAGE_TEXT}">{size_text}</text>'
            f'<text x="{w/2}" y="{by + 84}" text-anchor="middle" font-family="Georgia, serif" '
            f'font-size="23" fill="{FOREST}">{html.escape(desc)}</text>'
            f'<text x="{w/2}" y="{by + 111}" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" '
            f'font-size="13" fill="{SAGE_TEXT}">Columbia Animal Hospital \u00b7 replace before launch</text></g>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-hidden="true">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{SAGE_PALE}"/><stop offset="0.55" stop-color="{CREAM}"/>'
        f'<stop offset="1" stop-color="{SAGE_PALE}"/></linearGradient></defs>'
        f'<rect width="{w}" height="{h}" fill="url(#g)"/>'
        + "".join(paws)
        + f'<rect x="0.75" y="0.75" width="{w-1.5}" height="{h-1.5}" fill="none" '
        f'stroke="{TAN}" stroke-opacity="0.45" stroke-width="1.5"/>'
        + label
        + "</svg>\n"
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (w, h, variant, desc) in SLOTS.items():
        # A slot that already holds a real photograph is left alone — regenerating
        # a placeholder beside it would leave an orphan file and invite confusion.
        real = next((f for f in OUT.glob(f"{name}.*") if f.suffix != ".svg"), None)
        if real:
            print(f"    {name + '.svg':<36} skipped — {real.name} is in place")
            continue
        path = OUT / f"{name}.svg"
        path.write_text(build(name, w, h, variant, desc), encoding="utf-8")
        total += path.stat().st_size
        print(f"    {path.name:<36} {w}x{h:<6} {variant:<9} {path.stat().st_size/1024:5.1f} kB")
    print(f"\n{len(SLOTS)} placeholders, {total/1024:.0f} kB total")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:      # output piped into head/less
        raise SystemExit(0)
