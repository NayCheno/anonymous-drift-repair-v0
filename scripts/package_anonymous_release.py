#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def release_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def write_zip(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in release_files(root):
            arcname = Path(root.name) / path.relative_to(root)
            zf.write(path, arcname.as_posix())


def sample_checksums(root: Path, limit: int = 20) -> list[dict[str, Any]]:
    rows = []
    for path in release_files(root)[:limit]:
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Package the local anonymous release tree and write checksum metadata.")
    parser.add_argument("--root", default="release/anonymous-drift-repair-v0")
    parser.add_argument("--output", default="release/anonymous-drift-repair-v0.zip")
    parser.add_argument("--manifest-output", default="results/anonymous_release_package_v0.json")
    args = parser.parse_args()

    release_root = (ROOT / args.root).resolve()
    if not release_root.exists():
        raise SystemExit(f"Release root does not exist: {release_root}")
    release_manifest = release_root / "RELEASE_MANIFEST.txt"
    if not release_manifest.exists():
        raise SystemExit(f"Release manifest does not exist: {release_manifest}")

    zip_path = (ROOT / args.output).resolve()
    write_zip(release_root, zip_path)
    files = release_files(release_root)
    report = {
        "release_root": args.root,
        "package": args.output,
        "package_exists": zip_path.exists(),
        "package_bytes": zip_path.stat().st_size,
        "package_sha256": sha256_file(zip_path),
        "n_files": len(files),
        "release_manifest_sha256": sha256_file(release_manifest),
        "sample_file_checksums": sample_checksums(release_root),
        "note": "The zip file is generated under release/ and ignored by git; this JSON is the tracked checksum record.",
    }
    out = ROOT / args.manifest_output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {zip_path}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
