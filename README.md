# kennethmacmillan.com

A rebuild of the Kenneth MacMillan archive. Everything is generated from the old
Squarespace site plus the pre-2016 site held by the Internet Archive; nothing in
the essays or credits has been rewritten.

## Rebuild

```bash
./pipeline.sh
```

Output lands in `dist/` as plain HTML, CSS, one small JS file and the images.
No framework, no build server, nothing to keep up to date.

## Preview locally

```bash
python3 -m http.server 4180 --directory dist
```

## Deploy

`dist/` is a static folder, so any static host will serve it. It already contains
`_redirects` (Netlify/Cloudflare Pages format) mapping every old URL to its new
one, plus `sitemap.xml` and `robots.txt`.

- **Netlify / Cloudflare Pages** — drag `dist/` in, or point at this repo with
  publish directory `dist` and build command `./pipeline.sh`.
- **Anywhere else** — upload `dist/`, and translate `_redirects` into that host's
  own redirect format so existing links keep working.

## Layout

Each page has one content column and everything sits in it, so the title, the
photographs, the prose, the credits table and the rules all share an edge.

- `--shell` is that column: `45rem` on reading pages, which keeps the original
  site's proportion of a column a little over 700px with the black band running
  full bleed behind it. Pages that are tabular or gallery-like (the catalogue,
  the chronology, the hubs, the home page) carry `class="wide"` on `<html>`,
  which widens it to `68rem`.
- `--frame` is fixed at `68rem` and is used only by the masthead and footer, so
  the navigation does not jump as you move between a work page and the
  catalogue.
- Photographs fill the column but are never enlarged past their own pixel width
  (`--w`), because most of these are small archive scans.

## The pipeline

| Step | Script | What it does |
|---|---|---|
| 0 | `extract/crawl.py` | Crawls the live Squarespace site to `extract/html/`. Only needed if that site changes. |
| 1 | `extract/catalogue.py` | Reads the five period index pages for the canonical work list and ordering. |
| 2 | `extract/merge.py` | Matches each catalogued work to its page, by slug and then by title. |
| 3 | `extract/build_data.py` | Strips site chrome, normalises names and slugs, dedupes. |
| 4 | `extract/gallery.py` | Pulls the period-gallery photographs from the old sitemap and files each under the ballet its caption names. |
| 5 | `extract/wayback.py` | Recovers the credits blocks lost in the Squarespace migration. |
| 6 | `site/build.py` | Writes `dist/`. |

Facet logic (company, composer, designer, premiere date) lives in
`extract/facets.py` so steps 3 and 5 cannot drift apart.

`site-data.json` is the single source the site is built from. Editing it by hand
works, but `./pipeline.sh` will overwrite it.

## What changed from the old site

**Recovered.** Twenty works kept their essays but lost their credits when the
site moved to Squarespace, Romeo and Juliet, Manon and Song of the Earth among
them. Those blocks came back from the Internet Archive's copy of the pre-2016
site. Forty-two photographs that were stranded in the period galleries are now
on the individual ballet pages.

**Fixed.** The 1960 to 1966 index still linked to a site that has been dead for
a decade, so seventeen ballets were unreachable except through search. Every
work now has a real URL and title instead of `/new-page-62`.

**Added.** The catalogue can be searched and filtered by company, composer and
designer; filters are reflected in the URL, so a filtered view can be linked to
or cited. The site works on a phone.

**The chronology** is a graphic timeline. A strip across the top gives one
column per year from 1953 to 1992, drawn to the number of works that year holds
and stacked in company colour, so the shape of the working life is legible
before you read a word: the ochre Sadler's Wells apprenticeship, the blue Berlin
block in the late sixties, the long Royal Ballet red, and the three silent years
(1969, 1971, 1987). Each column jumps to its year; every one of the 91 works
below links to its own page. Company colours are shared across the site, so the
key means the same thing wherever it appears.

**Unchanged.** Every essay, caption and credit is the original wording. Image
credits to the V&A, the Royal Opera House Collections and the named
photographers are carried through as written.

## Known gaps

See `REPORT.md`, which the build regenerates.
