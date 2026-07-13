#!/usr/bin/env python3
"""Behavioral tests for SMART's trusted standalone-skill installer."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "skills/smart/skills/smart/scripts/fetch-skill.sh"
SCANNER = ROOT / "skills/smart/skills/smart/scripts/skill-security-scan.sh"


class TrustedInstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="smart-installer-", dir=ROOT))
        self.project = self.temp / "project"
        self.remotes = self.temp / "remotes"
        self.work = self.temp / "source"
        self.project.mkdir()
        self.remotes.mkdir()
        self.work.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        subprocess.run(["git", "init", "-q", "--initial-branch=main", str(self.work)], check=True)
        subprocess.run(["git", "-C", str(self.work), "config", "user.name", "SMART Tests"], check=True)
        subprocess.run(["git", "-C", str(self.work), "config", "user.email", "tests@example.invalid"], check=True)
        skill = self.work / "skills" / "safe-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: safe-skill\ndescription: fixture\n---\n# Safe\n", encoding="utf-8")
        (skill / "LICENSE").write_text("Test fixture license\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.work), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.work), "commit", "-qm", "initial"], check=True)
        self.first_commit = self.git_output(self.work, "rev-parse", "HEAD")
        bare = self.remotes / "owner" / "safe.git"
        bare.parent.mkdir()
        subprocess.run(["git", "clone", "-q", "--bare", str(self.work), str(bare)], check=True)
        self.env = os.environ.copy()
        self.env["SMART_GIT_BASE_URL"] = f"file://{self.remotes}"
        self.env["SMART_GITHUB_API_BASE_URL"] = "http://127.0.0.1:9"
        # Keep bundled-capability detection deterministic: never read the
        # test machine's real ~/.claude plugin cache.
        self.plugin_cache = self.temp / "plugin-cache"
        self.env["SMART_CLAUDE_PLUGIN_CACHE"] = str(self.plugin_cache)

    def seed_plugin_cache(self, capability: str, version: str = "1.3.0") -> Path:
        cached = self.plugin_cache / "saeed-skills" / capability / version
        (cached / ".claude-plugin").mkdir(parents=True)
        (cached / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": capability, "version": version}) + "\n",
            encoding="utf-8",
        )
        return cached

    def tearDown(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    @staticmethod
    def git_output(directory: Path, *args: str) -> str:
        return subprocess.check_output(["git", "-C", str(directory), *args], text=True).strip()

    def run_installer(
        self,
        *args: str,
        expected: int = 0,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["bash", str(INSTALLER), *args],
            cwd=self.project,
            env=env or self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != expected:
            self.fail(
                f"installer returned {result.returncode}, expected {expected}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def approve(self) -> None:
        self.run_installer(
            "approve", "safe-skill", ".claude/skills", "--reviewed-by", "test-reviewer"
        )

    def run_scanner(
        self, candidate: Path, *, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCANNER), str(candidate)],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_candidate_is_quarantined_then_explicitly_activated_and_locked(self) -> None:
        result = self.run_installer(
            "candidate", "safe-skill", "owner/safe", "main", "skills/safe-skill"
        )
        self.assertIn("QUARANTINED:", result.stdout)
        self.assertNotIn("--reviewed-by", result.stdout)
        self.assertNotIn("then run:", result.stdout)
        self.assertFalse((self.project / ".claude/skills/safe-skill").exists())
        state = json.loads((self.project / ".claude/skills/.smart-install-state.json").read_text())
        self.assertIn(state["skills"]["safe-skill"]["status"], {"STATIC_SCAN_PASSED", "REVIEW_REQUIRED"})
        handoff = next(
            json.loads(line)
            for line in result.stdout.splitlines()
            if line.startswith("{")
        )
        self.assertEqual(handoff["smart_event"], "third_party_approval_required")
        self.assertEqual(handoff["capability"], "safe-skill")
        self.assertEqual(handoff["provenance"]["repository"], "owner/safe")
        self.assertEqual(handoff["provenance"]["resolved_commit"], self.first_commit)
        self.assertIn("approve-or-reject", handoff["next_action"])
        self.assertIn("Static scanning does not prove safety", handoff["risk_notice"])

        self.approve()
        self.assertTrue((self.project / ".claude/skills/safe-skill/SKILL.md").is_file())
        lock = json.loads((self.project / ".smart-lock.json").read_text())
        entry = lock["skills"]["safe-skill"]
        self.assertEqual(entry["resolved_commit"], self.first_commit)
        self.assertEqual(entry["review_status"], "VERIFIED")
        self.assertEqual(entry["verified_by"], "test-reviewer")
        self.assertRegex(entry["scan_report_sha256"], r"^[0-9a-f]{64}$")
        self.run_installer("verify", "safe-skill")

    def test_install_uses_lock_until_explicit_update(self) -> None:
        self.run_installer("candidate", "safe-skill", "owner/safe", "main", "skills/safe-skill")
        self.approve()

        (self.work / "skills/safe-skill/SKILL.md").write_text(
            "---\nname: safe-skill\ndescription: changed\n---\n# Changed\n", encoding="utf-8"
        )
        subprocess.run(["git", "-C", str(self.work), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.work), "commit", "-qm", "change"], check=True)
        second_commit = self.git_output(self.work, "rev-parse", "HEAD")
        subprocess.run(
            ["git", "-C", str(self.work), "push", "-q", f"file://{self.remotes}/owner/safe.git", "main"],
            check=True,
        )

        shutil.rmtree(self.project / ".claude/skills/safe-skill")
        self.run_installer("install", "safe-skill")
        state = json.loads((self.project / ".claude/skills/.smart-install-state.json").read_text())
        self.assertEqual(state["skills"]["safe-skill"]["resolved_commit"], self.first_commit)
        self.approve()

        self.run_installer("update", "safe-skill")
        state = json.loads((self.project / ".claude/skills/.smart-install-state.json").read_text())
        self.assertEqual(state["skills"]["safe-skill"]["resolved_commit"], second_commit)
        lock = json.loads((self.project / ".smart-lock.json").read_text())
        self.assertEqual(lock["skills"]["safe-skill"]["resolved_commit"], self.first_commit)

    def test_candidate_mutation_and_lock_tampering_fail_closed(self) -> None:
        self.run_installer("candidate", "safe-skill", "owner/safe", "main", "skills/safe-skill")
        state_path = self.project / ".claude/skills/.smart-install-state.json"
        state = json.loads(state_path.read_text())
        quarantine = Path(state["skills"]["safe-skill"]["quarantine_path"])
        (quarantine / "SKILL.md").write_text("changed after scan\n", encoding="utf-8")
        rejected = self.run_installer(
            "approve", "safe-skill", ".claude/skills", "--reviewed-by", "test-reviewer", expected=1
        )
        self.assertIn("changed after scanning", rejected.stderr)

        shutil.rmtree(self.project / ".claude", ignore_errors=True)
        self.run_installer("candidate", "safe-skill", "owner/safe", "main", "skills/safe-skill")
        self.approve()
        lock_path = self.project / ".smart-lock.json"
        lock = json.loads(lock_path.read_text())
        lock["skills"]["safe-skill"]["resolved_commit"] = "../not-a-commit"
        lock_path.write_text(json.dumps(lock), encoding="utf-8")
        rejected = self.run_installer("verify", "safe-skill", expected=1)
        self.assertIn("no lock entry", rejected.stderr)

    def test_rejects_unsafe_names_and_targets(self) -> None:
        bad_name = self.run_installer("install", "../escape", expected=1)
        self.assertIn("skill name must match", bad_name.stderr)
        outside = self.run_installer("install", "safe-skill", str(self.temp / "outside"), expected=1)
        self.assertIn("target must stay inside project root", outside.stderr)
        for target in (".git", ".git/hooks", ".github/workflows", "node_modules", ".venv", "vendor"):
            rejected = self.run_installer("install", "safe-skill", target, expected=1)
            self.assertIn("sensitive project path", rejected.stderr, target)
        missing_ref = self.run_installer(
            "candidate", "safe-skill", "owner/safe", "missing-branch", "skills/safe-skill", expected=1
        )
        self.assertIn("no default-branch fallback is allowed", missing_ref.stderr)

        self.run_installer("candidate", "safe-skill", "owner/safe", "main", "skills/safe-skill")
        invalid_reviewer = self.run_installer(
            "approve", "safe-skill", ".claude/skills", "--reviewed-by", "x", expected=1
        )
        self.assertIn("accountable identity", invalid_reviewer.stderr)

    def test_static_scanner_blocks_symlinks(self) -> None:
        candidate = self.temp / "symlink-candidate"
        candidate.mkdir()
        (candidate / "SKILL.md").write_text("# candidate\n", encoding="utf-8")
        (candidate / "escape").symlink_to("/etc/passwd")
        result = self.run_scanner(candidate)
        self.assertEqual(result.returncode, 1)
        self.assertIn("BLOCKER [SYMLINK]", result.stdout)
        self.assertIn("result=BLOCKED", result.stdout)

    def test_static_scanner_blocks_hardlinks_and_limits(self) -> None:
        hardlink_candidate = self.temp / "hardlink-candidate"
        hardlink_candidate.mkdir()
        source = hardlink_candidate / "SKILL.md"
        source.write_text("# candidate\n", encoding="utf-8")
        os.link(source, hardlink_candidate / "duplicate.md")
        hardlink = self.run_scanner(hardlink_candidate)
        self.assertEqual(hardlink.returncode, 1)
        self.assertIn("BLOCKER [HARDLINK]", hardlink.stdout)

        limits_candidate = self.temp / "limits-candidate"
        limits_candidate.mkdir()
        (limits_candidate / "SKILL.md").write_text("# candidate\n", encoding="utf-8")
        (limits_candidate / "LICENSE").write_text("fixture\n", encoding="utf-8")
        limited_env = self.env.copy()
        limited_env["SMART_SCAN_MAX_FILES"] = "1"
        limited_env["SMART_SCAN_MAX_BYTES"] = "1"
        limits = self.run_scanner(limits_candidate, env=limited_env)
        self.assertEqual(limits.returncode, 1)
        self.assertIn("file count", limits.stdout)
        self.assertIn("size", limits.stdout)
        self.assertIn("result=BLOCKED", limits.stdout)

    def test_active_content_and_scan_report_tampering_fail_verification(self) -> None:
        self.run_installer("candidate", "safe-skill", "owner/safe", "main", "skills/safe-skill")
        state_path = self.project / ".claude/skills/.smart-install-state.json"
        state = json.loads(state_path.read_text())
        quarantine = Path(state["skills"]["safe-skill"]["quarantine_path"])
        report = quarantine / ".smart-scan-report.txt"
        report.write_text(report.read_text() + "tampered=true\n", encoding="utf-8")
        rejected = self.run_installer(
            "approve", "safe-skill", ".claude/skills", "--reviewed-by", "test-reviewer", expected=1
        )
        self.assertIn("scan report changed after scanning", rejected.stderr)

        shutil.rmtree(self.project / ".claude", ignore_errors=True)
        self.run_installer("candidate", "safe-skill", "owner/safe", "main", "skills/safe-skill")
        self.approve()
        active = self.project / ".claude/skills/safe-skill"
        (active / "SKILL.md").write_text("tampered after activation\n", encoding="utf-8")
        rejected = self.run_installer("verify", "safe-skill", expected=1)
        self.assertIn("tree checksum mismatch", rejected.stderr)

    def test_bundled_capability_installs_as_native_plugin_without_quarantine(self) -> None:
        fake_bin = self.temp / "bin"
        fake_bin.mkdir()
        command_log = self.temp / "claude-commands.log"
        fake_claude = fake_bin / "claude"
        fake_claude.write_text(
            """#!/usr/bin/env bash
