import json

import pytest
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services import chat as chat_svc
from tests.conftest import Api, make_user


def sse(text: str) -> list[tuple[str, dict]]:
    events = []
    for block in text.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)
        if "event" in lines:
            events.append((lines["event"], json.loads(lines["data"])))
    return events


def new_chat(api: Api, **kw) -> str:
    r = api.post("/conversations", {"provider": "mock", "model": "aura-mock-1", **kw})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def send(api: Api, cid: str, text: str) -> list[tuple[str, dict]]:
    r = api.post(f"/conversations/{cid}/messages", {"content": text})
    assert r.status_code == 200, r.text
    return sse(r.text)


def test_chat_round_trip_and_language(db: Session) -> None:
    api = make_user(db)
    cid = new_chat(api)
    events = send(api, cid, "aap kaise hain")
    kinds = [e for e, _ in events]
    assert kinds[0] == "meta" and kinds[-1] == "done" and "delta" in kinds
    assert events[0][1]["language"] == "ur-Latn"
    reply = "".join(d["text"] for e, d in events if e == "delta")
    assert "Demo jawab" in reply  # mock replies follow the Roman Urdu instruction
    msgs = api.get(f"/conversations/{cid}/messages").json()
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert api.get(f"/conversations/{cid}").json()["title"] == "aap kaise hain"


def test_unverified_user_cannot_chat(api: Api, db: Session) -> None:
    api.post("/auth/signup", {"email": "nv@example.com", "password": "correct-horse-1"})
    api.post("/auth/login", {"email": "nv@example.com", "password": "correct-horse-1"})
    r = api.post("/conversations", {"provider": "mock", "model": "aura-mock-1"})
    assert r.status_code == 403 and r.json()["error"]["code"] == "email_unverified"


def test_cross_user_isolation(db: Session) -> None:
    alice = make_user(db, "alice@example.com")
    bob = make_user(db, "bob@example.com")
    cid = new_chat(alice)
    send(alice, cid, "secret plans")
    mem = alice.post("/memory", {"content": "Alice likes tea"}).json()["id"]

    for path in (
        f"/conversations/{cid}",
        f"/conversations/{cid}/messages",
        f"/conversations/{cid}/export",
    ):
        assert bob.get(path).status_code == 404
    assert bob.post(f"/conversations/{cid}/messages", {"content": "hi"}).status_code == 404
    assert bob.patch(f"/conversations/{cid}", {"title": "pwned"}).status_code == 404
    assert bob.delete(f"/conversations/{cid}").status_code == 404
    assert bob.patch(f"/memory/{mem}", {"content": "x"}).status_code == 404
    assert bob.delete(f"/memory/{mem}").status_code == 404
    assert bob.get("/conversations").json() == []
    assert bob.get("/memory").json() == []
    assert bob.get("/conversations?q=secret").json() == []
    assert alice.get(f"/conversations/{cid}").json()["title"] == "secret plans"


