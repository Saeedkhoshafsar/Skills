#!/usr/bin/env python3
"""Skill library curator — lifecycle hygiene for SMART / project-memory (Hermes Phase 5).

Deterministic inactivity transitions + archive/restore. Optional consolidate
(LLM umbrella-building) is OFF by default and protocol-documented only.

Sidecars:
  .smart/memory/skill-usage.json   — per-skill telemetry / state (skill_usage.py)
  .smart/memory/curator-state.json — last run, paused, counters
  .smart/memory/config.json        — optional curator.* overrides
  .smart/skills-archive/<skill>/   — recoverable archives (never delete)

Strict invariants (Hermes parity, SMART paths):
  - Only agent-created skills (created_by=agent) are auto-transitioned.
  - Never auto-delete — archive only.
  - Pinned skills bypass all auto-transitions.
  - Protected builtins never archive / never mark agent-created.
  - consolidate defaults OFF; dry-run default for any opinionated pass.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from memory_store import project_root  # type: ignore
except ImportError:  # pragma: no cover
    project_root = None  # type: ignore

import skill_usage as su  # type: ignore

CURATOR_STATE_REL = Path(".smart/memory/curator-state.json")
CONFIG_REL = Path(".smart/memory/config.json")
ARCHIVE_REL = Path(".smart/skills-archive")

# Defaults match Hermes curator.py
DEFAULT_STALE_AFTER_DAYS = 30
DEFAULT_ARCHIVE_AFTER_DAYS = 90
DEFAULT_INTERVAL_HOURS = 24 * 7  # 7 days
DEFAULT_MIN_IDLE_HOURS = 2.0
DEFAULT_CONSOLIDATE = False
DEFAULT_ENABLED = True

# Project-local skill roots the curator may move when archiving.
# First match wins; missing skill dir → state-only archive (telemetry still updates).
DEFAULT_SKILL_SEARCH_DIRS = (
    Path(".claude/skills"),
    Path("skills"),
    Path(".smart/skills"),
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().replace(microsecond=0).isoformat()


def _parse_iso(ts: Any) -> datetime | None:
    if not ts:
        return None
    try:
        parsed = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


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


def _curator_cfg(root: Path) -> dict[str, Any]:
    cfg = load_config(root)
    cur = cfg.get("curator")
    if isinstance(cur, dict):
        return cur
    # Flat keys also accepted for simple configs.
    return {
        k: cfg[k]
        for k in (
            "stale_after_days",
            "archive_after_days",
            "interval_hours",
            "min_idle_hours",
            "consolidate",
            "enabled",
            "skill_search_dirs",
        )
        if k in cfg
    }


def get_stale_after_days(root: Path) -> int:
    cur = _curator_cfg(root)
    try:
        return int(cur.get("stale_after_days", DEFAULT_STALE_AFTER_DAYS))
    except (TypeError, ValueError):
        return DEFAULT_STALE_AFTER_DAYS


def get_archive_after_days(root: Path) -> int:
    cur = _curator_cfg(root)
    try:
        return int(cur.get("archive_after_days", DEFAULT_ARCHIVE_AFTER_DAYS))
    except (TypeError, ValueError):
        return DEFAULT_ARCHIVE_AFTER_DAYS


def get_interval_hours(root: Path) -> int:
    cur = _curator_cfg(root)
    try:
        return int(cur.get("interval_hours", DEFAULT_INTERVAL_HOURS))
    except (TypeError, ValueError):
        return DEFAULT_INTERVAL_HOURS


def get_min_idle_hours(root: Path) -> float:
    cur = _curator_cfg(root)
    try:
        return float(cur.get("min_idle_hours", DEFAULT_MIN_IDLE_HOURS))
    except (TypeError, ValueError):
        return DEFAULT_MIN_IDLE_HOURS


def get_consolidate(root: Path) -> bool:
    cur = _curator_cfg(root)
    return bool(cur.get("consolidate", DEFAULT_CONSOLIDATE))


def is_enabled(root: Path) -> bool:
    cur = _curator_cfg(root)
    return bool(cur.get("enabled", DEFAULT_ENABLED))


def skill_search_dirs(root: Path) -> list[Path]:
    cur = _curator_cfg(root)
    raw = cur.get("skill_search_dirs")
    if isinstance(raw, list) and raw:
        return [root / Path(str(p)) for p in raw]
    return [root / p for p in DEFAULT_SKILL_SEARCH_DIRS]


def archive_root(root: Path) -> Path:
    return root / ARCHIVE_REL


def curator_state_path(root: Path) -> Path:
    return root / CURATOR_STATE_REL


def _default_state() -> dict[str, Any]:
    return {
        "last_run_at": None,
        "last_run_duration_seconds": None,
        "last_run_summary": None,
        "paused": False,
        "run_count": 0,
        "last_counts": None,
    }


def load_state(root: Path) -> dict[str, Any]:
    path = curator_state_path(root)
    base = _default_state()
    if not path.is_file():
        return base
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return base
    if not isinstance(data, dict):
        return base
    base.update({k: v for k, v in data.items() if k in base or k.startswith("_")})
    return base


def save_state(root: Path, data: dict[str, Any]) -> None:
    path = curator_state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=".curator-state_", suffix=".tmp"
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


def set_paused(root: Path, paused: bool) -> dict[str, Any]:
    state = load_state(root)
    state["paused"] = bool(paused)
    save_state(root, state)
    return {"success": True, "paused": bool(paused), "path": str(CURATOR_STATE_REL)}


def is_paused(root: Path) -> bool:
    return bool(load_state(root).get("paused"))


def find_skill_dir(root: Path, skill_name: str) -> Path | None:
    """Locate a skill directory by name under configured search roots."""
    for base in skill_search_dirs(root):
        if not base.is_dir():
            continue
        # Flat: base/<skill>/SKILL.md
        direct = base / skill_name
        if (direct / "SKILL.md").is_file() or direct.is_dir():
            return direct
        # Nested plugin layout: base/<plugin>/skills/<skill>/
        for plugin in base.iterdir():
            if not plugin.is_dir():
                continue
            nested = plugin / "skills" / skill_name
            if (nested / "SKILL.md").is_file() or nested.is_dir():
                return nested
            # Also base/<skill>/skills/<skill>/
            nested2 = plugin / skill_name
            if plugin.name == skill_name and (
                (nested2 / "SKILL.md").is_file() or (plugin / "SKILL.md").is_file()
            ):
                if (plugin / "SKILL.md").is_file():
                    return plugin
    return None


def list_archived(root: Path) -> list[str]:
    ar = archive_root(root)
    if not ar.is_dir():
        return []
    return sorted({p.name for p in ar.iterdir() if p.is_dir()})


def archive_skill(root: Path, skill_name: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Move skill dir to .smart/skills-archive/ and set state=archived.

    Never deletes. Protected builtins refused. Missing on-disk skill still marks
    usage state archived (state-only) so telemetry stays consistent.
    """
    gate = su.assert_can_archive(skill_name)
    if not gate.get("success"):
        return {**gate, "action": "archive"}

    if su.is_protected_builtin(skill_name):
        return {
            "success": False,
            "error": f"Protected skill '{skill_name}' is never archived.",
            "protected": True,
            "skill": skill_name,
            "action": "archive",
        }

    src = find_skill_dir(root, skill_name)
    dest_parent = archive_root(root)
    dest: Path | None = None
    moved = False
    state_only = src is None

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "skill": skill_name,
            "action": "archive",
            "would_move": str(src) if src else None,
            "archive_root": str(ARCHIVE_REL),
            "state_only": state_only,
        }

    if src is not None and src.exists():
        dest_parent.mkdir(parents=True, exist_ok=True)
        dest = dest_parent / skill_name
        if dest.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            dest = dest_parent / f"{skill_name}-{stamp}"
        try:
            shutil.move(str(src), str(dest))
            moved = True
        except OSError as e:
            return {
                "success": False,
                "error": f"failed to archive: {e}",
                "skill": skill_name,
                "action": "archive",
            }

    state_result = su.set_state(root, skill_name, su.STATE_ARCHIVED)
    if not state_result.get("success"):
        return state_result

    return {
        "success": True,
        "skill": skill_name,
        "action": "archive",
        "moved": moved,
        "state_only": state_only,
        "source": str(src) if src else None,
        "destination": str(dest) if dest else None,
        "archive_root": str(ARCHIVE_REL),
        "record": state_result.get("record"),
    }


