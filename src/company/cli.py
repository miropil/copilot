"""Minimal CLI for Company prototype.
Run with: python -m company.cli
"""
import click
import uuid
import yaml
import os
from .db import get_engine, init_db, SessionLocal
from .models import Team, Agent, Run
from .provenance import append_jsonl, init_and_get_session, record_action, record_review

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEAM_TEMPLATE = os.path.join(BASE_DIR, "examples", "team.yaml")


@click.group()
def cli():
    pass


@cli.command()
@click.option("--team", default="my-team", help="Team name to initialize")
def init(team):
    """Scaffold a paired team template (team.yaml)"""
    os.makedirs(os.path.dirname(TEAM_TEMPLATE), exist_ok=True)
    sample = {
        "name": team,
        "teams": [
            {
                "id": f"{team}-1",
                "agents": [
                    {"name": "alice", "role": "primary", "capabilities": ["planner","researcher","executor"]},
                    {"name": "bob", "role": "peer", "capabilities": ["researcher","verifier","executor"]},
                ],
                "specialists": [{"name": "retriever-vec", "type": "retriever", "promotable_to_mcp": True}],
                "policies": {"auto_approve_risk": "low", "peer_required_risk": "medium", "ensemble_required_risk": "high"},
            }
        ]
    }
    with open(TEAM_TEMPLATE, "w", encoding="utf-8") as f:
        yaml.safe_dump(sample, f)
    click.echo(f"Wrote example team template to {TEAM_TEMPLATE}")


@cli.command()
@click.option("--team-file", default=TEAM_TEMPLATE, help="Path to team.yaml")
@click.option("--task", default="demo task", help="Task description")
def run(team_file, task):
    """Start a simple demo run: create run, one action by proposer and a peer review. Records provenance."""
    if not os.path.exists(team_file):
        click.echo("Team file not found. Run `copilot company init` to create an example.")
        return
    with open(team_file, "r", encoding="utf-8") as f:
        team_cfg = yaml.safe_load(f)
    team_entry = team_cfg["teams"][0]
    team_name = team_cfg["name"]
    # init db and session
    session = init_and_get_session()
    # create or get team
    t = session.query(Team).filter_by(name=team_name).first()
    if not t:
        t = Team(name=team_name, metadata_json={})
        session.add(t)
        session.commit()
    run_id = str(uuid.uuid4())
    r = Run(run_id=run_id, team_id=t.id, task=task)
    session.add(r)
    session.commit()

    # create a demo action by proposer (alice)
    action_record = {
        "ts": None,
        "run_id": run_id,
        "team": team_name,
        "step": 1,
        "action_id": f"a-{uuid.uuid4().hex[:8]}",
        "actor": "alice",
        "actor_role": "proposer",
        "action": "summarize_repo",
        "input": task,
        "output": "Demo summary: repo has N files...",
        "evidence_refs": ["file://README.md"],
        "confidence": 0.9,
        "review": {"reviewer": "bob", "decision": "accept", "notes": "Looks reasonable"},
    }
    append_jsonl(action_record)
    action_obj = record_action(session, r, action_record)
    session.commit()
    record_review(session, action_obj, action_record.get("review", {}))
    session.commit()
    click.echo(f"Run {run_id} created. Action {action_record['action_id']} recorded with reviewer bob.")


@cli.command()
@click.option("--db-path", default=None, help="Optional path to SQLite DB file")
def initdb(db_path):
    eng = get_engine(db_path)
    init_db(eng)
    click.echo(f"Initialized vData DB at {db_path or '(default .company_vdata.db)'}")


@cli.command()
@click.option("--run-id", default=None, help="Show status of a run")
def status(run_id):
    session = init_and_get_session()
    q = session.query(Run)
    if run_id:
        q = q.filter_by(run_id=run_id)
    runs = q.all()
    for rr in runs:
        click.echo(f"Run {rr.run_id} team_id={rr.team_id} task={rr.task} created={rr.created_at}")


if __name__ == "__main__":
    cli()
