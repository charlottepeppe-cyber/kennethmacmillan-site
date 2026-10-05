"""Live studio: swap the display face and the accent hue on a real work page
excerpt. Writes dist/studio/."""
import json, html, pathlib

PROJ = pathlib.Path(__file__).parent.parent
OUT = PROJ / "dist" / "studio"
OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((PROJ / "site-data.json").read_text())
DIMS = json.loads((PROJ / "extract" / "dims.json").read_text())
W = next(w for w in DATA["works"] if w["slug"] == "the-judas-tree")
E = lambda s: html.escape(str(s or ""), quote=True)

FACES = [
    ("Anton", "Anton", 400, "0", "Current. Heavy, stamped, almost no counter space."),
    ("Antonio", "Antonio", 400, "0", "Anton's lighter sibling — same condensed proportions, much less weight."),
    ("Antonio Light", "Antonio", 300, ".01em", "Lighter again. Starts to feel drawn rather than stamped."),
    ("Bebas Neue", "Bebas Neue", 400, ".01em", "Caps-only, even stroke, a little wider. Cleaner, more neutral."),
    ("Big Shoulders", "Big Shoulders Display", 300, ".01em", "Flat cut terminals. More character, slightly industrial."),
    ("Barlow Condensed", "Barlow Condensed", 500, ".02em", "Softest of the set. Quieter, least like a poster."),
    ("Oswald", "Oswald", 300, ".01em", "Familiar and highly legible. The safe choice."),
]

HUES = [
    ("Acid", "#d2f24c", "#9bb437", "Current. Loud, contemporary, gallery-ish."),
    ("Bone", "#ece4d3", "#a89f8d", "No colour at all. Pure restraint — the archive speaking plainly."),
    ("Vermilion", "#e8492c", "#a8341f", "Theatrical and bloody. Suits Mayerling and the Judas Tree."),
    ("Brass", "#c9a24a", "#8f7333", "Opera house gilt. Warm, ceremonial, a little formal."),
    ("Rose", "#dfa093", "#a2685e", "Flesh and tulle. Softer, more bodily, unmistakably dance."),
    ("Ice", "#93bcd9", "#5f83a0", "Cool and distant. Stage light rather than blood."),
    ("Sulphur", "#e5c93f", "#a08a25", "Between brass and acid. Old paper under a bright lamp."),
]

im = W["images"][0]
wh = DIMS.get(im["file"], [800, 600])
rows = "".join(
    f"<dt>{E(k)}</dt><dd>{E(W['credits'][k])}</dd>"
    for k in ["First Performance", "Company", "Cast", "Music", "Design"] if W["credits"].get(k))

face_btns = "".join(
    f'<button data-face="{E(f)}" data-weight="{w}" data-ls="{ls}"'
    f'{" class=\'on\'" if n == 0 else ""} title="{E(note)}">{E(label)}</button>'
    for n, (label, f, w, ls, note) in enumerate(FACES))
hue_btns = "".join(
    f'<button data-hue="{E(h)}" data-dim="{E(d)}"{" class=\'on\'" if n == 0 else ""}'
    f' title="{E(note)}"><i style="background:{E(h)}"></i>{E(label)}</button>'
    for n, (label, h, d, note) in enumerate(HUES))

FONT_URL = ("https://fonts.googleapis.com/css2?family=Anton&family=Antonio:wght@100..700"
            "&family=Bebas+Neue&family=Big+Shoulders+Display:wght@100..900"
            "&family=Barlow+Condensed:wght@300;400;500&family=Oswald:wght@200..600"
            "&family=Spectral:ital,wght@0,200;0,300;0,400;1,300"
            "&family=JetBrains+Mono:wght@400;500&display=swap")

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Studio — face and hue</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONT_URL}" rel="stylesheet">
<style>
:root{{
  --ground:#0d0d0c; --panel:#161615; --panel-2:#1c1c1a; --ink:#e6e4e0;
  --ink-soft:#b4b0a9; --faint:#7d7a74; --rule:#2a2a28;
  --accent:#d2f24c; --accent-dim:#9bb437;
  --display:'Anton'; --display-w:400; --display-ls:0;
  --text:'Spectral',Georgia,serif; --meta:'JetBrains Mono',monospace;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--text);
  font-weight:300;line-height:1.65;padding-bottom:9rem}}
img{{max-width:100%;height:auto;display:block}}

/* controls */
.panel{{position:fixed;left:0;right:0;bottom:0;z-index:99;background:#111;
  border-top:1px solid var(--rule);padding:.7rem clamp(.75rem,2vw,1.5rem);
  display:grid;gap:.5rem}}
.set{{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}}
.set > span{{font-family:var(--meta);font-size:.55rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--faint);width:4.5rem;flex:none}}
.panel button{{font-family:var(--meta);font-size:.58rem;letter-spacing:.08em;
  text-transform:uppercase;background:#1c1c1a;color:#b4b0a9;border:1px solid #2a2a28;
  padding:.45rem .7rem;cursor:pointer;display:flex;align-items:center;gap:.4rem;
  transition:background .15s,color .15s,border-color .15s}}
