#!/usr/bin/env python3
"""Import real photographs into the site's image slots.

    python3 tools/photos.py list              what each slot needs
    python3 tools/photos.py import [DIR]      process everything in DIR (default: incoming/)
    python3 tools/photos.py credits           rewrite docs/PHOTO-CREDITS.md

Drop files into incoming/ named after the slot they fill — hero-care.jpg,
svc-surgery.png, why-exam.webp — and run `import`. Each photo is cropped to the
slot's aspect ratio, resized to its exact dimensions, encoded as WebP, written
to assets/img/, and every reference in src/ is rewritten from the placeholder.

Why this exists rather than a plain copy: a 4000x3000 phone photo dropped
straight in would ship six megabytes and shift the layout, because the markup
declares the placeholder's width and height. Cropping to the declared ratio
keeps those attributes honest and keeps Core Web Vitals intact.

Attribution: put a sidecar .txt next to the photo with the credit line
(photographer, source, licence) and it is carried into docs/PHOTO-CREDITS.md.
Stock photography must be licensed for commercial use — record where each image
came from, because "it was on the internet" is not a licence.
"""
import importlib.util
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
INCOMING = ROOT / "incoming"
CREDITS = ROOT / "docs" / "PHOTO-CREDITS.md"
LEDGER = ROOT / "src" / "photo-credits.json"
SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".tif", ".tiff", ".heic"}


def slots() -> dict:
    spec = importlib.util.spec_from_file_location("mp", ROOT / "tools" / "make-placeholders.py")
    mp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mp)
    return mp.SLOTS


def require_pillow():
    try:
        from PIL import Image, ImageOps  # noqa: F401
    except ImportError:
        sys.exit("photos: Pillow is required — pip install Pillow")
    from PIL import Image, ImageOps
    return Image, ImageOps


def cmd_list() -> int:
    print("Image slots\n")
    print(f"  {'slot':<30} {'size':<12} {'status':<12} what it needs")
    print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*46}")
    for name, (w, h, variant, desc) in slots().items():
        real = next((p for p in IMG.glob(f"{name}.*") if p.suffix != ".svg"), None)
        status = f"real ({real.suffix.lstrip('.')})" if real else "placeholder"
        print(f"  {name:<30} {f'{w}x{h}':<12} {status:<12} {desc}")
    print(f"\n  Drop files into {INCOMING.relative_to(ROOT)}/ named after the slot, then:")
    print("      python3 tools/photos.py import")
    return 0


def cmd_import(directory: pathlib.Path) -> int:
    Image, ImageOps = require_pillow()
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created {directory.relative_to(ROOT)}/ — drop photos in there and run this again.")
        print("Name each file after the slot it fills. `python3 tools/photos.py list` shows them.")
        return 0

    catalogue = slots()
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
    sources = [p for p in sorted(directory.iterdir())
               if p.is_file() and p.suffix.lower() in SUFFIXES]
    if not sources:
        print(f"No images found in {directory.relative_to(ROOT)}/.")
        print("Supported: " + ", ".join(sorted(s.lstrip('.') for s in SUFFIXES)))
        return 0

    done, skipped = 0, []
    for src in sources:
        slot = src.stem
        if slot not in catalogue:
            skipped.append(f"{src.name} — no slot called '{slot}'")
            continue
        w, h, _variant, desc = catalogue[slot]

        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)          # honour the camera's rotation
            # Cut-outs arrive with an alpha channel. Flattening them to RGB would
            # silently paint the transparency black, so keep it when it is there.
            transparent = im.mode in ("RGBA", "LA") or (
                im.mode == "P" and "transparency" in im.info)
            im = im.convert("RGBA" if transparent else "RGB")
            before = im.size
            # crop to the slot's ratio from the centre, then resize to exactly it
            im = ImageOps.fit(im, (w, h), method=Image.LANCZOS, centering=(0.5, 0.42))
            out = IMG / f"{slot}.webp"
            im.save(out, "WEBP", quality=82, method=6)

        placeholder = IMG / f"{slot}.svg"
        if placeholder.exists():
            placeholder.unlink()
        for page in ROOT.joinpath("src").rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            if f"{slot}.svg" in text:
                page.write_text(text.replace(f"{slot}.svg", f"{slot}.webp"), encoding="utf-8")

        credit = src.with_suffix(".txt")
        ledger[slot] = {
            "file": f"{slot}.webp",
            "describes": desc,
            "credit": credit.read_text(encoding="utf-8").strip() if credit.exists() else "",
        }
        kb = out.stat().st_size / 1024
        alpha = " alpha" if transparent else ""
        print(f"  {slot:<30} {before[0]}x{before[1]} -> {w}x{h}{alpha}  {kb:6.1f} kB"
              + ("" if ledger[slot]["credit"] else "   (no credit recorded)"))
        done += 1

    for s in skipped:
        print(f"  skipped: {s}")
    if not done:
        return 0

    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    write_credits(ledger, catalogue)
    print(f"\n{done} photo(s) imported. Now run:")
    print("    python3 tools/build.py && python3 tools/check.py --browser")
    return 0


def write_credits(ledger: dict, catalogue: dict) -> None:
    lines = [
        "# Photo credits",
        "",
        "Every photograph on this site, where it came from, and under what licence.",
        "",
        "Generated by `tools/photos.py` — record credits by putting a `.txt` sidecar next to",
        "each photo in `incoming/` before importing it.",
        "",
        "> **Stock photography must be licensed for commercial use.** Unsplash, Pexels and",
        "> Pixabay all permit it without attribution, but keep the record anyway: a licence you",
        "> cannot evidence is a licence you do not have. Photographs of identifiable people need",
        "> a model release; photographs of a client's pet need the client's permission.",
        "",
        "| Slot | File | Shows | Credit / licence |",
        "|---|---|---|---|",
    ]
    for slot in catalogue:
        entry = ledger.get(slot)
        if not entry:
            continue
        credit = entry["credit"] or "**not recorded — add before launch**"
        lines.append(f"| `{slot}` | `{entry['file']}` | {entry['describes']} | {credit} |")

    missing = [s for s in catalogue if s not in ledger]
    if missing:
        lines += ["", "## Still on placeholders", "",
                  "These slots have no real photograph yet:", ""]
        lines += [f"- `{s}` — {catalogue[s][3]}" for s in missing]
    lines.append("")
    CREDITS.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {CREDITS.relative_to(ROOT)} updated")


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        return cmd_list()
    if cmd == "import":
        target = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else INCOMING
        return cmd_import(target if target.is_absolute() else ROOT / target)
    if cmd == "credits":
        ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {}
        write_credits(ledger, slots())
        return 0
    sys.exit(f"photos: unknown command {cmd!r} — try list, import or credits")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:      # output piped into head/less
        raise SystemExit(0)
