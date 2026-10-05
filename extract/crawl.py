import re, time, pathlib, urllib.request, urllib.parse, gzip, io, json

ROOT = pathlib.Path(__file__).parent
HTML = ROOT / "html"
HTML.mkdir(exist_ok=True)
BASE = "https://www.kennethmacmillan.com"
SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".mp3", ".mp4")

seen, queue, assets = set(), ["/"], set()


def slug_of(path):
    s = path.strip("/").replace("/", "__") or "home"
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)[:150]


def fetch(path):
    req = urllib.request.Request(
        BASE + path,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "Accept-Encoding": "gzip"},
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        return data.decode("utf-8", "replace")


while queue:
    path = queue.pop(0)
    if path in seen:
        continue
    seen.add(path)
    f = HTML / (slug_of(path) + ".html")
    if f.exists():
        html = f.read_text()
    else:
        try:
            html = fetch(path)
        except Exception as e:
            print("FAIL", path, e)
            continue
        f.write_text(html)
        time.sleep(0.35)
    print(f"{len(seen):>3} {path}  ({len(html)//1024}kb)")
    for href in re.findall(r'href="(/[^"\'>]*)"', html):
        href = href.split("#")[0].split("?")[0]
        if not href or href in seen or href in queue:
            continue
        if href.lower().endswith(SKIP_EXT) or href.startswith(("/s/", "/static", "/api", "/config", "/universal", "/assets")):
            if href.lower().endswith(SKIP_EXT):
                assets.add(href)
            continue
        queue.append(href)

(ROOT / "crawled.json").write_text(json.dumps({"pages": sorted(seen), "assets": sorted(assets)}, indent=2))
print(f"\nDONE: {len(seen)} pages, {len(assets)} linked assets")
