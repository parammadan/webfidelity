"""Live: when does Firecrawl take its snapshot? (one real scrape per delay)

    python demo_timing.py https://<tunnel>/
"""

import random
import sys
import time

from probes.timing import build
from webfidelity import generator
from webfidelity.scrapers import firecrawl_scrape
from webfidelity.score import score_page

RED, GREEN, DIM, BOLD, OFF = "\033[31m", "\033[32m", "\033[2m", "\033[1m", "\033[0m"
base = sys.argv[1].rstrip("/") + "/"
facts = build()
print(f"{BOLD}Firecrawl /v2/scrape · default settings · content appears after N ms{OFF}")
last_md = ""
for d in (0, 500, 1000, 2000):
    md = firecrawl_scrape(f"{base}probe/timing-{d}.html?r={time.time_ns()}")
    s = score_page(md, facts[d], {})
    n, total = len(s["found"]), len(facts[d])
    mark = f"{GREEN}✓ captured{OFF}" if s["recall"] == 1 else f"{RED}✕ MISSED{OFF}  "
    print(f"  {d:>5} ms   {mark}   {n:>2}/{total} facts")
    last_md = md
print(f"\n{DIM}what came back for the 2000 ms page:{OFF}")
for line in [l for l in last_md.splitlines() if l.strip()][:4]:
    if "cookie" in line.lower():
        continue
    print(f"  {BOLD if line.startswith('#') else ''}{line}{OFF}")
