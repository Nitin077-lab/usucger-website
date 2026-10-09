#!/usr/bin/env python3
"""Recolour the logo SVGs for the active theme without needing the source fonts.

brand/logo/*.svg are the Strata masters. This maps each Strata colour to the
active theme's logo colours and writes the results to assets/brand/, which is
what build.py inlines. Run:  python3 brand/recolor_logo.py && python3 build.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
t = json.load(open(os.path.join(ROOT, "theme.json"), encoding="utf-8"))
th = t["themes"][t["active"]]
L = th["logo"]

def mix(a, b, w):
    a, b = a.lstrip("#"), b.lstrip("#")
    return "#%02X%02X%02X" % tuple(round(int(a[i:i+2], 16) * (1 - w) + int(b[i:i+2], 16) * w) for i in (0, 2, 4))

MAP = {
    "#102747": L["wall"],
    "#1B3F6E": L["strata"][1],
    "#2554A0": L["strata"][0],
    "#5B86CC": L["rev_strata"][0],
    "#B9CCEB": mix(th["primary"], "#FFFFFF", 0.7),
    "#C47A1A": L["accent"],
    "#FCD87A": L["accent_hi"],
}
pat = re.compile("|".join(re.escape(k) for k in MAP), re.I)
src, dst = os.path.join(HERE, "logo"), os.path.join(ROOT, "assets", "brand")
for name in sorted(os.listdir(src)):
    if not name.endswith(".svg"):
        continue
    svg = open(os.path.join(src, name), encoding="utf-8").read()
    svg = pat.sub(lambda m: MAP[m.group(0).upper()], svg)
    open(os.path.join(dst, name), "w", encoding="utf-8").write(svg)
print("logo recoloured for theme:", t["active"])
