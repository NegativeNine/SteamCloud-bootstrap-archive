# Acceptance and Validation Gates

**Document status:** Current bootstrap gates. Passing them validates only this
archive handoff; it does not qualify or deploy SteamCloud, SteamGraph, Campfire,
or Ember.

## Status coverage

- `CURRENT LIVE`: the repository is a public naming placeholder only.
- `IMPLEMENTED BUT NOT LIVE`: the archival documentation after merge.
- `SHADOW/CANARY`: none observed or enabled.
- `REFERENCE/PROTOTYPE`: the historical v1 sample and verified v2 target package.
- `BLOCKED/NOT QUALIFIED`: all runtime, credential, datastore, scheduler, and
  authority claims.
- `TARGET`: the separately authorized administrator rename sequence.

## Required gates

1. The README links to one coherent documentation authority.
2. All relative Markdown links resolve.
3. All JSON files parse, and status values remain explicit.
4. The v1 sample tree is reconstructable from commit `069c244` and matches its
   archived SHA-256 manifest.
5. No application scaffold, operational workflow, schema authority, package,
   deployment unit, or architecture ZIP remains in the current tree. The
   archive validator and its CI workflow are the only executable exceptions.
6. No high-confidence secret pattern appears in changed or tracked files.
7. No page claims this repository is the production SteamCloud implementation.
8. Alias, dependency, security, observability, rollback, and administrator
   gates are present.
9. `git diff --check` and repository integrity checks pass.

## Local validation commands

Run from the repository root. The validator checks the exact file allowlist,
JSON syntax and semantics, YAML triggers/permissions, Markdown paths and
anchors, status vocabulary, v1 ancestry/content parity, absence of the ZIP and
sample scaffold, and high-confidence secret patterns across every allowed
file.

```bash
set -euo pipefail
python3 -c 'import yaml; assert yaml.__version__ == "6.0.3"'
python3 scripts/validate_placeholder.py
git diff --check
git diff --cached --check
git fsck --full
```

Install the pinned validation-only prerequisite with
`python3 -m pip install PyYAML==6.0.3` if it is unavailable. CI installs that
exact version, runs the validator, checks the committed diff, and runs Git
integrity validation with a full-history checkout.

The final tree contains no application source package, generated contract, or
schema, so application lint, type-check, schema parity, and runtime tests are
not applicable after archival. The original sample commands and their observed
outcomes are retained in the
[bootstrap report](BOOTSTRAP_REPORT.md#validation-evidence).
