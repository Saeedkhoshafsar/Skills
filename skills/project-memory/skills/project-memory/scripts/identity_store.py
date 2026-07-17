#!/usr/bin/env python3
"""Identity, personality presets, and memory dashboard (Hermes Phase 8).

Protocol-level port of Hermes SOUL/identity + light profile isolation:

  - Optional ``docs/SOUL.md`` load order + threat scan + char cap (C-14)
  - Lightweight personality presets (overlay, not full re-identity)
  - Multi-profile **design** (personal vs work) — config-ready, single
    active profile default (C-13 deferred full isolation)
  - Dashboard: memory usage %, pending writes, last review, provider, soul

Does not replace Project Mind / Vision Lock. SOUL is agent tone/identity for
this project; USER.md is who the user is; AGENT-MEMORY is operational lessons.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from memory_store import (  # type: ignore
        MemoryStore,
        load_config,
        project_root,
        scan_threats,
    )
except ImportError:  # pragma: no cover
    MemoryStore = None  # type: ignore
    load_config = None  # type: ignore
    project_root = None  # type: ignore
    scan_threats = None  # type: ignore

try:
    from memory_provider import (  # type: ignore
        resolve_provider_name,
        provider_catalog,
    )
except ImportError:  # pragma: no cover
    resolve_provider_name = None  # type: ignore
    provider_catalog = None  # type: ignore

CONFIG_REL = Path(".smart/memory/config.json")
SOUL_REL = Path("docs/SOUL.md")
PROFILES_REL = Path(".smart/profiles")
DEFAULT_SOUL_CHAR_LIMIT = 4000

# Load order for identity/context (project-local first).
# SMART still prefers STATE2 over STATE for resume; this is identity only.
IDENTITY_LOAD_ORDER = (
    "docs/SOUL.md",  # project agent identity / tone
    "docs/USER.md",  # user profile (who the user is)
    "docs/AGENT-MEMORY.md",  # operational lessons
    # Product truth is separate (Project Mind / BRIEF / STATE) — not identity.
)

DEFAULT_SOUL_TEMPLATE = """# Agent identity (SOUL)

<!--
Optional project-local agent identity and tone.
Loaded after Vision Lock / Project Mind (product truth stays authoritative).
Threat-scanned like learning memory. Keep short and durable.

Examples:
  - "Direct senior engineer. Prefer evidence over ceremony."
  - "Warm mentor for novices; still apply expert defaults silently."
  - "Concise. No fluff. Admit uncertainty."

Delete this file or leave empty to use the host/default personality.
-->

