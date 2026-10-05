import re, json, sys, pathlib, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import facets
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
HTML = ROOT / "html"

NAV = {"kenneth macmillan", "the ballets", "information", "the man, the choreographer",
       "his life, his work", "an online resource", "enter"}

FIELD_RE = re.compile(r"^(" + facets.FIELD_PATTERN + r")\s*:\s*(.+)$", re.I)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def parse_page(f):
    raw = f.read_text()
    soup = BeautifulSoup(raw, "lxml")
    for bad in soup(["script", "style", "noscript"]):
        bad.decompose()
    title = soup.title.get_text(strip=True).replace("— Kenneth MacMillan", "").strip() if soup.title else ""
    main = soup.select_one("#page, main, #content") or soup.body
    if main is None:
        return None

    paras, seen = [], set()
    for el in main.select("p,h1,h2,h3,h4,li,blockquote"):
        if el.find(["p", "h1", "h2", "h3", "h4"]):
            continue
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if not t or t.lower() in NAV or t.lower() in seen:
            continue
        seen.add(t.lower())
        paras.append(t)

    credits, body, year = {}, [], None
    for t in paras:
        m = FIELD_RE.match(t)
        if m and m.group(2).strip():
            credits[facets.canon_field(m.group(1))] = m.group(2).strip()
        elif re.fullmatch(r"(19|20)\d{2}", t):
            year = year or int(t)
        else:
            body.append(t)

    imgs = []
    for img in main.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if not src or "universal" in src:
            continue
        cap = facets.image_caption(img)
        imgs.append({"src": src.split("?")[0],
                     "alt": facets.clean_caption(img.get("alt")),
                     "caption": cap, "dims": img.get("data-image-dimensions", "")})

    return {"slug": f.stem, "title": title, "year": year, "credits": credits,
            "body": body, "images": imgs,
            "embeds": sorted(set(re.findall(
                r'(?:src|href)="(https?://[^"]*(?:youtube|youtu\.be|vimeo|soundcloud)[^"]*)"', raw)))}


parsed = {}
for f in sorted(HTML.glob("*.html")):
    p = parse_page(f)
    if p:
        parsed[f.stem] = p

by_title = {}
for p in parsed.values():
    by_title.setdefault(norm(p["title"]), []).append(p)

catalogue = json.loads((ROOT / "catalogue.json").read_text())
INDEX_PAGES = {"when-where", "the-ballets-1960-", "the-ballets-1", "the-ballets-1970-", "the-ballets-1977-1992"}

works, unmatched = [], []
used = set()
for c in catalogue:
    slug = c["slug"]
    p = None
    if slug in parsed and slug not in INDEX_PAGES:
        p = parsed[slug]
    else:
        cands = [x for x in by_title.get(norm(c["name"]), []) if x["slug"] not in INDEX_PAGES]
        # prefer one not already used, and with most content
        cands = sorted(cands, key=lambda x: (x["slug"] in used, -sum(len(b.split()) for b in x["body"])))
        if cands:
            p = cands[0]
    if not p:
        unmatched.append(c)
        continue
    used.add(p["slug"])
    works.append({
        "name": c["name"], "period": c["period"], "order": c["order"],
        "slug": p["slug"], "page_title": p["title"], "year": p["year"],
        "credits": p["credits"], "body": p["body"], "images": p["images"],
        "embeds": p["embeds"], "words": sum(len(b.split()) for b in p["body"]),
    })

for w in works:
    fp = w["credits"].get("First Performance", "")
    m = re.search(r"((?:18|19|20)\d{2})", fp)
    if m and not w["year"]:
        w["year"] = int(m.group(1))

(ROOT / "works.json").write_text(json.dumps(works, indent=2, ensure_ascii=False))

# non-ballet editorial pages
essay_slugs = {w["slug"] for w in works} | INDEX_PAGES
essays = [p for s, p in parsed.items() if s not in essay_slugs
          and sum(len(b.split()) for b in p["body"]) > 120]
essays.sort(key=lambda p: -sum(len(b.split()) for b in p["body"]))
(ROOT / "essays.json").write_text(json.dumps(essays, indent=2, ensure_ascii=False))

print(f"WORKS matched: {len(works)}/{len(catalogue)}   unmatched: {len(unmatched)}")
if unmatched:
    for u in unmatched:
        print("   MISSING:", u["name"])
print(f"\nwith credits: {sum(1 for w in works if w['credits'])}")
print(f"with essay >200w: {sum(1 for w in works if w['words']>200)}")
print(f"total work words: {sum(w['words'] for w in works):,}   images: {sum(len(w['images']) for w in works)}")
print(f"\nEDITORIAL PAGES: {len(essays)}")
for e in essays[:22]:
    print(f"   {sum(len(b.split()) for b in e['body']):>5}w  {e['slug']:<34} {e['title'][:44]}")
