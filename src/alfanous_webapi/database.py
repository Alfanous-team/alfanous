#!/usr/bin/env python3
# coding: utf-8

"""
Database Module for Alfanous Web API
======================================

Sets up the SQLAlchemy engine, session factory, and declarative base used
by the "ask AI" conversation feature.

Two tables are defined:

* ``ai_cache``      – Stores pre-loaded AI model resource data (populated by
  ``scripts/release_tasks.py`` during the Heroku release phase).
* ``conversations`` – Stores user ↔ AI conversation history for the "ask AI"
  feature; the endpoint filters to today's conversations automatically.

The database URL is read from the ``DATABASE_URL`` environment variable (set
automatically by Heroku's Postgres add-on).  When not set, a local SQLite
file is used so that development and testing work without any extra setup.
"""

import json
import logging
import os
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine / session factory
# ---------------------------------------------------------------------------


def _build_db_url() -> str:
    """Construct the database URL from the environment.

    Heroku exposes a ``DATABASE_URL`` that starts with ``postgres://``; newer
    versions of SQLAlchemy require ``postgresql://``.
    """
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if not url:
        url = "sqlite:///alfanous.db"
    return url


DATABASE_URL: str = _build_db_url()

engine = create_engine(
    DATABASE_URL,
    # ``check_same_thread=False`` is required for SQLite when used with
    # FastAPI's threaded / async request handling.
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# ORM base and models
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class AICacheEntry(Base):
    """Persistent cache for AI model resource data.

    Populated by ``scripts/release_tasks.py`` during the Heroku release phase
    so that the web-API dynos can retrieve AI model data from the database
    rather than reading from the file system on every request.
    """

    __tablename__ = "ai_cache"

    key = Column(String(255), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())

    def get_value(self) -> object:
        """Deserialise the stored JSON value."""
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value


class Conversation(Base):
    """Stores a single turn of the "ask AI" conversation.

    Each row represents one user message and the corresponding AI response.
    The ``created_at`` timestamp is used to filter conversations to the
    current day on the ``GET /api/ask-ai/conversations/today`` endpoint.
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    ai_response_html = Column(Text, nullable=True,
                              doc="HTML-formatted version of ai_response with "
                                  "clickable links and styled aya references.")
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), index=True)


# ---------------------------------------------------------------------------
# Table initialisation
# ---------------------------------------------------------------------------


def init_db() -> None:
    """Create all tables that do not yet exist in the database.

    Safe to call repeatedly — SQLAlchemy's ``CREATE TABLE IF NOT EXISTS``
    semantics mean existing tables are never dropped or modified.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialised (url=%s)", DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL)
    except Exception as exc:
        logger.error("Failed to initialise database tables: %s", exc)


# ---------------------------------------------------------------------------
# Session dependency (for FastAPI's Depends())
# ---------------------------------------------------------------------------


def get_db():
    """FastAPI dependency that yields a SQLAlchemy ``Session`` and closes it
    after the request finishes."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def get_cached_resource(db: Session, key: str) -> Optional[object]:
    """Retrieve a cached AI resource from the database.

    Returns the deserialised Python object, or ``None`` if the key is not
    found.
    """
    entry: Optional[AICacheEntry] = db.query(AICacheEntry).filter(
        AICacheEntry.key == key
    ).first()
    if entry is None:
        return None
    return entry.get_value()


# ---------------------------------------------------------------------------
# Conversation helpers
# ---------------------------------------------------------------------------


def get_today_conversations(db: Session, session_id: str) -> list:
    """Return all conversations for *session_id* created today (UTC).

    The comparison is done at the database level so that the query stays
    efficient regardless of how many historical rows exist.
    """
    today = date.today()
    rows = (
        db.query(Conversation)
        .filter(
            Conversation.session_id == session_id,
            func.date(Conversation.created_at) == today,
        )
        .order_by(Conversation.created_at)
        .all()
    )
    return rows


def save_conversation(
    db: Session,
    session_id: str,
    user_message: str,
    ai_response: str,
    ai_response_html: Optional[str] = None,
) -> Conversation:
    """Persist a conversation turn and return the saved ORM object."""
    conv = Conversation(
        session_id=session_id,
        user_message=user_message,
        ai_response=ai_response,
        ai_response_html=ai_response_html,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv
