#!/usr/bin/env python3
"""Bundle the whole built site into ONE self-contained HTML file with hash routing,
for hosting as a single page (board preview). Run after build.py.

    python3 build_preview.py   ->  dist/usucger-preview.html
"""
import base64
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dist")
os.makedirs(OUT, exist_ok=True)

manifest = json.load(open(os.path.join(ROOT, "pages.json"), encoding="utf-8"))
slugs = list(manifest.keys())


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
        return fh.read()


def data_uri(path, mime):
    with open(os.path.join(ROOT, path), "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode("ascii"))


def rewrite_links(html):
    # x.html#anchor -> #x/anchor ; x.html -> #x ; keep externals
    def repl(m):
        attr, target = m.group(1), m.group(2)
        if target.startswith(("http", "mailto:", "data:", "#", "assets/")):
            return m.group(0)
        page, _, frag = target.partition("#")
        if page.endswith(".html"):
            page = page[:-5]
            return '%s="#%s%s"' % (attr, page, "/" + frag if frag else "")
        return m.group(0)
    return re.sub(r'\b(href)="([^"]+)"', repl, html)


# ---- shared chrome from the built homepage
index = read("index.html")
head_top = index.index("<body>") + len("<body>")
main_start = index.index('<main id="main">')
chrome_before = index[head_top:main_start]          # skip link, notice bar, nav, drawer, search
footer_start = index.index("<footer")
footer_end = index.index("</footer>") + len("</footer>")
footer = index[footer_start:footer_end]

# ---- per-page content (main + optional cta strip)
pages = []
for slug in slugs:
    html = read(slug)
    a = html.index('<main id="main">')
    b = html.index("<footer")
    body = html[a:b]
    body = body.replace('<main id="main">', "", 1)
    body = body[: body.rindex("</main>")] + body[body.rindex("</main>") + len("</main>"):]
    key = slug[:-5]
    if key != "index":
        # the member map lives on the homepage in the single-file preview (ids must be unique)
        if key == "universities":
            a2 = body.find('<div class="rv" style="margin-bottom:2.6rem"><div class="map-wrap">')
            if a2 != -1:
                b2 = body.index("</script>", a2) + len("</script>")
                body = body[:a2] + '<div class="info-callout callout-grey rv" style="margin-bottom:2rem"><div class="ic-head">Member map</div><div class="ic-body">The interactive map of members by state is on the <a href="#index/members-map">home page</a>.</div></div>' + body[b2:]
    pages.append((key, body))

# ---- inline assets
css = read("assets/site.css") + "\n" + read("assets/theme.css")
css = css.replace("url('", "url('")  # nothing external referenced
js = read("assets/site.js").replace('href="membership.html"', 'href="#membership"')
idx = read("assets/search-index.js")
idx = re.sub(r'"u":"([^"#]+)\.html(#([^"]+))?"', lambda m: '"u":"#%s%s"' % (m.group(1), "/" + m.group(3) if m.group(3) else ""), idx)

# brand svgs referenced by <img src="assets/brand/..."> (footer/nav are inline already)
def inline_asset_imgs(html):
    def repl(m):
        path = m.group(1)
        full = os.path.join(ROOT, path)
        if os.path.exists(full) and path.endswith(".svg"):
            return 'src="%s"' % data_uri(path, "image/svg+xml")
        return m.group(0)
    return re.sub(r'src="(assets/[^"]+)"', repl, html)

sections = []
for key, body in pages:
    body = inline_asset_imgs(rewrite_links(body))
    sections.append('<div class="pg" data-pg="%s" hidden>%s</div>' % (key, body))

chrome_before = inline_asset_imgs(rewrite_links(chrome_before))
footer = inline_asset_imgs(rewrite_links(footer))
chrome_before = chrome_before.replace('href="index.html"', 'href="#index"')

ROUTER = r"""
(function(){
  try{history.scrollRestoration='manual'}catch(e){}
  var pages=[].slice.call(document.querySelectorAll('.pg'));
  function show(){
    var h=(location.hash||'#index').slice(1), parts=h.split('/'), key=parts[0]||'index', anchor=parts[1];
    if(!document.querySelector('.pg[data-pg="'+key+'"]')) key='index';
    pages.forEach(function(p){p.hidden=p.dataset.pg!==key;});
    document.querySelectorAll('#nav .nav-item>a, .nav-sub a, .drawer-links a').forEach(function(a){
      var href=a.getAttribute('href')||''; a.classList.toggle('active', href==='#'+key);
    });
    document.querySelectorAll('#nav .nav-item').forEach(function(li){
      var hit=[].some.call(li.querySelectorAll('.nav-sub a'),function(a){return a.getAttribute('href')==='#'+key});
      li.querySelector(':scope>a').classList.toggle('active',hit);
    });
    document.querySelectorAll('.pg[data-pg="'+key+'"] .rv').forEach(function(e){e.classList.add('show')});
    var sb=document.getElementById('search'); if(sb) sb.hidden=true; document.body.style.overflow='';
    var dr=document.getElementById('drawer'); if(dr) dr.classList.remove('open');
    var el=anchor&&document.getElementById(anchor);
    var top=el?Math.max(0,el.getBoundingClientRect().top+window.scrollY-76):0;
    window.scrollTo({top:top,behavior:'instant'});
  }
  window.addEventListener('hashchange',show); show();
  var t=document.title.split(' — ')[0];
})();
"""

page = []
page.append("<title>USUCGER</title>")
page.append('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
page.append('<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=Figtree:wght@300;400;500;600;700&display=swap" rel="stylesheet">')
page.append("<style>%s\n.pg[hidden]{display:none}\n.rv{opacity:1;transform:none}\n.preview-tag{position:fixed;left:1rem;bottom:1rem;z-index:350;font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:var(--amber);color:#fff;padding:.35rem .7rem;border-radius:3px;box-shadow:var(--sh)}</style>" % css)
page.append(chrome_before)
page.append('<main id="main">%s</main>' % "".join(sections))
page.append(footer)
page.append('<button id="btt" type="button" title="Back to top" aria-label="Back to top">&uarr;</button>')
page.append('<div class="preview-tag" aria-hidden="true">Board preview</div>')
page.append("<script>%s</script>" % idx)
page.append("<script>%s</script>" % js)
page.append("<script>%s</script>" % ROUTER)
html = "\n".join(page)
# the built chrome may contain a stray </body></html>? no — footer slice stops at </footer>
out = os.path.join(OUT, "usucger-preview.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(html)
print("preview: %d pages, %.1f MB -> %s" % (len(sections), len(html.encode("utf-8")) / 1e6, os.path.relpath(out, ROOT)))
