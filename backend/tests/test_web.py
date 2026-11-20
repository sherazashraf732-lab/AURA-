import pytest

from app.core.errors import AppError
from app.modules.web import check_url, default_search, html_to_text


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/admin",
        "http://localhost:8000",
        "http://169.254.169.254/latest/meta-data",  # cloud metadata
        "http://10.0.0.5",
        "http://192.168.1.1",
        "http://[::1]/",
        "file:///etc/passwd",
        "ftp://example.com",
        "http://user:pass@example.com",
        "javascript:alert(1)",
    ],
)
def test_ssrf_targets_blocked(url: str) -> None:
    with pytest.raises(AppError) as e:
        check_url(url)
    assert e.value.code == "blocked_url"


def test_html_to_text_strips_scripts_and_markup() -> None:
    doc = "<html><head><style>x{}</style><script>alert('x')</script></head><body><nav>menu</nav><h1>Title</h1><p>Hello &amp; welcome</p></body></html>"
    text = html_to_text(doc)
    assert "alert" not in text and "menu" not in text
    assert "Title" in text and "Hello & welcome" in text


def test_default_search_is_offline_without_keys() -> None:
    p = default_search()
    assert p.id == "fixture"
    hits = p.search("solar energy")
    assert len(hits) == 3 and all(h.url.startswith("https://example.org/") for h in hits)
