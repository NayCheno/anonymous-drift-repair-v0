#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DRIFT_TYPES = [
    "G1_goal_drift",
    "G2_constraint_drift",
    "E1_evidence_drift",
    "E2_retrieval_drift",
    "T1_tool_state_drift",
    "M1_memory_drift",
    "U1_abstention_drift",
]
ALLOWED_REPAIRS = [
    "answer_as_is",
    "revise_response",
    "re_retrieve",
    "re_retrieve_and_replan",
    "re_retrieve_and_verify",
    "call_tool",
    "cross_validate_tool",
    "ask_clarification",
    "abstain",
    "rollback_and_replan",
    "rewrite_query_and_retrieve",
    "update_memory_priority",
]
DRIFT_ALIASES = {
    "G1": "G1_goal_drift",
    "G2": "G2_constraint_drift",
    "E1": "E1_evidence_drift",
    "E2": "E2_retrieval_drift",
    "T1": "T1_tool_state_drift",
    "M1": "M1_memory_drift",
    "U1": "U1_abstention_drift",
}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            sep = "=" if "=" in line else ":" if ":" in line else ""
            if not sep:
                continue
            key, value = line.split(sep, 1)
            values[key.strip().lower()] = value.strip().strip('"').strip("'")
    for key, value in os.environ.items():
        values.setdefault(key.lower(), value)
    return values


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def taxonomy_text() -> str:
    return "\n".join(
        [
            "G1_goal_drift: follows an obsolete or incorrect user goal.",
            "G2_constraint_drift: violates an active user/system/domain constraint.",
            "E1_evidence_drift: generated factual claims are unsupported or contradicted by evidence.",
            "E2_retrieval_drift: retrieved context remains aligned with stale intent.",
            "T1_tool_state_drift: action or response contradicts tool/database observations.",
            "M1_memory_drift: uses obsolete memory after an update or supersession.",
            "U1_abstention_drift: answers when it should clarify/abstain, or refuses when it can answer.",
        ]
    )


