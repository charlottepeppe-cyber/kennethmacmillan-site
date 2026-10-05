"""Three experimental-editorial design directions, rendered on real content so
they can be compared like for like. Writes into dist/design/.

Run: .venv/bin/python site/directions.py
"""
import json, html, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
PROJ = ROOT.parent
OUT = PROJ / "dist" / "design"
DATA = json.loads((PROJ / "site-data.json").read_text())
DIMS = json.loads((PROJ / "extract" / "dims.json").read_text())

W = next(w for w in DATA["works"] if w["slug"] == "the-judas-tree")
E = lambda s: html.escape(str(s or ""), quote=True)

CREDIT_ORDER = ["First Performance", "Company", "Cast", "Music", "Design",
                "Benesh Notation Score", "Video"]

DIRECTIONS = [
    ("a", "Programme", "Didone display, hairline rules, plates in the margin"),
    ("b", "Wonk", "Variable serif, warm ground, overlapping plates"),
    ("c", "Specimen", "Grotesque and mono, catalogue logic, images as evidence"),
]


def switcher(active):
    links = "".join(
        f'<a href="/design/{k}/"{" class=\'on\'" if k == active else ""}>'
        f'<b>{k.upper()}</b> {E(name)}</a>'
        for k, name, _ in DIRECTIONS)
    return f'<nav class="switch">{links}<a href="/" class="live">Current site &rarr;</a></nav>'


SWITCH_CSS = """
.switch{position:fixed;left:0;right:0;bottom:0;z-index:999;display:flex;
  font:400 10px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.14em;
  text-transform:uppercase;background:#111;color:#bbb;border-top:1px solid #333}
.switch a{flex:1;padding:.85rem 1rem;color:inherit;text-decoration:none;
  border-right:1px solid #333;transition:background .15s,color .15s}
.switch a b{color:#fff;margin-right:.5em;font-weight:400}
.switch a:hover{background:#1c1c1c;color:#fff}
.switch a.on{background:#fff;color:#111}
.switch a.on b{color:#111}
.switch a.live{flex:0 0 auto;border-right:0;opacity:.6}
body{padding-bottom:3rem}
"""


def img(i, cls="", nocap=False):
    im = W["images"][i]
    wh = DIMS.get(im["file"], [800, 600])
    cap = "" if nocap else (
        f'<figcaption>{E(im["caption"])}</figcaption>' if im["caption"] else "")
    return (f'<figure class="{cls}" style="--w:{wh[0]}px;--ar:{wh[0]}/{wh[1]}">'
            f'<img src="/images/{E(im["file"])}" alt="{E(im["caption"] or W["name"])}" '
            f'width="{wh[0]}" height="{wh[1]}" loading="lazy" decoding="async">{cap}</figure>')


def credits_rows():
    return [(k, W["credits"][k]) for k in CREDIT_ORDER if W["credits"].get(k)]


def page(key, title, head, body):
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} — direction {key.upper()}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{head}
<style>{SWITCH_CSS}</style>
</head><body>
{body}
{switcher(key)}
</body></html>"""


# ─────────────────────────────────────────────────────── A · PROGRAMME
def direction_a():
    paras = W["body"]
    body = f"""
<style>
:root{{
  --ink:#12100e; --ground:#f2efe9; --faint:#8b8378; --rule:#c9c2b6;
  --accent:#8c1c13;
  --display:"Bodoni Moda",Didot,serif; --text:"Newsreader",Georgia,serif;
  --meta:"IBM Plex Mono",ui-monospace,monospace;
}}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--text);
  font-size:clamp(1rem,.95rem + .2vw,1.12rem);line-height:1.62;
  background-image:radial-gradient(circle at 1px 1px,rgba(18,16,14,.045) 1px,transparent 0);
  background-size:22px 22px}}
img{{max-width:100%;height:auto;display:block}}
.sheet{{max-width:78rem;margin:0 auto;padding:clamp(1.5rem,4vw,3.5rem)}}

.masthead{{display:flex;justify-content:space-between;align-items:flex-start;
  border-bottom:2px solid var(--ink);padding-bottom:.7rem;
  font-family:var(--meta);font-size:.62rem;letter-spacing:.26em;text-transform:uppercase}}

