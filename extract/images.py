import json, re, sys, pathlib, time, urllib.request, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import facets
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
OUT = ROOT.parent / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# gather every image reference across the whole crawl
seen = {}
for f in sorted((ROOT / "html").glob("*.html")):
    soup = BeautifulSoup(f.read_text(), "lxml")
    for img in soup.find_all("img"):
        src = (img.get("data-src") or img.get("src") or "").split("?")[0]
        if not src.startswith("http") or "universal" in src or "squarespace-cdn" not in src:
            continue
        cap = facets.image_caption(img)
        rec = seen.setdefault(src, {"src": src, "captions": set(), "pages": set(),
                                    "dims": img.get("data-image-dimensions", "")})
        if cap:
            rec["captions"].add(cap)
        alt = facets.clean_caption(img.get("alt"))
        if alt:
            rec["captions"].add(alt)
        rec["pages"].add(f.stem)

print(f"{len(seen)} unique images")

manifest = []
for i, (src, rec) in enumerate(sorted(seen.items()), 1):
    tail = src.rstrip("/").split("/")[-1]
    ext = ".jpg"
    for e in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if tail.lower().endswith(e):
            ext = e if e != ".jpeg" else ".jpg"
            tail = tail[: -len(e)]
            break
    name = re.sub(r"[^A-Za-z0-9_-]+", "-", urllib.parse.unquote(tail))[:70].strip("-")
    fn = f"{hashlib.md5(src.encode()).hexdigest()[:6]}-{name or 'img'}{ext}"
    dest = OUT / fn
    if not dest.exists():
        try:
            req = urllib.request.Request(src + "?format=2500w",
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                dest.write_bytes(r.read())
            time.sleep(0.15)
        except Exception as e:
            print("  FAIL", src, e)
            continue
    manifest.append({
        "file": fn, "src": src, "dims": rec["dims"],
        "caption": max(rec["captions"], key=len) if rec["captions"] else "",
        "captions": sorted(rec["captions"]),
        "pages": sorted(rec["pages"]),
        "bytes": dest.stat().st_size,
    })
    if i % 25 == 0:
        print(f"  {i}/{len(seen)}")

(ROOT / "image-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
tot = sum(m["bytes"] for m in manifest)
print(f"\ndownloaded {len(manifest)} images, {tot/1e6:.1f} MB")
print(f"with captions: {sum(1 for m in manifest if m['caption'])}")
