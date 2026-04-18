# CLAUDE.md

## Project Overview

**Palnackie** — the official community website for Palnackie village, Dumfries and Galloway, Scotland. Target URL: `https://www.palnackie.scot`.

**Goal:** A clean, modern, easily navigable community site replacing the outdated Drupal site. Serves both residents and visitors.

**Audience:** Palnackie residents, people visiting or planning to visit the village.

## Development Commands

```bash
bundle install
bundle exec jekyll serve --livereload   # http://localhost:4000
bundle exec jekyll build
```

No test suite or linting — content and template site with no JavaScript.

## Architecture

**No JavaScript.** All styling is inline CSS in `_layouts/default.html`.

**Layout hierarchy:**
- `_layouts/default.html` — base shell (sticky nav, footer, all CSS inline)
- `_layouts/home.html` — extends default, for the homepage
- `_layouts/page.html` — extends default, wraps content in `.page-wrap`

**Pages** — each section is a directory with an `index.html`:
- `index.html` — homepage
- `village-shop/`
- `flounders/`
- `village-hall/`
- `glenisle-inn/`
- `the-port/`
- `places-to-stay/`
- `orchardton-tower/`
- `village-walks/`
- `businesses/`
- `community-council/`
- `buittle-quest/`
- `emergencies/`

**Colour palette:**
- `--navy: #1c3345` — header, headings, footer
- `--slate: #2a4a63` — secondary headings, hover states
- `--teal: #2e7d8c` — accent, links, badges
- `--stone: #f4f0e8` — body background
- `--white: #ffffff` — cards, contact blocks

**Navigation:**
- Main nav: Village Shop, Flounders, Village Hall, Glenisle Inn, The Port
- "More" CSS dropdown: Places to Stay, Orchardton Tower, Village Walks, Businesses & Services, Community Council, Buittle Quest, Emergencies

## Content to Add Later

- Village walks leaflet PDF (upload to `assets/` and link from `village-walks/`)
- Buittle Quest constitution PDF (link from `buittle-quest/`)
- Household Emergency Lifesaving Plan (add to `emergencies/`)
- Hero image for the homepage (add to `assets/images/` and set as `hero` background-image)

## Deployment

GitHub Pages — push to `main`, site rebuilds automatically.
