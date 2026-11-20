from sqlalchemy.orm import Session

from app.api.v1.workflows import fill
from tests.conftest import make_user

STEPS = [
    {"type": "template", "name": "Frame", "template": "Topic: {{input}}"},
    {"type": "llm", "name": "Draft", "prompt": "Write a tagline for {{previous}}"},
    {"type": "approval", "name": "Check draft"},
    {"type": "llm", "name": "Polish", "prompt": "Polish: {{previous}}"},
]


def test_workflow_runs_until_approval_then_resumes(db: Session) -> None:
    api = make_user(db)
    wf = api.post("/workflows", {"name": "Tagline", "steps": STEPS}).json()
    run = api.post(f"/workflows/{wf['id']}/runs", {"input": "solar"}).json()
    assert run["status"] == "waiting_for_approval" and run["step_index"] == 2
    assert run["log"][0]["output"] == "Topic: solar"
    assert "Demo reply" in run["log"][1]["output"]

    done = api.post(f"/workflows/runs/{run['id']}/decision", {"approve": True}).json()
    assert done["status"] == "succeeded" and done["log"][-1]["name"] == "Polish"
    assert api.post(f"/workflows/runs/{run['id']}/decision", {"approve": True}).status_code == 409


def test_rejection_stops_run(db: Session) -> None:
    api = make_user(db)
    wf = api.post("/workflows", {"name": "W", "steps": STEPS}).json()
    run = api.post(f"/workflows/{wf['id']}/runs", {"input": "x"}).json()
    r = api.post(f"/workflows/runs/{run['id']}/decision", {"approve": False}).json()
    assert r["status"] == "rejected"


def test_versioning_and_validation(db: Session) -> None:
    api = make_user(db)
    assert (
        api.post(
            "/workflows", {"name": "bad", "steps": [{"type": "shell", "name": "rm"}]}
        ).status_code
        == 422
    )
    assert api.post("/workflows", {"name": "empty", "steps": []}).status_code == 422
    wf = api.post("/workflows", {"name": "V", "steps": STEPS[:1]}).json()
    run = api.post(f"/workflows/{wf['id']}/runs", {"input": "a"}).json()
    upd = api.put(f"/workflows/{wf['id']}", {"name": "V2", "steps": STEPS[:2]}).json()
    assert upd["version"] == 2 and run["workflow_version"] == 1 and run["status"] == "succeeded"


def test_workflows_are_private(db: Session) -> None:
    alice = make_user(db, "wa@example.com")
    bob = make_user(db, "wb@example.com")
    wf = alice.post("/workflows", {"name": "A", "steps": STEPS}).json()
    run = alice.post(f"/workflows/{wf['id']}/runs", {"input": "x"}).json()
    assert bob.get("/workflows").json() == []
    assert bob.post(f"/workflows/{wf['id']}/runs", {"input": "x"}).status_code == 404
    assert bob.post(f"/workflows/runs/{run['id']}/decision", {"approve": True}).status_code == 404
    assert bob.delete(f"/workflows/{wf['id']}").status_code == 404


def test_coding_lab_never_executes(db: Session) -> None:
    api = make_user(db)
    r = api.post(
        "/coding/assist",
        {"task": "review", "code": "import os\nos.system('rm -rf /')", "language": "python"},
    )
    assert r.status_code == 200 and r.json()["executed"] is False
    assert api.post("/coding/assist", {"task": "run", "code": "x"}).status_code == 422


def test_fill() -> None:
    assert fill("{{ input }} / {{previous}}", "a", "b") == "a / b"
