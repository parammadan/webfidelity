"""Is 'scroll code in the page's JS files' a usable incompleteness signal?

Downloads each site's own script files (first 10, 3 MB cap each, cached under
<dir>/<site>/scripts/) and checks for scroll-driven loading code. If complete
pages have it as often as incomplete ones, the signal is noise.

    python -m probes.scriptscan results/real results/real-holdout
"""

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests

from probes.realsites import UA

SCROLL = re.compile(r"addEventListener\(\s*['\"]scroll['\"]|\bonscroll\b|IntersectionObserver")


def scripts_for(site_dir, url):
    cache = site_dir / "scripts"
    cache.mkdir(exist_ok=True)
    html = (site_dir / "source.html").read_text()
    out = [" ".join(re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.S))]
    for src in re.findall(r'<script[^>]+src="([^"]+)"', html)[:10]:
        full = urljoin(url, src.replace("&amp;", "&"))
        f = cache / (hashlib.sha1(full.encode()).hexdigest()[:12] + ".js")
        if not f.exists():
            try:
                r = requests.get(full, headers={"User-Agent": UA}, timeout=10, stream=True)
                f.write_bytes(r.raw.read(3_000_000, decode_content=True))
            except Exception:
                f.write_text("")
        out.append(f.read_text(errors="ignore"))
    return out


def main(dirs):
    rows = []
    for d in map(Path, dirs):
        for r in json.loads((d / "scores.json").read_text()):
            if r["cov_default"] is None or r["ref_sentences"] < 5:
                continue
            js = scripts_for(d / r["slug"], r["url"])
            rows.append({"url": r["url"], "incomplete": r["cov_default"] < 0.8,
                         "scroll_code": any(SCROLL.search(j) for j in js),
                         "kb": sum(len(j) for j in js) // 1000})
    for label, cond in (("incomplete", True), ("complete", False)):
        rs = [r for r in rows if r["incomplete"] == cond]
        hit = sum(r["scroll_code"] for r in rs)
        print(f"{label:11} sites={len(rs):3}  with scroll code in their JS: {hit} ({hit / len(rs):.0%})")
    for r in rows:
        if r["incomplete"]:
            print(f"   incomplete: {r['url'][8:60]:52} scroll_code={r['scroll_code']}  js={r['kb']}KB")


if __name__ == "__main__":
    main(sys.argv[1:])
