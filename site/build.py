"""Static site generator for kennethmacmillan.com.

Reads site-data.json (produced by extract/build_data.py) and writes dist/.
"""
import json, re, shutil, html, pathlib, datetime, collections

ROOT = pathlib.Path(__file__).parent
PROJ = ROOT.parent
DIST = PROJ / "dist"
DATA = json.loads((PROJ / "site-data.json").read_text())
WORKS, ESSAYS = DATA["works"], DATA["essays"]

PERIODS = ["1953 - 1960", "1960 - 1966", "1966 - 1970", "1970 - 1977", "1977 - 1992"]
PERIOD_NOTE = {
    "1953 - 1960": "Early works for the Sadler's Wells Choreographic Group and Theatre Ballet.",
    "1960 - 1966": "The Royal Ballet years: The Invitation, Romeo and Juliet, Song of the Earth.",
    "1966 - 1970": "Director of the Ballet of the Deutsche Oper, Berlin.",
    "1970 - 1977": "Director of the Royal Ballet: Anastasia, Manon, Elite Syncopations.",
    "1977 - 1992": "Principal Choreographer: Mayerling, Isadora, The Judas Tree.",
}
NAV = [
    ("The Man, The Choreographer", "/the-man/"),
    ("The Ballets", "/ballets/"),
    ("Chronology", "/chronology/"),
    ("Information", "/information/"),
]
E = lambda s: html.escape(str(s or ""), quote=True)

YEARS = [w["display_year"] for w in WORKS if w["display_year"]]
YEAR_MIN, YEAR_MAX = min(YEARS), max(YEARS)

_ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
         "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def split_title(name):
    """Signature of this direction: the tail of the title in the accent colour.
    A trailing parenthetical is taken whole, so "Anastasia (3 act)" highlights
    the qualifier rather than the stray word "act)". A single-word title stays
    plain and lets the year carry the colour instead."""
    name = name.strip()
    if name.endswith(")") and "(" in name:
        head, _, tail = name.rpartition("(")
        if head.strip():
            return E(head.strip()) + ' <em>(' + E(tail) + "</em>"
    parts = name.split()
    if len(parts) < 2:
        return E(name)
    return E(" ".join(parts[:-1])) + " <em>" + E(parts[-1]) + "</em>"


def spell(n):
    if n < 20:
        w = _ONES[n]
    elif n % 10 == 0:
        w = _TENS[n // 10]
    else:
        w = f"{_TENS[n // 10]}-{_ONES[n % 10]}"
    return w[0].upper() + w[1:]


def page(title, body, desc="", active="", cls=""):
    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{E(t)}</a>'
        for t, h in NAV)
    foot_works = "".join(
        f'<li><a href="/ballets/?period={E(p)}">{E(p)}</a></li>' for p in PERIODS)
    foot_read = "".join(
        f'<li><a href="/the-man/{e["slug"]}/">{E(e["title"])}</a></li>' for e in ESSAYS[:6])
    return f"""<!doctype html>
<html lang="en" class="{cls}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Antonio:wght@200..600&family=Spectral:ital,wght@0,200;0,300;0,400;1,300&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="masthead__inner">
    <a class="wordmark" href="/"><span>Kenneth</span><span>MacMillan</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav class="nav" id="nav">{nav}</nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="shell">
    <div class="foot__grid">
      <div>
        <h3 class="tracked">The Ballets</h3>
        <ul>{foot_works}<li><a href="/chronology/">Full chronology</a></li></ul>
      </div>
      <div>
        <h3 class="tracked">Reading</h3>
        <ul>{foot_read}</ul>
      </div>
      <div>
        <h3 class="tracked">Information</h3>
        <ul>
          <li><a href="/information/licensing-the-work/">Licensing the work</a></li>
          <li><a href="/information/notating-the-work/">Notating the work</a></li>
          <li><a href="/information/credits-and-thanks/">Credits and thanks</a></li>
        </ul>
      </div>
    </div>
    <p class="foot__legal">© The MacMillan Estate unless otherwise stated. Images reproduced by
    courtesy of the Victoria &amp; Albert Museum, the Royal Opera House Collections and the
    photographers and archives credited throughout.</p>
  </div>
</footer>
<script src="/site.js" defer></script>
</body>
</html>"""


