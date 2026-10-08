import base64
import json
import re

from webfidelity import generator
from webfidelity.score import normalize, score_page


def payloads(html, api=None):
    found = re.findall(r"wfDecode\('([^']+)'\)", html) + re.findall(r'"([A-Za-z0-9+/=]{40,})"', html)
    if api and api.exists():
        found.append(json.loads(api.read_text())["html"])
    return [base64.b64decode(m).decode() for m in found]


def page_text(html, api=None):
    """HTML plus every base64 payload decoded: everything a perfect browser sees."""
    decoded = payloads(html, api)
    return re.sub(r"<[^>]+>", " ", html + " ".join(decoded))


def test_every_fact_is_on_its_page(tmp_path):
    for page in generator.generate(tmp_path, seeds=2):
        html = (tmp_path / page["path"]).read_text()
        text = normalize(page_text(html, tmp_path / "api" / f"{page['id']}.json"))
        for f in page["facts"]:
            assert all(normalize(p) in text for p in f["parts"]), (page["id"], f)


def test_hidden_content_not_in_raw_html(tmp_path):
    """JS-only pages must not leak facts as plain text in the source."""
    for page in generator.generate(tmp_path, seeds=2):
        if page["type"] in ("static_article", "pricing_table", "hidden_tabs"):
            continue
        html = (tmp_path / page["path"]).read_text()
        payload = " ".join(payloads(html, tmp_path / "api" / f"{page['id']}.json"))
        hidden = [f for f in page["facts"] if f["text"] in payload]
        assert hidden and not any(f["text"] in html for f in hidden)


def test_generation_is_deterministic(tmp_path):
    a = generator.generate(tmp_path / "a")
    b = generator.generate(tmp_path / "b")
    assert a == b


def test_row_fact_needs_same_line():
    fact = {"id": "f1", "kind": "row", "text": "X 1", "parts": ["Velora AB-123", "$12.00"]}
    assert score_page("| Velora AB-123 | **$12.00** |", [fact], {})["recall"] == 1
    assert score_page("Velora AB-123\n$12.00", [fact], {})["recall"] == 0
