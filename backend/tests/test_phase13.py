import io
import json
from datetime import timedelta

import pytest
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.integrations import entities
from app.api.v1.workflows import run_due
from app.database.session import utcnow
from app.models.identity import User
from app.models.workflows import WorkflowRun, WorkflowSchedule
from tests.conftest import Api, make_user


def post_file(api: Api, path: str, name: str, data: bytes, form: dict | None = None):  # type: ignore[no-untyped-def]
    return api.c.post(
        f"/api/v1{path}",
        files={"file": (name, data)},
        data=form or {},
        headers={"x-csrf-token": api.c.cookies.get("aura_csrf") or api.csrf},
    )


def png(w: int = 40, h: int = 20, exif: bool = False) -> bytes:
    img = Image.new("RGB", (w, h), "white")
    buf = io.BytesIO()
    if exif:
        e = Image.Exif()
        e[0x010F] = "SecretCam"  # camera make
        img.save(buf, "JPEG", exif=e)
    else:
        img.save(buf, "PNG")
    return buf.getvalue()


# ---------- Security Center ----------


def test_sessions_and_revoke_others(db: Session) -> None:
    a = make_user(db, "s1@example.com")
    b = Api()
    b.post("/auth/login", {"email": "s1@example.com", "password": "correct-horse-1"})
    sessions = a.get("/security/sessions").json()
    assert len(sessions) == 2 and sum(s["current"] for s in sessions) == 1
    assert a.post("/security/sessions/revoke-others").status_code == 204
    assert b.get("/auth/me").json() is None and a.get("/auth/me").json() is not None


def test_export_contains_only_own_data(db: Session) -> None:
    a = make_user(db, "e1@example.com")
    other = make_user(db, "e2@example.com")
    other.post("/memory", {"content": "other secret"})
    a.post("/memory", {"content": "my memory"})
    data = json.loads(a.get("/security/export").content)
    assert data["account"]["email"] == "e1@example.com"
    assert [m["content"] for m in data["memories"]] == ["my memory"]
    assert "other secret" not in json.dumps(data)


def test_delete_account_removes_everything(db: Session) -> None:
    a = make_user(db, "d1@example.com")
    a.post("/memory", {"content": "x"})
    assert (
        a.post(
            "/security/delete-account", {"password": "wrong-pass-123", "confirm": "DELETE"}
        ).status_code
        == 401
    )
    assert (
        a.post(
            "/security/delete-account", {"password": "correct-horse-1", "confirm": "nope"}
        ).status_code
        == 422
    )
    assert (
        a.post(
            "/security/delete-account", {"password": "correct-horse-1", "confirm": "DELETE"}
        ).status_code
        == 204
    )
    db.expire_all()
    assert db.scalar(select(User).where(User.email == "d1@example.com")) is None
    assert a.get("/auth/me").json() is None


# ---------- Arena & Evaluation ----------


def test_arena_side_by_side(db: Session) -> None:
    api = make_user(db)
    c = {"provider": "mock", "model": "aura-mock-1"}
    r = api.post("/arena", {"prompt": "hello", "contenders": [c, c]}).json()
    assert len(r["results"]) == 2 and all(
        "latency_ms" in x and x["error"] is None for x in r["results"]
    )
    assert api.post("/arena", {"prompt": "x", "contenders": [c]}).status_code == 422
    groq = {"provider": "groq", "model": "openai/gpt-oss-120b"}
    assert (
        api.post("/arena", {"prompt": "x", "contenders": [c, groq]}).json()["error"]["code"]
        == "consent_required"
    )


def test_evaluation_scores_cases(db: Session) -> None:
    api = make_user(db)
    ds = api.post(
        "/evaluations/datasets",
        {
            "name": "Echo",
            "cases": [
                {"input": "say banana", "expected": "banana"},
                {"input": "say apple", "expected": "mango"},
            ],
        },
    ).json()
    run = api.post(f"/evaluations/datasets/{ds['id']}/runs", {}).json()
    assert run["passed"] == 1 and run["total"] == 2
    assert [r["passed"] for r in run["results"]] == [True, False]
    assert len(api.get(f"/evaluations/datasets/{ds['id']}/runs").json()) == 1
    other = make_user(db, "ev2@example.com")
    assert other.post(f"/evaluations/datasets/{ds['id']}/runs", {}).status_code == 404


# ---------- Automation ----------


