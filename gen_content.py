#!/usr/bin/env python3
"""Generate data-driven page bodies from data/*.json:

  data/positions.json  -> pages/positions.html, pages/industry-positions.html,
                          pages/partials/positions-module.html (homepage)
  data/board.json      -> pages/board.html

    python3 gen_content.py
"""
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
PAGES = os.path.join(ROOT, "pages")
PARTIALS = os.path.join(PAGES, "partials")
os.makedirs(PARTIALS, exist_ok=True)

TODAY = date.today()


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%b %-d, %Y")


def age_days(iso):
    return (TODAY - date.fromisoformat(iso)).days


def initials(name):
    parts = [p for p in name.replace("-", " ").split() if p]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


# ------------------------------------------------------------------ positions
with open(os.path.join(DATA, "positions.json"), encoding="utf-8") as fh:
    POS = json.load(fh)

academic = sorted(POS["academic"], key=lambda p: p["posted"], reverse=True)
industry = sorted(POS.get("industry", []), key=lambda p: p["posted"], reverse=True)


def posting_row(p, kind="academic"):
    fresh = age_days(p["posted"]) <= 45
    badge = '<span class="badge badge-amber"><span class="bdot"></span>New</span> ' if fresh else ""
    return (
        '<a class="linkrow pos-row" href="%s" target="_blank" rel="noopener" data-inst="%s" data-title="%s" data-loc="%s">'
        '<div class="linkrow-ic">&#127979;</div>'
        '<div class="linkrow-body">'
        '<div class="linkrow-title">%s%s</div>'
        '<div class="linkrow-desc">%s%s</div>'
        '<div class="linkrow-meta">Posted %s &middot; listing expires %s</div>'
        "</div>"
        '<div class="pos-go" aria-hidden="true">&rarr;</div>'
        "</a>"
    ) % (
        esc(p["url"]), esc(p["institution"]).lower(), esc(p["title"]).lower(), esc(p.get("location", "")).lower(),
        badge, esc(p["institution"]),
        esc(p["title"]), (" &middot; " + esc(p["location"])) if p.get("location") else "",
        fmt_date(p["posted"]), fmt_date(date.fromordinal(date.fromisoformat(p["posted"]).toordinal() + 365).isoformat()),
    )


