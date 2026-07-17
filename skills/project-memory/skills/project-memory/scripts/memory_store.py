#!/usr/bin/env python3
"""Bounded dual learning-memory stores for SMART / project-memory.

Hermes-parity mechanism, SMART paths:

  docs/USER.md           — user profile (prefs, style, habits)   default 1375 chars
  docs/AGENT-MEMORY.md   — agent operational notes / lessons     default 2200 chars

Actions: add | replace | remove | render | status | pending | loop
Targets: user | memory

Entry delimiter: § (section sign) with newlines around it for multiline entries.
Frozen snapshot: capture at load; mid-session writes update disk + live state only.
Overflow never silent-drops — returns error + current_entries for consolidation.

Phase 2: threat scan on write/load + optional write_approval pending queue.
Phase 3: loop-state counters + nudge intervals for self-learning reviews.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENTRY_DELIMITER = "\n§\n"
DEFAULT_USER_LIMIT = 1375
DEFAULT_MEMORY_LIMIT = 2200
DEFAULT_MEMORY_NUDGE_INTERVAL = 10
DEFAULT_SKILL_NUDGE_INTERVAL = 15
TARGET_FILES = {
    "user": "docs/USER.md",
    "memory": "docs/AGENT-MEMORY.md",
}
CONFIG_REL = Path(".smart/memory/config.json")
PENDING_REL = Path(".smart/memory/pending.json")
LOOP_STATE_REL = Path(".smart/memory/loop-state.json")

# ---------------------------------------------------------------------------
# Threat patterns (P2-T1) — minimal set for skill-injected memory.
# Scope: prompt injection, instruction override, exfil, invisible Unicode.
# Not a full security product scanner; blocks poisoned always-on snapshots.
# ---------------------------------------------------------------------------

_THREAT_REGEXES: list[tuple[str, re.Pattern[str]]] = [
    # Instruction / role override
    (
        "instruction_override",
        re.compile(
            r"(?is)\b("
            r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)"
            r"|disregard\s+(all\s+)?(previous|prior|above)"
            r"|forget\s+(all\s+)?(previous|prior|your)\s+(instructions?|rules?|guidelines?)"
            r"|override\s+(system|safety|security)\s*(prompt|rules?|instructions?)?"
            r"|you\s+are\s+now\s+(a|an|in)\b"
            r"|act\s+as\s+(if\s+you\s+have\s+no|an?\s+unrestricted)"
            r"|jailbreak"
            r"|do\s+not\s+follow\s+(your|the)\s+(system|safety|previous)"
            r")\b"
        ),
    ),
    # Fake system / developer role markers injected into memory
    (
        "role_marker_injection",
        re.compile(
            r"(?is)("
            r"^\s*system\s*:"
            r"|<\s*/?\s*system\s*>"
            r"|\[\s*system\s*\]"
            r"|<<\s*sys\s*>>"
            r"|developer\s*mode\s*(on|enabled|activated)"
            r"|###\s*system\s*(prompt|message|override)"
            r")"
        ),
    ),
    # Exfiltration / credential harvest into always-on memory
    (
        "exfil_or_credential",
        re.compile(
            r"(?is)\b("
            r"send\s+(all\s+)?(secrets?|credentials?|api[_\s-]?keys?|tokens?|passwords?)"
            r"|exfiltrat"
            r"|webhook\.site"
            r"|pastebin\.com"
            r"|curl\s+[^\n]{0,80}(api[_\s-]?key|token|password|secret|authorization)"
            r"|base64[_\s-]?encode\s+(and\s+)?(send|post|upload)"
            r")\b"
        ),
    ),
    # Invisible / bidirectional Unicode abuse (homoglyph / prompt smuggling)
    (
        "invisible_unicode",
        re.compile(
            r"["
            r"​‌‍⁠﻿"  # zero-width / word joiner / BOM
            r"‪‫‬‭‮"  # bidi overrides
            r"⁦⁧⁨⁩"  # isolate controls
            r"]"
        ),
    ),
]


def scan_threats(content: str) -> list[dict[str, str]]:
    """Return list of {id, match} for each threat pattern that hits content."""
    hits: list[dict[str, str]] = []
    for tid, pattern in _THREAT_REGEXES:
        m = pattern.search(content)
        if m:
            snippet = m.group(0)
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."
            hits.append({"id": tid, "match": snippet})
    return hits


def project_root(start: str | Path = ".") -> Path:
    path = Path(start).resolve()
    if path.is_file():
        path = path.parent
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists() or (candidate / "docs").exists():
            return candidate
    return path


def load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def emit(payload: dict[str, Any], *, code: int = 0) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return code


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _new_pending_id() -> str:
    return "p_" + uuid.uuid4().hex[:10]


class MemoryStore:
    """File-backed dual store with frozen snapshot + live mutations.

    Phase 2 adds:
      - threat scan on write and load (blocked entries excluded from snapshot)
      - optional write_approval pending queue under .smart/memory/pending.json

    Phase 3 adds:
      - loop-state counters under .smart/memory/loop-state.json
      - configurable memory/skill nudge intervals (default 10 / 15 turns)
    """

    def __init__(
        self,
        root: Path,
        *,
        user_char_limit: int | None = None,
        memory_char_limit: int | None = None,
        write_approval: bool | None = None,
        memory_nudge_interval: int | None = None,
        skill_nudge_interval: int | None = None,
    ) -> None:
        self.root = root
        cfg = load_config(root)
        self.user_char_limit = int(
            user_char_limit
            if user_char_limit is not None
            else cfg.get("user_char_limit", DEFAULT_USER_LIMIT)
        )
        self.memory_char_limit = int(
            memory_char_limit
            if memory_char_limit is not None
            else cfg.get("memory_char_limit", DEFAULT_MEMORY_LIMIT)
        )
        # P2-T5: memory.write_approval | write_approval; default false
        if write_approval is not None:
            self.write_approval = bool(write_approval)
        else:
            mem_cfg = cfg.get("memory")
            if isinstance(mem_cfg, dict) and "write_approval" in mem_cfg:
                self.write_approval = bool(mem_cfg["write_approval"])
            else:
                self.write_approval = bool(cfg.get("write_approval", False))

        # P3-T2: intervals — top-level or nested under "loop"
        loop_cfg = cfg.get("loop") if isinstance(cfg.get("loop"), dict) else {}
        if memory_nudge_interval is not None:
            self.memory_nudge_interval = int(memory_nudge_interval)
        else:
            self.memory_nudge_interval = int(
                loop_cfg.get(
                    "memory_nudge_interval",
                    cfg.get("memory_nudge_interval", DEFAULT_MEMORY_NUDGE_INTERVAL),
                )
            )
        if skill_nudge_interval is not None:
            self.skill_nudge_interval = int(skill_nudge_interval)
        else:
            self.skill_nudge_interval = int(
                loop_cfg.get(
                    "skill_nudge_interval",
                    cfg.get("skill_nudge_interval", DEFAULT_SKILL_NUDGE_INTERVAL),
                )
            )
        # Interval 0 disables that nudge (Hermes parity).
        if self.memory_nudge_interval < 0:
            self.memory_nudge_interval = 0
        if self.skill_nudge_interval < 0:
            self.skill_nudge_interval = 0

        self.user_entries: list[str] = []
        self.memory_entries: list[str] = []
        # Entries loaded from disk that failed threat scan — inspectable, not injected.
        self.blocked_entries: dict[str, list[dict[str, Any]]] = {
            "user": [],
            "memory": [],
        }
        self._system_prompt_snapshot: dict[str, str] = {"user": "", "memory": ""}

    # -- paths / limits -------------------------------------------------

    def path_for(self, target: str) -> Path:
        if target not in TARGET_FILES:
            raise ValueError(f"Unknown target {target!r}; use user|memory")
        return self.root / TARGET_FILES[target]

    def pending_path(self) -> Path:
        return self.root / PENDING_REL

    def loop_state_path(self) -> Path:
        return self.root / LOOP_STATE_REL

    def entries_for(self, target: str) -> list[str]:
        return self.user_entries if target == "user" else self.memory_entries

    def set_entries(self, target: str, entries: list[str]) -> None:
        if target == "user":
            self.user_entries = entries
        else:
            self.memory_entries = entries

    def char_limit(self, target: str) -> int:
        return self.user_char_limit if target == "user" else self.memory_char_limit

    def char_count(self, target: str) -> int:
        entries = self.entries_for(target)
        if not entries:
            return 0
        return len(ENTRY_DELIMITER.join(entries))

    # -- load / save ----------------------------------------------------

    def load(self) -> None:
        self.user_entries, self.blocked_entries["user"] = self._read_and_scan(
            self.path_for("user")
        )
        self.memory_entries, self.blocked_entries["memory"] = self._read_and_scan(
            self.path_for("memory")
        )
        self.user_entries = list(dict.fromkeys(self.user_entries))
        self.memory_entries = list(dict.fromkeys(self.memory_entries))
        # Snapshot only clean (non-blocked) entries — poisoned memory never injects.
        self._system_prompt_snapshot = {
            "user": self.render_block("user", self.user_entries),
            "memory": self.render_block("memory", self.memory_entries),
        }

    def save(self, target: str) -> None:
        path = self.path_for(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Persist clean entries + blocked raw entries (inspectable on disk).
        # Blocked stay on disk so operators can audit; load keeps them out of snapshot.
        clean = self.entries_for(target)
        blocked_raw = [b["content"] for b in self.blocked_entries.get(target, [])]
        # Dedup: clean takes precedence if same string somehow appears in both.
        blocked_only = [c for c in blocked_raw if c not in clean]
        entries = clean + blocked_only
        if not entries:
            if path.exists():
                path.write_text("", encoding="utf-8")
            return
        content = ENTRY_DELIMITER.join(entries)
        if not content.endswith("\n"):
            content += "\n"
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)

    def _read_and_scan(self, path: Path) -> tuple[list[str], list[dict[str, Any]]]:
        """Read file; split clean vs blocked. Blocked kept inspectable."""
        raw_entries = self._read_file(path)
        clean: list[str] = []
        blocked: list[dict[str, Any]] = []
        for entry in raw_entries:
            hits = scan_threats(entry)
            if hits:
                blocked.append(
                    {
                        "content": entry,
                        "threats": hits,
                        "reason": "threat_scan_on_load",
                    }
                )
            else:
                clean.append(entry)
        return clean, blocked

    @staticmethod
    def _read_file(path: Path) -> list[str]:
        if not path.exists():
            return []
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            return []
        if not raw.strip():
            return []
        entries = [e.strip() for e in raw.split(ENTRY_DELIMITER)]
        return [e for e in entries if e]

    # -- render / snapshot ----------------------------------------------

    def render_block(self, target: str, entries: list[str] | None = None) -> str:
        entries = self.entries_for(target) if entries is None else entries
        if not entries:
            return ""
        limit = self.char_limit(target)
        content = ENTRY_DELIMITER.join(entries)
        current = len(content)
        pct = min(100, int((current / limit) * 100)) if limit > 0 else 0
        if target == "user":
            header = f"USER PROFILE (who the user is) [{pct}% — {current:,}/{limit:,} chars]"
        else:
            header = (
                f"AGENT MEMORY (operational notes) [{pct}% — {current:,}/{limit:,} chars]"
            )
        separator = "═" * 46
        return f"{separator}\n{header}\n{separator}\n{content}"

    def frozen_snapshot(self, target: str) -> str:
        """Session-stable prompt block captured at load time (clean entries only)."""
        return self._system_prompt_snapshot.get(target, "")

    def status(self, target: str | None = None) -> dict[str, Any]:
        targets = [target] if target else ["user", "memory"]
        out: dict[str, Any] = {
            "success": True,
            "write_approval": self.write_approval,
            "stores": {},
        }
        for t in targets:
            current = self.char_count(t)
            limit = self.char_limit(t)
            pct = min(100, int((current / limit) * 100)) if limit > 0 else 0
            blocked = self.blocked_entries.get(t, [])
            out["stores"][t] = {
                "path": str(self.path_for(t).relative_to(self.root)),
                "entry_count": len(self.entries_for(t)),
                "usage": f"{pct}% — {current:,}/{limit:,} chars",
                "chars": current,
                "limit": limit,
                "entries": self.entries_for(t),
                "blocked_count": len(blocked),
                "blocked_entries": blocked,
            }
        pending = self.list_pending()
        out["pending_count"] = len(pending.get("pending", []))
        out["loop"] = self.loop_status()
        return out

    # -- loop state (Phase 3) -------------------------------------------

    def _default_loop_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "user_turn_count": 0,
            "turns_since_memory": 0,
            "turns_since_skill": 0,
            "last_memory_review_at": None,
            "last_skill_review_at": None,
            "last_review_kind": None,
            "updated_at": None,
        }

    def _load_loop_state(self) -> dict[str, Any]:
        path = self.loop_state_path()
        base = self._default_loop_state()
        if not path.is_file():
            return base
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return base
        if not isinstance(raw, dict):
            return base
        for key in base:
            if key in raw:
                base[key] = raw[key]
        # Coerce counters to non-negative ints.
        for key in ("user_turn_count", "turns_since_memory", "turns_since_skill"):
            try:
                base[key] = max(0, int(base[key] or 0))
            except (TypeError, ValueError):
                base[key] = 0
        return base

    def _save_loop_state(self, state: dict[str, Any]) -> None:
        path = self.loop_state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        state = dict(state)
        state["updated_at"] = _now_iso()
        path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def loop_status(self) -> dict[str, Any]:
        """Return counters, intervals, and due flags for review nudges."""
        state = self._load_loop_state()
        mem_iv = self.memory_nudge_interval
        skill_iv = self.skill_nudge_interval
        memory_due = bool(mem_iv > 0 and state["turns_since_memory"] >= mem_iv)
        skill_due = bool(skill_iv > 0 and state["turns_since_skill"] >= skill_iv)
        return {
            "user_turn_count": state["user_turn_count"],
            "turns_since_memory": state["turns_since_memory"],
            "turns_since_skill": state["turns_since_skill"],
            "memory_nudge_interval": mem_iv,
            "skill_nudge_interval": skill_iv,
            "memory_due": memory_due,
            "skill_due": skill_due,
            "any_due": memory_due or skill_due,
            "last_memory_review_at": state.get("last_memory_review_at"),
            "last_skill_review_at": state.get("last_skill_review_at"),
            "last_review_kind": state.get("last_review_kind"),
            "path": str(LOOP_STATE_REL),
        }

    def loop_tick(self, n: int = 1) -> dict[str, Any]:
        """Increment user-turn counters after a meaningful user turn.

        Call once per user message that SMART actually processes (not host
        slash-only noise). Does not run review itself — returns due flags.
        """
        if n < 1:
            n = 1
        state = self._load_loop_state()
        state["user_turn_count"] = int(state["user_turn_count"]) + n
        state["turns_since_memory"] = int(state["turns_since_memory"]) + n
        state["turns_since_skill"] = int(state["turns_since_skill"]) + n
        self._save_loop_state(state)
        status = self.loop_status()
        status["success"] = True
        status["message"] = f"Ticked {n} user turn(s)."
        return status

    def loop_mark_reviewed(
        self,
        kind: str,
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        """Reset counters after a memory and/or skill review pass.

        kind: memory | skill | both
        force: allow mark even if not due (e.g. after user correction trigger).
        """
        kind = (kind or "").strip().lower()
        if kind not in ("memory", "skill", "both"):
            return {
                "success": False,
                "error": "kind must be memory|skill|both",
            }
        status_before = self.loop_status()
        if not force:
            if kind == "memory" and not status_before["memory_due"]:
                return {
                    "success": False,
                    "error": "memory review not due; pass force=true for event triggers",
                    "loop": status_before,
                }
            if kind == "skill" and not status_before["skill_due"]:
                return {
                    "success": False,
                    "error": "skill review not due; pass force=true for event triggers",
                    "loop": status_before,
                }
            if kind == "both" and not status_before["any_due"]:
                return {
                    "success": False,
                    "error": "no review due; pass force=true for event triggers",
                    "loop": status_before,
                }

        state = self._load_loop_state()
        now = _now_iso()
        if kind in ("memory", "both"):
            state["turns_since_memory"] = 0
            state["last_memory_review_at"] = now
        if kind in ("skill", "both"):
            state["turns_since_skill"] = 0
            state["last_skill_review_at"] = now
        state["last_review_kind"] = kind
        self._save_loop_state(state)
        status = self.loop_status()
        status["success"] = True
        status["message"] = f"Marked {kind} review complete."
        status["forced"] = force
        return status

    def loop_reset(self) -> dict[str, Any]:
        """Reset all loop counters (tests / explicit operator action)."""
        state = self._default_loop_state()
        self._save_loop_state(state)
        status = self.loop_status()
        status["success"] = True
        status["message"] = "Loop state reset."
        return status

    # -- threat gate ----------------------------------------------------

    def _threat_block_result(self, content: str, hits: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "success": False,
            "blocked": True,
            "error": (
                "Threat scan blocked this write: content matches injection/exfil/"
                "invisible-Unicode patterns and must not enter always-on memory."
            ),
            "threats": hits,
            "raw_entry": content,
            "note": (
                "Raw entry is returned for inspection only; it was not written to "
                "USER.md / AGENT-MEMORY.md or the frozen snapshot."
            ),
        }

    def _check_content_threats(self, content: str) -> dict[str, Any] | None:
        hits = scan_threats(content)
        if hits:
            return self._threat_block_result(content, hits)
        return None

    # -- pending queue (P2-T3 / P2-T4) ----------------------------------

    def _load_pending_doc(self) -> dict[str, Any]:
        path = self.pending_path()
        if not path.is_file():
            return {"pending": []}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"pending": []}
        if not isinstance(data, dict):
            return {"pending": []}
        items = data.get("pending", [])
        if not isinstance(items, list):
            items = []
        return {"pending": items}

    def _save_pending_doc(self, doc: dict[str, Any]) -> None:
        path = self.pending_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(path)

    def list_pending(self) -> dict[str, Any]:
        doc = self._load_pending_doc()
        return {"success": True, "pending": doc.get("pending", []), "count": len(doc.get("pending", []))}

    def enqueue_pending(
        self,
        *,
        target: str,
        action: str,
        content: str | None = None,
        old_text: str | None = None,
        reason: str = "write_approval",
    ) -> dict[str, Any]:
        doc = self._load_pending_doc()
        item = {
            "id": _new_pending_id(),
            "target": target,
            "action": action,
            "content": content,
            "old_text": old_text,
            "reason": reason,
            "created_at": _now_iso(),
        }
        doc.setdefault("pending", []).append(item)
        self._save_pending_doc(doc)
        return {
            "success": True,
            "pending": True,
            "done": False,
            "message": (
                f"Write queued for approval (id={item['id']}). "
                "Use pending approve/reject. Not applied to disk yet."
            ),
            "item": item,
            "pending_count": len(doc["pending"]),
        }

    def approve_pending(self, item_id: str) -> dict[str, Any]:
        doc = self._load_pending_doc()
        items: list[dict[str, Any]] = list(doc.get("pending", []))
        match = next((i for i in items if i.get("id") == item_id), None)
        if match is None:
            return {
                "success": False,
                "error": f"No pending item with id={item_id!r}.",
                "pending": items,
            }
        # Apply without re-queueing even if write_approval is on.
        action = match.get("action")
        target = match.get("target")
        if target not in TARGET_FILES:
            return {"success": False, "error": f"Invalid target in pending item: {target!r}"}

        if action == "add":
            result = self._apply_add(target, str(match.get("content") or ""))
        elif action == "replace":
            result = self._apply_replace(
                target,
                str(match.get("old_text") or ""),
                str(match.get("content") or ""),
            )
        elif action == "remove":
            result = self._apply_remove(target, str(match.get("old_text") or ""))
        else:
            return {"success": False, "error": f"Unknown pending action {action!r}."}

        if not result.get("success"):
            # Leave item in queue if apply failed (e.g. overflow / no match).
            result["pending_id"] = item_id
            result["note"] = (
                "Approve did not apply; pending item kept for retry after fix."
            )
            return result

        # Remove from queue on successful apply.
        doc["pending"] = [i for i in items if i.get("id") != item_id]
        self._save_pending_doc(doc)
        result["approved_id"] = item_id
        result["pending_count"] = len(doc["pending"])
        result["message"] = (
            f"Pending {item_id} approved and applied. " + result.get("message", "")
        )
        return result

    def reject_pending(self, item_id: str) -> dict[str, Any]:
        doc = self._load_pending_doc()
        items: list[dict[str, Any]] = list(doc.get("pending", []))
        match = next((i for i in items if i.get("id") == item_id), None)
        if match is None:
            return {
                "success": False,
                "error": f"No pending item with id={item_id!r}.",
                "pending": items,
            }
        doc["pending"] = [i for i in items if i.get("id") != item_id]
        self._save_pending_doc(doc)
        return {
            "success": True,
            "done": True,
            "rejected_id": item_id,
            "rejected_item": match,
            "message": f"Pending {item_id} rejected and removed from queue.",
            "pending_count": len(doc["pending"]),
        }

    # -- mutations ------------------------------------------------------

    def add(self, target: str, content: str) -> dict[str, Any]:
        content = content.strip()
        if not content:
            return {"success": False, "error": "Content cannot be empty."}
        if "\n§\n" in content or content.strip() == "§":
            return {
                "success": False,
                "error": "Content must not contain the entry delimiter § as its own line.",
            }

        blocked = self._check_content_threats(content)
        if blocked:
            return blocked

        if self.write_approval:
            # Still reject exact duplicates without queue noise.
            if content in self.entries_for(target):
                return self._success(target, "Entry already exists (no duplicate added).")
            return self.enqueue_pending(
                target=target, action="add", content=content, reason="write_approval"
            )

        return self._apply_add(target, content)

    def _apply_add(self, target: str, content: str) -> dict[str, Any]:
        content = content.strip()
        if not content:
            return {"success": False, "error": "Content cannot be empty."}

        blocked = self._check_content_threats(content)
        if blocked:
            return blocked

        entries = list(self.entries_for(target))
        if content in entries:
            return self._success(target, "Entry already exists (no duplicate added).")

        limit = self.char_limit(target)
        new_entries = entries + [content]
        new_total = len(ENTRY_DELIMITER.join(new_entries))
        if new_total > limit:
            current = self.char_count(target)
            return {
                "success": False,
                "error": (
                    f"Memory at {current:,}/{limit:,} chars. "
                    f"Adding this entry ({len(content)} chars) would exceed the limit. "
                    "Consolidate now: use 'replace' to merge overlapping entries into "
                    "shorter ones or 'remove' stale or less important entries (see "
                    "current_entries below), then retry this add — all in this turn."
                ),
                "current_entries": entries,
                "usage": f"{current:,}/{limit:,}",
            }

        entries.append(content)
        self.set_entries(target, entries)
        self.save(target)
        return self._success(target, "Entry added.")

    def replace(self, target: str, old_text: str, content: str) -> dict[str, Any]:
        old_text = old_text.strip()
        content = content.strip()
        if not old_text:
            return {"success": False, "error": "old_text cannot be empty."}
        if not content:
            return {
                "success": False,
                "error": "content cannot be empty. Use 'remove' to delete entries.",
            }
        if "\n§\n" in content:
            return {
                "success": False,
                "error": "Content must not contain the entry delimiter § as its own line.",
            }

        blocked = self._check_content_threats(content)
        if blocked:
            return blocked

        if self.write_approval:
            return self.enqueue_pending(
                target=target,
                action="replace",
                content=content,
                old_text=old_text,
                reason="write_approval",
            )

        return self._apply_replace(target, old_text, content)

    def _apply_replace(self, target: str, old_text: str, content: str) -> dict[str, Any]:
        old_text = old_text.strip()
        content = content.strip()
        if not old_text:
            return {"success": False, "error": "old_text cannot be empty."}
        if not content:
            return {
                "success": False,
                "error": "content cannot be empty. Use 'remove' to delete entries.",
            }

        blocked = self._check_content_threats(content)
        if blocked:
            return blocked

        entries = list(self.entries_for(target))
        matches = [(i, e) for i, e in enumerate(entries) if old_text in e]
        if not matches:
            return {
                "success": False,
                "error": (
                    f"No entry matched {old_text!r}. Check current_entries below "
                    "and retry with a unique substring of the entry to replace."
                ),
                "current_entries": entries,
            }
        if len(matches) > 1:
            unique = {e for _, e in matches}
            if len(unique) > 1:
                return {
                    "success": False,
                    "error": f"Multiple entries matched {old_text!r}. Be more specific.",
                    "matches": [e[:80] + ("..." if len(e) > 80 else "") for _, e in matches],
                }

        idx = matches[0][0]
        limit = self.char_limit(target)
        test = entries.copy()
        test[idx] = content
        new_total = len(ENTRY_DELIMITER.join(test))
        if new_total > limit:
            current = self.char_count(target)
            return {
                "success": False,
                "error": (
                    f"Replacement would put memory at {new_total:,}/{limit:,} chars. "
                    "Shorten the new content, or 'remove' other entries to make room "
                    "(see current_entries below), then retry — all in this turn."
                ),
                "current_entries": entries,
                "usage": f"{current:,}/{limit:,}",
            }

        entries[idx] = content
        self.set_entries(target, entries)
        self.save(target)
        return self._success(target, "Entry replaced.")

    def remove(self, target: str, old_text: str) -> dict[str, Any]:
        old_text = old_text.strip()
        if not old_text:
            return {"success": False, "error": "old_text cannot be empty."}

        # remove does not inject content; still gate via approval when enabled.
        if self.write_approval:
            return self.enqueue_pending(
                target=target,
                action="remove",
                old_text=old_text,
                reason="write_approval",
            )

        return self._apply_remove(target, old_text)

    def _apply_remove(self, target: str, old_text: str) -> dict[str, Any]:
        old_text = old_text.strip()
        if not old_text:
            return {"success": False, "error": "old_text cannot be empty."}

        entries = list(self.entries_for(target))
        matches = [(i, e) for i, e in enumerate(entries) if old_text in e]
        if not matches:
            return {
                "success": False,
                "error": (
                    f"No entry matched {old_text!r}. Check current_entries below "
                    "and retry with a unique substring of the entry to remove."
                ),
                "current_entries": entries,
            }
        if len(matches) > 1:
            unique = {e for _, e in matches}
            if len(unique) > 1:
                return {
                    "success": False,
                    "error": f"Multiple entries matched {old_text!r}. Be more specific.",
                    "matches": [e[:80] + ("..." if len(e) > 80 else "") for _, e in matches],
                }

        entries.pop(matches[0][0])
        self.set_entries(target, entries)
        self.save(target)
        return self._success(target, "Entry removed.")

    def _success(self, target: str, message: str) -> dict[str, Any]:
        current = self.char_count(target)
        limit = self.char_limit(target)
        pct = min(100, int((current / limit) * 100)) if limit > 0 else 0
        return {
            "success": True,
            "done": True,
            "target": target,
            "message": message,
            "usage": f"{pct}% — {current:,}/{limit:,} chars",
            "entry_count": len(self.entries_for(target)),
            "note": "Write saved to disk. Frozen session snapshot is unchanged until next load.",
        }


# -- CLI ----------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        default=".",
        help="Project root (default: cwd; walks up for .git/docs)",
    )
    parser.add_argument("--user-limit", type=int, default=None)
    parser.add_argument("--memory-limit", type=int, default=None)
    parser.add_argument(
        "--write-approval",
        choices=("true", "false"),
        default=None,
        help="Override write_approval for this invocation",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("add", "replace", "remove", "render", "status"):
        p = sub.add_parser(name)
        if name != "status":
            p.add_argument(
                "--target",
                required=True,
                choices=("user", "memory"),
                help="user → docs/USER.md; memory → docs/AGENT-MEMORY.md",
            )
        else:
            p.add_argument(
                "--target",
                choices=("user", "memory"),
                default=None,
                help="Optional single store; default both",
            )
        if name == "add":
            p.add_argument("--content", required=True)
        elif name == "replace":
            p.add_argument("--old-text", required=True)
            p.add_argument("--content", required=True)
        elif name == "remove":
            p.add_argument("--old-text", required=True)
        elif name == "render":
            p.add_argument(
                "--frozen",
                action="store_true",
                help="Emit frozen snapshot from last load (not live)",
            )
            p.add_argument(
                "--json",
                action="store_true",
                help="Wrap render text in JSON",
            )

    # pending list | approve | reject
    pend = sub.add_parser("pending", help="List / approve / reject pending writes")
    pend_sub = pend.add_subparsers(dest="pending_cmd", required=True)
    pend_sub.add_parser("list", help="List queued writes")
    ap = pend_sub.add_parser("approve", help="Apply a pending write by id")
    ap.add_argument("--id", required=True, dest="pending_id")
    rj = pend_sub.add_parser("reject", help="Drop a pending write by id")
    rj.add_argument("--id", required=True, dest="pending_id")

    # loop status | tick | mark-reviewed | reset  (Phase 3)
    loop = sub.add_parser("loop", help="Self-learning loop counters / nudges")
    loop_sub = loop.add_subparsers(dest="loop_cmd", required=True)
    loop_sub.add_parser("status", help="Show counters, intervals, due flags")
    tick_p = loop_sub.add_parser("tick", help="Increment turn counters")
    tick_p.add_argument(
        "--n",
        type=int,
        default=1,
        help="Number of user turns to tick (default 1)",
    )
    mark_p = loop_sub.add_parser(
        "mark-reviewed",
        help="Reset counters after a memory/skill review pass",
    )
    mark_p.add_argument(
        "--kind",
        required=True,
        choices=("memory", "skill", "both"),
        help="Which review completed",
    )
    mark_p.add_argument(
        "--force",
        action="store_true",
        help="Allow mark even when not interval-due (event triggers)",
    )
    loop_sub.add_parser("reset", help="Reset all loop counters")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = project_root(args.project)
    wa: bool | None = None
    if args.write_approval is not None:
        wa = args.write_approval == "true"
    store = MemoryStore(
        root,
        user_char_limit=args.user_limit,
        memory_char_limit=args.memory_limit,
        write_approval=wa,
    )
    store.load()

    cmd = args.command
    if cmd == "status":
        return emit(store.status(args.target))

    if cmd == "render":
        text = (
            store.frozen_snapshot(args.target)
            if args.frozen
            else store.render_block(args.target)
        )
        if args.json:
            return emit(
                {
                    "success": True,
                    "target": args.target,
                    "frozen": bool(args.frozen),
                    "text": text,
                }
            )
        sys.stdout.write(text + ("\n" if text and not text.endswith("\n") else ""))
        return 0

    if cmd == "pending":
        if args.pending_cmd == "list":
            return emit(store.list_pending())
        if args.pending_cmd == "approve":
            result = store.approve_pending(args.pending_id)
            return emit(result, code=0 if result.get("success") else 1)
        result = store.reject_pending(args.pending_id)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "loop":
        if args.loop_cmd == "status":
            payload = store.loop_status()
            payload["success"] = True
            return emit(payload)
        if args.loop_cmd == "tick":
            return emit(store.loop_tick(args.n))
        if args.loop_cmd == "mark-reviewed":
            result = store.loop_mark_reviewed(args.kind, force=bool(args.force))
            return emit(result, code=0 if result.get("success") else 1)
        # reset
        return emit(store.loop_reset())

    if cmd == "add":
        result = store.add(args.target, args.content)
    elif cmd == "replace":
        result = store.replace(args.target, args.old_text, args.content)
    else:  # remove
        result = store.remove(args.target, args.old_text)

    # pending enqueue is success=True with pending=True; exit 0
    return emit(result, code=0 if result.get("success") else 1)


if __name__ == "__main__":
    raise SystemExit(main())