.hero{{margin:clamp(2.5rem,7vw,5rem) 0 clamp(2rem,5vw,3.5rem);position:relative}}
.hero h1{{font-family:var(--display);font-weight:400;font-style:italic;
  font-size:clamp(3.4rem,2rem + 11vw,11rem);line-height:.82;letter-spacing:-.02em;
  margin:0;text-indent:-.04em}}
.hero .yr{{position:absolute;right:0;top:-.4em;font-family:var(--meta);
  font-size:clamp(.7rem,.6rem + .5vw,1rem);letter-spacing:.3em;color:var(--accent)}}
.hero .sub{{margin-top:1.6rem;font-family:var(--meta);font-size:.68rem;
  letter-spacing:.24em;text-transform:uppercase;color:var(--faint);
  display:flex;flex-wrap:wrap;gap:.4rem 2rem;border-top:1px solid var(--rule);padding-top:.9rem}}

/* asymmetric: text sits left of centre, plates hang in the right margin */
.spread{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,15rem);
  gap:clamp(2rem,5vw,4.5rem);align-items:start}}
@media(max-width:56rem){{.spread{{grid-template-columns:1fr}}}}

.copy p{{margin:0 0 1.15em;hanging-punctuation:first}}
.copy p:first-of-type::first-letter{{font-family:var(--display);font-size:4.1em;
  float:left;line-height:.78;margin:.06em .09em 0 0;color:var(--accent)}}
.copy p.pull{{font-family:var(--display);font-style:italic;font-size:1.7em;
  line-height:1.22;margin:1.6em 0;color:var(--ink);text-indent:0;
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:.7em 0}}

.rail{{position:sticky;top:2rem;display:grid;gap:2.2rem}}
.rail figure{{margin:0}}
.rail img{{width:100%;filter:grayscale(1) contrast(1.06)}}
.rail figcaption,.plate figcaption{{font-family:var(--meta);font-size:.58rem;
  line-height:1.5;letter-spacing:.06em;color:var(--faint);margin-top:.5rem;
  text-transform:uppercase}}

.plate{{margin:clamp(2.5rem,6vw,4rem) 0}}
.plate img{{width:100%;max-width:var(--w);filter:grayscale(1) contrast(1.06)}}
.plate--offset{{margin-left:clamp(0rem,8vw,7rem)}}

.credits{{margin-top:clamp(3.5rem,8vw,6rem);border-top:2px solid var(--ink);padding-top:1.4rem}}
.credits h2{{font-family:var(--meta);font-size:.62rem;letter-spacing:.3em;
  text-transform:uppercase;color:var(--faint);margin:0 0 1.6rem;font-weight:400}}
.credits dl{{margin:0;display:grid;grid-template-columns:11rem 1fr;gap:0}}
.credits dt{{font-family:var(--meta);font-size:.6rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--accent);padding:.85rem 1rem .85rem 0;
  border-top:1px solid var(--rule)}}
.credits dd{{margin:0;padding:.8rem 0;border-top:1px solid var(--rule);font-size:.95rem}}
@media(max-width:40rem){{.credits dl{{grid-template-columns:1fr}}
  .credits dd{{border-top:0;padding-top:0;padding-bottom:1rem}}}}
</style>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..600&family=Newsreader:ital,opsz,wght@0,6..72,300..500;1,6..72,300..450&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">

<div class="sheet">
  <div class="masthead">
    <span>Kenneth MacMillan &nbsp;·&nbsp; The Ballets</span>
    <span>1977&ndash;1992 &nbsp;/&nbsp; no. 31</span>
  </div>

  <header class="hero">
    <span class="yr">{W["display_year"]}</span>
    <h1>The Judas<br>Tree</h1>
    <div class="sub">
      <span>{E(W["company"])}</span><span>{E(W["venue"])}</span>
      <span>Music &mdash; Brian Elias</span><span>Design &mdash; Jock McFadyen</span>
    </div>
  </header>

  <div class="spread">
    <div class="copy">
      {"".join(('<p class="pull">' if n == 3 else '<p>') + E(p) + '</p>' for n, p in enumerate(paras[:6]))}
      {img(1,"plate plate--offset")}
      {"".join(f"<p>{E(p)}</p>" for p in paras[6:])}
    </div>
    <aside class="rail">
      {img(0)}
      {img(2)}
    </aside>
  </div>

  {img(3,"plate")}

  <section class="credits">
    <h2>Creation</h2>
    <dl>{"".join(f"<dt>{E(k)}</dt><dd>{E(v)}</dd>" for k,v in credits_rows())}</dl>
  </section>
