#!/usr/bin/env python3
"""Unit tests for project-memory session_store.py (Hermes-port Phase 6)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "skills/project-memory/skills/project-memory/scripts/session_store.py"
)
sys.path.insert(0, str(SCRIPT.parent))
import session_store as ss  # noqa: E402


class SessionStoreUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        self.store = ss.SessionStore(self.root)

    def tearDown(self) -> None:
        self.store.close()
        self.temp.cleanup()

    def test_start_append_browse(self) -> None:
        started = self.store.start(title="Smoke", task_id="P6-T1")
        self.assertTrue(started["success"])
        sid = started["session_id"]
        a = self.store.append(sid, "user", "We decided to use SQLite for notes storage.")
        self.assertTrue(a["success"], a)
        self.assertGreater(a["message_id"], 0)
        self.store.append(sid, "assistant", "Recorded: SQLite backend for notes.")
        browsed = self.store.browse()
        self.assertEqual(browsed["mode"], "browse")
        self.assertGreaterEqual(browsed["count"], 1)
        ids = [s["session_id"] for s in browsed["sessions"]]
        self.assertIn(sid, ids)

    def test_discovery_search(self) -> None:
        sid = self.store.start(title="Backend decision")["session_id"]
        self.store.append(
            sid, "user", "Last week we chose SQLite FTS5 for the notes backend."
        )
        self.store.append(sid, "assistant", "Agreed: SQLite path under .smart/sessions.")
        result = self.store.search("SQLite notes backend")
        self.assertTrue(result["success"], result)
        self.assertEqual(result["mode"], "discovery")
        self.assertGreaterEqual(result["count"], 1)
        self.assertTrue(
            any("SQLite" in (s.get("snippet") or "") for s in result["sessions"])
        )

    def test_scroll_window(self) -> None:
        sid = self.store.start()["session_id"]
        ids = []
        for i in range(7):
            r = self.store.append(sid, "user", f"message number {i} about widgets")
            ids.append(r["message_id"])
        mid = ids[3]
        scrolled = self.store.scroll(sid, mid, window=2)
        self.assertTrue(scrolled["success"], scrolled)
        self.assertEqual(scrolled["mode"], "scroll")
        self.assertTrue(any(m.get("anchor") for m in scrolled["messages"]))
        self.assertLessEqual(len(scrolled["messages"]), 5)

    def test_redaction_api_key(self) -> None:
        sid = self.store.start()["session_id"]
        secret = "sk-" + ("A" * 24)
        r = self.store.append(
            sid, "user", f"My key is {secret} please remember"
        )
        self.assertTrue(r["redacted"])
        got = self.store.get_session(sid)
        body = got["messages"][0]["content"]
        self.assertNotIn(secret, body)
        self.assertIn("[REDACTED:", body)

    def test_automation_hidden_from_browse(self) -> None:
        inter = self.store.start(source="interactive", title="human")["session_id"]
        cron = self.store.start(
            session_id="cron-1", source="cron", title="nightly"
        )["session_id"]
        self.store.append(inter, "user", "interactive hello world alpha")
        self.store.append(cron, "user", "cron hello world alpha")
        browsed = self.store.browse(include_automation=False)
        ids = [s["session_id"] for s in browsed["sessions"]]
        self.assertIn(inter, ids)
        self.assertNotIn(cron, ids)
        # discovery without automation should prefer interactive
        found = self.store.search("hello world alpha", include_automation=False)
        sids = [s["session_id"] for s in found["sessions"]]
        self.assertIn(inter, sids)
        self.assertNotIn(cron, sids)

    def test_extract_durable_no_user_md_write(self) -> None:
        sid = self.store.start()["session_id"]
        self.store.append(
            sid, "user", "I prefer short bullets always from now on."
        )
        self.store.append(
            sid, "assistant", "We decided to use Postgres for billing."
        )
        user_md = self.root / "docs" / "USER.md"
        user_md.write_text("existing\n", encoding="utf-8")
        before = user_md.read_text(encoding="utf-8")
        ex = self.store.extract_durable(sid)
        self.assertTrue(ex["success"], ex)
        self.assertGreaterEqual(ex["count"], 1)
        after = user_md.read_text(encoding="utf-8")
        self.assertEqual(before, after)
        self.assertIn("Candidates only", ex["note"])

    def test_content_length_cap(self) -> None:
        sid = self.store.start()["session_id"]
        big = "x" * (ss.MAX_CONTENT_CHARS + 500)
        r = self.store.append(sid, "note", big)
        self.assertTrue(r["success"])
        self.assertLessEqual(r["content_len"], ss.MAX_CONTENT_CHARS)
        got = self.store.get_session(sid)
        self.assertIn("[truncated]", got["messages"][0]["content"])

    def test_redact_secrets_helper(self) -> None:
        text, changed, kinds = ss.redact_secrets(
            "token AKIAIOSFODNN7EXAMPLE and sk-" + ("B" * 20)
        )
        self.assertTrue(changed)
        self.assertTrue(kinds)
        self.assertNotIn("AKIA", text)

    def test_status(self) -> None:
        st = self.store.status()
        self.assertTrue(st["success"])
        self.assertIn("fts_enabled", st)
        self.assertIn("Prefer USER.md", st["routing"])


class SessionStoreCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), "--project", str(self.root), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_cli_start_append_search_browse(self) -> None:
        start = self.run_cli("start", "--title", "CLI", "--task-id", "P6-T2")
        self.assertEqual(start.returncode, 0, start.stderr)
        sid = json.loads(start.stdout)["session_id"]
        ap = self.run_cli(
            "append",
            "--session-id",
            sid,
            "--role",
            "user",
            "--content",
            "Chose Redis for cache last Tuesday.",
        )
        self.assertEqual(ap.returncode, 0, ap.stderr)
        search = self.run_cli("search", "--query", "Redis cache")
        self.assertEqual(search.returncode, 0, search.stderr)
        payload = json.loads(search.stdout)
        self.assertTrue(payload["success"])
        self.assertGreaterEqual(payload["count"], 1)
        browse = self.run_cli("browse")
        self.assertEqual(browse.returncode, 0, browse.stderr)
        self.assertGreaterEqual(json.loads(browse.stdout)["count"], 1)


class Phase6ContractTests(unittest.TestCase):
    def test_project_memory_session_docs(self) -> None:
        text = (
            ROOT / "skills/project-memory/skills/project-memory/SKILL.md"
        ).read_text(encoding="utf-8")
        for needle in (
            "Episodic session search",
            "session_store.py",
            "state.db",
            "discovery",
            "scroll",
            "browse",
            "extract-durable",
            "Prefer USER",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_smart_session_docs(self) -> None:
        text = (ROOT / "skills/smart/skills/smart/SKILL.md").read_text(
            encoding="utf-8"
        )
        for needle in (
            "session_store.py",
            "extract-durable",
            "session search",
            "Prefer USER",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
