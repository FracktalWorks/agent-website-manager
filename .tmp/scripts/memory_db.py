#!/usr/bin/env python3
"""
Memory Database — SQLite + FTS5 persistent memory for DOE Framework agents.

Provides ALL agents with a local, searchable database split into:
  SHORT-TERM MEMORY — Session/task working memory (auto-expires)
  LONG-TERM MEMORY  — Persistent facts, entities, insights, decisions

Every piece of information is an independently searchable atom.
Zero external dependencies — uses Python's built-in sqlite3.

Usage:
    # === UNIVERSAL SEARCH (main agent interface) ===
    python memory_db.py search "customer onboarding"
    python memory_db.py search "API rate limit" --type facts
    python memory_db.py search "project deadline" --after 2026-01-01

    # === SHORT-TERM MEMORY (session/task context) ===
    python memory_db.py stm set "current_task" "Processing batch 3 of lead enrichment"
    python memory_db.py stm set "last_error" "Rate limit hit on SerpAPI" --ttl 3600
    python memory_db.py stm get "current_task"
    python memory_db.py stm show
    python memory_db.py stm clear                    # Clear expired entries
    python memory_db.py stm clear --all              # Clear everything

    # === LONG-TERM MEMORY: Facts ===
    python memory_db.py add-fact "SerpAPI free tier allows 100 searches/month" \\
        --category "api_limits" --tags "serpapi,rate-limit"
    python memory_db.py add-fact "Client prefers formal tone in emails" \\
        --category "preferences" --entity "Client ABC"

    # === LONG-TERM MEMORY: Entities ===
    python memory_db.py add-entity "Acme Corp" --type company \\
        --details "Primary client, 50 employees, SaaS product" --tags "client,saas"
    python memory_db.py add-entity "John Smith" --type person \\
        --details "CTO at Acme Corp, decision maker" --tags "contact,decision-maker"

    # === LONG-TERM MEMORY: Insights (append-only lessons learned) ===
    python memory_db.py add-insight "Always add 200ms delay between API calls to avoid 429s" \\
        --category "api"
    python memory_db.py add-insight "PDF extraction works better with pymupdf than pdfplumber for academic papers" \\
        --category "tools"

    # === INTERACTIONS (conversation/task log) ===
    python memory_db.py log-interaction --summary "Generated 50 leads for Acme Corp" \\
        --topics "lead-gen,google-maps" --follow-ups "Enrich emails,Send to client"

    # === DECISIONS ===
    python memory_db.py log-decision --decision "Switch from Apify to direct scraping" \\
        --context "Apify costs too high for volume needed"
    python memory_db.py update-outcome 1 "Direct scraping 3x cheaper, slightly slower"

    # === CONTEXT (mutable current state) ===
    python memory_db.py context set "project.stage" "data_collection"
    python memory_db.py context set "project.client" "Acme Corp"
    python memory_db.py context get "project.stage"
    python memory_db.py context show

    # === PROFILE (agent/project identity) ===
    python memory_db.py profile set "agent.type" "lead_generation"
    python memory_db.py profile show

    # === MAINTENANCE ===
    python memory_db.py status
    python memory_db.py rebuild-fts
    python memory_db.py export --format json          # Export all memory as JSON
"""

import os
import sys
import json
import sqlite3
import argparse
import re
import struct
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
MEMORY_DIR = PROJECT_ROOT / "memory"
DB_PATH = MEMORY_DIR / "agent_memory.db"

# ---------------------------------------------------------------------------
# Optional: Sentence-Transformers for semantic/embedding search
# Falls back gracefully if not installed — BM25 still works fine.
# Install with: pip install sentence-transformers
# ---------------------------------------------------------------------------
_EMBEDDER = None
_EMBED_DIM = 0

def _get_embedder():
    """Lazy-load the embedding model. Returns None if unavailable."""
    global _EMBEDDER, _EMBED_DIM
    if _EMBEDDER is not None:
        return _EMBEDDER
    try:
        from sentence_transformers import SentenceTransformer
        model_name = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _EMBEDDER = SentenceTransformer(model_name)
        _EMBED_DIM = _EMBEDDER.get_sentence_embedding_dimension()
        return _EMBEDDER
    except ImportError:
        return None

def _embed_text(text):
    """Embed a single text string. Returns bytes or None."""
    model = _get_embedder()
    if model is None:
        return None
    vec = model.encode(text, normalize_embeddings=True)
    return struct.pack(f"{len(vec)}f", *vec)