def prose(paras):
    out = []
    for p in paras:
        t = E(p)
        if len(p) < 70 and p.endswith(":"):
            out.append(f"<h2>{t}</h2>")
        elif p.startswith("“") or p.startswith("‘"):
            out.append(f"<p>{t}</p>")
        else:
            out.append(f"<p>{t}</p>")
    return "\n".join(out)


DIMS = json.loads((PROJ / "extract" / "dims.json").read_text())

# corrections.py may republish an image under a corrected filename; the download
# cache keeps the original name so it still mirrors the source archive
RENAMES = DATA.get("image_renames", {})


def img_url(fn):
    return "/images/" + RENAMES.get(fn, fn)


def figures(images, wide=False, eager=False, label=""):
    """Archive scans are mostly under 1000px wide, so a figure is capped at its
    own intrinsic width and never stretched to fill the column."""
    out = []
    for im in images:
        cap = f"<figcaption>{E(im['caption'])}</figcaption>" if im.get("caption") else ""
        wh = DIMS.get(im["file"])
        size = f' width="{wh[0]}" height="{wh[1]}"' if wh else ""
        style = f' style="--w:{wh[0]}px"' if wh else ""
        cls = "figure--wide" if wide else "figure--inline"
        load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
        out.append(
            f'<figure class="{cls}"{style}>'
            f'<img src="{E(img_url(im["file"]))}" alt="{E(im.get("caption") or label)}"'
            f'{size} {load} decoding="async">{cap}</figure>')
    return "\n".join(out)


def embeds(urls):
    out = []
    for u in urls:
        if "vimeo" in u or "youtube" in u:
            out.append(f'<div class="embed"><iframe src="{E(u)}" loading="lazy" '
                       f'allowfullscreen title="Video"></iframe></div>')
    return "\n".join(out)


def write(path, content):
    f = DIST / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content)


# ---------------------------------------------------------------- work pages
CREDIT_ORDER = ["First Performance", "Occasion", "Company", "Cast", "Music", "Lyrics",
                "Scenario", "Libretto", "Choreography", "Dance sequences",
                "Design", "Costumes", "Lighting", "Director", "Producer", "Screenplay",
                "Benesh Notation Score", "Video", "Television", "Cinema release", "Duration"]

def work_page(w, prev, nxt):
    meta = []
    if w["company"]:
        meta.append(f'<span class="tracked">{E(w["company"])}</span>')
    if w["venue"]:
        meta.append(f'<span class="tracked">{E(w["venue"])}</span>')

    rows = []
    for k in CREDIT_ORDER:
        v = w["credits"].get(k)
        if not v:
            continue
        label = "Design" if k == "Designer" else k
        rows.append(f"<dt>{E(label)}</dt><dd>{E(v)}</dd>")
    credits = ""
    if rows:
        credits = ('<section class="credits"><h2>Creation</h2><dl>'
                   + "".join(rows) + "</dl></section>")

    imgs = w["images"]
    lead = figures(imgs[:1], wide=True, eager=True, label=w["name"]) if imgs else ""
    rest = ""
    if len(imgs) > 1:
        cells = "".join(
            f'<div class="sp"><span class="n">PL. {n:02d}</span>'
            + figures([im], label=w["name"]) + '</div>'
            for n, im in enumerate(imgs[1:], 2))
        rest = f'<div class="plates">{cells}</div>' 

    pager = []
    if prev:
        pager.append(f'<a href="/ballets/{prev["slug"]}/"><span class="tracked">Previous</span>'
                     f'<strong>{E(prev["name"])}</strong></a>')
    if nxt:
        pager.append(f'<a class="to-end" href="/ballets/{nxt["slug"]}/">'
                     f'<span class="tracked">Next</span><strong>{E(nxt["name"])}</strong></a>')

    body = f"""
<section class="band">
  <div class="band__inner">
    <p class="tracked" style="color:inherit;opacity:.6;margin:0 0 1.5rem">
      <a href="/ballets/" style="text-decoration:none">The Ballets</a> &nbsp;/&nbsp; {E(w["period"])}</p>
    <h1>{split_title(w["name"])}</h1>
    <div class="band__meta">
      <span class="band__year">{E(w["display_year"] or "")}</span>
      {"".join(meta)}
    </div>
  </div>
</section>
<div class="shell">
  {lead}
  <article class="prose">
    {prose(w["body"])}
  </article>
  {rest}
  {embeds(w["embeds"])}
  {credits}
  <nav class="pager">{"".join(pager)}</nav>
</div>"""
    desc = (w["body"][0][:180] if w["body"] else f'{w["name"]}, a ballet by Kenneth MacMillan.')
    write(f'ballets/{w["slug"]}/index.html',
          page(f'{w["name"]} — Kenneth MacMillan', body, desc, "/ballets/"))