POSITIONS_PAGE = """<section class="section bg-white">
  <div class="wrap">
    <div class="split">
      <div class="rv">
        <div class="pos-toolbar">
          <div class="tbl-search"><span class="si" aria-hidden="true">&#128269;</span><input id="posSearch" type="search" placeholder="Filter by institution, title or location&hellip;" aria-label="Filter positions"></div>
          <div class="tbl-count" id="posCount">%(n)d open position%(s)s</div>
        </div>
        <div class="linklist" id="posList">
          %(rows)s
        </div>
        <div class="tbl-empty" id="posEmpty" hidden>No positions match that filter.</div>
        <p style="font-size:.79rem;color:var(--muted-lt);margin-top:1rem">Always confirm the closing date on the official posting &mdash; searches sometimes close before a listing is removed here. Listings are removed one year after posting.</p>
      </div>

      <aside class="sticky-aside rv d2">
        <div class="award-box" style="padding:1.6rem 1.7rem">
          <div class="ab-amount" style="font-size:2.4rem">Free</div>
          <div class="ab-label">to post for member institutions</div>
          <div class="ab-body">Email the position title, institution and a link to the official posting to the webmaster. Listings go up within a few days and stay for one year.</div>
          <a href="mailto:webmaster@usucger.org?subject=Academic%%20Position%%20Posting" class="btn btn-amber" style="margin-top:1.1rem">Post a position &rarr;</a>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128188; Industry &amp; practice</div>
          <div class="sc-body">
            <p style="font-size:.83rem;line-height:1.7;color:var(--ink-2)">Looking for, or offering, a role in consulting, contracting or government? Those go on a separate board.</p>
            <a href="industry-positions.html" class="btn btn-outline btn-sm" style="margin-top:.9rem">Industry positions &rarr;</a>
          </div>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128279; For candidates</div>
          <div class="sc-body">
            <a class="sc-link" href="universities.html"><span class="sc-link-ic">&#127979;</span> Member universities</a>
            <a class="sc-link" href="directory.html"><span class="sc-link-ic">&#128101;</span> Membership directory</a>
            <a class="sc-link" href="funding-tips.html"><span class="sc-link-ic">&#128161;</span> Funding tips for new faculty</a>
            <a class="sc-link" href="membership.html"><span class="sc-link-ic">&#128179;</span> Join USUCGER</a>
          </div>
        </div>
        <div class="info-callout callout-grey">
          <div class="ic-head">Why this page exists</div>
          <div class="ic-body">Serving as a clearinghouse for faculty vacancies is one of the Council's standing functions under <a href="bylaws.html#article-iv">Article IV of the By-Laws</a>.</div>
        </div>
      </aside>
    </div>
  </div>
</section>

<script>
(function(){
  var q=document.getElementById('posSearch'),rows=[].slice.call(document.querySelectorAll('#posList .pos-row')),
      count=document.getElementById('posCount'),empty=document.getElementById('posEmpty');
  if(!q)return;
  q.addEventListener('input',function(){
    var v=q.value.trim().toLowerCase(),n=0;
    rows.forEach(function(r){var hit=!v||(r.dataset.inst+' '+r.dataset.title+' '+r.dataset.loc).indexOf(v)!==-1;r.hidden=!hit;if(hit)n++;});
    count.textContent=n+' of '+rows.length+' position'+(rows.length===1?'':'s');empty.hidden=n>0;
  });
})();
</script>
"""

INDUSTRY_PAGE = """<section class="section bg-white">
  <div class="wrap">
    <div class="split">
      <div class="rv">
        %(content)s
      </div>

      <aside class="sticky-aside rv d2">
        <div class="award-box" style="padding:1.6rem 1.7rem">
          <div class="ab-amount" style="font-size:2.4rem">Post</div>
          <div class="ab-label">an industry or agency position</div>
          <div class="ab-body">Send the role title, employer, location and a link to the official posting. Include a closing date if there is one. Listings stay for up to one year.</div>
          <a href="mailto:webmaster@usucger.org?subject=Industry%%20Position%%20Posting" class="btn btn-amber" style="margin-top:1.1rem">Submit a listing &rarr;</a>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#127979; Academic openings</div>
          <div class="sc-body">
            <p style="font-size:.83rem;line-height:1.7;color:var(--ink-2)">Faculty, lecturer and postdoctoral positions at universities are listed on the academic positions board.</p>
            <a href="positions.html" class="btn btn-outline btn-sm" style="margin-top:.9rem">Academic positions &rarr;</a>
          </div>
        </div>
        <div class="info-callout callout-grey">
          <div class="ic-head">Who reads this</div>
          <div class="ic-body">USUCGER's network reaches roughly 500 faculty and their graduate students at 180+ institutions &mdash; the people who will be your next hires.</div>
        </div>
      </aside>
    </div>
  </div>
</section>
"""

