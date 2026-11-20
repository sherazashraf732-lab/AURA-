"""Integrations hub (M14) and Knowledge Graph (M15).

Integrations: an allowlisted catalog of read-only tools with declared scopes. Users enable each tool
explicitly; every invocation is audit-logged and its output is treated as untrusted data.
Connecting arbitrary external MCP servers is intentionally not offered in the beta (S7).

Knowledge Graph: entities and "mentioned with" links extracted from the user's own documents with a
deterministic heuristic (no model call). Links mean co-occurrence in a sentence, never a verified
fact, and every edge keeps provenance (document + part). Users can delete wrong entities.
"""

import re
from collections import Counter
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, String, delete, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.api.deps import CurrentUser, DbSession, VerifiedUser
from app.core.errors import AppError
from app.database.session import Base, IdMixin, utcnow
from app.models.knowledge import DocumentChunk, KnowledgeSource
from app.modules.web import fetch_text
from app.services import knowledge as kb
from app.services.auth import audit

router = APIRouter(tags=["integrations"])

CATALOG = {
    "knowledge_search": {
        "name": "Knowledge Base search",
        "scopes": ["read:documents"],
        "description": "Search passages in your uploaded documents.",
    },
    "web_fetch": {
        "name": "Web page reader",
        "scopes": ["read:public-web"],
        "description": "Read the text of a public web page (private addresses blocked).",
    },
}


class ToolGrant(IdMixin, Base):
    __tablename__ = "tool_grants"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    tool: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class GraphEntity(IdMixin, Base):
    __tablename__ = "graph_entities"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    mentions: Mapped[int] = mapped_column(default=0)


class GraphEdge(IdMixin, Base):
    __tablename__ = "graph_edges"

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    a_id: Mapped[UUID] = mapped_column(ForeignKey("graph_entities.id", ondelete="CASCADE"))
    b_id: Mapped[UUID] = mapped_column(ForeignKey("graph_entities.id", ondelete="CASCADE"))
    weight: Mapped[int] = mapped_column(default=1)
    provenance: Mapped[list[dict[str, object]]] = mapped_column(JSONB, default=list)


# ---------------- integrations ----------------


@router.get("/integrations")
def catalog(user: CurrentUser, db: DbSession) -> list[dict[str, object]]:
    granted = set(db.scalars(select(ToolGrant.tool).where(ToolGrant.owner_id == user.id)))
    return [{"id": k, **v, "enabled": k in granted} for k, v in CATALOG.items()]


class GrantIn(BaseModel):
    enabled: bool


@router.put("/integrations/{tool}")
def set_grant(tool: str, body: GrantIn, user: VerifiedUser, db: DbSession) -> dict[str, object]:
    if tool not in CATALOG:
        raise AppError("unknown_tool", "Unknown integration.", 404)
    db.execute(delete(ToolGrant).where(ToolGrant.owner_id == user.id, ToolGrant.tool == tool))
    if body.enabled:
        db.add(ToolGrant(owner_id=user.id, tool=tool))
    audit(db, "tool.grant" if body.enabled else "tool.revoke", user, target=tool)
    return {"id": tool, "enabled": body.enabled}


class InvokeIn(BaseModel):
    query: str = Field(min_length=2, max_length=2000)


@router.post("/integrations/{tool}/invoke")
def invoke(tool: str, body: InvokeIn, user: VerifiedUser, db: DbSession) -> dict[str, object]:
    if tool not in CATALOG:
        raise AppError("unknown_tool", "Unknown integration.", 404)
    if (
        db.scalar(select(ToolGrant).where(ToolGrant.owner_id == user.id, ToolGrant.tool == tool))
        is None
    ):
        raise AppError("tool_not_enabled", "Enable this integration first.", 403)
    audit(db, "tool.invoke", user, target=tool, detail=body.query[:200])
    if tool == "knowledge_search":
        hits = kb.search(db, user, body.query)
        return {
            "untrusted": True,
            "results": [
                {"filename": h.filename, "part": h.seq + 1, "excerpt": h.text[:400]} for h in hits
            ],
        }
    url, text = fetch_text(body.query)
    return {"untrusted": True, "url": url, "text": text[:5000]}


