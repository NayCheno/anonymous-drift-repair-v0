# AAAI Template Migration Status

Checked on 2026-06-03. I did not find a public AAAI-27 author kit in the current sources. The latest public proxy located during this pass is the AAAI 2026 author kit, surfaced through Overleaf and attributed there to the official AAAI source at `https://aaai.org/authorkit26/`.

This repository now applies the current public AAAI 2026 proxy format to `paper/main.tex` as the working submission source. This is still not a claim that the final AAAI-27 author kit has been released or adopted; the target kit must be rechecked before final submission.

## Current Public Proxy Requirements

The AAAI 2026 LaTeX source indicates:

- use `\documentclass[letterpaper]{article}`;
- use `\usepackage[submission]{aaai2026}`;
- keep Times/Helvetica/Courier font packages;
- do not use `geometry` to alter margins;
- do not use `hyperref` in submitted source;
- keep submitted source as a single `.tex` file, with no `\input{...}` section or table files;
- use the official AAAI bibliography style when migrating references.

## Current Scaffold Status

`paper/main.tex` now uses the current public AAAI 2026 proxy style line, letterpaper article class, anonymous author metadata, and single-source inlined generated tables. It removes `geometry`, `hyperref`, and `\input{...}` from the main source.

`paper/main_aaai2026_candidate.tex` is retained as the generated proxy candidate for auditability. It should match the same proxy constraints as `paper/main.tex`; future AAAI-27 migration can regenerate or replace both once the target kit is selected.

Run:

```bash
python scripts/check_aaai_template_readiness.py
python scripts/make_aaai_source_candidate.py
python scripts/check_aaai_template_readiness.py --input paper/main_aaai2026_candidate.tex --output results/aaai_template_candidate_readiness_v0.json
```

The generated `results/aaai_template_readiness_v0.json` is expected to report `template_applied: true` for the current public AAAI 2026 proxy constraints. Final AAAI-27 compliance remains a separate pre-submission check.