def test_memory_is_used_only_when_enabled(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    api = make_user(db)
    api.post("/memory", {"content": "User prefers metric units"})
    seen: list[str] = []
    real = chat_svc.build_context

    def spy(*a, **kw):  # type: ignore[no-untyped-def]
        ctx = real(*a, **kw)
        seen.append(ctx[0].content)
        return ctx

    monkeypatch.setattr(chat_svc, "build_context", spy)
    cid = new_chat(api)
    send(api, cid, "hello")
    assert "metric units" in seen[-1] and "<memory>" in seen[-1]

    api.patch("/auth/me", {"memory_enabled": False})
    send(api, cid, "hello again")
    assert "metric units" not in seen[-1]


def test_memory_crud_and_disable(db: Session) -> None:
    api = make_user(db)
    mid = api.post("/memory", {"content": "Lives in Lahore"}).json()["id"]
    assert api.patch(f"/memory/{mid}", {"enabled": False}).json()["enabled"] is False
    assert (
        api.patch(f"/memory/{mid}", {"content": "Lives in Karachi"}).json()["content"]
        == "Lives in Karachi"
    )
    assert api.delete(f"/memory/{mid}").status_code == 204
    api.post("/memory", {"content": "a"})
    api.post("/memory", {"content": "b"})
    assert api.delete("/memory").status_code == 204
    assert api.get("/memory").json() == []


def test_project_memory_does_not_leak_outside_project(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = make_user(db)
    pid = api.post("/projects", {"name": "Thesis"}).json()["id"]
    api.post("/memory", {"content": "Thesis deadline is June", "project_id": pid})
    seen: list[str] = []
    real = chat_svc.build_context
    monkeypatch.setattr(
        chat_svc,
        "build_context",
        lambda *a, **k: (seen.append((ctx := real(*a, **k))[0].content), ctx)[1],
    )
    send(api, new_chat(api), "hi")
    assert "Thesis deadline" not in seen[-1]
    send(api, new_chat(api, project_id=pid), "hi")
    assert "Thesis deadline" in seen[-1]


def test_daily_quota_enforced(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "default_user_daily_request_limit", 1)
    api = make_user(db)
    cid = new_chat(api)
    for _ in range(chat_svc.MOCK_DAILY_MULTIPLIER):
        send(api, cid, "hi")
    r = api.post(f"/conversations/{cid}/messages", {"content": "one more"})
    assert r.status_code == 429 and r.json()["error"]["code"] == "daily_limit"


def test_external_provider_requires_consent_and_configuration(db: Session) -> None:
    api = make_user(db)
    cid = api.post("/conversations", {"provider": "groq", "model": "openai/gpt-oss-120b"}).json()[
        "id"
    ]
    r = api.post(f"/conversations/{cid}/messages", {"content": "hi"})
    assert r.status_code == 403 and r.json()["error"]["code"] == "consent_required"
    api.patch("/auth/me", {"provider_consent": True})
    r = api.post(f"/conversations/{cid}/messages", {"content": "hi"})
    assert r.status_code == 503 and r.json()["error"]["code"] == "provider_unconfigured"


def test_unknown_model_rejected(db: Session) -> None:
    api = make_user(db)
    r = api.post("/conversations", {"provider": "mock", "model": "gpt-99"})
    assert r.status_code == 400


def test_models_listing_never_marks_paid_available(db: Session) -> None:
    api = make_user(db)
    providers = api.get("/models").json()
    assert {p["id"] for p in providers} >= {"mock", "groq", "gemini", "openrouter"}
    assert all(not p["paid"] for p in providers)
    mock = next(p for p in providers if p["id"] == "mock")
    assert mock["available"] is True and mock["requires_consent"] is False


def test_manual_and_automatic_continuation(db: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    api = make_user(db)
    cid = new_chat(api)
    send(api, cid, "We decided to use PostgreSQL for the project.")
    r = api.post(f"/conversations/{cid}/continue")
    assert r.status_code == 201
    new = r.json()
    assert new["continued_from_id"] == cid and new["continuation_summary_id"]
    summary = api.get(f"/summaries/{new['continuation_summary_id']}").json()
    assert summary["version"] == 1 and "goal" in summary["content"]
    # Original chat is preserved untouched.
    assert len(api.get(f"/conversations/{cid}/messages").json()) == 2

    # Automatic: shrink the threshold so the next message triggers a continuation.
    monkeypatch.setattr(chat_svc, "REPLY_RESERVE_TOKENS", 6000)
    events = send(api, cid, "next question")
    assert events[0][0] == "continued"
    cont_id = events[0][1]["conversation_id"]
    assert cont_id != cid
    assert api.get(f"/conversations/{cont_id}").json()["continued_from_id"] == cid


def test_summary_edit_and_delete(db: Session) -> None:
    api = make_user(db)
    cid = new_chat(api)
    send(api, cid, "hello")
    sid = api.post(f"/conversations/{cid}/continue").json()["continuation_summary_id"]
    r = api.put(f"/summaries/{sid}", {"content": {"goal": "Edited goal", "pending": ["x"]}})
    assert r.status_code == 200 and r.json()["content"]["goal"] == "Edited goal"
    assert api.delete(f"/summaries/{sid}").status_code == 204
    assert api.get(f"/summaries/{sid}").status_code == 404


def test_search_and_archive(db: Session) -> None:
    api = make_user(db)
    a = new_chat(api)
    send(api, a, "Discuss quantum computing")
    b = new_chat(api)
    send(api, b, "Recipe for biryani")
    assert [c["id"] for c in api.get("/conversations?q=biryani").json()] == [b]
    assert api.get("/conversations?q=%25").json() == []  # wildcard is escaped, not a match-all
    api.patch(f"/conversations/{a}", {"archived": True})
    assert [c["id"] for c in api.get("/conversations").json()] == [b]
    assert [c["id"] for c in api.get("/conversations?archived=true").json()] == [a]
    r = api.post(f"/conversations/{a}/messages", {"content": "hi"})
    assert r.status_code == 409


def test_auto_provider_fails_over_between_free_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.errors import AppError
    from app.modules import providers as pv

    calls: list[str] = []

    def fake(pid: str, fail: bool):  # type: ignore[no-untyped-def]
        def stream(model, messages, result):  # type: ignore[no-untyped-def]
            calls.append(pid)
            if fail:
                raise AppError("provider_quota", "limit", 429)
            yield f"hi from {pid}"

        return stream

    for pid, fail in (("groq", True), ("gemini", False), ("openrouter", False)):
        monkeypatch.setattr(pv.PROVIDERS[pid], "configured", lambda: True)
        monkeypatch.setattr(pv.PROVIDERS[pid], "stream", fake(pid, fail))
    res = pv.StreamResult()
    out = "".join(pv.PROVIDERS["auto"].stream("auto", [pv.ChatMessage("user", "x")], res))
    assert out == "hi from gemini" and calls == ["groq", "gemini"]
    assert res.served_by.startswith("gemini/")

    # Long inputs try the largest-context provider first.
    assert pv.PROVIDERS["auto"].candidates(200_000)[0] == "gemini"  # type: ignore[attr-defined]

    # Everything exhausted -> clear error, never a paid provider or the demo model.
    monkeypatch.setattr(pv.PROVIDERS["gemini"], "stream", fake("gemini", True))
    monkeypatch.setattr(pv.PROVIDERS["openrouter"], "stream", fake("openrouter", True))
    with pytest.raises(AppError) as e:
        "".join(
            pv.PROVIDERS["auto"].stream("auto", [pv.ChatMessage("user", "x")], pv.StreamResult())
        )
    assert e.value.code == "no_free_provider"


def test_auto_unavailable_without_keys(db: Session) -> None:
    api = make_user(db)
    auto = next(p for p in api.get("/models").json() if p["id"] == "auto")
    assert auto["available"] is False
