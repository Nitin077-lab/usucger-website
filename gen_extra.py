#!/usr/bin/env python3
"""Awards, deadlines, member map and notice ticker — generated from data/*.json.

  data/awards.json            -> pages/awards.html, pages/partials/awards-module.html
  data/deadlines.json         -> pages/partials/deadlines-card.html, pages/partials/notices.html
  data/university_states.txt  -> pages/partials/member-map.html

    python3 gen_extra.py
"""
import json
import os
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
PARTIALS = os.path.join(ROOT, "pages", "partials")
os.makedirs(PARTIALS, exist_ok=True)


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def w(name, content, where=PARTIALS):
    with open(os.path.join(where, name), "w", encoding="utf-8") as fh:
        fh.write(content)


# ====================================================================== AWARDS
A = json.load(open(os.path.join(DATA, "awards.json"), encoding="utf-8"))
FY = A["featured_year"]


def crop_style(crop):
    # the 2026 winners composite: two portraits side by side in the top half
    return "left:-4.5%;top:-4.5%" if crop == "left" else "left:-113%;top:-4.5%"


def winner_photo(f, size_cls=""):
    """Local file first; fall back to a cropped view of the composite on the current site."""
    ini = "".join(p[0] for p in f["name"].replace("-", " ").split()[:2]).upper()
    return (
        '<div class="win-photo %s"><img src="%s" alt="%s" loading="lazy" '
        "onerror=\"if(!this.dataset.f){this.dataset.f=1;this.src='%s';this.className='composite';this.style.cssText='%s'}else{this.style.display='none';this.parentNode.insertAdjacentHTML('beforeend','<span class=init>%s</span>')}\"></div>"
        % (size_cls, f["photo"], esc(f["name"]), f["composite"], crop_style(f["crop"]), ini)
    )


featured_cards = "".join(
    '<div class="winner-card">%s<div class="winner-body"><div class="winner-year">%d recipient</div>'
    '<div class="winner-name">%s</div><div class="winner-award">%s</div><div class="winner-inst">%s</div></div></div>'
    % (winner_photo(f), FY, esc(f["name"]), esc(f["award"]), esc(f["inst"]))
    for f in A["featured"]
)

# all recipients flattened for the timeline
rows = []
for aw in A["awards"]:
    for name, year, inst in aw["recipients"]:
        rows.append((year, name, inst, aw["key"], aw["name"], aw["active"]))
rows.sort(key=lambda r: (-r[0], r[4], r[1]))
years = sorted({r[0] for r in rows}, reverse=True)

timeline = []
cur = None
for year, name, inst, key, aname, active in rows:
    if year != cur:
        cur = year
        timeline.append('<div class="tl-year" data-year="%d">%d</div>' % (year, year))
    timeline.append(
        '<div class="tl-item aw-row%s" data-award="%s" data-year="%d" data-name="%s"><span class="tl-date">%s</span>'
        '<span class="tl-kind">%s%s</span>%s</div>'
        % ("" if active else " legacy", key, year, esc(name).lower(), esc(name),
           esc(aname), "" if active else " &dagger;",
           ('<span class="tl-inst">%s</span>' % esc(inst)) if inst else "")
    )

active_awards = [a for a in A["awards"] if a["active"]]
legacy = [a for a in A["awards"] if not a["active"]]

ICONS = {
    "ecr": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h12"/><path d="M8 18v-2a4 4 0 0 1 8 0v2"/><path d="M10 6l4 4"/><path d="M8.5 7.5 13 3l3 3-4.5 4.5z"/><path d="M6 14l3-3"/></svg>',
    "ece": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5h6a3 3 0 0 1 3 3v11a2 2 0 0 0-2-2H3z"/><path d="M21 5h-6a3 3 0 0 0-3 3v11a2 2 0 0 1 2-2h7z"/></svg>',
    "dsa": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V10M10 21V10M14 21V10M19 21V10"/><path d="M3 10l9-6 9 6z"/></svg>',
    "dei": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18a14 14 0 0 1 0-18z"/></svg>',
}


def initials_of(name):
    parts = [p for p in name.replace("-", " ").split() if p]
    return (parts[0][0] + parts[-1][0]).upper()


def award_card(a):
    recips = a["recipients"]
    latest_name, latest_year = recips[0][0], recips[0][1]
    first_year = min(r[1] for r in recips)
    feat = next((f for f in A["featured"] if f["name"] == latest_name), None)
    if feat:
        avatar = winner_photo(feat, "mini")
    else:
        avatar = '<span class="win-photo mini"><span class="init">%s</span></span>' % initials_of(latest_name)
    return (
        '<article class="aw-card">'
        '<div class="aw-top"><span class="aw-medal">%s</span><span class="aw-freq">%s</span></div>'
        '<h3 class="aw-title">%s</h3>'
        '<p class="aw-body">%s</p>'
        '<div class="aw-foot">%s<div><div class="aw-latest">%s <span>%d</span></div><div class="aw-count">%d recipient%s since %d</div></div></div>'
        "</article>"
    ) % (ICONS.get(a["key"], ""), a["freq"], esc(a["name"]), a["desc"], avatar,
         esc(latest_name), latest_year, len(recips), "" if len(recips) == 1 else "s", first_year)