EMPTY_STATE = """<div class="empty-state">
  <div class="es-art" aria-hidden="true">
    <svg viewBox="0 0 120 120" width="96" height="96"><defs><clipPath id="esClip"><path d="M34 12 V67 A26 26 0 0 0 86 67 V12 Z"/></clipPath></defs>
      <path d="M34 12 V67 A26 26 0 0 0 86 67 V12 Z" fill="#fff"/>
      <g clip-path="url(#esClip)"><path d="M24 44 Q60 62 96 44 V110 H24Z" fill="var(--primary-md)" opacity=".25"/><path d="M24 60 Q60 78 96 60 V110 H24Z" fill="var(--primary)" opacity=".35"/><path d="M24 76 Q60 94 96 76 V110 H24Z" fill="var(--primary-dk)" opacity=".45"/></g>
      <path d="M20 10 V67 A40 40 0 0 0 100 67 V10 H86 V67 A26 26 0 0 1 34 67 V10 Z" fill="var(--border-dk)"/>
      <path d="M56 4 H64 V72 L60 82 L56 72 Z" fill="var(--accent)" opacity=".55"/>
    </svg>
  </div>
  <h2 style="color:var(--cobalt-dk)">No industry positions posted yet</h2>
  <p class="lead" style="margin:.6rem auto 0;max-width:52ch">This board is reserved for roles in consulting, contracting, instrumentation, software and government agencies. It opens as soon as the first listing arrives &mdash; be the first to post.</p>
  <div style="display:flex;gap:.7rem;justify-content:center;flex-wrap:wrap;margin-top:1.6rem">
    <a href="mailto:webmaster@usucger.org?subject=Industry%%20Position%%20Posting" class="btn btn-cobalt">Post the first listing &rarr;</a>
    <a href="positions.html" class="btn btn-outline">See academic positions</a>
  </div>
</div>
<div class="grid-3" style="margin-top:2.4rem">
  <div class="card"><div class="card-icon">&#128203;</div><div class="card-title">What to send</div><div class="card-desc">Role title, employer, location, a link to the official posting, and the closing date if there is one.</div></div>
  <div class="card"><div class="card-icon">&#128101;</div><div class="card-title">Who sees it</div><div class="card-desc">Faculty at 180+ member institutions and, through them, the graduate students they advise.</div></div>
  <div class="card"><div class="card-icon">&#9203;</div><div class="card-title">How long it stays</div><div class="card-desc">Up to one year, or until you tell the webmaster the search has closed.</div></div>
</div>
"""

MODULE = """<section class="section bg-white" id="positions">
  <div class="wrap">
    <div class="pos-head rv">
      <div>
        <div class="eyebrow"><span class="eyebrow-line"></span>Careers</div>
        <h2 style="color:var(--cobalt-dk)">Recent academic positions</h2>
        <p class="lead" style="margin-top:.4rem">Faculty and lecturer openings shared by member institutions. Free to post; updated as listings arrive.</p>
      </div>
      <a href="positions.html" class="btn btn-cobalt">All recent positions &rarr;</a>
    </div>
    <div class="linklist rv">
      %(rows)s
    </div>
    <div class="pos-foot rv">
      <span>Member institutions post for free &middot; <a href="mailto:webmaster@usucger.org?subject=Academic%%20Position%%20Posting">submit a listing</a></span>
      <a href="industry-positions.html">Industry &amp; agency positions &rarr;</a>
    </div>
  </div>
</section>
"""

n = len(academic)
with open(os.path.join(PAGES, "positions.html"), "w", encoding="utf-8") as fh:
    fh.write(POSITIONS_PAGE % {"n": n, "s": "" if n == 1 else "s", "rows": "\n          ".join(posting_row(p) for p in academic)})

if industry:
    content = '<div class="linklist">' + "\n".join(posting_row(p, "industry") for p in industry) + "</div>"
else:
    content = EMPTY_STATE
with open(os.path.join(PAGES, "industry-positions.html"), "w", encoding="utf-8") as fh:
    fh.write(INDUSTRY_PAGE % {"content": content})

with open(os.path.join(PARTIALS, "positions-module.html"), "w", encoding="utf-8") as fh:
    fh.write(MODULE % {"n": n, "s": "" if n == 1 else "s", "rows": "\n      ".join(posting_row(p) for p in academic[:4])})

with open(os.path.join(DATA, "positions_count.txt"), "w") as fh:
    fh.write(str(n))

# ---------------------------------------------------------------------- board
with open(os.path.join(DATA, "board.json"), encoding="utf-8") as fh:
    BOARD = json.load(fh)

