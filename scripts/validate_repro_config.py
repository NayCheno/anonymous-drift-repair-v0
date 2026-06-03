#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_model_group(group_name: str, models: list[dict[str, Any]], errors: list[str]) -> None:
    require(bool(models), f"models.{group_name} must not be empty", errors)
    for model in models:
        name = model.get("name", "<missing>")
        if model.get("enabled"):
            require(bool(model.get("version")), f"{group_name}.{name} missing version", errors)
            decoding = model.get("decoding", {})
            for key in ("temperature", "top_p", "max_output_tokens"):
                require(decoding.get(key) is not None, f"{group_name}.{name} missing decoding.{key}", errors)
        if model.get("provider") == "placeholder":
            require(not model.get("enabled"), f"placeholder model {group_name}.{name} must be disabled", errors)


def validate_retriever(config: dict[str, Any], errors: list[str]) -> None:
    retriever = config.get("retriever", {})
    require(bool(retriever.get("type")), "retriever.type missing", errors)
    require(bool(retriever.get("version")), "retriever.version missing", errors)
    require(isinstance(retriever.get("top_k"), int), "retriever.top_k must be an integer", errors)
    require(bool(retriever.get("preprocessing")), "retriever.preprocessing missing", errors)
    require(bool(retriever.get("chunking")), "retriever.chunking missing", errors)
    require(bool(retriever.get("index")), "retriever.index missing", errors)
    corpus_path = retriever.get("corpus_path")
    if corpus_path:
        require((ROOT / corpus_path).exists(), f"retriever.corpus_path does not exist: {corpus_path}", errors)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate deterministic v0 reproducibility config.")
    parser.add_argument("--config", default="configs/models.yaml")
    args = parser.parse_args()

    with (ROOT / args.config).open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    errors: list[str] = []
    models = config.get("models", {})
    validate_model_group("generator", models.get("generator", []), errors)
    validate_model_group("verifier", models.get("verifier", []), errors)
    validate_retriever(config, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Reproducibility config valid: {args.config}")


if __name__ == "__main__":
    main()
