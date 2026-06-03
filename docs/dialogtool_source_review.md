# DialogTool Source Review

Review date: 2026-06-03

This note records the source and license review for the planned `dialogtool` external adapter. It is a negative-evidence record: the paper exists, but this pass did not confirm an authoritative public dataset/code repository or dataset license.

## Reviewed Sources

| Source | URL | Finding |
|---|---|---|
| arXiv record | `https://arxiv.org/abs/2505.13328` | Paper record for "Rethinking Stateful Tool Use in Multi-Turn Dialogues: Benchmarks and Challenges"; arXiv page lists code/data discovery widgets but no confirmed official repository in the page content reviewed. |
| ACL Anthology record | `https://aclanthology.org/2025.findings-acl.284/` | Peer-reviewed Findings 2025 publication record with PDF/DOI; no official dataset repository or dataset license link found in the page content reviewed. |
| Web search | `"DialogTool" "Stateful Tool Use" GitHub`, `"DialogTool" "2505.13328"`, `"Rethinking Stateful Tool Use in Multi-Turn Dialogues" DialogTool` | Results pointed to paper pages and third-party paper indexes, not an authoritative upstream data/code repository with a license. |

## Current Decision

- Keep `dialogtool.enabled = False`.
- Keep `dialogtool.license_status = pending`.
- Keep `dialogtool.redistribution = unknown`.
- Do not include DialogTool data in deterministic v0 reproduction, release packages, or reported benchmark claims.

DialogTool can be reconsidered only after an authoritative upstream repository or direct author-provided distribution terms are confirmed and recorded in `configs/datasets.yaml`.
