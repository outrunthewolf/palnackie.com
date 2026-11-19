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

**Thin-data weeks:** traffic is ~100 visitors/month, so the report includes a 90-day long view and the agent treats small swings as noise. When nothing clears the noise bar it works through `_plans/BACKLOG.md` ("Agent can do" items; "Needs the owner" items are Chris's). Edit that file to steer the agent.

**palnackie.scot:** the old Drupal site's domain, run by an agency, showing only a "Site under maintenance" holding page (checked 2026-11-19), believed down since a PHP vulnerability scare. Public WHOIS (2026-11-19): registrant organisation **Palnackie Village Shop Limited**, registrar PDR Ltd (PublicDomainRegistry, usually via a reseller — likely the agency), status `clientTransferProhibited`, **expires 2027-04-22**. Goal: the shop, as registrant, requests the transfer (EPP) code, moves it to a community-held domain account, and forwards it (301) to palnackie.com. palnackie.com is currently registered personally to Chris.

**Setup checklist (started 2026-11-18 — pick up here):**
- [x] `scripts/site_report.py` written and tested (BigQuery auth works; degrades cleanly with no data/token)
- [x] `scripts/`, `_plans/`, `parse_logs.py` excluded from Jekyll build; `_plans/` created
- [x] Commit + push the above to `main` (cloud routine runs from GitHub, so it can't see the script until pushed)
- [x] **Chris:** confirm `palnackie.com` is a verified property in Google Search Console
- [x] **Chris:** GSC → Settings → Bulk data export → project `nash-claude-gcp`, dataset `searchconsole_palnackiecom`, location `europe-west2` (export permissions should already exist from dogfriendlydg; first data lands within ~48h, no backfill)
- [x] **Chris:** GoatCounter → Settings → API → new token, *Read statistics* only
- [x] **Chris:** add it as `GOATCOUNTER_TOKEN` in the claude.ai cloud environment (alongside the existing `GCP_SA_KEY_JSON`)
- [x] Sanity-check real output — first run 2026-11-19 opened PR #1 (plan only; GoatCounter working after adding palnackie.goatcounter.com to the environment allowlist; Search Console tables not yet populated)
- [x] Create the weekly cloud routine — **Palnackie — Weekly Site Agent** (`trig_01QCxcFWrJaULqVo5mAs9Vu6`), Fridays 09:00 UTC, env `palnackie.com`, Sonnet 5.5, no connectors. Manage: https://claude.ai/code/routines/trig_01QCxcFWrJaULqVo5mAs9Vu6
- [ ] Set up a loop for ongoing site optimisation on top of the weekly reports
- [x] Record the routine name/id in this section

**Running locally** (local gcloud is the float work account and must stay that way):
```bash
GOOGLE_APPLICATION_CREDENTIALS=~/.config/nash-claude-gcp/bigquery-claude-ro.json GOATCOUNTER_TOKEN=... python3 scripts/site_report.py   # needs: pip install google-cloud-bigquery
```

`scripts/`, `_plans/` and `parse_logs.py` are excluded from the Jekyll build (still visible in the public GitHub repo, so never commit credentials).

## Deployment

GitHub Pages — push to `main`, site rebuilds automatically.
