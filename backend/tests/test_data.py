import io

from openpyxl import Workbook, load_workbook
from sqlalchemy.orm import Session

from app.services.data import chart, clean, dedupe_header
from tests.conftest import Api, make_user

CSV = b"city,month,sales\nLahore,1,100\nKarachi,1,250\nLahore,2,150\n , , \nLahore,2,150\nIslamabad,1,=CMD()\n"


def upload(api: Api, name: str, data: bytes, query: str = ""):  # type: ignore[no-untyped-def]
    return api.c.post(
        f"/api/v1/data/datasets{query}",
        files={"file": (name, data)},
        headers={"x-csrf-token": api.c.cookies.get("aura_csrf") or api.csrf},
    )


def test_import_profile_chart_export(db: Session) -> None:
    api = make_user(db)
    r = upload(api, "sales.csv", CSV, "?dedupe=true")
    assert r.status_code == 201, r.text
    ds = r.json()
    assert (
        ds["columns"] == ["city", "month", "sales"] and ds["row_count"] == 4
    )  # blank + duplicate dropped

    detail = api.get(f"/data/datasets/{ds['id']}").json()
    sales = next(c for c in detail["profile"] if c["name"] == "city")
    assert sales["type"] == "text" and sales["unique"] == 3

    pts = api.get(f"/data/datasets/{ds['id']}/chart?x=city&y=sales&agg=sum").json()["points"]
    assert sorted(pts, key=lambda p: p["x"]) == [
        {"x": "Karachi", "y": 250.0},
        {"x": "Lahore", "y": 250.0},
    ]

    csv_out = api.get(f"/data/datasets/{ds['id']}/export?format=csv").content.decode("utf-8-sig")
    assert "'=CMD()" in csv_out  # formula injection neutralised
    xlsx = api.get(f"/data/datasets/{ds['id']}/export?format=xlsx")
    ws = load_workbook(io.BytesIO(xlsx.content)).active
    assert ws["C2"].value == 100


def test_xlsx_import(db: Session) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(["name", "score"])
    ws.append(["a", 1])
    ws.append(["b", 3])
    buf = io.BytesIO()
    wb.save(buf)
    api = make_user(db)
    r = upload(api, "scores.xlsx", buf.getvalue())
    assert r.status_code == 201
    detail = api.get(f"/data/datasets/{r.json()['id']}").json()
    score = next(c for c in detail["profile"] if c["name"] == "score")
    assert score["type"] == "number" and score["mean"] == 2.0


def test_datasets_private_and_validated(db: Session) -> None:
    alice = make_user(db, "da@example.com")
    bob = make_user(db, "db@example.com")
    did = upload(alice, "s.csv", CSV).json()["id"]
    for path in (
        f"/data/datasets/{did}",
        f"/data/datasets/{did}/chart?x=city",
        f"/data/datasets/{did}/export",
    ):
        assert bob.get(path).status_code == 404
    assert bob.delete(f"/data/datasets/{did}").status_code == 404
    assert alice.get(f"/data/datasets/{did}/chart?x=nope").status_code == 400
    assert upload(alice, "x.txt", b"a,b").status_code == 415
    assert upload(alice, "fake.xlsx", b"not a zip").status_code == 415
    assert upload(alice, "empty.csv", b"").status_code == 422


def test_helpers() -> None:
    assert dedupe_header(["a", "a", "b"]) == ["a", "a_2", "b"]
    assert clean([[" x ", ""], ["", ""], [" x ", ""]], trim=True, drop_empty=True, dedupe=True) == [
        ["x", ""]
    ]
    assert chart(["k"], [["a"], ["b"], ["a"]], "k", None, "count") == [
        {"x": "a", "y": 2.0},
        {"x": "b", "y": 1.0},
    ]
