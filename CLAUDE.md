# CLAUDE.md

## Project Overview

**Palnackie** — the official community website for Palnackie village, Dumfries and Galloway, Scotland. Target URL: `https://www.palnackie.com`.

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
- `resources/` — Documents & Resources, driven by `_data/resources.yml` (files live in `assets/documents/`; `featured: true` shows on the homepage)
- `news/` — news index; posts live in `_posts/`

**Colour palette:**
- `--navy: #1c3345` — header, headings, footer
- `--slate: #2a4a63` — secondary headings, hover states
- `--teal: #2e7d8c` — accent, links, badges
- `--stone: #f4f0e8` — body background
- `--white: #ffffff` — cards, contact blocks

**Navigation:**
- Main nav: Village Shop, Flounders, Village Hall, Glenisle Inn, The Port
- "More" CSS dropdown: Places to Stay, Orchardton Tower, Village Walks, Businesses & Services, Community Council, Buittle Quest, Emergencies, Village News, Documents & Resources

## Content to Add Later

- Village walks leaflet PDF (upload to `assets/` and link from `village-walks/`)
- Buittle Quest constitution PDF (link from `buittle-quest/`)
- Household Emergency Lifesaving Plan (add to `emergencies/`)
- Hero image for the homepage (add to `assets/images/` and set as `hero` background-image)

## Weekly Site Agent (analytics → changes)

Modelled on the dogfriendlydg setup. `scripts/site_report.py` produces a Markdown report from two read-only sources; a weekly cloud routine reads it, writes `_plans/YYYY-MM-DD.md`, makes up to 3 small changes and opens **one PR** (branch `agent/site-YYYY-MM-DD`). It never pushes to `main`. Chris reviews and merges. If last week's PR is still open, the agent comments on it instead of making new changes.

**Data sources:**
- **Search Console → BigQuery:** project `nash-claude-gcp` (location `europe-west2`), dataset `searchconsole_palnackiecom`, read via the `bigquery-claude-ro@nash-claude-gcp.iam.gserviceaccount.com` service account.
- **GoatCounter:** `palnackie.goatcounter.com`, read-only API token in `GOATCOUNTER_TOKEN`.

Either source is skipped with a note if its credentials or data are missing.

**Agent remit (community site, not a growth site):** improve titles/meta descriptions, internal links, clarity and findability of existing pages; add redirect stubs for old Drupal URLs still getting traffic; flag stale or missing information. It must **not** invent facts about the village, businesses, opening times, councillors or events. Anything needing real-world information goes in the plan as a question for Chris.

**Setup checklist (started 2026-11-18 — pick up here):**
- [x] `scripts/site_report.py` written and tested (BigQuery auth works; degrades cleanly with no data/token)
- [x] `scripts/`, `_plans/`, `parse_logs.py` excluded from Jekyll build; `_plans/` created
- [x] Commit + push the above to `main` (cloud routine runs from GitHub, so it can't see the script until pushed)
- [x] **Chris:** confirm `palnackie.com` is a verified property in Google Search Console
- [x] **Chris:** GSC → Settings → Bulk data export → project `nash-claude-gcp`, dataset `searchconsole_palnackiecom`, location `europe-west2` (export permissions should already exist from dogfriendlydg; first data lands within ~48h, no backfill)
- [x] **Chris:** GoatCounter → Settings → API → new token, *Read statistics* only
- [x] **Chris:** add it as `GOATCOUNTER_TOKEN` in the claude.ai cloud environment (alongside the existing `GCP_SA_KEY_JSON`)
- [ ] Run the report locally once with both sources to sanity-check real output
- [ ] Create the weekly cloud routine (pick day/time; self-contained prompt with the remit above, one PR per week, skip if last PR still open)
- [ ] Set up a loop for ongoing site optimisation on top of the weekly reports
- [ ] Record the routine name/id in this section

**Running locally** (local gcloud is the float work account and must stay that way):
```bash
GOOGLE_APPLICATION_CREDENTIALS=~/.config/nash-claude-gcp/bigquery-claude-ro.json GOATCOUNTER_TOKEN=... python3 scripts/site_report.py   # needs: pip install google-cloud-bigquery
```

`scripts/`, `_plans/` and `parse_logs.py` are excluded from the Jekyll build (still visible in the public GitHub repo, so never commit credentials).

## Deployment

GitHub Pages — push to `main`, site rebuilds automatically.
