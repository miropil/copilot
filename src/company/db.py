"""vData (verifiable data) DB utilities.
Default: SQLite local file at .company_vdata.db. Use SQLAlchemy with clear adapter for portability.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, ".company_vdata.db")

def get_engine(sqlite_path: str = None):
    path = sqlite_path or DEFAULT_DB_PATH
    url = f"sqlite:///{path}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    return engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None)
Base = declarative_base()


def init_db(engine=None):
    """Create DB tables."""
    eng = engine or get_engine()
    SessionLocal.configure(bind=eng)
    Base.metadata.create_all(bind=eng)
    return eng
