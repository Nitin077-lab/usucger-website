#!/usr/bin/env python3
"""Generate the two data-driven page bodies (directory + member universities)
from the pipe-delimited source files, with the data inlined so the site works
straight off the filesystem with no fetch()/CORS problems."""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "pages")


def read(name, cols):
    rows = []
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("|")
            parts += [""] * (cols - len(parts))
            rows.append([p.strip() for p in parts[:cols]])
    return rows


members = read("members.txt", 3)
unis = read("universities.txt", 2)

inst = sorted({m[2] for m in members if m[2]})

DIRECTORY = """<section class="section bg-white">
  <div class="wrap">
    <div class="split">
      <div class="rv">
        <div class="grid-4" style="margin-bottom:1.8rem">
          <div class="card" style="padding:1.2rem 1.3rem"><div class="stat-n" style="font-size:2rem">%(n_members)d</div><div class="stat-l">Listed members</div></div>
          <div class="card" style="padding:1.2rem 1.3rem"><div class="stat-n" style="font-size:2rem">%(n_inst)d</div><div class="stat-l">Affiliations</div></div>
          <div class="card" style="padding:1.2rem 1.3rem"><div class="stat-n" style="font-size:2rem">$75</div><div class="stat-l">Dues per person</div></div>
          <div class="card" style="padding:1.2rem 1.3rem"><div class="stat-n" style="font-size:2rem">2027</div><div class="stat-l">Cycle ends</div></div>
        </div>
        <div id="memberTable"></div>
        <p style="font-size:.79rem;color:var(--muted-lt);margin-top:.9rem">Directory reflects dues collected for the 2025&ndash;2027 cycle. Missing or incorrect? Email <a href="mailto:webmaster@usucger.org" style="color:var(--teal);font-weight:600">webmaster@usucger.org</a>.</p>
      </div>
      <aside class="sticky-aside rv d2">
        <div class="info-callout">
          <div class="ic-head">&#128269; Searching the directory</div>
          <div class="ic-body">Type any part of a name or institution to filter instantly &mdash; for example <em>Purdue</em>, <em>Berkeley</em> or a surname. Click a column heading to sort, click again to reverse.</div>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128279; Related</div>
          <div class="sc-body">
            <a class="sc-link" href="universities.html"><span class="sc-link-ic">&#127979;</span> Member universities &amp; contacts</a>
            <a class="sc-link" href="membership.html"><span class="sc-link-ic">&#128179;</span> Join or renew</a>
            <a class="sc-link" href="https://usucger.org/my-account/" target="_blank" rel="noopener"><span class="sc-link-ic">&#128274;</span> Member login</a>
            <a class="sc-link" href="board.html"><span class="sc-link-ic">&#127963;</span> Board of Directors</a>
          </div>
        </div>
        <div class="info-callout callout-grey">
          <div class="ic-head">Add yourself</div>
          <div class="ic-body">Membership is $75 per person for the full 2025&ndash;2027 cycle, in either the University or Associate category. <a href="membership.html">See the options &rarr;</a></div>
        </div>
      </aside>
    </div>
  </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function () {
buildDataTable({
  mount: 'memberTable',
  noun: 'members',
  placeholder: 'Search members by name or institution\\u2026',
  defaultSort: 1,
  columns: [{label:'First name'},{label:'Last name'},{label:'Affiliation'}],
  rows: %(members)s
});
});
</script>
"""

UNIVERSITIES = """<section class="section bg-white">
  <div class="wrap">
    <div class="rv" style="margin-bottom:2.6rem"><!--include:member-map.html--></div>
    <div class="split">
      <div class="rv">
        <div id="uniTable"></div>
        <p style="font-size:.79rem;color:var(--muted-lt);margin-top:.9rem">Each member institution designates a contact person who serves as its delegate for Council voting. To update your institution's contact, email <a href="mailto:webmaster@usucger.org" style="color:var(--teal);font-weight:600">webmaster@usucger.org</a>.</p>
      </div>
      <aside class="sticky-aside rv d2">
        <div class="stat-block">
          <div class="stat-cell"><div class="stat-n">%(n_uni)d</div><div class="stat-l">Institutions</div><div class="stat-d">Geotechnical programs represented in the Council</div></div>
          <div class="stat-cell"><div class="stat-n">2</div><div class="stat-l">Votes each</div><div class="stat-d">One for a junior and one for a senior Board candidate</div></div>
        </div>
        <div class="info-callout">
          <div class="ic-head">&#128220; What membership requires</div>
          <div class="ic-body">Academic institutions in the U.S. with a program of research and/or education in geotechnical engineering are eligible, subject to Board approval. Each institution must have a paid member serving as contact person. <a href="bylaws.html#article-iii">By-Laws, Article III &rarr;</a></div>
        </div>
        <div class="sidebar-card">
          <div class="sc-head">&#128279; Related</div>
          <div class="sc-body">
            <a class="sc-link" href="directory.html"><span class="sc-link-ic">&#128101;</span> Full membership directory</a>
            <a class="sc-link" href="membership.html"><span class="sc-link-ic">&#128179;</span> Membership &amp; dues</a>
            <a class="sc-link" href="positions.html"><span class="sc-link-ic">&#128188;</span> Post a faculty position</a>
          </div>
        </div>
      </aside>
    </div>
  </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function () {
buildDataTable({
  mount: 'uniTable',
  noun: 'institutions',
  placeholder: 'Search institutions or contacts\\u2026',
  defaultSort: 0,
  columns: [{label:'Member institution'},{label:'Contact person'}],
  rows: %(unis)s
});
});
</script>
"""

with open(os.path.join(OUT, "directory.html"), "w", encoding="utf-8") as fh:
    fh.write(DIRECTORY % {
        "n_members": len(members),
        "n_inst": len(inst),
        "members": json.dumps(members, ensure_ascii=False),
    })

with open(os.path.join(OUT, "universities.html"), "w", encoding="utf-8") as fh:
    fh.write(UNIVERSITIES % {
        "n_uni": len(unis),
        "unis": json.dumps(unis, ensure_ascii=False),
    })

print("directory: %d members / %d affiliations" % (len(members), len(inst)))
print("universities: %d institutions" % len(unis))