def restore_skill(root: Path, skill_name: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Restore from .smart/skills-archive/ into .claude/skills/<name>/ by default."""
    ar = archive_root(root)
    if not ar.is_dir():
        return {
            "success": False,
            "error": "no archive directory",
            "skill": skill_name,
            "action": "restore",
        }

    candidates = [p for p in ar.rglob("*") if p.is_dir() and p.name == skill_name]
    if not candidates:
        # Timestamp-disambiguated names: skill-YYYYMMDDHHMMSS
        candidates = [
            p
            for p in ar.iterdir()
            if p.is_dir()
            and (
                p.name == skill_name
                or (
                    p.name.startswith(f"{skill_name}-")
                    and len(p.name) > len(skill_name) + 1
                    and p.name[len(skill_name) + 1 :].isdigit()
                )
            )
        ]
    if not candidates:
        return {
            "success": False,
            "error": f"skill '{skill_name}' not found in archive",
            "skill": skill_name,
            "action": "restore",
        }

    src = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    dest_base = skill_search_dirs(root)[0]
    dest = dest_base / skill_name

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "skill": skill_name,
            "action": "restore",
            "would_move_from": str(src),
            "would_move_to": str(dest),
        }

    if dest.exists():
        return {
            "success": False,
            "error": f"destination already exists: {dest}",
            "skill": skill_name,
            "action": "restore",
        }

    dest_base.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(src), str(dest))
    except OSError as e:
        return {
            "success": False,
            "error": f"failed to restore: {e}",
            "skill": skill_name,
            "action": "restore",
        }

    state_result = su.set_state(root, skill_name, su.STATE_ACTIVE)
    return {
        "success": True,
        "skill": skill_name,
        "action": "restore",
        "source": str(src),
        "destination": str(dest),
        "record": state_result.get("record"),
    }


def apply_automatic_transitions(
    root: Path,
    *,
    now: datetime | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Walk agent-created skills; active → stale → archived by inactivity.

    Pinned and protected skills are never touched. Never deletes.
    """
    if now is None:
        now = _now()
    stale_days = get_stale_after_days(root)
    archive_days = get_archive_after_days(root)
    stale_cutoff = now - timedelta(days=stale_days)
    archive_cutoff = now - timedelta(days=archive_days)

    counts = {
        "marked_stale": 0,
        "archived": 0,
        "reactivated": 0,
        "checked": 0,
        "skipped_pinned": 0,
        "skipped_protected": 0,
    }
    details: list[dict[str, Any]] = []

    for row in su.agent_created_report(root):
        counts["checked"] += 1
        name = row["name"]

        if su.is_protected_builtin(name):
            counts["skipped_protected"] += 1
            continue
        if row.get("pinned"):
            counts["skipped_pinned"] += 1
            continue

        last_activity = _parse_iso(row.get("last_activity_at"))
        anchor = last_activity or _parse_iso(row.get("created_at")) or now
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=timezone.utc)

        current = row.get("state") or su.STATE_ACTIVE
        never_used = int(row.get("use_count") or 0) == 0

        # Never-used grace: younger than stale window → leave alone / unstale.
        if never_used and anchor > stale_cutoff:
            if current == su.STATE_STALE:
                if not dry_run:
                    su.set_state(root, name, su.STATE_ACTIVE)
                counts["reactivated"] += 1
                details.append({"skill": name, "action": "reactivate", "reason": "never_used_grace"})
            continue

        if anchor <= archive_cutoff and current != su.STATE_ARCHIVED:
            if dry_run:
                counts["archived"] += 1
                details.append(
                    {
                        "skill": name,
                        "action": "would_archive",
                        "anchor": anchor.isoformat(),
                    }
                )
            else:
                result = archive_skill(root, name, dry_run=False)
                if result.get("success"):
                    counts["archived"] += 1
                    details.append({"skill": name, "action": "archive", "result": result})
        elif anchor <= stale_cutoff and current == su.STATE_ACTIVE:
            if not dry_run:
                su.set_state(root, name, su.STATE_STALE)
            counts["marked_stale"] += 1
            details.append({"skill": name, "action": "mark_stale", "anchor": anchor.isoformat()})
        elif anchor > stale_cutoff and current == su.STATE_STALE:
            if not dry_run:
                su.set_state(root, name, su.STATE_ACTIVE)
            counts["reactivated"] += 1
            details.append({"skill": name, "action": "reactivate", "reason": "recent_activity"})

    return {
        "success": True,
        "dry_run": dry_run,
        "stale_after_days": stale_days,
        "archive_after_days": archive_days,
        "counts": counts,
        "details": details,
        "consolidate": get_consolidate(root),
        "note": (
            "Optional LLM consolidate pass is OFF by default. "
            "Set curator.consolidate=true only when explicitly enabled; "
            "this CLI never spawns a model."
            if not get_consolidate(root)
            else "consolidate=true in config — run umbrella review protocol separately (no auto-delete)."
        ),
    }


