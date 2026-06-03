#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from drift_repair.dataset_adapters import load_jsonl, save_jsonl
from drift_repair.pipeline import SageRPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SAGE-R on a JSONL dataset.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    examples = load_jsonl(args.dataset)
    pipe = SageRPipeline()
    records = []
    for ex in examples:
        result = pipe.run_one(ex).to_dict()
        result["gold"] = ex.gold
        records.append(result)
    save_jsonl(args.output, records)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
