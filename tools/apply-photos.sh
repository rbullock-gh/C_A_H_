#!/usr/bin/env bash
# Swap placeholder SVGs for real photographs in one pass.
#
#     1. Drop real photos into assets/img/ using the placeholder's basename,
#        keeping your own extension:  vet-loper.jpg, svc-surgery.webp, ...
#     2. ./tools/apply-photos.sh
#
# Every reference in src/ is rewritten from <name>.svg to <name>.<your ext>, the
# placeholder is deleted, and the site is rebuilt. Run it as often as photos
# arrive — it only touches slots that now have a real file.
set -euo pipefail
cd "$(dirname "$0")/.."

shopt -s nullglob
swapped=0

for real in assets/img/*.jpg assets/img/*.jpeg assets/img/*.png assets/img/*.webp assets/img/*.avif; do
  base="$(basename "${real%.*}")"
  ext="${real##*.}"
  placeholder="assets/img/${base}.svg"

  # Skip files that were never placeholder slots (the logo, the share card).
  [ -f "$placeholder" ] || continue

  echo "  ${base}.svg  ->  ${base}.${ext}"
  grep -rl "${base}\.svg" src/ | while read -r f; do
    sed -i "s|${base}\.svg|${base}.${ext}|g" "$f"
  done
  rm "$placeholder"
  swapped=$((swapped + 1))
done

if [ "$swapped" -eq 0 ]; then
  echo "No real photos found. Drop files into assets/img/ named after the"
  echo "placeholders they replace — see docs/PHOTO-CHECKLIST.md."
  exit 0
fi

echo
python3 tools/build.py
echo
echo "${swapped} photo(s) applied. Now run: python3 tools/check.py --browser"
