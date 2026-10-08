"""Collect the published numbers from results/ into docs/data.json, so the
demo page and charts are generated from runs, never typed in by hand."""

import json
import statistics
from pathlib import Path

R = Path("results")


def latest(pattern):
    return sorted(R.glob(pattern))[-1]


def timing():
    rows = json.loads(latest("timing-*.json").read_text())
    out = []
    for d in sorted({r["delay_ms"] for r in rows}):
        dflt = [r for r in rows if r["delay_ms"] == d and r["cond"] == "default"]
        wait = [r for r in rows if r["delay_ms"] == d and r["cond"] != "default"]
        out.append({"delay_ms": d, "default": sum(r["recall"] == 1 for r in dflt) / len(dflt),
                    "runs": len(dflt), "waitFor": sum(r["recall"] == 1 for r in wait) / len(wait)})
    return out


def retry():
    rows = json.loads(latest("*-retry/scores.json").read_text())
    out = []
    for t in dict.fromkeys(r["type"] for r in rows):
        get = lambda lab: statistics.mean(r["recall"] for r in rows if r["scraper"] == lab and r["type"] == t)
        out.append({"type": t, "default": get("firecrawl"), "actions": get("firecrawl+actions")})
    return out


def real():
    sets = {"tuning": "real", "held-out 1": "real-holdout", "held-out 2": "real-holdout2"}
    out = []
    for name, d in sets.items():
        f = R / d / "scores.json"
        if not f.exists():
            continue
        for r in json.loads(f.read_text()):
            if r["cov_default"] is None or r["ref_sentences"] < 5:
                continue
            out.append({"set": name, "url": r["url"], "category": r["category"],
                        "default": round(r["cov_default"], 3),
                        "actions": None if r["cov_heavy"] is None else round(r["cov_heavy"], 3),
                        "ref_sentences": r["ref_sentences"], "flagged": r["detector"] >= 0.5,
                        "reasons": r["reasons"]})
    return out


def detector(real_rows):
    out = []
    for name in dict.fromkeys(r["set"] for r in real_rows):
        rs = [r for r in real_rows if r["set"] == name]
        inc = [r for r in rs if r["default"] < 0.8]
        out.append({"set": name, "sites": len(rs), "incomplete": len(inc),
                    "caught": sum(r["flagged"] for r in inc),
                    "false_alarms": sum(r["flagged"] for r in rs if r["default"] >= 0.8)})
    return out


if __name__ == "__main__":
    rr = real()
    data = {"timing": timing(), "retry": retry(), "real": rr, "detector": detector(rr)}
    Path("docs").mkdir(exist_ok=True)
    Path("docs/data.json").write_text(json.dumps(data, indent=1))
    print(json.dumps(data["detector"], indent=1))
    print(f"{len(rr)} real sites, {len(data['timing'])} timing points, {len(data['retry'])} page types")
