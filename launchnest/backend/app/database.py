"""
LaunchNest — Database Setup
============================
SQLAlchemy engine + session factory using SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

# ─── Engine ───
# check_same_thread=False is required for SQLite + FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# ─── Session ───
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ─── Base ───
Base = declarative_base()


# ─── Dependency ───
def get_db():
    """
    FastAPI dependency — yields a database session.
    Automatically closes it when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()