# ---------------------------------------------------------------- ballets index
def facet(key):
    vals = set()
    for w in WORKS:
        v = w[key]
        for x in (v if isinstance(v, list) else [v]):
            if x:
                vals.add(x)
    return sorted(vals)


def ballets_index():
    rows = []
    for w in WORKS:
        blob = " ".join(filter(None, [
            w["name"], w["company"], w["music"], w["design"],
            " ".join(w["cast"]), str(w["display_year"] or ""), w["venue"]])).lower()
        rows.append(
            f'<li data-period="{E(w["period"])}" data-company="{E(w["company"])}" '
            f'data-composer="{E("|".join(w["composers"]))}" '
            f'data-designer="{E("|".join(w["designers"]))}" '
            f'data-search="{E(blob)}">'
            f'<a href="/ballets/{w["slug"]}/">'
            f'<span class="yr">{E(w["display_year"] or "")}</span>'
            f'<span class="nm">{E(w["name"])}</span>'
            f'<span class="co">{E(w["company"])}</span></a></li>')

    def opts(name, values, label):
        o = "".join(f'<option value="{E(v)}">{E(v)}</option>' for v in values)
        return (f'<select data-filter="{name}" aria-label="Filter by {name}">'
                f'<option value="">All {label}</option>{o}</select>')

    body = f"""
<section class="band band--slim">
  <div class="band__inner">
    <p class="tracked" style="opacity:.6;margin:0 0 1.25rem">The Ballets</p>
    <h1>{spell(len(WORKS))} <em>works</em></h1>
    <div class="band__meta"><span class="tracked">{YEAR_MIN} &ndash; {YEAR_MAX}</span></div>
  </div>
</section>
<div class="shell">
  <div class="controls">
    <div class="controls__row">
      <input class="search" type="search" placeholder="Search titles, dancers, composers, designers…" aria-label="Search the ballets">
      {opts("period", PERIODS, "periods")}
      {opts("company", facet("company"), "companies")}
      {opts("composer", facet("composers"), "composers")}
      {opts("designer", facet("designers"), "designers")}
      <span class="count" data-count>{len(WORKS)} works</span>
    </div>
  </div>
  <ul class="works" data-works>
    {"".join(rows)}
  </ul>
  <p class="empty" hidden data-empty>No works match those filters.</p>
</div>"""
    write("ballets/index.html",
          page("The Ballets — Kenneth MacMillan", body,
               f"The complete catalogue of Kenneth MacMillan's {len(WORKS)} ballets, {YEAR_MIN}–{YEAR_MAX}, "
               "searchable by company, composer and designer.", "/ballets/", "wide"))


# ---------------------------------------------------------------- chronology
# Companies are grouped so the timeline can be read at a glance: the Sadler's
# Wells apprenticeship, the Berlin years, the long Royal Ballet spine.
COMPANY_GROUPS = [
    ("royal", "The Royal Ballet"),
    ("sadlers", "Sadler's Wells"),
    ("berlin", "Deutsche Oper, Berlin"),
    ("stuttgart", "Stuttgart Ballet"),
    ("abt", "American Ballet Theatre"),
    ("other", "Other companies"),
]


def company_group(c):
    c = c or ""
    if c.startswith("Sadler's Wells"):
        return "sadlers"
    if c.startswith("The Royal Ballet") or c == "The Royal Opera":
        return "royal"
    if c == "Ballet of the Deutsche Oper":
        return "berlin"
    if c == "Stuttgart Ballet":
        return "stuttgart"
    if c == "American Ballet Theatre":
        return "abt"
    return "other"