award_cards = "".join(award_card(a) for a in active_awards)

filter_btns = '<button class="tab-btn on" data-aw="all">All awards</button>' + "".join(
    '<button class="tab-btn" data-aw="%s">%s</button>' % (a["key"], esc(a["name"]).replace(" Award", ""))
    for a in A["awards"]
)

AWARDS_PAGE = """<section class="section bg-white">
  <div class="wrap">
    <div class="rv" style="margin-bottom:1.4rem">
      <div class="eyebrow"><span class="eyebrow-line"></span>%(fy)d Recipients</div>
      <h2 style="color:var(--cobalt-dk)">Congratulations to this year's honorees</h2>
    </div>
    <div class="winner-grid rv">%(featured)s</div>
  </div>
</section>

<section class="section-lg bg-cobalt-dk" style="position:relative;overflow:hidden">
  <div class="wrap">
    <div class="rv" style="max-width:680px;margin-bottom:2.4rem">
      <div class="eyebrow" style="color:var(--amber-hi)"><span class="eyebrow-line" style="background:var(--amber-hi)"></span>The Awards</div>
      <h2 style="color:#fff">Four awards, one community</h2>
      <p class="sec-sub-light">Honoring outstanding contributions to geotechnical engineering &mdash; from early career breakthroughs to lifetime service and sustained commitment to inclusion.</p>
    </div>
    <div class="aw-grid rv">%(cards)s</div>
  </div>
</section>

<section class="section bg-white" id="history">
  <div class="wrap">
    <div class="split">
      <div class="rv">
        <div style="margin-bottom:1.2rem">
          <div class="eyebrow"><span class="eyebrow-line"></span>Recipient history</div>
          <h2 style="color:var(--cobalt-dk)">Every recipient since 1998</h2>
        </div>
        <div class="tabs" data-awfilter role="tablist" style="margin-bottom:1rem">%(filters)s</div>
        <div class="pos-toolbar">
          <div class="tbl-search"><span class="si" aria-hidden="true">&#128269;</span><input id="awSearch" type="search" placeholder="Search recipients&hellip;" aria-label="Search recipients"></div>
          <div class="tbl-count" id="awCount">%(n)d recipients</div>
        </div>
        <div class="tl" id="awList">
          %(timeline)s
        </div>
        <div class="tbl-empty" id="awEmpty" hidden>No recipients match.</div>
        <div class="legacy-note" style="background:var(--slate);border-color:var(--border);color:var(--muted)">&dagger; <strong style="color:var(--ink-2)">No longer awarded.</strong> The Distinguished Researcher, Distinguished Educator and Research Investment awards have been discontinued. Recipients are listed for historical reference.</div>
      </div>

      <aside class="sticky-aside rv d2">
        <div class="info-callout">
          <div class="ic-head">&#9200; Nominations</div>
          <div class="ic-body" data-deadline="2026-01-15" data-closed="Nominations for the %(fy)d awards have closed. The next call will be announced to members by email and here.">Nominations close <strong>January 15, 2026</strong>. Send to <a href="mailto:uboard@usucger.org?subject=USUCGER%%20Award%%20Nomination">uboard@usucger.org</a>.</div>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128203; Who can be nominated</div>
          <div class="sc-body">
            <p style="font-size:.83rem;line-height:1.7;color:var(--ink-2)"><strong>Early career awards:</strong> tenure-track or tenured faculty at a member institution, no more than 45 years of age and 12 years from the PhD.</p>
            <p style="font-size:.83rem;line-height:1.7;color:var(--ink-2);margin-top:.6rem"><strong>Service and DEI awards:</strong> any affiliate of a member institution, at any rank or position.</p>
          </div>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128202; Frequency</div>
          <div class="sc-body">
            <div class="sc-row"><span class="sc-name">Early Career Researcher</span><span class="sc-date" style="color:var(--cobalt)">2 years</span></div>
            <div class="sc-row"><span class="sc-name">Early Career Educator</span><span class="sc-date" style="color:var(--cobalt)">2 years</span></div>
            <div class="sc-row"><span class="sc-name">Distinguished Service</span><span class="sc-date" style="color:var(--cobalt)">2 years</span></div>
            <div class="sc-row"><span class="sc-name">Diversity, Equity &amp; Inclusion</span><span class="sc-date" style="color:var(--cobalt)">3 years</span></div>
          </div>
        </div>
        <div class="info-callout callout-teal">
          <div class="ic-head">Student travel grants</div>
          <div class="ic-body">The Board also funds student conference travel on its own twice-yearly schedule. <a href="travel-grants.html">Deadlines &amp; eligibility &rarr;</a></div>
        </div>
      </aside>
    </div>
  </div>
</section>

<script>
(function(){
  var btns=document.querySelectorAll('[data-awfilter] .tab-btn'),q=document.getElementById('awSearch'),
      items=[].slice.call(document.querySelectorAll('#awList .aw-row')),yrs=[].slice.call(document.querySelectorAll('#awList .tl-year')),
      count=document.getElementById('awCount'),empty=document.getElementById('awEmpty'),cur='all';
  function apply(){
    var v=(q.value||'').trim().toLowerCase(),n=0,seen={};
    items.forEach(function(it){var ok=(cur==='all'||it.dataset.award===cur)&&(!v||it.dataset.name.indexOf(v)!==-1||it.textContent.toLowerCase().indexOf(v)!==-1);it.hidden=!ok;if(ok){n++;seen[it.dataset.year]=1;}});
    yrs.forEach(function(y){y.hidden=!seen[y.dataset.year];});
    count.textContent=n+' recipient'+(n===1?'':'s');empty.hidden=n>0;
  }
  btns.forEach(function(b){b.addEventListener('click',function(){btns.forEach(function(x){x.classList.toggle('on',x===b)});cur=b.dataset.aw;apply();});});
  q.addEventListener('input',apply);
})();
</script>
"""

