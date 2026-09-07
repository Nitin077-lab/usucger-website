#!/usr/bin/env python3
"""
USUCGER logo generator.

Produces a family of pure-vector SVG files with all text converted to outlines,
so the files print identically on any machine with no fonts installed.

    python3 brand/make_logo.py
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.environ.get(
    "FONT_DIR",
    "/tmp/claude-0/-home-claude/8ca2c76d-0319-57d9-892a-a1947be1486f/scratchpad/fonts/package/files",
)
OUT = os.path.join(HERE, "logo")
os.makedirs(OUT, exist_ok=True)

import json as _json
with open(os.path.join(os.path.dirname(HERE), "theme.json"), encoding="utf-8") as _fh:
    _T = _json.load(_fh)
_L = _T["themes"][_T["active"]]["logo"]
COBALT_DK = _L["dark"]                 # wall / wordmark
COBALT_MD, COBALT, _deep = _L["strata"]  # strata, top to bottom
COBALT_LT = _L["rev_strata"][0]
REV_STRATA = tuple(_L["rev_strata"])
AMBER = _L["accent"]
AMBER_HI = _L["accent_hi"]
WHITE = "#FFFFFF"
INK = "#181818"
print("logo colours from theme:", _T["active"])

# --------------------------------------------------------------------- text
_cache = {}


def font(name):
    if name not in _cache:
        _cache[name] = TTFont(os.path.join(FONTS, name))
    return _cache[name]


def text_path(text, fontfile, size, x=0, y=0, tracking=0.0):
    """Return (svg path d, advance width) for `text` set in `fontfile` at `size`
    px with baseline at (x, y). tracking is in em units (e.g. 0.02)."""
    f = font(fontfile)
    upem = f["head"].unitsPerEm
    scale = size / upem
    cmap = f.getBestCmap()
    glyphs = f.getGlyphSet()
    hmtx = f["hmtx"]
    # simple GPOS-free kerning via 'kern' table when present
    kern = {}
    if "kern" in f:
        for st in f["kern"].kernTables:
            kern.update(getattr(st, "kernTable", {}))
    d = []
    pen_x = x
    prev = None
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            pen_x += size * 0.3
            prev = None
            continue
        if prev and (prev, gname) in kern:
            pen_x += kern[(prev, gname)] * scale
        spen = SVGPathPen(glyphs)
        tpen = TransformPen(spen, (scale, 0, 0, -scale, pen_x, y))
        glyphs[gname].draw(tpen)
        cmd = spen.getCommands()
        if cmd:
            d.append(cmd)
        pen_x += hmtx[gname][0] * scale + tracking * size
        prev = gname
    return " ".join(d), pen_x - x


# --------------------------------------------------------------------- mark
def mark(x=0, y=0, s=1.0, wall=COBALT_DK, strata=(COBALT_MD, COBALT, COBALT_DK),
         accent=AMBER, sky=WHITE, mono=False, id_suffix=""):
    """The USUCGER mark in a 100x100 box, placed at (x,y) scaled by s.

    Reading of the mark: a U-shaped basin of ground whose interior shows
    curved sedimentary strata (a syncline), with an amber horizon at the ground
    surface and an amber sounding rod with a cone tip driven through the layers
    — the cone penetration test, the community's signature site investigation.
    U for Universities; the ground for geotechnics; the probe for research;
    the layers for the depth of education."""
    cid = "uInner" + id_suffix
    if mono:
        # single colour: strata rendered as tints of the wall colour
        s1, s2, s3 = wall, wall, wall
        op = (0.42, 0.62, 0.82)
        accent = wall
        horizon = wall
    else:
        s1, s2, s3 = strata
        op = (1, 1, 1)
        horizon = accent
    g = []
    g.append('<g transform="translate(%g %g) scale(%g)">' % (x, y, s))
    g.append('<defs><clipPath id="%s"><path d="M28 10 V56 A22 22 0 0 0 72 56 V10 Z"/></clipPath></defs>' % cid)
    # sky (interior above horizon)
    g.append('<path d="M28 10 V56 A22 22 0 0 0 72 56 V10 Z" fill="%s"/>' % sky)
    # strata, clipped to interior — each band is a sagging arc (syncline)
    g.append('<g clip-path="url(#%s)">' % cid)
    g.append('<path d="M20 34 Q50 50 80 34 V90 H20 Z" fill="%s" fill-opacity="%g"/>' % (s1, op[0]))
    g.append('<path d="M20 47 Q50 63 80 47 V90 H20 Z" fill="%s" fill-opacity="%g"/>' % (s2, op[1]))
    g.append('<path d="M20 60 Q50 76 80 60 V90 H20 Z" fill="%s" fill-opacity="%g"/>' % (s3, op[2]))
    # thin light partings between beds
    for yy in (34, 47, 60):
        g.append('<path d="M20 %d Q50 %d 80 %d" fill="none" stroke="%s" stroke-opacity=".55" stroke-width="1.6"/>' % (yy, yy + 16, yy, sky))
    g.append('</g>')
    # horizon line (ground surface) — sits at the top of the first bed
    g.append('<path d="M28 33.2 Q50 49.2 72 33.2" fill="none" stroke="%s" stroke-width="3.2" stroke-linecap="round"/>' % horizon)
    # the U wall
    g.append('<path d="M16 8 V56 A34 34 0 0 0 84 56 V8 H72 V56 A22 22 0 0 1 28 56 V8 Z" fill="%s"/>' % wall)
    # sounding rod with cone tip, driven through the beds
    g.append('<path d="M46.6 2 H53.4 V63 L50 71 L46.6 63 Z" fill="%s"/>' % accent)
    g.append('<rect x="40" y="0" width="20" height="5.2" rx="1.6" fill="%s"/>' % accent)
    g.append('</g>')
    return "\n".join(g)


def svg(width, height, body, bg=None, title="USUCGER"):
    title = title.replace("&", "&amp;")
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%g" height="%g" role="img" aria-label="%s">'
             % (width, height, width, height, title)]
    parts.append("<title>%s</title>" % title)
    if bg:
        parts.append('<rect width="100%%" height="100%%" fill="%s"/>' % bg)
    parts.append(body)
    parts.append("</svg>")
    return "\n".join(parts)


def write(name, content):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("  wrote", os.path.relpath(p, HERE))


FRA = "fraunces-latin-700-normal.woff"
FIG = "figtree-latin-600-normal.woff"
FIG7 = "figtree-latin-700-normal.woff"

TAGLINE = "UNITED STATES UNIVERSITIES COUNCIL ON GEOTECHNICAL EDUCATION AND RESEARCH"
SHORT = "GEOTECHNICAL EDUCATION & RESEARCH"


def horizontal(word_fill, tag_fill, mark_kwargs, bg=None, name="", tagline=SHORT, id_suffix=""):
    # mark 100 tall at left; word set at 62px; tagline under it
    wd, ww = text_path("USUCGER", FRA, 64, tracking=-0.015)
    td, tw = text_path(tagline, FIG7, 12.6, tracking=0.17)
    gap = 22
    total_w = 100 + gap + max(ww, tw) + 6
    H = 100
    body = [mark(0, 0, 1.0, id_suffix=id_suffix, **mark_kwargs)]
    body.append('<path transform="translate(%g %g)" d="%s" fill="%s"/>' % (100 + gap, 58, wd, word_fill))
    body.append('<path transform="translate(%g %g)" d="%s" fill="%s"/>' % (100 + gap + 1.5, 82, td, tag_fill))
    return svg(total_w, H, "\n".join(body), bg=bg, title="USUCGER — " + tagline.title())


def stacked(word_fill, tag_fill, mark_kwargs, bg=None, id_suffix=""):
    """Mark above the wordmark, full name set on two lines beneath a rule."""
    wd, ww = text_path("USUCGER", FRA, 58, tracking=-0.015)
    l1, w1 = text_path("UNITED STATES UNIVERSITIES COUNCIL ON", FIG7, 9.6, tracking=0.18)
    l2, w2 = text_path("GEOTECHNICAL EDUCATION AND RESEARCH", FIG7, 9.6, tracking=0.18)
    W = max(ww, w1, w2) + 48
    y_word = 100 + 24 + 46
    y_rule = y_word + 14
    y_l1 = y_rule + 19
    y_l2 = y_l1 + 15
    H = y_l2 + 12
    rule = AMBER if not mark_kwargs.get("mono") else tag_fill
    body = [mark((W - 100) / 2, 0, 1.0, id_suffix=id_suffix, **mark_kwargs)]
    body.append('<path transform="translate(%g %g)" d="%s" fill="%s"/>' % ((W - ww) / 2, y_word, wd, word_fill))
    body.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="1.6"/>' % (W / 2 - 28, y_rule, W / 2 + 28, y_rule, rule))
    body.append('<path transform="translate(%g %g)" d="%s" fill="%s"/>' % ((W - w1) / 2, y_l1, l1, tag_fill))
    body.append('<path transform="translate(%g %g)" d="%s" fill="%s"/>' % ((W - w2) / 2, y_l2, l2, tag_fill))
    return svg(W, H, "\n".join(body), bg=bg, title="USUCGER — " + TAGLINE.title())


def main():
    print("Generating logo family →", OUT)
    full = dict(wall=COBALT_DK, strata=(COBALT_MD, COBALT, _deep), accent=AMBER, sky=WHITE)
    rev = dict(wall=WHITE, strata=REV_STRATA, accent=AMBER_HI, sky=COBALT_DK)
    mono_dark = dict(wall=INK, mono=True, sky=WHITE)
    mono_white = dict(wall=WHITE, mono=True, sky="none")

    # 1. mark alone
    write("usucger-mark.svg", svg(100, 100, mark(**full), title="USUCGER mark"))
    write("usucger-mark-reversed.svg", svg(100, 100, mark(**rev), bg=COBALT_DK, title="USUCGER mark (reversed)"))
    write("usucger-mark-mono-black.svg", svg(100, 100, mark(**mono_dark), title="USUCGER mark (black)"))
    write("usucger-mark-mono-white.svg", svg(100, 100, mark(**mono_white), title="USUCGER mark (white)"))

    # 2. horizontal lockups
    write("usucger-logo-horizontal.svg", horizontal(COBALT_DK, AMBER, full))
    write("usucger-logo-horizontal-reversed.svg", horizontal(WHITE, AMBER_HI, rev, bg=COBALT_DK))
    write("usucger-logo-horizontal-mono-black.svg", horizontal(INK, INK, mono_dark))
    write("usucger-logo-horizontal-mono-white.svg", horizontal(WHITE, WHITE, mono_white))
    write("usucger-logo-horizontal-fullname.svg", horizontal(COBALT_DK, AMBER, full, tagline=TAGLINE))

    # 3. stacked lockups
    write("usucger-logo-stacked.svg", stacked(COBALT_DK, COBALT, full))
    write("usucger-logo-stacked-reversed.svg", stacked(WHITE, "#B9CCEB", rev, bg=COBALT_DK))
    write("usucger-logo-stacked-mono-black.svg", stacked(INK, INK, mono_dark))

    # 4. favicon / app icon: mark on rounded cobalt tile
    tile = ['<rect width="100" height="100" rx="20" fill="%s"/>' % COBALT_DK, mark(12, 12, 0.76, **rev)]
    write("usucger-icon.svg", svg(100, 100, "\n".join(tile), title="USUCGER icon"))

    # 5. inline-nav version (mark only, small, full colour) is the same as the mark
    print("done")


if __name__ == "__main__":
    main()