SEAT = {"junior": ("seat-junior", "Junior seat"), "senior": ("seat-senior", "Senior seat"), "ex": ("seat-ex", "Non-voting")}


def person_card(m):
    cls, label = SEAT[m["seat"]]
    local = "assets/board/%s.jpg" % m["slug"]
    photo = (
        '<div class="person-photo"><img src="%s" alt="%s" loading="lazy" '
        "onerror=\"if(!this.dataset.f){this.dataset.f=1;this.src='%s'}else{this.style.display='none';this.parentNode.insertAdjacentHTML('beforeend','<span class=init>%s</span>')}\"></div>"
        % (local, esc(m["name"]), esc(m["photo"]), initials(m["name"]))
    )
    term = '<div class="person-term">Term %s</div>' % m["term"] if m["term"] else ""
    return (
        '<div class="person has-photo">%s<span class="seat %s">%s</span>'
        '<div class="person-name">%s</div><div class="person-role">%s</div><div class="person-inst">%s</div>%s</div>'
        % (photo, cls, label, esc(m["name"]), esc(m["role"]), esc(m["inst"]), term)
    )


officers = [m for m in BOARD if m["role"] in ("President", "Secretary", "Membership Coordinator", "Webmaster")]
elected = [m for m in BOARD if m["seat"] in ("junior", "senior")]
exoff = [m for m in BOARD if m["seat"] == "ex"]

BOARD_PAGE = """<section class="section bg-white">
  <div class="wrap">
    <div class="rv" style="margin-bottom:1.4rem">
      <div class="eyebrow"><span class="eyebrow-line"></span>Officers</div>
      <h2 style="color:var(--cobalt-dk)">Council officers</h2>
      <p class="lead" style="margin-top:.4rem">The President is elected from among Board members for a two-year term; the Secretary/Treasurer, Comptroller and Webmaster are appointed by the Board.</p>
    </div>
    <div class="officer-strip rv">
      %(officers)s
    </div>

    <div class="split">
      <div>
        <div class="rv" style="margin-bottom:1.4rem">
          <div class="eyebrow"><span class="eyebrow-line"></span>Elected Directors</div>
          <h2 style="color:var(--cobalt-dk)">The full Board</h2>
          <p class="lead" style="margin-top:.4rem">Eight directors serve four-year terms &mdash; four senior and four junior &mdash; with two elected each year, one of each. Only one delegate from any member institution may serve at a time.</p>
        </div>
        <div class="people-grid rv" style="margin-bottom:2.4rem">
          %(elected)s
        </div>
        <div class="rv" style="margin-bottom:1.4rem">
          <div class="eyebrow"><span class="eyebrow-line"></span>Ex-Officio</div>
          <h2 style="color:var(--cobalt-dk)">Ex-officio members</h2>
        </div>
        <div class="people-grid rv">
          %(exoff)s
        </div>
      </div>

      <aside class="sticky-aside rv d2">
        <div class="info-callout">
          <div class="ic-head">&#9993; Reach the Board</div>
          <div class="ic-body">The whole Board can be reached at <a href="mailto:uboard@usucger.org">uboard@usucger.org</a> &mdash; use this address for award nominations, travel grant questions and Council business. Website corrections go to <a href="mailto:webmaster@usucger.org">webmaster@usucger.org</a>.</div>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128499; How the Board is elected</div>
          <div class="sc-body">
            <div class="sc-row"><span class="sc-name">Nominations announced</span><span class="sc-date" style="color:var(--cobalt)">by Sept 30</span></div>
            <div class="sc-row"><span class="sc-name">Nominations close</span><span class="sc-date" style="color:var(--cobalt)">Oct 30</span></div>
            <div class="sc-row"><span class="sc-name">Delegate votes cast</span><span class="sc-date" style="color:var(--cobalt)">by Dec 1</span></div>
            <div class="sc-row"><span class="sc-name">Board changes over</span><span class="sc-date" style="color:var(--cobalt)">Q1 meeting</span></div>
            <p style="font-size:.8rem;color:var(--muted);line-height:1.65;margin-top:.8rem">Each member institution holds two votes &mdash; one for a junior faculty candidate and one for a senior faculty candidate. No proxy votes are allowed.</p>
            <a href="bylaws.html#article-vi" class="btn btn-outline btn-sm" style="margin-top:.9rem">By-Laws, Article VI &rarr;</a>
          </div>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128203; Board record</div>
          <div class="sc-body">
            <a class="sc-link" href="minutes.html"><span class="sc-link-ic">&#128203;</span> Meeting minutes archive</a>
            <a class="sc-link" href="awards.html"><span class="sc-link-ic">&#127942;</span> Awards administered by the Board</a>
            <a class="sc-link" href="travel-grants.html"><span class="sc-link-ic">&#9992;</span> Student travel grants</a>
            <a class="sc-link" href="research-grants.html"><span class="sc-link-ic">&#128176;</span> Small research grants</a>
          </div>
        </div>
      </aside>
    </div>
  </div>
</section>
"""


