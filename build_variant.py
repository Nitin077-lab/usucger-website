#!/usr/bin/env python3
"""Build a review copy of the site in another theme, in a subfolder.

    python3 build_variant.py moraine

writes <theme>/ with all 22 pages built in that theme. The copy shares the main
site's assets (../assets/) except its own theme stylesheet, so it adds only a few
hundred KB. The main site, theme.json and assets/ are left exactly as they were.
"""
import os, re, shutil, subprocess, sys, tempfile, json

ROOT = os.path.dirname(os.path.abspath(__file__))
theme = sys.argv[1] if len(sys.argv) > 1 else "moraine"
themes = json.load(open(os.path.join(ROOT, "theme.json"), encoding="utf-8"))["themes"]
if theme not in themes:
    sys.exit("unknown theme: %s (choose from %s)" % (theme, ", ".join(themes)))

tmp = tempfile.mkdtemp()
src = os.path.join(tmp, "site")
shutil.copytree(ROOT, src, ignore=shutil.ignore_patterns(".git", "dist", theme))
t = json.load(open(os.path.join(src, "theme.json"), encoding="utf-8"))
t["active"] = theme
json.dump(t, open(os.path.join(src, "theme.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
for step in (["brand/recolor_logo.py"], ["build.py"]):
    subprocess.run([sys.executable] + step, cwd=src, check=True, stdout=subprocess.DEVNULL)

out = os.path.join(ROOT, theme)
os.makedirs(out, exist_ok=True)
shutil.copy(os.path.join(src, "assets", "theme.css"), os.path.join(out, "theme.css"))
label = themes[theme]["label"]
for name in sorted(os.listdir(src)):
    if not name.endswith(".html"):
        continue
    html = open(os.path.join(src, name), encoding="utf-8").read()
    html = html.replace('href="assets/theme.css"', 'href="theme.css"')
    html = re.sub(r'((?:href|src)=")assets/', r'\1../assets/', html)
    html = re.sub(r"(url\(['\"]?)assets/", r"\1../assets/", html)
    html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
    html = html.replace("<title>", "<title>[%s preview] " % label.split(" —")[0], 1)
    open(os.path.join(out, name), "w", encoding="utf-8").write(html)
shutil.rmtree(tmp)
print("built %s/ in theme %s" % (theme, label))
