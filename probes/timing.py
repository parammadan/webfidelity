"""How late can JavaScript content arrive and still make it into a scrape?

Serves js_rendered pages whose content appears after N ms, scrapes each one
several times, and reports the share of runs that captured it.

    python -m probes.timing --base-url https://<tunnel>/ --runs 5
"""

import argparse
import json
import random
import time
from pathlib import Path

from webfidelity import generator
from webfidelity.scrapers import firecrawl_scrape
from webfidelity.score import score_page

DELAYS = [0, 50, 100, 150, 200, 250, 300, 500, 1000, 2000]
PROBE_DIR = Path("bench/probe")


def build():
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    facts = {}
    for d in DELAYS:
        html, f = generator.js_rendered(random.Random(f"timing:{d}"), delay_ms=d)
        (PROBE_DIR / f"timing-{d}.html").write_text(html)
        facts[d] = f
    return facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--runs", type=int, default=5)
    args = ap.parse_args()

    facts = build()
    rows = []
    for d in DELAYS:
        conds = [("default", {})] * args.runs + [("waitFor=5000", {"waitFor": 5000})]
        for i, (cond, opts) in enumerate(conds):
            # unique query string per request, so no cache anywhere can answer
            url = f"{args.base_url}probe/timing-{d}.html?r={time.time_ns()}"
            t0 = time.time()
            md = firecrawl_scrape(url, **opts)
            s = score_page(md, facts[d], {})
            rows.append({"delay_ms": d, "cond": cond, "run": i, "recall": s["recall"],
                         "secs": round(time.time() - t0, 2), "hash": s["hash"]})
            print(f"delay={d:5}ms {cond:13} recall={s['recall']:.2f}", flush=True)

    out = Path("results") / f"timing-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=2))

    print(f"\n{'delay_ms':>8} {'captured (default)':>19} {'waitFor=5000':>13}")
    for d in DELAYS:
        dflt = [r for r in rows if r["delay_ms"] == d and r["cond"] == "default"]
        wait = [r for r in rows if r["delay_ms"] == d and r["cond"] != "default"]
        hit = sum(r["recall"] == 1 for r in dflt)
        print(f"{d:>8} {hit:>14}/{len(dflt)} {wait[0]['recall']:>13.0%}")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