</div>"""
    return page("a", W["name"], "", body)


# ─────────────────────────────────────────────────────── B · WONK
def direction_b():
    paras = W["body"]
    body = f"""
<style>
:root{{
  --ink:#1b1410; --ground:#e8ddcd; --paper:#f5eee2; --faint:#8a7a66;
  --accent:#b2442e; --deep:#2f1d16;
  --display:"Fraunces",Georgia,serif; --text:"Fraunces",Georgia,serif;
  --meta:"Archivo",system-ui,sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);
  font-family:var(--text);font-variation-settings:"SOFT" 20,"WONK" 1,"opsz" 14;
  font-size:clamp(1rem,.95rem + .25vw,1.15rem);line-height:1.6}}
img{{max-width:100%;height:auto;display:block}}
.wrap{{max-width:82rem;margin:0 auto;padding:clamp(1.25rem,3vw,3rem)}}

.top{{font-family:var(--meta);font-size:.66rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--faint);display:flex;
  justify-content:space-between;margin-bottom:clamp(2rem,6vw,4rem)}}

/* title overlaps the first plate */
.head{{position:relative;margin-bottom:clamp(2rem,6vw,4rem)}}
.head figure{{margin:0;width:min(46%,26rem);margin-left:auto}}
.head img{{width:100%;border-radius:2px}}
.head h1{{font-family:var(--display);font-variation-settings:"SOFT" 40,"WONK" 1,"opsz" 100;
  font-weight:600;font-size:clamp(3rem,1.5rem + 10vw,9.5rem);line-height:.86;
  margin:0;color:var(--deep);position:relative;z-index:2;
  mix-blend-mode:multiply;max-width:11ch}}
.head .meta{{position:absolute;right:0;bottom:-2.2rem;font-family:var(--meta);
  font-size:.66rem;letter-spacing:.18em;text-transform:uppercase;color:var(--faint)}}
@media(min-width:56rem){{
  .head{{display:grid;grid-template-columns:1fr 1fr;align-items:end}}
  .head h1{{grid-column:1/3;grid-row:1;margin-bottom:-1.5rem}}
  .head figure{{grid-column:2/3;grid-row:1;width:100%}}
}}

.lede{{font-size:1.42em;line-height:1.38;max-width:26ch;color:var(--deep);
  font-variation-settings:"SOFT" 60,"WONK" 1,"opsz" 40;margin:0 0 3rem}}

.cols{{columns:2;column-gap:clamp(2rem,5vw,4rem);orphans:3;widows:3}}
@media(max-width:52rem){{.cols{{columns:1}}}}
.cols p{{margin:0 0 1.1em;break-inside:avoid-column}}

.plate{{margin:clamp(2.5rem,6vw,4rem) 0;max-width:var(--w)}}
.plate img{{width:100%;border-radius:2px}}
.plate--right{{margin-left:auto}}
figcaption{{font-family:var(--meta);font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--faint);margin-top:.6rem}}

.quote{{background:var(--deep);color:var(--paper);margin:clamp(3rem,7vw,5rem) 0;
  padding:clamp(2rem,5vw,3.5rem);border-radius:3px}}
.quote p{{font-family:var(--display);font-variation-settings:"SOFT" 70,"WONK" 1,"opsz" 60;
  font-size:clamp(1.3rem,1rem + 1.6vw,2.2rem);line-height:1.24;margin:0;max-width:30ch}}

.credits{{background:var(--paper);border-radius:3px;padding:clamp(1.5rem,4vw,2.5rem);
  margin-top:clamp(3rem,7vw,5rem)}}
.credits h2{{font-family:var(--meta);font-size:.66rem;letter-spacing:.24em;
  text-transform:uppercase;margin:0 0 1.4rem;color:var(--accent)}}
.credits dl{{margin:0;display:grid;grid-template-columns:10rem 1fr;gap:.1rem 1rem}}
.credits dt{{font-family:var(--meta);font-size:.64rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--faint);padding:.6rem 0}}
.credits dd{{margin:0;padding:.55rem 0;font-size:.95rem}}
@media(max-width:40rem){{.credits dl{{grid-template-columns:1fr}}.credits dd{{padding-top:0;margin-bottom:.7rem}}}}
</style>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..700,0..100,0..1;1,9..144,300..700,0..100,0..1&family=Archivo:wght@400;500&display=swap" rel="stylesheet">

