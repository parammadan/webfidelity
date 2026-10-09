"""Live: ask Firecrawl's browser how tall its window is, and whether it scrolls.

    python demo_viewport.py https://<tunnel>/
"""

import json
import os
import sys
import time

import requests

from webfidelity import scrapers  # loads FIRECRAWL_API_KEY from .env

BOLD, CYAN, RED, OFF = "\033[1m", "\033[36m", "\033[31m", "\033[0m"
base = sys.argv[1].rstrip("/") + "/"
probe = "JSON.stringify({innerHeight: innerHeight, scrollY: Math.round(scrollY)})"
acts = [{"type": "executeJavascript", "script": probe},
        {"type": "executeJavascript", "script": "window.scrollTo(0, document.body.scrollHeight)"},
        {"type": "wait", "milliseconds": 800},
        {"type": "executeJavascript", "script": probe}]
print(f"{BOLD}asking Firecrawl's browser from inside the page…{OFF}")
r = requests.post("https://api.firecrawl.dev/v2/scrape", headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}"},
                  json={"url": f"{base}pages/infinite_scroll-0.html?r={time.time_ns()}", "formats": ["markdown"],
                        "maxAge": 0, "actions": acts}, timeout=180).json()
vals = [json.loads(x["value"]) for x in r["data"]["actions"]["javascriptReturns"] if x.get("type") == "string"]
before, after = vals[0], vals[-1]
print(f"  window.innerHeight        = {CYAN}{BOLD}{before['innerHeight']:,}{OFF} px")
print(f"  scrollY before scrolling  = {before['scrollY']}")
print(f"  scrollY after scrollTo()  = {RED}{BOLD}{after['scrollY']}{OFF}   <- it never moves")
