"""Detector-triggered retry: does re-scraping only the flagged pages recover
the lost content, and at what cost?

Scrapes every bench page twice: once with defaults, once 'heavy' (waits,
scrolls to the bottom, clicks any 'Show more'). Then compares policies:
always default, always heavy, heavy only when the detector flags the default
scrape, and an oracle that retries exactly the incomplete ones.

    python -m probes.retry --base-url https://<tunnel>/
"""

import argparse
import json
import os
import statistics
import time
from pathlib import Path

import requests

from webfidelity.detector import detect, reveal_selector
from webfidelity.scrapers import firecrawl_scrape
from webfidelity.score import score_page

BENCH = Path("bench")
JUMP = [{"type": "executeJavascript", "script": "window.scrollTo(0, document.body.scrollHeight)"},
        {"type": "wait", "milliseconds": 1000}]


def credits():
    r = requests.get("https://api.firecrawl.dev/v2/team/credit-usage",
                     headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}"}, timeout=30)
    return r.json()["data"]["remainingCredits"]


def heavy_actions(html):
    acts = [{"type": "wait", "milliseconds": 1500}] + JUMP * 4
    sel = reveal_selector(html)
    if sel:
        acts += [{"type": "click", "selector": sel}, {"type": "wait", "milliseconds": 1000}]
    return acts


def scrape_all(pages, base, noise, out, label, opts_fn):
    rows = []
    for page in pages:
        html = (BENCH / page["path"]).read_text()
        t0 = time.time()
        try:
            md, err = firecrawl_scrape(f"{base}{page['path']}?r={time.time_ns()}", **opts_fn(html)), None
        except Exception as e:
            md, err = "", f"{type(e).__name__}: {e}"
        f = out / label / page["id"] / "run0.md"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(md)
        s = score_page(md, page["facts"], noise)
        d = detect(md, html)
        rows.append({"scraper": label, "page": page["id"], "type": page["type"], "run": 0,
                     "secs": round(time.time() - t0, 2), "error": err, **s,
                     "detector_score": d["score"], "detector_reasons": d["reasons"]})
        print(f"{label:18} {page['id']:18} recall={s['recall']:.2f} flag={d['score'] >= 0.5}"
              + (f" ERROR {err}" if err else ""), flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--threshold", type=float, default=0.5)
    args = ap.parse_args()

    manifest = json.loads((BENCH / "manifest.json").read_text())
    pages, noise = manifest["pages"], manifest["noise"]
    out = Path("results") / f"{time.strftime('%Y%m%d-%H%M%S')}-retry"

    c0 = credits()
    dflt = scrape_all(pages, args.base_url, noise, out, "firecrawl", lambda h: {})
    c1 = credits()
    heavy = scrape_all(pages, args.base_url, noise, out, "firecrawl+actions",
                       lambda h: {"actions": heavy_actions(h)})
    c2 = credits()
    (out / "scores.json").write_text(json.dumps(dflt + heavy, indent=2))

    n = len(pages)
    cost_d, cost_h = (c0 - c1) / n, (c1 - c2) / n
    H = {r["page"]: r for r in heavy}
    policies = {
        "always default": [(r["recall"], cost_d, r["secs"]) for r in dflt],
        "always heavy": [(H[r["page"]]["recall"], cost_h, H[r["page"]]["secs"]) for r in dflt],
        "detector retry": [((H[r["page"]]["recall"], cost_d + cost_h, r["secs"] + H[r["page"]]["secs"])
                            if r["detector_score"] >= args.threshold else (r["recall"], cost_d, r["secs"]))
                           for r in dflt],
        "oracle retry": [((H[r["page"]]["recall"], cost_d + cost_h, r["secs"] + H[r["page"]]["secs"])
                          if r["recall"] < 1 else (r["recall"], cost_d, r["secs"])) for r in dflt],
    }
    print(f"\ncredits per page: default={cost_d:.2f}  heavy={cost_h:.2f}")
    print(f"{'policy':16} {'recall':>7} {'credits/page':>13} {'secs/page':>10}")
    for name, xs in policies.items():
        print(f"{name:16} {statistics.mean(x[0] for x in xs):7.0%} {statistics.mean(x[1] for x in xs):13.2f}"
              f" {statistics.mean(x[2] for x in xs):10.1f}")
    flagged = sum(r["detector_score"] >= args.threshold for r in dflt)
    print(f"\ndetector flagged {flagged}/{n} default scrapes for retry")
    print(f"\n{'page type':16} {'default':>8} {'heavy':>6} {'detector':>9}")
    for t in dict.fromkeys(r["type"] for r in dflt):
        rs = [r for r in dflt if r["type"] == t]
        det = [H[r["page"]]["recall"] if r["detector_score"] >= args.threshold else r["recall"] for r in rs]
        print(f"{t:16} {statistics.mean(r['recall'] for r in rs):8.0%}"
              f" {statistics.mean(H[r['page']]['recall'] for r in rs):6.0%} {statistics.mean(det):9.0%}")
    print(f"\n-> {out}/")


if __name__ == "__main__":
    main()
