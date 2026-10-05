"""Final clean dataset: strips site chrome, normalises names/slugs, derives facets."""
import json, re, sys, collections, pathlib, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import facets

ROOT = pathlib.Path(__file__).parent
works = json.loads((ROOT / "works.json").read_text())
essays = json.loads((ROOT / "essays.json").read_text())

# The ballet Different Drummer (1984) was matched to the page about Jann Parry's
# biography of the same name; both pages carry the identical <title>.
_pages = {e["slug"]: e for e in essays}
for w in works:
    if w["name"].lower() == "different drummer" and w["slug"] == "new-page":
        src = _pages.get("different-drummer")
        if src:
            w.update({k: src[k] for k in ("slug", "credits", "body", "images", "embeds")})
            w["year"] = src.get("year") or 1984
# MacMillan choreographed the Venusberg bacchanale twice, in 1955 for Ralph
# Koltai's production and again in 1984 for Yolanda Sonnabend's. The old site
# kept a page for each but its 1977-92 index linked both entries to the 1955
# page, so the later work was invisible. Assign each catalogue entry the page
# whose date matches its period.
for w in works:
    if w["name"].lower().startswith(("tannh", "tannha")):
        want = "tannhuser-1" if w["period"] == "1977 - 1992" else "tannhuser"
        src = _pages.get(want) if want != w["slug"] else None
        if src:
            w.update({k: src[k] for k in ("slug", "credits", "body", "images", "embeds")})
            w["year"] = src.get("year")

manifest = json.loads((ROOT / "image-manifest.json").read_text())
by_src = {m["src"]: m for m in manifest}

# --- chrome detection: lines present on (nearly) every page ---
counts = collections.Counter()
allpages = works + essays
for x in allpages:
    for b in set(x["body"]):
        counts[b] += 1
CHROME = {t for t, k in counts.items() if k >= len(allpages) * 0.9}
CHROME |= {"© The MacMillan Estate unless otherwise stated."}


def clean_body(body, title):
    out = []
    tnorm = re.sub(r"\s+", " ", title).strip().lower()
    for b in body:
        t = re.sub(r"\s+", " ", b).strip()
        if not t or t in CHROME:
            continue
        if t.lower() == tnorm or t.lower() == tnorm.rstrip("0123456789 "):
            continue
        if re.fullmatch(r"(19)\d{2}\s*[-–]\s*(19)\d{2}", t):
            continue
        if re.fullmatch(r"\W{0,3}", t):
            continue
        out.append(t)
    # drop leading duplicate of the title
    while out and out[0].lower().startswith(tnorm[:18]) and len(out[0]) < len(title) + 12:
        out.pop(0)
    return out


def slugify(s, drop_parens=True):
    if drop_parens:
        s = re.sub(r"\s*\(.*?\)", "", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "work"


def pick_images(imgs):
    out, seen = [], set()
    for i in imgs:
        m = by_src.get(i["src"])
        if not m or m["file"] in seen:
            continue
        seen.add(m["file"])
        out.append({"file": m["file"], "caption": i["caption"] or m["caption"], "dims": m["dims"]})
    return out


# ---------- works ----------
# The period index pages list a few works twice; the same source page under the
# same title is one work, whereas MacMillan's genuine re-stagings (Requiem 1976
# and 1986, three Sleeping Beauties) have separate source pages and must survive.
deduped, key_seen = [], set()
for w in works:
    key = (w["slug"], re.sub(r"\s+", " ", w["name"]).strip().lower())
    if key in key_seen:
        continue
    key_seen.add(key)
    deduped.append(w)
works = deduped

out_works, slugs = [], set()
for w in works:
    name = re.sub(r"\s*(19|20)\d{2}\s*$", "", w["name"]).strip()
    name = re.sub(r"\s+", " ", name)
    slug = slugify(name)
    if slug in slugs:
        yr = w["year"] or (facets.parse_premiere(w["credits"].get("First Performance", "")) or "")[:4]
        if yr:
            slug = f"{slug}-{yr}"
    base, n = slug, 2
    while slug in slugs:
        slug = f"{base}-{n}"; n += 1
    slugs.add(slug)

    body = clean_body(w["body"], w["name"])
    out_works.append(facets.derive({
        "slug": slug, "name": name, "year": w["year"], "period": w["period"],
        "order": w["order"],
        "credits": w["credits"],
        "body": body,
        "words": sum(len(b.split()) for b in body),
        "images": pick_images(w["images"]),
        "embeds": w["embeds"],
        "old_slug": w["slug"],
    }))

out_works.sort(key=lambda w: (w["premiere"] or str(w["year"] or 9999), w["name"]))

# ---------- essays ----------
DROP = {"portland", "new-page-45", "tannhuser-1", "seven-deadly-sins", "different-drummer",
        "new-page-62", "az-of-ballets"}
TITLES = {
    "best-friends": "Biography",
    "director-of-the-royal-ballet-by-sir-peter-wright": "Director of the Royal Ballet",
    "new-page-2": "MacMillan and his Designers",
    "new-page-3": "Agent Provocateur",
    "new-page-1": "Kiss to the Beat of Four",
    "inner-turmoil-inner-strength": "Inner Turmoil, Inner Strength",
    "maker-of-dancer": "Maker of Dances",
    "our-story": "An Introduction",
    "interview": "Interview",
    "notating-the-work": "Notating the Work",
    "licensing-the-work": "Licensing the Work",
    "acknowledgements": "Credits and Thanks",
    "media-1": "Articles, Books and Media",
    "media-clips": "Media Clips",
    "subscribe": "Subscribe",
}
out_essays = []
for e in essays:
    if e["slug"] in DROP:
        continue
    title = TITLES.get(e["slug"], e["title"])
    body = clean_body(e["body"], title)
    # short pages are kept only when curated: licensing and contact matter to the
    # estate however few words they run to
    if sum(len(b.split()) for b in body) < 90 and e["slug"] not in TITLES:
        continue
    out_essays.append({
        "slug": slugify(title), "title": title, "old_slug": e["slug"],
        "body": body, "words": sum(len(b.split()) for b in body),
        "images": pick_images(e["images"]), "embeds": e["embeds"],
    })
out_essays.sort(key=lambda e: -e["words"])

data = {"works": out_works, "essays": out_essays}
(ROOT.parent / "site-data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

fac = lambda key: collections.Counter(
    x for w in out_works for x in (w[key] if isinstance(w[key], list) else [w[key]]) if x)
print(f"WORKS {len(out_works)}  words {sum(w['words'] for w in out_works):,}  images {sum(len(w['images']) for w in out_works)}")
print(f"ESSAYS {len(out_essays)}  words {sum(e['words'] for e in out_essays):,}")
print(f"\nwith premiere date: {sum(1 for w in out_works if w['premiere'])}")
print(f"\nCOMPANIES ({len(fac('company'))}):")
for k, v in fac("company").most_common(14):
    print(f"   {v:>3}  {k}")
print(f"\nCOMPOSERS ({len(fac('composers'))}):")
for k, v in fac("composers").most_common(12):
    print(f"   {v:>3}  {k}")
print(f"\nDESIGNERS ({len(fac('designers'))}):")
for k, v in fac("designers").most_common(12):
    print(f"   {v:>3}  {k}")
print("\nsample:", json.dumps(out_works[-1], ensure_ascii=False)[:420])