.panel button:hover{{color:#fff;border-color:#444}}
.panel button.on{{background:var(--accent);color:#0d0d0c;border-color:var(--accent)}}
.panel button i{{width:.65rem;height:.65rem;display:block;border-radius:1px}}
.hint{{font-family:var(--meta);font-size:.52rem;letter-spacing:.1em;color:#5a5854;
  text-transform:uppercase}}

/* the specimen page itself */
.wrap{{max-width:46rem;margin:0 auto;padding:clamp(1rem,3vw,2.5rem)}}
.crumb{{font-family:var(--meta);font-size:.58rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--faint);border-bottom:1px solid var(--rule);
  padding-bottom:.7rem;margin-bottom:clamp(1.5rem,4vw,3rem)}}
h1{{font-family:var(--display);font-weight:var(--display-w);
  letter-spacing:var(--display-ls);text-transform:uppercase;
  font-size:clamp(2.6rem,1rem + 11vw,7rem);line-height:.9;margin:0}}
h1 em{{font-style:normal;color:var(--accent)}}
.meta{{margin-top:1.2rem;display:flex;flex-wrap:wrap;gap:.3rem 1.5rem;
  font-family:var(--meta);font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--faint)}}
.meta .yr{{color:var(--accent)}}
figure{{margin:clamp(2rem,5vw,3rem) 0}}
figure img{{max-width:min(100%,{wh[0]}px);filter:grayscale(1) contrast(1.08) brightness(.96)}}
figcaption{{margin-top:.6rem;font-family:var(--meta);font-size:.56rem;
  letter-spacing:.05em;text-transform:uppercase;color:var(--faint)}}
p{{margin:0 0 1.15em}}
p:first-of-type::first-line{{font-family:var(--meta);font-size:.78em;
  letter-spacing:.04em;text-transform:uppercase;color:var(--accent)}}
.credits{{margin-top:clamp(2.5rem,6vw,4rem);border:1px solid var(--rule)}}
.credits h2{{font-family:var(--meta);font-weight:400;text-transform:uppercase;
  letter-spacing:.22em;font-size:.6rem;color:var(--accent);margin:0;padding:.85rem 1rem;
  border-bottom:1px solid var(--rule)}}
.credits dl{{margin:0;display:grid;grid-template-columns:minmax(9rem,13rem) 1fr}}
.credits dt{{font-family:var(--meta);font-size:.58rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--faint);padding:.8rem 1rem;background:var(--panel);
  border-bottom:1px solid var(--rule)}}
.credits dd{{margin:0;padding:.8rem 1rem;border-bottom:1px solid var(--rule);font-size:.92rem}}
@media(max-width:40rem){{.credits dl{{grid-template-columns:1fr}}
  .credits dt{{border-bottom:0;padding-bottom:.2rem;background:none}}}}
</style></head><body>

<div class="wrap">
  <div class="crumb">Kenneth MacMillan &nbsp;/&nbsp; The Ballets &nbsp;/&nbsp; 1977&ndash;1992</div>
  <h1>The Judas <em>Tree</em></h1>
  <div class="meta"><span class="yr">1992</span><span>{E(W["company"])}</span>
    <span>{E(W["venue"])}</span><span>Music &mdash; Brian Elias</span></div>
  <figure><img src="/images/{E(im["file"])}" alt="" width="{wh[0]}" height="{wh[1]}">
    <figcaption>{E(im["caption"])}</figcaption></figure>
  {"".join(f"<p>{E(p)}</p>" for p in W["body"][:3])}
  <section class="credits"><h2>Creation</h2><dl>{rows}</dl></section>
</div>

<div class="panel">
  <div class="set"><span>Face</span>{face_btns}</div>
  <div class="set"><span>Hue</span>{hue_btns}</div>
  <div class="hint">Hover a button for a note. Choice is remembered while you browse.</div>
</div>

<script>
const root=document.documentElement;
function pick(group,btn){{
  group.querySelectorAll('button').forEach(b=>b.classList.remove('on'));
  btn.classList.add('on');
}}
document.querySelectorAll('[data-face]').forEach(b=>b.addEventListener('click',()=>{{
  root.style.setProperty('--display',"'"+b.dataset.face+"'");
  root.style.setProperty('--display-w',b.dataset.weight);
  root.style.setProperty('--display-ls',b.dataset.ls);
  pick(b.parentElement,b);
  localStorage.setItem('face',JSON.stringify(b.dataset));
}}));
document.querySelectorAll('[data-hue]').forEach(b=>b.addEventListener('click',()=>{{
  root.style.setProperty('--accent',b.dataset.hue);
  root.style.setProperty('--accent-dim',b.dataset.dim);
  pick(b.parentElement,b);
  localStorage.setItem('hue',JSON.stringify(b.dataset));
}}));
try{{
  const f=JSON.parse(localStorage.getItem('face')||'null');
  if(f){{const b=document.querySelector(`[data-face="${{f.face}}"][data-weight="${{f.weight}}"]`);if(b)b.click();}}
  const h=JSON.parse(localStorage.getItem('hue')||'null');
  if(h){{const b=document.querySelector(`[data-hue="${{h.hue}}"]`);if(b)b.click();}}
}}catch(e){{}}
</script>
</body></html>"""

(OUT / "index.html").write_text(page)
print(f"wrote {OUT}/index.html")
print(f"  {len(FACES)} faces, {len(HUES)} hues, live on real content")
