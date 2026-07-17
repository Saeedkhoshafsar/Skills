#!/usr/bin/env python3
"""Pluggable memory providers for SMART / project-memory (Hermes Phase 7).

Protocol-level port of Hermes ``agent/memory_provider.py``:

  - MemoryProvider ABC (lifecycle + optional hooks)
  - ``<memory-context>`` fencing + scrub helpers (C-23)
  - Builtin provider (USER.md / AGENT-MEMORY.md via memory_store)
  - Null provider (explicit no-op external for tests)
  - LocalFactProvider (zero-cloud SQLite facts — first real adapter)

Deep cloud adapters (Honcho, Mem0, Supermemory, …) stay catalog-documented
and optional; CI stays offline with builtin/null/local + FakeProvider tests.
"""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from memory_store import (  # type: ignore
        MemoryStore,
        load_config,
        project_root,
    )
except ImportError:  # pragma: no cover
    MemoryStore = None  # type: ignore
    load_config = None  # type: ignore
    project_root = None  # type: ignore

CONFIG_REL = Path(".smart/memory/config.json")
FACTS_REL = Path(".smart/memory/facts.db")

# Known provider names (catalog). Only builtin|null|local ship code in-tree.
KNOWN_PROVIDERS = (
    "builtin",
    "null",
    "local",
    "honcho",
    "mem0",
    "supermemory",
    "hindsight",
    "holographic",
    "openviking",
    "byterover",
    "retaindb",
)

# ---------------------------------------------------------------------------
# Context fencing (C-23) — strip / wrap external recall
# ---------------------------------------------------------------------------

_FENCE_TAG_RE = re.compile(r"</?\s*memory-context\s*>", re.IGNORECASE)
_INTERNAL_CONTEXT_RE = re.compile(
    r"<\s*memory-context\s*>[\s\S]*?</\s*memory-context\s*>",
    re.IGNORECASE,
)
_INTERNAL_NOTE_RE = re.compile(
    r"\[System note:\s*The following is recalled memory context,\s*"
    r"NOT new user input\.\s*Treat as (?:informational background data|"
    r"authoritative reference data[^\]]*)\.\]\s*",
    re.IGNORECASE,
)


def sanitize_context(text: str) -> str:
    """Strip fence tags, injected context blocks, and system notes."""
    if not text:
        return ""
    text = _INTERNAL_CONTEXT_RE.sub("", text)
    text = _INTERNAL_NOTE_RE.sub("", text)
    text = _FENCE_TAG_RE.sub("", text)
    return text