def prompt_for(row: dict[str, Any]) -> list[dict[str, str]]:
    compact = {
        "id": row["id"],
        "turns": row.get("turns", []),
        "retrieved": row.get("retrieved", []),
        "tool_outputs": row.get("tool_outputs", []),
        "candidate_response": row.get("candidate_response", ""),
    }
    system = (
        "You are a strict annotation reviewer for state drift in multi-turn RAG/tool agents. "
        "Return only valid JSON with keys drift_types, severity, expected_repair, task_success, notes. "
        "Use severity 0 for no drift, 1 minor, 2 major, 3 critical. "
        f"Allowed drift_types: {ALLOWED_DRIFT_TYPES}. Use [] for no drift. "
        f"Allowed expected_repair: {ALLOWED_REPAIRS}."
    )
    user = (
        "Taxonomy:\n"
        f"{taxonomy_text()}\n\n"
        "Annotate this item. task_success means whether the candidate response/action succeeds under the active state.\n"
        f"{json.dumps(compact, ensure_ascii=False, indent=2)}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_json_response(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end >= start:
        stripped = stripped[start : end + 1]
    return json.loads(stripped)


def validate_labels(labels: dict[str, Any]) -> dict[str, Any]:
    drift_types = labels.get("drift_types", [])
    if drift_types in (None, ["NONE"], "NONE"):
        drift_types = []
    if not isinstance(drift_types, list):
        raise ValueError("drift_types must be a list")
    drift_types = [DRIFT_ALIASES.get(str(item), str(item)) for item in drift_types if item != "NONE"]
    invalid = sorted(set(drift_types) - set(ALLOWED_DRIFT_TYPES))
    if invalid:
        raise ValueError(f"invalid drift_types: {invalid}")
    severity = labels.get("severity")
    if severity not in {0, 1, 2, 3}:
        raise ValueError("severity must be 0, 1, 2, or 3")
    expected_repair = labels.get("expected_repair", "")
    if isinstance(expected_repair, list) and expected_repair:
        expected_repair = expected_repair[0]
    if expected_repair not in ALLOWED_REPAIRS:
        raise ValueError(f"invalid expected_repair: {expected_repair}")
    task_success = labels.get("task_success")
    if not isinstance(task_success, bool):
        raise ValueError("task_success must be boolean")
    return {
        "drift_types": drift_types,
        "severity": severity,
        "expected_repair": expected_repair,
        "task_success": task_success,
        "notes": str(labels.get("notes", ""))[:500],
    }


def call_chat(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    timeout: int,
    response_format_json: bool,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0,
    }
    if response_format_json:
        body["response_format"] = {"type": "json_object"}
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def annotate_rows(
    rows: list[dict[str, Any]],
    base_url: str,
    api_key: str,
    model: str,
    max_items: int | None,
    timeout: int,
    sleep_s: float,
    response_format_json: bool,
    concurrency: int,
    existing_by_id: dict[str, dict[str, Any]] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    outputs: list[dict[str, Any] | None] = [None] * (len(rows) if max_items is None else min(max_items, len(rows)))
    errors = []
    limit = len(rows) if max_items is None else min(max_items, len(rows))
    selected_rows = rows[:limit]

    def annotate_one(index: int, row: dict[str, Any]) -> tuple[int, dict[str, Any], dict[str, Any] | None]:
        if existing_by_id and row.get("id") in existing_by_id:
            existing = existing_by_id[row["id"]]
            try:
                validate_labels(existing.get("labels_to_fill", {}))
                return index, existing, None
            except ValueError:
                pass
        out = dict(row)
        try:
            content = call_chat(base_url, api_key, model, prompt_for(row), timeout, response_format_json)
            labels = validate_labels(parse_json_response(content))
            labels["reviewer"] = "llm_mimo_openai_compatible"
            labels["review_model"] = model
            out["labels_to_fill"] = labels
            return index, out, None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:500]
            error = {"id": row.get("id", ""), "error": "HTTPError", "message": body or str(exc)[:300]}
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
            error = {"id": row.get("id", ""), "error": type(exc).__name__, "message": str(exc)[:300]}
        return index, out, error

    if concurrency <= 1:
        for idx, row in enumerate(selected_rows):
            out_idx, out, error = annotate_one(idx, row)
            outputs[out_idx] = out
            if error:
                errors.append(error)
            if sleep_s and idx + 1 < limit:
                time.sleep(sleep_s)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(annotate_one, idx, row) for idx, row in enumerate(selected_rows)]
            for future in as_completed(futures):
                out_idx, out, error = future.result()
                outputs[out_idx] = out
                if error:
                    errors.append(error)
                if sleep_s:
                    time.sleep(sleep_s)
    return [row for row in outputs if row is not None], errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill blinded annotation packets using an OpenAI-compatible LLM reviewer.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--status-output", required=True)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-items", type=int)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--sleep-s", type=float, default=0.0)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--resume", action="store_true", help="Reuse complete rows already present in --output.")
    parser.add_argument(
        "--response-format-json",
        action="store_true",
        help="Request OpenAI JSON-object response_format. Disabled by default for broader compatible API support.",
    )
    args = parser.parse_args()

    env = load_env(ROOT / args.env_file)
    base_url = env.get("openai_base_url") or env.get("openai_api_base") or env.get("base_url")
    api_key = env.get("openai_api_key") or env.get("api_key")
    model = args.model or env.get("openai_model") or "gpt-4o-mini"
    if not base_url or not api_key:
        raise SystemExit("Missing openai_base_url/openai_api_key in env file or environment.")

    rows = load_jsonl(ROOT / args.input)
    existing_by_id = None
    output_path = ROOT / args.output
    if args.resume and output_path.exists():
        existing_by_id = {row["id"]: row for row in load_jsonl(output_path)}
    outputs, errors = annotate_rows(
        rows,
        base_url,
        api_key,
        model,
        args.max_items,
        args.timeout,
        args.sleep_s,
        args.response_format_json,
        max(1, args.concurrency),
        existing_by_id,
    )
    write_jsonl(ROOT / args.output, outputs)
    status = {
        "input": args.input,
        "output": args.output,
        "model": model,
        "n_input": len(rows),
        "n_requested": len(outputs),
        "n_completed": len(outputs) - len(errors),
        "n_errors": len(errors),
        "concurrency": max(1, args.concurrency),
        "resume": args.resume,
        "errors": errors[:20],
        "complete": not errors and len(outputs) == (args.max_items or len(rows)),
        "note": "Uses OpenAI-compatible reviewer config from env; API key is never written to outputs.",
    }
    status_path = ROOT / args.status_output
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(status, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {ROOT / args.output}")
    print(f"Wrote {status_path}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
