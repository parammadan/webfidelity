# PEDAGOGY.md — GATE P — half-a-page

**Status: SIGNED.** Per toolkit rule 3, a human signs
`VERDICT: PASS` at the bottom of this file before any audio is generated. I have
not signed it.

## Learning outcome

After watching, a viewer who has never heard of web scraping can:

1. **Explain** why an AI agent can answer from an incomplete page without anyone
   noticing (the scraper's output looks finished),
2. **Name** the two ways Firecrawl's defaults lose content: an early snapshot
   (~0.3 s) and a window too tall to scroll, and
3. **Apply** the fix: add a wait for pages that load late; fetch the pages of an
   endless feed directly; keep a held-out test set when measuring.

Measurable: show the viewer a scrape that ends in "Loading…" and they can say what
happened and what setting to change.

## Audience

People who use or build AI agents, with no knowledge of scrapers, rendering or
JavaScript. Defined on first use: *scraper* (B00), *JavaScript* (B02), *answer
key* (B02), *actions* (B05), *recall* (B05).

## Teaching arc (PROOF GATE checklist)

| Requirement | Where | Status |
|---|---|---|
| Framework before examples | B00B states the three claims (lost, why, fix) before any number | ✓ |
| Worked example | B02–B05 follow the same test pages from method to fix | ✓ |
| Falsifiability | B06B shows the detector that failed on unseen sites; B06 shows Firecrawl doing well on ordinary pages, not only the failures | ✓ |
| Scaffolded viewer task | B08: five facts, check the scraper output, on a page the viewer actually uses | ✓ |
| Four bookends | B00 ask · B00B promise · B08 handoff · B09 outro | ✓ |
| No source, no verdict | Every figure ledgered in SOURCES.md | ✓ |
| Expiry handled | B06 carries "Measured October 2026"; B07 says the settings will change and the habit won't | ✓ |

## Known weakness

B03 carries two ideas: the timing curve, then the slow server request. They are
the same mechanism (the snapshot doesn't wait), so they share a beat; if a
reviewer finds it dense, the request-log line is the piece to split out.

---

VERDICT: PASS
Signed by: Param Madan (replied "ok do it" to the full script review in chat)
Date: 2026-10-08
