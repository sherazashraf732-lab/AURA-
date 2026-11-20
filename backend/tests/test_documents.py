import io

import docx
import pytest
from openpyxl import load_workbook
from pptx import Presentation
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.services.documents import _cell, parse_draft
from tests.conftest import make_user

CONTENT = {
    "title": "AURA Beta Plan",
    "sections": [
        {
            "heading": "Goals",
            "paragraphs": ["Launch to 50 testers."],
            "bullets": ["Free tier", "Urdu: خوش آمدید"],
        },
        {
            "heading": "Budget",
            "table": {"columns": ["Item", "Cost"], "rows": [["Hosting", "0"], ["Email", "=1+1"]]},
        },
    ],
}


@pytest.mark.parametrize("fmt", ["docx", "pptx", "xlsx", "pdf"])
def test_render_each_format_round_trips(db: Session, fmt: str) -> None:
    api = make_user(db)
    r = api.post("/documents/render", {"format": fmt, "content": CONTENT})
    assert r.status_code == 200, r.text
    assert f'filename="AURA Beta Plan.{fmt}"' in r.headers["content-disposition"]
    f = io.BytesIO(r.content)
    if fmt == "docx":
        text = "\n".join(p.text for p in docx.Document(f).paragraphs)
        assert "Launch to 50 testers." in text and "خوش آمدید" in text
    elif fmt == "pptx":
        assert len(Presentation(f).slides) == 4  # title + 2 sections + 1 table slide
    elif fmt == "xlsx":
        wb = load_workbook(f)
        assert wb.sheetnames == ["Summary", "Budget"]
        assert wb["Budget"]["B2"].value == 0 and wb["Budget"]["B3"].value == "'=1+1"
    else:
        assert "AURA Beta Plan" in PdfReader(f).pages[0].extract_text()


def test_render_validates_input(db: Session) -> None:
    api = make_user(db)
    assert api.post("/documents/render", {"format": "exe", "content": CONTENT}).status_code == 422
    assert (
        api.post("/documents/render", {"format": "docx", "content": {"title": ""}}).status_code
        == 422
    )


def test_draft_returns_editable_content(db: Session) -> None:
    api = make_user(db)
    r = api.post("/documents/draft", {"prompt": "A one-page project brief for AURA"})
    assert r.status_code == 200
    assert r.json()["title"]
    assert api.post("/documents/render", {"format": "docx", "content": r.json()}).status_code == 200


def test_spreadsheet_formula_injection_neutralised() -> None:
    assert _cell('=HYPERLINK("x")') == '\'=HYPERLINK("x")'
    assert _cell("-5") == -5.0 and _cell("abc") == "abc"


def test_parse_draft_falls_back_to_text() -> None:
    d = parse_draft("not json at all", "My title")
    assert d.title == "My title" and d.sections[0].paragraphs == ["not json at all"]
