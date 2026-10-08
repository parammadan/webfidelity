"""Run scrapers over the benchmark pages and print a scorecard.

    python run.py --scrapers trafilatura,playwright --runs 3
    python run.py --scrapers firecrawl --base-url https://<public host>/
"""

import argparse
import functools
import http.server
import json
import statistics
import threading
import time
from collections import defaultdict
from pathlib import Path

from webfidelity import generator, scrapers
from webfidelity.score import score_page

BENCH = Path("bench")


def serve(port):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(BENCH))
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scrapers", default="trafilatura,playwright")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--base-url", help="where bench/ is hosted; default: serve locally")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    generator.generate(BENCH)
    manifest = json.loads((BENCH / "manifest.json").read_text())
    base = args.base_url or serve(args.port)
    out_dir = Path("results") / time.strftime("%Y%m%d-%H%M%S")
    rows = []

    for name in args.scrapers.split(","):
        scrape = scrapers.get(name)
        for page in manifest["pages"]:
            for run in range(args.runs):
                t0 = time.time()
                try:
                    md, err = scrape(base + page["path"]), None
                except Exception as e:
                    md, err = "", f"{type(e).__name__}: {e}"
                secs = time.time() - t0
                f = out_dir / name / page["id"] / f"run{run}.md"
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(md)
                s = score_page(md, page["facts"], manifest["noise"])
                rows.append({"scraper": name, "page": page["id"], "type": page["type"],
                             "run": run, "secs": round(secs, 2), "error": err, **s})
                print(f"{name:12} {page['id']:18} run{run} recall={s['recall']:.2f}"
                      + (f"  ERROR {err}" if err else ""))
        if hasattr(scrape, "close"):
            scrape.close()

    (out_dir / "scores.json").write_text(json.dumps(rows, indent=2))
    report(rows)
    print(f"\noutputs + scores.json -> {out_dir}/")


def report(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["scraper"], r["type"])].append(r)
    print(f"\n{'scraper':12} {'page type':15} {'recall':>7} {'noise':>6} {'stable':>7} {'errors':>6} {'secs':>5}")
    for (scraper, ptype), all_rs in sorted(groups.items()):
        rs = [r for r in all_rs if not r["error"]] or all_rs  # failed requests are not 0% recall
        by_page = defaultdict(set)
        for r in rs:
            by_page[r["page"]].add(r["hash"])
        stable = sum(len(h) == 1 for h in by_page.values()) / len(by_page)
        print(f"{scraper:12} {ptype:15} {statistics.mean(r['recall'] for r in rs):7.0%} "
              f"{statistics.mean(r['noise'] for r in rs):6.0%} {stable:7.0%} "
              f"{sum(1 for r in all_rs if r['error']):6} {statistics.mean(r['secs'] for r in rs):5.1f}")


if __name__ == "__main__":
    main()
