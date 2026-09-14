#!/usr/bin/env bash
# Point every absolute URL at the live domain, then rebuild.
#
#     ./tools/set-domain.sh https://www.columbiaanimalhospital.net
#
# Canonical tags, Open Graph, Twitter cards, JSON-LD, the sitemap and robots.txt
# all derive from one value in src/data.json, so this is a single edit plus a
# build. Link previews cache hard — re-scrape after deploying.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: $0 https://example.com" >&2
  exit 64
fi

DOMAIN="${1%/}"
case "$DOMAIN" in
  https://*) ;;
  *) echo "error: the domain must start with https:// — scrapers reject the rest" >&2; exit 65 ;;
esac

cd "$(dirname "$0")/.."

python3 - "$DOMAIN" <<'PY'
import json, pathlib, sys
domain = sys.argv[1]
p = pathlib.Path("src/data.json")
data = json.loads(p.read_text())
old = data["site"]["url"]
data["site"]["url"] = domain
data["site"]["ogImage"] = f"{domain}/assets/img/og-image.png"
p.write_text(json.dumps(data, indent=2) + "\n")
print(f"  site.url   {old}  ->  {domain}")
print(f"  og:image   {data['site']['ogImage']}")
PY

python3 tools/build.py
echo
echo "Done. Verify the card at https://developers.facebook.com/tools/debug/ after deploying."
