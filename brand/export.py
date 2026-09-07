#!/usr/bin/env python3
"""Export PNG (transparent, print-resolution) and a vector PDF logo sheet from
the SVG masters in brand/logo. Requires Playwright + Chromium.

    python3 brand/export.py
"""
import asyncio
import glob
import os
import re

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "logo")
PNG = os.path.join(HERE, "png")
os.makedirs(PNG, exist_ok=True)

import json
with open(os.path.join(os.path.dirname(HERE), "theme.json"), encoding="utf-8") as _fh:
    _T = json.load(_fh)
_TH = _T["themes"][_T["active"]]
TARGET_W = 3000  # px wide for horizontal lockups (≈ 10 in at 300 dpi)


def dims(svg_text):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_text)
    return float(m.group(1)), float(m.group(2))


async def main():
    files = sorted(glob.glob(os.path.join(SRC, "*.svg")))
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # --- PNGs
        for f in files:
            name = os.path.splitext(os.path.basename(f))[0]
            text = open(f, encoding="utf-8").read()
            w, h = dims(text)
            scale = TARGET_W / w if w >= h else 1600 / h
            W, H = int(round(w * scale)), int(round(h * scale))
            pg = await b.new_page(viewport={"width": W, "height": H})
            await pg.set_content(
                "<html><body style='margin:0;background:transparent'>"
                + text.replace('width="%g"' % w, 'width="%d"' % W, 1).replace('height="%g"' % h, 'height="%d"' % H, 1)
                + "</body></html>"
            )
            await pg.screenshot(path=os.path.join(PNG, name + ".png"), omit_background=True)
            await pg.close()
            print("  png", name, "%dx%d" % (W, H))

        # --- vector PDF sheet
        rows = []
        for f in files:
            name = os.path.basename(f)
            text = open(f, encoding="utf-8").read()
            dark = "white" in name or "reversed" in name
            rows.append(
                "<div class='cell %s'><div class='lbl'>%s</div>%s</div>"
                % ("dark" if dark else "", name, text)
            )
        html = """<html><head><style>
        @page{size:A4 landscape;margin:12mm}
        body{font-family:Helvetica,Arial,sans-serif;margin:0;color:#333}
        h1{font-size:18pt;margin:0 0 2mm}
        p{font-size:9pt;margin:0 0 6mm;color:#666}
        .grid{display:flex;flex-wrap:wrap;gap:5mm}
        .cell{border:0.3pt solid #bbb;padding:5mm;break-inside:avoid;background:#fff}
        .cell.dark{background:%s}
        .cell svg{height:28mm;width:auto;display:block}
        .lbl{font-size:7pt;color:#777;margin-bottom:3mm;font-family:monospace}
        .dark .lbl{color:#9ab}
        </style></head><body>
        <h1>USUCGER logo family — vector master sheet</h1>
        <p>All artwork is vector. Text is converted to outlines. Theme: %s. Primary %s / %s / %s &middot; Accent %s / %s.</p>
        <div class='grid'>%s</div></body></html>""" % (_TH["primary-dk"], _TH["label"], _TH["primary-dk"], _TH["primary"], _TH["primary-md"], _TH["accent"], _TH["accent-hi"], "".join(rows))
        pg = await b.new_page()
        await pg.set_content(html)
        await pg.pdf(path=os.path.join(HERE, "USUCGER-logo-sheet.pdf"), format="A4", landscape=True,
                     print_background=True, margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"})
        print("  pdf USUCGER-logo-sheet.pdf")
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
