"""Provenance writer: append JSONL and insert into vData DB tables."""
import json
import os
from .db import get_engine, SessionLocal, init_db
from .models import Run, Action, Evidence, Review
from sqlalchemy.orm import Session

DEFAULT_JSONL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "company_provenance.jsonl"))


def append_jsonl(record: dict, path: str = None):
    p = path or DEFAULT_JSONL
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def record_action(session: Session, run_obj: Run, record: dict):
    """Insert action and evidence into DB using an existing session."""
    a = Action(
        action_id=record.get("action_id"),
        run_id=run_obj.id,
        step=record.get("step", 0),
        actor=record.get("actor"),
        actor_role=record.get("actor_role"),
        action=record.get("action"),
        input=record.get("input"),
        output=record.get("output"),
        evidence_refs=record.get("evidence_refs"),
        confidence=record.get("confidence"),
    )
    session.add(a)
    session.flush()
    for uri in record.get("evidence_refs", []) or []:
        e = Evidence(action_id=a.id, uri=uri)
        session.add(e)
    # review field handled separately by record_review
    return a


def record_review(session: Session, action_obj: Action, review: dict):
    r = Review(action_id=action_obj.id, reviewer=review.get("reviewer"), decision=review.get("decision"), notes=review.get("notes"))
    session.add(r)
    return r


def init_and_get_session(sqlite_path: str = None):
    eng = get_engine(sqlite_path)
    init_db(engine=eng)
    SessionLocal.configure(bind=eng)
    return SessionLocal()
