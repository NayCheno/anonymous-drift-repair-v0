# Deterministic v0 Model and Retrieval Configuration

This document freezes the model and retrieval settings for the deterministic v0 scaffold. It does not describe final real-model experiments.

## Models

The v0 scaffold uses local deterministic rules only:

| Role | Name | Provider | Version | Enabled |
|---|---|---|---|---|
| Generator | `dummy_generator` | `local_rules` | `deterministic_v0.1` | yes |
| Verifier | `dummy_verifier` | `local_rules` | `deterministic_v0.1` | yes |

Placeholder API and open-source models are listed in `configs/models.yaml` but disabled. Their versions, API dates, and decoding parameters must be filled before model-backed experiments.

## Optional LLM Reviewer

The human-validation workflow can be assisted by an OpenAI-compatible LLM reviewer using local `.env` credentials. The local configuration uses `mimo-v2.5` through the Mimo endpoint. The current v0 packet has completed LLM-reviewed annotations for 240 A items and 48 B items; these outputs should be reported as LLM-reviewed validation, not as human-only annotation.

## Decoding Parameters

The enabled v0 rule models use deterministic decoding placeholders:

```yaml
temperature: 0.0
top_p: 1.0
max_output_tokens: 256
```

These values document the reproducibility contract for the scaffold. They are not evidence that an external LLM was called.

## Retrieval

The v0 retriever is an in-memory keyword scaffold:

| Setting | Value |
|---|---|
| Type | `keyword` |
| Version | `deterministic_v0.1` |
| Corpus | `data/toy_corpus.jsonl` |
| top-k | `3` |
| Chunking | one JSONL record per chunk |
| Index | in-memory keyword index |

Preprocessing is lowercase normalization, punctuation stripping, and whitespace splitting. The scaffold does not persist an index. Real experiments must replace this with a documented retriever, corpus preprocessing pipeline, chunking policy, and reproducible index build.

## Validation

Run:

```bash
python scripts/validate_repro_config.py
```

The validator checks that enabled models have versions and decoding parameters, that the retriever has top-k/chunking/index fields, and that the deterministic corpus path exists.
