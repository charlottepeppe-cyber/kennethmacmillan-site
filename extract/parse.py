import json, re, pathlib, html
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
RAW = ROOT / "raw"
OUT = ROOT / "content"
OUT.mkdir(exist_ok=True)

images = []
index = []


def block_text(el):
    parts = []
    for node in el.descendants:
        if node.name in ("h1", "h2", "h3", "h4"):
            t = node.get_text(" ", strip=True)
            if t:
                parts.append(("#" * int(node.name[1]) + " " + t))
        elif node.name == "p":
            t = node.get_text(" ", strip=True)
            if t:
                parts.append(t)
        elif node.name == "li":
            t = node.get_text(" ", strip=True)
            if t:
                parts.append("- " + t)
    return parts


for f in sorted(RAW.glob("*.json")):
    d = json.loads(f.read_text())
    coll = d.get("collection") or {}
    slug = f.stem
    title = coll.get("title") or slug
    url = coll.get("fullUrl", "/" + slug)
    soup = BeautifulSoup(d.get("mainContent") or "", "lxml")

    # images with captions
    page_imgs = []
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if not src:
            continue
        cap = ""
        fig = img.find_parent(["figure", "div"])
        if fig:
            c = fig.find(class_=re.compile("caption|image-caption"))
            if c:
                cap = c.get_text(" ", strip=True)
        rec = {
            "page": slug,
            "src": src.split("?")[0],
            "alt": img.get("alt", ""),
            "caption": cap,
            "dims": img.get("data-image-dimensions", ""),
        }
        page_imgs.append(rec)
        images.append(rec)

    # text
    lines = []
    seen = set()
    for el in soup.select("h1,h2,h3,h4,p,li"):
        t = el.get_text(" ", strip=True)
        t = re.sub(r"\s+", " ", t)
        if not t or t in seen:
            continue
        seen.add(t)
        if el.name.startswith("h"):
            lines.append("\n" + "#" * int(el.name[1]) + " " + t + "\n")
        elif el.name == "li":
            lines.append("- " + t)
        else:
            lines.append(t)

    # links
    links = []
    for a in soup.find_all("a", href=True):
        txt = a.get_text(" ", strip=True)
        if txt:
            links.append((txt, a["href"]))

    body = "\n\n".join(lines).strip()
    md = f"# {title}\n\nURL: {url}\n\n{body}\n"
    if links:
        md += "\n\n## Links\n\n" + "\n".join(f"- [{t}]({h})" for t, h in dict(links).items())
    if page_imgs:
        md += f"\n\n## Images ({len(page_imgs)})\n\n"
        md += "\n".join(f"- {i['src']} — {i['caption'] or i['alt']}" for i in page_imgs)
    (OUT / f"{slug}.md").write_text(md)
    index.append({"slug": slug, "title": title, "url": url, "words": len(body.split()), "images": len(page_imgs)})

(ROOT / "images.json").write_text(json.dumps(images, indent=2))
(ROOT / "index.json").write_text(json.dumps(index, indent=2))

print(f"{len(index)} pages, {len(images)} images, {sum(i['words'] for i in index)} words")
for i in sorted(index, key=lambda x: -x["words"]):
    print(f"  {i['words']:>6}w {i['images']:>4}img  {i['slug']}")