def chronology():
    by_year = collections.defaultdict(list)
    for w in WORKS:
        by_year[w["display_year"]].append(w)
    lo, hi = min(by_year), max(by_year)
    years = list(range(lo, hi + 1))
    peak = max(len(v) for v in by_year.values())

    counts = collections.Counter(company_group(w["company"]) for w in WORKS)
    key = "".join(
        f'<span class="tl-key__item" data-co="{k}">'
        f'<i class="tl-key__swatch"></i>{E(label)} '
        f'<b>{counts.get(k, 0)}</b></span>'
        for k, label in COMPANY_GROUPS if counts.get(k))

    # overview: one column per year, stacked in company colour, so the Berlin
    # years and the long Royal Ballet spine are legible before you read a word
    ov = []
    for y in years:
        ws = by_year.get(y, [])
        segs = "".join(
            f'<span class="tl-ov__seg" data-co="{company_group(w["company"])}"></span>'
            for w in ws)
        label = (f"{y}: " + ", ".join(w["name"] for w in ws)) if ws else f"{y}: no new work"
        ov.append(
            f'<a class="tl-ov__col" href="#y{y}" style="--n:{len(ws)}" '
            f'title="{E(label)}" aria-label="{E(label)}">'
            f'<span class="tl-ov__stack">{segs}</span>'
            f'<span class="tl-ov__yr">{str(y)[2:]}</span></a>')
    ov = "".join(ov)

    # spine: a row per year, era headings inserted where the period turns over
    rows, seen_era = [], set()
    for y in years:
        ws = by_year.get(y, [])
        era = ws[0]["period"] if ws else None
        if era and era not in seen_era:
            seen_era.add(era)
            n = sum(1 for w in WORKS if w["period"] == era)
            rows.append(
                f'<li class="tl__era"><h2>{E(era)}</h2>'
                f'<p>{E(PERIOD_NOTE.get(era, ""))}</p>'
                f'<span class="tracked">{n} works</span></li>')
        if not ws:
            rows.append(
                f'<li class="tl__year tl__year--empty" id="y{y}">'
                f'<span class="tl__yr">{y}</span>'
                f'<span class="tl__none">no new work</span></li>')
            continue
        chips = "".join(
            f'<li><a class="tl__work" data-co="{company_group(w["company"])}" '
            f'href="/ballets/{w["slug"]}/">'
            f'<span class="tl__nm">{E(w["name"])}</span>'
            f'<span class="tl__co">{E(w["company"] or "company not recorded")}</span></a></li>'
            for w in ws)
        rows.append(
            f'<li class="tl__year" id="y{y}"><span class="tl__yr">{y}</span>'
            f'<ul class="tl__works">{chips}</ul></li>')

    body = f"""
<section class="band band--slim">
  <div class="band__inner">
    <p class="tracked" style="opacity:.6;margin:0 0 1.25rem">Chronology</p>
    <h1>{lo} &ndash; <em>{hi}</em></h1>
    <div class="band__meta">
      <span class="tracked">Forty years of work</span>
      <span class="tracked">{len(WORKS)} ballets</span>
    </div>
  </div>
</section>
<div class="shell">
  <p class="lede measure" style="margin-block:clamp(2rem,5vw,3rem) 2rem">
    Every ballet in order of first performance. Each year is drawn to the number
    of works it holds, so the pace of the working life is visible: the crowded
    Sadler's Wells apprenticeship, the Berlin years, and the silences.</p>

  <div class="tl-key">{key}</div>

  <nav class="tl-ov" aria-label="Works per year, {lo} to {hi}"
       style="--peak:{peak};--cols:{len(years)}">{ov}</nav>

  <ol class="tl">{"".join(rows)}</ol>
</div>"""
    write("chronology/index.html",
          page("Chronology — Kenneth MacMillan", body,
               f"Every MacMillan ballet in order of first performance, {lo} to {hi}, "
               "as a graphic timeline linking to each work.",
               "/chronology/", "wide"))


# ---------------------------------------------------------------- essays
INFO_SLUGS = {"licensing-the-work", "notating-the-work", "credits-and-thanks",
              "articles-books-and-media", "subscribe"}


