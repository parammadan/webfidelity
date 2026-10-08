# Half a page: measuring what AI scrapers silently drop

When an AI agent reads a website, it doesn't see the page the way you do. A
scraper turns the page into text first, and the agent answers from whatever
text comes back. If the scraper misses part of the page, nobody tells the
agent. It just answers from half a page.

I wanted to know how often that happens, so I built a benchmark called
**WebFidelity** and pointed it at [Firecrawl](https://firecrawl.dev), one of
the most widely used scrapers for AI.

## You can't measure what's missing without an answer key

Most scraper comparisons eyeball the output. To measure what's missing, you
need to know what *should* have been there. So I generated 36 web pages and
planted 240 facts in them: prices, product codes, shipping counts. Some facts
are in the HTML from the start. Others only appear once JavaScript adds them:
after a delay, after a slow API call, when you scroll, or when you click
"Show more." Every scrape is then scored by counting how many facts survived.
No judgement calls.

## Finding 1: the snapshot comes about 300 ms after load

With default settings, Firecrawl captured content that arrived within 250 ms
in 5 runs out of 5. At 300 ms it captured it 2 times out of 5, and from
500 ms on it never did.

The part that matters for agents: **the output gives no sign of it.** It comes
back with a heading and a line that says "Loading release notes…", which looks
like a finished page.

A slow API call is no different. My test server logged Firecrawl's browser
sending the request about a quarter-second after load. It then took the
snapshot before the response arrived. A one-second API call was lost every
time, while a plain Playwright script that waits for the network to go quiet
got all of it.

## Finding 2: the browser window is 100,000 pixels tall

I asked Firecrawl's browser for its window size from inside the page:
`innerHeight` was 100,000, and `scrollY` stayed at 0 after every scroll
action.

That's a clever trick, because anything that loads "when it comes into view"
loads immediately. But feeds that load more content on scroll events never
trigger, and the scroll action does nothing. On two real infinite-scroll pages,
Firecrawl got 9% of the content with or without scrolling.

## The fix is free

Firecrawl's `actions` let you wait, scroll, or click before the snapshot. With
waits plus a click on any "Show more" button, recall on the test pages went
from **52% to 89%**. Each scrape cost 1 credit either way. The gap that remains
is the scroll-feed problem.

## The real web is kinder

Synthetic pages are built to break things, so I also tested real sites. There
the answer key is a patient local browser: it waits for the network to go
quiet and scrolls until the page stops growing. It loads each page right
before *and* right after the Firecrawl scrape, and only text present both times
counts, so vote counts and clocks that change by the minute aren't scored as
misses.

On **46 real sites I never tuned anything on, Firecrawl captured 85% by
default**, and most ordinary pages were 95–100%. Both failure modes showed up
on real sites too: a page that renders after 2 seconds went from 0% to 100%
with a wait, and a scroll feed stayed at 9%.

## What didn't work

I also tried to build a detector that flags incomplete scrapes *without* an
answer key, using leftover "Loading…" text, source text missing from the
output, empty JavaScript shells, and "Show more" buttons.

On held-out synthetic pages it was right 9 times in 10. **On real sites it had
never seen, it caught 2 of 9 incomplete pages.** Real sites keep their code in
external bundles, and scroll listeners turn out to be everywhere: 56% of
complete sites have them, against 60% of incomplete ones. So reading the code
can't tell the two apart.

The signal that *would* work is one only the renderer has: how many requests
were still pending, and how long the page had been quiet, when the snapshot
was taken. If scrapers exposed that, callers could retry only the pages that
need it.

## Mistakes I caught along the way

Several of my own early "findings" were bugs, and I think they're the most
useful part of the project:

- Rate-limit errors were scored as 0% recall, which made Firecrawl look
  unstable. It wasn't.
- My first infinite-scroll test page was broken: Chrome's scroll anchoring
  meant it could never load past batch 1.
- My first real-site scorer tripped on markdown link syntax and on pages
  changing between loads. Hacker News scored 17% before the fix and 98%
  after.
- Firecrawl refused one site outright (HTTP 403), and that was being counted
  as a 0% scrape.

Every number above was re-checked against raw outputs after these fixes, and
every rule was tested on data it was never tuned on.

## What to do with this

- If a page loads data after it opens, add a wait.
- If it's an endless feed, scrolling won't help, so fetch its pages directly.
- Whenever you measure anything, keep a test set you never tune on.

Video (3 min): [https://youtu.be/fscMxvmFdgM](https://youtu.be/fscMxvmFdgM)
· Code, data and method: [github.com/parammadan/webfidelity](https://github.com/parammadan/webfidelity)
· Interactive results: [parammadan.github.io/webfidelity](https://parammadan.github.io/webfidelity/)

*Measured October 2026 against Firecrawl's hosted API. Renderers change, so
re-run before relying on these numbers.*
