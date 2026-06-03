# External Dataset Adapter Notes

The repository includes local-file adapters for the external datasets planned in the paper:

| Adapter | Intended source | Current support |
|---|---|---|
| `mtrag` | MTRAG | Local JSON/JSONL normalization |
| `mtrag_un` | MTRAG-UN | Local JSON/JSONL normalization |
| `tau_bench` | tau-bench | Local JSON/JSONL normalization |
| `dialogtool` | DialogTool | Local JSON/JSONL normalization |
| `longmemeval` | LongMemEval | Local JSON/JSONL normalization |

These adapters do not download, redistribute, or license external datasets. They are schema-normalization entrypoints for data that has already been obtained according to the upstream dataset terms.

The current license review is stored in `configs/datasets.yaml` and checked by `python scripts/validate_dataset_licenses.py`. MTRAG/MTRAG-UN, tau-bench, and LongMemEval have recorded upstream licenses for local-only use; DialogTool remains pending because no authoritative public repository/license was confirmed. The DialogTool negative-evidence review is recorded in `docs/dialogtool_source_review.md` and `results/dialogtool_source_review_v0.json`.

## Conversion

Use:

```bash
python scripts/convert_external_dataset.py --adapter mtrag --input external/mt-rag-benchmark --output data/external_mtrag_seed.jsonl
```

The `--input` path may be a JSONL file, a JSON file, or a directory containing JSON/JSONL files. The converter accepts common field names for:

- conversation turns: `turns`, `messages`, `conversation`, `dialogue`, `history`, `trajectory`;
- retrieved context: `retrieved`, `documents`, `contexts`, `passages`, `evidence`, `retrievals`;
- tool observations: `tool_outputs`, `tools`, `tool_calls`, `observations`, `api_results`;
- candidate answer: `candidate_response`, `response`, `answer`, `assistant_response`, `output`, `prediction`, `final_response`.

## Output Status

Converted records are marked as:

- `metadata.construction = <adapter>_adapter_seed`;
- `metadata.perturbation = needs_drift_annotation`;
- `metadata.manual_check_status = needs_annotation`;
- `gold.annotation_status = unlabeled_external_seed` when no labels are present;
- `gold.annotation_status = external_gold_seed_unverified` when the source record already contains gold fields.

This means the adapter output is a seed format for perturbation and annotation. Source-provided labels are preserved for inspection but still require project-specific verification. Adapter output must not be reported as a labeled DriftBench split until drift labels, repair actions, task success labels, and license checks are completed.

## Smoke Test

Run:

```bash
python scripts/smoke_dataset_adapters.py
```

This test uses temporary synthetic JSONL records and verifies that each external adapter produces non-empty DriftBench-shaped seed records.
