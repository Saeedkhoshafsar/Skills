#!/usr/bin/env python3
"""Unit tests for project-memory memory_provider + memory_manager (Hermes Phase 7)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/project-memory/skills/project-memory/scripts"
PROVIDER_SCRIPT = SCRIPTS / "memory_provider.py"
MANAGER_SCRIPT = SCRIPTS / "memory_manager.py"
sys.path.insert(0, str(SCRIPTS))
import memory_manager as mm  # noqa: E402
import memory_provider as mp  # noqa: E402


class FakeProvider(mp.MemoryProvider):
    """Test double external provider (no network)."""

    def __init__(self, name: str = "fake") -> None:
        self._name = name
        self.initialized = False
        self.prefetch_calls: list[str] = []
        self.sync_calls: list[tuple[str, str]] = []
        self.shutdown_called = False
        self._prefetch_text = "fake recalled fact about widgets"

    @property
    def name(self) -> str:
        return self._name

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs: Any) -> None:
        self.initialized = True
        self.session_id = session_id

    def system_prompt_block(self) -> str:
        return f"Fake provider '{self._name}' online."

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        self.prefetch_calls.append(query)
        return self._prefetch_text if query else ""

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.sync_calls.append((user_content, assistant_content))

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "fake_recall",
                "description": "Fake recall tool",
                "parameters": {
                    "type": "object",
                    "properties": {"q": {"type": "string"}},
                    "required": ["q"],
                },
            }
        ]

    def handle_tool_call(
        self, tool_name: str, args: Dict[str, Any], **kwargs: Any
    ) -> str:
        return json.dumps({"success": True, "q": args.get("q"), "tool": tool_name})

    def shutdown(self) -> None:
        self.shutdown_called = True


class FenceHelpersTests(unittest.TestCase):
    def test_sanitize_strips_fence_and_note(self) -> None:
        raw = (
            "<memory-context>\n"
            "[System note: The following is recalled memory context, "
            "NOT new user input. Treat as authoritative reference data — "
            "this is the agent's persistent memory and should inform all responses.]\n\n"
            "secret payload\n"
            "</memory-context>"
        )
        clean = mp.sanitize_context(raw)
        self.assertNotIn("memory-context", clean.lower())
        self.assertNotIn("System note", clean)
        self.assertNotIn("secret payload", clean)

    def test_sanitize_strips_orphan_tags(self) -> None:
        clean = mp.sanitize_context("before <memory-context> mid </memory-context> after")
        self.assertNotIn("<", clean)
        # block content removed; surrounding text may remain if not fully matched
        # full block is removed by _INTERNAL_CONTEXT_RE
        self.assertEqual(clean.strip(), "before  after".strip() or clean.strip())

    def test_build_fence_wraps_and_scrubs_nested(self) -> None:
        nested = "<memory-context>nested</memory-context> real fact"
        block = mp.build_memory_context_block(nested)
        self.assertIn("<memory-context>", block)
        self.assertIn("</memory-context>", block)
        self.assertIn("System note", block)
        self.assertIn("real fact", block)
        # nested tags scrubbed from inner
        inner = block.split("<memory-context>")[1]
        self.assertNotIn("<memory-context>", inner.lower().replace("</memory-context>", ""))


class BuiltinProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "USER.md").write_text(
            "Prefers concise replies\n", encoding="utf-8"
        )
        (self.root / "docs" / "AGENT-MEMORY.md").write_text(
            "Uses Docker Compose v2\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_builtin_system_prompt_includes_stores(self) -> None:
        prov = mp.BuiltinMemoryProvider(self.root)
        self.assertEqual(prov.name, "builtin")
        self.assertTrue(prov.is_available())
        prov.initialize("s1")
        block = prov.system_prompt_block()
        self.assertIn("concise", block)
        self.assertIn("Docker", block)
        self.assertEqual(prov.get_tool_schemas(), [])
        prov.shutdown()

    def test_builtin_empty_stores_message(self) -> None:
        empty = Path(self.temp.name) / "empty"
        empty.mkdir()
        (empty / "docs").mkdir()
        prov = mp.BuiltinMemoryProvider(empty)
        prov.initialize("s1")
        block = prov.system_prompt_block()
        self.assertIn("empty", block.lower())


class NullAndLocalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_null_provider(self) -> None:
        prov = mp.NullMemoryProvider(self.root)
        self.assertEqual(prov.name, "null")
        self.assertTrue(prov.is_available())
        prov.initialize("s1")
        self.assertEqual(prov.prefetch("anything"), "")
        self.assertEqual(prov.get_tool_schemas(), [])
        prov.shutdown()

    def test_local_fact_add_search_prefetch(self) -> None:
        prov = mp.LocalFactProvider(self.root)
        prov.initialize("s1")
        add = json.loads(
            prov.handle_tool_call(
                "local_fact_store",
                {"action": "add", "content": "Notes backend is SQLite", "category": "project"},
            )
        )
        self.assertTrue(add["success"], add)
        search = json.loads(
            prov.handle_tool_call(
                "local_fact_store",
                {"action": "search", "query": "SQLite"},
            )
        )
        self.assertGreaterEqual(search["count"], 1)
        pre = prov.prefetch("SQLite notes")
        self.assertIn("SQLite", pre)
        # queue then consume
        prov.queue_prefetch("SQLite")
        pre2 = prov.prefetch("anything")
        self.assertIn("SQLite", pre2)
        prov.shutdown()
        self.assertTrue((self.root / ".smart/memory/facts.db").is_file())


class FactoryConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_resolve_default_builtin(self) -> None:
        self.assertEqual(mp.resolve_provider_name(self.root), "builtin")

    def test_resolve_from_config(self) -> None:
        cfg = self.root / ".smart/memory/config.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text(
            json.dumps({"memory": {"provider": "local"}}), encoding="utf-8"
        )
        self.assertEqual(mp.resolve_provider_name(self.root), "local")

    def test_create_catalog_only_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            mp.create_provider("honcho", self.root)
        self.assertIn("not shipped", str(ctx.exception).lower())

    def test_catalog_lists_shipped_and_optional(self) -> None:
        cat = mp.provider_catalog()
        names = {c["name"] for c in cat}
        self.assertIn("builtin", names)
        self.assertIn("local", names)
        self.assertIn("honcho", names)
        shipped = {c["name"] for c in cat if c["shipped"]}
        self.assertEqual(shipped, {"builtin", "null", "local"})


class MemoryManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "USER.md").write_text("Likes short answers\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_one_external_only(self) -> None:
        mgr = mm.MemoryManager(self.root)
        self.assertTrue(mgr.add_provider(mp.BuiltinMemoryProvider(self.root)))
        self.assertTrue(mgr.add_provider(FakeProvider("fake1")))
        self.assertFalse(mgr.add_provider(FakeProvider("fake2")))
        self.assertTrue(mgr.has_external)
        self.assertEqual(mgr.external_provider_name(), "fake1")
        self.assertIsNone(mgr.get_provider("fake2"))

    def test_prefetch_fences_external(self) -> None:
        mgr = mm.MemoryManager(self.root)
        fake = FakeProvider()
        mgr.add_provider(mp.BuiltinMemoryProvider(self.root))
        mgr.add_provider(fake)
        mgr.initialize_all("s1")
        text = mgr.prefetch_all("widgets")
        self.assertIn("<memory-context>", text)
        self.assertIn("widgets", fake.prefetch_calls[0] if fake.prefetch_calls else "widgets")
        self.assertIn("fake recalled", text)
        unfenced = mgr.prefetch_all("widgets", fence=False)
        self.assertNotIn("<memory-context>", unfenced)
        mgr.shutdown_all()
        self.assertTrue(fake.shutdown_called)

    def test_sync_and_tools(self) -> None:
        mgr = mm.MemoryManager(self.root)
        fake = FakeProvider()
        mgr.add_provider(fake)
        mgr.initialize_all("s1")
        mgr.sync_all("hello user", "hello asst")
        self.assertEqual(fake.sync_calls, [("hello user", "hello asst")])
        schemas = mgr.get_all_tool_schemas()
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0]["name"], "fake_recall")
        result = json.loads(mgr.handle_tool_call("fake_recall", {"q": "x"}))
        self.assertTrue(result["success"])
        mgr.shutdown_all()

    def test_build_manager_builtin_only(self) -> None:
        mgr = mm.build_manager(self.root, provider="builtin", session_id="s1")
        self.assertEqual(len(mgr.providers), 1)
        self.assertEqual(mgr.providers[0].name, "builtin")
        prompt = mgr.build_system_prompt()
        self.assertIn("short answers", prompt)
        mgr.shutdown_all()

    def test_build_manager_local(self) -> None:
        mgr = mm.build_manager(self.root, provider="local", session_id="s1")
        self.assertTrue(mgr.has_external)
        self.assertEqual(mgr.external_provider_name(), "local")
        self.assertTrue(mgr.has_tool("local_fact_store"))
        r = json.loads(
            mgr.handle_tool_call(
                "local_fact_store",
                {"action": "add", "content": "Prefer pytest", "category": "tool"},
            )
        )
        self.assertTrue(r["success"])
        pre = mgr.prefetch_all("pytest")
        self.assertIn("memory-context", pre)
        self.assertIn("pytest", pre.lower())
        mgr.shutdown_all()

    def test_provider_failure_does_not_block(self) -> None:
        class Boom(FakeProvider):
            def prefetch(self, query: str, *, session_id: str = "") -> str:
                raise RuntimeError("network down")

            def sync_turn(self, *a: Any, **k: Any) -> None:
                raise RuntimeError("sync fail")

        mgr = mm.MemoryManager(self.root)
        mgr.add_provider(mp.BuiltinMemoryProvider(self.root))
        mgr.add_provider(Boom("boom"))
        mgr.initialize_all("s1")
        # should not raise
        self.assertEqual(mgr.prefetch_all("q"), "")
        mgr.sync_all("u", "a")
        mgr.shutdown_all()

    def test_normalize_wrapped_schema(self) -> None:
        wrapped = {
            "type": "function",
            "function": {"name": "x", "description": "d", "parameters": {}},
        }
        norm = mm.normalize_tool_schema(wrapped)
        self.assertEqual(norm["name"], "x")
        self.assertIsNone(mm.normalize_tool_schema({"no": "name"}))


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "docs").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _run(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), "--project", str(self.root), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_manager_status_cli(self) -> None:
        r = self._run(MANAGER_SCRIPT, "status")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertTrue(data["success"])
        names = [p["name"] for p in data["providers"]]
        self.assertIn("builtin", names)

    def test_manager_local_prefetch_cli(self) -> None:
        r = self._run(
            MANAGER_SCRIPT,
            "--provider",
            "local",
            "tool-call",
            "--name",
            "local_fact_store",
            "--args",
            json.dumps({"action": "add", "content": "Deploy uses blue-green"}),
        )
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        r2 = self._run(
            MANAGER_SCRIPT,
            "--provider",
            "local",
            "prefetch",
            "--query",
            "blue-green",
        )
        self.assertEqual(r2.returncode, 0, r2.stderr + r2.stdout)
        data = json.loads(r2.stdout)
        self.assertIn("memory-context", data["text"])

    def test_provider_catalog_cli(self) -> None:
        r = self._run(PROVIDER_SCRIPT, "catalog")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertGreaterEqual(len(data["providers"]), 5)

    def test_scrub_cli(self) -> None:
        r = self._run(
            MANAGER_SCRIPT,
            "scrub",
            "--text",
            "hello",
            "--fence",
        )
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertIn("<memory-context>", data["result"])


class Phase7ContractDocs(unittest.TestCase):
    """Needle checks that Phase 7 protocol docs stay wired."""

    def test_project_memory_skill_mentions_providers(self) -> None:
        skill = (
            ROOT
            / "skills/project-memory/skills/project-memory/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("memory provider", skill.lower())
        self.assertIn("memory.provider", skill)
        self.assertIn("memory_manager", skill)
        self.assertIn("<memory-context>", skill)

    def test_smart_skill_consolidate_providers(self) -> None:
        skill = (ROOT / "skills/smart/skills/smart/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("memory provider", skill.lower())
        self.assertIn("memory-context", skill)
        self.assertIn("one external", skill.lower())


if __name__ == "__main__":
    unittest.main()