<div class="wrap">
  <div class="top"><span>Kenneth MacMillan</span><span>{W["display_year"]} &nbsp;·&nbsp; {E(W["company"])}</span></div>

  <header class="head">
    <h1>The Judas Tree</h1>
    {img(0, nocap=True)}
    <span class="meta">{E(W["venue"])} &nbsp;·&nbsp; Painting: Jock McFadyen</span>
  </header>

  <p class="lede">{E(paras[0])}</p>

  <div class="cols">
    {"".join(f"<p>{E(p)}</p>" for p in paras[1:5])}
  </div>

  {img(1,"plate plate--right")}

  <blockquote class="quote"><p>{E(paras[5][:210])}…</p></blockquote>

  <div class="cols">
    {"".join(f"<p>{E(p)}</p>" for p in paras[6:])}
  </div>

  {img(2,"plate")}

  <section class="credits">
    <h2>Creation</h2>
    <dl>{"".join(f"<dt>{E(k)}</dt><dd>{E(v)}</dd>" for k,v in credits_rows())}</dl>
  </section>
</div>"""
    return page("b", W["name"], "", body)


# ─────────────────────────────────────────────────────── C · SPECIMEN
def direction_c():
    paras = W["body"]
    plates = "".join(
        f'<div class="sp"><span class="n">{n + 1:02d}</span>{img(n)}</div>'
        for n in range(len(W["images"])))
    body = f"""
<style>
:root{{
  --ink:#e6e4e0; --ground:#0d0d0c; --panel:#161615; --faint:#7d7a74;
  --rule:#2a2a28; --accent:#d2f24c;
  --display:"Anton",Impact,sans-serif;
  --text:"Spectral",Georgia,serif;
  --meta:"JetBrains Mono",ui-monospace,monospace;
}}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--text);
  font-size:clamp(.98rem,.94rem + .2vw,1.08rem);line-height:1.65;font-weight:300}}
img{{max-width:100%;height:auto;display:block}}
.grid{{max-width:88rem;margin:0 auto;padding:clamp(1rem,2.5vw,2rem)}}

.bar{{display:grid;grid-template-columns:repeat(12,1fr);gap:1px;background:var(--rule);
  border:1px solid var(--rule);font-family:var(--meta);font-size:.6rem;
  letter-spacing:.1em;text-transform:uppercase}}
.bar span{{background:var(--ground);padding:.7rem .8rem;color:var(--faint)}}
.bar span:first-child{{grid-column:span 4;color:var(--ink)}}
.bar span:nth-child(2){{grid-column:span 4}}
.bar span:nth-child(3){{grid-column:span 4;text-align:right}}
@media(max-width:52rem){{.bar span,.bar span:first-child{{grid-column:span 12!important;text-align:left!important}}}}

.title{{margin:clamp(2rem,6vw,4.5rem) 0 clamp(1.5rem,4vw,3rem)}}
.title h1{{font-family:var(--display);font-weight:400;text-transform:uppercase;
  font-size:clamp(3.2rem,1rem + 13vw,12rem);line-height:.84;letter-spacing:-.01em;
  margin:0;color:var(--ink)}}
.title h1 em{{font-style:normal;color:var(--accent);display:block}}
.title .tag{{font-family:var(--meta);font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--faint);margin-top:1.2rem;
  display:flex;flex-wrap:wrap;gap:.4rem 2rem}}

.two{{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);
  gap:clamp(1.5rem,4vw,3.5rem);margin-top:clamp(2rem,5vw,3.5rem)}}
@media(max-width:56rem){{.two{{grid-template-columns:1fr}}}}
.two p{{margin:0 0 1.05em}}
.two p:first-child::first-line{{font-family:var(--meta);font-size:.8em;
  letter-spacing:.04em;text-transform:uppercase;color:var(--accent)}}

/* plates presented as catalogued specimens */
.plates{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));
  gap:1px;background:var(--rule);border:1px solid var(--rule);
  margin:clamp(2.5rem,6vw,4.5rem) 0}}
