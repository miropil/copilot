"""ORM models for Company vData provenance store.
Tables: Team, Agent, Run, Action, Evidence, Review, RealitySnapshot
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from .db import Base
import datetime

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    metadata_json = Column(JSON, nullable=True)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", backref="agents")

class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    run_id = Column(String, unique=True, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    task = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Action(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True)
    action_id = Column(String, unique=True, nullable=False)
    run_id = Column(Integer, ForeignKey("runs.id"))
    step = Column(Integer, nullable=False)
    actor = Column(String, nullable=False)
    actor_role = Column(String, nullable=True)
    action = Column(String, nullable=True)
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    evidence_refs = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey("actions.id"))
    reviewer = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey("actions.id"))
    uri = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    ts = Column(DateTime, default=datetime.datetime.utcnow)

class RealitySnapshot(Base):
    __tablename__ = "reality_snapshots"
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    source = Column(String, nullable=True)
    ts = Column(DateTime, default=datetime.datetime.utcnow)
