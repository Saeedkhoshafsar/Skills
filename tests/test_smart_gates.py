#!/usr/bin/env python3
"""Behavioral tests for SMART's machine-verifiable execution gates."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/smart/skills/smart/scripts/smart-gates.py"


class SmartGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Gate Test")
        self.git("config", "user.email", "gate@example.test")
        (self.project / "docs").mkdir()
        (self.project / "docs/PROJECT-BRIEF.md").write_text(
            "# Brief\n\n## Vision Lock\nStatus: CONFIRMED\n", encoding="utf-8"
        )
        (self.project / "app.txt").write_text("v1\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "initial")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "-C", str(self.project), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            self.fail(result.stderr)
        return result

    def gate(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), "--project", str(self.project), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def confirm_vision(self) -> subprocess.CompletedProcess[str]:
        return self.gate("vision", "confirm", "--confirmed-by", "product-owner@example.test")

    def run_verify(self, command: str = "test -f app.txt") -> subprocess.CompletedProcess[str]:
        return self.gate(
            "verify", "run", "--task-id", "P1-T1", "--command", command
        )

    def write_release_evidence(self) -> None:
        evidence = self.project / "evidence"
        evidence.mkdir()
        (evidence / "security.json").write_text(
            json.dumps({"verdict": "PASS", "critical_findings": 0}) + "\n",
            encoding="utf-8",
        )
        for name in ("migration", "backup", "restore", "smoke", "health"):
            (evidence / f"{name}.txt").write_text(f"{name}: PASS\n", encoding="utf-8")

    def create_release(self) -> subprocess.CompletedProcess[str]:
        return self.gate(
            "release", "create",
            "--version", "1.0.0",
            "--approved-by", "release-owner@example.test",
            "--security-report", "evidence/security.json",
            "--migration-plan", "evidence/migration.txt",
            "--backup-evidence", "evidence/backup.txt",
            "--restore-evidence", "evidence/restore.txt",
            "--rollback-command", "deploy --version previous",
            "--smoke-test-evidence", "evidence/smoke.txt",
            "--health-check-evidence", "evidence/health.txt",
        )

    def test_vision_confirmation_records_brief_hash_and_identity(self) -> None:
        result = self.confirm_vision()
        self.assertEqual(result.returncode, 0, result.stderr)
        artifact = json.loads(
            (self.project / ".smart/evidence/vision-lock.json").read_text()
        )
        self.assertEqual(artifact["status"], "CONFIRMED")
        self.assertEqual(artifact["confirmed_by"], "product-owner@example.test")
        self.assertEqual(len(artifact["brief_sha256"]), 64)
        self.assertEqual(self.gate("vision", "check").returncode, 0)

    def test_vision_check_rejects_changed_brief(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        (self.project / "docs/PROJECT-BRIEF.md").write_text("changed\n")
        result = self.gate("vision", "check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed after Vision Lock", result.stderr)

    def test_vision_rejects_symlink_brief(self) -> None:
        (self.project / "brief-link.md").symlink_to("docs/PROJECT-BRIEF.md")
        result = self.gate(
            "vision", "confirm", "--brief", "brief-link.md", "--confirmed-by", "owner"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink evidence", result.stderr)

    def test_verify_run_records_green_command_commit_and_tree(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        result = self.run_verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        artifact = json.loads((self.project / ".smart/evidence/verify.json").read_text())
        self.assertEqual(artifact["status"], "GREEN")
        self.assertEqual(artifact["exit_code"], 0)
        self.assertEqual(len(artifact["git_commit"]), 40)
        self.assertEqual(len(artifact["tree_sha256"]), 64)
        self.assertEqual(self.gate("verify", "check").returncode, 0)

    def test_verify_run_records_red_and_returns_failure(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        result = self.run_verify("echo no >&2; exit 7")
        self.assertEqual(result.returncode, 7)
        artifact = json.loads((self.project / ".smart/evidence/verify.json").read_text())
        self.assertEqual(artifact["status"], "RED")
        self.assertEqual(artifact["exit_code"], 7)
        self.assertNotEqual(self.gate("verify", "check").returncode, 0)

    def test_verify_check_rejects_worktree_change_after_green(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.assertEqual(self.run_verify().returncode, 0)
        (self.project / "app.txt").write_text("tampered\n")
        result = self.gate("verify", "check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("working tree changed", result.stderr)

    def test_verify_check_allows_only_evidence_artifact_changes(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.assertEqual(self.run_verify().returncode, 0)
        (self.project / ".smart/evidence/note.txt").write_text("metadata\n")
        self.assertEqual(self.gate("verify", "check").returncode, 0)

    def test_release_requires_passing_structured_security_report(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.write_release_evidence()
        (self.project / "evidence/security.json").write_text(
            json.dumps({"verdict": "BLOCKED", "critical_findings": 1})
        )
        self.assertEqual(self.run_verify().returncode, 0)
        result = self.create_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("security report", result.stderr)

    def test_release_create_and_check_bind_all_evidence(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.write_release_evidence()
        self.assertEqual(self.run_verify().returncode, 0)
        result = self.create_release()
        self.assertEqual(result.returncode, 0, result.stderr)
        artifact = json.loads((self.project / ".smart/evidence/release.json").read_text())
        self.assertEqual(artifact["status"], "READY")
        self.assertEqual(artifact["security_report"]["path"], "evidence/security.json")
        self.assertEqual(self.gate("release", "check").returncode, 0)

    def test_release_check_rejects_changed_evidence(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.write_release_evidence()
        self.assertEqual(self.run_verify().returncode, 0)
        self.assertEqual(self.create_release().returncode, 0)
        (self.project / "evidence/restore.txt").write_text("restore: UNKNOWN\n")
        result = self.gate("release", "check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("restore_evidence evidence changed", result.stderr)

    def test_vision_confirm_blocks_not_ready_brief(self) -> None:
        (self.project / "docs/PROJECT-BRIEF.md").write_text(
            "# Brief\n\n## Vision Lock\nStatus: NOT READY\n", encoding="utf-8"
        )
        result = self.confirm_vision()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("NOT READY", result.stderr)

    def test_vision_confirm_blocks_open_mind_coverage_gaps(self) -> None:
        (self.project / "docs/STATE.md").write_text(
            "# STATE\n\n| Mind coverage | GAPS: M-PPL-02 |\n", encoding="utf-8"
        )
        result = self.confirm_vision()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("coverage gaps", result.stderr)

    def test_vision_confirm_allows_complete_mind_coverage(self) -> None:
        (self.project / "docs/STATE.md").write_text(
            "# STATE\n\n| Mind coverage | COMPLETE 2026-07-11 |\n", encoding="utf-8"
        )
        self.assertEqual(self.confirm_vision().returncode, 0)

    def test_vision_check_rejects_hand_edited_artifact(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        artifact = self.project / ".smart/evidence/vision-lock.json"
        data = json.loads(artifact.read_text())
        data["confirmed_by"] = "forger@example.test"
        artifact.write_text(json.dumps(data, indent=2, sort_keys=True))
        result = self.gate("vision", "check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("seal mismatch", result.stderr)

    def test_verify_check_rejects_red_artifact_flipped_to_green(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.assertNotEqual(self.run_verify("exit 3").returncode, 0)
        artifact = self.project / ".smart/evidence/verify.json"
        data = json.loads(artifact.read_text())
        data["status"] = "GREEN"
        data["exit_code"] = 0
        artifact.write_text(json.dumps(data, indent=2, sort_keys=True))
        result = self.gate("verify", "check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("seal mismatch", result.stderr)

    def test_verify_check_rejects_task_id_swap_on_green_artifact(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.assertEqual(self.run_verify().returncode, 0)
        artifact = self.project / ".smart/evidence/verify.json"
        data = json.loads(artifact.read_text())
        data["task_id"] = "P9-T9-forged"
        artifact.write_text(json.dumps(data, indent=2, sort_keys=True))
        result = self.gate("verify", "check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("seal mismatch", result.stderr)

    def test_release_check_rejects_hand_edited_release_artifact(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.write_release_evidence()
        self.assertEqual(self.run_verify().returncode, 0)
        self.assertEqual(self.create_release().returncode, 0)
        artifact = self.project / ".smart/evidence/release.json"
        data = json.loads(artifact.read_text())
        data["approved_by"] = "forger@example.test"
        artifact.write_text(json.dumps(data, indent=2, sort_keys=True))
        result = self.gate("release", "check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("seal mismatch", result.stderr)

    def test_release_missing_evidence_file_fails_closed_without_traceback(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.write_release_evidence()
        self.assertEqual(self.run_verify().returncode, 0)
        result = self.gate(
            "release", "create", "--version", "1", "--approved-by", "owner",
            "--security-report", "evidence/missing.json",
            "--migration-plan", "evidence/migration.txt",
            "--backup-evidence", "evidence/backup.txt",
            "--restore-evidence", "evidence/restore.txt",
            "--rollback-command", "rollback",
            "--smoke-test-evidence", "evidence/smoke.txt",
            "--health-check-evidence", "evidence/health.txt",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GATE BLOCKED", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_release_rejects_evidence_outside_project(self) -> None:
        self.assertEqual(self.confirm_vision().returncode, 0)
        self.write_release_evidence()
        self.assertEqual(self.run_verify().returncode, 0)
        result = self.gate(
            "release", "create", "--version", "1", "--approved-by", "owner",
            "--security-report", "evidence/security.json", "--migration-plan", "/etc/hosts",
            "--backup-evidence", "evidence/backup.txt", "--restore-evidence", "evidence/restore.txt",
            "--rollback-command", "rollback", "--smoke-test-evidence", "evidence/smoke.txt",
            "--health-check-evidence", "evidence/health.txt",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escapes project root", result.stderr)

    def test_memory_resume_check_requires_state_file(self) -> None:
        result = self.gate("memory", "resume-check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no durable STATE resume file", result.stderr)
        self.assertIn("GATE BLOCKED", result.stderr)

    def test_memory_resume_check_rejects_incomplete_packet(self) -> None:
        (self.project / "docs/STATE.md").write_text(
            "# STATE\n\n## Resume packet\n\n```\nMode: EXECUTION\n```\n",
            encoding="utf-8",
        )
        result = self.gate("memory", "resume-check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("resume packet is incomplete", result.stderr)

    def test_memory_resume_check_accepts_complete_packet(self) -> None:
        (self.project / "docs/STATE.md").write_text(
            "# STATE\n\n## Resume packet\n\n```\n"
            "Mode      : EXECUTION\n"
            "Task      : P2-T4 CSV export\n"
            "Exact progress : exporter helper written; tests pending\n"
            "Last evidence : python3 -m unittest tests.test_export -v -> RED\n"
            "Blocker  : none\n"
            "Next     : finish export tests and re-run verify\n"
            "```\n",
            encoding="utf-8",
        )
        result = self.gate("memory", "resume-check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MEMORY GATE: RESUME READY", result.stdout)

    def test_memory_resume_check_prefers_state2_when_present(self) -> None:
        (self.project / "docs/STATE.md").write_text("stale archive\n", encoding="utf-8")
        (self.project / "docs/STATE2.md").write_text(
            "## Resume packet\n\n```\n"
            "Mode: SURFACE TRACK\n"
            "Task: U2-T2 onboarding\n"
            "Progress: U2-T1 done\n"
            "Evidence: npm run verify GREEN\n"
            "Blockers: none\n"
            "Next: consolidate empty-product path\n"
            "```\n",
            encoding="utf-8",
        )
        result = self.gate("memory", "resume-check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("docs/STATE2.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