def _cosine_similarity(a_bytes, b_bytes):
    """Compute cosine similarity between two embedding byte blobs."""
    n = len(a_bytes) // 4
    a = struct.unpack(f"{n}f", a_bytes)
    b = struct.unpack(f"{n}f", b_bytes)
    dot = sum(x * y for x, y in zip(a, b))
    return dot  # Already normalized, so dot product = cosine similarity


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def get_db(db_path=None):
    """Get a connection to the memory database."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn):
    """Create all tables and FTS indexes if they don't exist."""
    conn.executescript(dedent("""\
        -- =============================================
        -- SHORT-TERM MEMORY: Session/task working memory
        -- Key-value with optional TTL (time-to-live)
        -- =============================================
        CREATE TABLE IF NOT EXISTS short_term (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL,
            category    TEXT DEFAULT 'session',
            created_at  TEXT DEFAULT (datetime('now')),
            expires_at  TEXT DEFAULT NULL,
            access_count INTEGER DEFAULT 0
        );

        -- =============================================
        -- PROFILE: Key-value store for agent/project identity
        -- =============================================
        CREATE TABLE IF NOT EXISTS profile (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL,
            category    TEXT DEFAULT 'general',
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- =============================================
        -- CONTEXT: Mutable current state (project status, etc.)
        -- =============================================
        CREATE TABLE IF NOT EXISTS context (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL,
            category    TEXT DEFAULT 'general',
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- =============================================
        -- INTERACTIONS: Conversation/task log
        -- =============================================
        CREATE TABLE IF NOT EXISTS interactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL DEFAULT (datetime('now')),
            summary     TEXT NOT NULL,
            topics      TEXT DEFAULT '',
            advice      TEXT DEFAULT '',
            follow_ups  TEXT DEFAULT '',
            raw_data    TEXT DEFAULT ''
        );

        -- =============================================
        -- DECISIONS: Decision journal with outcomes
        -- =============================================
        CREATE TABLE IF NOT EXISTS decisions (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            date                TEXT NOT NULL DEFAULT (datetime('now')),
            decision            TEXT NOT NULL,
            context             TEXT DEFAULT '',
            reasoning           TEXT DEFAULT '',
            expected_outcome    TEXT DEFAULT '',
            actual_outcome      TEXT DEFAULT '',
            status              TEXT DEFAULT 'pending',
            outcome_date        TEXT DEFAULT NULL
        );

        -- =============================================
        -- FACTS: Atomic searchable knowledge units
        -- Every discrete piece of information = one row.
        -- =============================================
        CREATE TABLE IF NOT EXISTS facts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            content     TEXT NOT NULL,
            category    TEXT DEFAULT 'general',
            entity      TEXT DEFAULT '',
            tags        TEXT DEFAULT '',
            source      TEXT DEFAULT '',
            confidence  TEXT DEFAULT 'confirmed',
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- =============================================
        -- ENTITIES: People, companies, concepts, tools
        -- =============================================
        CREATE TABLE IF NOT EXISTS entities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            type        TEXT DEFAULT 'general',
            details     TEXT DEFAULT '',
            tags        TEXT DEFAULT '',
            first_mentioned TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        -- =============================================
        -- INSIGHTS: Accumulated wisdom (append-only)
        -- Lessons learned, patterns, self-annealing notes
        -- =============================================
        CREATE TABLE IF NOT EXISTS insights (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            content     TEXT NOT NULL,
            category    TEXT DEFAULT 'general',
            date        TEXT DEFAULT (datetime('now'))
        );

        -- =============================================
        -- EMBEDDINGS: Optional vector storage for semantic search
        -- Stores embeddings as BLOBs alongside a reference to source
        -- =============================================
        CREATE TABLE IF NOT EXISTS embeddings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source_table TEXT NOT NULL,
            source_id   TEXT NOT NULL,
            text_hash   TEXT NOT NULL,
            embedding   BLOB NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(source_table, source_id)
        );

        -- =============================================
        -- EVALUATION LOG: Track task outcomes, costs, quality
        -- =============================================
        CREATE TABLE IF NOT EXISTS evaluation_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL DEFAULT (datetime('now')),
            task_name   TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'success',
            score       REAL DEFAULT NULL,
            cost_usd    REAL DEFAULT 0.0,
            tokens_used INTEGER DEFAULT 0,
            duration_s  REAL DEFAULT 0.0,
            input_hash  TEXT DEFAULT '',
            output_hash TEXT DEFAULT '',
            errors      TEXT DEFAULT '',
            notes       TEXT DEFAULT ''
        );

        -- =============================================
        -- GUARDRAIL LOG: Track validation checks and violations
        -- =============================================
        CREATE TABLE IF NOT EXISTS guardrail_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL DEFAULT (datetime('now')),
            check_name  TEXT NOT NULL,
            passed      INTEGER NOT NULL DEFAULT 1,
            severity    TEXT DEFAULT 'info',
            details     TEXT DEFAULT '',
            task_name   TEXT DEFAULT '',
            remediation TEXT DEFAULT ''
        );

        -- =============================================
        -- FTS5 VIRTUAL TABLES for ranked full-text search
        -- =============================================

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_interactions USING fts5(
            summary, topics, advice, follow_ups,
            content='interactions', content_rowid='id',
            tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_facts USING fts5(
            content, category, entity, tags,
            content='facts', content_rowid='id',
            tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_entities USING fts5(
            name, type, details, tags,
            content='entities', content_rowid='id',
            tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_decisions USING fts5(
            decision, context, reasoning, expected_outcome, actual_outcome,
            content='decisions', content_rowid='id',
            tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_insights USING fts5(
            content, category,
            content='insights', content_rowid='id',
            tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_profile USING fts5(
            key, value, category,
            content='profile',
            tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_context USING fts5(
            key, value, category,
            content='context',
            tokenize='porter unicode61'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_short_term USING fts5(
            key, value, category,
            content='short_term',
            tokenize='porter unicode61'
        );

        -- =============================================
        -- TRIGGERS to keep FTS indexes in sync
        -- =============================================

        -- interactions
        CREATE TRIGGER IF NOT EXISTS trg_interactions_ai AFTER INSERT ON interactions BEGIN
            INSERT INTO fts_interactions(rowid, summary, topics, advice, follow_ups)
            VALUES (new.id, new.summary, new.topics, new.advice, new.follow_ups);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_interactions_ad AFTER DELETE ON interactions BEGIN
            INSERT INTO fts_interactions(fts_interactions, rowid, summary, topics, advice, follow_ups)
            VALUES ('delete', old.id, old.summary, old.topics, old.advice, old.follow_ups);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_interactions_au AFTER UPDATE ON interactions BEGIN
            INSERT INTO fts_interactions(fts_interactions, rowid, summary, topics, advice, follow_ups)
            VALUES ('delete', old.id, old.summary, old.topics, old.advice, old.follow_ups);
            INSERT INTO fts_interactions(rowid, summary, topics, advice, follow_ups)
            VALUES (new.id, new.summary, new.topics, new.advice, new.follow_ups);
        END;

        -- facts
        CREATE TRIGGER IF NOT EXISTS trg_facts_ai AFTER INSERT ON facts BEGIN
            INSERT INTO fts_facts(rowid, content, category, entity, tags)
            VALUES (new.id, new.content, new.category, new.entity, new.tags);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_facts_ad AFTER DELETE ON facts BEGIN
            INSERT INTO fts_facts(fts_facts, rowid, content, category, entity, tags)
            VALUES ('delete', old.id, old.content, old.category, old.entity, old.tags);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_facts_au AFTER UPDATE ON facts BEGIN
            INSERT INTO fts_facts(fts_facts, rowid, content, category, entity, tags)
            VALUES ('delete', old.id, old.content, old.category, old.entity, old.tags);
            INSERT INTO fts_facts(rowid, content, category, entity, tags)
            VALUES (new.id, new.content, new.category, new.entity, new.tags);
        END;

        -- entities
        CREATE TRIGGER IF NOT EXISTS trg_entities_ai AFTER INSERT ON entities BEGIN
            INSERT INTO fts_entities(rowid, name, type, details, tags)
            VALUES (new.id, new.name, new.type, new.details, new.tags);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_entities_ad AFTER DELETE ON entities BEGIN
            INSERT INTO fts_entities(fts_entities, rowid, name, type, details, tags)
            VALUES ('delete', old.id, old.name, old.type, old.details, old.tags);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_entities_au AFTER UPDATE ON entities BEGIN
            INSERT INTO fts_entities(fts_entities, rowid, name, type, details, tags)
            VALUES ('delete', old.id, old.name, old.type, old.details, old.tags);
            INSERT INTO fts_entities(rowid, name, type, details, tags)
            VALUES (new.id, new.name, new.type, new.details, new.tags);
        END;

        -- decisions
        CREATE TRIGGER IF NOT EXISTS trg_decisions_ai AFTER INSERT ON decisions BEGIN
            INSERT INTO fts_decisions(rowid, decision, context, reasoning, expected_outcome, actual_outcome)
            VALUES (new.id, new.decision, new.context, new.reasoning, new.expected_outcome, new.actual_outcome);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_decisions_ad AFTER DELETE ON decisions BEGIN
            INSERT INTO fts_decisions(fts_decisions, rowid, decision, context, reasoning, expected_outcome, actual_outcome)
            VALUES ('delete', old.id, old.decision, old.context, old.reasoning, old.expected_outcome, old.actual_outcome);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_decisions_au AFTER UPDATE ON decisions BEGIN
            INSERT INTO fts_decisions(fts_decisions, rowid, decision, context, reasoning, expected_outcome, actual_outcome)
            VALUES ('delete', old.id, old.decision, old.context, old.reasoning, old.expected_outcome, old.actual_outcome);
            INSERT INTO fts_decisions(rowid, decision, context, reasoning, expected_outcome, actual_outcome)
            VALUES (new.id, new.decision, new.context, new.reasoning, new.expected_outcome, new.actual_outcome);
        END;

        -- insights
        CREATE TRIGGER IF NOT EXISTS trg_insights_ai AFTER INSERT ON insights BEGIN
            INSERT INTO fts_insights(rowid, content, category)
            VALUES (new.id, new.content, new.category);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_insights_ad AFTER DELETE ON insights BEGIN
            INSERT INTO fts_insights(fts_insights, rowid, content, category)
            VALUES ('delete', old.id, old.content, old.category);
        END;
        CREATE TRIGGER IF NOT EXISTS trg_insights_au AFTER UPDATE ON insights BEGIN
            INSERT INTO fts_insights(fts_insights, rowid, content, category)
            VALUES ('delete', old.id, old.content, old.category);
            INSERT INTO fts_insights(rowid, content, category)
            VALUES (new.id, new.content, new.category);
        END;
    """))
    conn.commit()


# ---------------------------------------------------------------------------
# Rebuild FTS indexes
# ---------------------------------------------------------------------------

def rebuild_fts(conn):
    """Rebuild all FTS indexes from source tables."""
    tables = [
        "fts_interactions", "fts_facts", "fts_entities",
        "fts_decisions", "fts_insights",
    ]
    for fts_table in tables:
        try:
            conn.execute(f"INSERT INTO {fts_table}({fts_table}) VALUES('rebuild')")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    print("FTS indexes rebuilt.")