def essay_page(e, section):
    imgs = e["images"]
    lead = figures(imgs[:1], wide=True, eager=True, label=e["title"]) if imgs else ""
    rest = figures(imgs[1:], label=e["title"]) if len(imgs) > 1 else ""
    body = f"""
<section class="band band--slim">
  <div class="band__inner">
    <p class="tracked" style="opacity:.6;margin:0 0 1.25rem">
      <a href="/{section}/" style="text-decoration:none">{"Information" if section=="information" else "The Man, The Choreographer"}</a></p>
    <h1>{split_title(e["title"])}</h1>
  </div>
</section>
<div class="shell">
  {lead}
  <article class="prose">{prose(e["body"])}</article>
  {rest}
  {embeds(e["embeds"])}
</div>"""
    desc = e["body"][0][:180] if e["body"] else e["title"]
    write(f'{section}/{e["slug"]}/index.html',
          page(f'{e["title"]} — Kenneth MacMillan', body, desc, f"/{section}/"))


def card_img(images):
    """Always emit the frame so cards without a photograph still line up."""
    if images:
        return (f'<div class="card__img"><img src="{E(img_url(images[0]["file"]))}" alt="" '
                f'loading="lazy" decoding="async"></div>')
    return '<div class="card__img card__img--empty"></div>'


def hub(section, title, blurb, items):
    cards = "".join(
        f'<li><a class="card" href="/{section}/{e["slug"]}/">'
        + card_img(e["images"])
        + f'<h3>{E(e["title"])}</h3>'
          f'<p>{E((e["body"][0][:130] + "…") if e["body"] else "")}</p></a></li>'
        for e in items)
    body = f"""
<section class="band band--slim">
  <div class="band__inner">
    <h1>{split_title(title)}</h1>
  </div>
</section>
<div class="shell">
  <p class="lede measure" style="margin-bottom:clamp(2.5rem,6vw,4rem)">{E(blurb)}</p>
  <ul class="grid">{cards}</ul>
</div>"""
    write(f"{section}/index.html",
          page(f"{title} — Kenneth MacMillan", body, blurb, f"/{section}/", "wide"))


# ---------------------------------------------------------------- home
def home():
    # The best-known works first, but only ones with a photograph, so the grid
    # is not half placeholders; topped up with the fullest illustrated entries.
    NOTABLE = ["romeo-and-juliet", "manon", "mayerling", "the-judas-tree",
               "the-prince-of-the-pagodas", "isadora", "anastasia", "gloria",
               "winter-dreams", "different-drummer"]
    rank = {s: i for i, s in enumerate(NOTABLE)}
    illustrated = [w for w in WORKS if w["images"]]
    featured = sorted(
        illustrated,
        key=lambda w: (rank.get(w["slug"], len(NOTABLE)), -w["words"]))[:6]
    featured.sort(key=lambda w: w["display_year"])
    cards = "".join(
        f'<li><a class="card" href="/ballets/{w["slug"]}/">'
        + card_img(w["images"])
        + f'<h3>{E(w["name"])}</h3><p>{E(w["display_year"])} &middot; {E(w["company"])}</p></a></li>'
        for w in featured[:6])

    body = f"""
<section class="band">
  <div class="band__inner">
    <h1>Kenneth<br><em>MacMillan</em></h1>
    <div class="band__meta">
      <span class="tracked">His life, his work</span>
      <span class="tracked">1929 &ndash; 1992</span>
    </div>
  </div>
</section>
<div class="shell">
  <p class="lede measure" style="margin-block:clamp(2.5rem,6vw,4rem)">
    An online resource devoted to the choreographer Kenneth MacMillan:
    {spell(len(WORKS)).lower()} ballets made over forty years, with the essays,
    photographs and production records that surround them.</p>

  <div class="era__head" style="margin-bottom:2.5rem">
    <h2 style="font-family:var(--sans);font-weight:300;text-transform:uppercase;letter-spacing:.2em;font-size:1.2rem;margin:0">Selected works</h2>
    <a href="/ballets/" class="tracked" style="margin-left:auto;color:var(--ink-faint);text-decoration:none">All {len(WORKS)} &rarr;</a>
  </div>
  <ul class="grid">{cards}</ul>

  <div class="era__head" style="margin:clamp(4rem,9vw,6rem) 0 2.5rem">
    <h2 style="font-family:var(--sans);font-weight:300;text-transform:uppercase;letter-spacing:.2em;font-size:1.2rem;margin:0">Reading</h2>
    <a href="/the-man/" class="tracked" style="margin-left:auto;color:var(--ink-faint);text-decoration:none">The man &rarr;</a>
  </div>
  <ul class="grid">{"".join(
      f'<li><a class="card" href="/the-man/{e["slug"]}/">'
      + card_img(e["images"])
      + f'<h3>{E(e["title"])}</h3><p>{E((e["body"][0][:120] + "…") if e["body"] else "")}</p></a></li>'
      for e in [x for x in ESSAYS if x["slug"] not in INFO_SLUGS][:3])}</ul>
</div>"""
    write("index.html", page("Kenneth MacMillan — His Life, His Work", body,
                             "An online resource devoted to the choreographer Kenneth MacMillan "
                             f"(1929–1992): his {spell(len(WORKS)).lower()} ballets, essays and archive.", "/", "wide"))


