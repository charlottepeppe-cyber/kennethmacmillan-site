#!/bin/bash
# Full rebuild: crawled HTML -> clean data -> gallery photos -> static site.
# Re-crawling is only needed if the old Squarespace site changes.
set -e
cd "$(dirname "$0")"
PY=.venv/bin/python

echo "== 1. catalogue"   && $PY extract/catalogue.py  | tail -3
echo "== 2. merge"       && $PY extract/merge.py      | head -3
echo "== 3. clean data"  && $PY extract/build_data.py | head -3
echo "== 4. gallery"     && $PY extract/gallery.py    | head -3
echo "== 5. wayback"     && $PY extract/wayback.py    | tail -3
echo "== 6. corrections" && $PY extract/corrections.py | head -3
echo "== 7. site"        && $PY site/build.py
echo "== 8. report"      && $PY site/report.py
