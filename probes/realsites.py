"""Do the bench findings hold on real websites?

Answer key: what a patient local browser sees (network idle, then scroll
until the page stops growing), loaded twice; only sentences present in both
loads count, so rotating ads, timestamps and live numbers don't count as
'missed'. Firecrawl is scraped with defaults and with heavy actions; each
output is scored by how many answer-key sentences it contains.

    python -m probes.realsites ref            # local browser, free
    python -m probes.realsites firecrawl      # ~2 credits per site
    python -m probes.realsites score
"""

import json
import re
import statistics
import sys
import time
from pathlib import Path

import requests

from probes.retry import heavy_actions
from webfidelity.detector import detect, md_text, squash, tokens
from webfidelity.scrapers import firecrawl_scrape

SITES = Path("data/real_sites.tsv")
OUT = Path("results/real")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")


def sites():
    rows = [l.split("\t") for l in SITES.read_text().splitlines()[1:] if l.strip()]
    return [{"category": c, "url": u, "slug": re.sub(r"[^a-z0-9]+", "-", u.lower().split("//")[1]).strip("-")[:60]}
            for c, u in rows]


def sentences(text):
    out = set()
    for line in text.splitlines():
        for s in re.split(r"(?<=[.!?])\s", line):
            if len(tokens(s)) >= 5:
                out.add(squash(s))
    return out


def coverage(ref, md):
    flat = squash(md_text(md))
    return sum(s in flat for s in ref) / len(ref) if ref else None


def patient_load(browser, url):
    page = browser.new_page(user_agent=UA, viewport={"width": 1280, "height": 900})
    try:
        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
        except Exception:
            page.goto(url, wait_until="load", timeout=45000)
        page.wait_for_timeout(2000)
        last = 0
        for _ in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            h = page.evaluate("document.body.scrollHeight")
            if h == last:
                break
            last = h
        # Firecrawl keeps main content only by default; judge it on that
        page.evaluate("document.querySelectorAll('nav,header,footer,aside,[role=navigation],[role=contentinfo]')"
                      ".forEach(e => e.style.display = 'none')")
        return page.inner_text("body")
    finally:
        page.close()


def phase_ref():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for s in sites():
            d = OUT / s["slug"]
            d.mkdir(parents=True, exist_ok=True)
            try:
                r = requests.get(s["url"], headers={"User-Agent": UA}, timeout=30)
                (d / "source.html").write_text(r.text)
                for i in (1, 2):
                    (d / f"ref{i}.txt").write_text(patient_load(browser, s["url"]))
                print(f"ref ok   {s['url']}", flush=True)
            except Exception as e:
                print(f"ref FAIL {s['url']}  {type(e).__name__}: {e}", flush=True)
        browser.close()


def phase_firecrawl():
    for s in sites():
        d = OUT / s["slug"]
        src = (d / "source.html").read_text() if (d / "source.html").exists() else ""
        for label, opts in (("default", {}), ("heavy", {"actions": heavy_actions(src)})):
            t0 = time.time()
            try:
                md = firecrawl_scrape(s["url"], **opts)
                err = None
            except Exception as e:
                md, err = "", f"{type(e).__name__}: {e}"
            (d / f"fc_{label}.md").write_text(md)
            (d / f"fc_{label}.meta.json").write_text(json.dumps({"secs": round(time.time() - t0, 2), "error": err}))
            print(f"{label:8} {s['url']}" + (f"  ERROR {err}" if err else ""), flush=True)


def phase_run():
    """Sandwich: answer key loaded right before AND right after the two
    Firecrawl scrapes, so pages that change by the minute don't count."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for s in sites():
            d = OUT / s["slug"]
            d.mkdir(parents=True, exist_ok=True)
            try:
                src = requests.get(s["url"], headers={"User-Agent": UA}, timeout=30).text
                (d / "source.html").write_text(src)
                (d / "ref1.txt").write_text(patient_load(browser, s["url"]))
                for label, opts in (("default", {}), ("heavy", {"actions": heavy_actions(src)})):
                    t0, err = time.time(), None
                    try:
                        md = firecrawl_scrape(s["url"], **opts)
                    except Exception as e:
                        md, err = "", f"{type(e).__name__}: {e}"
                    (d / f"fc_{label}.md").write_text(md)
                    (d / f"fc_{label}.meta.json").write_text(json.dumps({"secs": round(time.time() - t0, 2), "error": err}))
                (d / "ref2.txt").write_text(patient_load(browser, s["url"]))
                print(f"ok   {s['url']}", flush=True)
            except Exception as e:
                print(f"FAIL {s['url']}  {type(e).__name__}: {e}", flush=True)
        browser.close()


def phase_score():
    rows = []
    for s in sites():
        d = OUT / s["slug"]
        if not (d / "ref2.txt").exists() or not (d / "fc_default.md").exists():
            continue
        err = lambda lab: (json.loads((d / f"fc_{lab}.meta.json").read_text()).get("error")
                           if (d / f"fc_{lab}.meta.json").exists() else None)
        if err("default"):  # Firecrawl refused or failed: an error, not a miss
            print(f"skip (firecrawl error) {s['url']}: {err('default')[:60]}")
            continue
        ref = sentences((d / "ref1.txt").read_text()) & sentences((d / "ref2.txt").read_text())
        md_d, md_h = (d / "fc_default.md").read_text(), (d / "fc_heavy.md").read_text()
        det = detect(md_d, (d / "source.html").read_text())
        rows.append({**s, "ref_sentences": len(ref), "cov_default": coverage(ref, md_d),
                     "cov_heavy": None if err("heavy") else coverage(ref, md_h), "detector": det["score"], "reasons": det["reasons"],
                     "words_default": len(tokens(md_d)), "words_heavy": len(tokens(md_h))})
    (OUT / "scores.json").write_text(json.dumps(rows, indent=2))

    def pct(x):
        return "  n/a" if x is None else f"{x:5.0%}"
    print(f"{'category':20} {'site':48} {'ref':>4} {'default':>8} {'heavy':>6} {'flag':>5}")
    for r in rows:
        print(f"{r['category']:20} {r['url'][8:56]:48} {r['ref_sentences']:4} {pct(r['cov_default']):>8}"
              f" {pct(r['cov_heavy']):>6} {'YES' if r['detector'] >= 0.5 else '':>5}")
    ok = [r for r in rows if r["cov_default"] is not None]
    print(f"\nmean coverage over {len(ok)} sites: default {statistics.mean(r['cov_default'] for r in ok):.0%}"
          f", heavy {statistics.mean(r['cov_heavy'] for r in ok if r['cov_heavy'] is not None):.0%}")


if __name__ == "__main__":
    if len(sys.argv) > 2:  # alternate site list + output dir, e.g. a held-out set
        SITES, OUT = Path(sys.argv[2]), Path(sys.argv[3])
    {"ref": phase_ref, "firecrawl": phase_firecrawl, "run": phase_run, "score": phase_score}[sys.argv[1]]()
