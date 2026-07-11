#!/usr/bin/env python3
"""Run SMART behavioral scenarios against an OpenAI-compatible chat endpoint.

The harness intentionally separates response generation from rubric judging so saved
responses can be re-judged after a rubric change. It uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_SUITE = HERE / "scenarios.json"
DEFAULT_SKILL = HERE.parent / "SKILL.md"


class EvalError(RuntimeError):
    """A user-actionable evaluation failure."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvalError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EvalError(f"Invalid JSON in {path}: {exc}") from exc


def validate_suite(suite: dict[str, Any]) -> None:
    if suite.get("schema_version") != "1.0":
        raise EvalError("Unsupported or missing suite schema_version; expected 1.0")
    scenarios = suite.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise EvalError("Suite must contain at least one scenario")

    scenario_ids: set[str] = set()
    for scenario in scenarios:
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", scenario_id):
            raise EvalError(f"Invalid scenario id: {scenario_id!r}")
        if scenario_id in scenario_ids:
            raise EvalError(f"Duplicate scenario id: {scenario_id}")
        scenario_ids.add(scenario_id)
        if not isinstance(scenario.get("user_prompt"), str) or not scenario["user_prompt"].strip():
            raise EvalError(f"{scenario_id}: user_prompt must be non-empty")
        rubrics = scenario.get("rubrics")
        if not isinstance(rubrics, list) or not rubrics:
            raise EvalError(f"{scenario_id}: rubrics must be a non-empty list")
        rubric_ids: set[str] = set()
        for rubric in rubrics:
            rubric_id = rubric.get("id")
            if not isinstance(rubric_id, str) or not rubric_id:
                raise EvalError(f"{scenario_id}: every rubric needs an id")
            if rubric_id in rubric_ids:
                raise EvalError(f"{scenario_id}: duplicate rubric id {rubric_id}")
            rubric_ids.add(rubric_id)
            if not isinstance(rubric.get("criterion"), str) or not rubric["criterion"].strip():
                raise EvalError(f"{scenario_id}/{rubric_id}: criterion must be non-empty")
            weight = rubric.get("weight", 1)
            if not isinstance(weight, int) or weight < 1:
                raise EvalError(f"{scenario_id}/{rubric_id}: weight must be a positive integer")
        for pattern in scenario.get("forbidden_patterns", []):
            try:
                re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            except re.error as exc:
                raise EvalError(f"{scenario_id}: invalid forbidden pattern {pattern!r}: {exc}") from exc


def select_scenarios(suite: dict[str, Any], selected: list[str]) -> list[dict[str, Any]]:
    scenarios = suite["scenarios"]
    if not selected:
        return scenarios
    wanted = set(selected)
    found = {scenario["id"] for scenario in scenarios if scenario["id"] in wanted}
    missing = sorted(wanted - found)
    if missing:
        raise EvalError(f"Unknown scenario id(s): {', '.join(missing)}")
    return [scenario for scenario in scenarios if scenario["id"] in wanted]


def endpoint_url(base_url: str) -> str:
    clean = base_url.rstrip("/")
    if clean.endswith("/chat/completions"):
        return clean
    return f"{clean}/chat/completions"


