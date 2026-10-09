#!/usr/bin/env python3
"""
USUCGER static site builder.

Every page shares one header, nav, drawer, footer and asset bundle, so the whole
site is guaranteed to stay in the same format. Page bodies live in pages/*.html.

    python3 build.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(ROOT, "pages")
OUT_DIR = ROOT

CONTACT = "webmaster@usucger.org"
BOARD_EMAIL = "uboard@usucger.org"
LOGIN_URL = "https://usucger.org/my-account/"
JOIN_UNIV = "https://usucger.org/membership/usucger-3-year-membership-us-universities-2025-2027/"
JOIN_ASSOC = "https://usucger.org/membership/usucger-3-year-membership-associate-2025-2027/"

# ---------------------------------------------------------------- navigation
NAV = [
    ("About", "about.html", [
        ("History &amp; Mission", "about.html"),
        ("By-Laws", "bylaws.html"),
        ("Board of Directors", "board.html"),
        ("Contact USUCGER", "contact.html"),
    ]),
    ("Members", "membership.html", [
        ("Membership &amp; Dues", "membership.html"),
        ("Membership Directory", "directory.html"),
        ("Member Universities", "universities.html"),
        ("Member Login", LOGIN_URL),
    ]),
    ("Positions", "positions.html", [
        ("Academic Positions", "positions.html"),
        ("Industry &amp; Agency Positions", "industry-positions.html"),
        ("Post a Position", "mailto:webmaster@usucger.org?subject=Position%20Posting"),
    ]),
    ("Activities", "awards.html", [
        ("Awards", "awards.html"),
        ("Student Travel Grants", "travel-grants.html"),
        ("Small Research Grants", "research-grants.html"),
        ("Meeting Minutes", "minutes.html"),
    ]),
    ("Resources", "teaching-aids.html", [
        ("Teaching Aids", "teaching-aids.html"),
        ("Books &amp; Publications", "books.html"),
        ("Software &amp; Data", "software.html"),
        ("Videos &amp; Webinars", "videos.html"),
        ("Funding Tips", "funding-tips.html"),
        ("Photo Collections", "photos.html"),
    ]),
    ("Events", "conferences.html", [
        ("Conferences", "conferences.html"),
        ("Workshops", "workshops.html"),
    ]),
]

FOOTER = [
    ("About", [
        ("History &amp; Mission", "about.html"),
        ("By-Laws", "bylaws.html"),
        ("Board of Directors", "board.html"),
        ("Contact USUCGER", "contact.html"),
    ]),
    ("Members", [
        ("Membership &amp; Dues", "membership.html"),
        ("Membership Directory", "directory.html"),
        ("Member Universities", "universities.html"),
        ("Meeting Minutes", "minutes.html"),
        ("Member Login", LOGIN_URL),
    ]),
    ("Positions", [
        ("Academic Positions", "positions.html"),
        ("Industry &amp; Agency Positions", "industry-positions.html"),
        ("Post a Position", "mailto:webmaster@usucger.org?subject=Position%20Posting"),
    ]),
    ("Resources", [
        ("Awards", "awards.html"),
        ("Student Travel Grants", "travel-grants.html"),
        ("Small Research Grants", "research-grants.html"),
        ("Teaching Aids", "teaching-aids.html"),
        ("Books &amp; Publications", "books.html"),
        ("Software &amp; Data", "software.html"),
        ("Videos &amp; Webinars", "videos.html"),
        ("Conferences", "conferences.html"),
    ]),
]

NOTICES = (
    '<span class="notice-item"><span class="bdot" style="background:#FCD87A"></span> '
    '<strong>2025 Award Winners:</strong> Dr. Sheng Dai &amp; Dr. Ed Kavazanjian '
    '&mdash; <a href="awards.html">View awards &rarr;</a></span>'
    '<span class="notice-sep">&middot;</span>'
    '<span class="notice-item">&#9200; <strong>Award Nominations:</strong> due January 15, 2026 '
    '&mdash; <a href="awards.html">Nominate &rarr;</a></span>'
    '<span class="notice-sep">&middot;</span>'
    '<span class="notice-item">&#9992; <strong>Student Travel Grants</strong> due March 15, 2026 '
    '&mdash; <a href="travel-grants.html">Apply &rarr;</a></span>'
    '<span class="notice-sep">&middot;</span>'
    '<span class="notice-item">&#128179; <strong>Membership 2025&ndash;2027:</strong> $75 per person '
    '&mdash; <a href="membership.html">Join / Renew &rarr;</a></span>'
    '<span class="notice-sep">&middot;</span>'
)

# ------------------------------------------------------------------- helpers
def inline_svg(name, suffix, cls, extra=""):
    """Read a brand SVG and return it inline with unique clip ids and a class."""
    path = os.path.join(ROOT, "brand", "logo", name)  # Strata masters; colours become theme variables
    with open(path, "r", encoding="utf-8") as fh:
        svg = fh.read()
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    svg = svg.replace('id="uInner"', 'id="uInner%s"' % suffix).replace("url(#uInner)", "url(#uInner%s)" % suffix)
    svg = re.sub(r'\swidth="[\d.]+"\sheight="[\d.]+"', "", svg, count=1)
    svg = svg.replace("<svg ", '<svg class="%s" %s ' % (cls, extra), 1)
    svg = re.sub("|".join(LOGO_VARS), lambda m: "var(%s)" % LOGO_VARS[m.group(0).upper()], svg, flags=re.I)
    return svg


# Strata master colour -> theme variable, so the inline logo follows the active theme
LOGO_VARS = {"#102747": "--logo-wall", "#1B3F6E": "--logo-s1", "#2554A0": "--logo-s0", "#5B86CC": "--logo-r0",
             "#B9CCEB": "--logo-pale", "#C47A1A": "--logo-accent", "#FCD87A": "--logo-accent-hi"}


def is_external(href):
    return href.startswith(("http://", "https://", "mailto:"))


def link_attrs(href):
    return ' target="_blank" rel="noopener"' if is_external(href) else ""


def positions_count():
    try:
        with open(os.path.join(ROOT, "data", "positions_count.txt")) as fh:
            return int(fh.read().strip())
    except Exception:
        return 0


def nav_html(current):
    out = []
    for label, root, subs in NAV:
        active = any(current == h for _, h in subs) or current == root
        hot = label == "Positions"
        out.append('<li class="nav-item%s">' % (" nav-hot" if hot else ""))
        pill = ""
        out.append(
            '<a href="%s"%s class="%s">%s%s <span class="nav-caret" aria-hidden="true">&#9662;</span></a>'
            % (root, link_attrs(root), "active" if active else "", label, pill)
        )
        out.append('<div class="nav-sub">')
        for slabel, shref in subs:
            cls = ' class="active"' if shref == current else ""
            out.append('<a href="%s"%s%s>%s</a>' % (shref, link_attrs(shref), cls, slabel))
        out.append("</div></li>")
    return "".join(out)


def drawer_html(current):
    out = []
    for label, root, subs in NAV:
        active = any(current == h for _, h in subs) or current == root
        out.append('<div class="drawer-group%s">' % (" open" if active else ""))
        out.append(
            '<button type="button" aria-expanded="%s">%s<span class="chev" aria-hidden="true">&#9662;</span></button>'
            % ("true" if active else "false", label)
        )
        out.append('<div class="drawer-links">')
        for slabel, shref in subs:
            cls = ' class="active"' if shref == current else ""
            out.append('<a href="%s"%s%s>%s</a>' % (shref, link_attrs(shref), cls, slabel))
        out.append("</div></div>")
    return "".join(out)


def footer_links_html():
    out = []
    for title, links in FOOTER:
        out.append('<div><div class="ft-col-title">%s</div><ul class="ft-links">' % title)
        for label, href in links:
            out.append('<li><a href="%s"%s>%s</a></li>' % (href, link_attrs(href), label))
        out.append("</ul></div>")
    return "".join(out)


def crumbs_html(trail):
    if not trail:
        return ""
    bits = ['<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a>']
    for label, href in trail:
        bits.append('<span class="sep" aria-hidden="true">/</span>')
        if href:
            bits.append('<a href="%s">%s</a>' % (href, label))
        else:
            bits.append("<span>%s</span>" % label)
    bits.append("</nav>")
    return "".join(bits)


# --------------------------------------------------------------------- shell
SHELL = """<!DOCTYPE html>
<html lang="en" data-theme="{theme_key}" data-band="{theme_band}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website">
{icon_links}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=Figtree:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/theme.css">
<script>(function(){{var L={light_keys};try{{var q=new URLSearchParams(location.search).get("theme");var t=q||localStorage.getItem("usucger-theme");if(q)localStorage.setItem("usucger-theme",q);if(t&&{all_keys}.indexOf(t)>-1){{var h=document.documentElement;h.setAttribute("data-theme",t);h.setAttribute("data-band",L.indexOf(t)>-1?"light":"dark");}}}}catch(e){{}}}})();</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<nav id="nav" aria-label="Primary">
  <div class="nav-wrap">
    <a href="index.html" class="nav-brand" aria-label="USUCGER home">
      {nav_mark}
      <div class="nav-brand-text"><strong>USUCGER</strong></div>
    </a>
    <ul class="nav-menu">{nav}</ul>
    <div class="nav-end">
      <button type="button" class="nav-search" id="searchOpen" aria-label="Search the site" title="Search (Ctrl+K)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><span>Search</span><kbd>&#8984;K</kbd></button>
      <a href="contact.html" class="btn btn-outline btn-sm">Contact</a>
      <a href="membership.html" class="btn btn-cobalt btn-sm">Join / Renew &rarr;</a>
    </div>
    <button type="button" class="nav-search nav-search-m" id="searchOpenM" aria-label="Search the site"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></button>
    <button class="nav-toggle" id="navToggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="drawer">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
