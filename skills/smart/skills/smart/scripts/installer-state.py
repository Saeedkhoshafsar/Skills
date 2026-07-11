#!/usr/bin/env python3
"""Validation, lockfile, and manifest primitives for SMART's trusted installer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVIEWER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9@._-]{1,127}$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"JSON root must be an object: {path}")
    return value


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def validate_skill(value: str) -> str:
    if not SKILL_RE.fullmatch(value):
        fail("skill name must match ^[a-z0-9][a-z0-9._-]*$")
    return value


def validate_repo(value: str) -> str:
    if not REPO_RE.fullmatch(value) or ".." in value:
        fail("repository must be an owner/name GitHub slug")
    return value


def validate_ref(value: str) -> str:
    if not REF_RE.fullmatch(value) or ".." in value or value.endswith("/"):
        fail("ref contains unsafe characters")
    return value


def validate_repo_path(value: str) -> str:
    candidate = Path(value)
    if value.startswith("/") or any(part in ("", "..") for part in candidate.parts):
        fail("repository path must be relative and may not contain '..'")
    return value


def project_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def validate_target(value: str, skill: str) -> tuple[Path, Path]:
    validate_skill(skill)
    raw = Path(value)
    target = (Path.cwd() / raw).resolve() if not raw.is_absolute() else raw.resolve()
    root = project_root()
    try:
        relative_target = target.relative_to(root)
    except ValueError:
        fail(f"target must stay inside project root {root}")
    if target == root:
        fail("target may not be the project root")
    sensitive_prefixes = (
        (".git",),
        (".github", "workflows"),
        ("node_modules",),
        (".venv",),
        ("vendor",),
    )
    relative_parts = relative_target.parts
    if any(relative_parts[: len(prefix)] == prefix for prefix in sensitive_prefixes):
        fail(f"target may not be inside sensitive project path {relative_target}")
    if raw.is_symlink() or target.is_symlink():
        fail("target may not be a symlink")
    destination = target / skill
    if destination.exists() and destination.is_symlink():
        fail("skill destination may not be a symlink")
    return target, destination


def file_manifest(root: Path) -> tuple[list[dict], str]:
    if not root.is_dir() or root.is_symlink():
        fail(f"manifest root must be a real directory: {root}")
    records: list[dict] = []
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            fail(f"symlink is forbidden in quarantined content: {relative}")
        if not path.is_file() or relative in {".smart-scan-report.txt", ".smart-manifest.json"}:
            continue
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        executable = bool(path.stat().st_mode & 0o111)
        record = {"path": relative, "sha256": file_hash, "size": path.stat().st_size}
        if executable:
            record["executable"] = True
        records.append(record)
        digest.update(relative.encode("utf-8") + b"\0" + file_hash.encode("ascii") + b"\n")
    return records, digest.hexdigest()


def command_validate(args: argparse.Namespace) -> None:
    target, destination = validate_target(args.target, args.skill)
    print(f"{target}\t{destination}")


def command_validate_source(args: argparse.Namespace) -> None:
    print(
        "\t".join(
            (
                validate_skill(args.skill),
                validate_repo(args.repository),
                validate_ref(args.ref),
                validate_repo_path(args.path),
            )
        )
    )


def command_manifest(args: argparse.Namespace) -> None:
    root = Path(args.directory).resolve()
    files, tree_hash = file_manifest(root)
    value = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "tree_sha256": tree_hash,
        "files": files,
    }
    output = root / ".smart-manifest.json"
    atomic_json(output, value)
    print(tree_hash)


def command_file_sha256(args: argparse.Namespace) -> None:
    path = Path(args.file).resolve()
    if not path.is_file() or path.is_symlink():
        fail(f"hash input must be a regular file: {path}")
    print(hashlib.sha256(path.read_bytes()).hexdigest())


def command_lock_get(args: argparse.Namespace) -> None:
    skill = validate_skill(args.skill)
    lock = read_json(Path(args.lockfile), {"lockfile_version": 1, "skills": {}})
    entry = lock.get("skills", {}).get(skill)
    if not isinstance(entry, dict):
        raise SystemExit(1)
    validate_repo(str(entry.get("repository", "")))
    validate_ref(str(entry.get("requested_ref", "")))
    validate_repo_path(str(entry.get("path", "")))
    if not COMMIT_RE.fullmatch(str(entry.get("resolved_commit", ""))):
        fail("lock entry contains an invalid commit")
    if not SHA256_RE.fullmatch(str(entry.get("tree_sha256", ""))):
        fail("lock entry contains an invalid tree hash")
    if not SHA256_RE.fullmatch(str(entry.get("scan_report_sha256", ""))):
        fail("lock entry contains an invalid scan report hash")
    if entry.get("review_status") != "VERIFIED":
        fail("lock entry is not VERIFIED")
    fields = (
        "repository",
        "requested_ref",
        "path",
        "resolved_commit",
        "tree_sha256",
        "scan_report_sha256",
        "review_status",
    )
    print("\t".join(str(entry.get(field, "")) for field in fields))


def command_lock_put(args: argparse.Namespace) -> None:
    skill = validate_skill(args.skill)
    validate_repo(args.repository)
    validate_ref(args.ref)
    validate_repo_path(args.path)
    if not COMMIT_RE.fullmatch(args.commit):
        fail("resolved commit must be a full 40-character lowercase SHA")
    if not SHA256_RE.fullmatch(args.tree_hash):
        fail("tree hash must be a full 64-character lowercase SHA-256")
    if not SHA256_RE.fullmatch(args.scan_report_hash):
        fail("scan report hash must be a full 64-character lowercase SHA-256")
    if not REVIEWER_RE.fullmatch(args.reviewed_by):
        fail("reviewer identity must use 2-128 letters, digits, @, dot, underscore, or hyphen")
    lock_path = Path(args.lockfile)
    lock = read_json(lock_path, {"lockfile_version": 1, "skills": {}})
    if lock.get("lockfile_version") != 1:
        fail("unsupported lockfile_version")
    skills = lock.setdefault("skills", {})
    if not isinstance(skills, dict):
        fail("lockfile skills must be an object")
    skills[skill] = {
        "repository": args.repository,
        "requested_ref": args.ref,
        "path": args.path,
        "resolved_commit": args.commit,
        "tree_sha256": args.tree_hash,
        "scan_report_sha256": args.scan_report_hash,
        "review_status": "VERIFIED",
        "verified_by": args.reviewed_by,
        "verified_at": utc_now(),
    }
    atomic_json(lock_path, lock)


def command_state_put(args: argparse.Namespace) -> None:
    skill = validate_skill(args.skill)
    if not COMMIT_RE.fullmatch(args.commit):
        fail("resolved commit must be a full 40-character lowercase SHA")
    if args.tree_hash and not SHA256_RE.fullmatch(args.tree_hash):
        fail("tree hash must be empty or a full 64-character lowercase SHA-256")
    if args.scan_report_hash and not SHA256_RE.fullmatch(args.scan_report_hash):
        fail("scan report hash must be empty or a full 64-character lowercase SHA-256")
    state_path = Path(args.state_file)
    state = read_json(state_path, {"schema_version": 1, "skills": {}})
    skills = state.setdefault("skills", {})
    skills[skill] = {
        "status": args.status,
        "repository": validate_repo(args.repository),
        "requested_ref": validate_ref(args.ref),
        "path": validate_repo_path(args.path),
        "resolved_commit": args.commit,
        "tree_sha256": args.tree_hash,
        "scan_report_sha256": args.scan_report_hash,
        "quarantine_path": args.quarantine,
        "updated_at": utc_now(),
    }
    atomic_json(state_path, state)


def command_state_get(args: argparse.Namespace) -> None:
    skill = validate_skill(args.skill)
    state = read_json(Path(args.state_file), {"schema_version": 1, "skills": {}})
    entry = state.get("skills", {}).get(skill)
    if not isinstance(entry, dict):
        raise SystemExit(1)
    fields = (
        "status",
        "repository",
        "requested_ref",
        "path",
        "resolved_commit",
        "tree_sha256",
        "scan_report_sha256",
        "quarantine_path",
    )
    print("\t".join(str(entry.get(field, "")) for field in fields))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    commands = result.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("skill")
    validate.add_argument("target")
    validate.set_defaults(func=command_validate)

    source = commands.add_parser("validate-source")
    source.add_argument("skill")
    source.add_argument("repository")
    source.add_argument("ref")
    source.add_argument("path")
    source.set_defaults(func=command_validate_source)

    manifest = commands.add_parser("manifest")
    manifest.add_argument("directory")
    manifest.set_defaults(func=command_manifest)

    file_sha256 = commands.add_parser("file-sha256")
    file_sha256.add_argument("file")
    file_sha256.set_defaults(func=command_file_sha256)

    lock_get = commands.add_parser("lock-get")
    lock_get.add_argument("lockfile")
    lock_get.add_argument("skill")
    lock_get.set_defaults(func=command_lock_get)

    lock_put = commands.add_parser("lock-put")
    lock_put.add_argument("lockfile")
    lock_put.add_argument("skill")
    lock_put.add_argument("repository")
    lock_put.add_argument("ref")
    lock_put.add_argument("path")
    lock_put.add_argument("commit")
    lock_put.add_argument("tree_hash")
    lock_put.add_argument("scan_report_hash")
    lock_put.add_argument("reviewed_by")
    lock_put.set_defaults(func=command_lock_put)

    state_put = commands.add_parser("state-put")
    state_put.add_argument("state_file")
    state_put.add_argument("skill")
    state_put.add_argument("status", choices=("QUARANTINED", "STATIC_SCAN_PASSED", "REVIEW_REQUIRED", "BLOCKED", "VERIFIED", "ACTIVE"))
    state_put.add_argument("repository")
    state_put.add_argument("ref")
    state_put.add_argument("path")
    state_put.add_argument("commit")
    state_put.add_argument("tree_hash")
    state_put.add_argument("scan_report_hash")
    state_put.add_argument("quarantine")
    state_put.set_defaults(func=command_state_put)

    state_get = commands.add_parser("state-get")
    state_get.add_argument("state_file")
    state_get.add_argument("skill")
    state_get.set_defaults(func=command_state_get)
    return result


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
