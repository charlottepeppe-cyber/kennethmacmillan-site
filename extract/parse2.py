import re, json, pathlib
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).parent
HTML = ROOT / "html"
OUT = ROOT / "content"
OUT.mkdir(exist_ok=True)

NAV_NOISE = {
    "KENNETH MACMILLAN", "THE MAN, THE CHOREOGRAPHER", "THE BALLETS", "INFORMATION",
    "ENTER", "HIS LIFE, HIS WORK", "AN ONLINE RESOURCE",
}

pages = []

for f in sorted(HTML.glob("*.html")):
    soup = BeautifulSoup(f.read_text(), "lxml")
    for bad in soup(["script", "style", "noscript", "nav", "header", "footer"]):
        bad.decompose()

    title = ""
    if soup.title:
        title = soup.title.get_text(strip=True).replace(" — Kenneth MacMillan", "").strip()

    main = soup.select_one("#page, main, #content") or soup.body
    if main is None:
        continue

    # images
    imgs = []
    for img in main.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if not src or "squarespace.com/universal" in src:
            continue
        cap = ""
        for anc in img.parents:
            if anc is main:
                break
            c = anc.find(class_=re.compile("caption"))
            if c:
                cap = c.get_text(" ", strip=True)
                break
        imgs.append({
            "src": src.split("?")[0],
            "alt": (img.get("alt") or "").strip(),
            "caption": cap,
            "dims": img.get("data-image-dimensions", ""),
        })

    # text
    lines, seen = [], set()
    for el in main.select("h1,h2,h3,h4,p,li,blockquote"):
        if el.find(["h1", "h2", "h3", "h4", "p"]):
            continue
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if not t or t in NAV_NOISE or len(t) < 2:
            continue
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        if el.name.startswith("h"):
            lines.append("\n## " + t)
        elif el.name == "blockquote":
            lines.append("> " + t)
        else:
            lines.append(t)

    body = "\n\n".join(lines).strip()
    words = len(body.split())

    # video / audio embeds
    embeds = sorted({
        a for a in re.findall(r'(?:src|href)="(https?://[^"]*(?:youtube|youtu\.be|vimeo|soundcloud)[^"]*)"', f.read_text())
    })

    slug = f.stem
    md = f"# {title}\n\nSource: /{'' if slug=='home' else slug}\n\n{body}\n"
    if embeds:
        md += "\n## Embeds\n\n" + "\n".join("- " + e for e in embeds) + "\n"
    if imgs:
        md += f"\n## Images ({len(imgs)})\n\n" + "\n".join(
            f"- {i['src']}" + (f" — {i['caption'] or i['alt']}" if (i['caption'] or i['alt']) else "") for i in imgs
        ) + "\n"
    (OUT / f"{slug}.md").write_text(md)

    pages.append({
        "slug": slug, "title": title, "words": words,
        "images": imgs, "embeds": embeds,
    })

(ROOT / "pages.json").write_text(json.dumps(pages, indent=2))

tot_w = sum(p["words"] for p in pages)
tot_i = sum(len(p["images"]) for p in pages)
print(f"{len(pages)} pages | {tot_w:,} words | {tot_i} images | {sum(len(p['embeds']) for p in pages)} embeds\n")
for p in sorted(pages, key=lambda x: -x["words"])[:45]:
    print(f"  {p['words']:>6}w {len(p['images']):>3}i  {p['slug']:<42} {p['title'][:40]}")