# ---------------------------------------------------------------- run
def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for i, w in enumerate(WORKS):
        work_page(w, WORKS[i - 1] if i else None, WORKS[i + 1] if i + 1 < len(WORKS) else None)
    ballets_index()
    chronology()

    man = [e for e in ESSAYS if e["slug"] not in INFO_SLUGS]
    info = [e for e in ESSAYS if e["slug"] in INFO_SLUGS]
    for e in man:
        essay_page(e, "the-man")
    for e in info:
        essay_page(e, "information")
    hub("the-man", "The Man, The Choreographer",
        "Biography, criticism and first-hand accounts of MacMillan at work, by Jann Parry, "
        "Sir Peter Wright, Deborah MacMillan and the dancers who created his roles.", man)
    hub("information", "Information",
        "Licensing, notation, sources and acknowledgements for the MacMillan repertory.", info)
    home()

    # assets
    (DIST / "images").mkdir(parents=True, exist_ok=True)
    for src in (PROJ / "assets" / "images").iterdir():
        if src.is_file():
            shutil.copy(src, DIST / "images" / RENAMES.get(src.name, src.name))
    shutil.copy(ROOT / "static" / "site.css", DIST / "site.css")

    # the standalone holding page ships alongside, so it can be previewed here
    # and uploaded on its own when the site goes dark
    holding = PROJ / "holding"
    if holding.is_dir():
        shutil.copytree(holding, DIST / "holding", dirs_exist_ok=True)
    shutil.copy(ROOT / "static" / "site.js", DIST / "site.js")

    # sitemap + redirects from the old URLs
    urls = ["/", "/ballets/", "/chronology/", "/the-man/", "/information/"] \
        + [f'/ballets/{w["slug"]}/' for w in WORKS] \
        + [f'/the-man/{e["slug"]}/' for e in man] \
        + [f'/information/{e["slug"]}/' for e in info]
    today = datetime.date.today().isoformat()
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>https://kennethmacmillan.com{u}</loc>"
                    f"<lastmod>{today}</lastmod></url>\n" for u in urls)
          + "</urlset>\n")
    write("robots.txt", "User-agent: *\nAllow: /\n\n"
                        "Sitemap: https://kennethmacmillan.com/sitemap.xml\n")
    redirects = [f'/{w["old_slug"]}  /ballets/{w["slug"]}/  301' for w in WORKS] \
        + [f'/{e["old_slug"]}  /the-man/{e["slug"]}/  301' for e in man] \
        + [f'/{e["old_slug"]}  /information/{e["slug"]}/  301' for e in info] \
        + ["/when-where  /chronology/  301", "/the-ballets-1  /ballets/  301",
           "/the-ballets-1960-  /ballets/  301", "/the-ballets-1970-  /ballets/  301",
           "/the-ballets-1977-1992  /ballets/  301", "/our-story  /the-man/an-introduction/  301"]
    write("_redirects", "\n".join(redirects) + "\n")

    n = len(list(DIST.rglob("*.html")))
    print(f"built {n} pages -> {DIST}")
    print(f"  {len(WORKS)} works, {len(man)} essays, {len(info)} information pages")
    print(f"  {len(list((DIST/'images').iterdir()))} images, {len(redirects)} redirects")


if __name__ == "__main__":
    main()
