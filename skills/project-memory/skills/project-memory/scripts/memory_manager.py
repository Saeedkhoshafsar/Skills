#!/usr/bin/env python3
"""MemoryManager — orchestrates memory providers for SMART (Hermes Phase 7).

Protocol-level port of Hermes ``agent/memory_manager.py``:

  - At most ONE external (non-builtin) provider (C-20)
  - Builtin always first when present
  - Fence external prefetch as ``<memory-context>`` (C-23)
  - Prefetch / queue_prefetch / sync_turn lifecycle (C-24)
  - Failures in one provider never block others
  - Sync is **synchronous by default** (skill/protocol host has no long-lived
    agent loop); optional background executor can be enabled for host runtimes

Config: ``.smart/memory/config.json`` → ``memory.provider`` = builtin|null|local|…
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memory_provider import (  # noqa: E402
    BuiltinMemoryProvider,
    MemoryProvider,
    build_memory_context_block,
    create_provider,
    provider_catalog,
    resolve_provider_name,
    sanitize_context,
)

try:
    from memory_store import project_root, load_config  # type: ignore
except ImportError:  # pragma: no cover
    project_root = None  # type: ignore
    load_config = None  # type: ignore

logger = logging.getLogger(__name__)

BUILTIN_NAME = "builtin"


def normalize_tool_schema(schema: Any) -> Optional[Dict[str, Any]]:
    """Normalize bare or OpenAI-wrapped tool schemas; require a name."""
    if not isinstance(schema, dict):
        return None
    if schema.get("type") == "function" and isinstance(schema.get("function"), dict):
        schema = schema["function"]
        if not isinstance(schema, dict):
            return None
    name = schema.get("name", "")
    if not name or not isinstance(name, str):
        return None
    return schema


class MemoryManager:
    """Orchestrates the built-in provider plus at most one external provider."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else None
        self._providers: List[MemoryProvider] = []
        self._tool_to_provider: Dict[str, MemoryProvider] = {}
        self._has_external: bool = False
        self._session_id: str = ""
        self._initialized: bool = False

    # -- Registration ----------------------------------------------------

    def add_provider(self, provider: MemoryProvider) -> bool:
        """Register a provider. Returns False if rejected (second external)."""
        is_builtin = provider.name == BUILTIN_NAME

        if not is_builtin:
            if self._has_external:
                existing = next(
                    (p.name for p in self._providers if p.name != BUILTIN_NAME),
                    "unknown",
                )
                logger.warning(
                    "Rejected memory provider '%s' — external provider '%s' "
                    "already registered. Only one external memory provider "
                    "is allowed (memory.provider in config).",
                    provider.name,
                    existing,
                )
                return False
            self._has_external = True

        # Avoid duplicate names
        if any(p.name == provider.name for p in self._providers):
            logger.warning(
                "Provider '%s' already registered; ignoring duplicate",
                provider.name,
            )
            return False

        self._providers.append(provider)

        for raw_schema in provider.get_tool_schemas():
            schema = normalize_tool_schema(raw_schema)
            if schema is None:
                continue
            tool_name = schema["name"]
            if tool_name in self._tool_to_provider:
                logger.warning(
                    "Memory tool name conflict: '%s' already registered by %s, "
                    "ignoring from %s",
                    tool_name,
                    self._tool_to_provider[tool_name].name,
                    provider.name,
                )
                continue
            self._tool_to_provider[tool_name] = provider

        logger.info(
            "Memory provider '%s' registered (%d tools)",
            provider.name,
            len(provider.get_tool_schemas()),
        )
        return True

    @property
    def providers(self) -> List[MemoryProvider]:
        return list(self._providers)

    @property
    def has_external(self) -> bool:
        return self._has_external

    def get_provider(self, name: str) -> Optional[MemoryProvider]:
        for p in self._providers:
            if p.name == name:
                return p
        return None

    def external_provider_name(self) -> Optional[str]:
        for p in self._providers:
            if p.name != BUILTIN_NAME:
                return p.name
        return None

    # -- Lifecycle -------------------------------------------------------

    def initialize_all(self, session_id: str = "", **kwargs: Any) -> None:
        self._session_id = session_id or ("s_" + uuid.uuid4().hex[:10])
        for provider in self._providers:
            try:
                if not provider.is_available():
                    logger.warning(
                        "Memory provider '%s' not available; skip initialize",
                        provider.name,
                    )
                    continue
                provider.initialize(self._session_id, **kwargs)
            except Exception as e:
                logger.warning(
                    "Memory provider '%s' initialize failed: %s",
                    provider.name,
                    e,
                )
        self._initialized = True

    def shutdown_all(self) -> None:
        for provider in self._providers:
            try:
                provider.shutdown()
            except Exception as e:
                logger.warning(
                    "Memory provider '%s' shutdown failed: %s",
                    provider.name,
                    e,
                )
        self._initialized = False

    # -- System prompt ---------------------------------------------------

    def build_system_prompt(self) -> str:
        blocks: list[str] = []
        for provider in self._providers:
            try:
                block = provider.system_prompt_block()
                if block and block.strip():
                    blocks.append(block.strip())
            except Exception as e:
                logger.warning(
                    "Memory provider '%s' system_prompt_block() failed: %s",
                    provider.name,
                    e,
                )
        return "\n\n".join(blocks)

    # -- Prefetch / sync (C-24) ------------------------------------------

    def prefetch_all(self, query: str, *, session_id: str = "", fence: bool = True) -> str:
        """Collect prefetch context from all providers.

        External (non-builtin) results are fenced as ``<memory-context>``
        when ``fence`` is True (default).
        """
        if not query or not str(query).strip():
            return ""
        parts: list[str] = []
        for provider in self._providers:
            try:
                result = provider.prefetch(query, session_id=session_id or self._session_id)
                if not result or not str(result).strip():
                    continue
                text = str(result).strip()
                if fence and provider.name != BUILTIN_NAME:
                    text = build_memory_context_block(text)
                    if not text:
                        continue
                parts.append(text)
            except Exception as e:
                logger.debug(
                    "Memory provider '%s' prefetch failed (non-fatal): %s",
                    provider.name,
                    e,
                )
        return "\n\n".join(parts)

    def queue_prefetch_all(self, query: str, *, session_id: str = "") -> None:
        if not query or not str(query).strip():
            return
        for provider in self._providers:
            try:
                provider.queue_prefetch(
                    query, session_id=session_id or self._session_id
                )
            except Exception as e:
                logger.debug(
                    "Memory provider '%s' queue_prefetch failed: %s",
                    provider.name,
                    e,
                )

    def sync_all(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if not user_content:
            return
        for provider in self._providers:
            try:
                provider.sync_turn(
                    user_content,
                    assistant_content,
                    session_id=session_id or self._session_id,
                    messages=messages,
                )
            except Exception as e:
                logger.warning(
                    "Memory provider '%s' sync_turn failed: %s",
                    provider.name,
                    e,
                )

    # -- Tools -----------------------------------------------------------

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        schemas: list[dict[str, Any]] = []
        seen: set[str] = set()
        for provider in self._providers:
            try:
                for raw in provider.get_tool_schemas():
                    schema = normalize_tool_schema(raw)
                    if schema is None:
                        continue
                    name = schema["name"]
                    if name in seen:
                        continue
                    schemas.append(schema)
                    seen.add(name)
            except Exception as e:
                logger.warning(
                    "Memory provider '%s' get_tool_schemas failed: %s",
                    provider.name,
                    e,
                )
        return schemas

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._tool_to_provider

    def handle_tool_call(
        self, tool_name: str, args: Dict[str, Any], **kwargs: Any
    ) -> str:
        provider = self._tool_to_provider.get(tool_name)
        if provider is None:
            return json.dumps(
                {"success": False, "error": f"No provider for tool '{tool_name}'"}
            )
        try:
            return provider.handle_tool_call(tool_name, args, **kwargs)
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Provider {provider.name} tool {tool_name}: {e}",
                }
            )

    # -- Optional hooks fan-out ------------------------------------------

    def on_turn_start(
        self, turn_number: int, message: str, **kwargs: Any
    ) -> None:
        for provider in self._providers:
            try:
                provider.on_turn_start(turn_number, message, **kwargs)
            except Exception as e:
                logger.debug(
                    "Provider '%s' on_turn_start failed: %s", provider.name, e
                )

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        for provider in self._providers:
            try:
                provider.on_session_end(messages)
            except Exception as e:
                logger.debug(
                    "Provider '%s' on_session_end failed: %s", provider.name, e
                )

    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str:
        parts: list[str] = []
        for provider in self._providers:
            try:
                text = provider.on_pre_compress(messages)
                if text and text.strip():
                    parts.append(text.strip())
            except Exception as e:
                logger.debug(
                    "Provider '%s' on_pre_compress failed: %s", provider.name, e
                )
        return "\n\n".join(parts)

    def on_memory_write(
        self,
        action: str,
        target: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        for provider in self._providers:
            try:
                provider.on_memory_write(action, target, content, metadata)
            except Exception as e:
                logger.debug(
                    "Provider '%s' on_memory_write failed: %s", provider.name, e
                )

    # -- Status ----------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "success": True,
            "session_id": self._session_id,
            "initialized": self._initialized,
            "has_external": self._has_external,
            "external": self.external_provider_name(),
            "providers": [
                {
                    "name": p.name,
                    "available": p.is_available(),
                    "tools": [
                        (normalize_tool_schema(s) or {}).get("name")
                        for s in p.get_tool_schemas()
                        if normalize_tool_schema(s)
                    ],
                }
                for p in self._providers
            ],
            "tool_count": len(self._tool_to_provider),
        }


