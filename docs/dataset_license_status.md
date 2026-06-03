# Dataset License Status

This document records the deterministic v0 dataset license gate and the current upstream-source review. It is not permission to redistribute external datasets; external adapters remain disabled and local-only until data has been obtained from upstream under the relevant terms.

| Dataset | Enabled | Source | License status | SPDX | Redistribution | Notes |
|---|---:|---|---|---|---|---|
| `toy` | yes | internal | `internal_scaffold` | n/a | `allowed` | Hand-written examples created for this scaffold. |
| `driftbench_v0` | yes | internal | `internal_scaffold` | n/a | `allowed` | Generated from internal toy templates. |
| `mtrag` | no | `https://github.com/IBM/mt-rag-benchmark` | `checked` | `Apache-2.0` | `not_redistributed` | Local adapter only. |
| `mtrag_un` | no | `https://github.com/IBM/mt-rag-benchmark` | `checked` | `Apache-2.0` | `not_redistributed` | Same upstream repository as MTRAG-UN paper. |
| `tau_bench` | no | `https://github.com/sierra-research/tau-bench` | `checked` | `MIT` | `not_redistributed` | Local adapter only. |
| `dialogtool` | no | `https://arxiv.org/abs/2505.13328` | `pending` | `unknown` | `unknown` | Paper and ACL record located; no authoritative public repository/license confirmed. See `docs/dialogtool_source_review.md`. |
| `longmemeval` | no | `https://github.com/xiaowu0162/LongMemEval` | `checked` | `MIT` | `not_redistributed` | Local adapter only; dataset is downloaded from upstream by the user. |

Run:

```bash
python scripts/validate_dataset_licenses.py
```

The validator writes `results/dataset_license_review_v0.json`. It permits enabled datasets only when `license_status` is `internal_scaffold` or `checked` and redistribution is `allowed` or `not_redistributed`. This prevents accidental use of pending external data in reproduction runs.

`DialogTool` remains pending. The source-review evidence is recorded in `docs/dialogtool_source_review.md` and `results/dialogtool_source_review_v0.json`, so the global reproducibility checklist still does not mark all dataset licenses as completed.
