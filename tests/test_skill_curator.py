#!/usr/bin/env python3
"""Unit tests for project-memory skill_curator.py (Hermes-port Phase 5)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills/project-memory/skills/project-memory/scripts"
CURATOR = SCRIPT_DIR / "skill_curator.py"
sys.path.insert(0, str(SCRIPT_DIR))
import skill_curator as sc  # noqa: E402
import skill_usage as su  # noqa: E402


def _iso_days_ago(days: int) -> str:
    return (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).replace(microsecond=0).isoformat()


class CuratorUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / ".claude" / "skills").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _make_skill(self, name: str, *, agent: bool = True) -> Path:
        skill_dir = self.root / ".claude" / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill for curator.\n---\n\n# {name}\n",
            encoding="utf-8",
        )
        if agent:
            su.mark_agent_created(self.root, name)
        return skill_dir

    def test_stale_then_archive_transitions(self) -> None:
        self._make_skill("old-helper")
        # Anchor activity 100 days ago so both stale (30) and archive (90) apply.
        def age(rec: dict) -> None:
            rec["last_used_at"] = _iso_days_ago(100)
            rec["use_count"] = 1
            rec["created_at"] = _iso_days_ago(120)

        su._mutate(self.root, "old-helper", age)

        result = sc.apply_automatic_transitions(self.root, dry_run=False)
        self.assertTrue(result["success"])
        self.assertEqual(result["counts"]["archived"], 1)

        rec = su.get_record(self.root, "old-helper")
        self.assertEqual(rec["state"], su.STATE_ARCHIVED)
        self.assertFalse((self.root / ".claude" / "skills" / "old-helper").exists())
        self.assertTrue(
            (self.root / ".smart" / "skills-archive" / "old-helper" / "SKILL.md").is_file()
        )

    def test_mark_stale_only(self) -> None:
        self._make_skill("mid-helper")

        def age(rec: dict) -> None:
            rec["last_used_at"] = _iso_days_ago(45)
            rec["use_count"] = 2
            rec["created_at"] = _iso_days_ago(60)

        su._mutate(self.root, "mid-helper", age)
        result = sc.apply_automatic_transitions(self.root)
        self.assertEqual(result["counts"]["marked_stale"], 1)
        self.assertEqual(result["counts"]["archived"], 0)
        self.assertEqual(su.get_record(self.root, "mid-helper")["state"], su.STATE_STALE)
        # Skill still on disk
        self.assertTrue(
            (self.root / ".claude" / "skills" / "mid-helper" / "SKILL.md").is_file()
        )

    def test_pinned_skips_transitions(self) -> None:
        self._make_skill("pinned-helper")

        def age(rec: dict) -> None:
            rec["last_used_at"] = _iso_days_ago(200)
            rec["use_count"] = 5
            rec["created_at"] = _iso_days_ago(250)
            rec["pinned"] = True

        su._mutate(self.root, "pinned-helper", age)
        result = sc.apply_automatic_transitions(self.root)
        self.assertEqual(result["counts"]["skipped_pinned"], 1)
        self.assertEqual(result["counts"]["archived"], 0)
        self.assertEqual(
            su.get_record(self.root, "pinned-helper")["state"], su.STATE_ACTIVE
        )
        self.assertTrue(
            (self.root / ".claude" / "skills" / "pinned-helper").exists()
        )

    def test_protected_never_archived(self) -> None:
        # Even if someone wrongly marked smart as agent-created (blocked),
        # archive_skill and can-archive refuse.
        gate = su.assert_can_archive("smart")
        self.assertFalse(gate["success"])
        result = sc.archive_skill(self.root, "smart")
        self.assertFalse(result["success"])
        self.assertTrue(result.get("protected"))

        # agent_created_report excludes protected even if present in usage
        def force_agent(rec: dict) -> None:
            rec["created_by"] = "agent"
            rec["last_used_at"] = _iso_days_ago(200)
            rec["use_count"] = 1

        su._mutate(self.root, "smart", force_agent)
        rows = su.agent_created_report(self.root)
        self.assertFalse(any(r["name"] == "smart" for r in rows))
        transitions = sc.apply_automatic_transitions(self.root)
        self.assertEqual(transitions["counts"]["archived"], 0)

    def test_never_auto_delete(self) -> None:
        skill_dir = self._make_skill("keep-bytes")

        def age(rec: dict) -> None:
            rec["last_used_at"] = _iso_days_ago(200)
            rec["use_count"] = 1
            rec["created_at"] = _iso_days_ago(300)

        su._mutate(self.root, "keep-bytes", age)
        sc.apply_automatic_transitions(self.root)
        archived = self.root / ".smart" / "skills-archive" / "keep-bytes" / "SKILL.md"
        self.assertTrue(archived.is_file())
        # Original content preserved in archive
        self.assertIn("keep-bytes", archived.read_text(encoding="utf-8"))
        self.assertFalse(skill_dir.exists())

    def test_restore_from_archive(self) -> None:
        self._make_skill("roundtrip")

        def age(rec: dict) -> None:
            rec["last_used_at"] = _iso_days_ago(200)
            rec["use_count"] = 1
            rec["created_at"] = _iso_days_ago(300)

        su._mutate(self.root, "roundtrip", age)
        sc.archive_skill(self.root, "roundtrip")
        restored = sc.restore_skill(self.root, "roundtrip")
        self.assertTrue(restored["success"], restored)
        self.assertTrue(
            (self.root / ".claude" / "skills" / "roundtrip" / "SKILL.md").is_file()
        )
        self.assertEqual(
            su.get_record(self.root, "roundtrip")["state"], su.STATE_ACTIVE
        )

    def test_reactivate_stale_on_recent_use(self) -> None:
        self._make_skill("revived")
        su.set_state(self.root, "revived", su.STATE_STALE)

        def recent(rec: dict) -> None:
            rec["last_used_at"] = _iso_days_ago(2)
            rec["use_count"] = 3
            rec["created_at"] = _iso_days_ago(40)

        su._mutate(self.root, "revived", recent)
        result = sc.apply_automatic_transitions(self.root)
        self.assertEqual(result["counts"]["reactivated"], 1)
        self.assertEqual(su.get_record(self.root, "revived")["state"], su.STATE_ACTIVE)

    def test_never_used_grace_floor(self) -> None:
        self._make_skill("brand-new")
        # use_count 0, created 10 days ago — younger than 30d stale window
        def young(rec: dict) -> None:
            rec["use_count"] = 0
            rec["created_at"] = _iso_days_ago(10)
            rec["last_used_at"] = None
            rec["last_viewed_at"] = None
            rec["last_patched_at"] = None

        su._mutate(self.root, "brand-new", young)
        result = sc.apply_automatic_transitions(self.root)
        self.assertEqual(result["counts"]["archived"], 0)
        self.assertEqual(result["counts"]["marked_stale"], 0)
        self.assertEqual(su.get_record(self.root, "brand-new")["state"], su.STATE_ACTIVE)

    def test_consolidate_default_off(self) -> None:
        self.assertFalse(sc.get_consolidate(self.root))
        result = sc.apply_automatic_transitions(self.root)
        self.assertIn("OFF by default", result["note"])

    def test_pin_via_skill_usage(self) -> None:
        self._make_skill("pinnable")
        r = su.set_pinned(self.root, "pinnable", True)
        self.assertTrue(r["success"])
        self.assertTrue(su.get_record(self.root, "pinnable")["pinned"])


class CuratorCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / ".claude" / "skills").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(CURATOR), "--project", str(self.root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_cli_status_and_run_force(self) -> None:
        # Create agent skill aged past archive
        skill_dir = self.root / ".claude" / "skills" / "cli-old"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# cli-old\n", encoding="utf-8")
        su.mark_agent_created(self.root, "cli-old")

        def age(rec: dict) -> None:
            rec["last_used_at"] = _iso_days_ago(120)
            rec["use_count"] = 1
            rec["created_at"] = _iso_days_ago(150)

        su._mutate(self.root, "cli-old", age)

        st = self.run_cli("status")
        self.assertEqual(st.returncode, 0, st.stderr)
        payload = json.loads(st.stdout)
        self.assertTrue(payload["success"])
        self.assertIn("stale_after_days", payload["config"])
        self.assertEqual(payload["config"]["stale_after_days"], 30)
        self.assertEqual(payload["config"]["archive_after_days"], 90)
        self.assertFalse(payload["config"]["consolidate"])

        run = self.run_cli("run", "--force")
        self.assertEqual(run.returncode, 0, run.stderr)
        run_payload = json.loads(run.stdout)
        self.assertTrue(run_payload["ran"])
        self.assertEqual(run_payload["transitions"]["counts"]["archived"], 1)

        listed = self.run_cli("list-archived")
        names = json.loads(listed.stdout)["skills"]
        self.assertIn("cli-old", names)

    def test_cli_archive_protected_fails(self) -> None:
        r = self.run_cli("archive", "--skill", "project-memory")
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(json.loads(r.stdout).get("protected"))

    def test_cli_pin(self) -> None:
        su.mark_agent_created(self.root, "x")
        r = self.run_cli("pin", "--skill", "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["pinned"])


class Phase5ContractTests(unittest.TestCase):
    def test_project_memory_curator_docs(self) -> None:
        text = (
            ROOT / "skills/project-memory/skills/project-memory/SKILL.md"
        ).read_text(encoding="utf-8")
        for needle in (
            "Skill library curator",
            "skills-archive",
            "skill_curator.py",
            "stale after 30",
            "archive after 90",
            "never auto-delete",
            "pinned",
            "consolidate",
            "curator-state.json",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_smart_curator_docs(self) -> None:
        text = (ROOT / "skills/smart/skills/smart/SKILL.md").read_text(
            encoding="utf-8"
        )
        for needle in (
            "Skill library curator",
            "skill_curator.py",
            "skills-archive",
            "never auto-delete",
            "pinned",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_skill_usage_lifecycle_cli(self) -> None:
        text = (
            ROOT
            / "skills/project-memory/skills/project-memory/scripts/skill_usage.py"
        ).read_text(encoding="utf-8")
        for needle in (
            "set-state",
            "set-pinned",
            "list-agent-created",
            "can-archive",
            "STATE_STALE",
            "STATE_ARCHIVED",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
