"""Score a scraper's markdown against a page's answer key."""

import hashlib
import re


def normalize(text):
    """Strip markdown decoration so '**$1,284.50**' matches '$1,284.50'."""
    text = text.lower().replace("\\", "").replace(" ", " ")
    text = re.sub(r"[*_`]", "", text)
    return "\n".join(re.sub(r"\s+", " ", line).strip() for line in text.splitlines())


def fact_found(fact, norm):
    if fact["kind"] == "row":
        parts = [normalize(p) for p in fact["parts"]]
        return any(all(p in line for p in parts) for line in norm.splitlines())
    return normalize(fact["text"]) in norm


def score_page(markdown, facts, noise):
    norm = normalize(markdown)
    found = [f["id"] for f in facts if fact_found(f, norm)]
    leaked = [k for k, v in noise.items() if normalize(v) in norm]
    return {
        "recall": len(found) / len(facts) if facts else 1.0,
        "found": found,
        "missed": [f["id"] for f in facts if f["id"] not in found],
        "noise": len(leaked) / len(noise) if noise else 0.0,
        "noise_leaked": leaked,
        "lines": len(markdown.splitlines()),
        "hash": hashlib.sha256(markdown.encode()).hexdigest()[:12],
    }
