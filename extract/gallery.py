"""Rescue the period-gallery photographs from the old sitemap and attach each
one to the ballet its caption names."""
import re, json, html, pathlib, time, hashlib, urllib.request, unicodedata

ROOT = pathlib.Path(__file__).parent
IMGDIR = ROOT.parent / "assets" / "images"
IMGDIR.mkdir(parents=True, exist_ok=True)

xml = (ROOT / "sitemap.xml").read_text()
recs = []
for b in re.findall(r"<image:image>(.*?)</image:image>", xml, re.S):
    g = lambda t: (re.search(rf"<image:{t}>(.*?)</image:{t}>", b, re.S) or [None, ""])[1]
    loc = g("loc").strip()
    if loc:
        recs.append({"loc": loc, "title": html.unescape(g("title")).strip(),
                     "caption": html.unescape(g("caption")).strip()})

manifest = {m["src"]: m for m in json.loads((ROOT / "image-manifest.json").read_text())}

# download anything new
for i, r in enumerate(recs, 1):
    src = r["loc"].split("?")[0]
    if src in manifest:
        r["file"] = manifest[src]["file"]
        continue
    fn = f"g{hashlib.md5(src.encode()).hexdigest()[:8]}.jpg"
    dest = IMGDIR / fn
    if not dest.exists():
        try:
            req = urllib.request.Request(src + "?format=2500w", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                dest.write_bytes(resp.read())
            time.sleep(0.15)
        except Exception as e:
            print("  FAIL", src, e)
            continue
    r["file"] = fn

recs = [r for r in recs if r.get("file")]
print(f"{len(recs)} gallery images available")

# ---- match caption -> work ----
data = json.loads((ROOT.parent / "site-data.json").read_text())
works = data["works"]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s)


ABBREV = {"mbms": "My Brother, My Sisters", "r&j": "Romeo and Juliet",
          "sideshow": "Side Show"}

# longest names first so "Romeo and Juliet pas de deux" wins over "Romeo and Juliet"
ordered = sorted(works, key=lambda w: -len(w["name"]))

attached = 0
for r in recs:
    text = norm(r["caption"] + " " + r["title"])
    for k, v in ABBREV.items():
        if k in (r["caption"] or "").lower():
            text += " " + norm(v)
    hit = None
    for w in ordered:
        n = norm(w["name"])
        if len(n) < 4:
            continue
        if re.search(rf"\b{re.escape(n)}\b", text):
            hit = w
            break
    if not hit:
        continue
    if any(im["file"] == r["file"] for im in hit["images"]):
        continue
    hit["images"].append({"file": r["file"], "caption": r["caption"], "dims": ""})
    attached += 1

print(f"attached {attached} photographs to works")
(ROOT.parent / "site-data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

withimg = sum(1 for w in works if w["images"])
print(f"works with at least one image: {withimg}/{len(works)}")
for w in works:
    if len(w["images"]) >= 2:
        print(f'   {len(w["images"])}  {w["name"]}')
