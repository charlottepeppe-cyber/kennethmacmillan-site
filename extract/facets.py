"""Derive the filterable facets (company, composer, designer, premiere) from a
work's credits. Shared so facets stay correct after the Wayback merge adds
credits that weren't present when the work was first built."""
import re

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

# The pages were written over many years and label the same thing several ways.
# Everything on the left is folded into the canonical name on the right.
FIELD_ALIASES = {
    "first performance": "First Performance",
    "first performed": "First Performance",
    "company": "Company",
    "cast": "Cast",
    "dancers": "Cast",
    "participants": "Cast",
    "music": "Music",
    "score": "Music",
    "design": "Design",
    "designer": "Design",
    "costumes": "Costumes",
    "lighting": "Lighting",
    "scenario": "Scenario",
    "libretto": "Libretto",
    "choreography": "Choreography",
    "director": "Director",
    "producer": "Producer",
    "screenplay": "Screenplay",
    "lyrics": "Lyrics",
    "occasion": "Occasion",
    "duration": "Duration",
    "benesh notation score": "Benesh Notation Score",
    "video": "Video",
    "dvd": "Video",
    "television": "Television",
    "cinema release": "Cinema release",
    "dance sequences": "Dance sequences",
}
# longest first so "first performance" is not shadowed by a shorter alias
FIELD_PATTERN = "|".join(
    re.escape(k) for k in sorted(FIELD_ALIASES, key=len, reverse=True))


def canon_field(label):
    return FIELD_ALIASES.get(label.strip().rstrip(":").lower())


# Squarespace stamps theme tweaks such as "image-block-poster-text-alignment-center"
# onto <body>, so a substring match for "image-block" climbs all the way up and
# every uncaptioned photograph adopts the first caption on the page. Match whole
# class tokens instead, and stop after a few levels.
IMAGE_BLOCK = {"sqs-block-image", "image-block", "sqs-block-content"}

_FILENAMEY = re.compile(
    r"^[\w\-. +%]+\.(jpe?g|png|gif|webp|tiff?)$|^(img|dsc|scan|image)[\s_-]*\d+$", re.I)


def clean_caption(text):
    """Drop alt text that is really just the asset's filename."""
    t = " ".join((text or "").split())
    return "" if _FILENAMEY.match(t) else t


def image_caption(img, max_depth=5):
    """The caption belonging to this image, or '' if it has none of its own."""
    node, depth = img, 0
    while node is not None and depth < max_depth:
        node = node.parent
        depth += 1
        if node is None or node.name in ("body", "html", "[document]"):
            break
        if node.name == "figure" or (IMAGE_BLOCK & set(node.get("class") or [])):
            cap = node.find(class_=lambda c: c and "caption" in " ".join(
                c if isinstance(c, list) else [c]).lower())
            if cap:
                text = clean_caption(cap.get_text(" ", strip=True))
                if text:
                    return text
            if node.name == "figure":
                break
    return ""

SPELLING = {"Nicholas Geordiadis": "Nicholas Georgiadis"}

COMPANY_CANON = [
    ("Sadler's Wells Choreographic Group", ["choreographic group"]),
    ("Sadler's Wells Theatre Ballet", ["sadler's wells theatre ballet", "sadlers wells theatre ballet"]),
    ("Sadler's Wells Royal Ballet", ["sadler’s wells royal", "sadler's wells royal"]),
    ("Sadler's Wells Ballet", ["sadler’s wells ballet", "sadler's wells ballet"]),
    ("Sadler's Wells", ["sadler’s wells", "sadler's wells"]),
    ("The Royal Ballet New Group", ["new group"]),
    ("The Royal Ballet School", ["royal ballet school"]),
    ("The Royal Ballet", ["royal ballet"]),
    ("The Royal Opera", ["royal opera"]),
    ("Stuttgart Ballet", ["stuttgart"]),
    ("Ballet of the Deutsche Oper", ["deutsche oper"]),
    ("American Ballet Theatre", ["american ballet theat"]),
    ("Paris Opera Ballet", ["paris opera"]),
    ("Royal Swedish Ballet", ["royal swedish"]),
    ("Birmingham Royal Ballet", ["birmingham royal"]),
    ("Western Theatre Ballet", ["western theatre"]),
    ("London Festival Ballet", ["festival ballet"]),
    ("BBC Television", ["bbc"]),
    ("National Theatre", ["national theatre"]),
]


def split_names(v):
    v = re.sub(r"\(.*?\)", "", v or "")
    out = []
    for p in re.split(r"\s*[,;]\s*|\s+and\s+|\s*&\s*|\s*/\s*", v):
        p = re.sub(r"\s+", " ", p).strip(" .")
        if 2 < len(p) < 60 and not re.match(
                r"^(after|arranged|orch|from|the score|commissioned)", p, re.I):
            out.append(SPELLING.get(p, p))
    return out


def canon_company(v):
    low = (v or "").lower()
    for name, keys in COMPANY_CANON:
        if any(k in low for k in keys):
            return name
    return re.sub(r"\s+", " ", v or "").strip(" .,")[:60]


def parse_premiere(fp):
    fp = fp or ""
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+((?:18|19|20)\d{2})", fp)
    if m and m.group(2)[:3].lower() in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(2)[:3].lower()]:02d}-{int(m.group(1)):02d}"
    m = re.search(r"([A-Za-z]{3,9})\s+((?:18|19|20)\d{2})", fp)
    if m and m.group(1)[:3].lower() in MONTHS:
        return f"{m.group(2)}-{MONTHS[m.group(1)[:3].lower()]:02d}"
    m = re.search(r"((?:18|19|20)\d{2})", fp)
    return m.group(1) if m else None


def venue_of(fp):
    fp = fp or ""
    part = re.split(r",?\s*\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|,?\s*[A-Za-z]{3,9}\s+\d{4}|,?\s*\d{4}",
                    fp)[0]
    return re.sub(r"\s+", " ", part).strip(" .,")


def derive(w):
    """Recompute a work's facet fields in place from its credits."""
    c = w["credits"]
    fp = c.get("First Performance", "")
    music = c.get("Music", "")
    design = c.get("Design") or c.get("Designer", "")
    company = c.get("Company", "")

    w["premiere_raw"] = fp
    w["premiere"] = parse_premiere(fp)
    w["venue"] = venue_of(fp)
    w["company_raw"] = company
    w["company"] = canon_company(company) if company else ""
    w["music"] = music
    w["composers"] = split_names(music)[:1] if music else []
    w["design"] = design
    w["designers"] = split_names(design) if design else []
    w["cast"] = split_names(c.get("Cast", "")) if c.get("Cast") else []
    w["notation"] = c.get("Benesh Notation Score", "")
    w["video"] = c.get("Video", "")
    if not w.get("year") and w["premiere"]:
        w["year"] = int(w["premiere"][:4])
    # A handful of pages are headed with the year MacMillan made the ballet rather
    # than the year it opened. The dated first performance is the sourced fact, so
    # it wins wherever the two disagree.
    w["display_year"] = int(w["premiere"][:4]) if w["premiere"] else w.get("year")
    return w
