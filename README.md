# WebFidelity

How much of a web page survives the scrape?

LLM agents read the web through scrapers. When a scraper silently drops
content, the agent answers from a partial page and nobody notices. WebFidelity
measures that loss: on synthetic pages with a planted answer key, and on real
sites against a patient-browser reference.

▶ **3-minute explainer video:** [https://youtu.be/fscMxvmFdgM](https://youtu.be/fscMxvmFdgM) · **Interactive results:** [parammadan.github.io/webfidelity](https://parammadan.github.io/webfidelity/)

The main subject is [Firecrawl](https://firecrawl.dev). Trafilatura and a
plain Playwright scraper are included for comparison.

## Findings

All Firecrawl numbers use the hosted `/v2/scrape` API with `maxAge: 0`
(no cache), October 2026.

**1. Default scrapes snapshot about 300 ms after load.** Content injected
later is dropped, and the output gives no sign of it: the heading and a
"Loading..." line come back looking like a finished page.

| content appears after | captured, default (5 runs) | with `waitFor: 5000` |
|---|---|---|
| 0–250 ms | 5/5 | 100% |
| 300 ms | 2/5 | 100% |
| 500 ms, 1 s, 2 s | 0/5 | 100% |

Real site: `quotes.toscrape.com/js-delayed` (2 s delay) scored **0%** with
defaults and **100%** with waits.

**2. In-flight requests are not awaited.** On a page whose content comes from
an API call that takes N ms, the server's request log shows Firecrawl's
browser *does* send the request (about 0.25 s after load), then snapshots
before the response lands.

| API latency | Firecrawl default | Playwright (`networkidle`) |
|---|---|---|
| 200 ms | 3/3 | 100% |
| 1 s, 2.5 s, 5 s | 0/3 each | 100% |

**3. The browser viewport is 100,000 px tall.** `innerHeight` reports
100000, so `scrollY` stays 0: scroll actions do nothing, and feeds that load
on scroll events never load. (IntersectionObserver lazy-loading benefits:
everything is "in view" at once.)

| infinite-scroll page | default | with scroll actions |
|---|---|---|
| synthetic feed (3 batches) | 0% | 0% |
| `quotes.toscrape.com/scroll` (real) | 9% | 9% |
| `webscraper.io/.../scroll/computers/laptops` (real, held out) | 9% | 9% |

**4. Where Firecrawl beats a plain browser.** Shadow DOM and hidden tabs:
Firecrawl 100%, Playwright `innerText` 0% and 33%. Converting the DOM, not
the visible text, pays off.

**5. Actions fix most of it, at no extra credit cost.** Waits plus a click
on any "Show more" button raised synthetic-bench recall from 52% to 89%. Actions
cost 1 credit per page, the same as a plain scrape. The remaining gap is
finding 3.

| page type | default | with actions |
|---|---|---|
| static article, pricing table, shadow DOM, hidden tabs | 100% | 100% |
| JS-rendered (800 ms) | 0% | 100% |
| lazy scroll | 33% | 100% |
| slow API (0.2–5 s) | 0% | 100% |
| click to load | 33% | 100% |
| infinite scroll | 0% | 0% |

Minor: a fixed-position cookie banner leaked into every Firecrawl output.

**On the normal web Firecrawl does well.** Mean coverage over 46 held-out
real sites: 85% default (held-out 1: 89% on 25 sites; held-out 2, which adds
client-rendered apps: 81% on 21 sites). 56 of 74 real sites score 90% or better.

## A detector that didn't generalize

Can you tell a scrape is incomplete *without* an answer key? A rule-based
detector (leftover "Loading..." text, source sentences missing from the
output, async hooks plus thin output, reveal buttons) looked strong on the
synthetic bench and fell apart on real sites:

| evaluation set | caught incomplete | false alarms |
|---|---|---|
| synthetic, held-out variants (v1) | 90% recall, 90% precision | |
| real sites, tuning set (v2) | 2 of 2 | 5 of 26 |
| real sites, held out 1 (v2, frozen) | **1 of 3** | 3 of 22 |
| real sites, held out 2 (v3: + "unrendered shell" signal, frozen) | **1 of 6** | 0 of 15 |

Why it failed on held-out sites:
- Real sites load their JS from external bundles; the detector only reads
  inline scripts, so the scroll feed showed no signal at all.
- The delayed-JS page scored 0.45 against a 0.5 threshold. The threshold was
  frozen before the held-out run and stays frozen.
- Reading external JS doesn't fix it: scroll code appears in 56% of complete
  sites and 60% of incomplete ones (`probes/scriptscan.py`), so it can't
  separate them.
- v3 added one signal (a JS-only page shell whose scrape adds no text beyond
  the shell). On a fresh held-out set it caught the delayed-JS page with zero
  false alarms, but still missed 5 of 6.

**Proposal.** The signal that would make this reliable is one only the
renderer has: how many network requests were still pending, and how long the
DOM had been quiet, at snapshot time. Exposing that in response metadata
would let callers retry only the scrapes that need it.

## Method

**Synthetic bench.** `webfidelity/generator.py` builds 36 pages (9 types × 4
variants). Each page plants unique facts (product codes, prices, counts) and
records them in `bench/manifest.json`. Content that only exists after
JavaScript runs is base64-encoded in the HTML, so raw-HTML scrapers can't
find it by accident. A fact counts as found if its text appears in the
output; table facts also need their row label and value on the same line.

**Real sites.** No answer key exists, so the reference is a patient local
browser: `networkidle`, then scroll until the page stops growing, with
nav/header/footer hidden (Firecrawl keeps main content only by default). The
reference is loaded right before and right after the Firecrawl scrapes, and
only sentences present in both count, so pages that change minute to minute
(vote counts, clocks) don't register as misses. Text is compared with
markdown links stripped and everything except letters and digits removed.

**Held-out discipline.** Detector rules were tuned on synthetic variants
0–1 and reported on 2–3; real-site rules were tuned on
`data/real_sites.tsv` and reported on `data/real_sites_holdout.tsv`.

## Mistakes caught along the way

- Rate-limit errors (HTTP 429) were first scored as 0% recall, which produced
  a fake "Firecrawl is unstable" result. Errors are now excluded.
- The first synthetic infinite-scroll page was broken: Chrome's scroll
  anchoring kept the sentinel in view, so batches 2–3 could never load.
  Earlier results are marked invalid in `results/SUPERSEDED.json`.
- The first real-site scorer broke on markdown link syntax, page drift and
  boilerplate (Hacker News scored 17%; corrected: 98%).
- Blind "Show more" clicking broke two real sites: an invalid Tailwind
  selector caused a server error, and clicking a generic link navigated away.
  Now only `<button>` elements with plain selectors are clicked.

- Firecrawl refused one held-out site (HTTP 403, speedtest.net); the first
  real-site scorer counted it as 0% coverage. Errored scrapes are now excluded.

## Limitations

- One week of measurements from one region; Firecrawl's renderer may change.
- The real-site reference runs from a residential connection and Firecrawl
  from a datacenter, so bot walls can differ (AP News challenged the local
  browser; IMDb served Firecrawl an ad page). Sites with fewer than 5 stable
  reference sentences are excluded. On aljazeera.com (29%) the missing headlines
  aren't in the raw source either, which points to a regional edition rather
  than a render failure; it is still counted.
- Finding 3 is shown on one synthetic and two real feeds; how many real sites
  use scroll listeners rather than IntersectionObserver isn't measured.

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest

# local scrapers, synthetic bench
.venv/bin/python run.py --scrapers trafilatura,playwright --runs 3

# Firecrawl needs FIRECRAWL_API_KEY in .env and a public URL for bench/
.venv/bin/python -m webfidelity.server 8765 &
cloudflared tunnel --url http://127.0.0.1:8765        # prints https://<x>.trycloudflare.com
.venv/bin/python run.py --scrapers firecrawl --base-url https://<x>.trycloudflare.com/
.venv/bin/python -m probes.timing --base-url https://<x>.trycloudflare.com/
.venv/bin/python -m probes.retry  --base-url https://<x>.trycloudflare.com/

# real sites
.venv/bin/python -m probes.realsites run
.venv/bin/python -m probes.realsites score
.venv/bin/python -m probes.realsites run   data/real_sites_holdout.tsv results/real-holdout
.venv/bin/python -m probes.realsites score data/real_sites_holdout.tsv results/real-holdout

.venv/bin/python eval_detector.py --split test
```

| path | what |
|---|---|
| `webfidelity/generator.py` | synthetic pages + answer key |
| `webfidelity/score.py` | fact recall, noise, stability |
| `webfidelity/scrapers.py` | Trafilatura, Playwright, Firecrawl adapters |
| `webfidelity/detector.py` | completeness detector |
| `webfidelity/server.py` | bench server with `/slow/<ms>/` delayed responses |
| `probes/timing.py` | snapshot-timing curve |
| `probes/retry.py` | default vs actions vs detector-triggered retry |
| `probes/realsites.py` | real-site reference + scoring |
