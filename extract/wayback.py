"""Recover production credits that were lost when the site moved to Squarespace.

Twenty works — Romeo and Juliet, Manon, Song of the Earth and most of 1960-66 —
kept their essays but lost their credits blocks in the migration. The pre-2016
site is archived, so the original data is recoverable rather than re-typed.
"""
import re, json, time, sys, pathlib, urllib.request, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
CACHE = ROOT / "wayback"
CACHE.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}

import facets
LABEL = re.compile(r"^(" + facets.FIELD_PATTERN + r")\s*:?\s*$", re.I)
INLINE = re.compile(r"^(" + facets.FIELD_PATTERN + r")\s*:\s*(.+)$", re.I)


def get(url, dest):
    if dest.exists():
        return dest.read_text(errors="replace")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                t = r.read().decode("utf-8", "replace")
            dest.write_text(t)
            time.sleep(1.0)
            return t
        except Exception as e:
            print("   retry", e)
            time.sleep(5 * (attempt + 1))
    return ""


cdx = get("http://web.archive.org/cdx/search/cdx?url=kennethmacmillan.com/ballets/all-works*"
          "&output=text&fl=original,timestamp&collapse=urlkey&filter=statuscode:200&limit=400",
          CACHE / "_cdx.txt")

seen, targets = set(), []
for line in cdx.splitlines():
    parts = line.split()
    if len(parts) != 2:
        continue
    url, ts = parts
    if "tmpl=" in url or "task=" in url or not url.endswith(".html"):
        continue
    key = url.split("/")[-1]
    if key in seen or key == "all-works.html":
        continue
    seen.add(key)
    targets.append((url, ts, key))

print(f"{len(targets)} archived work pages")


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)


recovered = {}
for i, (url, ts, key) in enumerate(targets, 1):
    raw = get(f"http://web.archive.org/web/{ts}id_/{url}", CACHE / f"{key}")
    if not raw:
        continue
    soup = BeautifulSoup(raw, "lxml")
    for b in soup(["script", "style"]):
        b.decompose()
    # every archived page carries the site masthead as its <h1>, so the work is
    # identified by the filename, which is the old site's own slug
    title = key[:-5].replace("-", " ")
    lines = [re.sub(r"\s+", " ", x).strip()
             for x in soup.get_text("\n", strip=True).split("\n")]
    lines = [x for x in lines if x]

    # stop at the sub-navigation, which repeats every ballet title
    for stop, x in enumerate(lines):
        if x.lower() in ("sub navigation", "all works"):
            lines = lines[:stop]
            break

    credits, cur = {}, None
    for x in lines:
        m = INLINE.match(x)
        if m and m.group(2).strip():
            credits[facets.canon_field(m.group(1))] = m.group(2).strip()
            cur = None
            continue
        if LABEL.match(x):
            cur = facets.canon_field(x)
            continue
        if cur:
            credits[cur] = (credits.get(cur, "") + " " + x).strip()
            cur = None
    if credits:
        recovered[norm(title)] = {"title": title, "url": url, "credits": credits}
    if i % 20 == 0:
        print(f"  {i}/{len(targets)}")

(ROOT / "wayback-credits.json").write_text(json.dumps(recovered, indent=2, ensure_ascii=False))
print(f"\nrecovered credits for {len(recovered)} works")

# ---- merge into site data ----
data = json.loads((ROOT.parent / "site-data.json").read_text())
filled, added_fields = 0, 0
for w in data["works"]:
    n = norm(w["name"])
    r = recovered.get(n)
    if not r and len(n) >= 10:
        # the archive's filenames keep subtitles that the display name drops,
        # e.g. song-of-the-earth-das-lied-von-der-erde
        hits = [v for k, v in recovered.items() if k.startswith(n) or n.startswith(k)]
        r = hits[0] if len(hits) == 1 else None
    if not r:
        continue
    before = len(w["credits"])
    for k, v in r["credits"].items():
        if not w["credits"].get(k):
            w["credits"][k] = v
            added_fields += 1
    if before == 0 and w["credits"]:
        filled += 1
        w["credits_source"] = "web.archive.org"

# facets were derived before these credits existed, so recompute them
for w in data["works"]:
    facets.derive(w)

(ROOT.parent / "site-data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
still = [w["name"] for w in data["works"] if not w["credits"]]
print(f"works given a credits block: {filled}")
print(f"individual fields added: {added_fields}")
print(f"still without credits: {len(still)} {still}")
