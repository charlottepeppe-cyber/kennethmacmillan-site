import re, json, pathlib
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
HTML = ROOT / "html"

PERIODS = [
    ("when-where", "1953 - 1960"),
    ("the-ballets-1960-", "1960 - 1966"),
    ("the-ballets-1", "1966 - 1970"),
    ("the-ballets-1970-", "1970 - 1977"),
    ("the-ballets-1977-1992", "1977 - 1992"),
]

catalogue, order = [], 0
for slug, label in PERIODS:
    f = HTML / f"{slug}.html"
    if not f.exists():
        print("missing", slug)
        continue
    soup = BeautifulSoup(f.read_text(), "lxml")
    block = soup.select_one(".sqs-html-content")
    if not block:
        continue
    seen = set()
    for li in block.select("ul > li"):
        a = li.find("a", href=True)
        if not a:
            continue
        href = a["href"].split("#")[0].split("?")[0].strip("/")
        name = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
        if not href or not name or href in seen:
            continue
        seen.add(href)
        order += 1
        catalogue.append({"order": order, "name": name, "slug": href, "period": label})

(ROOT / "catalogue.json").write_text(json.dumps(catalogue, indent=2, ensure_ascii=False))

have = {f.stem for f in HTML.glob("*.html")}
missing = [c for c in catalogue if c["slug"] not in have]
print(f"{len(catalogue)} works in catalogue across {len(PERIODS)} periods")
for _, label in PERIODS:
    n = sum(1 for c in catalogue if c["period"] == label)
    print(f"  {label}: {n}")
if missing:
    print("\nNOT CRAWLED:", [(m['name'], m['slug']) for m in missing])
