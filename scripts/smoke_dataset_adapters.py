#!/usr/bin/env python
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drift_repair.dataset_adapters import get_adapter


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def assert_record(record: dict) -> None:
    assert record["turns"], record
    assert "gold" in record, record
    assert record["metadata"]["benchmark"] == "DriftBench", record
    assert record["metadata"]["manual_check_status"] == "needs_annotation", record


def main() -> None:
    examples = [
        {
            "id": "rag_case_1",
            "messages": [{"speaker": "user", "text": "Answer from the provided passages."}],
            "documents": [{"doc_id": "d1", "text": "The answer is not specified."}],
            "answer": "The answer is unknown.",
        },
        {
            "task_id": "tool_case_1",
            "trajectory": [{"role": "user", "content": "Refund if eligible."}],
            "tool_outputs": [{"tool": "refund_policy", "result": "not eligible"}],
            "final_response": "Refund denied because the order is not eligible.",
        },
    ]

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "external.jsonl"
        write_jsonl(path, examples)
        for adapter_name in ["mtrag", "mtrag_un", "tau_bench", "dialogtool", "longmemeval"]:
            records = get_adapter(adapter_name).load_records(path)
            assert len(records) == len(examples)
            for record in records:
                assert_record(record)
    print("External dataset adapter smoke test passed.")


if __name__ == "__main__":
    main()
