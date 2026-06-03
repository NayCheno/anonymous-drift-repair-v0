# DriftBench v0 JSONL Schema

Schema version: `driftbench_v0.1`

Each line is one diagnostic example.

## Required top-level fields

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Unique example id. |
| `turns` | list | Conversation turns, each with `role` and `content`. |
| `retrieved` | list | Retrieved evidence chunks, each with `id` and `text`. |
| `tool_outputs` | list | Tool observations, each with `tool` and `content`. |
| `candidate_response` | string | Response or action being diagnosed. |
| `gold` | object | Drift labels and expected repair. |
| `metadata` | object | Construction and provenance metadata. |

## Required `gold` fields

| Field | Type | Meaning |
|---|---|---|
| `drift_types` | list[string] | Zero or more labels from the frozen taxonomy. |
| `expected_action` | string | Primary repair action or `answer_as_is`. |
| `task_success` | boolean | Whether the candidate response satisfies the active state. |
| `schema_version` | string | Must be `driftbench_v0.1`. |
| `annotation_status` | string | `draft` for generated v0 cases. |

## Required `metadata` fields

| Field | Type | Meaning |
|---|---|---|
| `benchmark` | string | Must be `DriftBench`. |
| `schema_version` | string | Must be `driftbench_v0.1`. |
| `construction` | string | Construction method. |
| `source_example_id` | string | Week 1 hand-written template id. |
| `variant_index` | integer | Deterministic generated index. |
| `split` | string | `draft` for Week 2 v0. |
| `perturbation` | string | Main perturbation family. |
| `manual_check_status` | string | `unchecked` until human annotation replaces draft labels. |

## Week 2 v0 boundary

`data/driftbench_v0.jsonl` is a deterministic toy-equivalent draft set. It is intended to validate schema, scripts, metrics, and annotation workflow before external datasets are downloaded and licensed. It must not be reported as a real benchmark result.