</nav>

<div class="drawer" id="drawer">
  <div class="drawer-scrim"></div>
  <div class="drawer-panel" role="dialog" aria-label="Site menu">
    <div class="drawer-head"><span style="display:flex;align-items:center;gap:.6rem">{nav_mark}<strong>USUCGER</strong></span><button class="drawer-close" type="button" aria-label="Close menu">&times;</button></div>
    {drawer}
    <div class="drawer-cta">
      <a href="membership.html" class="btn btn-cobalt">Join / Renew Membership</a>
      <a href="contact.html" class="btn btn-outline">Contact USUCGER</a>
    </div>
  </div>
</div>

<div class="search" id="search" hidden>
  <div class="search-scrim"></div>
  <div class="search-box" role="dialog" aria-modal="true" aria-label="Search USUCGER">
    <div class="search-field"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input type="search" id="searchInput" placeholder="Search pages, awards, resources, people&hellip;" autocomplete="off"><button type="button" class="search-close" id="searchClose" aria-label="Close search">Esc</button></div>
    <div class="search-results" id="searchResults"><div class="search-hint">Try <em>travel grant</em>, <em>by-laws</em>, <em>CPT proceedings</em>, <em>Purdue</em>&hellip;</div></div>
  </div>
</div>

<main id="main">
{body}
</main>

