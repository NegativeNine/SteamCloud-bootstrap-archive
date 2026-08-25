# Source manifest

- **Repository ID:** `1338764433`
- **Repository:** `NegativeNine/SteamCloud-bootstrap-archive`
- **Default branch:** `main`
- **Pinned source commit:** `f395c6c922124c716d216d80fee42dba7d3547d2`
- **Complete D0 inventory:** [refactoring/D0-DOCUMENT-INVENTORY.json](refactoring/D0-DOCUMENT-INVENTORY.json)
- **Tree completeness:** complete; `truncated=false`

## Archive contents at the pinned baseline

| Class | Count | Primary locations |
|---|---:|---|
| Prose documents | 12 | root README/CONTRIBUTING and `docs/` |
| Machine evidence and checksums | 9 | `docs/archive`, `docs/migration`, `docs/roadmap` |
| Archive validation workflow | 1 | `.github/workflows/ci.yml` |
| Validator and tests | 2 | `scripts/` |
| Other configuration | 1 | `.gitignore` |

Every document and machine artifact is bound to its Git blob and size in the D0 JSON. That inventory is the source map for documentation refactoring; it does not replace the original files.

The counts and blobs above describe only the pinned D0 baseline. Phase 00,
Phase 01, and the D0/D1 index commits now present are post-baseline additions and
are deliberately excluded from those historical counts. The sealed phase
artifacts are retained without byte rewriting.

## Historical source references

The repository records a historical sample recoverable from earlier Git history and names commit `069c244` as a recovery point. That reference remains historical provenance, not an instruction to restore an active application on the archive branch.

Architecture and schema material reachable from the baseline or the historical
sample is `HISTORICAL_SEED_NON_NORMATIVE`. It is not a current architecture
contract, protocol freeze, consumer-schema freeze, migration authority, or
`CurrentAuthority` evidence source.

## Exclusions

This manifest does not include private SteamCloud implementation history, operational credentials, live provider configuration, sibling deployments, external GitHub settings, secrets, packages, Projects, forks, or provider state. Those are not inferred from the public Git tree.
