#!/usr/bin/env python3
"""Skill usage telemetry + protected set for SMART / project-memory (Hermes Phase 4).

Sidecar: ``.smart/memory/skill-usage.json`` (per-project).

Tracks views, uses, patches, and agent-created provenance so the self-learning
loop and later curator can improve procedural skills without rotting the library.

Design:
  - Best-effort counters — never raise into the caller path on IO errors.
  - Protected local companions cannot be deleted/archived by agent self-improve.
  - Patch protocol expects a prior ``bump view`` (or force) so agents read first.
  - Content security reuses memory_store.scan_threats for agent-authored text.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import shared threat scanner from sibling module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from memory_store import project_root, scan_threats  # type: ignore
except ImportError:  # pragma: no cover
    project_root = None  # type: ignore
    scan_threats = None  # type: ignore

USAGE_REL = Path(".smart/memory/skill-usage.json")
CONFIG_REL = Path(".smart/memory/config.json")

# Load-bearing local skills — never auto-delete / archive via self-improve.
PROTECTED_BUILTIN_SKILLS: frozenset[str] = frozenset(
    {
        "smart",
        "project-memory",
        "project-planner",
        "step-pilot",
        "code-review",
        "debug-detective",
        "security-check",
    }
)

STATE_ACTIVE = "active"
STATE_STALE = "stale"
STATE_ARCHIVED = "archived"
_VALID_STATES = {STATE_ACTIVE, STATE_STALE, STATE_ARCHIVED}

# Authoring limits (Hermes-adapted for Claude Code skills).
MAX_DESCRIPTION_CHARS = 60
MAX_NAME_CHARS = 64
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$|^[a-z0-9]$")

# Support file roots allowed under agent-created skills.
ALLOWED_SUPPORT_DIRS = frozenset({"references", "templates", "scripts"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def is_protected_builtin(skill_name: str) -> bool:
    return skill_name in PROTECTED_BUILTIN_SKILLS


def _empty_record() -> dict[str, Any]:
    return {
        "created_by": None,  # "agent" | "user" | None
        "use_count": 0,
        "view_count": 0,
        "last_used_at": None,
        "last_viewed_at": None,
        "patch_count": 0,
        "last_patched_at": None,
        "created_at": _now_iso(),
        "state": STATE_ACTIVE,
        "pinned": False,
        "archived_at": None,
    }


def usage_path(root: Path) -> Path:
    return root / USAGE_REL


def load_usage(root: Path) -> dict[str, dict[str, Any]]:
    path = usage_path(root)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    clean: dict[str, dict[str, Any]] = {}
    for k, v in data.items():
        if isinstance(v, dict):
            clean[str(k)] = v
    return clean


def save_usage(root: Path, data: dict[str, dict[str, Any]]) -> None:
    path = usage_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=".skill-usage_", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def get_record(root: Path, skill_name: str) -> dict[str, Any]:
    data = load_usage(root)
    rec = data.get(skill_name)
    base = _empty_record()
    if not isinstance(rec, dict):
        return base
    for k, v in base.items():
        rec.setdefault(k, v)
    return rec


def _mutate(root: Path, skill_name: str, mutator) -> dict[str, Any]:
    data = load_usage(root)
    rec = data.get(skill_name)
    if not isinstance(rec, dict):
        rec = _empty_record()
    else:
        base = _empty_record()
        for k, v in base.items():
            rec.setdefault(k, v)
    mutator(rec)
    data[skill_name] = rec
    save_usage(root, data)
    return rec


def bump_view(root: Path, skill_name: str) -> dict[str, Any]:
    def apply(rec: dict[str, Any]) -> None:
        rec["view_count"] = int(rec.get("view_count") or 0) + 1
        rec["last_viewed_at"] = _now_iso()

    rec = _mutate(root, skill_name, apply)
    return {"success": True, "skill": skill_name, "action": "view", "record": rec}


def bump_use(root: Path, skill_name: str) -> dict[str, Any]:
    def apply(rec: dict[str, Any]) -> None:
        rec["use_count"] = int(rec.get("use_count") or 0) + 1
        rec["last_used_at"] = _now_iso()

    rec = _mutate(root, skill_name, apply)
    return {"success": True, "skill": skill_name, "action": "use", "record": rec}


def bump_patch(root: Path, skill_name: str, *, force: bool = False) -> dict[str, Any]:
    """Record a patch. Requires prior view unless force=True (P4-T7)."""
    if is_protected_builtin(skill_name) and not force:
        # Protected skills may receive careful pitfall patches with force after read,
        # but default path still requires view. Deletion is always blocked elsewhere.
        pass
    rec = get_record(root, skill_name)
    views = int(rec.get("view_count") or 0)
    if views < 1 and not force:
        return {
            "success": False,
            "error": (
                f"Patch of '{skill_name}' requires a prior skill view "
                "(bump view / skill_view). Pass --force only after explicit read."
            ),
            "skill": skill_name,
            "view_count": views,
        }

    def apply(r: dict[str, Any]) -> None:
        r["patch_count"] = int(r.get("patch_count") or 0) + 1
        r["last_patched_at"] = _now_iso()

    new_rec = _mutate(root, skill_name, apply)
    return {
        "success": True,
        "skill": skill_name,
        "action": "patch",
        "forced": force,
        "record": new_rec,
    }


def mark_agent_created(root: Path, skill_name: str) -> dict[str, Any]:
    if is_protected_builtin(skill_name):
        return {
            "success": False,
            "error": f"Cannot mark protected builtin '{skill_name}' as agent-created.",
            "skill": skill_name,
        }

    def apply(rec: dict[str, Any]) -> None:
        rec["created_by"] = "agent"
        if not rec.get("created_at"):
            rec["created_at"] = _now_iso()

    rec = _mutate(root, skill_name, apply)
    return {
        "success": True,
        "skill": skill_name,
        "action": "mark_agent_created",
        "record": rec,
    }


def assert_can_delete(skill_name: str) -> dict[str, Any]:
    if is_protected_builtin(skill_name):
        return {
            "success": False,
            "error": (
                f"Protected skill '{skill_name}' must not be deleted or auto-archived "
                "by self-improve/curator. Core local companions are permanent."
            ),
            "protected": True,
            "skill": skill_name,
        }
    return {"success": True, "skill": skill_name, "protected": False}


def assert_can_archive(skill_name: str) -> dict[str, Any]:
    """Same protection gate as delete — archive is the max destructive action."""
    return assert_can_delete(skill_name)


def _parse_iso_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def latest_activity_at(record: dict[str, Any]) -> str | None:
    """Newest use/view/patch timestamp. Creation time is intentionally excluded."""
    latest_dt: datetime | None = None
    latest_raw: str | None = None
    for key in ("last_used_at", "last_viewed_at", "last_patched_at"):
        raw = record.get(key)
        dt = _parse_iso_timestamp(raw)
        if dt is None:
            continue
        if latest_dt is None or dt > latest_dt:
            latest_dt = dt
            latest_raw = str(raw)
    return latest_raw


def is_agent_created(root: Path, skill_name: str) -> bool:
    rec = get_record(root, skill_name)
    return rec.get("created_by") == "agent"


def set_state(root: Path, skill_name: str, state: str) -> dict[str, Any]:
    if state not in _VALID_STATES:
        return {
            "success": False,
            "error": f"invalid state {state!r}; expected one of {sorted(_VALID_STATES)}",
            "skill": skill_name,
        }
    if is_protected_builtin(skill_name) and state == STATE_ARCHIVED:
        gate = assert_can_archive(skill_name)
        return {**gate, "action": "set_state"}

    def apply(rec: dict[str, Any]) -> None:
        rec["state"] = state
        if state == STATE_ARCHIVED:
            rec["archived_at"] = _now_iso()
        elif state == STATE_ACTIVE:
            rec["archived_at"] = None

    rec = _mutate(root, skill_name, apply)
    return {
        "success": True,
        "skill": skill_name,
        "action": "set_state",
        "state": state,
        "record": rec,
    }


def set_pinned(root: Path, skill_name: str, pinned: bool) -> dict[str, Any]:
    def apply(rec: dict[str, Any]) -> None:
        rec["pinned"] = bool(pinned)

    rec = _mutate(root, skill_name, apply)
    return {
        "success": True,
        "skill": skill_name,
        "action": "set_pinned",
        "pinned": bool(pinned),
        "record": rec,
    }


def agent_created_report(root: Path) -> list[dict[str, Any]]:
    """Rows for curator: agent-created skills only, with derived activity."""
    data = load_usage(root)
    rows: list[dict[str, Any]] = []
    for name, raw in sorted(data.items()):
        if not isinstance(raw, dict):
            continue
        if raw.get("created_by") != "agent":
            continue
        if is_protected_builtin(name):
            continue
        rec = get_record(root, name)
        row = dict(rec)
        row["name"] = name
        row["last_activity_at"] = latest_activity_at(rec)
        row["protected"] = False
        rows.append(row)
    return rows


def status(root: Path, skill_name: str | None = None) -> dict[str, Any]:
    data = load_usage(root)
    if skill_name:
        rec = get_record(root, skill_name)
        return {
            "success": True,
            "skill": skill_name,
            "protected": is_protected_builtin(skill_name),
            "record": rec,
            "last_activity_at": latest_activity_at(rec),
            "path": str(USAGE_REL),
        }
    agent_rows = agent_created_report(root)
    return {
        "success": True,
        "count": len(data),
        "agent_created_count": len(agent_rows),
        "skills": data,
        "protected": sorted(PROTECTED_BUILTIN_SKILLS),
        "path": str(USAGE_REL),
    }


# -- Authoring / security helpers (protocol tooling) -----------------------


def validate_skill_name(name: str) -> list[str]:
    errors: list[str] = []
    if not name:
        errors.append("name is required")
        return errors
    if len(name) > MAX_NAME_CHARS:
        errors.append(f"name must be <= {MAX_NAME_CHARS} chars")
    if not _NAME_RE.match(name) and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name):
        errors.append("name must be lowercase-hyphenated (a-z0-9-)")
    if is_protected_builtin(name):
        errors.append(f"name '{name}' collides with a protected builtin")
    return errors


def validate_description(description: str) -> list[str]:
    errors: list[str] = []
    d = (description or "").strip()
    if not d:
        errors.append("description is required")
        return errors
    if len(d) > MAX_DESCRIPTION_CHARS:
        errors.append(
            f"description must be <= {MAX_DESCRIPTION_CHARS} characters "
            f"(got {len(d)}); skill indexes truncate past this limit"
        )
    if not d.endswith("."):
        errors.append("description should end with a period")
    marketing = ("powerful", "comprehensive", "seamless", "advanced", "robust")
    low = d.lower()
    for word in marketing:
        if word in low:
            errors.append(f"description avoids marketing word '{word}'")
            break
    return errors


def validate_frontmatter_fields(name: str, description: str) -> dict[str, Any]:
    errors = validate_skill_name(name) + validate_description(description)
    return {
        "success": len(errors) == 0,
        "errors": errors,
        "name": name,
        "description": description,
        "description_len": len((description or "").strip()),
        "max_description": MAX_DESCRIPTION_CHARS,
    }


def validate_support_path(file_path: str) -> dict[str, Any]:
    """Ensure write_file targets references/|templates/|scripts/ or SKILL.md."""
    raw = (file_path or "").replace("\\", "/").lstrip("/")
    if not raw or ".." in raw.split("/"):
        return {"success": False, "error": "invalid path (empty or traversal)"}
    if raw == "SKILL.md" or raw.endswith("/SKILL.md"):
        return {"success": True, "kind": "skill_md", "path": raw}
    top = raw.split("/", 1)[0]
    if top not in ALLOWED_SUPPORT_DIRS:
        return {
            "success": False,
            "error": (
                f"support files must live under references/, templates/, or scripts/ "
                f"(got {raw!r})"
            ),
            "path": raw,
        }
    return {"success": True, "kind": top, "path": raw}


def scan_skill_content(content: str) -> dict[str, Any]:
    """Security scan for agent-created skill text (P4-T5)."""
    if scan_threats is None:
        return {"success": False, "error": "scan_threats unavailable"}
    hits = scan_threats(content)
    return {
        "success": len(hits) == 0,
        "blocked": len(hits) > 0,
        "threats": hits,
        "note": (
            "Agent-created skills with threat hits must not be activated; "
            "rephrase or quarantine like third-party candidates."
        ),
    }


def check_create(
    name: str,
    description: str,
    content: str = "",
) -> dict[str, Any]:
    """Combined create gate: name/description + optional content threat scan."""
    fm = validate_frontmatter_fields(name, description)
    threats: list[dict[str, str]] = []
    if content and scan_threats is not None:
        threats = scan_threats(content)
    ok = fm["success"] and not threats
    return {
        "success": ok,
        "frontmatter": fm,
        "threats": threats,
        "blocked": bool(threats),
        "protected_collision": is_protected_builtin(name),
    }


# -- CLI -------------------------------------------------------------------


def emit(payload: dict[str, Any], *, code: int = 0) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return code


def _resolve_root(start: str) -> Path:
    if project_root is not None:
        return project_root(start)
    return Path(start).resolve()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".", help="Project root")
    sub = p.add_subparsers(dest="command", required=True)

    st = sub.add_parser("status", help="Show usage map or one skill")
    st.add_argument("--skill", default=None)

    bump = sub.add_parser("bump", help="Bump view|use|patch counter")
    bump.add_argument("--skill", required=True)
    bump.add_argument(
        "--kind",
        required=True,
        choices=("view", "use", "patch"),
    )
    bump.add_argument(
        "--force",
        action="store_true",
        help="For patch: allow without prior view",
    )

    mk = sub.add_parser("mark-created", help="Mark skill as agent-created")
    mk.add_argument("--skill", required=True)

    can = sub.add_parser("can-delete", help="Check if skill may be deleted")
    can.add_argument("--skill", required=True)

    ca = sub.add_parser("can-archive", help="Check if skill may be archived")
    ca.add_argument("--skill", required=True)

    ss = sub.add_parser("set-state", help="Set lifecycle state active|stale|archived")
    ss.add_argument("--skill", required=True)
    ss.add_argument("--state", required=True, choices=sorted(_VALID_STATES))

    pin = sub.add_parser("set-pinned", help="Pin or unpin skill (opt out of auto transitions)")
    pin.add_argument("--skill", required=True)
    pin.add_argument(
        "--pinned",
        required=True,
        choices=("true", "false", "1", "0", "yes", "no"),
    )

    lac = sub.add_parser(
        "list-agent-created",
        help="List agent-created skills eligible for curator",
    )

    chk = sub.add_parser("check-create", help="Validate name/description/content")
    chk.add_argument("--name", required=True)
    chk.add_argument("--description", required=True)
    chk.add_argument("--content", default="")

    scan = sub.add_parser("scan-content", help="Threat-scan skill body text")
    scan.add_argument("--content", required=True)

    sp = sub.add_parser("check-path", help="Validate support file path")
    sp.add_argument("--path", required=True)

    return p


def _parse_bool(raw: str) -> bool:
    return str(raw).strip().lower() in {"1", "true", "yes", "on", "y"}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _resolve_root(args.project)
    cmd = args.command

    if cmd == "status":
        return emit(status(root, args.skill))

    if cmd == "bump":
        if args.kind == "view":
            return emit(bump_view(root, args.skill))
        if args.kind == "use":
            return emit(bump_use(root, args.skill))
        result = bump_patch(root, args.skill, force=bool(args.force))
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "mark-created":
        result = mark_agent_created(root, args.skill)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "can-delete":
        result = assert_can_delete(args.skill)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "can-archive":
        result = assert_can_archive(args.skill)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "set-state":
        result = set_state(root, args.skill, args.state)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "set-pinned":
        result = set_pinned(root, args.skill, _parse_bool(args.pinned))
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "list-agent-created":
        rows = agent_created_report(root)
        return emit({"success": True, "count": len(rows), "skills": rows})

    if cmd == "check-create":
        result = check_create(args.name, args.description, args.content)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "scan-content":
        result = scan_skill_content(args.content)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "check-path":
        result = validate_support_path(args.path)
        return emit(result, code=0 if result.get("success") else 1)

    return emit({"success": False, "error": f"unknown command {cmd}"}, code=1)


if __name__ == "__main__":
    raise SystemExit(main())
