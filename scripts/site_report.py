#!/usr/bin/env python3
"""Weekly analytics report for palnackie.com.

Combines two read-only sources and prints a Markdown report that the weekly
site agent uses to choose site changes:

  1. Google Search Console bulk export in BigQuery (how people find the site)
  2. GoatCounter API (what visitors actually read, and where they came from)

Either source is skipped with a note if its credentials are missing, so the
report still runs while one of them is being set up.

Credentials:
  BigQuery (first match wins):
    GCP_SA_KEY_JSON                 raw service-account JSON (cloud routine)
    GOOGLE_APPLICATION_CREDENTIALS  path to a key file (local use)
  GoatCounter:
    GOATCOUNTER_TOKEN               API token with "Read statistics" permission

Usage:
  pip install google-cloud-bigquery
  python scripts/site_report.py [--days 28] > report.md
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

PROJECT = "nash-claude-gcp"
DATASET = f"{PROJECT}.searchconsole_palnackiecom"
SITE = "https://palnackie.com"
GOATCOUNTER = "https://palnackie.goatcounter.com"


# ---------------------------------------------------------------- output

def md_table(title, rows):
    print(f"\n## {title}\n")
    if not rows:
        print("_No rows._")
        return
    cols = list(rows[0].keys())
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for r in rows:
        print("| " + " | ".join("" if r[c] is None else str(r[c]).replace("|", "\\|") for c in cols) + " |")


# ---------------------------------------------------------------- Search Console (BigQuery)

def bq_client():
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
    except ImportError:
        return None, "google-cloud-bigquery not installed (pip install google-cloud-bigquery)"
    raw = os.environ.get("GCP_SA_KEY_JSON")
    if raw:
        creds = service_account.Credentials.from_service_account_info(json.loads(raw))
        return bigquery.Client(project=PROJECT, credentials=creds), None
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        return bigquery.Client(project=PROJECT), None
    return None, "no credentials (set GCP_SA_KEY_JSON or GOOGLE_APPLICATION_CREDENTIALS)"


def gsc_section(days):
    print("\n# Part 1 — Google Search (Search Console)\n")
    bq, err = bq_client()
    if err:
        print(f"_Skipped: {err}._")
        return
    from google.cloud import bigquery

    def table(title, sql, params):
        try:
            job = bq.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params))
            md_table(title, [dict(r.items()) for r in job.result()])
            return True
        except Exception as e:  # dataset not created yet, permissions, etc.
            print(f"\n## {title}\n\n_Query failed: {str(e).splitlines()[0]}_")
            return False

    u = f"`{DATASET}.searchdata_url_impression`"
    s = f"`{DATASET}.searchdata_site_impression`"
    page = r"REGEXP_REPLACE(url, r'^https?://(www\.)?palnackie\.com', '')"
    win = f"""
      WITH bounds AS (SELECT MAX(data_date) AS mx FROM {u}),
      w AS (SELECT DATE_SUB(mx, INTERVAL @days - 1 DAY) AS cur_start, mx AS cur_end,
                   DATE_SUB(mx, INTERVAL 2 * @days - 1 DAY) AS prev_start,
                   DATE_SUB(mx, INTERVAL @days DAY) AS prev_end FROM bounds)
    """
    p = [bigquery.ScalarQueryParameter("days", "INT64", days)]

    print(f"Source: `{DATASET}`. Last {days} days vs previous {days}. "
          "Position = impression-weighted average (1 = top).")

    if not table("Data coverage", f"""
      SELECT MIN(data_date) first_day, MAX(data_date) last_day,
             COUNT(DISTINCT data_date) days FROM {u}""", []):
        print("\n_Remaining Search Console sections skipped._")
        return

    table("Weekly totals", f"""
      SELECT DATE_TRUNC(data_date, WEEK(MONDAY)) week, COUNT(DISTINCT data_date) days,
             SUM(clicks) clicks, SUM(impressions) impressions,
             ROUND(SAFE_DIVIDE(SUM(clicks), SUM(impressions)) * 100, 2) ctr_pct,
             ROUND(SUM(sum_position) / SUM(impressions) + 1, 1) position
      FROM {u} WHERE data_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 WEEK)
      GROUP BY 1 ORDER BY 1""", [])

    table("Pages: current vs previous window", win + f"""
      , agg AS (
        SELECT {page} AS pg,
          SUM(IF(data_date >= cur_start, impressions, 0)) AS ci,
          SUM(IF(data_date >= cur_start, clicks, 0)) AS cc,
          SUM(IF(data_date >= cur_start, sum_position, 0)) AS cp,
          SUM(IF(data_date <= prev_end, impressions, 0)) AS pi,
          SUM(IF(data_date <= prev_end, clicks, 0)) AS pc,
          SUM(IF(data_date <= prev_end, sum_position, 0)) AS pp
        FROM {u}, w WHERE data_date BETWEEN prev_start AND cur_end
        GROUP BY 1)
      SELECT pg AS page, ci AS impr, cc AS clicks,
             ROUND(SAFE_DIVIDE(cp, ci) + 1, 1) AS pos,
             pi AS prev_impr, pc AS prev_clicks,
             ROUND(SAFE_DIVIDE(pp, pi) + 1, 1) AS prev_pos
      FROM agg WHERE ci > 0 ORDER BY ci DESC LIMIT 40""", p)

    table("Top queries (current window)", win + f"""
      SELECT query, SUM(impressions) impr, SUM(clicks) clicks,
             ROUND(SUM(sum_top_position) / SUM(impressions) + 1, 1) pos
      FROM {s}, w WHERE data_date >= cur_start AND query IS NOT NULL
      GROUP BY 1 ORDER BY impr DESC LIMIT 50""", p)

    table("Query → page (which page Google shows for each query)", win + f"""
      SELECT query, {page} page, SUM(impressions) impr, SUM(clicks) clicks,
             ROUND(SUM(sum_position) / SUM(impressions) + 1, 1) pos
      FROM {u}, w WHERE data_date >= cur_start AND query IS NOT NULL
      GROUP BY 1, 2 HAVING impr >= 5 ORDER BY impr DESC LIMIT 60""", p)

    table("Striking distance: pos 4–20, ≥10 impressions, CTR < 3%", win + f"""
      SELECT * FROM (
        SELECT {page} AS page, query, SUM(impressions) AS impr, SUM(clicks) AS clk,
               ROUND(SUM(sum_position) / SUM(impressions) + 1, 1) AS pos
        FROM {u}, w WHERE data_date >= cur_start AND query IS NOT NULL
        GROUP BY 1, 2)
      WHERE impr >= 10 AND pos BETWEEN 4 AND 20 AND SAFE_DIVIDE(clk, impr) < 0.03
      ORDER BY impr DESC LIMIT 30""", p)

    # Old Drupal URLs, www/http variants, missing trailing slash — candidates for redirects.
    table("Non-canonical or legacy URLs getting impressions", win + f"""
      SELECT url, SUM(impressions) impr, SUM(clicks) clicks
      FROM {u}, w WHERE data_date >= cur_start
        AND (NOT STARTS_WITH(url, '{SITE}/')
             OR (NOT ENDS_WITH(url, '/') AND NOT REGEXP_CONTAINS(url, r'\\.[a-z]+$'))
             OR REGEXP_CONTAINS(url, r'/(node|content|taxonomy|sites/default)/|\\?q='))
      GROUP BY 1 ORDER BY impr DESC LIMIT 30""", p)


# ---------------------------------------------------------------- GoatCounter

def gc_get(path, params):
    token = os.environ["GOATCOUNTER_TOKEN"]
    url = f"{GOATCOUNTER}/api/v0{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def goatcounter_section(days):
    print("\n# Part 2 — Visitors (GoatCounter)\n")
    if not os.environ.get("GOATCOUNTER_TOKEN"):
        print("_Skipped: GOATCOUNTER_TOKEN not set._")
        return

    today = dt.date.today()
    cur = (today - dt.timedelta(days=days), today)
    prev = (today - dt.timedelta(days=2 * days), today - dt.timedelta(days=days))
    rng = lambda a, b: {"start": a.isoformat(), "end": b.isoformat()}
    print(f"Source: GoatCounter. Last {days} days ({cur[0]} → {cur[1]}) vs previous {days}. "
          "Counts are unique visitors.")

    def safe(title, fn):
        try:
            fn()
        except urllib.error.HTTPError as e:
            print(f"\n## {title}\n\n_API error {e.code}: {e.read()[:200]!r}_")
        except Exception as e:
            print(f"\n## {title}\n\n_Failed: {e}_")

    def totals():
        c = gc_get("/stats/total", rng(*cur)).get("total")
        p = gc_get("/stats/total", rng(*prev)).get("total")
        md_table("Totals", [{"window": "current", "visitors": c},
                            {"window": "previous", "visitors": p}])

    def pages():
        def fetch(a, b):
            out = {}
            data = gc_get("/stats/hits", {**rng(a, b), "limit": 100})
            for h in data.get("hits", []):
                out[h.get("path")] = (h.get("title") or "", h.get("count", 0))
            return out
        c, p = fetch(*cur), fetch(*prev)
        rows = [{"path": k, "title": v[0][:50], "visitors": v[1],
                 "prev_visitors": p.get(k, ("", 0))[1]}
                for k, v in sorted(c.items(), key=lambda kv: -kv[1][1])[:40]]
        md_table("Pages: current vs previous window", rows)
        dead = [{"path": k, "visitors": v[1]} for k, v in c.items()
                if k and not k.endswith("/") and "." not in k.rsplit("/", 1)[-1]]
        md_table("Paths without trailing slash (possible old links / 404s)", dead[:20])

    def refs():
        data = gc_get("/stats/toprefs", {**rng(*cur), "limit": 30})
        md_table("Top referrers (current window)",
                 [{"referrer": r.get("name") or "(direct / unknown)", "visitors": r.get("count")}
                  for r in data.get("stats", [])])

    def campaigns():
        data = gc_get("/stats/campaigns", {**rng(*cur), "limit": 20})
        md_table("Campaigns (current window)",
                 [{"campaign": r.get("name"), "visitors": r.get("count")}
                  for r in data.get("stats", [])])

    safe("Totals", totals)
    safe("Pages", pages)
    safe("Top referrers", refs)
    safe("Campaigns", campaigns)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28, help="current window length")
    days = ap.parse_args().days
    print(f"# palnackie.com analytics report — generated {dt.date.today()}")
    gsc_section(days)
    goatcounter_section(days)


if __name__ == "__main__":
    main()
