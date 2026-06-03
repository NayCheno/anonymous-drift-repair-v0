#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


CHECKS = [
    {
        "id": "uses_aaai_style",
        "severity": "blocker",
        "pattern": r"\\usepackage\[submission\]\{aaai2026\}",
        "expected": True,
        "message": "Submission source should use the official AAAI style package once the target author kit is selected.",
    },
    {
        "id": "letterpaper_article",
        "severity": "blocker",
        "pattern": r"\\documentclass\[letterpaper\]\{article\}",
        "expected": True,
        "message": "AAAI author kit uses letterpaper article document class.",
    },
    {
        "id": "no_geometry",
        "severity": "blocker",
        "pattern": r"\\usepackage(?:\[[^\]]*\])?\{geometry\}",
        "expected": False,
        "message": "AAAI formatting forbids geometry-based margin changes.",
    },
    {
        "id": "no_hyperref",
        "severity": "blocker",
        "pattern": r"\\usepackage(?:\[[^\]]*\])?\{hyperref\}",
        "expected": False,
        "message": "AAAI 2026 instructions forbid hyperref/navigator packages in submitted source.",
    },
    {
        "id": "single_source_no_input",
        "severity": "blocker",
        "pattern": r"\\input\{",
        "expected": False,
        "message": "AAAI final source should be a single .tex file without section/table input files.",
    },
    {
        "id": "anonymous_author",
        "severity": "warning",
        "pattern": r"\\author\{Anonymous Authors\}",
        "expected": True,
        "message": "Current scaffold should remain anonymous until final author metadata is intentionally added.",
    },
]


def check_source(source: str) -> list[dict[str, object]]:
    results = []
    for check in CHECKS:
        found = bool(re.search(check["pattern"], source))
        passed = found is check["expected"]
        results.append(
            {
                "id": check["id"],
                "severity": check["severity"],
                "passed": passed,
                "expected": check["expected"],
                "found": found,
                "message": check["message"],
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Check paper source readiness for AAAI template migration.")
    parser.add_argument("--input", default="paper/main.tex")
    parser.add_argument("--output", default="results/aaai_template_readiness_v0.json")
    args = parser.parse_args()

    source = (ROOT / args.input).read_text(encoding="utf-8")
    checks = check_source(source)
    report = {
        "input": args.input,
        "target_template": "AAAI 2026 author kit used as current public proxy; AAAI-27 kit not yet confirmed.",
        "template_applied": all(check["passed"] for check in checks if check["severity"] == "blocker"),
        "checks": checks,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
