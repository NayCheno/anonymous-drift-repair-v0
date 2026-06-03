from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List

from .schemas import Example


SCHEMA_VERSION = "driftbench_v0.1"


def load_jsonl(path: str | Path) -> List[Example]:
    path = Path(path)
    examples = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(Example.from_dict(json.loads(line)))
    return examples


def load_raw_records(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if path.is_dir():
        records: list[dict[str, Any]] = []
        for child in sorted(path.rglob("*.jsonl")) + sorted(path.rglob("*.json")):
            records.extend(load_raw_records(child))
        return records

    if path.suffix.lower() == ".jsonl":
        records = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("examples", "data", "records", "instances", "items", "conversations"):
                if isinstance(data.get(key), list):
                    return data[key]
            return [data]
        raise ValueError(f"JSON dataset root must be an object or list: {path}")

    raise ValueError(f"Unsupported dataset file type: {path}")


def save_jsonl(path: str | Path, records: Iterable[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


class DatasetAdapter:
    def load(self, path: str | Path) -> List[Example]:
        raise NotImplementedError

    def load_records(self, path: str | Path) -> list[dict[str, Any]]:
        return [example.to_dict() for example in self.load(path)]


class ToyAdapter(DatasetAdapter):
    def load(self, path: str | Path) -> List[Example]:
        return load_jsonl(path)


def _first_text(record: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = record.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
    return ""


def _coerce_turns(record: dict[str, Any]) -> list[dict[str, str]]:
    raw_turns = None
    for key in ("turns", "messages", "conversation", "dialogue", "history", "trajectory"):
        value = record.get(key)
        if isinstance(value, list):
            raw_turns = value
            break

    turns: list[dict[str, str]] = []
    if raw_turns:
        for item in raw_turns:
            if isinstance(item, str):
                turns.append({"role": "user", "content": item})
                continue
            if not isinstance(item, dict):
                continue
            role = _first_text(item, ("role", "speaker", "from", "author", "type")) or "user"
            content = _first_text(
                item,
                ("content", "text", "utterance", "message", "value", "query"),
            )
            if content:
                turns.append({"role": role, "content": content})

    question = _first_text(record, ("question", "query", "user_query", "instruction", "task", "prompt"))
    if not turns and question:
        turns.append({"role": "user", "content": question})
    if not turns:
        turns.append({"role": "user", "content": "External dataset record requires manual turn mapping."})
    return turns


def _coerce_evidence(record: dict[str, Any]) -> list[dict[str, str]]:
    raw_items = None
    for key in ("retrieved", "documents", "contexts", "passages", "evidence", "retrievals"):
        value = record.get(key)
        if isinstance(value, list):
            raw_items = value
            break

    evidence: list[dict[str, str]] = []
    for index, item in enumerate(raw_items or []):
        if isinstance(item, str):
            evidence.append({"id": f"doc_{index}", "text": item})
            continue
        if not isinstance(item, dict):
            continue
        text = _first_text(item, ("text", "content", "passage", "document", "body", "snippet"))
        if text:
            evidence_id = (
                _first_text(item, ("id", "doc_id", "document_id", "pid", "title"))
                or f"doc_{index}"
            )
            evidence.append({"id": evidence_id, "text": text})
    return evidence


def _coerce_tool_outputs(record: dict[str, Any]) -> list[dict[str, str]]:
    raw_items = None
    for key in ("tool_outputs", "tools", "tool_calls", "observations", "api_results"):
        value = record.get(key)
        if isinstance(value, list):
            raw_items = value
            break

    outputs: list[dict[str, str]] = []
    for index, item in enumerate(raw_items or []):
        if isinstance(item, str):
            outputs.append({"tool": f"tool_{index}", "content": item})
            continue
        if not isinstance(item, dict):
            continue
        tool = _first_text(item, ("tool", "name", "api", "function", "action")) or f"tool_{index}"
        content = _first_text(item, ("content", "text", "result", "observation", "output", "message"))
        if content:
            outputs.append({"tool": tool, "content": content})
    return outputs


def _coerce_gold(record: dict[str, Any]) -> dict[str, Any]:
    gold = record.get("gold") if isinstance(record.get("gold"), dict) else {}
    drift_types = gold.get("drift_types") if isinstance(gold.get("drift_types"), list) else []
    expected_action = gold.get("expected_action") or "answer_as_is"
    task_success = gold.get("task_success")
    if not isinstance(task_success, bool):
        task_success = True
    default_status = "external_gold_seed_unverified" if gold else "unlabeled_external_seed"
    return {
        "drift_types": drift_types,
        "expected_action": expected_action,
        "task_success": task_success,
        "schema_version": gold.get("schema_version", SCHEMA_VERSION),
        "annotation_status": gold.get("annotation_status", default_status),
    }


class GenericExternalAdapter(DatasetAdapter):
    dataset_name = "external"

    def normalize_record(self, record: dict[str, Any], index: int) -> dict[str, Any]:
        source_id = (
            _first_text(record, ("id", "uid", "qid", "conversation_id", "task_id"))
            or str(index)
        )
        candidate_response = _first_text(
            record,
            (
                "candidate_response",
                "response",
                "answer",
                "assistant_response",
                "output",
                "prediction",
                "final_response",
            ),
        )
        normalized = {
            "id": f"{self.dataset_name}_{source_id}",
            "turns": _coerce_turns(record),
            "retrieved": _coerce_evidence(record),
            "tool_outputs": _coerce_tool_outputs(record),
            "candidate_response": candidate_response,
            "gold": _coerce_gold(record),
            "metadata": {
                "benchmark": "DriftBench",
                "schema_version": SCHEMA_VERSION,
                "construction": f"{self.dataset_name}_adapter_seed",
                "source_example_id": source_id,
                "variant_index": index,
                "split": _first_text(record, ("split", "subset")) or "external_seed",
                "perturbation": "needs_drift_annotation",
                "manual_check_status": "needs_annotation",
            },
        }
        return normalized

    def load_records(self, path: str | Path) -> list[dict[str, Any]]:
        return [self.normalize_record(record, index) for index, record in enumerate(load_raw_records(path))]

    def load(self, path: str | Path) -> List[Example]:
        return [Example.from_dict(record) for record in self.load_records(path)]


class MTRAGAdapter(GenericExternalAdapter):
    dataset_name = "mtrag"


class MTRAGUNAdapter(GenericExternalAdapter):
    dataset_name = "mtrag_un"


class TauBenchAdapter(GenericExternalAdapter):
    dataset_name = "tau_bench"


class DialogToolAdapter(GenericExternalAdapter):
    dataset_name = "dialogtool"


class LongMemEvalAdapter(GenericExternalAdapter):
    dataset_name = "longmemeval"


ADAPTERS: dict[str, DatasetAdapter] = {
    "toy": ToyAdapter(),
    "mtrag": MTRAGAdapter(),
    "mtrag_un": MTRAGUNAdapter(),
    "tau_bench": TauBenchAdapter(),
    "dialogtool": DialogToolAdapter(),
    "longmemeval": LongMemEvalAdapter(),
}


def get_adapter(name: str) -> DatasetAdapter:
    try:
        return ADAPTERS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown dataset adapter: {name}") from exc