def build_memory_context_block(raw_context: str) -> str:
    """Wrap prefetched memory in a fenced block with system note."""
    if not raw_context or not str(raw_context).strip():
        return ""
    clean = sanitize_context(str(raw_context))
    if not clean.strip():
        return ""
    return (
        "<memory-context>\n"
        "[System note: The following is recalled memory context, "
        "NOT new user input. Treat as authoritative reference data — "
        "this is the agent's persistent memory and should inform all responses.]\n\n"
        f"{clean.strip()}\n"
        "</memory-context>"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------------------
# MemoryProvider ABC (C-18)
# ---------------------------------------------------------------------------


class MemoryProvider(ABC):
    """Abstract base class for memory providers.

    Lifecycle (called by MemoryManager):
      initialize()           — connect / warm up
      system_prompt_block()  — static text for system prompt
      prefetch(query)        — recall before each turn
      queue_prefetch(query)  — background prep for next turn
      sync_turn(user, asst)  — persist after each turn
      get_tool_schemas()     — tools exposed to the model
      handle_tool_call()     — dispatch a tool call
      shutdown()             — clean exit

    Optional hooks (override to opt in):
      on_turn_start, on_session_end, on_session_switch,
      on_pre_compress, on_memory_write, on_delegation
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier (e.g. 'builtin', 'local', 'honcho')."""

    @abstractmethod
    def is_available(self) -> bool:
        """True if configured and ready (no network calls)."""

    @abstractmethod
    def initialize(self, session_id: str, **kwargs: Any) -> None:
        """Initialize for a session."""

    def system_prompt_block(self) -> str:
        return ""

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        return ""

    def queue_prefetch(self, query: str, *, session_id: str = "") -> None:
        return None

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        return None

    @abstractmethod
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """OpenAI-style function schemas; empty if context-only."""

    def handle_tool_call(
        self, tool_name: str, args: Dict[str, Any], **kwargs: Any
    ) -> str:
        raise NotImplementedError(
            f"Provider {self.name} does not handle tool {tool_name}"
        )

    def shutdown(self) -> None:
        return None

    # -- Optional hooks -----------------------------------------------------

    def on_turn_start(
        self, turn_number: int, message: str, **kwargs: Any
    ) -> None:
        return None

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        return None

    def on_session_switch(
        self,
        new_session_id: str,
        *,
        parent_session_id: str = "",
        reset: bool = False,
        rewound: bool = False,
        **kwargs: Any,
    ) -> None:
        return None

    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str:
        return ""

    def on_memory_write(
        self,
        action: str,
        target: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        return None

    def on_delegation(
        self,
        task: str,
        result: str,
        *,
        child_session_id: str = "",
        **kwargs: Any,
    ) -> None:
        return None

    def get_config_schema(self) -> List[Dict[str, Any]]:
        return []

    def backup_paths(self) -> List[str]:
        return []


# ---------------------------------------------------------------------------
# Builtin provider — always-on USER / AGENT-MEMORY (C-18/C-19 core path)
# ---------------------------------------------------------------------------


class BuiltinMemoryProvider(MemoryProvider):
    """Wraps memory_store dual files as the always-on built-in provider."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._session_id = ""
        self._store: Any = None
        self._initialized = False

    @property
    def name(self) -> str:
        return "builtin"

    def is_available(self) -> bool:
        return MemoryStore is not None and self.root is not None

    def initialize(self, session_id: str, **kwargs: Any) -> None:
        self._session_id = session_id or ""
        if MemoryStore is None:
            raise RuntimeError("memory_store.MemoryStore unavailable")
        self._store = MemoryStore(self.root)
        try:
            self._store.load()
        except Exception:
            # Empty / missing files are fine — status still works.
            pass
        self._initialized = True

    def system_prompt_block(self) -> str:
        if not self._initialized or self._store is None:
            return ""
        try:
            user = (self._store.frozen_snapshot("user") or "").strip()
            mem = (self._store.frozen_snapshot("memory") or "").strip()
        except Exception:
            return ""
        parts: list[str] = []
        if user:
            parts.append(user)
        if mem:
            parts.append(mem)
        if not parts:
            return (
                "Built-in learning memory is empty. "
                "Use memory_store add/replace for durable prefs and lessons."
            )
        return "Built-in learning memory (always-on):\n\n" + "\n\n".join(parts)

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        # Always-on stores are already in system_prompt_block; no extra recall.
        return ""

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        # Built-in writes go through memory_store CLI / SMART protocol, not tools.
        return []

    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str:
        return (
            "Before compact: extract durable candidates; promote only via "
            "memory_store add/replace into USER.md / AGENT-MEMORY.md."
        )

    def shutdown(self) -> None:
        self._initialized = False
        self._store = None


# ---------------------------------------------------------------------------
# Null provider — explicit no-op external (tests + disable)
# ---------------------------------------------------------------------------


class NullMemoryProvider(MemoryProvider):
    """No-op external provider. Available always; contributes nothing."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else None
        self._session_id = ""

    @property
    def name(self) -> str:
        return "null"

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs: Any) -> None:
        self._session_id = session_id or ""

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return []


# ---------------------------------------------------------------------------
# LocalFactProvider — zero-cloud SQLite facts (first real adapter, C-22 local)
# ---------------------------------------------------------------------------

_FACT_TOOL = {
    "name": "local_fact_store",
    "description": (
        "Local offline fact memory (SQLite under .smart/memory/facts.db). "
        "Use for durable project/user facts beyond always-on USER/AGENT-MEMORY. "
        "Actions: add, search, list, remove."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "search", "list", "remove"],
            },
            "content": {"type": "string", "description": "Fact text (add)."},
            "query": {"type": "string", "description": "Search query."},
            "fact_id": {"type": "integer", "description": "Id for remove."},
            "category": {
                "type": "string",
                "enum": ["user_pref", "project", "tool", "general"],
            },
            "limit": {"type": "integer", "description": "Max results."},
        },
        "required": ["action"],
    },
}