def build_manager(
    root: Path,
    *,
    provider: str | None = None,
    include_builtin: bool = True,
    session_id: str = "",
    initialize: bool = True,
) -> MemoryManager:
    """Construct a manager with builtin + configured external provider.

    ``provider`` override / config:
      - ``builtin`` (default): builtin only
      - ``null``: builtin + null external
      - ``local``: builtin + LocalFactProvider
      - catalog-only names: raise ValueError (not shipped)
    """
    mgr = MemoryManager(root)
    name = resolve_provider_name(root, provider)

    if include_builtin:
        mgr.add_provider(BuiltinMemoryProvider(root))

    if name and name != BUILTIN_NAME:
        external = create_provider(name, root)
        ok = mgr.add_provider(external)
        if not ok:
            raise RuntimeError(f"Failed to register external provider '{name}'")

    if initialize:
        mgr.initialize_all(session_id=session_id)
    return mgr


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="MemoryManager CLI (Phase 7)")
    p.add_argument("--project", default=".", help="Project root")
    p.add_argument(
        "--provider",
        default=None,
        help="Override memory.provider (builtin|null|local|…)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Show registered providers")
    sub.add_parser("catalog", help="Provider catalog")
    sp = sub.add_parser("system-prompt", help="Build combined system prompt")
    sp.add_argument("--session-id", default="")
    pf = sub.add_parser("prefetch", help="Prefetch context for a query")
    pf.add_argument("--query", required=True)
    pf.add_argument("--session-id", default="")
    pf.add_argument("--no-fence", action="store_true")
    sy = sub.add_parser("sync", help="Sync a turn to all providers")
    sy.add_argument("--user", required=True)
    sy.add_argument("--assistant", default="")
    sy.add_argument("--session-id", default="")
    tl = sub.add_parser("tools", help="List provider tool schemas")
    tc = sub.add_parser("tool-call", help="Dispatch a provider tool")
    tc.add_argument("--name", required=True)
    tc.add_argument("--args", default="{}", help="JSON object of args")
    sc = sub.add_parser("scrub", help="Sanitize / fence sample text")
    sc.add_argument("--text", required=True)
    sc.add_argument("--fence", action="store_true")

    args = p.parse_args(argv)
    root = (
        project_root(args.project)
        if project_root
        else Path(args.project).resolve()
    )

    if args.cmd == "catalog":
        print(json.dumps({"providers": provider_catalog()}, indent=2))
        return 0

    if args.cmd == "scrub":
        if args.fence:
            out = build_memory_context_block(args.text)
        else:
            out = sanitize_context(args.text)
        print(json.dumps({"result": out}, indent=2, ensure_ascii=False))
        return 0

    try:
        mgr = build_manager(
            root,
            provider=args.provider,
            session_id=getattr(args, "session_id", "") or "",
            initialize=args.cmd
            in ("status", "system-prompt", "prefetch", "sync", "tools", "tool-call"),
        )
    except ValueError as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        return 1

    try:
        if args.cmd == "status":
            print(json.dumps(mgr.status(), indent=2))
            return 0

        if args.cmd == "system-prompt":
            text = mgr.build_system_prompt()
            print(
                json.dumps(
                    {"success": True, "chars": len(text), "text": text},
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0

        if args.cmd == "prefetch":
            text = mgr.prefetch_all(
                args.query,
                session_id=args.session_id or "",
                fence=not args.no_fence,
            )
            print(
                json.dumps(
                    {
                        "success": True,
                        "chars": len(text),
                        "fenced": not args.no_fence,
                        "text": text,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0

        if args.cmd == "sync":
            mgr.sync_all(args.user, args.assistant, session_id=args.session_id or "")
            print(json.dumps({"success": True, "synced": True}, indent=2))
            return 0

        if args.cmd == "tools":
            schemas = mgr.get_all_tool_schemas()
            print(
                json.dumps(
                    {
                        "success": True,
                        "count": len(schemas),
                        "tools": schemas,
                    },
                    indent=2,
                )
            )
            return 0

        if args.cmd == "tool-call":
            try:
                call_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(
                    json.dumps(
                        {"success": False, "error": f"bad --args JSON: {e}"},
                        indent=2,
                    )
                )
                return 1
            if not isinstance(call_args, dict):
                print(
                    json.dumps(
                        {"success": False, "error": "--args must be a JSON object"},
                        indent=2,
                    )
                )
                return 1
            result = mgr.handle_tool_call(args.name, call_args)
            # result is already JSON string from provider
            try:
                parsed = json.loads(result)
            except json.JSONDecodeError:
                parsed = {"raw": result}
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
            return 0 if parsed.get("success", True) else 1
    finally:
        mgr.shutdown_all()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