set -eu
printf '%s\\n' "$*" >> "$SMART_TEST_CLAUDE_LOG"
case "$*" in
  "plugin marketplace list --json"|"plugin list --json") printf '[]\\n' ;;
esac
""",
            encoding="utf-8",
        )
        fake_claude.chmod(0o755)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        env["SMART_TEST_CLAUDE_LOG"] = str(command_log)

        self.run_installer("install", "project-planner", env=env)

        commands = command_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            [
                "plugin marketplace list --json",
                "plugin marketplace add --scope user Saeedkhoshafsar/Skills",
                "plugin list --json",
                "plugin install --scope user project-planner@saeed-skills",
            ],
            commands,
        )
        self.assertFalse((self.project / ".claude/skills/.smart-quarantine").exists())

    def test_bundled_capability_install_is_idempotent(self) -> None:
        fake_bin = self.temp / "bin"
        fake_bin.mkdir()
        command_log = self.temp / "claude-commands.log"
        fake_claude = fake_bin / "claude"
        fake_claude.write_text(
            """#!/usr/bin/env bash
set -eu
printf '%s\\n' "$*" >> "$SMART_TEST_CLAUDE_LOG"
case "$*" in
  "plugin marketplace list --json")
    printf '[{"name":"saeed-skills"}]\\n'
    ;;
  "plugin list --json")
    printf '[{"id":"project-memory@saeed-skills"}]\\n'
    ;;