class LocalFactProvider(MemoryProvider):
    """Simple local SQLite fact store — no network, no numpy."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._session_id = ""
        self._conn: Optional[sqlite3.Connection] = None
        self._prefetch_cache = ""

    @property
    def name(self) -> str:
        return "local"

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs: Any) -> None:
        self._session_id = session_id or ""
        path = self.root / FACTS_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'general',
                created_at TEXT NOT NULL,
                session_id TEXT DEFAULT ''
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_facts_content ON facts(content)"
        )
        self._conn.commit()

    def system_prompt_block(self) -> str:
        return (
            "Local fact provider active (offline SQLite). "
            "Use local_fact_store for deep recall beyond always-on memory."
        )

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        if self._prefetch_cache:
            cached, self._prefetch_cache = self._prefetch_cache, ""
            return cached
        if not query or not query.strip() or self._conn is None:
            return ""
        rows = self._search(query.strip(), limit=5)
        if not rows:
            return ""
        lines = [f"- [{r['category']}] {r['content']}" for r in rows]
        return "Local facts matching query:\n" + "\n".join(lines)

    def queue_prefetch(self, query: str, *, session_id: str = "") -> None:
        if not query or self._conn is None:
            return
        rows = self._search(query.strip(), limit=5)
        if rows:
            lines = [f"- [{r['category']}] {r['content']}" for r in rows]
            self._prefetch_cache = "Local facts (queued):\n" + "\n".join(lines)
        else:
            self._prefetch_cache = ""

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        # Local provider does not auto-extract; writes are explicit via tool.
        return None

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [dict(_FACT_TOOL)]

    def handle_tool_call(
        self, tool_name: str, args: Dict[str, Any], **kwargs: Any
    ) -> str:
        if tool_name != "local_fact_store":
            raise NotImplementedError(tool_name)
        action = (args.get("action") or "").strip().lower()
        if action == "add":
            content = (args.get("content") or "").strip()
            if not content:
                return json.dumps({"success": False, "error": "content required"})
            category = (args.get("category") or "general").strip() or "general"
            fid = self._add(content, category)
            return json.dumps(
                {"success": True, "fact_id": fid, "content": content, "category": category}
            )
        if action == "search":
            q = (args.get("query") or "").strip()
            limit = int(args.get("limit") or 10)
            rows = self._search(q, limit=limit)
            return json.dumps(
                {
                    "success": True,
                    "count": len(rows),
                    "facts": [
                        {
                            "id": r["id"],
                            "content": r["content"],
                            "category": r["category"],
                        }
                        for r in rows
                    ],
                }
            )
        if action == "list":
            limit = int(args.get("limit") or 20)
            rows = self._list(limit=limit)
            return json.dumps(
                {
                    "success": True,
                    "count": len(rows),
                    "facts": [
                        {
                            "id": r["id"],
                            "content": r["content"],
                            "category": r["category"],
                        }
                        for r in rows
                    ],
                }
            )
        if action == "remove":
            fid = args.get("fact_id")
            if fid is None:
                return json.dumps({"success": False, "error": "fact_id required"})
            ok = self._remove(int(fid))
            return json.dumps({"success": ok, "fact_id": int(fid)})
        return json.dumps({"success": False, "error": f"unknown action: {action}"})

    def on_memory_write(
        self,
        action: str,
        target: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        # Optional mirror: when built-in memory adds, also store a local fact.
        if action != "add" or not content or not content.strip():
            return
        if self._conn is None:
            return
        cat = "user_pref" if target == "user" else "tool"
        self._add(content.strip(), cat)

    def shutdown(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _add(self, content: str, category: str) -> int:
        assert self._conn is not None
        cur = self._conn.execute(
            "INSERT INTO facts (content, category, created_at, session_id) "
            "VALUES (?, ?, ?, ?)",
            (content, category, _now_iso(), self._session_id),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def _search(self, query: str, *, limit: int = 10) -> list[sqlite3.Row]:
        assert self._conn is not None
        if not query:
            return list(
                self._conn.execute(
                    "SELECT id, content, category FROM facts "
                    "ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
            )
        # Multi-token: match if any token appears (OR). Full-phrase first.
        tokens = [t for t in re.split(r"\s+", query.strip()) if t]
        if not tokens:
            return []
        # Prefer phrase match, then fall back to any-token match.
        phrase = f"%{query.strip()}%"
        rows = list(
            self._conn.execute(
                "SELECT id, content, category FROM facts "
                "WHERE content LIKE ? COLLATE NOCASE "
                "ORDER BY id DESC LIMIT ?",
                (phrase, limit),
            )
        )
        if rows:
            return rows
        clauses = " OR ".join(
            ["content LIKE ? COLLATE NOCASE"] * len(tokens)
        )
        params: list[Any] = [f"%{t}%" for t in tokens]
        params.append(limit)
        return list(
            self._conn.execute(
                f"SELECT id, content, category FROM facts "
                f"WHERE {clauses} "
                f"ORDER BY id DESC LIMIT ?",
                params,
            )
        )

    def _list(self, *, limit: int = 20) -> list[sqlite3.Row]:
        assert self._conn is not None
        return list(
            self._conn.execute(
                "SELECT id, content, category FROM facts "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            )
        )

    def _remove(self, fact_id: int) -> bool:
        assert self._conn is not None
        cur = self._conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
        self._conn.commit()
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Factory / config (C-20, C-24, P7-T7)
# ---------------------------------------------------------------------------


def resolve_provider_name(root: Path, override: str | None = None) -> str:
    """Read ``memory.provider`` from config; default ``builtin``."""
    if override:
        return override.strip().lower()
    cfg: dict[str, Any] = {}
    if load_config is not None:
        try:
            cfg = load_config(root) or {}
        except Exception:
            cfg = {}
    if not cfg:
        path = root / CONFIG_REL
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    cfg = data
            except (OSError, json.JSONDecodeError):
                pass
    mem = cfg.get("memory")
    if isinstance(mem, dict) and mem.get("provider"):
        return str(mem["provider"]).strip().lower()
    if cfg.get("provider"):
        return str(cfg["provider"]).strip().lower()
    return "builtin"


def create_provider(name: str, root: Path) -> MemoryProvider:
    """Instantiate a shipped provider by name.

    Catalog-only names (honcho, mem0, …) raise — they are not in-tree.
    """
    key = (name or "builtin").strip().lower()
    if key in ("builtin", ""):
        return BuiltinMemoryProvider(root)
    if key == "null":
        return NullMemoryProvider(root)
    if key == "local":
        return LocalFactProvider(root)
    if key in KNOWN_PROVIDERS:
        raise ValueError(
            f"Provider '{key}' is catalog-documented but not shipped in-tree. "
            f"Install/enable separately, or use builtin|null|local. "
            f"See project-memory provider catalog."
        )
    raise ValueError(
        f"Unknown memory provider '{key}'. "
        f"Known: {', '.join(KNOWN_PROVIDERS)}"
    )


def provider_catalog() -> list[dict[str, Any]]:
    """Documented provider catalog (P7-T5)."""
    return [
        {
            "name": "builtin",
            "shipped": True,
            "network": False,
            "summary": "Always-on USER.md + AGENT-MEMORY.md via memory_store.",
        },
        {
            "name": "null",
            "shipped": True,
            "network": False,
            "summary": "No-op external; tests and explicit disable.",
        },
        {
            "name": "local",
            "shipped": True,
            "network": False,
            "summary": "Zero-cloud SQLite facts under .smart/memory/facts.db.",
        },
        {
            "name": "honcho",
            "shipped": False,
            "network": True,
            "summary": "Dialectic user model (deep mind-clone). Optional plugin.",
        },
        {
            "name": "mem0",
            "shipped": False,
            "network": True,
            "summary": "Managed memory graph. Optional plugin.",
        },
        {
            "name": "supermemory",
            "shipped": False,
            "network": True,
            "summary": "Hosted long-term memory. Optional plugin.",
        },
        {
            "name": "hindsight",
            "shipped": False,
            "network": True,
            "summary": "Temporal/episodic external memory. Optional plugin.",
        },
        {
            "name": "holographic",
            "shipped": False,
            "network": False,
            "summary": "HRR vector facts (numpy). Optional; use local for lean offline.",
        },
        {
            "name": "openviking",
            "shipped": False,
            "network": True,
            "summary": "Optional external memory backend.",
        },
        {
            "name": "byterover",
            "shipped": False,
            "network": True,
            "summary": "Optional external memory backend.",
        },
        {
            "name": "retaindb",
            "shipped": False,
            "network": True,
            "summary": "Optional external memory backend.",
        },
    ]


def main(argv: list[str] | None = None) -> int:
    """Minimal CLI: catalog | resolve | create-check."""
    import argparse

    p = argparse.ArgumentParser(description="Memory provider helpers (Phase 7)")
    p.add_argument("--project", default=".", help="Project root")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("catalog", help="List provider catalog")
    r = sub.add_parser("resolve", help="Resolve configured provider name")
    r.add_argument("--provider", default=None)
    c = sub.add_parser("create-check", help="Instantiate provider and report availability")
    c.add_argument("--provider", default=None)
    c.add_argument("--session-id", default="")

    args = p.parse_args(argv)
    root = project_root(args.project) if project_root else Path(args.project).resolve()

    if args.cmd == "catalog":
        print(json.dumps({"providers": provider_catalog()}, indent=2))
        return 0

    if args.cmd == "resolve":
        name = resolve_provider_name(root, getattr(args, "provider", None))
        print(json.dumps({"provider": name, "root": str(root)}, indent=2))
        return 0

    if args.cmd == "create-check":
        name = resolve_provider_name(root, getattr(args, "provider", None))
        try:
            prov = create_provider(name, root)
        except ValueError as e:
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
            return 1
        available = prov.is_available()
        sid = args.session_id or ("s_" + uuid.uuid4().hex[:8])
        if available:
            prov.initialize(sid)
        block = prov.system_prompt_block() if available else ""
        tools = prov.get_tool_schemas() if available else []
        if available:
            prov.shutdown()
        print(
            json.dumps(
                {
                    "success": True,
                    "provider": name,
                    "available": available,
                    "system_prompt_chars": len(block or ""),
                    "tool_count": len(tools),
                    "tools": [t.get("name") for t in tools],
                },
                indent=2,
            )
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