You are a project-local assistant operating under SMART. You are helpful,
knowledgeable, and direct. You prioritize genuine usefulness over verbosity,
admit uncertainty when appropriate, and never override Project Mind, Vision
Lock, or security gates for tone. Be targeted and efficient.
"""

# Lightweight presets (P8-T2). Overlay text only — never wipe SOUL without ask.
PERSONALITY_PRESETS: dict[str, dict[str, str]] = {
    "default": {
        "label": "Default",
        "summary": "Helpful, direct, efficient; expert defaults silently.",
        "overlay": (
            "Be helpful, knowledgeable, and direct. Prefer concise, evidence-based "
            "answers. Apply expert-quality defaults without asking the user quality "
            "trivia. Admit uncertainty."
        ),
    },
    "concise": {
        "label": "Concise",
        "summary": "Minimal words; facts first; no fluff.",
        "overlay": (
            "Be extremely concise. Lead with the answer. Skip filler, throat-clearing, "
            "and optional asides unless the user asks. Prefer bullets over paragraphs."
        ),
    },
    "mentor": {
        "label": "Mentor",
        "summary": "Patient teaching tone; still expert defaults.",
        "overlay": (
            "Teach clearly for mixed expertise. Explain the why briefly when it helps "
            "learning, but still apply professional defaults without dumping ceremony "
            "or asking novices to design the quality bar."
        ),
    },
    "strict": {
        "label": "Strict engineer",
        "summary": "Blunt, correctness-first, low ceremony.",
        "overlay": (
            "Be blunt and correctness-first. Challenge weak assumptions. Refuse "
            "unclear Vision Lock and unverified DONE claims. Minimize process theater."
        ),
    },
    "warm": {
        "label": "Warm collaborator",
        "summary": "Friendly coworker tone; still high quality.",
        "overlay": (
            "Sound like a friendly, capable coworker. Encourage progress, but never "
            "soften security or Vision Lock requirements. Keep reports short."
        ),
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _emit(payload: dict[str, Any], *, code: int = 0) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return code


def _read_config(root: Path) -> dict[str, Any]:
    if load_config is not None:
        try:
            cfg = load_config(root) or {}
            if isinstance(cfg, dict):
                return cfg
        except Exception:
            pass
    path = root / CONFIG_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_config(root: Path, cfg: dict[str, Any]) -> None:
    path = root / CONFIG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _identity_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    ident = cfg.get("identity")
    return dict(ident) if isinstance(ident, dict) else {}


def soul_char_limit(root: Path) -> int:
    cfg = _read_config(root)
    ident = _identity_cfg(cfg)
    if "soul_char_limit" in ident:
        try:
            return max(200, int(ident["soul_char_limit"]))
        except (TypeError, ValueError):
            pass
    mem = cfg.get("memory")
    if isinstance(mem, dict) and "soul_char_limit" in mem:
        try:
            return max(200, int(mem["soul_char_limit"]))
        except (TypeError, ValueError):
            pass
    return DEFAULT_SOUL_CHAR_LIMIT


def active_profile_name(root: Path) -> str:
    """Return active profile id (default: 'default')."""
    cfg = _read_config(root)
    ident = _identity_cfg(cfg)
    name = (
        ident.get("profile")
        or (cfg.get("profile") if isinstance(cfg.get("profile"), str) else None)
        or "default"
    )
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(name).strip()) or "default"
    return cleaned[:64]


def active_personality(root: Path) -> str:
    cfg = _read_config(root)
    ident = _identity_cfg(cfg)
    name = ident.get("personality") or "default"
    key = str(name).strip().lower()
    return key if key in PERSONALITY_PRESETS else "default"


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def truncate_soul(content: str, limit: int) -> tuple[str, bool]:
    if len(content) <= limit:
        return content, False
    head = int(limit * 0.7)
    tail = max(0, limit - head - 80)
    marker = (
        f"\n\n[...truncated SOUL.md: kept {head}+{tail} of {len(content)} chars. "
        f"Trim docs/SOUL.md or raise identity.soul_char_limit...]\n\n"
    )
    if tail:
        return content[:head] + marker + content[-tail:], True
    return content[:limit] + marker, True


# ---------------------------------------------------------------------------
# SOUL load / seed / scan (P8-T1)
# ---------------------------------------------------------------------------


def soul_path(root: Path) -> Path:
    return root / SOUL_REL


def load_soul(
    root: Path,
    *,
    apply_scan: bool = True,
    apply_truncate: bool = True,
) -> dict[str, Any]:
    """Load optional docs/SOUL.md with threat scan + char cap.

    Returns success payload; missing file is success with present=False.
    """
    path = soul_path(root)
    limit = soul_char_limit(root)
    if not path.is_file():
        return {
            "success": True,
            "present": False,
            "path": str(SOUL_REL),
            "chars": 0,
            "limit": limit,
            "content": "",
            "blocked": False,
            "threats": [],
            "truncated": False,
            "load_order": list(IDENTITY_LOAD_ORDER),
        }
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        return {
            "success": False,
            "present": True,
            "path": str(SOUL_REL),
            "error": str(e),
            "limit": limit,
        }
    content = raw.replace("\r\n", "\n").replace("\r", "\n").lstrip("﻿")
    # Strip HTML comment scaffolding for injection (keep file as-is on disk).
    inject = strip_html_comments(content).strip()
    threats: list[dict[str, str]] = []
    blocked = False
    if apply_scan and scan_threats is not None and inject:
        threats = scan_threats(inject)
        if threats:
            blocked = True
            inject = ""
    truncated = False
    if apply_truncate and inject:
        inject, truncated = truncate_soul(inject, limit)
    return {
        "success": True,
        "present": True,
        "path": str(SOUL_REL),
        "chars": len(content),
        "inject_chars": len(inject),
        "limit": limit,
        "content": inject,
        "blocked": blocked,
        "threats": threats,
        "truncated": truncated,
        "load_order": list(IDENTITY_LOAD_ORDER),
        "profile": active_profile_name(root),
        "personality": active_personality(root),
    }


def seed_soul(root: Path, *, force: bool = False) -> dict[str, Any]:
    """Create docs/SOUL.md from template if missing (or force overwrite)."""
    path = soul_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and not force:
        return {
            "success": True,
            "created": False,
            "path": str(SOUL_REL),
            "note": "already exists; pass force to overwrite",
        }
    path.write_text(DEFAULT_SOUL_TEMPLATE, encoding="utf-8")
    return {
        "success": True,
        "created": True,
        "path": str(SOUL_REL),
        "chars": len(DEFAULT_SOUL_TEMPLATE),
    }


def render_identity_block(root: Path) -> dict[str, Any]:
    """Combined identity prompt block: SOUL + personality overlay."""
    soul = load_soul(root)
    preset_key = active_personality(root)
    preset = PERSONALITY_PRESETS[preset_key]
    parts: list[str] = []
    if soul.get("success") and soul.get("content") and not soul.get("blocked"):
        parts.append("## Agent identity (SOUL.md)\n" + soul["content"])
    elif soul.get("blocked"):
        parts.append(
            "## Agent identity (SOUL.md)\n"
            "[BLOCKED by threat scan — fix docs/SOUL.md before using as identity.]"
        )
    parts.append(
        f"## Personality preset: {preset['label']}\n{preset['overlay']}"
    )
    text = "\n\n".join(parts)
    return {
        "success": True,
        "profile": active_profile_name(root),
        "personality": preset_key,
        "soul_present": bool(soul.get("present")),
        "soul_blocked": bool(soul.get("blocked")),
        "chars": len(text),
        "text": text,
        "load_order": list(IDENTITY_LOAD_ORDER),
    }


# ---------------------------------------------------------------------------
# Personality presets (P8-T2)
# ---------------------------------------------------------------------------


def list_personalities() -> list[dict[str, str]]:
    return [
        {"id": k, "label": v["label"], "summary": v["summary"]}
        for k, v in PERSONALITY_PRESETS.items()
    ]


def set_personality(root: Path, name: str) -> dict[str, Any]:
    key = (name or "").strip().lower()
    if key not in PERSONALITY_PRESETS:
        return {
            "success": False,
            "error": f"unknown personality '{name}'",
            "known": list(PERSONALITY_PRESETS.keys()),
        }
    cfg = _read_config(root)
    ident = _identity_cfg(cfg)
    ident["personality"] = key
    cfg["identity"] = ident
    _write_config(root, cfg)
    return {
        "success": True,
        "personality": key,
        "label": PERSONALITY_PRESETS[key]["label"],
        "config": str(CONFIG_REL),
    }


# ---------------------------------------------------------------------------
# Multi-profile design (P8-T3) — light isolation metadata only
# ---------------------------------------------------------------------------


def profile_status(root: Path) -> dict[str, Any]:
    """Describe active profile + isolation design (no full multi-home yet)."""
    active = active_profile_name(root)
    profiles_dir = root / PROFILES_REL
    known: list[str] = []
    if profiles_dir.is_dir():
        known = sorted(
            p.name
            for p in profiles_dir.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        )
    if active not in known:
        known = sorted(set(known) | {active})
    return {
        "success": True,
        "active": active,
        "profiles": known,
        "profiles_dir": str(PROFILES_REL),
        "isolation": {
            "mode": "single-project-default",
            "note": (
                "Full multi-home isolation (personal vs work HERMES-style) is "
                "deferred until multi-project demand. Active profile name is "
                "recorded under identity.profile; optional sidecars may live "
                "under .smart/profiles/<name>/ later."
            ),
            "product_truth": "Project Mind / STATE remain project-scoped, not profile-scoped.",
        },
    }


def set_profile(root: Path, name: str) -> dict[str, Any]:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", (name or "").strip()) or "default"
    cleaned = cleaned[:64]
    cfg = _read_config(root)
    ident = _identity_cfg(cfg)
    ident["profile"] = cleaned
    cfg["identity"] = ident
    _write_config(root, cfg)
    # Ensure placeholder dir for future isolation without migrating stores yet.
    (root / PROFILES_REL / cleaned).mkdir(parents=True, exist_ok=True)
    marker = root / PROFILES_REL / cleaned / "README.md"
    if not marker.is_file():
        marker.write_text(
            f"# Profile: {cleaned}\n\n"
            "Placeholder for future profile-scoped sidecars. "
            "Learning memory (USER/AGENT-MEMORY) remains project-local by default.\n",
            encoding="utf-8",
        )
    return {
        "success": True,
        "profile": cleaned,
        "config": str(CONFIG_REL),
        "path": str(PROFILES_REL / cleaned),
    }


# ---------------------------------------------------------------------------
# Dashboard (P8-T4)
# ---------------------------------------------------------------------------


def dashboard(root: Path) -> dict[str, Any]:
    """Aggregate memory usage %, pending, last review, provider, soul."""
    out: dict[str, Any] = {
        "success": True,
        "generated_at": _now_iso(),
        "root": str(root),
        "profile": active_profile_name(root),
        "personality": active_personality(root),
    }

    # Learning memory stores
    if MemoryStore is not None:
        store = MemoryStore(root)
        try:
            store.load()
        except Exception:
            pass
        st = store.status()
        out["stores"] = st.get("stores", {})
        out["pending_count"] = st.get("pending_count", 0)
        out["write_approval"] = st.get("write_approval", False)
        loop = st.get("loop") or {}
        out["loop"] = {
            "memory_due": loop.get("memory_due"),
            "skill_due": loop.get("skill_due"),
            "turns_since_memory": loop.get("turns_since_memory"),
            "turns_since_skill": loop.get("turns_since_skill"),
            "last_memory_review_at": loop.get("last_memory_review_at"),
            "last_skill_review_at": loop.get("last_skill_review_at"),
            "last_review_kind": loop.get("last_review_kind"),
        }
        # Compact usage summary
        usage = {}
        for key, block in (st.get("stores") or {}).items():
            usage[key] = {
                "pct": int(
                    (block.get("chars", 0) / block.get("limit", 1) * 100)
                    if block.get("limit")
                    else 0
                ),
                "chars": block.get("chars", 0),
                "limit": block.get("limit", 0),
                "entries": block.get("entry_count", 0),
                "blocked": block.get("blocked_count", 0),
            }
        out["usage"] = usage
    else:
        out["stores"] = {}
        out["pending_count"] = 0
        out["loop"] = {}
        out["usage"] = {}

    # Provider
    if resolve_provider_name is not None:
        try:
            out["provider"] = resolve_provider_name(root)
        except Exception:
            out["provider"] = "builtin"
    else:
        out["provider"] = "builtin"

    # SOUL
    soul = load_soul(root)
    out["soul"] = {
        "present": soul.get("present", False),
        "blocked": soul.get("blocked", False),
        "chars": soul.get("chars", 0),
        "limit": soul.get("limit", DEFAULT_SOUL_CHAR_LIMIT),
        "truncated": soul.get("truncated", False),
        "threats": soul.get("threats", []),
    }

    out["identity_load_order"] = list(IDENTITY_LOAD_ORDER)
    out["profile_isolation"] = profile_status(root).get("isolation")
    return out


# ---------------------------------------------------------------------------
# Migration / bootstrap (P8-T6)
# ---------------------------------------------------------------------------


def migrate_learning_memory(
    root: Path,
    *,
    seed_soul_file: bool = False,
    force_soul: bool = False,
) -> dict[str, Any]:
    """Ensure empty USER/AGENT-MEMORY paths exist without ceremony.

    Existing content is never wiped. Creates docs/ if needed and empty
    learning-memory files so status/render work on pre-existing projects.
    """
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    existed: list[str] = []
    for rel in ("docs/USER.md", "docs/AGENT-MEMORY.md"):
        path = root / rel
        if path.is_file():
            existed.append(rel)
        else:
            path.write_text("", encoding="utf-8")
            created.append(rel)

    soul_result: Optional[dict[str, Any]] = None
    if seed_soul_file:
        soul_result = seed_soul(root, force=force_soul)

    # Default config fragment if missing
    cfg_path = root / CONFIG_REL
    cfg_created = False
    if not cfg_path.is_file():
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(
            json.dumps(
                {
                    "memory": {"provider": "builtin"},
                    "identity": {"personality": "default", "profile": "default"},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        cfg_created = True

    return {
        "success": True,
        "created": created,
        "existed": existed,
        "config_created": cfg_created,
        "config_path": str(CONFIG_REL),
        "soul": soul_result,
        "note": (
            "Pre-existing projects keep content; empty USER/AGENT-MEMORY "
            "are ready for add/replace without rediscovery ceremony."
        ),
        "dashboard": dashboard(root),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Identity / personality / memory dashboard (Phase 8)"
    )
    p.add_argument("--project", default=".", help="Project root")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("dashboard", help="Memory + identity status dashboard")
    sub.add_parser("load-order", help="Show identity load order")
    s = sub.add_parser("soul", help="SOUL.md operations")
    s.add_argument(
        "soul_cmd",
        choices=["status", "load", "seed", "render"],
        help="status|load|seed|render",
    )
    s.add_argument("--force", action="store_true", help="Overwrite on seed")

    per = sub.add_parser("personality", help="List or set personality preset")
    per.add_argument("personality_cmd", choices=["list", "get", "set"])
    per.add_argument("--name", default=None)

    pr = sub.add_parser("profile", help="Active profile metadata")
    pr.add_argument("profile_cmd", choices=["status", "set"])
    pr.add_argument("--name", default=None)

    mig = sub.add_parser(
        "migrate",
        help="Bootstrap empty USER/AGENT-MEMORY without ceremony",
    )
    mig.add_argument(
        "--seed-soul",
        action="store_true",
        help="Also create docs/SOUL.md from template if missing",
    )
    mig.add_argument("--force-soul", action="store_true")

    args = p.parse_args(argv)
    root = (
        project_root(args.project)
        if project_root
        else Path(args.project).resolve()
    )

    if args.cmd == "dashboard":
        return _emit(dashboard(root))

    if args.cmd == "load-order":
        return _emit(
            {
                "success": True,
                "load_order": list(IDENTITY_LOAD_ORDER),
                "note": (
                    "SOUL = agent tone; USER = who user is; "
                    "AGENT-MEMORY = ops lessons. Product truth is Project Mind."
                ),
            }
        )

    if args.cmd == "soul":
        if args.soul_cmd == "status":
            data = load_soul(root)
            # Don't dump full content on status unless small
            if data.get("content") and len(data["content"]) > 200:
                data = dict(data)
                data["content_preview"] = data["content"][:200] + "..."
                data.pop("content", None)
            return _emit(data)
        if args.soul_cmd == "load":
            return _emit(load_soul(root))
        if args.soul_cmd == "seed":
            return _emit(seed_soul(root, force=bool(args.force)))
        if args.soul_cmd == "render":
            return _emit(render_identity_block(root))

    if args.cmd == "personality":
        if args.personality_cmd == "list":
            return _emit(
                {
                    "success": True,
                    "active": active_personality(root),
                    "presets": list_personalities(),
                }
            )
        if args.personality_cmd == "get":
            key = active_personality(root)
            return _emit(
                {
                    "success": True,
                    "personality": key,
                    "preset": PERSONALITY_PRESETS[key],
                }
            )
        if args.personality_cmd == "set":
            if not args.name:
                return _emit(
                    {"success": False, "error": "--name required"}, code=1
                )
            result = set_personality(root, args.name)
            return _emit(result, code=0 if result.get("success") else 1)

    if args.cmd == "profile":
        if args.profile_cmd == "status":
            return _emit(profile_status(root))
        if args.profile_cmd == "set":
            if not args.name:
                return _emit(
                    {"success": False, "error": "--name required"}, code=1
                )
            return _emit(set_profile(root, args.name))

    if args.cmd == "migrate":
        return _emit(
            migrate_learning_memory(
                root,
                seed_soul_file=bool(args.seed_soul),
                force_soul=bool(args.force_soul),
            )
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
