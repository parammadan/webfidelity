"""Score the completeness detector against every scrape we have on disk.

Ground truth: a scrape is incomplete if it missed any planted fact. Failed
requests are skipped. Prints precision/recall overall, per scraper and per
page type, plus the worst misses so they can be inspected by hand.

    python eval_detector.py [--threshold 0.5]
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from webfidelity.detector import detect

BENCH = Path("bench")


def load():
    sup = Path("results/SUPERSEDED.json")
    skip = {(x["dir"], x["type"]) for x in json.loads(sup.read_text())["skip"]} if sup.exists() else set()
    seen, rows = set(), []
    for scores in sorted(Path("results").glob("*/scores.json")):
        for r in json.loads(scores.read_text()):
            if r["error"] or (scores.parent.name, r["type"]) in skip:
                continue
            md_path = scores.parent / r["scraper"] / r["page"] / f"run{r['run']}.md"
            key = (r["scraper"], r["page"], r["run"], scores.parent.name)
            if key in seen or not md_path.exists():
                continue
            seen.add(key)
            rows.append({**r, "markdown": md_path.read_text(),
                         "html": (BENCH / "pages" / f"{r['page']}.html").read_text(),
                         "incomplete": r["recall"] < 1})
    return rows


def prf(pairs):
    tp = sum(p and t for p, t in pairs)
    fp = sum(p and not t for p, t in pairs)
    fn = sum(t and not p for p, t in pairs)
    prec = tp / (tp + fp) if tp + fp else 1.0
    rec = tp / (tp + fn) if tp + fn else 1.0
    return prec, rec, tp, fp, fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--split", choices=["dev", "test", "all"], default="all",
                    help="dev = page variants 0-1 (used to tune rules), test = 2-3 (held out)")
    ap.add_argument("--no-html", action="store_true", help="markdown-only detector")
    args = ap.parse_args()

    rows = load()
    if args.split != "all":
        keep = {"dev": "01", "test": "23"}[args.split]
        rows = [r for r in rows if r["page"][-1] in keep]
    for r in rows:
        d = detect(r["markdown"], None if args.no_html else r["html"])
        r["flag"], r["reasons"] = d["score"] >= args.threshold, d["reasons"]

    def line(name, rs):
        p, rc, tp, fp, fn = prf([(r["flag"], r["incomplete"]) for r in rs])
        print(f"{name:24} n={len(rs):4}  incomplete={sum(r['incomplete'] for r in rs):4}"
              f"  precision={p:5.0%}  recall={rc:5.0%}  (fp={fp}, fn={fn})")

    line("ALL", rows)
    print()
    for key in ("scraper", "type"):
        groups = defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        for k, rs in sorted(groups.items()):
            line(f"{key}={k}", rs)
        print()

    for label, cond in (("missed (incomplete, not flagged)", lambda r: r["incomplete"] and not r["flag"]),
                        ("false alarms (complete, flagged)", lambda r: r["flag"] and not r["incomplete"])):
        bad = [r for r in rows if cond(r)]
        kinds = defaultdict(int)
        for r in bad:
            kinds[(r["scraper"], r["type"], tuple(r["reasons"]))] += 1
        print(label)
        for (s, t, why), n in sorted(kinds.items(), key=lambda x: -x[1]):
            print(f"  {n:3}x {s:12} {t:16} reasons={list(why)}")


if __name__ == "__main__":
    main()