def chat_completion(
    *, base_url: str, api_key: str, model: str, messages: list[dict[str, str]], timeout: int
) -> str:
    payload = json.dumps({"model": model, "messages": messages}).encode("utf-8")
    request = urllib.request.Request(
        endpoint_url(base_url),
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "smart-behavioral-evals/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise EvalError(f"API returned HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise EvalError(f"API request failed: {exc}") from exc
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise EvalError("API response did not contain choices[0].message.content") from exc


def scenario_context(scenario: dict[str, Any]) -> str:
    context = scenario.get("project_context")
    if not context:
        return "No project files or durable state are supplied."
    return json.dumps(context, ensure_ascii=False, indent=2)


def generate_response(
    scenario: dict[str, Any], skill_text: str, args: argparse.Namespace
) -> str:
    system = (
        "You are SMART. Follow the complete SMART contract below. Treat the supplied project "
        "context as the repository evidence available for this turn. Do not discuss this test harness.\n\n"
        + skill_text
    )
    user = f"PROJECT CONTEXT:\n{scenario_context(scenario)}\n\nUSER REQUEST:\n{scenario['user_prompt']}"
    return chat_completion(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        timeout=args.timeout,
    )


def extract_json_object(raw: str) -> dict[str, Any]:
    candidate = raw.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s*```$", "", candidate)
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise EvalError(f"Judge returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise EvalError("Judge result must be a JSON object")
    return value


def judge_response(
    scenario: dict[str, Any], assistant_response: str, args: argparse.Namespace
) -> dict[str, Any]:
    rubric_payload = [
        {
            "id": rubric["id"],
            "criterion": rubric["criterion"],
            "must_pass": rubric.get("must_pass", False),
        }
        for rubric in scenario["rubrics"]
    ]
    prompt = f"""Evaluate one assistant response against the behavioral rubric.
Use only the scenario, response, and criteria below. Be strict: intent or eloquence is not evidence.
Return JSON only in this exact shape:
{{"criteria":[{{"id":"criterion-id","pass":true,"reason":"specific evidence"}}],"summary":"one sentence"}}
Include every criterion exactly once. A criterion passes only when the response visibly satisfies it.

SCENARIO:
{scenario['title']}

PROJECT CONTEXT:
{scenario_context(scenario)}

USER REQUEST:
{scenario['user_prompt']}

RUBRIC:
{json.dumps(rubric_payload, ensure_ascii=False, indent=2)}

ASSISTANT RESPONSE:
{assistant_response}
"""
    raw = chat_completion(
        base_url=args.base_url,
        api_key=args.api_key,
        model=args.judge_model or args.model,
        messages=[
            {
                "role": "system",
                "content": "You are an impartial behavioral-evaluation judge. Output valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        timeout=args.timeout,
    )
    return extract_json_object(raw)


def score_result(
    scenario: dict[str, Any], assistant_response: str, judge: dict[str, Any]
) -> dict[str, Any]:
    expected = {rubric["id"]: rubric for rubric in scenario["rubrics"]}
    judged_items = judge.get("criteria")
    if not isinstance(judged_items, list):
        raise EvalError(f"{scenario['id']}: judge result has no criteria list")
    judged: dict[str, dict[str, Any]] = {}
    for item in judged_items:
        if not isinstance(item, dict) or item.get("id") not in expected:
            raise EvalError(f"{scenario['id']}: judge returned an unknown criterion")
        if item["id"] in judged or not isinstance(item.get("pass"), bool):
            raise EvalError(f"{scenario['id']}: malformed or duplicate criterion {item.get('id')}")
        judged[item["id"]] = item
    missing = set(expected) - set(judged)
    if missing:
        raise EvalError(f"{scenario['id']}: judge omitted criteria: {', '.join(sorted(missing))}")

    total_weight = sum(rubric.get("weight", 1) for rubric in expected.values())
    passed_weight = sum(
        expected[rubric_id].get("weight", 1)
        for rubric_id, item in judged.items()
        if item["pass"]
    )
    critical_failures = [
        rubric_id
        for rubric_id, item in judged.items()
        if expected[rubric_id].get("must_pass", False) and not item["pass"]
    ]
    pattern_failures = [
        pattern
        for pattern in scenario.get("forbidden_patterns", [])
        if re.search(pattern, assistant_response, re.IGNORECASE | re.MULTILINE)
    ]
    score = passed_weight / total_weight
    passed = score >= scenario.get("pass_threshold", 0.8) and not critical_failures and not pattern_failures
    return {
        "scenario_id": scenario["id"],
        "title": scenario["title"],
        "critical": scenario.get("critical", False),
        "passed": passed,
        "score": round(score, 4),
        "critical_failures": critical_failures,
        "forbidden_pattern_matches": pattern_failures,
        "criteria": [judged[rubric_id] for rubric_id in expected],
        "judge_summary": judge.get("summary", ""),
        "response": assistant_response,
    }


def write_report(path: Path, args: argparse.Namespace, results: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(result["passed"] for result in results)
    critical_failed = [result["scenario_id"] for result in results if result["critical"] and not result["passed"]]
    report = {
        "schema_version": "1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": args.model,
        "judge_model": args.judge_model or args.model,
        "summary": {
            "passed": passed,
            "total": len(results),
            "pass_rate": round(passed / len(results), 4),
            "critical_failures": critical_failed,
        },
        "results": results,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL)
    parser.add_argument("--scenario", action="append", default=[], help="Run one scenario id; repeatable")
    parser.add_argument("--validate-only", action="store_true", help="Validate suite structure without API calls")
    parser.add_argument("--responses", type=Path, help="JSON object mapping scenario ids to saved responses")
    parser.add_argument("--output", type=Path, default=Path(".smart/evidence/behavioral-eval.json"))
    parser.add_argument("--model", default=os.environ.get("SMART_EVAL_MODEL", "gpt-5-mini"))
    parser.add_argument("--judge-model", default=os.environ.get("SMART_EVAL_JUDGE_MODEL"))
    parser.add_argument(
        "--base-url",
        default=os.environ.get("SMART_EVAL_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )
    parser.add_argument("--api-key", default=os.environ.get("SMART_EVAL_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--fail-under", type=float, default=0.8)
    args = parser.parse_args(argv)
    if not 0 <= args.fail_under <= 1:
        parser.error("--fail-under must be between 0 and 1")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        suite = load_json(args.suite)
        if not isinstance(suite, dict):
            raise EvalError("Suite root must be a JSON object")
        validate_suite(suite)
        scenarios = select_scenarios(suite, args.scenario)
        if args.validate_only:
            print(f"Valid behavioral suite: {len(scenarios)} scenario(s)")
            return 0
        if not args.api_key:
            raise EvalError("Set SMART_EVAL_API_KEY (or OPENAI_API_KEY) to run generation/judging")
        saved = load_json(args.responses) if args.responses else {}
        if not isinstance(saved, dict):
            raise EvalError("--responses must contain a JSON object mapping ids to responses")
        skill_text = args.skill.read_text(encoding="utf-8")
        results = []
        for scenario in scenarios:
            scenario_id = scenario["id"]
            response = saved.get(scenario_id)
            if response is None:
                response = generate_response(scenario, skill_text, args)
            if not isinstance(response, str) or not response.strip():
                raise EvalError(f"{scenario_id}: saved/generated response is empty")
            result = score_result(scenario, response, judge_response(scenario, response, args))
            results.append(result)
            print(f"{'PASS' if result['passed'] else 'FAIL'} {scenario_id}: {result['score']:.0%}")
        report = write_report(args.output, args, results)
        summary = report["summary"]
        print(f"Result: {summary['passed']}/{summary['total']} ({summary['pass_rate']:.0%}) -> {args.output}")
        return 1 if summary["pass_rate"] < args.fail_under or summary["critical_failures"] else 0
    except (EvalError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