# ---------------- knowledge graph ----------------

_ENTITY = re.compile(r"\b(?:[A-Z][a-zA-Z0-9&.'-]+(?:\s+(?:of|the|de|al)\s+|\s+)?){1,4}")
_STOP = {
    "The",
    "A",
    "An",
    "This",
    "That",
    "These",
    "It",
    "In",
    "On",
    "At",
    "For",
    "And",
    "But",
    "If",
    "We",
    "I",
    "You",
    "He",
    "She",
    "They",
    "Our",
    "My",
}


def entities(sentence: str) -> list[str]:
    found = []
    for m in _ENTITY.finditer(sentence):
        name = re.sub(r"\s+(?:of|the|de|al)$", "", m.group(0).strip()).strip(" .,'")
        if name and name not in _STOP and len(name) >= 3:
            found.append(name[:120])
    return list(dict.fromkeys(found))


@router.post("/graph/build")
def build_graph(user: VerifiedUser, db: DbSession) -> dict[str, int]:
    """Rebuild the user's graph from their documents (replaces previous extraction)."""
    db.execute(delete(GraphEntity).where(GraphEntity.owner_id == user.id))
    rows = db.execute(
        select(DocumentChunk.text, DocumentChunk.seq, KnowledgeSource.filename)
        .join(KnowledgeSource, KnowledgeSource.id == DocumentChunk.source_id)
        .where(DocumentChunk.owner_id == user.id)
        .limit(5000)
    ).all()
    counts: Counter[str] = Counter()
    pairs: dict[tuple[str, str], list[dict[str, object]]] = {}
    for text, seq, fname in rows:
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
            ents = entities(sentence)
            counts.update(ents)
            for i, a in enumerate(ents):
                for b in ents[i + 1 :]:
                    key = (min(a, b), max(a, b))
                    prov = pairs.setdefault(key, [])
                    if len(prov) < 5:
                        prov.append(
                            {"document": fname, "part": seq + 1, "sentence": sentence[:300]}
                        )
    keep = {n for n, c in counts.most_common(300)}
    ids: dict[str, GraphEntity] = {}
    for name in keep:
        ids[name] = GraphEntity(owner_id=user.id, name=name, mentions=counts[name])
        db.add(ids[name])
    db.flush()
    n_edges = 0
    for (a, b), prov in pairs.items():
        if a in ids and b in ids:
            db.add(
                GraphEdge(
                    owner_id=user.id,
                    a_id=ids[a].id,
                    b_id=ids[b].id,
                    weight=len(prov),
                    provenance=prov,
                )
            )
            n_edges += 1
    return {"entities": len(ids), "links": n_edges}


@router.get("/graph")
def graph(user: CurrentUser, db: DbSession) -> dict[str, object]:
    ents = db.scalars(
        select(GraphEntity)
        .where(GraphEntity.owner_id == user.id)
        .order_by(GraphEntity.mentions.desc())
    ).all()
    edges = db.scalars(
        select(GraphEdge)
        .where(GraphEdge.owner_id == user.id)
        .order_by(GraphEdge.weight.desc())
        .limit(500)
    ).all()
    return {
        "note": "Links mean the names appear in the same sentence; they are not verified facts.",
        "entities": [{"id": str(e.id), "name": e.name, "mentions": e.mentions} for e in ents],
        "links": [
            {"a": str(e.a_id), "b": str(e.b_id), "weight": e.weight, "provenance": e.provenance}
            for e in edges
        ],
    }


@router.delete("/graph/entities/{entity_id}", status_code=204)
def delete_entity(entity_id: UUID, user: CurrentUser, db: DbSession) -> None:
    e = db.scalar(
        select(GraphEntity).where(GraphEntity.id == entity_id, GraphEntity.owner_id == user.id)
    )
    if e is None:
        raise AppError("not_found", "Entity not found.", 404)
    db.delete(e)
