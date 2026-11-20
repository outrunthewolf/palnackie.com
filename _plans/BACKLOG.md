---
title: Site improvement backlog
---

# Site improvement backlog

Improvements that are worth making **whatever the traffic numbers say**. The weekly agent takes items from here when the analytics are too thin to justify a data-led change. Chris can add, remove or reorder items at any time; the agent works top to bottom within each section.

Format: `- [ ] item` — when done, change to `- [x] item (YYYY-MM-DD, PR #n)`. Items needing facts or files only Chris can supply go under **Needs the owner** and the agent never does them itself.

## Agent can do

- [x] **Page titles say where we are.** Most section titles are generic ("Village Shop", "The Port", "Places to Stay", "News"), so in search results and browser tabs they don't mention Palnackie. Rewrite each `title` to include Palnackie naturally (e.g. "Palnackie Village Shop & Post Office", "Places to Stay in and near Palnackie"), keeping them under ~60 characters. Check each `description` is a useful one-sentence summary under ~155 characters. One change covers all pages. (2026-11-20)
- [x] **Related-page links.** Add a short "See also" line at the end of pages that naturally connect, using only existing pages: Village Walks ↔ Orchardton Tower ↔ The Port; Places to Stay ↔ Glenisle Inn ↔ Village Walks; Village Shop ↔ Flounders ↔ Village Hall; Community Council ↔ Documents & Resources ↔ Village News. (2026-11-20)
- [ ] **Structured data for the main places.** `_includes/json_ld.html` has schema.org data for the village and the shop. Add matching blocks for Orchardton Tower (`TouristAttraction`), the Glenisle Inn (`BarOrPub`), Flounders (`CafeOrCoffeeShop`) and the Village Hall (`CivicStructure`), using **only facts already in the repo** (`_data/pages/*.yml`). Validate the JSON is well formed.
- [ ] **External link check.** The site has ~48 external links (businesses, council, booking sites). Check each one (HTTP status, and whether it still goes to the right organisation). Fix obvious moved URLs that clearly belong to the same organisation; list the rest under "For the owner".
- [ ] **Freshness sweep.** Look for content that goes out of date: years, "currently", "this season", opening hours, prices, named office-holders, event dates. Don't change facts; list each one with its file and line under "For the owner" so Chris can confirm or update.
- [ ] **Accessibility basics.** Check that every page has one `h1` and headings in order, links make sense out of context (no "click here"), and the 3 images have meaningful `alt` text. Fix what doesn't need new facts.
- [ ] **404 page.** Once GoatCounter shows real broken links, make sure the most common ones are listed as redirects or linked from `404.html`.

## Needs the owner

- [ ] **Recover palnackie.scot.** The old Drupal site's domain now shows a "Site under maintenance" holding page. Get it transferred to a community-held account and forward it (domain-level 301) to palnackie.com.
- [ ] **Social sharing image.** There's no `og:image`, so links shared on Facebook have no picture. Needs a good landscape photo of the village (1200×630) that the community has rights to use.
- [ ] **Homepage hero image** (also listed in CLAUDE.md).
- [ ] **Village walks leaflet PDF**, **Buittle Quest constitution PDF**, **Household Emergency Lifesaving Plan** (listed in CLAUDE.md "Content to Add Later").
- [ ] **Inbound links.** Ask Buittle Quest, the Glenisle Inn, Flounders, D&G Council community pages and VisitScotland listings to link to palnackie.com. Use `?utm_campaign=<source>` on links you control (Facebook posts, noticeboard QR codes) so GoatCounter shows what works.
