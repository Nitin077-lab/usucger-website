#!/usr/bin/env python3
"""Member map with real state boundaries.

Inputs
  data/us-states.json          pre-projected (Albers USA, 975x610) SVG paths per state,
                               built from the us-atlas 10m TopoJSON
  data/universities.txt        member institutions
  data/university_states.txt   institution -> state
  data/members.txt             membership directory (First|Last|Affiliation)

Output
  pages/partials/member-map.html   SVG map + side panel + inline data

Members are matched to institutions by normalised affiliation name; a few
affiliations that are not member institutions are placed in a state directly
(see OTHER_STATE). States are shaded by NUMBER OF MEMBERS.

    python3 gen_map.py
"""
import json
import os
import re
from collections import OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
PARTIALS = os.path.join(ROOT, "pages", "partials")

ALIASES = {
    "University of Arkansas Fayetteville": "University of Arkansas",
    "MIT": "Massachusetts Institute of Technology",
    "California State University of Los Angeles": "California State University-Los Angeles",
    "Marian University, Indianapolis": "Marian University",
}
# affiliations that are not member institutions but sit in a known state
OTHER_STATE = {
    "Deep Foundations Institute": "NJ",
    "Portland State University": "OR",
    "AGR, LLC / Turner-Fairbank Highway Research Center": "VA",
    "Brigham Young University – Idaho": "ID",
    "GRL Engineers, Inc.": "OH",
    "Geosetta": "MD",
    "Menard USA": "PA",
    "Terracon Consultants, Inc.": "KS",
    "West Virginia University Institute of Technology": "WV",
}
INTL_HINTS = ("University of British Columbia", "University of Technology Sydney", "Wuhan University")
NAMES = {"AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DC": "District of Columbia", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "IA": "Iowa", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "MA": "Massachusetts", "MD": "Maryland", "ME": "Maine", "MI": "Michigan", "MN": "Minnesota", "MO": "Missouri", "MS": "Mississippi", "MT": "Montana", "NC": "North Carolina", "ND": "North Dakota", "NE": "Nebraska", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NV": "Nevada", "NY": "New York", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "PR": "Puerto Rico", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VA": "Virginia", "VT": "Vermont", "WA": "Washington", "WI": "Wisconsin", "WV": "West Virginia", "WY": "Wyoming", "INTL": "International"}
SMALL = {"CT", "RI", "DE", "DC", "MD", "NJ", "NH", "VT", "MA"}  # no inline label