{cta}

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="ft-brand">
        <a href="index.html" aria-label="USUCGER home">{footer_logo}</a>
        <p>United States Universities Council on Geotechnical Education and Research. Founded 1985 in San Francisco &mdash; advocacy for geomechanical, geotechnical and geoenvironmental engineering research and education at U.S. universities.</p>
        <p style="margin-top:.8rem">Questions? <a href="mailto:{contact}">{contact}</a><br>Board: <a href="mailto:{board_email}">{board_email}</a></p>
      </div>
      {footer_links}
    </div>
  </div>
</footer>

<div class="footer-bottom fixed-bar" role="contentinfo">
  <div class="wrap fb-inner">
    <span class="fb-copy">&copy; <span data-now-year>2026</span> USUCGER. All rights reserved.</span>
    <span class="fb-contact">Contact: <a href="mailto:{contact}">{contact}</a></span>
    <span class="footer-credit">Website designed by Dr. Nitin Tiwari, Southern Illinois University Carbondale, IL</span>
  </div>
</div>

<button id="btt" type="button" title="Back to top" aria-label="Back to top">&uarr;</button>
<script src="assets/search-index.js" defer></script>
<script src="assets/themes.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
"""

CTA_STRIP = """<section class="cta-strip">
  <div class="wrap"><div class="cta-inner">
    <div>
      <h2>{heading}</h2>
      <p>{sub}</p>
    </div>
    <div class="cta-actions">
      <a href="membership.html" class="btn btn-amber">Join / Renew &rarr;</a>
      <a href="contact.html" class="btn btn-ghost">Contact USUCGER</a>
    </div>
  </div></div>