.sp{{background:var(--panel);padding:1rem;position:relative}}
.sp .n{{font-family:var(--meta);font-size:.58rem;color:var(--accent);
  letter-spacing:.12em;display:block;margin-bottom:.7rem}}
.sp figure{{margin:0}}
.sp img{{width:100%;filter:grayscale(1) contrast(1.1) brightness(.95)}}
.sp figcaption{{font-family:var(--meta);font-size:.55rem;line-height:1.5;
  color:var(--faint);margin-top:.6rem;text-transform:uppercase;letter-spacing:.05em}}

.data{{border:1px solid var(--rule);margin-top:clamp(2.5rem,6vw,4rem)}}
.data h2{{font-family:var(--meta);font-size:.6rem;letter-spacing:.24em;
  text-transform:uppercase;color:var(--accent);margin:0;padding:.9rem 1rem;
  border-bottom:1px solid var(--rule);font-weight:400}}
.data dl{{margin:0;display:grid;grid-template-columns:13rem 1fr}}
.data dt{{font-family:var(--meta);font-size:.6rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--faint);padding:.8rem 1rem;
  border-bottom:1px solid var(--rule);background:var(--panel)}}
.data dd{{margin:0;padding:.8rem 1rem;border-bottom:1px solid var(--rule);font-size:.92rem}}
@media(max-width:44rem){{.data dl{{grid-template-columns:1fr}}
  .data dd{{border-bottom:1px solid var(--rule)}}}}
</style>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Spectral:ital,wght@0,200;0,300;0,400;1,300&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<div class="grid">
  <div class="bar">
    <span>Kenneth MacMillan / Catalogue</span>
    <span>Work 091 &nbsp;·&nbsp; Period 1977&ndash;1992</span>
    <span>{E(W["premiere_raw"])}</span>
  </div>

  <header class="title">
    <h1>The Judas<em>Tree</em></h1>
    <div class="tag">
      <span>{W["display_year"]}</span><span>{E(W["company"])}</span>
      <span>Brian Elias</span><span>Jock McFadyen</span>
      <span>{len(W["images"])} plates</span>
    </div>
  </header>

  <div class="two">
    <div>{"".join(f"<p>{E(p)}</p>" for p in paras[:6])}</div>
    <div>{"".join(f"<p>{E(p)}</p>" for p in paras[6:])}</div>
  </div>

  <div class="plates">{plates}</div>

  <section class="data">
    <h2>Creation record</h2>
    <dl>{"".join(f"<dt>{E(k)}</dt><dd>{E(v)}</dd>" for k,v in credits_rows())}</dl>
  </section>
</div>"""
    return page("c", W["name"], "", body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for key, fn in [("a", direction_a), ("b", direction_b), ("c", direction_c)]:
        d = OUT / key
        d.mkdir(parents=True)
        (d / "index.html").write_text(fn())
    idx = "".join(
        f'<li><a href="/design/{k}/"><b>{k.upper()}</b> <strong>{E(n)}</strong>'
        f'<span>{E(d)}</span></a></li>' for k, n, d in DIRECTIONS)
    (OUT / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Design directions</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#0d0d0c;color:#e6e4e0;font:400 14px/1.6 "JetBrains Mono",monospace;
  display:grid;place-items:center;min-height:100vh;padding:2rem}}
ul{{list-style:none;padding:0;margin:0;max-width:34rem;width:100%}}
li+li{{margin-top:1px}}
a{{display:grid;grid-template-columns:2.5rem 1fr;gap:.4rem 1rem;padding:1.4rem;
  background:#161615;color:inherit;text-decoration:none;transition:background .15s}}
a:hover{{background:#222}}
b{{color:#d2f24c;font-weight:400}}
strong{{font-weight:400;font-size:1.1rem}}
span{{grid-column:2;color:#7d7a74;font-size:.72rem}}
h1{{font-size:.7rem;letter-spacing:.3em;text-transform:uppercase;color:#7d7a74;
  margin:0 0 1.5rem;max-width:34rem;width:100%;font-weight:400}}
</style></head><body>
<h1>The Judas Tree &mdash; three directions</h1>
<ul>{idx}</ul>
</body></html>""")
    print(f"wrote {len(DIRECTIONS)} directions to {OUT}")
    for k, n, d in DIRECTIONS:
        print(f"  /design/{k}/  {n:<10} {d}")


if __name__ == "__main__":
    main()