def should_run_now(
    root: Path,
    *,
    now: datetime | None = None,
    idle_for_seconds: float | None = None,
) -> dict[str, Any]:
    """Whether idle-triggered curator should fire (protocol helper)."""
    if now is None:
        now = _now()
    reasons: list[str] = []
    enabled = is_enabled(root)
    paused = is_paused(root)
    if not enabled:
        return {"should_run": False, "reason": "disabled", "enabled": False}
    if paused:
        return {"should_run": False, "reason": "paused", "paused": True}

    state = load_state(root)
    last = _parse_iso(state.get("last_run_at"))
    interval_h = get_interval_hours(root)
    min_idle_h = get_min_idle_hours(root)

    if last is not None:
        elapsed_h = (now - last).total_seconds() / 3600.0
        if elapsed_h < interval_h:
            return {
                "should_run": False,
                "reason": "interval_not_elapsed",
                "hours_since_last": round(elapsed_h, 3),
                "interval_hours": interval_h,
            }
    else:
        reasons.append("never_run")

    if idle_for_seconds is not None:
        min_idle_s = min_idle_h * 3600.0
        if idle_for_seconds < min_idle_s:
            return {
                "should_run": False,
                "reason": "not_idle_enough",
                "idle_for_seconds": idle_for_seconds,
                "min_idle_hours": min_idle_h,
            }
        reasons.append("idle_ok")
    else:
        reasons.append("idle_unchecked")

    return {
        "should_run": True,
        "reason": ",".join(reasons) or "due",
        "interval_hours": interval_h,
        "min_idle_hours": min_idle_h,
        "last_run_at": state.get("last_run_at"),
    }


