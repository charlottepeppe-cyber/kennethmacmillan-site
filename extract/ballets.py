import re, json, pathlib
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
HTML = ROOT / "html"

FIELDS = [
    "First performance", "Company", "Cast", "Music", "Design", "Designer",
    "Benesh notation score", "Video", "Libretto", "Scenario", "Lighting",
    "Costumes", "Revivals", "Other companies", "Duration", "Notes",
]
FIELD_RE = re.compile(r"^(" + "|".join(re.escape(f) for f in FIELDS) + r")\s*:\s*(.*)$", re.I)


def image_records(main):
    """Captions scoped to the image's own figure/block, not any ancestor."""
    out = []
    for img in main.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if not src or "universal" in src:
            continue
        cap = ""
        holder = img.find_parent("figure") or img.find_parent(class_=re.compile("sqs-block-image|image-block"))
        if holder:
            c = holder.find(class_=re.compile("caption"))
            if c:
                cap = re.sub(r"\s+", " ", c.get_text(" ", strip=True))
        out.append({
            "src": src.split("?")[0],
            "alt": (img.get("alt") or "").strip(),
            "caption": cap,
            "dims": img.get("data-image-dimensions", ""),
        })
    return out


ballets, other = [], []

for f in sorted(HTML.glob("*.html")):
    raw = f.read_text()
    soup = BeautifulSoup(raw, "lxml")
    for bad in soup(["script", "style", "noscript"]):
        bad.decompose()

    title = soup.title.get_text(strip=True).replace("— Kenneth MacMillan", "").strip() if soup.title else ""
    main = soup.select_one("#page, main, #content") or soup.body
    if main is None:
        continue

    paras = []
    for el in main.select("p,h1,h2,h3,h4,li,blockquote"):
        if el.find(["p", "h1", "h2", "h3", "h4"]):
            continue
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if t:
            paras.append(t)

    # de-dupe consecutive/global repeats while preserving order
    seen, clean = set(), []
    for t in paras:
        k = t.lower()
        if k in seen:
            continue
        seen.add(k)
        clean.append(t)

    credits, body, year = {}, [], None
    for t in clean:
        m = FIELD_RE.match(t)
        if m:
            key = m.group(1).strip().title()
            val = m.group(2).strip()
            if val:
                credits[key] = (credits.get(key, "") + " " + val).strip()
        elif re.fullmatch(r"(19|20)\d{2}", t) and year is None:
            year = int(t)
        elif t.lower() not in ("kenneth macmillan", "the ballets", "information", "the man, the choreographer"):
            body.append(t)

    imgs = image_records(main)
    embeds = sorted(set(re.findall(r'(?:src|href)="(https?://[^"]*(?:youtube|youtu\.be|vimeo|soundcloud)[^"]*)"', raw)))

    rec = {
        "slug": f.stem, "title": title, "year": year,
        "credits": credits, "body": body,
        "words": sum(len(b.split()) for b in body),
        "images": imgs, "embeds": embeds,
    }
    (ballets if "First Performance" in credits else other).append(rec)

# premiere date -> sortable
for b in ballets:
    fp = b["credits"].get("First Performance", "")
    m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+((?:18|19|20)\d{2})", fp)
    b["premiere"] = f"{m.group(3)}-{m.group(2)[:3]}-{m.group(1).zfill(2)}" if m else None
    ym = re.search(r"((?:18|19|20)\d{2})", fp)
    if ym and not b["year"]:
        b["year"] = int(ym.group(1))

ballets.sort(key=lambda b: (b["year"] or 9999, b["title"]))

(ROOT / "ballets.json").write_text(json.dumps(ballets, indent=2, ensure_ascii=False))
(ROOT / "other-pages.json").write_text(json.dumps(other, indent=2, ensure_ascii=False))

print(f"BALLETS: {len(ballets)}   OTHER PAGES: {len(other)}")
from collections import Counter
print("\ncredit fields:", Counter(k for b in ballets for k in b["credits"]).most_common())
print(f"\nyears {min(b['year'] for b in ballets if b['year'])}–{max(b['year'] for b in ballets if b['year'])}")
print(f"images on ballet pages: {sum(len(b['images']) for b in ballets)}\n")
for b in ballets:
    print(f"  {b['year']}  {b['title'][:38]:<38} {b['words']:>5}w {len(b['images'])}i  {b['credits'].get('Company','')[:34]}")