def officer_cell(m):
    local = "assets/board/%s.jpg" % m["slug"]
    return (
        '<div class="of-cell"><span class="of-photo-wrap"><img src="%s" alt="" loading="lazy" '
        "onerror=\"if(!this.dataset.f){this.dataset.f=1;this.src='%s'}else{this.style.display='none';this.parentNode.insertAdjacentHTML('beforeend','<span class=init>%s</span>')}\"></span>"
        '<div><div class="of-role">%s</div><div class="of-name">%s</div><div class="of-inst">%s</div></div></div>'
        % (local, esc(m["photo"]), initials(m["name"]), esc(m["role"]), esc(m["name"]), esc(m["inst"]))
    )


with open(os.path.join(PAGES, "board.html"), "w", encoding="utf-8") as fh:
    fh.write(BOARD_PAGE % {
        "officers": "\n      ".join(officer_cell(m) for m in officers),
        "elected": "\n          ".join(person_card(m) for m in elected),
        "exoff": "\n          ".join(person_card(m) for m in exoff),
    })

print("positions: %d academic, %d industry | board: %d members" % (n, len(industry), len(BOARD)))


# ------------------------------------------------------------------- palette
with open(os.path.join(ROOT, "theme.json"), encoding="utf-8") as fh:
    THEME = json.load(fh)
TH = THEME["themes"][THEME["active"]]


def rgb(h):
    h = h.lstrip("#")
    return "%d %d %d" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


SWATCHES = [
    ("primary-dk", "Primary Deep", "Headings, wordmark, dark backgrounds, footer"),
    ("primary", "Primary", "Primary buttons, table headers, section bands"),
    ("primary-md", "Primary Bright", "Hover states, upper stratum, highlights on dark"),
    ("accent", "Accent", "Eyebrows, the probe, calls to action, key figures"),
    ("accent-hi", "Accent Highlight", "Accent on dark backgrounds only"),
    ("link", "Link", "In-text links, secondary emphasis, checkmarks"),
    ("sand", "Sand", "Alternate section backgrounds, panels"),
    ("border", "Border", "Rules, card edges, table lines"),
    ("muted", "Muted", "Secondary text, captions, metadata"),
    ("ink", "Ink", "Body text; one-colour black logo"),
]
sw = []
for key, name, use in SWATCHES:
    hexv = TH[key]
    sw.append('<div class="swatch"><div class="sw-color" style="background:%s"></div><div class="sw-body"><div class="sw-name">%s</div><div class="sw-hex">%s &middot; RGB %s</div><div class="sw-use">%s</div></div></div>' % (hexv, name, hexv, rgb(hexv), use))
with open(os.path.join(PARTIALS, "swatches.html"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(sw))
with open(os.path.join(PARTIALS, "theme-label.html"), "w", encoding="utf-8") as fh:
    fh.write(TH["label"])
print("palette partial:", THEME["active"])
