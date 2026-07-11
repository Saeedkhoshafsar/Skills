#!/usr/bin/env python3
"""Machine-verifiable Vision, Verify, and Release gates for SMART projects."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_PREFIX = "smart.gate"
DEFAULT_DIR = Path(".smart/evidence")
EVIDENCE_EXCLUDES = (".smart/evidence",)


class GateError(RuntimeError):
    """A fail-closed gate validation error."""


def fail(message: str) -> None:
    raise GateError(message)


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def project_root(start: str | Path = ".") -> Path:
    start_path = Path(start).resolve()
    result = subprocess.run(
        ["git", "-C", str(start_path), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail("SMART gates require a Git worktree")
    return Path(result.stdout.strip()).resolve()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_file(root: Path, value: str, *, must_exist: bool = True) -> tuple[Path, str]:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    if candidate.is_symlink():
        fail(f"symlink evidence is not allowed: {value}")
    resolved = candidate.resolve(strict=must_exist)
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        fail(f"path escapes project root: {value}")
    if must_exist and not resolved.is_file():
        fail(f"required file does not exist: {value}")
    return resolved, relative.as_posix()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"invalid JSON artifact {path}: {error}")
    if not isinstance(value, dict):
        fail(f"artifact must contain a JSON object: {path}")
    return value


def artifact_path(root: Path, value: str | None, name: str) -> Path:
    raw = value or str(DEFAULT_DIR / f"{name}.json")
    path, _ = relative_file(root, raw, must_exist=False)
    return path


def current_commit(root: Path) -> str:
    commit = run_git(root, "rev-parse", "HEAD")
    if len(commit) != 40:
        fail("could not resolve a full current commit SHA")
    return commit


def evidence_ref(root: Path, value: str) -> dict[str, str]:
    path, relative = relative_file(root, value)
    return {"path": relative, "sha256": sha256(path)}


def check_evidence_ref(root: Path, value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        fail(f"{label} evidence reference is malformed")
    path, relative = relative_file(root, str(value["path"]))
    if relative != value["path"] or sha256(path) != value["sha256"]:
        fail(f"{label} evidence changed or moved")


def code_changes_since(root: Path, commit: str) -> list[str]:
    run_git(root, "merge-base", "--is-ancestor", commit, "HEAD")
    changed = run_git(root, "diff", "--name-only", f"{commit}..HEAD")
    return [
        item
        for item in changed.splitlines()
        if item and not any(item == prefix or item.startswith(prefix + "/") for prefix in EVIDENCE_EXCLUDES)
    ]


def vision_confirm(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    brief, brief_relative = relative_file(root, args.brief)
    if not args.confirmed_by.strip():
        fail("--confirmed-by requires an accountable identity")
    payload = {
        "schema": f"{SCHEMA_PREFIX}/vision/v1",
        "status": "CONFIRMED",
        "project_id": args.project_id or root.name,
        "brief_path": brief_relative,
        "brief_sha256": sha256(brief),
        "confirmed_by": args.confirmed_by.strip(),
        "confirmed_at": now(),
    }
    output = artifact_path(root, args.output, "vision-lock")
    atomic_json(output, payload)
    print(f"VISION GATE: CONFIRMED ({output.relative_to(root)})")


def validate_vision(root: Path, path: Path) -> dict[str, Any]:
    data = load_json(path)
    required = {"schema", "status", "project_id", "brief_path", "brief_sha256", "confirmed_by", "confirmed_at"}
    if set(data) != required or data["schema"] != f"{SCHEMA_PREFIX}/vision/v1":
        fail("Vision Lock artifact schema is invalid")
    if data["status"] != "CONFIRMED" or not str(data["confirmed_by"]).strip():
        fail("Vision Lock is not accountably confirmed")
    brief, relative = relative_file(root, str(data["brief_path"]))
    if relative != data["brief_path"] or sha256(brief) != data["brief_sha256"]:
        fail("Project Brief changed after Vision Lock confirmation")
    return data


def vision_check(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    validate_vision(root, artifact_path(root, args.artifact, "vision-lock"))
    print("VISION GATE: GREEN")


def tree_fingerprint(root: Path) -> str:
    tracked = run_git(root, "ls-files", "--cached", "--others", "--exclude-standard").splitlines()
    digest = hashlib.sha256()
    for item in sorted(tracked):
        if any(item == prefix or item.startswith(prefix + "/") for prefix in EVIDENCE_EXCLUDES):
            continue
        path = root / item
        if not path.is_file() or path.is_symlink():
            fail(f"tree contains unsupported file for verification: {item}")
        digest.update(item.encode("utf-8") + b"\0" + sha256(path).encode("ascii") + b"\n")
    return digest.hexdigest()


def verify_run(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    validate_vision(root, artifact_path(root, args.vision_artifact, "vision-lock"))
    if not args.command.strip() or not args.task_id.strip():
        fail("--command and --task-id must be non-empty")
    commit = current_commit(root)
    started_at = now()
    result = subprocess.run(
        args.command,
        cwd=root,
        shell=True,
        executable="/bin/bash",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    payload = {
        "schema": f"{SCHEMA_PREFIX}/verify/v1",
        "status": "GREEN" if result.returncode == 0 else "RED",
        "task_id": args.task_id.strip(),
        "git_commit": commit,
        "tree_sha256": tree_fingerprint(root),
        "command": args.command,
        "exit_code": result.returncode,
        "started_at": started_at,
        "completed_at": now(),
        "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest(),
    }
    output = artifact_path(root, args.output, "verify")
    atomic_json(output, payload)
    if args.log:
        log_path = artifact_path(root, args.log, "verify.log")
        log_path.write_text(
            f"$ {args.command}\n\n[stdout]\n{result.stdout}\n[stderr]\n{result.stderr}",
            encoding="utf-8",
        )
    print(f"VERIFY GATE: {payload['status']} (exit={result.returncode}, artifact={output.relative_to(root)})")
    if result.returncode != 0:
        raise SystemExit(result.returncode or 1)


def validate_verify(root: Path, path: Path) -> dict[str, Any]:
    data = load_json(path)
    required = {
        "schema", "status", "task_id", "git_commit", "tree_sha256", "command",
        "exit_code", "started_at", "completed_at", "stdout_sha256", "stderr_sha256",
    }
    if set(data) != required or data["schema"] != f"{SCHEMA_PREFIX}/verify/v1":
        fail("Verify artifact schema is invalid")
    if data["status"] != "GREEN" or data["exit_code"] != 0:
        fail("fresh verification is not GREEN")
    if len(str(data["git_commit"])) != 40:
        fail("Verify artifact does not contain a full commit SHA")
    changed = code_changes_since(root, str(data["git_commit"]))
    if changed:
        fail("code changed after verification: " + ", ".join(changed))
    if tree_fingerprint(root) != data["tree_sha256"]:
        fail("working tree changed after verification")
    return data


def verify_check(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    validate_vision(root, artifact_path(root, args.vision_artifact, "vision-lock"))
    validate_verify(root, artifact_path(root, args.artifact, "verify"))
    print("VERIFY GATE: GREEN")


def release_create(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    vision = artifact_path(root, args.vision_artifact, "vision-lock")
    verify = artifact_path(root, args.verify_artifact, "verify")
    validate_vision(root, vision)
    verify_data = validate_verify(root, verify)
    security_path, _ = relative_file(root, args.security_report)
    security = load_json(security_path)
    if security.get("verdict") != "PASS" or security.get("critical_findings") != 0:
        fail("security report must have verdict PASS and zero critical findings")
    if not args.rollback_command.strip() or not args.approved_by.strip():
        fail("rollback command and accountable approver are required")
    payload = {
        "schema": f"{SCHEMA_PREFIX}/release/v1",
        "status": "READY",
        "version": args.version,
        "git_commit": verify_data["git_commit"],
        "approved_by": args.approved_by.strip(),
        "approved_at": now(),
        "vision_artifact": evidence_ref(root, str(vision.relative_to(root))),
        "verify_artifact": evidence_ref(root, str(verify.relative_to(root))),
        "security_report": evidence_ref(root, args.security_report),
        "migration_plan": evidence_ref(root, args.migration_plan),
        "backup_evidence": evidence_ref(root, args.backup_evidence),
        "restore_evidence": evidence_ref(root, args.restore_evidence),
        "smoke_test_evidence": evidence_ref(root, args.smoke_test_evidence),
        "health_check_evidence": evidence_ref(root, args.health_check_evidence),
        "rollback_command": args.rollback_command.strip(),
    }
    output = artifact_path(root, args.output, "release")
    atomic_json(output, payload)
    print(f"RELEASE GATE: READY ({output.relative_to(root)})")


def validate_release(root: Path, path: Path) -> dict[str, Any]:
    data = load_json(path)
    required = {
        "schema", "status", "version", "git_commit", "approved_by", "approved_at",
        "vision_artifact", "verify_artifact", "security_report", "migration_plan",
        "backup_evidence", "restore_evidence", "smoke_test_evidence",
        "health_check_evidence", "rollback_command",
    }
    if set(data) != required or data["schema"] != f"{SCHEMA_PREFIX}/release/v1":
        fail("Release artifact schema is invalid")
    if data["status"] != "READY" or not str(data["approved_by"]).strip() or not str(data["rollback_command"]).strip():
        fail("release is not accountably READY with rollback")
    for label in (
        "vision_artifact", "verify_artifact", "security_report", "migration_plan",
        "backup_evidence", "restore_evidence", "smoke_test_evidence", "health_check_evidence",
    ):
        check_evidence_ref(root, data[label], label)
    vision_path, _ = relative_file(root, data["vision_artifact"]["path"])
    verify_path, _ = relative_file(root, data["verify_artifact"]["path"])
    security_path, _ = relative_file(root, data["security_report"]["path"])
    validate_vision(root, vision_path)
    verify = validate_verify(root, verify_path)
    security = load_json(security_path)
    if security.get("verdict") != "PASS" or security.get("critical_findings") != 0:
        fail("security evidence no longer passes")
    if verify["git_commit"] != data["git_commit"]:
        fail("release and Verify artifacts refer to different commits")
    return data


def release_check(args: argparse.Namespace) -> None:
    root = project_root(args.project)
    validate_release(root, artifact_path(root, args.artifact, "release"))
    print("RELEASE GATE: GREEN")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--project", default=".", help="path inside the target Git project")
    commands = result.add_subparsers(dest="gate", required=True)

    vision = commands.add_parser("vision")
    vision_commands = vision.add_subparsers(dest="action", required=True)
    confirm = vision_commands.add_parser("confirm")
    confirm.add_argument("--brief", default="docs/PROJECT-BRIEF.md")
    confirm.add_argument("--confirmed-by", required=True)
    confirm.add_argument("--project-id")
    confirm.add_argument("--output")
    confirm.set_defaults(function=vision_confirm)
    check = vision_commands.add_parser("check")
    check.add_argument("--artifact")
    check.set_defaults(function=vision_check)

    verify = commands.add_parser("verify")
    verify_commands = verify.add_subparsers(dest="action", required=True)
    run = verify_commands.add_parser("run")
    run.add_argument("--task-id", required=True)
    run.add_argument("--command", required=True)
    run.add_argument("--vision-artifact")
    run.add_argument("--output")
    run.add_argument("--log")
    run.set_defaults(function=verify_run)
    check = verify_commands.add_parser("check")
    check.add_argument("--vision-artifact")
    check.add_argument("--artifact")
    check.set_defaults(function=verify_check)

    release = commands.add_parser("release")
    release_commands = release.add_subparsers(dest="action", required=True)
    create = release_commands.add_parser("create")
    create.add_argument("--version", required=True)
    create.add_argument("--approved-by", required=True)
    create.add_argument("--security-report", required=True)
    create.add_argument("--migration-plan", required=True)
    create.add_argument("--backup-evidence", required=True)
    create.add_argument("--restore-evidence", required=True)
    create.add_argument("--rollback-command", required=True)
    create.add_argument("--smoke-test-evidence", required=True)
    create.add_argument("--health-check-evidence", required=True)
    create.add_argument("--vision-artifact")
    create.add_argument("--verify-artifact")
    create.add_argument("--output")
    create.set_defaults(function=release_create)
    check = release_commands.add_parser("check")
    check.add_argument("--artifact")
    check.set_defaults(function=release_check)
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        args.function(args)
        return 0
    except GateError as error:
        print(f"GATE BLOCKED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