def run_curator(
    root: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
    idle_for_seconds: float | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Run automatic transitions; record curator-state. No LLM."""
    if now is None:
        now = _now()
    started = now

    gate = should_run_now(root, now=now, idle_for_seconds=idle_for_seconds)
    if not force and not gate.get("should_run"):
        return {
            "success": True,
            "ran": False,
            "gate": gate,
            "message": f"curator skipped: {gate.get('reason')}",
        }

    if not is_enabled(root) and not force:
        return {
            "success": True,
            "ran": False,
            "message": "curator disabled",
            "gate": gate,
        }

    transitions = apply_automatic_transitions(root, now=now, dry_run=dry_run)
    duration = (_now() - started).total_seconds()

    summary = (
        f"checked={transitions['counts']['checked']} "
        f"stale={transitions['counts']['marked_stale']} "
        f"archived={transitions['counts']['archived']} "
        f"reactivated={transitions['counts']['reactivated']}"
    )

    if not dry_run:
        state = load_state(root)
        state["last_run_at"] = _now_iso()
        state["last_run_duration_seconds"] = round(duration, 3)
        state["last_run_summary"] = summary
        state["run_count"] = int(state.get("run_count") or 0) + 1
        state["last_counts"] = transitions["counts"]
        save_state(root, state)

    return {
        "success": True,
        "ran": True,
        "dry_run": dry_run,
        "forced": force,
        "summary": summary,
        "transitions": transitions,
        "gate": gate,
        "consolidate_enabled": get_consolidate(root),
        "archive_path": str(ARCHIVE_REL),
        "protected": sorted(su.PROTECTED_BUILTIN_SKILLS),
    }


def status(root: Path) -> dict[str, Any]:
    state = load_state(root)
    rows = su.agent_created_report(root)
    by_state: dict[str, int] = {}
    pinned = 0
    for r in rows:
        st = r.get("state") or su.STATE_ACTIVE
        by_state[st] = by_state.get(st, 0) + 1
        if r.get("pinned"):
            pinned += 1
    return {
        "success": True,
        "enabled": is_enabled(root),
        "paused": is_paused(root),
        "state": state,
        "config": {
            "stale_after_days": get_stale_after_days(root),
            "archive_after_days": get_archive_after_days(root),
            "interval_hours": get_interval_hours(root),
            "min_idle_hours": get_min_idle_hours(root),
            "consolidate": get_consolidate(root),
        },
        "agent_created_count": len(rows),
        "by_state": by_state,
        "pinned_count": pinned,
        "archived_on_disk": list_archived(root),
        "archive_path": str(ARCHIVE_REL),
        "protected": sorted(su.PROTECTED_BUILTIN_SKILLS),
        "should_run": should_run_now(root),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default=".", help="Project root")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Curator state + skill lifecycle summary")

    run = sub.add_parser("run", help="Apply automatic lifecycle transitions")
    run.add_argument(
        "--dry-run",
        action="store_true",
        help="Report transitions without mutating",
    )
    run.add_argument(
        "--force",
        action="store_true",
        help="Ignore interval/paused/enabled gates",
    )
    run.add_argument(
        "--idle-seconds",
        type=float,
        default=None,
        help="Seconds the agent has been idle (for should_run gate)",
    )

    trans = sub.add_parser(
        "transitions",
        help="Apply transitions only (no gate / no state stamp unless --stamp)",
    )
    trans.add_argument("--dry-run", action="store_true")
    trans.add_argument(
        "--stamp",
        action="store_true",
        help="Also update curator-state last_run (like run)",
    )

    arch = sub.add_parser("archive", help="Archive one skill (never delete)")
    arch.add_argument("--skill", required=True)
    arch.add_argument("--dry-run", action="store_true")

    rest = sub.add_parser("restore", help="Restore skill from archive")
    rest.add_argument("--skill", required=True)
    rest.add_argument("--dry-run", action="store_true")

    sub.add_parser("list-archived", help="List skills under .smart/skills-archive/")

    pause = sub.add_parser("pause", help="Pause idle curator")
    resume = sub.add_parser("resume", help="Resume idle curator")
    # silence unused
    del pause, resume

    gate = sub.add_parser("should-run", help="Evaluate idle/interval gate")
    gate.add_argument("--idle-seconds", type=float, default=None)

    pin = sub.add_parser("pin", help="Pin skill (opt out of auto transitions)")
    pin.add_argument("--skill", required=True)
    unpin = sub.add_parser("unpin", help="Unpin skill")
    unpin.add_argument("--skill", required=True)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _resolve_root(args.project)
    cmd = args.command

    if cmd == "status":
        return emit(status(root))

    if cmd == "should-run":
        return emit(
            {
                "success": True,
                **should_run_now(root, idle_for_seconds=args.idle_seconds),
            }
        )

    if cmd == "run":
        result = run_curator(
            root,
            dry_run=bool(args.dry_run),
            force=bool(args.force),
            idle_for_seconds=args.idle_seconds,
        )
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "transitions":
        result = apply_automatic_transitions(
            root, dry_run=bool(args.dry_run)
        )
        if args.stamp and not args.dry_run:
            st = load_state(root)
            st["last_run_at"] = _now_iso()
            st["last_run_summary"] = (
                f"transitions-only checked={result['counts']['checked']}"
            )
            st["run_count"] = int(st.get("run_count") or 0) + 1
            st["last_counts"] = result["counts"]
            save_state(root, st)
        return emit(result)

    if cmd == "archive":
        result = archive_skill(root, args.skill, dry_run=bool(args.dry_run))
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "restore":
        result = restore_skill(root, args.skill, dry_run=bool(args.dry_run))
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "list-archived":
        names = list_archived(root)
        return emit(
            {
                "success": True,
                "count": len(names),
                "skills": names,
                "archive_path": str(ARCHIVE_REL),
            }
        )

    if cmd == "pause":
        return emit(set_paused(root, True))

    if cmd == "resume":
        return emit(set_paused(root, False))

    if cmd == "pin":
        result = su.set_pinned(root, args.skill, True)
        return emit(result, code=0 if result.get("success") else 1)

    if cmd == "unpin":
        result = su.set_pinned(root, args.skill, False)
        return emit(result, code=0 if result.get("success") else 1)

    return emit({"success": False, "error": f"unknown command {cmd}"}, code=1)


if __name__ == "__main__":
    raise SystemExit(main())
