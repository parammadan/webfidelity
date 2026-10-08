"""Scraper adapters. Each takes a URL and returns markdown (or text)."""

import os
import re
import time
import urllib.request

import requests

_env = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env):
    for line in open(_env):
        k, _, v = line.strip().partition("=")
        if k and v:
            os.environ.setdefault(k, v)

def trafilatura_scrape(url):
    """Raw HTML + article extraction. No JavaScript."""
    import trafilatura
    html = urllib.request.urlopen(url, timeout=30).read().decode()
    return trafilatura.extract(html, output_format="markdown",
                               include_tables=True) or ""


class PlaywrightScraper:
    """Headless Chromium, wait, scroll, then body.innerText: the naive
    'just use a browser' approach."""

    def __init__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()

    def __call__(self, url):
        page = self._browser.new_page()
        try:
            page.goto(url, wait_until="networkidle")
            page.mouse.wheel(0, 20000)
            page.wait_for_timeout(1500)
            return page.inner_text("body")
        finally:
            page.close()

    def close(self):
        self._browser.close()
        self._pw.stop()


def firecrawl_scrape(url, **opts):
    """Firecrawl hosted API. maxAge=0 forces a fresh scrape, no cache, so
    repeated runs measure the pipeline and not the cache."""
    key = os.environ["FIRECRAWL_API_KEY"]
    for _ in range(6):
        r = requests.post("https://api.firecrawl.dev/v2/scrape",
                          headers={"Authorization": f"Bearer {key}"},
                          json={"url": url, "formats": ["markdown"], "maxAge": 0, **opts},
                          timeout=120)
        if r.status_code != 429:
            break
        wait = re.search(r"retry after (\d+)s", r.text)
        time.sleep(int(wait.group(1)) + 2 if wait else 30)
    r.raise_for_status()
    return r.json()["data"].get("markdown", "")


def get(name):
    if name == "trafilatura":
        return trafilatura_scrape
    if name == "playwright":
        return PlaywrightScraper()
    if name == "firecrawl":
        return firecrawl_scrape
    raise ValueError(f"unknown scraper {name}")