w("awards.html", AWARDS_PAGE % {
    "fy": FY, "featured": featured_cards, "cards": award_cards, "filters": filter_btns,
    "n": len(rows), "timeline": "\n          ".join(timeline),
}, where=os.path.join(ROOT, "pages"))

# homepage module
AWARDS_MODULE = """<section class="section-lg bg-cobalt-dk" id="awards" style="position:relative;overflow:hidden">
  <div class="wrap">
    <div class="awards-home rv">
      <div>
        <div class="eyebrow" style="color:var(--amber-hi)"><span class="eyebrow-line" style="background:var(--amber-hi)"></span>Recognition</div>
        <h2 style="color:#fff">%(fy)d award recipients</h2>
        <p class="sec-sub-light">Four awards honor the people who move geotechnical engineering forward &mdash; in research, in the classroom, in service to the Council, and in making the field more inclusive. Recipients go back to 1998.</p>
        <div style="display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1.6rem">
          <a href="awards.html" class="btn btn-amber">All awards &amp; recipient history &rarr;</a>
          <a href="awards.html#history" class="btn btn-ghost">Nominate a colleague</a>
        </div>
      </div>
      <div class="winner-grid dark">%(featured)s</div>
    </div>
  </div>
</section>
"""
w("awards-module.html", AWARDS_MODULE % {"fy": FY, "featured": featured_cards})

# =================================================================== DEADLINES
D = json.load(open(os.path.join(DATA, "deadlines.json"), encoding="utf-8"))


def fmt(iso):
    return date.fromisoformat(iso).strftime("%b %-d, %Y")


card_rows = "".join(
    '<a class="dl-row" href="%s" data-deadline="%s" data-closed="%s"><div class="dl-when"><span class="dl-days">&mdash;</span><span class="dl-unit">days</span></div>'
    '<div class="dl-body"><div class="dl-label">%s</div><div class="dl-detail">%s</div><div class="dl-date">%s</div></div></a>'
    % (d["href"], d["date"], esc(d["closed"]), esc(d["label"]), esc(d["detail"]), fmt(d["date"]))
    for d in D
)
DEADLINES_CARD = """<div class="sidebar-card" id="deadlines">
  <div class="sc-head">&#128197; Deadlines &amp; dates</div>
  <div class="dl-list">%s</div>
  <div class="dl-foot">Countdowns update automatically. Passed dates drop to the bottom.</div>
</div>""" % card_rows
w("deadlines-card.html", DEADLINES_CARD)

# notice ticker: winners + each deadline (JS hides passed ones)
ticker = ['<span class="notice-item" data-notice><span class="bdot" style="background:var(--amber-hi)"></span> <strong>%d Award Winners:</strong> %s &mdash; <a href="awards.html">View awards &rarr;</a></span>'
          % (FY, " &amp; ".join(esc(f["name"]) for f in A["featured"]))]
for d in D:
    ticker.append('<span class="notice-item" data-notice data-deadline="%s">&#9200; <strong>%s:</strong> %s &mdash; <a href="%s">Details &rarr;</a></span>'
                  % (d["date"], esc(d["label"]), fmt(d["date"]), d["href"]))
ticker.append('<span class="notice-item" data-notice>&#128188; <strong>Academic positions</strong> &mdash; free for member institutions to post &mdash; <a href="positions.html">See openings &rarr;</a></span>')
w("notices.html", '<span class="notice-sep">&middot;</span>'.join(ticker) + '<span class="notice-sep">&middot;</span>')

print("awards: %d recipients, featured %d | deadlines: %d" % (len(rows), FY, len(D)))
