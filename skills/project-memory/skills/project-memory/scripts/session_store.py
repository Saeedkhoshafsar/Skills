#!/usr/bin/env python3
"""Episodic session store + FTS search for SMART / project-memory (Hermes Phase 6).

Per-project SQLite under ``.smart/sessions/state.db`` with optional FTS5.
Three search shapes (Hermes parity, simplified):

  discovery — query → ranked sessions with snippet + context window
  scroll    — session_id + around_message_id → ±window messages
  browse    — recent sessions chronologically

Always-on USER/AGENT-MEMORY stays bounded; this store holds unlimited episodic
recall. Prefer always-on stores first; use session_search for specifics.

Privacy: redaction hooks before insert; local-only by default (no network).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from memory_store import project_root  # type: ignore
except ImportError:  # pragma: no cover
    project_root = None  # type: ignore

SESSIONS_REL = Path(".smart/sessions")
DB_NAME = "state.db"
CONFIG_REL = Path(".smart/memory/config.json")

DEFAULT_WINDOW = 5
DEFAULT_DISCOVER_LIMIT = 10
DEFAULT_BROWSE_LIMIT = 20
DEFAULT_GET_LIMIT = 50
MAX_CONTENT_CHARS = 20_000
MAX_FTS_QUERY_CHARS = 2_048
EXTRACT_DEFAULT_LIMIT = 30

# Automation sources demoted / hidden from browse by default (Hermes-inspired).
_HIDDEN_SOURCES = frozenset({"subagent", "tool"})
_DEMOTED_SOURCES = frozenset({"cron"})

_VALID_ROLES = frozenset({"user", "assistant", "system", "tool", "note"})
_VALID_SOURCES = frozenset(
    {"interactive", "compact", "handoff", "tool", "subagent", "cron", "import"}
)

# Redaction patterns (order matters — more specific first).
_REDACT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "pem_private_key",
        re.compile(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?"
            r"-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
            re.MULTILINE,
        ),
    ),
    (
        "bearer_token",
        re.compile(r"(?i)\b(bearer\s+)[a-z0-9\-._~+/]+=*", re.ASCII),
    ),
    (
        "openai_sk",
        re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    ),
    (
        "aws_access_key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
    (
        "github_pat",
        re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    ),
    (
        "generic_api_key_assign",
        re.compile(
            r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)"
            r"\s*[:=]\s*['\"]?[A-Za-z0-9\-._]{16,}['\"]?"
        ),
    ),
    (
        "long_hex_token",
        re.compile(r"\b[a-f0-9]{40,}\b", re.IGNORECASE),
    ),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def emit(payload: dict[str, Any], *, code: int = 0) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return code


def _resolve_root(start: str) -> Path:
    if project_root is not None:
        return project_root(start)
    return Path(start).resolve()


def load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def db_path(root: Path) -> Path:
    cfg = load_config(root)
    sessions_cfg = cfg.get("sessions") if isinstance(cfg.get("sessions"), dict) else {}
    custom = sessions_cfg.get("db_path") if isinstance(sessions_cfg, dict) else None
    if custom:
        p = Path(str(custom))
        return p if p.is_absolute() else root / p
    return root / SESSIONS_REL / DB_NAME


def redact_secrets(text: str) -> tuple[str, bool, list[str]]:
    """Return (redacted_text, changed, kinds). Local-only; no network."""
    if not text:
        return text, False, []
    out = text
    kinds: list[str] = []
    for kind, pat in _REDACT_PATTERNS:
        def _sub(m: re.Match[str], k: str = kind) -> str:
            if k == "bearer_token" and m.lastindex:
                return f"{m.group(1)}[REDACTED:{k}]"
            if k == "generic_api_key_assign":
                return f"{m.group(1)}=[REDACTED:{k}]"
            return f"[REDACTED:{k}]"

        new_out, n = pat.subn(_sub, out)
        if n:
            kinds.append(kind)
            out = new_out
    return out, bool(kinds), kinds


def truncate_content(text: str, limit: int = MAX_CONTENT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n…[truncated]"


def sanitize_fts_query(query: str) -> str:
    """Cap length and strip FTS special chars; build simple AND of tokens."""
    q = (query or "").strip()
    if len(q) > MAX_FTS_QUERY_CHARS:
        q = q[:MAX_FTS_QUERY_CHARS]
    # Drop FTS operators / quotes that break MATCH
    q = re.sub(r'[*"(){}[\]^~:]+', " ", q)
    tokens = [t for t in re.split(r"\s+", q) if t and not t.startswith("-")]
    if not tokens:
        return ""
    # Quote each token for phrase-safe match
    safe = []
    for t in tokens[:32]:
        t2 = re.sub(r"[^\w.@/+-]", "", t, flags=re.UNICODE)
        if t2:
            safe.append(f'"{t2}"')
    return " ".join(safe)


class SessionStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = db_path(root)
        self.fts_enabled = False
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema(conn)
        self._conn = conn
        return conn

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except sqlite3.Error:
                pass
            self._conn = None

    def _init_schema(self, conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                source TEXT DEFAULT 'interactive',
                task_id TEXT,
                mode TEXT,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                meta_json TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                task_id TEXT,
                timestamp TEXT NOT NULL,
                redacted INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id, id);
            CREATE INDEX IF NOT EXISTS idx_sessions_started
                ON sessions(started_at DESC);
            """
        )
        # FTS5 external content table
        try:
            conn.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5("
                "content, content='messages', content_rowid='id')"
            )
            conn.executescript(
                """
                CREATE TRIGGER IF NOT EXISTS messages_fts_ai
                AFTER INSERT ON messages BEGIN
                    INSERT INTO messages_fts(rowid, content)
                    VALUES (new.id, new.content);
                END;
                CREATE TRIGGER IF NOT EXISTS messages_fts_ad
                AFTER DELETE ON messages BEGIN
                    INSERT INTO messages_fts(messages_fts, rowid, content)
                    VALUES ('delete', old.id, old.content);
                END;
                CREATE TRIGGER IF NOT EXISTS messages_fts_au
                AFTER UPDATE ON messages BEGIN
                    INSERT INTO messages_fts(messages_fts, rowid, content)
                    VALUES ('delete', old.id, old.content);
                    INSERT INTO messages_fts(rowid, content)
                    VALUES (new.id, new.content);
                END;
                """
            )
            # Probe MATCH
            conn.execute(
                "SELECT 1 FROM messages_fts WHERE messages_fts MATCH ? LIMIT 1",
                ('"__probe__"',),
            )
            self.fts_enabled = True
        except sqlite3.OperationalError:
            self.fts_enabled = False
        conn.commit()

    # -- sessions -----------------------------------------------------------

    def start(
        self,
        *,
        session_id: str | None = None,
        title: str | None = None,
        source: str = "interactive",
        task_id: str | None = None,
        mode: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        sid = (session_id or "").strip() or f"s-{uuid.uuid4().hex[:12]}"
        src = source if source in _VALID_SOURCES else "interactive"
        conn = self.connect()
        existing = conn.execute(
            "SELECT id FROM sessions WHERE id = ?", (sid,)
        ).fetchone()
        if existing:
            return {
                "success": True,
                "session_id": sid,
                "created": False,
                "path": str(self.path.relative_to(self.root))
                if self.path.is_relative_to(self.root)
                else str(self.path),
            }
        conn.execute(
            """
            INSERT INTO sessions (id, title, source, task_id, mode, started_at, meta_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sid,
                title,
                src,
                task_id,
                mode,
                _now_iso(),
                json.dumps(meta or {}, ensure_ascii=False) if meta else None,
            ),
        )
        conn.commit()
        return {
            "success": True,
            "session_id": sid,
            "created": True,
            "source": src,
            "title": title,
            "task_id": task_id,
            "mode": mode,
            "started_at": _now_iso(),
            "db": str(SESSIONS_REL / DB_NAME),
        }

    def end(self, session_id: str) -> dict[str, Any]:
        conn = self.connect()
        row = conn.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            return {
                "success": False,
                "error": f"session not found: {session_id}",
                "session_id": session_id,
            }
        ended = _now_iso()
        conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ?",
            (ended, session_id),
        )
        conn.commit()
        return {"success": True, "session_id": session_id, "ended_at": ended}

    def append(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        if role not in _VALID_ROLES:
            return {
                "success": False,
                "error": f"invalid role {role!r}; expected {sorted(_VALID_ROLES)}",
            }
        conn = self.connect()
        sess = conn.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not sess:
            # Auto-create interactive session if missing
            self.start(session_id=session_id, source="interactive", task_id=task_id)
            conn = self.connect()

        raw = content if content is not None else ""
        redacted_text, changed, kinds = redact_secrets(raw)
        redacted_text = truncate_content(redacted_text)
        ts = _now_iso()
        cur = conn.execute(
            """
            INSERT INTO messages (session_id, role, content, task_id, timestamp, redacted)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                redacted_text,
                task_id,
                ts,
                1 if changed else 0,
            ),
        )
        conn.commit()
        mid = int(cur.lastrowid or 0)
        return {
            "success": True,
            "session_id": session_id,
            "message_id": mid,
            "role": role,
            "timestamp": ts,
            "redacted": changed,
            "redaction_kinds": kinds,
            "content_len": len(redacted_text),
        }

    # -- search shapes ------------------------------------------------------

    def browse(
        self,
        *,
        limit: int = DEFAULT_BROWSE_LIMIT,
        include_automation: bool = False,
    ) -> dict[str, Any]:
        conn = self.connect()
        limit = max(1, min(int(limit), 100))
        rows = conn.execute(
            """
            SELECT s.*,
                   (SELECT content FROM messages m
                    WHERE m.session_id = s.id
                    ORDER BY m.id DESC LIMIT 1) AS preview,
                   (SELECT COUNT(*) FROM messages m WHERE m.session_id = s.id) AS msg_count
            FROM sessions s
            ORDER BY s.started_at DESC
            LIMIT ?
            """,
            (limit * 3 if not include_automation else limit,),
        ).fetchall()
        sessions: list[dict[str, Any]] = []
        for r in rows:
            src = r["source"] or "interactive"
            if not include_automation and src in _HIDDEN_SOURCES | _DEMOTED_SOURCES:
                continue
            sessions.append(
                {
                    "session_id": r["id"],
                    "title": r["title"],
                    "source": src,
                    "task_id": r["task_id"],
                    "mode": r["mode"],
                    "started_at": r["started_at"],
                    "ended_at": r["ended_at"],
                    "msg_count": r["msg_count"],
                    "preview": (r["preview"] or "")[:200],
                }
            )
            if len(sessions) >= limit:
                break
        return {
            "success": True,
            "mode": "browse",
            "count": len(sessions),
            "sessions": sessions,
            "fts_enabled": self.fts_enabled,
            "message": (
                f"Showing {len(sessions)} most recent sessions. "
                "Pass --query to search, or --session-id + --around-message-id to scroll."
            ),
        }

    def scroll(
        self,
        session_id: str,
        around_message_id: int,
        *,
        window: int = DEFAULT_WINDOW,
    ) -> dict[str, Any]:
        conn = self.connect()
        window = max(0, min(int(window), 50))
        anchor = conn.execute(
            "SELECT * FROM messages WHERE id = ? AND session_id = ?",
            (around_message_id, session_id),
        ).fetchone()
        if not anchor:
            return {
                "success": False,
                "error": (
                    f"message {around_message_id} not found in session {session_id}"
                ),
                "mode": "scroll",
            }
        rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE session_id = ?
              AND id BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (
                session_id,
                around_message_id - window,
                around_message_id + window,
            ),
        ).fetchall()
        messages = [self._shape_message(r, around_message_id) for r in rows]
        return {
            "success": True,
            "mode": "scroll",
            "session_id": session_id,
            "around_message_id": around_message_id,
            "window": window,
            "count": len(messages),
            "messages": messages,
        }

    def search(
        self,
        query: str,
        *,
        limit: int = DEFAULT_DISCOVER_LIMIT,
        window: int = DEFAULT_WINDOW,
        include_automation: bool = False,
    ) -> dict[str, Any]:
        conn = self.connect()
        limit = max(1, min(int(limit), 50))
        window = max(0, min(int(window), 50))
        fts_q = sanitize_fts_query(query)
        if not fts_q and not (query or "").strip():
            return {
                "success": False,
                "error": "empty query",
                "mode": "discovery",
            }

        hits: list[sqlite3.Row] = []
        backend = "like"
        if self.fts_enabled and fts_q:
            try:
                hits = conn.execute(
                    """
                    SELECT m.*, s.source AS session_source, s.title AS session_title,
                           s.started_at AS session_started,
                           bm25(messages_fts) AS rank
                    FROM messages_fts
                    JOIN messages m ON m.id = messages_fts.rowid
                    JOIN sessions s ON s.id = m.session_id
                    WHERE messages_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                    """,
                    (fts_q, max(limit * 30, 100)),
                ).fetchall()
                backend = "fts5"
            except sqlite3.OperationalError:
                hits = []
                backend = "like"

        if not hits:
            # LIKE fallback
            tokens = [t for t in re.split(r"\s+", (query or "").strip()) if t][:8]
            if not tokens:
                tokens = [fts_q.strip('"')] if fts_q else []
            if not tokens:
                return {
                    "success": True,
                    "mode": "discovery",
                    "query": query,
                    "backend": backend,
                    "count": 0,
                    "sessions": [],
                }
            where = " AND ".join(["m.content LIKE ?" for _ in tokens])
            params: list[Any] = [f"%{t}%" for t in tokens]
            params.append(max(limit * 30, 100))
            hits = conn.execute(
                f"""
                SELECT m.*, s.source AS session_source, s.title AS session_title,
                       s.started_at AS session_started,
                       0.0 AS rank
                FROM messages m
                JOIN sessions s ON s.id = m.session_id
                WHERE {where}
                ORDER BY m.id DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
            backend = "like"

        # Demote automation sources
        def sort_key(r: sqlite3.Row) -> tuple[int, float, int]:
            src = r["session_source"] or ""
            demoted = 1 if src in _DEMOTED_SOURCES | _HIDDEN_SOURCES else 0
            if not include_automation and src in _HIDDEN_SOURCES:
                demoted = 2
            rank = float(r["rank"] or 0)
            return (demoted, rank, -int(r["id"]))

        ordered = sorted(hits, key=sort_key)

        # Group by session_id, keep best hit per session
        seen: dict[str, sqlite3.Row] = {}
        for r in ordered:
            src = r["session_source"] or "interactive"
            if not include_automation and src in _HIDDEN_SOURCES | _DEMOTED_SOURCES:
                # allow demoted only if include_automation; hide tool/subagent
                if src in _HIDDEN_SOURCES or src in _DEMOTED_SOURCES:
                    continue
            sid = r["session_id"]
            if sid not in seen:
                seen[sid] = r
            if len(seen) >= limit:
                break

        sessions_out: list[dict[str, Any]] = []
        for sid, hit in seen.items():
            mid = int(hit["id"])
            ctx = conn.execute(
                """
                SELECT * FROM messages
                WHERE session_id = ? AND id BETWEEN ? AND ?
                ORDER BY id ASC
                """,
                (sid, mid - window, mid + window),
            ).fetchall()
            content = hit["content"] or ""
            snippet = content if len(content) <= 240 else content[:240] + "…"
            sessions_out.append(
                {
                    "session_id": sid,
                    "title": hit["session_title"],
                    "source": hit["session_source"],
                    "started_at": hit["session_started"],
                    "match_message_id": mid,
                    "match_role": hit["role"],
                    "snippet": snippet,
                    "context": [self._shape_message(m, mid) for m in ctx],
                }
            )

        return {
            "success": True,
            "mode": "discovery",
            "query": query,
            "fts_query": fts_q,
            "backend": backend,
            "count": len(sessions_out),
            "sessions": sessions_out,
            "fts_enabled": self.fts_enabled,
        }

    def get_session(
        self,
        session_id: str,
        *,
        limit: int = DEFAULT_GET_LIMIT,
    ) -> dict[str, Any]:
        conn = self.connect()
        sess = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not sess:
            return {
                "success": False,
                "error": f"session not found: {session_id}",
            }
        limit = max(1, min(int(limit), 500))
        rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        return {
            "success": True,
            "session": {
                "session_id": sess["id"],
                "title": sess["title"],
                "source": sess["source"],
                "task_id": sess["task_id"],
                "mode": sess["mode"],
                "started_at": sess["started_at"],
                "ended_at": sess["ended_at"],
            },
            "count": len(rows),
            "messages": [self._shape_message(r) for r in rows],
        }

    def extract_durable(
        self,
        session_id: str,
        *,
        limit: int = EXTRACT_DEFAULT_LIMIT,
    ) -> dict[str, Any]:
        """Candidate notes for pre-compact promotion — does NOT write USER/AGENT-MEMORY."""
        conn = self.connect()
        sess = conn.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not sess:
            return {
                "success": False,
                "error": f"session not found: {session_id}",
            }
        limit = max(1, min(int(limit), 200))
        rows = conn.execute(
            """
            SELECT * FROM messages
            WHERE session_id = ? AND role IN ('user', 'assistant', 'note')
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        candidates = []
        for r in reversed(list(rows)):
            text = (r["content"] or "").strip()
            if len(text) < 12:
                continue
            # Heuristic durable signals
            low = text.lower()
            signals = []
            for needle, label in (
                ("decid", "decision"),
                ("prefer", "preference"),
                ("always ", "preference"),
                ("never ", "preference"),
                ("remember", "memory"),
                ("we will use", "decision"),
                ("chose ", "decision"),
                ("task ", "task"),
                ("p", "task_id_maybe"),
            ):
                if needle in low:
                    signals.append(label)
            candidates.append(
                {
                    "message_id": r["id"],
                    "role": r["role"],
                    "timestamp": r["timestamp"],
                    "task_id": r["task_id"],
                    "content": text[:500],
                    "signals": sorted(set(signals)),
                    "suggest_target": (
                        "user"
                        if any(s == "preference" for s in signals)
                        else "memory"
                        if signals
                        else None
                    ),
                }
            )
        return {
            "success": True,
            "session_id": session_id,
            "count": len(candidates),
            "candidates": candidates,
            "note": (
                "Candidates only — promote durable facts via memory_store "
                "add/replace into USER.md or AGENT-MEMORY.md; do not free-form dump."
            ),
        }

    def status(self) -> dict[str, Any]:
        conn = self.connect()
        n_sess = conn.execute("SELECT COUNT(*) AS c FROM sessions").fetchone()["c"]
        n_msg = conn.execute("SELECT COUNT(*) AS c FROM messages").fetchone()["c"]
        return {
            "success": True,
            "db": str(SESSIONS_REL / DB_NAME),
            "db_exists": self.path.is_file(),
            "fts_enabled": self.fts_enabled,
            "session_count": n_sess,
            "message_count": n_msg,
            "defaults": {
                "window": DEFAULT_WINDOW,
                "discover_limit": DEFAULT_DISCOVER_LIMIT,
                "browse_limit": DEFAULT_BROWSE_LIMIT,
                "max_content_chars": MAX_CONTENT_CHARS,
            },
            "routing": (
                "Prefer USER.md / AGENT-MEMORY.md for durable prefs and env facts; "
                "use session discovery/scroll/browse for episodic specifics."
            ),
        }

    @staticmethod
    def _shape_message(
        row: sqlite3.Row, anchor_id: int | None = None
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "id": row["id"],
            "role": row["role"],
            "content": row["content"],
            "timestamp": row["timestamp"],
        }
        if row["task_id"]:
            entry["task_id"] = row["task_id"]
        if row["redacted"]:
            entry["redacted"] = True
        if anchor_id is not None and row["id"] == anchor_id:
            entry["anchor"] = True
        return entry


# -- CLI --------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".", help="Project root")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Session DB status")

    st = sub.add_parser("start", help="Start or resume a session row")
    st.add_argument("--session-id", default=None)
    st.add_argument("--title", default=None)
    st.add_argument("--source", default="interactive")
    st.add_argument("--task-id", default=None)
    st.add_argument("--mode", default=None)

    en = sub.add_parser("end", help="Mark session ended")
    en.add_argument("--session-id", required=True)

    ap = sub.add_parser("append", help="Append a redacted message")
    ap.add_argument("--session-id", required=True)
    ap.add_argument(
        "--role",
        required=True,
        choices=sorted(_VALID_ROLES),
    )
    ap.add_argument("--content", required=True)
    ap.add_argument("--task-id", default=None)

    se = sub.add_parser("search", help="Discovery search (FTS/LIKE)")
    se.add_argument("--query", required=True)
    se.add_argument("--limit", type=int, default=DEFAULT_DISCOVER_LIMIT)
    se.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    se.add_argument(
        "--include-automation",
        action="store_true",
        help="Include cron/tool/subagent sources",
    )

    sc = sub.add_parser("scroll", help="Scroll ±window around message id")
    sc.add_argument("--session-id", required=True)
    sc.add_argument("--around-message-id", type=int, required=True)
    sc.add_argument("--window", type=int, default=DEFAULT_WINDOW)

    br = sub.add_parser("browse", help="Recent sessions")
    br.add_argument("--limit", type=int, default=DEFAULT_BROWSE_LIMIT)
    br.add_argument("--include-automation", action="store_true")

    gt = sub.add_parser("get", help="Get session messages")
    gt.add_argument("--session-id", required=True)
    gt.add_argument("--limit", type=int, default=DEFAULT_GET_LIMIT)

    ex = sub.add_parser(
        "extract-durable",
        help="List durable-note candidates (does not write memory)",
    )
    ex.add_argument("--session-id", required=True)
    ex.add_argument("--limit", type=int, default=EXTRACT_DEFAULT_LIMIT)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _resolve_root(args.project)
    store = SessionStore(root)
    try:
        cmd = args.command
        if cmd == "status":
            return emit(store.status())
        if cmd == "start":
            return emit(
                store.start(
                    session_id=args.session_id,
                    title=args.title,
                    source=args.source,
                    task_id=args.task_id,
                    mode=args.mode,
                )
            )
        if cmd == "end":
            r = store.end(args.session_id)
            return emit(r, code=0 if r.get("success") else 1)
        if cmd == "append":
            r = store.append(
                args.session_id,
                args.role,
                args.content,
                task_id=args.task_id,
            )
            return emit(r, code=0 if r.get("success") else 1)
        if cmd == "search":
            r = store.search(
                args.query,
                limit=args.limit,
                window=args.window,
                include_automation=bool(args.include_automation),
            )
            return emit(r, code=0 if r.get("success") else 1)
        if cmd == "scroll":
            r = store.scroll(
                args.session_id,
                args.around_message_id,
                window=args.window,
            )
            return emit(r, code=0 if r.get("success") else 1)
        if cmd == "browse":
            return emit(
                store.browse(
                    limit=args.limit,
                    include_automation=bool(args.include_automation),
                )
            )
        if cmd == "get":
            r = store.get_session(args.session_id, limit=args.limit)
            return emit(r, code=0 if r.get("success") else 1)
        if cmd == "extract-durable":
            r = store.extract_durable(args.session_id, limit=args.limit)
            return emit(r, code=0 if r.get("success") else 1)
        return emit({"success": False, "error": f"unknown command {cmd}"}, code=1)
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