def norm(s):
    s = s.lower().replace("&", "and")
    s = re.sub(r"[–—\-,/()]", " ", s)
    s = re.sub(r"\b(the|at)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------- load data
unis = [l.rstrip("\n").split("|") for l in open(os.path.join(DATA, "universities.txt"), encoding="utf-8") if l.strip()]
uni_state = dict(l.rstrip("\n").split("|") for l in open(os.path.join(DATA, "university_states.txt"), encoding="utf-8") if l.strip())
by_norm = {}
for name, _contact in unis:
    by_norm.setdefault(norm(name), name)

members = [l.rstrip("\n").split("|") for l in open(os.path.join(DATA, "members.txt"), encoding="utf-8") if l.strip()]

# state -> {unis: {uni: [members]}, other: {aff: [members]}}
S = {}
for st in NAMES:
    S[st] = {"unis": OrderedDict(), "other": OrderedDict()}
for name, contact in unis:
    S[uni_state[name]]["unis"][name] = []

unassigned = []
for first, last, aff in members:
    full = ("%s %s" % (first, last)).strip()
    a = ALIASES.get(aff, aff)
    key = norm(a)
    if key in by_norm:
        u = by_norm[key]
        S[uni_state[u]]["unis"][u].append(full)
    elif aff in OTHER_STATE:
        S[OTHER_STATE[aff]]["other"].setdefault(aff, []).append(full)
    elif aff in INTL_HINTS:
        S["INTL"]["other"].setdefault(aff, []).append(full)
    else:
        unassigned.append((full, aff))

geo = json.load(open(os.path.join(DATA, "us-states.json"), encoding="utf-8"))


def count(st):
    return sum(len(v) for v in S[st]["unis"].values()) + sum(len(v) for v in S[st]["other"].values())


def level(n):
    return 0 if n == 0 else 1 if n <= 3 else 2 if n <= 8 else 3 if n <= 15 else 4


# ---------------------------------------------------------------- SVG
paths, labels = [], []
for st, g in geo["states"].items():
    n = count(st)
    nu = len(S[st]["unis"])
    paths.append('<path class="st l%d" d="%s" data-st="%s" tabindex="0" role="button" aria-label="%s: %d member%s at %d institution%s"/>'
                 % (level(n), g["d"], st, NAMES[st], n, "" if n == 1 else "s", nu, "" if nu == 1 else "s"))
    if st not in SMALL:
        cx, cy = g["c"]
        labels.append('<text class="st-lbl%s" x="%d" y="%d">%s</text>' % (" on-dark" if level(n) >= 3 else "", cx, cy + 4, st))
        if n:
            labels.append('<text class="st-n%s" x="%d" y="%d">%d</text>' % (" on-dark" if level(n) >= 3 else "", cx, cy + 16, n))

svg = ('<svg class="usmap" viewBox="0 0 %d %d" role="group" aria-label="USUCGER members by state">'
       '<g class="states">%s</g><g class="labels" aria-hidden="true">%s</g></svg>'
       % (geo["w"], geo["h"], "".join(paths), "".join(labels)))

# side chips for places not on the Albers map
chips = []
for st in ("PR", "INTL"):
    n = count(st)
    chips.append('<button type="button" class="chip l%d" data-st="%s">%s <b>%d</b></button>' % (level(n), st, NAMES[st], n))

# ---------------------------------------------------------------- data + panel
data = {}
for st in NAMES:
    d = {"name": NAMES[st], "n": count(st), "unis": [], "other": []}
    for u, ms in sorted(S[st]["unis"].items(), key=lambda kv: (-len(kv[1]), kv[0])):
        d["unis"].append({"n": u, "m": sorted(ms, key=lambda x: x.split()[-1])})
    for a, ms in sorted(S[st]["other"].items(), key=lambda kv: (-len(kv[1]), kv[0])):
        d["other"].append({"n": a, "m": sorted(ms, key=lambda x: x.split()[-1])})
    data[st] = d

total_members = len(members)
placed = total_members - len(unassigned)
n_states = sum(1 for st in NAMES if st not in ("INTL",) and count(st) > 0)
n_unis = len(unis)
top = sorted(((count(st), st) for st in NAMES if st != "INTL"), reverse=True)[:4]

MAP = """<div class="map-wrap">
  <div class="map-stage">
    %(svg)s
    <div class="map-chips">%(chips)s</div>
    <div class="map-legend"><span><i class="l0"></i>no members</span><span><i class="l1"></i>1&ndash;3</span><span><i class="l2"></i>4&ndash;8</span><span><i class="l3"></i>9&ndash;15</span><span><i class="l4"></i>16+</span></div>
  </div>
  <div class="map-panel" id="mapPanel">
    <div class="mp-head"><div class="mp-title" id="mpTitle">%(placed)d members &middot; %(n_states)d states</div><div class="mp-sub" id="mpSub">%(n_unis)d member institutions &middot; hover or tap a state</div></div>
    <div class="mp-body" id="mpBody"><p class="mp-hint">Shading shows how many USUCGER members are in each state. Leading states: %(top)s. Click a state to pin it and expand an institution to see its members.</p></div>
    <div class="mp-foot"><a href="directory.html">Full membership directory &rarr;</a><a href="universities.html">Member universities &amp; contacts &rarr;</a></div>
  </div>
</div>
<script>window.USUCGER_MAP=%(data)s;</script>
""" % {
    "svg": svg, "chips": "".join(chips), "placed": placed, "n_states": n_states, "n_unis": n_unis,
    "top": ", ".join("%s (%d)" % (NAMES[st], n) for n, st in top),
    "data": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
}
os.makedirs(PARTIALS, exist_ok=True)
with open(os.path.join(PARTIALS, "member-map.html"), "w", encoding="utf-8") as fh:
    fh.write(MAP)

print("map: %d members placed of %d (%d unassigned: %s); %d states with members; svg+data %.0f KB"
      % (placed, total_members, len(unassigned), ", ".join(a or "(blank)" for _, a in unassigned), n_states, len(MAP) / 1024))
