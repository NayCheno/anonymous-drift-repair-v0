# Anonymous Remote Repository

This repository has a local anonymous release package and a hosted anonymous remote publication report for the deterministic v0 scaffold.

## Current Local Evidence

Run:

```bash
python scripts/build_anonymous_release.py --clean
python scripts/audit_anonymous_release.py --output results/anonymous_release_audit_v0.md
python scripts/audit_anonymous_release.py --root release/anonymous-drift-repair-v0 --output results/anonymous_release_tree_audit_v0.md
python scripts/package_anonymous_release.py
python scripts/package_anonymous_git_bundle.py
python scripts/verify_anonymous_git_bundle.py
python scripts/verify_anonymous_remote_import.py
python scripts/publish_anonymous_remote.py --remote-url ANONYMOUS_REMOTE_URL_REQUIRED
python scripts/check_remote_anonymous_readiness.py
python scripts/make_submission_handoff.py
```

The remote-readiness checker writes `results/anonymous_remote_readiness_v0.json`. It verifies that the local zip package exists, the git bundle can be cloned, the bundle can be pushed into a local bare-remote simulation, anonymous audits pass, and records whether the anonymous hosted remote requirement is satisfied. Once a hosted remote has already been published and verified by commit match, GitHub CLI availability is no longer required for the readiness gate.

## Publish Procedure

1. Create a new anonymous repository under the submission account.
2. Upload `release/anonymous-drift-repair-v0.zip`, import `release/anonymous-drift-repair-v0.bundle`, or push the contents of `release/anonymous-drift-repair-v0/`.
3. Keep author names, institution names, private paths, API keys, and private datasets out of the remote.
4. To push from the verified bundle, run `python scripts/publish_anonymous_remote.py --remote-url <anonymous-url> --push`; add `--record-url` only if the URL is safe to store in tracked outputs.
5. Re-run `python scripts/check_remote_anonymous_readiness.py` after adding the anonymous remote URL or writing a successful publish report.
6. Re-run `python scripts/make_submission_readiness.py` and `python scripts/make_submission_handoff.py`; update `roadmap/milestones_checklist.md` only after the hosted remote exists.

The current deterministic v0 state is upload-ready locally as both a zip and a git bundle. The hosted remote publication has been verified by commit match in `results/anonymous_remote_publish_v0.json`; record the anonymous URL in the submission system.