def test_schedule_runs_when_due(db: Session) -> None:
    api = make_user(db)
    wf = api.post(
        "/workflows",
        {"name": "W", "steps": [{"type": "template", "name": "T", "template": "hi {{input}}"}]},
    ).json()
    assert (
        api.post(f"/workflows/{wf['id']}/schedules", {"interval_minutes": 5}).status_code == 422
    )  # too frequent
    s = api.post(
        f"/workflows/{wf['id']}/schedules", {"interval_minutes": 60, "input": "there"}
    ).json()
    assert run_due(db) == 0  # not due yet
    db.get(WorkflowSchedule, s["id"]).next_run_at = utcnow() - timedelta(minutes=1)  # type: ignore[union-attr]
    db.commit()
    assert run_due(db) == 1
    run = db.scalars(select(WorkflowRun)).one()
    assert run.status == "succeeded" and run.log[0]["output"] == "hi there"
    api.patch(f"/workflows/schedules/{s['id']}", {"approve": False})
    db.expire_all()
    db.get(WorkflowSchedule, s["id"]).next_run_at = utcnow() - timedelta(minutes=1)  # type: ignore[union-attr]
    db.commit()
    assert run_due(db) == 0  # disabled


# ---------- Media ----------


def test_ocr_vision_audio_demo_and_validation(db: Session) -> None:
    api = make_user(db)
    r = post_file(api, "/media/ocr", "a.png", png())
    assert r.status_code == 200 and r.json()["demo"] is True and r.json()["image"]["width"] == 40
    assert post_file(api, "/media/ocr", "a.png", b"not an image").status_code == 415
    assert (
        post_file(api, "/media/ocr", "a.png", png(), {"engine": "gemini"}).json()["error"]["code"]
        == "consent_required"
    )
    assert post_file(api, "/media/ocr", "a.png", png(), {"lang": "eng; rm -rf"}).status_code == 422
    v = post_file(api, "/media/vision", "a.jpg", png(exif=True)).json()
    assert v["image"]["had_exif"] is True and v["demo"] is True
    t = post_file(api, "/media/transcribe", "a.wav", b"RIFF\x00\x00\x00\x00WAVEfmt ")
    assert t.status_code == 200 and t.json()["format"] == "wav"
    assert post_file(api, "/media/transcribe", "a.mp3", b"hello").status_code == 415


def test_reencoded_image_has_no_exif() -> None:
    from app.api.v1.media import clean_image

    out, info = clean_image(png(exif=True))
    assert info["had_exif"] is True
    assert not Image.open(io.BytesIO(out)).getexif()


def test_decompression_bomb_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.api.v1 import media
    from app.core.errors import AppError

    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 100)
    with pytest.raises(AppError):
        media.clean_image(png(400, 400))


# ---------- Integrations & Knowledge Graph ----------


def test_tools_require_grant_and_are_audited(db: Session) -> None:
    api = make_user(db)
    assert {t["id"] for t in api.get("/integrations").json()} == {"knowledge_search", "web_fetch"}
    assert api.post("/integrations/knowledge_search/invoke", {"query": "xx"}).status_code == 403
    assert api.put("/integrations/knowledge_search", {"enabled": True}).status_code == 200
    r = api.post("/integrations/knowledge_search/invoke", {"query": "anything"})
    assert r.status_code == 200 and r.json()["untrusted"] is True
    api.put("/integrations/web_fetch", {"enabled": True})
    assert (
        api.post("/integrations/web_fetch/invoke", {"query": "http://127.0.0.1/"}).status_code
        == 400
    )
    assert api.post("/integrations/shell/invoke", {"query": "ls"}).status_code == 404
    actions = [e["action"] for e in api.get("/security/audit").json()]
    assert "tool.invoke" in actions and "tool.grant" in actions


def test_knowledge_graph_from_documents(db: Session) -> None:
    from tests.test_knowledge import upload

    api = make_user(db)
    upload(
        api,
        "n.txt",
        b"Imran Khan met Ali Raza in Lahore. Ali Raza works at Aura Labs.\nThe weather was fine.",
    )
    built = api.post("/graph/build").json()
    assert built["entities"] >= 3 and built["links"] >= 2
    g = api.get("/graph").json()
    names = {e["name"] for e in g["entities"]}
    assert {"Imran Khan", "Ali Raza", "Lahore", "Aura Labs"} <= names and "The" not in names
    assert all(link["provenance"][0]["document"] == "n.txt" for link in g["links"])
    eid = next(e["id"] for e in g["entities"] if e["name"] == "Lahore")
    assert api.delete(f"/graph/entities/{eid}").status_code == 204
    assert make_user(db, "g2@example.com").get("/graph").json()["entities"] == []


def test_entity_heuristic() -> None:
    assert entities("Bank of England and Ali met.") == ["Bank of England", "Ali"]
