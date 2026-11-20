import time

from sqlalchemy.orm import Session

from app.services.research import parse_queries, parse_verdict, validate_citations
from tests.conftest import Api, make_user


def wait_done(api: Api, run_id: str, timeout: float = 15) -> dict:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        run = api.get(f"/agent-runs/{run_id}").json()
        if run["status"] not in ("queued", "running"):
            return run
        time.sleep(0.1)
    raise AssertionError("run did not finish")


def test_research_run_records_steps_and_sources(db: Session) -> None:
    api = make_user(db)
    r = api.post(
        "/agent-runs", {"kind": "research", "text": "Benefits of solar energy in Pakistan"}
    )
    assert r.status_code == 201, r.text
    run = wait_done(api, r.json()["id"])
    assert run["status"] == "succeeded", run
    names = [s["name"] for s in run["steps"]]
    assert names[0] == "Plan research" and names[-1] == "Write cited report"
    assert all(s["status"] == "ok" for s in run["steps"])
    res = run["result"]
    assert res["demo"] is True and len(res["sources"]) >= 1
    assert all(1 <= n <= len(res["sources"]) for n in res["cited"])
    assert all("retrieved_at" in s and s["url"].startswith("https://") for s in res["sources"])


def test_fact_check_run(db: Session) -> None:
    api = make_user(db)
    r = api.post("/agent-runs", {"kind": "fact_check", "text": "The Earth orbits the Sun."})
    run = wait_done(api, r.json()["id"])
    assert run["status"] == "succeeded"
    assert run["result"]["verdict"] in {
        "supported",
        "contradicted",
        "mixed",
        "insufficient_evidence",
    }


def test_runs_are_private(db: Session) -> None:
    alice = make_user(db, "a1@example.com")
    bob = make_user(db, "b1@example.com")
    rid = alice.post("/agent-runs", {"kind": "research", "text": "private topic"}).json()["id"]
    wait_done(alice, rid)
    assert bob.get(f"/agent-runs/{rid}").status_code == 404
    assert bob.post(f"/agent-runs/{rid}/cancel").status_code == 404
    assert bob.delete(f"/agent-runs/{rid}").status_code == 404
    assert bob.get("/agent-runs").json() == []
    assert bob.get(f"/agent-runs/{rid}/events").status_code == 404


def test_delete_finished_run(db: Session) -> None:
    api = make_user(db)
    rid = api.post("/agent-runs", {"kind": "research", "text": "delete me"}).json()["id"]
    wait_done(api, rid)
    assert api.delete(f"/agent-runs/{rid}").status_code == 204
    assert api.get(f"/agent-runs/{rid}").status_code == 404


def test_events_stream_ends_with_final_state(db: Session) -> None:
    api = make_user(db)
    rid = api.post("/agent-runs", {"kind": "research", "text": "stream test"}).json()["id"]
    wait_done(api, rid)
    r = api.get(f"/agent-runs/{rid}/events")
    assert r.status_code == 200 and '"status":"succeeded"' in r.text


def test_citation_and_parser_guards() -> None:
    text, used = validate_citations("Fact [1]. Invented [7]. Again [2][1].", 2)
    assert "[7]" not in text and used == [1, 2]
    assert parse_queries('["a", "b", "c", "d"]', "q") == ["a", "b", "c"]
    assert parse_queries("not json", "fallback question") == ["fallback question"]
    v = parse_verdict('{"verdict": "supported", "supporting": [1, 9], "explanation": "ok"}', 3)
    assert v["verdict"] == "supported" and v["supporting"] == [1]
    assert parse_verdict("garbage", 3)["verdict"] == "insufficient_evidence"
    assert parse_verdict('{"verdict": "totally true"}', 3)["verdict"] == "insufficient_evidence"
