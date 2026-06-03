# FAQ

## Is this a benchmark paper or method paper?

Best positioning: both, but method-led. DriftBench supports the method and analysis; SAGE-R is the main technical contribution.

## Do we need to train a model?

No. The recommended AAAI sprint version is inference-time and model-agnostic.

## What is the main risk?

Being perceived as an engineering pipeline. Mitigate by emphasizing formal problem definition, diagnostic labels, metrics, ablations, and failure analysis.

## Which dataset should be integrated first?

Start with MTRAG/MTRAG-UN for RAG drift, then add one tool-use dataset such as tau-bench or DialogTool.

## What is the strongest experiment?

Show that typed repair improves recovery and reduces over-repair compared with generic self-reflection across drift types.