</section>"""

STRATA = """<svg class="phero-band" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true" focusable="false">
  <path d="M0 26 C 240 6, 420 54, 720 34 S 1200 0, 1440 22 V90 H0 Z" fill="var(--primary-md)" fill-opacity=".26"/>
  <path d="M0 52 C 260 36, 480 80, 760 62 S 1220 28, 1440 52 V90 H0 Z" fill="var(--primary)" fill-opacity=".6"/>
  <path d="M0 74 C 300 62, 520 90, 800 80 S 1240 58, 1440 74 V90 H0 Z" fill="var(--primary)"/>
</svg>"""

PHERO = """<section class="phero">
  <div class="wrap">
    {crumbs}
    <div class="eyebrow"><span class="eyebrow-line"></span>{eyebrow}</div>
    <h1>{h1}</h1>
    {lead}
    {actions}
  </div>
  """ + STRATA + """
</section>"""


# Set to True (and replace brand/logo/*.svg) once the final logo is adopted.
SHOW_LOGO = False
NAV_MARK = None
FOOTER_LOGO = None


def hex_rgb(h):
    h = h.lstrip("#")
    return "%d,%d,%d" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


BAND_LIGHT_CSS = """/* light header band (theme.json "band": "light") */
html[data-band="light"] .hero,html[data-band="light"] .phero{background:var(--band-bg);border-bottom:1px solid var(--border)}
html[data-band="light"] .hero-glow,html[data-band="light"] .phero::after{display:none}
html[data-band="light"] .hero h1,html[data-band="light"] .phero h1{color:var(--primary-dk)}
html[data-band="light"] .hero h1 em{color:var(--accent)}
html[data-band="light"] .hero-kicker{color:var(--accent-dk);background:var(--accent-lt);border-color:rgba(var(--accent-rgb),.35)}
html[data-band="light"] .hero-lead,html[data-band="light"] .phero-lead{color:var(--ink-2);font-weight:400}
html[data-band="light"] .hero .btn-ghost,html[data-band="light"] .phero .btn-ghost{background:#fff;border-color:var(--border-dk);color:var(--primary-dk)}
html[data-band="light"] .hero .btn-ghost:hover,html[data-band="light"] .phero .btn-ghost:hover{background:var(--sand)}
html[data-band="light"] .hstat-n{color:var(--primary-dk)}
html[data-band="light"] .hstat-n em{color:var(--accent)}
html[data-band="light"] .hstat-l{color:var(--muted)}
html[data-band="light"] .hero-right{background:#fff;border-color:var(--border)}
html[data-band="light"] .hbul-head{color:var(--muted);border-bottom-color:var(--border)}
html[data-band="light"] .hbul-live{color:var(--muted)}
html[data-band="light"] .hbul-item{border-bottom-color:var(--border)}
html[data-band="light"] .hbul-item:hover{background:var(--sand)}
html[data-band="light"] .hbul-title{color:var(--primary-dk)}
html[data-band="light"] .hbul-sub{color:var(--muted)}
html[data-band="light"] .phero .eyebrow{color:var(--accent-dk)}
html[data-band="light"] .phero .eyebrow-line{background:var(--accent)}
html[data-band="light"] .crumbs{color:var(--muted)}
html[data-band="light"] .crumbs a{color:var(--ink-2)}
html[data-band="light"] .crumbs a:hover{color:var(--primary-dk)}
"""


THEME_INFO = {}


def theme_vars(th):
    keys = ["primary-dk", "primary", "primary-md", "primary-lt", "primary-lt2", "accent", "accent-dk", "accent-lt",
            "accent-pale", "accent-hi", "sand", "border", "border-dk", "ink", "ink-2", "muted", "muted-lt",
            "link", "link-lt", "on-dark-link"]
    out = ["--%s:%s" % (k, th[k]) for k in keys]
    out += ["--%s-rgb:%s" % (k, hex_rgb(th[k])) for k in ["primary", "primary-dk", "primary-md", "accent", "link"]]
    L = th["logo"]
    pale = "#" + "".join("%02X" % round(int(th["primary"][i:i + 2], 16) * .3 + 255 * .7) for i in (1, 3, 5))
    out += ["--logo-wall:%s" % L["wall"], "--logo-s0:%s" % L["strata"][0], "--logo-s1:%s" % L["strata"][1],
            "--logo-r0:%s" % L["rev_strata"][0], "--logo-pale:%s" % pale, "--logo-accent:%s" % L["accent"],
            "--logo-accent-hi:%s" % L["accent_hi"], "--band-bg:%s" % th.get("band-bg", th["primary-dk"])]
    return ";".join(out)


def load_theme():
    """Read theme.json and write assets/theme.css (every theme, active one as default) and
    assets/themes.js (labels for the on-page theme picker)."""
    with open(os.path.join(ROOT, "theme.json"), encoding="utf-8") as fh:
        t = json.load(fh)
    active = t["active"]
    th = t["themes"][active]
    lines = ["/* generated from theme.json — default theme: %s (%s). Do not edit; edit theme.json and rebuild. */" % (active, th["label"]),
             ":root{%s}" % theme_vars(th)]
    for key, tv in t["themes"].items():
        lines.append('html[data-theme="%s"]{%s}' % (key, theme_vars(tv)))
    lines.append(BAND_LIGHT_CSS)
    with open(os.path.join(ROOT, "assets", "theme.css"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    light = [k for k, v in t["themes"].items() if v.get("band") == "light"]
    picker = [{"k": k, "n": v["label"], "c": v["primary-dk"], "a": v["accent"], "l": v.get("band") == "light"}
              for k, v in t["themes"].items()]
    with open(os.path.join(ROOT, "assets", "themes.js"), "w", encoding="utf-8") as fh:
        fh.write("window.USUCGER_THEMES=" + json.dumps({"default": active, "list": picker}, ensure_ascii=False) + ";\n")
    THEME_INFO.update(theme_key=active, theme_band="light" if th.get("band") == "light" else "dark",
                      light_keys=json.dumps(light), all_keys=json.dumps(list(t["themes"])))
    return active, th


def load_brand():
    global NAV_MARK, FOOTER_LOGO
    if not SHOW_LOGO:
        # placeholder logo withdrawn until the final USUCGER logo is adopted: text-only brand
        NAV_MARK = ""
        FOOTER_LOGO = '<strong>USUCGER</strong><span class="ft-tag">Geotechnical Education &amp; Research</span>'
        return
    NAV_MARK = inline_svg("usucger-mark.svg", "Nav", "nav-mark", 'aria-hidden="true" focusable="false"')
    FOOTER_LOGO = inline_svg("usucger-logo-horizontal-reversed.svg", "Ft", "ft-logo", 'aria-hidden="true" focusable="false"')
    # footer lockup: drop the solid background rect so it sits on the footer colour
    FOOTER_LOGO = re.sub(r'<rect width="100%" height="100%" fill="var\(--logo-wall\)"/>', "", FOOTER_LOGO)


def notices_html():
    path = os.path.join(PAGES_DIR, "partials", "notices.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    return NOTICES


def build_page(slug, meta, body):
    if slug == "index.html":
        hero = ""
    else:
        lead = '<p class="phero-lead">%s</p>' % meta["lead"] if meta.get("lead") else ""
        actions = ""
        if meta.get("actions"):
            btns = "".join(
                '<a href="%s"%s class="btn %s">%s</a>' % (h, link_attrs(h), c, t)
                for t, h, c in meta["actions"]
            )
            actions = '<div class="phero-actions">%s</div>' % btns
        hero = PHERO.format(
            crumbs=crumbs_html(meta.get("crumbs", [])),
            eyebrow=meta.get("eyebrow", "USUCGER"),
            h1=meta.get("h1", meta["title"]),
            lead=lead,
            actions=actions,
        )
    cta = ""
    if meta.get("cta", True):
        cta = CTA_STRIP.format(
            heading=meta.get("cta_heading", "Be part of the geotechnical academic community"),
            sub=meta.get(
                "cta_sub",
                "Membership is $75 per person for the 2025&ndash;2027 cycle and open to faculty, "
                "researchers, students and practitioners with a stake in geotechnical education and research.",
            ),
        )
    return SHELL.format(
        title=meta["title"],
        description=meta["description"],
        notices=notices_html(),
        nav=nav_html(slug),
        drawer=drawer_html(slug),
        body=hero + "\n" + body,
        cta=cta,
        footer_links=footer_links_html(),
        contact=CONTACT,
        board_email=BOARD_EMAIL,
        nav_mark=NAV_MARK,
        footer_logo=FOOTER_LOGO,
        icon_links=('<link rel="icon" type="image/svg+xml" href="assets/brand/usucger-icon.svg">\n<link rel="apple-touch-icon" href="assets/brand/usucger-icon.svg">\n') if SHOW_LOGO else "",
        **THEME_INFO,
    )


def strip_tags(html):
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"&[a-z#0-9]+;", " ", html)
    return re.sub(r"\s+", " ", html).strip()


def build_search_index(manifest, bodies):
    """One entry per page plus one per h2/h3 section, so results land on the right anchor."""
    entries = []
    for slug, meta in manifest.items():
        title = strip_tags(meta.get("h1", meta["title"])).replace("— USUCGER", "").strip()
        body = bodies.get(slug, "")
        text = strip_tags(body)
        entries.append({"t": title, "u": slug, "s": strip_tags(meta.get("description", ""))[:160], "k": text[:1500].lower(), "p": 1})
        for m in re.finditer(r'<h([23])[^>]*?(?:id="([^"]+)")?[^>]*>(.*?)</h\1>', body, flags=re.S):
            hid, htxt = m.group(2), strip_tags(m.group(3))
            if not htxt or len(htxt) > 90:
                continue
            after = strip_tags(body[m.end(): m.end() + 600])
            entries.append({"t": htxt, "u": slug + ("#" + hid if hid else ""), "s": title, "k": (htxt + " " + after).lower()[:600]})
    # searchable data rows: members and universities
    try:
        with open(os.path.join(ROOT, "data", "members.txt"), encoding="utf-8") as fh:
            for line in fh:
                parts = [x.strip() for x in line.strip().split("|")]
                if len(parts) == 3 and parts[1]:
                    entries.append({"t": "%s %s" % (parts[0], parts[1]), "u": "directory.html", "s": parts[2] + " · Membership directory", "k": (" ".join(parts)).lower()})
        with open(os.path.join(ROOT, "data", "universities.txt"), encoding="utf-8") as fh:
            for line in fh:
                parts = [x.strip() for x in line.strip().split("|")]
                if parts and parts[0]:
                    entries.append({"t": parts[0], "u": "universities.html", "s": "Member university" + (" · contact: " + parts[1] if len(parts) > 1 and parts[1] else ""), "k": (" ".join(parts)).lower()})
    except FileNotFoundError:
        pass
    with open(os.path.join(ROOT, "assets", "search-index.js"), "w", encoding="utf-8") as fh:
        fh.write("window.USUCGER_INDEX=" + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";\n")
    return len(entries)


def main():
    active, _ = load_theme()
    print("theme:", active)
    load_brand()
    with open(os.path.join(ROOT, "pages.json"), "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    built = []
    bodies = {}
    for slug, meta in manifest.items():
        src = os.path.join(PAGES_DIR, slug)
        if not os.path.exists(src):
            print("  !! missing body: pages/%s" % slug, file=sys.stderr)
            continue
        with open(src, "r", encoding="utf-8") as fh:
            body = fh.read()
        for inc in re.findall(r"<!--include:([\w.-]+)-->", body):
            with open(os.path.join(PAGES_DIR, "partials", inc), "r", encoding="utf-8") as fh:
                body = body.replace("<!--include:%s-->" % inc, fh.read())
        bodies[slug] = body
        html = build_page(slug, meta, body)
        with open(os.path.join(OUT_DIR, slug), "w", encoding="utf-8") as fh:
            fh.write(html)
        built.append(slug)
    n = build_search_index(manifest, bodies)
    cache_bust(built)
    print("Built %d pages, search index %d entries" % (len(built), n))


def cache_bust(pages):
    """Add ?v=<content hash> to shared CSS/JS links so browsers fetch new versions right away."""
    import hashlib
    vers = {}
    for a in ["site.css", "theme.css", "site.js", "themes.js", "search-index.js"]:
        with open(os.path.join(ROOT, "assets", a), "rb") as fh:
            vers[a] = hashlib.md5(fh.read()).hexdigest()[:8]
    for slug in pages:
        path = os.path.join(OUT_DIR, slug)
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        for a, v in vers.items():
            html = html.replace('"assets/%s"' % a, '"assets/%s?v=%s"' % (a, v))
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)


if __name__ == "__main__":
    main()