# ---------------------------------------------------------------------------
# SHORT-TERM MEMORY (session/task working memory)
# ---------------------------------------------------------------------------

def stm_set(conn, key, value, category="session", ttl_seconds=None):
    """Set a short-term memory entry. Optional TTL for auto-expiry."""
    expires_at = None
    if ttl_seconds:
        expires_at = (datetime.now() + timedelta(seconds=int(ttl_seconds))).isoformat()

    # Clean up FTS for existing entry
    existing = conn.execute("SELECT key, value, category FROM short_term WHERE key = ?", (key,)).fetchone()
    if existing:
        try:
            conn.execute(
                "INSERT INTO fts_short_term(fts_short_term, key, value, category) VALUES('delete', ?, ?, ?)",
                (existing["key"], existing["value"], existing["category"])
            )
        except sqlite3.OperationalError:
            pass

    conn.execute("""
        INSERT INTO short_term (key, value, category, created_at, expires_at, access_count)
        VALUES (?, ?, ?, datetime('now'), ?, 0)
        ON CONFLICT(key) DO UPDATE SET
            value=excluded.value, category=excluded.category,
            expires_at=excluded.expires_at, access_count=0
    """, (key, value, category, expires_at))

    try:
        conn.execute(
            "INSERT INTO fts_short_term(key, value, category) VALUES(?, ?, ?)",
            (key, value, category)
        )
    except sqlite3.OperationalError:
        pass
    conn.commit()
    ttl_msg = f" (expires in {ttl_seconds}s)" if ttl_seconds else ""
    print(f"STM set: {key}{ttl_msg}")


def stm_get(conn, key):
    """Get a short-term memory value. Returns None if expired."""
    _stm_cleanup_expired(conn)
    row = conn.execute("SELECT * FROM short_term WHERE key = ?", (key,)).fetchone()
    if not row:
        return None
    # Increment access count
    conn.execute("UPDATE short_term SET access_count = access_count + 1 WHERE key = ?", (key,))
    conn.commit()
    return dict(row)


