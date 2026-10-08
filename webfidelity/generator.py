"""Synthetic test pages with a known answer key.

Every page embeds facts we planted ourselves, so scoring a scraper needs no
hand labelling: a fact either survived into the output or it did not.

Content that a real browser only sees after JavaScript runs is base64-encoded
in the HTML, so a scraper reading raw HTML cannot find it by accident.
"""

import base64
import json
import random
from pathlib import Path

BRANDS = ["Velora", "Quintex", "Marlowe", "Ostrava", "Kestrel", "Nimbra",
          "Halcyon", "Tervo", "Brightwell", "Corvane", "Lumio", "Saffra"]
CITIES = ["Tallinn", "Porto", "Gdansk", "Leeds", "Valencia", "Tampere",
          "Brno", "Cork", "Bergen", "Graz", "Malmo", "Lyon"]
FILLER = [
    "Teams evaluating the platform usually start with a short pilot.",
    "The release notes cover the remaining changes in more detail.",
    "Feedback from early customers shaped most of this update.",
    "Support is available through the usual channels during business hours.",
    "Pricing may vary by region and contract length.",
]


def b64(text):
    return base64.b64encode(text.encode()).decode()


class Facts:
    """Collects planted facts. kind 'text' = string must appear; kind 'row' =
    all parts must appear on one line (table structure survived)."""

    def __init__(self, rng):
        self.rng = rng
        self.items = []
        self.used = set()

    def code(self):
        while True:
            c = f"{self.rng.choice('ABCDEFGHJKMNPQRSTVWXZ')}{self.rng.choice('ABCDEFGHJKMNPQRSTVWXZ')}-{self.rng.randint(100, 999)}"
            if c not in self.used:
                self.used.add(c)
                return c

    def product(self):
        return f"{self.rng.choice(BRANDS)} {self.code()}"

    def price(self):
        return f"${self.rng.randint(12, 4999):,}.{self.rng.randint(0, 99):02d}"

    def add(self, text, question, kind="text", parts=None):
        self.items.append({"id": f"f{len(self.items) + 1}", "kind": kind,
                           "text": text, "parts": parts or [text],
                           "question": question})
        return text

    def sentence(self):
        """One prose sentence carrying one fact. Fact strings are unique per
        page, so finding one in the output is never ambiguous."""
        taken = {f["text"] for f in self.items}
        while True:
            p = self.product()
            n = self.rng.randint(0, 2)
            if n == 0:
                m = self.rng.randint(13, 59)
                fact, q = f"{m}-month warranty", f"How long is the warranty on the {p}?"
                s = f"The {p} ships with a {m}-month warranty."
            elif n == 1:
                city = self.rng.choice(CITIES)
                k = self.rng.randint(120, 980)
                fact, q = f"{k} units", f"How many {p} units were shipped to {city}?"
                s = f"Last quarter, {k} units of the {p} were shipped to {city}."
            else:
                pct = self.rng.randint(11, 89)
                fact, q = f"{pct}% lower latency", f"How much lower is the {p}'s latency?"
                s = f"Benchmarks show the {p} delivers {pct}% lower latency than its predecessor."
            if fact not in taken:
                self.add(fact, q)
                return s


NOISE = {
    "cookie": "We use cookies to improve your experience. Accept all cookies?",
    "nav": "Home | Products | Pricing | Careers | Contact",
    "footer": "Copyright 2026 Example Corp. All rights reserved. Privacy | Terms",
    "ad": "Sponsored: Try CloudBoost free for 30 days",
}


