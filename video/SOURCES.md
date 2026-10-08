# SOURCES.md — half-a-page

DOUBLE-CHECK LAW: every figure on screen, with where it comes from. All
measurements are the author's own (WebFidelity, `~/webfidelity`, repo
`parammadan/webfidelity`), taken October 7–8, 2026 against Firecrawl's hosted
`/v2/scrape` API with `maxAge: 0` (no cache). Firecrawl's renderer can change;
the reel dates its measurements on screen (B06).

| Beat | Figure | Source |
|---|---|---|
| B00B | Firecrawl is "one of the most popular scrapers for AI" | github.com/firecrawl/firecrawl: 189,488 stars, read via `gh repo view` on 2026-10-07 |
| B01, B03 | snapshot ≈ 300 ms; 5/5 captured at 0–250 ms, 2/5 at 300 ms, 0/5 at 500 ms, 1 s, 2 s | `results/timing-20261007-201251.json` (`probes/timing.py`, 50 default scrapes + 10 with waitFor) |
| B01 | output "# Release Notes / Loading release notes…" | `results/20261007-195227/firecrawl/js_rendered-0/run0.md` |
| B02 | 36 pages, 240 facts, 9 page types | `bench/manifest.json` from `webfidelity/generator.py` |
| B03 | browser sends the API request ~0.25 s after load, then snapshots before the response arrives | `results/requests.jsonl` (server request log) plus the slow_fetch scores in `results/20261008-081847/` |
| B04 | `innerHeight` = 100,000; `scrollY` stays 0 after scroll actions | `executeJavascript` probe on `infinite_scroll-0`, 2026-10-08 (output recorded in the README) |
| B04 | "A laptop screen is about 900" | Common laptop viewport height; the patient-browser reference used 1280×900 (`probes/realsites.py`) |
| B05 | recall 52% default → 89% with actions; 1 credit per page either way | `results/20261008-091300-retry/` (`probes/retry.py`); credit deltas from `/v2/team/credit-usage` before and after each pass |
| B06 | 85% mean coverage on 46 held-out real sites | `results/real-holdout/` (25 sites, 89%) + `results/real-holdout2/` (21 sites, 81%); sites with ≥5 stable reference sentences; one site Firecrawl refused (HTTP 403, speedtest.net) excluded as an error |
| B06 | delayed page 0% → 100% with a wait | `quotes.toscrape.com/js-delayed/page/2/?delay=2000`, held-out run |
| B06 | scroll feed 9% → 9% | `webscraper.io/test-sites/e-commerce/scroll/computers/laptops`, held-out run |
| B06B | detector right 9 in 10 on own test pages | `eval_detector.py --split test`, detector v1: 90% precision / 90% recall on held-out synthetic variants |
| B06B | caught 2 incomplete pages of 9 on unseen real sites | held-out 1: 1 of 3 (detector frozen before the run); held-out 2: 1 of 6 (detector v2 frozen before the run, 0 false alarms). One held-out-2 'incomplete' (aljazeera.com, 29%) is likely a regional-edition difference, not a render failure; it is counted, which makes the detector look worse, not better |