esac
""",
            encoding="utf-8",
        )
        fake_claude.chmod(0o755)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        env["SMART_TEST_CLAUDE_LOG"] = str(command_log)

        result = self.run_installer("install", "project-memory", env=env)

        self.assertIn("already installed", result.stdout)
        self.assertEqual(
            ["plugin marketplace list --json", "plugin list --json"],
            command_log.read_text(encoding="utf-8").splitlines(),
        )

    def test_bundled_capability_in_plugin_cache_is_recognized_without_cli(self) -> None:
        """Manual UI installs must count as installed even when `claude` is not on PATH."""
        cached = self.seed_plugin_cache("project-planner")
        env = self.env.copy()
        env["PATH"] = "/usr/bin:/bin"  # no claude CLI
        result = self.run_installer("install", "project-planner", env=env)
        self.assertIn("already installed", result.stdout)
        self.assertIn(str(cached), result.stdout)

    def test_bundled_capability_without_cache_or_cli_fails_with_actionable_error(self) -> None:
        env = self.env.copy()
        env["PATH"] = "/usr/bin:/bin"  # no claude CLI, no cache seeded
        result = self.run_installer("install", "project-planner", env=env, expected=1)
        self.assertIn("requires Claude Code CLI", result.stderr)
        self.assertIn("no cached plugin was found", result.stderr)

    def test_installed_listing_reports_cached_bundled_capabilities(self) -> None:
        self.seed_plugin_cache("project-memory")
        env = self.env.copy()
        env["PATH"] = "/usr/bin:/bin"  # no claude CLI
        result = self.run_installer("--installed", env=env)
        self.assertIn("bundled:project-memory INSTALLED", result.stdout)

    def test_bundled_update_with_cache_but_no_cli_is_non_blocking(self) -> None:
        self.seed_plugin_cache("project-planner")
        env = self.env.copy()
        env["PATH"] = "/usr/bin:/bin"  # no claude CLI
        result = self.run_installer("--update", "project-planner", env=env)
        self.assertIn("claude plugin update project-planner@saeed-skills", result.stderr)

    def test_cached_capability_short_circuits_before_cli_calls(self) -> None:
        """With the CLI available AND the cache present, no plugin commands should run."""
        self.seed_plugin_cache("project-planner")
        fake_bin = self.temp / "bin"
        fake_bin.mkdir()
        command_log = self.temp / "claude-commands.log"
        command_log.write_text("", encoding="utf-8")
        fake_claude = fake_bin / "claude"
        fake_claude.write_text(
            "#!/usr/bin/env bash\nset -eu\nprintf '%s\\n' \"$*\" >> \"$SMART_TEST_CLAUDE_LOG\"\n",
            encoding="utf-8",
        )
        fake_claude.chmod(0o755)
        env = self.env.copy()
        env["PATH"] = f"{fake_bin}:{env['PATH']}"
        env["SMART_TEST_CLAUDE_LOG"] = str(command_log)
        result = self.run_installer("install", "project-planner", env=env)
        self.assertIn("already installed", result.stdout)
        self.assertEqual("", command_log.read_text(encoding="utf-8"))

    def test_internal_sources_use_main(self) -> None:
        installer = INSTALLER.read_text(encoding="utf-8")
        self.assertNotIn("Saeedkhoshafsar/Skills|genspark_ai_developer|", installer)
        self.assertIn("Saeedkhoshafsar/Skills|main|skills", installer)


if __name__ == "__main__":
    unittest.main()
