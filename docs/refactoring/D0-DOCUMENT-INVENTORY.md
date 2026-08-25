# D0 documentation inventory — SteamCloud-bootstrap-archive

- **Status:** complete for the pinned `main` baseline
- **Owner:** `agent-portfolio`
- **Documentation profile:** `HISTORICAL_NON_AUTHORITATIVE_ARCHIVE`
- **Work-order disposition:** `KEEP_HISTORICAL_ARCHIVE`
- **Baseline:** `f395c6c922124c716d216d80fee42dba7d3547d2`
- **Repository ID:** `1338764433`
- **Plan archive SHA-256:** `c6ea88a5a4dd53f997ec9425299cab8c70a0347fffb402ba98bfad9ed0612cb5`
- **Last validated:** 2026-08-25 UTC

> This repository is a public historical naming archive. This inventory does not provide SteamCloud runtime, data, credential, execution, semantic, deployment, qualification, architecture, schema, protocol-freeze, or `CurrentAuthority` evidence.

The D0 baseline predates the merged Phase 00/01 records and the D0/D1 index
commits. Its 25-file count and blob identities remain a historical observation;
they are not rewritten to describe the later tree.

## Exact inventory summary

The complete tree contains 25 files and is not truncated:

- 12 prose documents;
- 9 machine-readable evidence or checksum artifacts;
- 1 archive-validation workflow;
- 1 configuration file;
- 1 validator and 1 validator test.

The machine-readable inventory records every path, blob, size, and provisional class.

## Historical archive entrypoint candidates

| Path | Role |
|---|---|
| `README.md` | Public archive entrypoint and no-authority notice |
| `docs/architecture/AUTHORITY_AND_BOUNDARIES.md` | Archive authority and boundary map |
| `docs/migration/CLOSEOUT.md` | Repository-local closeout and external blockers |

All other documents remain operational archive guidance, evidence, historical roadmap material, or machine-readable receipts. None is deleted or rewritten by D0.

## Duplicate and conflict assessment

Archive status and authority are intentionally repeated across README, authority maps, closeout, freeze, and phase-ledger artifacts. The overlap is evidentiary, but it lacks one compact archive index. D1 adds pointers rather than replacing or collapsing those records.

Statements in the historical closeout about there being no non-`main` branch or open PR are baseline observations. They become stale when this documentation branch exists and must not be presented as timeless repository state.

## Architecture and authority disposition

Architecture and schema material is `HISTORICAL_SEED_NON_NORMATIVE`.
`authority_change_permitted` is false and this integration has no
`CurrentAuthority` effect. It does not freeze G1-G5 or consumer schemas,
authorize production dispatch or blue multiwriter activation, prove destructive
erasure, promise protocol 1.0, or authorize product migration without authority
routing.

## Stage decision

D1 may add compact `ARCHIVE-NOTICE`, `SOURCE-MANIFEST`, `PROVENANCE`, and
`STATUS` documents. D2 remains blocked on external backup/settings export,
secret-history review, public-content review, protected-main evidence, and a
final owner-approved retention/settings decision.

## Rollback

Close or revert the documentation branch. Preserve every historical and evidence artifact. The exact rollback identity is `main@f395c6c922124c716d216d80fee42dba7d3547d2`.