def shell(title, body, script=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title></head>
<body>
<div id="cookie-banner" style="position:fixed;bottom:0;background:#eee">{NOISE['cookie']} <button>Accept</button></div>
<nav>{NOISE['nav']}</nav>
<aside class="ad">{NOISE['ad']}</aside>
<main>
<h1>{title}</h1>
{body}
</main>
<footer>{NOISE['footer']}</footer>
<script>
function wfDecode(s) {{ return new TextDecoder().decode(Uint8Array.from(atob(s), c => c.charCodeAt(0))); }}
{script}
</script>
</body></html>
"""


def paragraphs(facts, n):
    out = []
    for _ in range(n):
        sents = [facts.sentence(), facts.rng.choice(FILLER), facts.sentence()]
        out.append("<p>" + " ".join(sents) + "</p>")
    return "\n".join(out)


def static_article(rng):
    """Control: plain server-rendered HTML. Every scraper should ace this."""
    f = Facts(rng)
    return shell("Quarterly Product Update", paragraphs(f, 4)), f.items


def pricing_table(rng):
    """Tables: cells must survive AND stay on the same row as their label."""
    f = Facts(rng)
    rows = []
    for _ in range(8):
        name, price = f.product(), f.price()
        seats = rng.randint(2, 500)
        f.add(f"{name} {price}", f"What is the price of the {name}?",
              kind="row", parts=[name, price])
        rows.append(f"<tr><td>{name}</td><td>{price}</td><td>{seats} seats</td></tr>")
    body = (paragraphs(f, 1) +
            "<table><thead><tr><th>Plan</th><th>Price</th><th>Seats</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")
    return shell("Plans and Pricing", body), f.items


def js_rendered(rng, delay_ms=800):
    """Content injected by JavaScript after load, as in client-rendered apps."""
    f = Facts(rng)
    hidden = paragraphs(f, 3)
    body = '<p>Loading release notes...</p><div id="app"></div>'
    script = (f"setTimeout(() => {{ document.getElementById('app').innerHTML = "
              f"wfDecode('{b64(hidden)}'); }}, {delay_ms});")
    return shell("Release Notes", body, script), f.items


def shadow_dom(rng):
    """Content inside a web component's shadow root."""
    f = Facts(rng)
    hidden = paragraphs(f, 3)
    body = "<product-specs></product-specs>"
    script = (f"customElements.define('product-specs', class extends HTMLElement {{"
              f" connectedCallback() {{ this.attachShadow({{mode: 'open'}}).innerHTML = "
              f"wfDecode('{b64(hidden)}'); }} }});")
    return shell("Product Specifications", body, script), f.items


def lazy_scroll(rng):
    """Content that loads only once the reader scrolls near the bottom."""
    f = Facts(rng)
    visible = paragraphs(f, 1)
    hidden = paragraphs(f, 2)
    body = (visible + '<div style="height:4000px"></div>'
            '<div id="more"></div><div id="sentinel">Loading more...</div>')
    script = (f"new IntersectionObserver((es, o) => {{ if (es[0].isIntersecting) {{"
              f" document.getElementById('more').innerHTML = wfDecode('{b64(hidden)}');"
              f" o.disconnect(); }} }}).observe(document.getElementById('sentinel'));")
    return shell("Customer Stories", body, script), f.items


FETCH_DELAYS = [200, 1000, 2500, 5000]


def slow_fetch(rng, seed=0):
    """Content from an API call that takes FETCH_DELAYS[seed] ms. Unlike a
    timer, a browser can see this request is still pending."""
    f = Facts(rng)
    hidden = paragraphs(f, 3)
    ms = FETCH_DELAYS[seed % len(FETCH_DELAYS)]
    body = '<p>Fetching account activity...</p><div id="feed"></div>'
    script = (f"fetch('/slow/{ms}/api/__PAGE_ID__.json').then(r => r.json()).then(d => {{"
              f" document.getElementById('feed').innerHTML = wfDecode(d.html); }});")
    return shell("Account Activity", body, script), f.items, {"api": json.dumps({"html": b64(hidden)})}


def infinite_scroll(rng):
    """Three batches, each loaded when the reader reaches the bottom. Facts
    carry their batch number, so we can see how deep a scraper got."""
    f = Facts(rng)
    batches = []
    for i in range(3):
        start = len(f.items)
        batches.append(b64(paragraphs(f, 1)))
        for fact in f.items[start:]:
            fact["batch"] = i + 1
    body = '<div id="feed"></div><div style="height:3000px"></div><div id="sentinel">Loading more...</div>'
    script = (f"const batches = {json.dumps(batches)}; let n = 0;"
              f" const io = new IntersectionObserver(es => {{ if (es[0].isIntersecting && n < batches.length) {{"
              f" const d = document.createElement('div'); d.innerHTML = wfDecode(batches[n++]);"
              f" d.style.marginBottom = '3000px'; document.getElementById('feed').appendChild(d);"
              f" if (n == batches.length) io.disconnect(); }} }});"
              f" io.observe(document.getElementById('sentinel'));")
    return shell("Community Feed", body, script), f.items


def hidden_tabs(rng):
    """Three tabs; only the first is visible, the others are display:none but
    already in the HTML. A scraper that renders 'what you see' loses them."""
    f = Facts(rng)
    panels = [paragraphs(f, 1) for _ in range(3)]
    tabs = "".join(f'<button onclick="show({i})">Tab {i + 1}</button>' for i in range(3))
    body = tabs + "".join(
        f'<section class="panel" style="display:{"block" if i == 0 else "none"}">{p}</section>'
        for i, p in enumerate(panels))
    script = ("function show(i) { document.querySelectorAll('.panel').forEach("
              "(p, j) => p.style.display = i == j ? 'block' : 'none'); }")
    return shell("Technical Details", body, script), f.items


def click_to_load(rng):
    """Half the content only exists after the reader clicks 'Show more'."""
    f = Facts(rng)
    visible = paragraphs(f, 1)
    hidden = paragraphs(f, 2)
    body = visible + '<div id="rest"></div><button id="more-btn">Show more</button>'
    script = (f"document.getElementById('more-btn').onclick = () => {{"
              f" document.getElementById('rest').innerHTML = wfDecode('{b64(hidden)}'); }};")
    return shell("Frequently Asked Questions", body, script), f.items


PAGE_TYPES = {
    "static_article": static_article,
    "pricing_table": pricing_table,
    "js_rendered": js_rendered,
    "shadow_dom": shadow_dom,
    "lazy_scroll": lazy_scroll,
    "slow_fetch": slow_fetch,
    "infinite_scroll": infinite_scroll,
    "hidden_tabs": hidden_tabs,
    "click_to_load": click_to_load,
}


def generate(out_dir, seeds=4):
    out = Path(out_dir)
    for d in ("pages", "api"):
        (out / d).mkdir(parents=True, exist_ok=True)
    manifest = []
    for ptype, fn in PAGE_TYPES.items():
        for seed in range(seeds):
            page_id = f"{ptype}-{seed}"
            rng = random.Random(f"{ptype}:{seed}")
            res = fn(rng, seed) if fn is slow_fetch else fn(rng)
            html, facts = res[0].replace("__PAGE_ID__", page_id), res[1]
            for _, content in (res[2] if len(res) > 2 else {}).items():
                (out / "api" / f"{page_id}.json").write_text(content)
            (out / "pages" / f"{page_id}.html").write_text(html)
            manifest.append({"id": page_id, "type": ptype,
                             "path": f"pages/{page_id}.html", "facts": facts})
    (out / "manifest.json").write_text(json.dumps(
        {"noise": NOISE, "pages": manifest}, indent=2))
    return manifest


if __name__ == "__main__":
    pages = generate("bench")
    print(f"{len(pages)} pages, {sum(len(p['facts']) for p in pages)} facts -> bench/")
