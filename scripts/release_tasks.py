#!/usr/bin/env python3
# coding: utf-8

"""
Heroku Release Tasks Script
============================

This script is intended to run during the Heroku release phase (before dynos start).
It warms up the AI model cache by pre-loading resource data used by the AI mode
and the "ask AI" feature, then stores them in the database so the application
can retrieve them quickly at runtime without reading from the file system on
every request.

Usage (Heroku Procfile):
    release: python scripts/release_tasks.py

Usage (standalone):
    python scripts/release_tasks.py
"""

import json
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# SQLAlchemy is an optional dependency for this script: the release task
# degrades gracefully if it is not installed rather than aborting the release.
try:
    import sqlalchemy as sa  # type: ignore[import-untyped]
    _SQLALCHEMY_AVAILABLE = True
except ImportError:
    sa = None  # type: ignore[assignment]
    _SQLALCHEMY_AVAILABLE = False


def _get_db_url() -> str:
    """Return the database URL from the environment.

    Heroku sets DATABASE_URL automatically when a Postgres add-on is
    attached.  Fall back to a local SQLite file when running outside Heroku.
    """
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url.startswith("postgres://"):
        # SQLAlchemy ≥ 1.4 requires the dialect to be 'postgresql://'
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    if not db_url:
        db_url = "sqlite:///alfanous_cache.db"
        logger.info("DATABASE_URL not set, using local SQLite: alfanous_cache.db")
    return db_url


def _load_ai_resources() -> dict:
    """Load all AI model resources from the Alfanous library.

    Returns a dict mapping resource key → serialisable value.
    """
    resources: dict = {}

    # -- AI query translation rules -----------------------------------------
    try:
        # Ensure the src directory is importable when running from repo root
        _src = os.path.join(os.path.dirname(__file__), "..", "src")
        if _src not in sys.path:
            sys.path.insert(0, _src)

        from alfanous.data import (
            ai_query_translation_rules,
            information,
            recitations,
            translations,
        )

        rules = ai_query_translation_rules()
        resources["ai_query_translation_rules"] = rules
        logger.info(
            "Loaded ai_query_translation_rules: %d chars, %d lines",
            rules.get("length", 0),
            rules.get("lines", 0),
        )

        info = information()
        resources["information"] = info
        logger.info("Loaded information: %d keys", len(info))

        recs = recitations()
        resources["recitations"] = recs
        logger.info("Loaded recitations: %d entries", len(recs))

        trans = translations()
        resources["translations"] = trans
        logger.info("Loaded translations: %d entries", len(trans))

    except Exception as exc:
        logger.error("Failed to load AI resources: %s", exc)

    return resources


def _store_in_db(resources: dict, db_url: str) -> None:
    """Upsert *resources* into the ``ai_cache`` table.

    Creates the table if it does not already exist.  Each resource is stored
    as a JSON-serialised text value keyed by its resource name.
    """
    if not _SQLALCHEMY_AVAILABLE:
        logger.warning(
            "SQLAlchemy is not installed.  Skipping database cache population. "
            "Install it with: pip install sqlalchemy"
        )
        return

    try:
        engine = sa.create_engine(db_url)
        with engine.begin() as conn:
            # Create table on first run (idempotent)
            conn.execute(
                sa.text(
                    """
                    CREATE TABLE IF NOT EXISTS ai_cache (
                        key        VARCHAR(255) PRIMARY KEY,
                        value      TEXT         NOT NULL,
                        updated_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            )

            for key, value in resources.items():
                serialised = json.dumps(value, ensure_ascii=False)

                # Portable upsert: attempt INSERT first, then UPDATE on conflict.
                # SQLite and PostgreSQL both support this syntax (SQLite ≥ 3.24).
                try:
                    conn.execute(
                        sa.text(
                            """
                            INSERT INTO ai_cache (key, value, updated_at)
                            VALUES (:key, :value, CURRENT_TIMESTAMP)
                            ON CONFLICT (key) DO UPDATE
                                SET value      = EXCLUDED.value,
                                    updated_at = CURRENT_TIMESTAMP
                            """
                        ),
                        {"key": key, "value": serialised},
                    )
                except Exception:
                    # Older SQLite versions (<3.24) do not support ON CONFLICT DO UPDATE.
                    # Fall back to a DELETE + INSERT approach.
                    conn.execute(
                        sa.text("DELETE FROM ai_cache WHERE key = :key"),
                        {"key": key},
                    )
                    conn.execute(
                        sa.text(
                            "INSERT INTO ai_cache (key, value) VALUES (:key, :value)"
                        ),
                        {"key": key, "value": serialised},
                    )

        logger.info("Stored %d resource(s) in ai_cache table", len(resources))

    except Exception as exc:
        # Database failure must not abort the release process — the app can
        # fall back to reading from the file system if the cache is missing.
        logger.error("Failed to populate database cache: %s", exc)


def warm_cache() -> int:
    """Main entry point: load AI resources and persist them to the database.

    Returns 0 on success (or graceful degradation), 1 on a hard failure.
    """
    logger.info("=== Alfanous release tasks: warming AI model cache ===")

    db_url = _get_db_url()
    logger.info(
        "Using database: %s",
        db_url.split("@")[-1] if "@" in db_url else db_url,
    )

    resources = _load_ai_resources()
    if not resources:
        logger.warning("No AI resources loaded; skipping database write.")
        return 0

    _store_in_db(resources, db_url)
    logger.info("=== Release tasks completed successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(warm_cache())
