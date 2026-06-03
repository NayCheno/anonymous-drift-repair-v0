# Anonymous Release Plan

## Repository structure

```text
anonymous-drift-repair/
  paper/
  src/
  scripts/
  configs/
  data_sample/
  README.md
```

Build the local v0 release tree:

```bash
python scripts/build_anonymous_release.py --clean
```

This creates `release/anonymous-drift-repair-v0/` from `MANIFEST.txt` and writes `RELEASE_MANIFEST.txt` inside the release tree. The local `release/` directory is ignored by git.

Package the local tree and write a tracked checksum report:

```bash
python scripts/package_anonymous_release.py
python scripts/validate_anonymous_release_manifest.py
python scripts/package_anonymous_git_bundle.py
python scripts/verify_anonymous_git_bundle.py
python scripts/verify_anonymous_remote_import.py
python scripts/publish_anonymous_remote.py --remote-url ANONYMOUS_REMOTE_URL_REQUIRED
```

This writes `release/anonymous-drift-repair-v0.zip`, `release/anonymous-drift-repair-v0.bundle`, `results/anonymous_release_package_v0.json`, `results/anonymous_release_manifest_validation_v0.json`, `results/anonymous_git_bundle_v0.json`, `results/anonymous_git_bundle_verify_v0.json`, `results/anonymous_remote_import_verify_v0.json`, and a dry-run `results/anonymous_remote_publish_v0.json`. The zip, bundle, verification clones, local bare-remote simulation, and publish clone stay under ignored `release/`; the JSON checksum and verification records are tracked for upload dry runs and manual release checks. Checksum, readiness, handoff, and completion-audit reports that mention release hashes are intentionally excluded from the release tree to avoid stale self-referential package metadata.

## Remove before release

- Author names.
- Institution names.
- Private API keys.
- Non-anonymous file metadata.
- Internal paths or usernames.
- Private datasets.

## Keep in release

- Toy smoke test.
- DriftBench schema.
- Annotation guidelines.
- Scripts for reproducing tables.
- Clear instructions for downloading external datasets.

## Artifact statement draft

We release code for constructing DriftBench perturbations, running diagnosis and repair pipelines, and computing all reported metrics. For datasets that cannot be redistributed, we provide conversion scripts and instructions to reproduce the benchmark from the original sources subject to their licenses.

## Current v0 audit

Run:

```bash
python scripts/audit_anonymous_release.py --output results/anonymous_release_audit_v0.md
python scripts/audit_anonymous_release.py --root release/anonymous-drift-repair-v0 --output results/anonymous_release_tree_audit_v0.md
python scripts/package_anonymous_release.py
python scripts/validate_anonymous_release_manifest.py
python scripts/package_anonymous_git_bundle.py
python scripts/verify_anonymous_git_bundle.py
python scripts/verify_anonymous_remote_import.py
python scripts/publish_anonymous_remote.py --remote-url ANONYMOUS_REMOTE_URL_REQUIRED
```

Current deterministic v0 audit result:

```text
Tracked files findings: 0
Release tree findings: 0
Package checksum report: results/anonymous_release_package_v0.json
Release manifest validation report: results/anonymous_release_manifest_validation_v0.json
Git bundle checksum report: results/anonymous_git_bundle_v0.json
Git bundle verification report: results/anonymous_git_bundle_verify_v0.json
Local bare-remote import verification report: results/anonymous_remote_import_verify_v0.json
Hosted remote publish dry-run/report: results/anonymous_remote_publish_v0.json
```

This scan checks tracked text files for obvious local paths, username paths, API-key-shaped strings, author markers outside references, and institution markers outside allowed planning documents. It is a release gate, not a substitute for final manual review.

For a single aggregate view of deterministic v0 readiness and remaining final-submission blockers, run:

```bash
python scripts/check_remote_anonymous_readiness.py
python scripts/make_submission_readiness.py
```

Remote publication instructions are recorded in `docs/anonymous_remote_repository.md`. The current environment can prepare and audit the local package, but remote repository creation remains an external step.
