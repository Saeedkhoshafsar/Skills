#!/usr/bin/env python3
"""Validate SMART's offline behavioral-contract scenarios.

This validator is deterministic, dependency-free, and performs no network or model calls.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_SUITE = HERE / "scenarios.json"


class ValidationError(RuntimeError):
    """A user-actionable scenario validation failure."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path}: {exc}") from exc


def _require_non_empty_text(value: Any, field: str, scenario_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{scenario_id}: {field} must be non-empty text")


def validate_suite(suite: dict[str, Any]) -> None:
    if suite.get("schema_version") != "1.0":
        raise ValidationError("Unsupported or missing suite schema_version; expected 1.0")
    scenarios = suite.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValidationError("Suite must contain at least one scenario")

    scenario_ids: set[str] = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValidationError("Every scenario must be a JSON object")
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not re.fullmatch(
            r"[a-z0-9][a-z0-9_-]*", scenario_id
        ):
            raise ValidationError(f"Invalid scenario id: {scenario_id!r}")
        if scenario_id in scenario_ids:
            raise ValidationError(f"Duplicate scenario id: {scenario_id}")
        scenario_ids.add(scenario_id)

        for field in ("title", "category", "user_prompt"):
            _require_non_empty_text(scenario.get(field), field, scenario_id)
        if not isinstance(scenario.get("critical"), bool):
            raise ValidationError(f"{scenario_id}: critical must be boolean")
        context = scenario.get("project_context")
        if context is not None and not isinstance(context, dict):
            raise ValidationError(f"{scenario_id}: project_context must be an object")
        threshold = scenario.get("pass_threshold", 0.8)
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise ValidationError(f"{scenario_id}: pass_threshold must be numeric")
        if not 0 <= threshold <= 1:
            raise ValidationError(f"{scenario_id}: pass_threshold must be between 0 and 1")

        rubrics = scenario.get("rubrics")
        if not isinstance(rubrics, list) or not rubrics:
            raise ValidationError(f"{scenario_id}: rubrics must be a non-empty list")
        rubric_ids: set[str] = set()
        for rubric in rubrics:
            if not isinstance(rubric, dict):
                raise ValidationError(f"{scenario_id}: every rubric must be an object")
            rubric_id = rubric.get("id")
            if not isinstance(rubric_id, str) or not rubric_id:
                raise ValidationError(f"{scenario_id}: every rubric needs an id")
            if rubric_id in rubric_ids:
                raise ValidationError(f"{scenario_id}: duplicate rubric id {rubric_id}")
            rubric_ids.add(rubric_id)
            _require_non_empty_text(rubric.get("criterion"), "criterion", scenario_id)
            weight = rubric.get("weight", 1)
            if isinstance(weight, bool) or not isinstance(weight, int) or weight < 1:
                raise ValidationError(
                    f"{scenario_id}/{rubric_id}: weight must be a positive integer"
                )
            if "must_pass" in rubric and not isinstance(rubric["must_pass"], bool):
                raise ValidationError(
                    f"{scenario_id}/{rubric_id}: must_pass must be boolean"
                )

        patterns = scenario.get("forbidden_patterns", [])
        if not isinstance(patterns, list):
            raise ValidationError(f"{scenario_id}: forbidden_patterns must be a list")
        for pattern in patterns:
            if not isinstance(pattern, str):
                raise ValidationError(
                    f"{scenario_id}: every forbidden pattern must be text"
                )
            try:
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as exc:
                raise ValidationError(
                    f"{scenario_id}: invalid forbidden pattern {pattern!r}: {exc}"
                ) from exc


def select_scenarios(
    suite: dict[str, Any], selected: list[str]
) -> list[dict[str, Any]]:
    scenarios = suite["scenarios"]
    if not selected:
        return scenarios
    wanted = set(selected)
    found = {scenario["id"] for scenario in scenarios if scenario["id"] in wanted}
    missing = sorted(wanted - found)
    if missing:
        raise ValidationError(f"Unknown scenario id(s): {', '.join(missing)}")
    return [scenario for scenario in scenarios if scenario["id"] in wanted]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument(
        "--scenario", action="append", default=[], help="Validate one scenario id; repeatable"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        suite = load_json(args.suite)
        if not isinstance(suite, dict):
            raise ValidationError("Suite root must be a JSON object")
        validate_suite(suite)
        scenarios = select_scenarios(suite, args.scenario)
        print(f"Valid offline behavioral contract suite: {len(scenarios)} scenario(s)")
        return 0
    except (ValidationError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
