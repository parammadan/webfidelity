from webfidelity.detector import detect

HTML = '<main><h1>Notes</h1><p>Loading release notes...</p><div id="app"></div></main><script>setTimeout(() => {}, 800)</script>'


def test_stuck_spinner_is_flagged():
    d = detect("# Notes\n\nLoading release notes...", HTML)
    assert d["score"] >= 0.5 and "placeholder_text" in d["reasons"]


def test_spinner_followed_by_content_is_not_enough():
    body = " ".join(["The Velora AB-123 ships with a 38-month warranty."] * 12)
    assert detect(f"# Notes\n\nLoading release notes...\n\n{body}")["score"] < 0.5


def test_dropped_source_text_is_flagged():
    html = "<main>" + "".join(f"<p>Sentence number {i} has quite a few words in it.</p>" for i in range(6)) + "</main>"
    md = "Sentence number 0 has quite a few words in it."
    assert any(r.startswith("source_coverage") for r in detect(md, html)["reasons"])


def test_unrendered_client_shell_is_flagged():
    shell = '<html><body><div id="root"></div><script src="/app.js"></script></body></html>'
    assert "csr_shell_unrendered" in detect("Quotes to Scrape", shell)["reasons"]
    rendered = " ".join(["Albert Einstein said the world as we have created it is a process of our thinking."] * 5)
    assert "csr_shell_unrendered" not in detect(rendered, shell)["reasons"]
