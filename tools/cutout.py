#!/usr/bin/env python3
"""Remove a photograph's background, leaving the subject on transparency.

    pip install "rembg[cpu]"
    python3 tools/cutout.py incoming/hero-care.png
    python3 tools/cutout.py photo.jpg --out incoming/svc-grooming.png

Studio photographs on a white sweep look like a pasted-on box when they sit in a
page with a coloured ground. Cutting the background away lets the subject stand
directly on the design's own colour.

Settings are the ones that held up on the three-dog hero: the isnet-general-use
model with alpha matting, which keeps fur edges intact where a plain threshold
key leaves a white fringe — most visible on a black ear against a light
background. The result is trimmed to its alpha bounding box so no empty margin
is carried around, then handed to tools/photos.py to size and encode.

The model is ~179 MB and is downloaded on first run.
"""
import argparse
import pathlib
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Cut a subject out of its background.")
    ap.add_argument("source", type=pathlib.Path, help="image to process")
    ap.add_argument("--out", type=pathlib.Path, help="output PNG (default: <source>-cutout.png)")
    ap.add_argument("--model", default="isnet-general-use",
                    help="rembg model (default: isnet-general-use)")
    ap.add_argument("--no-trim", action="store_true",
                    help="keep the original canvas instead of trimming to the subject")
    args = ap.parse_args()

    if not args.source.exists():
        sys.exit(f"cutout: {args.source} does not exist")
    try:
        from rembg import new_session, remove
    except ImportError:
        sys.exit('cutout: rembg is required — pip install "rembg[cpu]"')
    from PIL import Image

    out_path = args.out or args.source.with_name(args.source.stem + "-cutout.png")
    src = Image.open(args.source).convert("RGBA")
    print(f"  in   {args.source}  {src.size[0]}x{src.size[1]}")

    result = remove(
        src,
        session=new_session(args.model),
        alpha_matting=True,
        alpha_matting_foreground_threshold=250,
        alpha_matting_background_threshold=15,
        alpha_matting_erode_size=8,
    )

    if not args.no_trim:
        bbox = result.getchannel("A").getbbox()
        if bbox and bbox != (0, 0, *result.size):
            result = result.crop(bbox)
            print(f"  trim {bbox}  ->  {result.size[0]}x{result.size[1]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path, optimize=True)

    hist = result.getchannel("A").histogram()
    print(f"  out  {out_path}  {out_path.stat().st_size / 1024:.0f} kB")
    print(f"       {hist[255]:,} opaque · {hist[0]:,} transparent · "
          f"{sum(hist[1:255]):,} feathered edge pixels")
    print("\n  Check the edges against a DARK ground before trusting it — a white")
    print("  fringe is invisible on white and obvious on forest green.")
    print("  Then size and encode it:  python3 tools/photos.py import")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
