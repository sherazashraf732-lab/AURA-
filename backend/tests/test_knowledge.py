import io
import zipfile

import docx
from sqlalchemy.orm import Session

from app.services.knowledge import chunk
from tests.conftest import Api, make_user


def upload(api: Api, name: str, data: bytes):  # type: ignore[no-untyped-def]
    return api.c.post(
        "/api/v1/knowledge/sources",
        files={"file": (name, data)},
        headers={"x-csrf-token": api.c.cookies.get("aura_csrf") or api.csrf},
    )


def docx_bytes(text: str) -> bytes:
    d = docx.Document()
    d.add_paragraph(text)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def test_upload_search_and_cited_answer(db: Session) -> None:
    api = make_user(db)
    r = upload(
        api, "notes.txt", b"The AURA beta launches in Lahore with fifty testers.\n\nBudget is zero."
    )
    assert r.status_code == 201, r.text
    assert r.json()["chunk_count"] >= 1
    assert (
        upload(
            api, "plan.docx", docx_bytes("Roman Urdu support: mujhe yeh feature chahiye")
        ).status_code
        == 201
    )

    hits = api.get("/knowledge/search?q=Lahore testers").json()
    assert hits and hits[0]["filename"] == "notes.txt"
    assert api.get("/knowledge/search?q=chahiye").json()[0]["filename"] == "plan.docx"

    ans = api.post("/knowledge/ask", {"question": "Where does the beta launch?"}).json()
    assert ans["citations"] and ans["citations"][0]["filename"] == "notes.txt"
    assert ans["demo"] is True


def test_no_match_is_honest(db: Session) -> None:
    api = make_user(db)
    upload(api, "a.txt", b"apples and oranges")
    ans = api.post("/knowledge/ask", {"question": "quantum chromodynamics"}).json()
    assert ans["citations"] == [] and "No matching" in ans["answer"]


def test_documents_are_private(db: Session) -> None:
    alice = make_user(db, "ka@example.com")
    bob = make_user(db, "kb@example.com")
    sid = upload(alice, "secret.txt", b"alice private salary figures").json()["id"]
    assert bob.get("/knowledge/search?q=salary").json() == []
    assert bob.get("/knowledge/sources").json() == []
    assert bob.post("/knowledge/ask", {"question": "salary"}).json()["citations"] == []
    assert bob.delete(f"/knowledge/sources/{sid}").status_code == 404
    assert alice.delete(f"/knowledge/sources/{sid}").status_code == 204
    assert alice.get("/knowledge/search?q=salary").json() == []


def test_file_validation(db: Session) -> None:
    api = make_user(db)
    assert upload(api, "x.exe", b"MZ....").status_code == 415
    assert upload(api, "fake.pdf", b"not a pdf").json()["error"]["code"] == "invalid_file"
    assert upload(api, "fake.docx", b"hello").json()["error"]["code"] == "invalid_file"
    assert upload(api, "bin.txt", b"\x00\x01\x02binary").status_code == 415
    assert upload(api, "empty.txt", b"").status_code == 400
    # A zip that is a "docx" but has no document part.
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("other.xml", "<x/>")
    assert upload(api, "odd.docx", buf.getvalue()).status_code == 415
    # Corrupt PDF body must be a clean 422, not a crash.
    assert upload(api, "broken.pdf", b"%PDF-1.7 garbage garbage").status_code == 422


def test_unverified_cannot_upload(api: Api) -> None:
    api.post("/auth/signup", {"email": "kv@example.com", "password": "correct-horse-1"})
    api.post("/auth/login", {"email": "kv@example.com", "password": "correct-horse-1"})
    assert upload(api, "a.txt", b"hello world").status_code == 403


def test_chunking_overlaps_and_bounds() -> None:
    text = ("Sentence number one. " * 300).strip()
    parts = chunk(text)
    assert len(parts) > 1 and all(len(p) <= 1200 for p in parts)
    assert chunk("") == []
