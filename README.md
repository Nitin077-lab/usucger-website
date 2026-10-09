# USUCGER website

A complete, static, 21-page website for the United States Universities Council on
Geotechnical Education and Research. Every page shares one header, navigation,
mobile drawer, footer and stylesheet, so the whole site is in a single format.

## Deploying

Upload the contents of this folder to any web host and point the domain at it.
There is no build step at deploy time, no server-side code and no database —
just HTML, one CSS file and one JS file. It also opens correctly straight off a
USB stick or local folder (all data is inlined, nothing is fetched at runtime).

```
index.html            about.html          bylaws.html         board.html
contact.html          membership.html     directory.html      universities.html
awards.html           travel-grants.html  research-grants.html minutes.html
teaching-aids.html    books.html          software.html       videos.html
funding-tips.html     positions.html      photos.html         conferences.html
workshops.html
assets/site.css       assets/site.js
```

## Hosting on GitHub Pages (free)

1. Create a repository on GitHub (e.g. `usucger/website`), then from this folder:
   ```
   git remote add origin https://github.com/<org>/<repo>.git
   git push -u origin main
   ```
   (The folder is already a git repository with the site committed.)
2. In the repository, open **Settings → Pages**, set *Source* to **Deploy from a
   branch**, pick `main` and the `/ (root)` folder, and save.
3. After a minute the site is live at `https://<org>.github.io/<repo>/`.
   A `.nojekyll` file is included so GitHub serves the files exactly as built.
4. To point `usucger.org` at it later, add the domain under *Custom domain* on
   the same Pages screen and set the DNS records GitHub shows.

Every later change is: edit → rebuild → `git commit` → `git push`. Pages
redeploys automatically.

## Editing

The published `.html` files at the top level are **generated**. Edit the sources
and rebuild, so the nav and footer stay identical everywhere:

| To change | Edit | Then run |
|---|---|---|
| A page's content | `pages/<page>.html` (body only) | `python3 build.py` |
| Page title, hero text, breadcrumbs, hero buttons | `pages.json` | `python3 build.py` |
| Single-file board preview (all pages, hash routing) | — | `python3 build_preview.py` → `dist/usucger-preview.html` |
| Navigation, footer, notice ticker, shared shell | `build.py` (`NAV`, `FOOTER`, `NOTICES`, `SHELL`) | `python3 build.py` |
| Colours, type, components | `assets/site.css` | nothing — it is linked, not inlined |
| Behaviour (drawer, tabs, tables) | `assets/site.js` | nothing |
| Job postings (academic or industry) | `data/positions.json` | `python3 gen_content.py && python3 build.py` |
| Board members and photos | `data/board.json` + `assets/board/<slug>.jpg` | `python3 gen_content.py && python3 build.py` |
| Award recipients, featured winners | `data/awards.json` + `assets/awards/<slug>.jpg` | `python3 gen_extra.py && python3 build.py` |
| Deadlines (countdowns, ticker, sidebar) | `data/deadlines.json` | `python3 gen_extra.py && python3 build.py` |
| Member map (state per institution, member matching) | `data/university_states.txt`, `data/members.txt`, aliases in `gen_map.py` | `python3 gen_map.py && python3 build.py` |
| Membership directory rows | `data/members.txt` (`First\|Last\|Affiliation`) | `python3 gen_data_pages.py && python3 build.py` |
| Member universities rows | `data/universities.txt` (`Institution\|Contact`) | `python3 gen_data_pages.py && python3 build.py` |

Adding a page: create `pages/newpage.html` with just the body markup, add an entry
to `pages.json`, add it to `NAV` and/or `FOOTER` in `build.py`, and rebuild.

## What's in it

* **Responsive** — three breakpoints, verified with no horizontal overflow at
  390 px, 768 px and 1440 px.
* **Mobile navigation** — a real slide-in drawer with expandable sections
  (the previous version simply hid the menu on phones).
* **Searchable tables** — the 330-person membership directory and the 185
  member universities filter as you type and sort on any column, with no
  external libraries.
* **Accessibility** — skip link, visible focus rings, ARIA on the drawer and
  tabs, semantic landmarks, and `prefers-reduced-motion` support.
* **Print styles** — navigation and footer drop away; the by-laws print cleanly.
* **No dependencies** — no jQuery, no framework, no CDN except Google Fonts
  (Fraunces + Figtree), which degrades gracefully to Georgia / system sans.

## Positions — the most-visited page

`data/positions.json` drives three things at once: the Academic Positions page
(with its live filter and "New" badges for anything under 45 days old), the
"Open academic positions" module on the homepage, and the count in the
**Positions** pill in the navigation. Add a listing as one JSON object with
`institution`, `title`, `location`, `posted` (YYYY-MM-DD) and `url`, run
`gen_content.py` then `build.py`, and all three update. Put industry roles in
the `industry` array — the Industry & Agency Positions page shows an empty
state until the first one arrives, then lists them the same way.

## Live, self-updating elements

