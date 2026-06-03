#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drift_repair.dataset_adapters import get_adapter, save_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a locally downloaded external dataset file/tree into DriftBench seed JSONL."
    )
    parser.add_argument(
        "--adapter",
        required=True,
        choices=["mtrag", "mtrag_un", "tau_bench", "dialogtool", "longmemeval"],
    )
    parser.add_argument("--input", required=True, help="Local JSON/JSONL file or directory.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of records to write.")
    args = parser.parse_args()

    records = get_adapter(args.adapter).load_records(args.input)
    if args.limit:
        records = records[: args.limit]
    save_jsonl(args.output, records)
    print(f"Wrote {len(records)} records using adapter={args.adapter}: {args.output}")


if __name__ == "__main__":
    main()
