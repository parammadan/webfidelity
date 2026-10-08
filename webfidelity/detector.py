"""Was this scrape incomplete? Decided WITHOUT the answer key.

Inputs are what a real user has: the scraped markdown, and optionally the
page's HTML source. Output is a score in [0, 1] plus the reasons behind it.
"""

import re

PLACEHOLDER = re.compile(
    r"\b(loading|fetching|please wait|one moment|retrieving|refreshing)\b[^\n]{0,40}?(\.\.\.|…)"
    r"|\bloading\b\s*$", re.I | re.M)
REVEAL_BUTTON = re.compile(
    r"<(button|a)\b[^>]*>\s*(show|load|read|view|see)\s+(more|all)\b", re.I)
ASYNC_HOOKS = {
    "fetch": re.compile(r"\bfetch\s*\(|XMLHttpRequest|axios\."),
    "timer": re.compile(r"\bsetTimeout\s*\("),
    "scroll": re.compile(r"IntersectionObserver|addEventListener\(\s*['\"]scroll"),
    "shadow": re.compile(r"attachShadow\s*\("),
}
TAG = re.compile(r"<script\b.*?</script>|<style\b.*?</style>|<title\b.*?</title>|<[^>]+>", re.S | re.I)
BLOCK = re.compile(r"</?(p|div|section|article|main|nav|aside|footer|header|li|tr|td|th|h[1-6]|button|br)\b[^>]*>", re.I)
EMPTY_MOUNT = re.compile(r"<(div|section|main|ul)\b[^>]*\bid=\"[^\"]+\"[^>]*>\s*</\1>", re.I)


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def words(text):
    return len(tokens(text))


def md_text(markdown):
    """Markdown -> plain text: images dropped, links reduced to their text."""
    markdown = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", markdown)
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", markdown)


def squash(text):
    """Letters and digits only: immune to spacing, punctuation, table pipes."""
    return "".join(tokens(text))


def source_coverage(markdown, html):
    """Share of the source's own sentences that made it into the output.
    Catches content that was in the HTML all along (e.g. hidden tabs) but
    got dropped. Returns None when the source has too little text to judge."""
    main = re.search(r"<(main|article)\b.*?</\1>", html, re.S | re.I)
    if main:  # boilerplate (nav, footer, banners) is fine to drop
        html = main.group(0)
    blocks = TAG.sub(" ", BLOCK.sub("\n", html)).splitlines()
    sents = [squash(s) for b in blocks for s in re.split(r"(?<=[.!?])\s", b) if words(s) >= 6]
    if len(sents) < 3:
        return None
    flat = squash(md_text(markdown))
    return sum(s in flat for s in sents) / len(sents)


def detect(markdown, html=None):
    reasons = {}

    last = None
    for last in PLACEHOLDER.finditer(markdown):
        pass
    if last:
        # a spinner followed by real content is a leftover; one followed by
        # little or nothing means the content never arrived
        after = words(markdown[last.end():])
        reasons["placeholder_text"] = 0.6 if after < 40 else 0.1

    if html:
        hooks = [k for k, rx in ASYNC_HOOKS.items() if rx.search(html)]
        mounts = len(EMPTY_MOUNT.findall(html))
        if REVEAL_BUTTON.search(html):
            reasons["reveal_button"] = 0.5
        # async hooks alone are normal on complete pages; they only count when
        # the output also looks thin or the source has empty slots to fill
        thin = words(markdown) < 60
        cov = source_coverage(markdown, html)
        if cov is not None and cov < 0.8:
            reasons[f"source_coverage_{cov:.0%}"] = 0.6
        if hooks and (thin or mounts):
            reasons["async_" + "+".join(hooks)] = 0.3 if not thin else 0.45
        if "shadow" in hooks and thin:
            reasons["shadow_root_thin_output"] = 0.3

    score = 1 - _prod(1 - w for w in reasons.values())
    return {"score": round(score, 3), "reasons": sorted(reasons)}


def _prod(xs):
    out = 1.0
    for x in xs:
        out *= x
    return out


def reveal_selector(html):
    """CSS selector for a 'Show more'-style button, if the source has one."""
    m = re.search(r"<(button|a)\b([^>]*)>\s*((show|load|read|view|see)\s+)?more\b", html, re.I)
    if not m:
        return None
    tag, attrs = m.group(1).lower(), m.group(2)
    id_ = re.search(r'\bid="([^"]+)"', attrs)
    cls = re.search(r'\bclass="([^"]+)"', attrs)
    if id_:
        return f"#{id_.group(1)}"
    return f"{tag}.{'.'.join(cls.group(1).split())}" if cls else tag