* **Deadlines** — `data/deadlines.json` feeds the sidebar countdown card, the
  notice ticker and inline callouts. The browser computes days remaining on
  every visit; passed dates show their `closed` text, drop to the bottom of
  the card and vanish from the ticker. Add next year's dates and they take
  over automatically.
* **Site search** — `build.py` writes `assets/search-index.js` from every
  page, section heading, directory member and member university. The overlay
  opens from the nav button or Ctrl/⌘+K; no server needed.
* **Member map** — real state boundaries (US Census 10 m via `us-atlas`,
  Albers USA projection, pre-rendered to SVG paths in `data/us-states.json`).
  States are shaded by **number of members**: every person in the membership
  directory is matched to a member institution by affiliation
  (`gen_map.py`, with a short alias list for spellings like "MIT"), and
  institutions are placed by `data/university_states.txt`. Hover or tap a
  state to list its institutions with member counts; expand one to see the
  names. Puerto Rico and international members appear as chips beside the
  map. Regenerate with `python3 gen_map.py && python3 build.py` after
  updating the directory.
* **Award history** — filter by award and search recipients; the two most
  recent winners are featured with photos on the homepage and awards page.

## Board & award photos

`data/board.json` lists each member with a `slug`. The page looks for
`assets/board/<slug>.jpg` first and falls back to the `photo` URL on the
current WordPress site if the local file is missing, so it works today and
keeps working after WordPress is retired once the JPEGs are copied in. The
eleven files to save (from the current board page's media library) are:

```
diane-moug.jpg          Moug2-1-768x568-crop.jpg
james-kaklamanos.jpg    kaklamanos_Headshot_v1.jpg
estefan-garcia.jpg      garcialab.engin.umich.edu … ProfilePhoto_FEG.jpg
lisa-star.jpg           Lisa-Star.jpg
ryan-shamet.jpg         Ryan-Shamet.jpg
marika-santagata.jpg    marika-Santagata_v2.jpg
kaleigh-yost.jpg        Kaleigh-Yost.jpg
alejandro-martinez.jpg  headshot-alejandro-martinez3.jpg
chukwuebuka-nweke.jpg   Nweke.jpg
jack-montgomery.jpg     jack-montgomery-crop-2.jpg
joseph-coe.jpg          Joe-Coe.jpg
```

Square-ish crops around 600 × 600 px look best; the cards crop to a square
from the top.

The 2026 award winners are shown from the composite graphic already on the
current site (`2026-awards.jpg`), cropped in CSS. For a cleaner result, save
individual portraits as `assets/awards/cheng-zhu.jpg` and
`assets/awards/adda-athanasopoulos-zekkos.jpg` — the page prefers those when
present. Add future winners to `featured` in `data/awards.json`.

## Colour theme

`theme.json` holds three complete palettes (Strata, Bedrock, Moraine) and an
`active` key. `build.py` writes `assets/theme.css` from the active theme,
`brand/make_logo.py` colours the logo from it, and `gen_content.py` builds the
palette swatches on the brand page from it — so switching the whole identity
is: change `active`, then run `make_logo.py`, `export.py`, copy
`brand/logo/*.svg` to `assets/brand/`, `gen_content.py`, `build.py`.
The site ships with **Strata — cobalt & amber** active; Bedrock and Moraine are kept as ready alternatives.

**Board review (Oct 2026):** theme.json now also holds the 18 palette options shown to the Board (A–R), and **Core Sample** (white & safety orange, light header) is active. Themes marked `"band": "light"` get a pale hero band with dark text. To switch: set `active` in theme.json, then `python3 brand/recolor_logo.py && python3 build.py` (recolours the logo without needing the fonts).

## Brand & logo

`brand/` holds the identity system. `brand/make_logo.py` generates every SVG in
`brand/logo/` from one parametric drawing of the mark, with the wordmark and
tagline converted to outlines (Fraunces 700 / Figtree 700), so the files need no
fonts. `brand/export.py` renders 3000 px transparent PNGs into `brand/png/` and a
vector `USUCGER-logo-sheet.pdf`. The site's `assets/brand/` is a copy of the SVG
masters. The nav mark, footer lockup and favicon on every page are inlined from
these files by `build.py`, so re-running `make_logo.py` and `build.py` updates the
whole site. (There is deliberately no public brand page; the logo pack is
distributed separately to whoever needs it.)

## Content sources

All content was migrated from the live usucger.org pages: history and mission,
the eleven by-law articles, the current Board, membership categories and dues,
the membership directory, member universities, award criteria and the complete
recipient history, student travel grants, small research grant projects, the
1996–2016 meeting minutes archive, teaching aids, books and proceedings,
software, videos, funding tips, academic positions, photo collections,
conferences and workshops.

Things worth checking before go-live:

* Academic position listings and conference dates go stale — they are the two
  pages that need the most regular attention.
* The membership directory reflects the 2025–2027 cycle as published; refresh
  `data/members.txt` whenever the dues list is updated.
* Member login and the two membership purchase links still point at the existing
  WordPress store, since that is where payment is processed.
