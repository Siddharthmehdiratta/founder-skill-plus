#!/bin/sh
# Builds the website (site/, Next.js) into docs/ for GitHub Pages.
# The app pages (builder, guide, review analysis, sample reports) live in site/public and are copied as-is.
set -e
cd "$(dirname "$0")/.."
python3 tools/app_chrome.py
cd site
[ -d node_modules ] || npm install --no-audit --no-fund
rm -rf out .next
NEXT_TELEMETRY_DISABLED=1 PAGES_BASE=/founder-skill-plus NEXT_PUBLIC_BASE=/founder-skill-plus npx next build
cd ..
rm -rf docs && cp -r site/out docs && touch docs/.nojekyll
python3 - <<'PY'
# sitemap.xml: one entry per page folder (submit it in Google Search Console).
import os
base = "https://siddharthmehdiratta.github.io/founder-skill-plus/"
pages = sorted(os.path.relpath(d, "docs").replace(os.sep, "/") for d, _, fs in os.walk("docs") if "index.html" in fs and "_next" not in d and "404" not in d and "_not-found" not in d)
urls = "".join(f"<url><loc>{base}{'' if p == '.' else p + '/'}</loc></url>" for p in pages)
open("docs/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
PY
echo "built docs/"
