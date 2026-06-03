#!/usr/bin/env python
from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


AAAI_PREAMBLE = r"""\documentclass[letterpaper]{article}
\usepackage[submission]{aaai2026}
\usepackage{times}
\usepackage{helvet}
\usepackage{courier}
\usepackage{booktabs}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{url}

"""


def inline_inputs(source: str, base_dir: Path) -> str:
    pattern = re.compile(r"\\input\{([^}]+)\}")

    def replace(match: re.Match[str]) -> str:
        rel = match.group(1)
        path = base_dir / f"{rel}.tex"
        if not path.exists():
            path = base_dir / rel
        if not path.exists():
            raise FileNotFoundError(f"Cannot inline missing input: {rel}")
        return "% BEGIN inlined " + rel + "\n" + path.read_text(encoding="utf-8") + "% END inlined " + rel

    return pattern.sub(replace, source)


def strip_current_preamble(source: str) -> str:
    begin = source.find(r"\begin{document}")
    if begin < 0:
        raise ValueError("Missing \\begin{document}")
    body = source[begin:]
    body = body.replace(r"\maketitle", r"\maketitle", 1)
    return body


def build_candidate(source: str, base_dir: Path) -> str:
    title = re.search(r"\\title\{.*?\}", source, flags=re.DOTALL)
    author = re.search(r"\\author\{.*?\}", source, flags=re.DOTALL)
    date = re.search(r"\\date\{.*?\}", source, flags=re.DOTALL)
    metadata = "\n".join(
        match.group(0)
        for match in (title, author, date)
        if match is not None
    )
    body = strip_current_preamble(source)
    for item in (title, author, date):
        if item is not None:
            body = body.replace(item.group(0), "", 1)
    body = inline_inputs(body, base_dir)
    return AAAI_PREAMBLE + metadata + "\n\n" + body


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a single-source AAAI template migration candidate.")
    parser.add_argument("--input", default="paper/main.tex")
    parser.add_argument("--output", default="paper/main_aaai2026_candidate.tex")
    args = parser.parse_args()

    input_path = ROOT / args.input
    output_path = ROOT / args.output
    source = input_path.read_text(encoding="utf-8")
    candidate = build_candidate(source, input_path.parent)
    output_path.write_text(candidate, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