def stm_show(conn):
    """Show all short-term memory entries."""
    _stm_cleanup_expired(conn)
    rows = conn.execute("SELECT * FROM short_term ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def stm_clear(conn, clear_all=False):
    """Clear expired entries, or all entries if clear_all=True."""
    if clear_all:
        conn.execute("DELETE FROM short_term")
        try:
            conn.execute("DELETE FROM fts_short_term")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        print("Cleared all short-term memory.")
    else:
        count = _stm_cleanup_expired(conn)
        print(f"Cleared {count} expired entries.")


def _stm_cleanup_expired(conn):
    """Remove expired short-term memory entries."""
    now = datetime.now().isoformat()
    expired = conn.execute(
        "SELECT key FROM short_term WHERE expires_at IS NOT NULL AND expires_at < ?", (now,)
    ).fetchall()
    for row in expired:
        conn.execute("DELETE FROM short_term WHERE key = ?", (row["key"],))
    conn.commit()
    return len(expired)


# ---------------------------------------------------------------------------
# PROFILE operations
# ---------------------------------------------------------------------------

def profile_set(conn, key, value, category="general"):
    """Set a profile key-value pair. Upserts."""
    existing = conn.execute("SELECT key, value, category FROM profile WHERE key = ?", (key,)).fetchone()
    if existing:
        try:
            conn.execute(
                "INSERT INTO fts_profile(fts_profile, key, value, category) VALUES('delete', ?, ?, ?)",
                (existing["key"], existing["value"], existing["category"])
            )
        except sqlite3.OperationalError:
            pass

    conn.execute("""
        INSERT INTO profile (key, value, category, updated_at)
        VALUES (?, ?, ?, datetime('now'))
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, category=excluded.category, updated_at=datetime('now')
    """, (key, value, category))

    try:
        conn.execute(
            "INSERT INTO fts_profile(key, value, category) VALUES(?, ?, ?)",
            (key, value, category)
        )
    except sqlite3.OperationalError:
        pass
    conn.commit()


def profile_get(conn, key):
    """Get a profile value by key."""
    row = conn.execute("SELECT * FROM profile WHERE key = ?", (key,)).fetchone()
    return dict(row) if row else None


def profile_show(conn):
    """Show all profile data grouped by category."""
    rows = conn.execute("SELECT * FROM profile ORDER BY category, key").fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# CONTEXT operations
# ---------------------------------------------------------------------------

def context_set(conn, key, value, category="general"):
    """Set a context key-value pair. Upserts."""
    existing = conn.execute("SELECT key, value, category FROM context WHERE key = ?", (key,)).fetchone()
    if existing:
        try:
            conn.execute(
                "INSERT INTO fts_context(fts_context, key, value, category) VALUES('delete', ?, ?, ?)",
                (existing["key"], existing["value"], existing["category"])
            )
        except sqlite3.OperationalError:
            pass

    conn.execute("""
        INSERT INTO context (key, value, category, updated_at)
        VALUES (?, ?, ?, datetime('now'))
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, category=excluded.category, updated_at=datetime('now')
    """, (key, value, category))

    try:
        conn.execute(
            "INSERT INTO fts_context(key, value, category) VALUES(?, ?, ?)",
            (key, value, category)
        )
    except sqlite3.OperationalError:
        pass
    conn.commit()


def context_get(conn, key):
    """Get a context value by key."""
    row = conn.execute("SELECT * FROM context WHERE key = ?", (key,)).fetchone()
    return dict(row) if row else None


def context_show(conn):
    """Show all context data."""
    rows = conn.execute("SELECT * FROM context ORDER BY category, key").fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# INTERACTION logging
# ---------------------------------------------------------------------------

def log_interaction(conn, summary, topics="", advice="", follow_ups="", raw_data=""):
    """Log a conversation/task interaction."""
    cur = conn.execute("""
        INSERT INTO interactions (summary, topics, advice, follow_ups, raw_data)
        VALUES (?, ?, ?, ?, ?)
    """, (summary, topics, advice, follow_ups, raw_data))
    conn.commit()
    print(f"Logged interaction #{cur.lastrowid}")
    return cur.lastrowid


# ---------------------------------------------------------------------------
# DECISION logging
# ---------------------------------------------------------------------------

def log_decision(conn, decision, context="", reasoning="", expected=""):
    """Log a decision."""
    cur = conn.execute("""
        INSERT INTO decisions (decision, context, reasoning, expected_outcome)
        VALUES (?, ?, ?, ?)
    """, (decision, context, reasoning, expected))
    conn.commit()
    print(f"Logged decision #{cur.lastrowid}")
    return cur.lastrowid


def update_outcome(conn, decision_id, outcome, status="completed"):
    """Update a decision's outcome."""
    conn.execute("""
        UPDATE decisions SET actual_outcome = ?, status = ?, outcome_date = datetime('now')
        WHERE id = ?
    """, (outcome, status, int(decision_id)))
    conn.commit()
    print(f"Updated decision #{decision_id}")


# ---------------------------------------------------------------------------
# FACT storage
# ---------------------------------------------------------------------------

def add_fact(conn, content, category="general", entity="", tags="", source="", confidence="confirmed"):
    """Store an atomic fact."""
    cur = conn.execute("""
        INSERT INTO facts (content, category, entity, tags, source, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (content, category, entity, tags, source, confidence))
    conn.commit()
    print(f"Stored fact #{cur.lastrowid}")
    return cur.lastrowid


# ---------------------------------------------------------------------------
# ENTITY storage
# ---------------------------------------------------------------------------

def add_entity(conn, name, type_="general", details="", tags=""):
    """Store or update an entity."""
    existing = conn.execute("SELECT id FROM entities WHERE name = ?", (name,)).fetchone()
    if existing:
        conn.execute("""
            UPDATE entities SET details = ?, type = ?, tags = ?, updated_at = datetime('now')
            WHERE name = ?
        """, (details, type_, tags, name))
        conn.commit()
        print(f"Updated entity: {name}")
        return existing["id"]
    else:
        cur = conn.execute("""
            INSERT INTO entities (name, type, details, tags) VALUES (?, ?, ?, ?)
        """, (name, type_, details, tags))
        conn.commit()
        print(f"Stored entity: {name} (#{cur.lastrowid})")
        return cur.lastrowid


# ---------------------------------------------------------------------------
# INSIGHT storage
# ---------------------------------------------------------------------------

def add_insight(conn, content, category="general"):
    """Store an insight (append-only)."""
    cur = conn.execute("""
        INSERT INTO insights (content, category) VALUES (?, ?)
    """, (content, category))
    conn.commit()
    print(f"Stored insight #{cur.lastrowid}")
    return cur.lastrowid


# ---------------------------------------------------------------------------
# UNIVERSAL SEARCH
# ---------------------------------------------------------------------------

def search(conn, query, type_filter=None, after=None, before=None, limit=20):
    """
    Search across ALL memory tables using FTS5 ranked search.
    Returns results sorted by relevance (BM25 score).
    """
    results = []
    fts_query = _sanitize_fts_query(query)

    search_configs = {
        "short_term": {
            "fts": "fts_short_term", "src": "short_term",
            "date_col": "created_at", "rowid_is_key": True,
            "display": lambda r: f"[STM - {r['key']}] {r['value'][:200]}"
        },
        "interactions": {
            "fts": "fts_interactions", "src": "interactions",
            "date_col": "date", "rowid_is_key": False,
            "display": lambda r: f"[Interaction #{r['id']} - {r['date'][:10]}] {r['summary'][:200]}"
        },
        "facts": {
            "fts": "fts_facts", "src": "facts",
            "date_col": "created_at", "rowid_is_key": False,
            "display": lambda r: f"[Fact - {r['category']}] {r['content'][:200]}"
        },
        "entities": {
            "fts": "fts_entities", "src": "entities",
            "date_col": "first_mentioned", "rowid_is_key": False,
            "display": lambda r: f"[Entity - {r['type']}] {r['name']}: {r['details'][:150]}"
        },
        "decisions": {
            "fts": "fts_decisions", "src": "decisions",
            "date_col": "date", "rowid_is_key": False,
            "display": lambda r: f"[Decision #{r['id']} - {r['status']}] {r['decision'][:200]}"
        },
        "insights": {
            "fts": "fts_insights", "src": "insights",
            "date_col": "date", "rowid_is_key": False,
            "display": lambda r: f"[Insight - {r['category']}] {r['content'][:200]}"
        },
        "profile": {
            "fts": "fts_profile", "src": "profile",
            "date_col": "updated_at", "rowid_is_key": True,
            "display": lambda r: f"[Profile - {r['key']}] {r['value'][:200]}"
        },
        "context": {
            "fts": "fts_context", "src": "context",
            "date_col": "updated_at", "rowid_is_key": True,
            "display": lambda r: f"[Context - {r['key']}] {r['value'][:200]}"
        },
    }

    types_to_search = [type_filter] if type_filter and type_filter in search_configs else list(search_configs.keys())

    for stype in types_to_search:
        cfg = search_configs[stype]
        is_kv = cfg.get("rowid_is_key", False)

        try:
            if is_kv:
                sql = f"""
                    SELECT s.*, fts.rank FROM {cfg['fts']} fts
                    JOIN {cfg['src']} s ON s.key = fts.key
                    WHERE {cfg['fts']} MATCH ? ORDER BY fts.rank LIMIT ?
                """
            else:
                sql = f"""
                    SELECT s.*, fts.rank FROM {cfg['fts']} fts
                    JOIN {cfg['src']} s ON s.id = fts.rowid
                    WHERE {cfg['fts']} MATCH ? ORDER BY fts.rank LIMIT ?
                """
            rows = conn.execute(sql, (fts_query, limit)).fetchall()

            for row in rows:
                r = dict(row)
                date_val = r.get(cfg["date_col"], "")
                if after and date_val and date_val < after:
                    continue
                if before and date_val and date_val > before:
                    continue
                results.append({
                    "type": stype,
                    "id": r.get("id") or r.get("key"),
                    "score": abs(r.get("rank", 0)),
                    "display": cfg["display"](r),
                    "date": date_val,
                    "data": {k: v for k, v in r.items() if k != "rank"}
                })
        except sqlite3.OperationalError:
            continue

    results.sort(key=lambda x: x["score"])
    return results


def _sanitize_fts_query(query):
    """Convert natural language query into valid FTS5 query."""
    if any(op in query for op in [' OR ', ' AND ', ' NOT ', '"', '*']):
        return query
    cleaned = re.sub(r'[^\w\s"*]', ' ', query)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    if not tokens:
        return query
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# STATUS / health check
# ---------------------------------------------------------------------------

def get_status(conn):
    """Get a summary of all memory tables."""
    tables = ["short_term", "profile", "context", "interactions", "decisions", "facts", "entities", "insights", "embeddings", "evaluation_log", "guardrail_log"]
    status = {}
    for table in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()["c"]
            status[table] = count
        except sqlite3.OperationalError:
            status[table] = "missing"
    return status


# ---------------------------------------------------------------------------
# EXPORT (dump entire memory as JSON)
# ---------------------------------------------------------------------------

def export_all(conn):
    """Export all memory as a JSON-serializable dict."""
    output = {}
    for table in ["short_term", "profile", "context", "interactions", "decisions", "facts", "entities", "insights", "evaluation_log", "guardrail_log"]:
        try:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            output[table] = [dict(r) for r in rows]
        except sqlite3.OperationalError:
            output[table] = []
    return output


# ---------------------------------------------------------------------------
# SEMANTIC / EMBEDDING SEARCH (optional — requires sentence-transformers)
# ---------------------------------------------------------------------------

def embed_store(conn, source_table, source_id, text):
    """Compute and store an embedding for a piece of text."""
    emb = _embed_text(text)
    if emb is None:
        return False
    text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
    conn.execute("""
        INSERT INTO embeddings (source_table, source_id, text_hash, embedding)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(source_table, source_id) DO UPDATE SET
            embedding=excluded.embedding, text_hash=excluded.text_hash, created_at=datetime('now')
    """, (source_table, str(source_id), text_hash, emb))
    conn.commit()
    return True


def embed_search(conn, query, top_k=10, source_table=None):
    """
    Semantic search across stored embeddings.
    Returns top_k results ranked by cosine similarity.
    Requires sentence-transformers to be installed.
    """
    query_emb = _embed_text(query)
    if query_emb is None:
        print("Embedding model not available. Install: pip install sentence-transformers")
        return []

    sql = "SELECT * FROM embeddings"
    params = []
    if source_table:
        sql += " WHERE source_table = ?"
        params.append(source_table)
    rows = conn.execute(sql, params).fetchall()

    scored = []
    for row in rows:
        sim = _cosine_similarity(query_emb, row["embedding"])
        scored.append({
            "source_table": row["source_table"],
            "source_id": row["source_id"],
            "similarity": round(sim, 4),
        })
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]


def embed_sync(conn):
    """
    Sync embeddings for all facts, insights, and entities.
    Skips entries that already have up-to-date embeddings.
    """
    if _get_embedder() is None:
        print("Embedding model not available. Install: pip install sentence-transformers")
        return

    synced = 0
    # Facts
    for row in conn.execute("SELECT id, content, category, entity, tags FROM facts").fetchall():
        text = f"{row['content']} [{row['category']}] {row['entity']} {row['tags']}"
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        existing = conn.execute(
            "SELECT text_hash FROM embeddings WHERE source_table='facts' AND source_id=?",
            (str(row["id"]),)
        ).fetchone()
        if existing and existing["text_hash"] == text_hash:
            continue
        if embed_store(conn, "facts", row["id"], text):
            synced += 1

    # Insights
    for row in conn.execute("SELECT id, content, category FROM insights").fetchall():
        text = f"{row['content']} [{row['category']}]"
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        existing = conn.execute(
            "SELECT text_hash FROM embeddings WHERE source_table='insights' AND source_id=?",
            (str(row["id"]),)
        ).fetchone()
        if existing and existing["text_hash"] == text_hash:
            continue
        if embed_store(conn, "insights", row["id"], text):
            synced += 1

    # Entities
    for row in conn.execute("SELECT id, name, type, details, tags FROM entities").fetchall():
        text = f"{row['name']} ({row['type']}): {row['details']} {row['tags']}"
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        existing = conn.execute(
            "SELECT text_hash FROM embeddings WHERE source_table='entities' AND source_id=?",
            (str(row["id"]),)
        ).fetchone()
        if existing and existing["text_hash"] == text_hash:
            continue
        if embed_store(conn, "entities", row["id"], text):
            synced += 1

    # Interactions
    for row in conn.execute("SELECT id, summary, topics FROM interactions").fetchall():
        text = f"{row['summary']} {row['topics']}"
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        existing = conn.execute(
            "SELECT text_hash FROM embeddings WHERE source_table='interactions' AND source_id=?",
            (str(row["id"]),)
        ).fetchone()
        if existing and existing["text_hash"] == text_hash:
            continue
        if embed_store(conn, "interactions", row["id"], text):
            synced += 1

    print(f"Synced {synced} embeddings.")


def hybrid_search(conn, query, type_filter=None, after=None, before=None, limit=20, semantic_weight=0.3):
    """
    Hybrid search combining BM25 (keyword) and semantic (embedding) results.
    Falls back to pure BM25 if embeddings are unavailable.

    Args:
        semantic_weight: 0.0 = pure BM25, 1.0 = pure semantic, 0.3 = default blend
    """
    # Always get BM25 results
    bm25_results = search(conn, query, type_filter, after, before, limit)

    # Try semantic search
    semantic_results = embed_search(conn, query, top_k=limit, source_table=type_filter)
    if not semantic_results:
        return bm25_results  # Fallback to pure BM25

    # Build combined score map: key = (type, id)
    combined = {}
    # Normalize BM25 scores (lower is better in BM25, invert to 0-1 where 1 is best)
    if bm25_results:
        max_bm25 = max(r["score"] for r in bm25_results) or 1.0
        for r in bm25_results:
            key = (r["type"], str(r["id"]))
            bm25_norm = 1.0 - (r["score"] / max_bm25) if max_bm25 > 0 else 1.0
            combined[key] = {
                "bm25": bm25_norm,
                "semantic": 0.0,
                "result": r,
            }

    # Add semantic scores
    for sr in semantic_results:
        key = (sr["source_table"], str(sr["source_id"]))
        if key in combined:
            combined[key]["semantic"] = sr["similarity"]
        else:
            # Semantic-only result — need to fetch full data
            combined[key] = {
                "bm25": 0.0,
                "semantic": sr["similarity"],
                "result": {
                    "type": sr["source_table"],
                    "id": sr["source_id"],
                    "score": 0.0,
                    "display": f"[{sr['source_table']}#{sr['source_id']}] (semantic match)",
                    "date": "",
                    "data": {},
                },
            }

    # Compute blended score
    for key, entry in combined.items():
        entry["final_score"] = (
            (1 - semantic_weight) * entry["bm25"]
            + semantic_weight * entry["semantic"]
        )

    # Sort by final score (higher is better)
    ranked = sorted(combined.values(), key=lambda x: x["final_score"], reverse=True)
    return [entry["result"] for entry in ranked[:limit]]


# ---------------------------------------------------------------------------
# MEMORY CONSOLIDATION / REFLECTION
# ---------------------------------------------------------------------------

def consolidate_stm(conn, days_old=1):
    """
    Move important short-term memories to long-term storage.
    STM entries older than `days_old` with high access_count become facts.
    Low-access entries are discarded.
    """
    cutoff = (datetime.now() - timedelta(days=days_old)).isoformat()
    old_entries = conn.execute(
        "SELECT * FROM short_term WHERE created_at < ?", (cutoff,)
    ).fetchall()

    promoted = 0
    discarded = 0
    for entry in old_entries:
        if entry["access_count"] >= 2:
            # Promote to fact
            add_fact(conn, f"[From STM] {entry['key']}: {entry['value']}",
                     category="promoted_stm", tags="auto-consolidated")
            promoted += 1
        else:
            discarded += 1
        conn.execute("DELETE FROM short_term WHERE key = ?", (entry["key"],))
    conn.commit()

    print(f"Consolidated STM: {promoted} promoted to facts, {discarded} discarded")
    return {"promoted": promoted, "discarded": discarded}


def deduplicate_facts(conn, similarity_threshold=0.95):
    """
    Find and merge near-duplicate facts.
    Uses embedding similarity if available, else exact content match.
    """
    if _get_embedder() is not None:
        return _deduplicate_facts_semantic(conn, similarity_threshold)
    else:
        return _deduplicate_facts_exact(conn)


def _deduplicate_facts_exact(conn):
    """Remove exact duplicate facts (same content, keep oldest)."""
    dupes = conn.execute("""
        SELECT content, COUNT(*) as cnt, MIN(id) as keep_id
        FROM facts GROUP BY content HAVING cnt > 1
    """).fetchall()
    removed = 0
    for dupe in dupes:
        conn.execute("DELETE FROM facts WHERE content = ? AND id != ?",
                     (dupe["content"], dupe["keep_id"]))
        removed += conn.execute("SELECT changes()").fetchone()[0]
    conn.commit()
    if removed:
        rebuild_fts(conn)
    print(f"Deduplicated: removed {removed} exact duplicate facts")
    return removed


def _deduplicate_facts_semantic(conn, threshold):
    """Remove semantically similar facts using embeddings."""
    embed_sync(conn)  # Ensure embeddings are current

    facts = conn.execute("SELECT id, content FROM facts ORDER BY id").fetchall()
    embs = {}
    for f in facts:
        row = conn.execute(
            "SELECT embedding FROM embeddings WHERE source_table='facts' AND source_id=?",
            (str(f["id"]),)
        ).fetchone()
        if row:
            embs[f["id"]] = row["embedding"]

    to_remove = set()
    fact_ids = list(embs.keys())
    for i in range(len(fact_ids)):
        if fact_ids[i] in to_remove:
            continue
        for j in range(i + 1, len(fact_ids)):
            if fact_ids[j] in to_remove:
                continue
            sim = _cosine_similarity(embs[fact_ids[i]], embs[fact_ids[j]])
            if sim >= threshold:
                to_remove.add(fact_ids[j])  # Remove the newer one

    for fid in to_remove:
        conn.execute("DELETE FROM facts WHERE id = ?", (fid,))
        conn.execute("DELETE FROM embeddings WHERE source_table='facts' AND source_id=?", (str(fid),))
    conn.commit()
    if to_remove:
        rebuild_fts(conn)
    print(f"Deduplicated: removed {len(to_remove)} similar facts (threshold={threshold})")
    return len(to_remove)


def generate_consolidation_report(conn):
    """
    Generate a consolidation/reflection report for the orchestrator (LLM) to review.
    Outputs a JSON summary of memory state + suggested actions.
    """
    status = get_status(conn)

    # Pending decisions
    pending = conn.execute(
        "SELECT id, decision, date FROM decisions WHERE status = 'pending' ORDER BY date"
    ).fetchall()

    # Stale STM (older than 24h)
    cutoff_24h = (datetime.now() - timedelta(hours=24)).isoformat()
    stale_stm = conn.execute(
        "SELECT key, value, created_at FROM short_term WHERE created_at < ?", (cutoff_24h,)
    ).fetchall()

    # Recent high-frequency topics
    recent_interactions = conn.execute(
        "SELECT topics FROM interactions WHERE date > ? ORDER BY date DESC LIMIT 50",
        ((datetime.now() - timedelta(days=7)).isoformat(),)
    ).fetchall()
    topic_freq = {}
    for row in recent_interactions:
        for t in row["topics"].split(","):
            t = t.strip()
            if t:
                topic_freq[t] = topic_freq.get(t, 0) + 1
    top_topics = sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    # Duplicate fact candidates (exact content match)
    dupe_count = conn.execute(
        "SELECT COUNT(*) as c FROM (SELECT content FROM facts GROUP BY content HAVING COUNT(*) > 1)"
    ).fetchone()["c"]

    report = {
        "timestamp": datetime.now().isoformat(),
        "memory_status": {k: v for k, v in status.items()},
        "actions_needed": [],
        "pending_decisions": [dict(r) for r in pending],
        "stale_stm_entries": [dict(r) for r in stale_stm],
        "top_topics_7d": top_topics,
        "duplicate_facts": dupe_count,
    }

    # Suggest actions
    if stale_stm:
        report["actions_needed"].append(
            f"Consolidate {len(stale_stm)} stale STM entries (run: consolidate-stm)"
        )
    if pending:
        report["actions_needed"].append(
            f"Review {len(pending)} pending decisions — update outcomes"
        )
    if dupe_count > 0:
        report["actions_needed"].append(
            f"Deduplicate {dupe_count} fact groups (run: deduplicate-facts)"
        )
    if status.get("embeddings", 0) == 0 and status.get("facts", 0) > 0:
        report["actions_needed"].append(
            "Sync embeddings for semantic search (run: embed-sync)"
        )

    return report


# ---------------------------------------------------------------------------
# EVALUATION & GUARDRAILS
# ---------------------------------------------------------------------------

def log_evaluation(conn, task_name, status="success", score=None, cost_usd=0.0,
                   tokens_used=0, duration_s=0.0, input_hash="", output_hash="",
                   errors="", notes=""):
    """Log a task execution for evaluation/tracking."""
    cur = conn.execute("""
        INSERT INTO evaluation_log
            (task_name, status, score, cost_usd, tokens_used, duration_s,
             input_hash, output_hash, errors, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (task_name, status, score, cost_usd, tokens_used, duration_s,
          input_hash, output_hash, errors, notes))
    conn.commit()
    print(f"Logged evaluation #{cur.lastrowid}: {task_name} [{status}]")
    return cur.lastrowid


def log_guardrail(conn, check_name, passed, severity="info", details="",
                  task_name="", remediation=""):
    """Log a guardrail check result."""
    cur = conn.execute("""
        INSERT INTO guardrail_log
            (check_name, passed, severity, details, task_name, remediation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (check_name, 1 if passed else 0, severity, details, task_name, remediation))
    conn.commit()
    status_str = "PASS" if passed else "FAIL"
    print(f"Guardrail [{status_str}] {check_name}: {details[:100]}")
    return cur.lastrowid


def check_guardrails(conn, task_name, output_text="", cost_usd=0.0, tokens_used=0):
    """
    Run standard guardrail checks on a task output.
    Returns list of check results. Logs all checks to guardrail_log.

    Checks:
    1. Output not empty
    2. No sensitive data patterns (API keys, passwords)
    3. Cost within budget
    4. Token usage within limits
    5. Output length reasonable
    """
    results = []

    # 1. Output not empty
    passed = len(output_text.strip()) > 0
    log_guardrail(conn, "output_not_empty", passed, "error" if not passed else "info",
                  f"Output length: {len(output_text)}", task_name,
                  "Task produced empty output — check script execution" if not passed else "")
    results.append({"check": "output_not_empty", "passed": passed})

    # 2. Sensitive data check (regex for common patterns)
    sensitive_patterns = [
        (r'(?:api[_-]?key|apikey)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}', "API key"),
        (r'(?:password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']{8,}', "Password"),
        (r'(?:secret|token)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}', "Secret/Token"),
        (r'(?:sk-|pk_live_|sk_live_)[a-zA-Z0-9]{20,}', "API key (known prefix)"),
    ]
    sensitive_found = []
    for pattern, label in sensitive_patterns:
        if re.search(pattern, output_text, re.IGNORECASE):
            sensitive_found.append(label)
    passed = len(sensitive_found) == 0
    log_guardrail(conn, "no_sensitive_data", passed, "critical" if not passed else "info",
                  f"Found: {', '.join(sensitive_found)}" if sensitive_found else "Clean",
                  task_name,
                  "REDACT sensitive data before output!" if not passed else "")
    results.append({"check": "no_sensitive_data", "passed": passed, "found": sensitive_found})

    # 3. Cost check (configurable daily budget)
    daily_budget = float(os.environ.get("DAILY_COST_BUDGET_USD", "10.0"))
    today = datetime.now().strftime("%Y-%m-%d")
    today_cost = conn.execute(
        "SELECT COALESCE(SUM(cost_usd), 0) as total FROM evaluation_log WHERE date LIKE ?",
        (f"{today}%",)
    ).fetchone()["total"]
    total_with_current = today_cost + cost_usd
    passed = total_with_current <= daily_budget
    log_guardrail(conn, "cost_within_budget", passed, "warning" if not passed else "info",
                  f"Today: ${total_with_current:.4f} / ${daily_budget:.2f} budget",
                  task_name,
                  "Daily cost budget exceeded! Pause expensive operations." if not passed else "")
    results.append({"check": "cost_within_budget", "passed": passed,
                    "today_cost": total_with_current, "budget": daily_budget})

    # 4. Token usage check
    token_limit = int(os.environ.get("MAX_TOKENS_PER_TASK", "100000"))
    passed = tokens_used <= token_limit
    log_guardrail(conn, "token_usage_ok", passed, "warning" if not passed else "info",
                  f"Tokens: {tokens_used:,} / {token_limit:,} limit",
                  task_name,
                  "Token usage too high — consider chunking or summarizing input." if not passed else "")
    results.append({"check": "token_usage_ok", "passed": passed})

    # 5. Output length check (not absurdly short or long)
    output_len = len(output_text)
    too_short = output_len < 10 and output_len > 0  # Non-empty but trivial
    too_long = output_len > 500000  # > 500KB is suspicious
    passed = not too_short and not too_long
    severity = "warning" if not passed else "info"
    detail = f"Output: {output_len:,} chars"
    if too_short:
        detail += " (suspiciously short)"
    if too_long:
        detail += " (unusually large)"
    log_guardrail(conn, "output_length_ok", passed, severity, detail, task_name,
                  "Review output — size is unusual" if not passed else "")
    results.append({"check": "output_length_ok", "passed": passed, "length": output_len})

    return results


def get_evaluation_summary(conn, days=7):
    """Get evaluation summary for the last N days."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    total = conn.execute(
        "SELECT COUNT(*) as c FROM evaluation_log WHERE date > ?", (cutoff,)
    ).fetchone()["c"]
    successes = conn.execute(
        "SELECT COUNT(*) as c FROM evaluation_log WHERE date > ? AND status = 'success'", (cutoff,)
    ).fetchone()["c"]
    failures = conn.execute(
        "SELECT COUNT(*) as c FROM evaluation_log WHERE date > ? AND status = 'failure'", (cutoff,)
    ).fetchone()["c"]
    total_cost = conn.execute(
        "SELECT COALESCE(SUM(cost_usd), 0) as c FROM evaluation_log WHERE date > ?", (cutoff,)
    ).fetchone()["c"]
    total_tokens = conn.execute(
        "SELECT COALESCE(SUM(tokens_used), 0) as c FROM evaluation_log WHERE date > ?", (cutoff,)
    ).fetchone()["c"]
    avg_duration = conn.execute(
        "SELECT COALESCE(AVG(duration_s), 0) as c FROM evaluation_log WHERE date > ? AND duration_s > 0",
        (cutoff,)
    ).fetchone()["c"]

    # Guardrail failures
    guardrail_failures = conn.execute(
        "SELECT check_name, COUNT(*) as cnt FROM guardrail_log WHERE date > ? AND passed = 0 GROUP BY check_name ORDER BY cnt DESC",
        (cutoff,)
    ).fetchall()

    return {
        "period_days": days,
        "total_tasks": total,
        "successes": successes,
        "failures": failures,
        "success_rate": f"{(successes/total*100):.1f}%" if total > 0 else "N/A",
        "total_cost_usd": round(total_cost, 4),
        "total_tokens": total_tokens,
        "avg_duration_s": round(avg_duration, 2),
        "guardrail_failures": [{"check": r["check_name"], "count": r["cnt"]} for r in guardrail_failures],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_search_results(results):
    """Pretty-print search results."""
    if not results:
        print("No results found.")
        return
    print(f"\n{'='*60}")
    print(f"Found {len(results)} results")
    print(f"{'='*60}\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['display']}")
        date_str = f"Date: {r['date'][:10]}  |  " if r.get('date') else ""
        print(f"   {date_str}Type: {r['type']}  |  Score: {r['score']:.2f}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Memory Database — Searchable persistent memory for DOE Framework agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Examples:
              python memory_db.py search "API rate limit"
              python memory_db.py stm set "current_task" "Processing leads"
              python memory_db.py add-fact "SerpAPI allows 100 free searches/month" --category api
              python memory_db.py add-entity "Acme Corp" --type company --details "Primary client"
              python memory_db.py status
        """)
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # --- search ---
    p_search = subparsers.add_parser("search", help="Search all memory")
    p_search.add_argument("query", help="Search terms")
    p_search.add_argument("--type", dest="type_filter")
    p_search.add_argument("--after", help="Only after date (YYYY-MM-DD)")
    p_search.add_argument("--before", help="Only before date (YYYY-MM-DD)")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.add_argument("--json", action="store_true", help="Output as JSON")

    # --- stm (short-term memory) ---
    p_stm = subparsers.add_parser("stm", help="Short-term memory operations")
    stm_sub = p_stm.add_subparsers(dest="stm_command")
    p_stm_set = stm_sub.add_parser("set", help="Set a short-term memory value")
    p_stm_set.add_argument("key")
    p_stm_set.add_argument("value")
    p_stm_set.add_argument("--ttl", type=int, help="Time-to-live in seconds")
    p_stm_set.add_argument("--category", default="session")
    p_stm_get = stm_sub.add_parser("get", help="Get a short-term memory value")
    p_stm_get.add_argument("key")
    stm_sub.add_parser("show", help="Show all short-term memory")
    p_stm_clear = stm_sub.add_parser("clear", help="Clear short-term memory")
    p_stm_clear.add_argument("--all", action="store_true", help="Clear everything, not just expired")

    # --- profile ---
    p_profile = subparsers.add_parser("profile", help="Profile operations")
    profile_sub = p_profile.add_subparsers(dest="profile_command")
    p_prof_set = profile_sub.add_parser("set", help="Set profile value")
    p_prof_set.add_argument("key")
    p_prof_set.add_argument("value")
    p_prof_set.add_argument("--category", default="general")
    p_prof_get = profile_sub.add_parser("get", help="Get profile value")
    p_prof_get.add_argument("key")
    profile_sub.add_parser("show", help="Show all profile data")

    # --- context ---
    p_ctx = subparsers.add_parser("context", help="Context operations")
    ctx_sub = p_ctx.add_subparsers(dest="ctx_command")
    p_ctx_set = ctx_sub.add_parser("set", help="Set context value")
    p_ctx_set.add_argument("key")
    p_ctx_set.add_argument("value")
    p_ctx_set.add_argument("--category", default="general")
    p_ctx_get = ctx_sub.add_parser("get", help="Get context value")
    p_ctx_get.add_argument("key")
    ctx_sub.add_parser("show", help="Show all context data")

    # --- log-interaction ---
    p_log = subparsers.add_parser("log-interaction", help="Log an interaction")
    p_log.add_argument("--summary", required=True)
    p_log.add_argument("--topics", default="")
    p_log.add_argument("--advice", default="")
    p_log.add_argument("--follow-ups", default="")

    # --- log-decision ---
    p_dec = subparsers.add_parser("log-decision", help="Log a decision")
    p_dec.add_argument("--decision", required=True)
    p_dec.add_argument("--context", default="")
    p_dec.add_argument("--reasoning", default="")
    p_dec.add_argument("--expected", default="")

    # --- update-outcome ---
    p_out = subparsers.add_parser("update-outcome", help="Update decision outcome")
    p_out.add_argument("decision_id", type=int)
    p_out.add_argument("outcome")
    p_out.add_argument("--status", default="completed")

    # --- add-fact ---
    p_fact = subparsers.add_parser("add-fact", help="Store a fact")
    p_fact.add_argument("content")
    p_fact.add_argument("--category", default="general")
    p_fact.add_argument("--entity", default="")
    p_fact.add_argument("--tags", default="")
    p_fact.add_argument("--source", default="")
    p_fact.add_argument("--confidence", default="confirmed")

    # --- add-entity ---
    p_ent = subparsers.add_parser("add-entity", help="Store an entity")
    p_ent.add_argument("name")
    p_ent.add_argument("--type", default="general")
    p_ent.add_argument("--details", default="")
    p_ent.add_argument("--tags", default="")

    # --- add-insight ---
    p_ins = subparsers.add_parser("add-insight", help="Store an insight")
    p_ins.add_argument("content")
    p_ins.add_argument("--category", default="general")

    # --- status ---
    subparsers.add_parser("status", help="Show memory status")

    # --- rebuild-fts ---
    subparsers.add_parser("rebuild-fts", help="Rebuild FTS indexes")

    # --- export ---
    p_exp = subparsers.add_parser("export", help="Export all memory")
    p_exp.add_argument("--format", default="json", choices=["json"])

    # --- embed-sync ---
    subparsers.add_parser("embed-sync", help="Sync embeddings for semantic search (requires sentence-transformers)")

    # --- embed-search ---
    p_esearch = subparsers.add_parser("embed-search", help="Semantic search via embeddings")
    p_esearch.add_argument("query", help="Search query")
    p_esearch.add_argument("--top-k", type=int, default=10)
    p_esearch.add_argument("--table", default=None, help="Limit to source table")

    # --- hybrid-search ---
    p_hsearch = subparsers.add_parser("hybrid-search", help="Hybrid BM25 + semantic search")
    p_hsearch.add_argument("query", help="Search query")
    p_hsearch.add_argument("--type", dest="type_filter", default=None)
    p_hsearch.add_argument("--after", default=None)
    p_hsearch.add_argument("--before", default=None)
    p_hsearch.add_argument("--limit", type=int, default=20)
    p_hsearch.add_argument("--semantic-weight", type=float, default=0.3)
    p_hsearch.add_argument("--json", action="store_true")

    # --- consolidation ---
    p_consol = subparsers.add_parser("consolidate-stm", help="Promote old STM to LTM, discard stale")
    p_consol.add_argument("--days", type=int, default=1, help="Entries older than N days")

    subparsers.add_parser("deduplicate-facts", help="Remove duplicate facts")

    p_reflect = subparsers.add_parser("reflect", help="Generate consolidation/reflection report")
    p_reflect.add_argument("--json", action="store_true")

    # --- evaluation ---
    p_eval_log = subparsers.add_parser("log-eval", help="Log a task evaluation")
    p_eval_log.add_argument("--task", required=True, help="Task name")
    p_eval_log.add_argument("--status", default="success", choices=["success", "failure", "partial"])
    p_eval_log.add_argument("--score", type=float, default=None)
    p_eval_log.add_argument("--cost", type=float, default=0.0, help="Cost in USD")
    p_eval_log.add_argument("--tokens", type=int, default=0)
    p_eval_log.add_argument("--duration", type=float, default=0.0, help="Duration in seconds")
    p_eval_log.add_argument("--errors", default="")
    p_eval_log.add_argument("--notes", default="")

    # --- guardrails ---
    p_guard = subparsers.add_parser("check-guardrails", help="Run guardrail checks on output")
    p_guard.add_argument("--task", required=True, help="Task name")
    p_guard.add_argument("--output-file", default=None, help="File containing output to check")
    p_guard.add_argument("--output-text", default="", help="Output text to check (inline)")
    p_guard.add_argument("--cost", type=float, default=0.0)
    p_guard.add_argument("--tokens", type=int, default=0)
    p_guard.add_argument("--json", action="store_true")

    p_eval_sum = subparsers.add_parser("eval-summary", help="Show evaluation summary")
    p_eval_sum.add_argument("--days", type=int, default=7)
    p_eval_sum.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()
    init_db(conn)

    try:
        if args.command == "search":
            results = search(conn, args.query, args.type_filter, args.after, args.before, args.limit)
            if getattr(args, 'json', False):
                print(json.dumps(results, indent=2, default=str))
            else:
                print_search_results(results)

        elif args.command == "stm":
            if args.stm_command == "set":
                stm_set(conn, args.key, args.value, args.category, args.ttl)
            elif args.stm_command == "get":
                result = stm_get(conn, args.key)
                if result:
                    print(json.dumps(result, indent=2, default=str))
                else:
                    print(f"Not found: {args.key}")
            elif args.stm_command == "show":
                entries = stm_show(conn)
                if entries:
                    for e in entries:
                        exp = f" (expires: {e['expires_at']})" if e['expires_at'] else ""
                        print(f"  {e['key']}: {e['value'][:100]}{exp}")
                else:
                    print("Short-term memory is empty.")
            elif args.stm_command == "clear":
                stm_clear(conn, getattr(args, 'all', False))
            else:
                p_stm.print_help()

        elif args.command == "profile":
            if args.profile_command == "set":
                profile_set(conn, args.key, args.value, args.category)
                print(f"Profile set: {args.key}")
            elif args.profile_command == "get":
                result = profile_get(conn, args.key)
                if result:
                    print(json.dumps(result, indent=2, default=str))
                else:
                    print(f"Not found: {args.key}")
            elif args.profile_command == "show":
                entries = profile_show(conn)
                if entries:
                    current_cat = None
                    for e in entries:
                        if e['category'] != current_cat:
                            current_cat = e['category']
                            print(f"\n[{current_cat}]")
                        print(f"  {e['key']}: {e['value'][:100]}")
                else:
                    print("Profile is empty.")
            else:
                p_profile.print_help()

        elif args.command == "context":
            if args.ctx_command == "set":
                context_set(conn, args.key, args.value, args.category)
                print(f"Context set: {args.key}")
            elif args.ctx_command == "get":
                result = context_get(conn, args.key)
                if result:
                    print(json.dumps(result, indent=2, default=str))
                else:
                    print(f"Not found: {args.key}")
            elif args.ctx_command == "show":
                entries = context_show(conn)
                if entries:
                    for e in entries:
                        print(f"  {e['key']}: {e['value'][:100]}")
                else:
                    print("Context is empty.")
            else:
                p_ctx.print_help()

        elif args.command == "log-interaction":
            log_interaction(conn, args.summary, args.topics, args.advice, getattr(args, 'follow_ups', ''))

        elif args.command == "log-decision":
            log_decision(conn, args.decision, args.context, args.reasoning, args.expected)

        elif args.command == "update-outcome":
            update_outcome(conn, args.decision_id, args.outcome, args.status)

        elif args.command == "add-fact":
            add_fact(conn, args.content, args.category, args.entity, args.tags, args.source, args.confidence)

        elif args.command == "add-entity":
            add_entity(conn, args.name, getattr(args, 'type', 'general'), args.details, args.tags)

        elif args.command == "add-insight":
            add_insight(conn, args.content, args.category)

        elif args.command == "status":
            status = get_status(conn)
            print(f"\n{'='*40}")
            print("MEMORY DATABASE STATUS")
            print(f"{'='*40}")
            print(f"  Database: {DB_PATH}")
            total = 0
            for table, count in status.items():
                icon = "short-term" if table == "short_term" else "long-term"
                print(f"  {table:15s}: {count:>5} rows  ({icon})")
                if isinstance(count, int):
                    total += count
            print(f"  {'TOTAL':15s}: {total:>5} rows")
            print(f"{'='*40}")

        elif args.command == "rebuild-fts":
            rebuild_fts(conn)

        elif args.command == "export":
            data = export_all(conn)
            print(json.dumps(data, indent=2, default=str))

        # ── Embedding commands ──────────────────────────────────
        elif args.command == "embed-sync":
            stats = embed_sync(conn)
            print(json.dumps(stats, indent=2))

        elif args.command == "embed-search":
            results = embed_search(conn, args.query, top_k=args.top_k, source_table=args.table)
            if results:
                for r in results:
                    print(f"  [{r['source_table']}#{r['source_id']}] sim={r['similarity']:.3f}  {r['text'][:120]}")
            else:
                print("No embedding results (is sentence-transformers installed? Run embed-sync first.)")

        elif args.command == "hybrid-search":
            results = hybrid_search(
                conn, args.query, args.type_filter, args.after, args.before,
                args.limit, args.semantic_weight
            )
            if getattr(args, 'json', False):
                print(json.dumps(results, indent=2, default=str))
            else:
                print_search_results(results)

        # ── Consolidation commands ──────────────────────────────
        elif args.command == "consolidate-stm":
            stats = consolidate_stm(conn, days_old=args.days)
            print(json.dumps(stats, indent=2))

        elif args.command == "deduplicate-facts":
            stats = deduplicate_facts(conn)
            print(json.dumps(stats, indent=2))

        elif args.command == "reflect":
            report = generate_consolidation_report(conn)
            if getattr(args, 'json', False):
                print(json.dumps(report, indent=2, default=str))
            else:
                print(f"\n{'='*40}")
                print("CONSOLIDATION REPORT")
                print(f"{'='*40}")
                for k, v in report.items():
                    print(f"\n[{k}]")
                    if isinstance(v, list):
                        for item in v[:10]:
                            print(f"  - {item}")
                    elif isinstance(v, dict):
                        for sk, sv in v.items():
                            print(f"  {sk}: {sv}")
                    else:
                        print(f"  {v}")
                print(f"{'='*40}")

        # ── Evaluation & Guardrail commands ─────────────────────
        elif args.command == "log-eval":
            log_evaluation(
                conn, args.task, args.status, args.score,
                args.cost, args.tokens, args.duration, args.errors, args.notes
            )
            print(f"Logged evaluation for task: {args.task}")

        elif args.command == "check-guardrails":
            output_text = args.output_text
            if args.output_file:
                with open(args.output_file, "r", encoding="utf-8") as f:
                    output_text = f.read()
            results = check_guardrails(conn, args.task, output_text, args.cost, args.tokens)
            if getattr(args, 'json', False):
                print(json.dumps(results, indent=2, default=str))
            else:
                all_passed = all(r["passed"] for r in results)
                icon = "PASS" if all_passed else "FAIL"
                print(f"\nGuardrails: {icon}")
                for r in results:
                    status_icon = "OK" if r["passed"] else "XX"
                    print(f"  [{status_icon}] {r['check']}: {r.get('details', '')}")

        elif args.command == "eval-summary":
            summary = get_evaluation_summary(conn, days=args.days)
            if getattr(args, 'json', False):
                print(json.dumps(summary, indent=2, default=str))
            else:
                print(f"\n{'='*40}")
                print(f"EVALUATION SUMMARY (last {args.days} days)")
                print(f"{'='*40}")
                for k, v in summary.items():
                    print(f"  {k}: {v}")
                print(f"{'='*40}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
