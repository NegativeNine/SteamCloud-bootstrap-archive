# Migration Roadmap

**Document status:** Current dependency- and evidence-driven plan. Dates do not
advance phases; only the stated gates do. Machine-verifiable phase and wave
status lives in [PHASE_LEDGER.json](PHASE_LEDGER.json) (schema v2, completion
contract fields). That ledger is the status authority; this document is the
narrative plan. Ledger statuses include `LIVE`, `RESEARCH_ONLY`, and
`PROHIBITED`; none of those apply to a runtime in this placeholder.

## Status vocabulary

`CURRENT LIVE`, `IMPLEMENTED BUT NOT LIVE`, `SHADOW/CANARY`,
`REFERENCE/PROTOTYPE`, `BLOCKED/NOT QUALIFIED`, and `TARGET` have the meanings
defined in the
[authority map](../architecture/AUTHORITY_AND_BOUNDARIES.md#status-vocabulary).

## Phase 0 — Placeholder bootstrap

**Status:** ledger `COMPLETE` at `5c66871`. Documentation remains
`IMPLEMENTED BUT NOT LIVE` for any runtime claim. The PR #2 archive
handoff (`541ff22`) and the 2026-08-19 ledger refresh are on `origin/main`.
This phase changed no runtime authority.

Work:

- establish one README-led documentation authority;
- preserve the v1 sample through immutable Git history and provenance;
- remove executable sample/application material from the branch tip;
- inventory settings, dependencies, aliases, and administrator gates;
- remove the verified architecture ZIP after integration succeeds.

Exit gate:

- all acceptance checks pass;
- the repository contains only the archival handoff and provenance;
- the v1 tree is reproducible from its recorded commit and digest manifest;
- no remote setting or live authority changed.

Rollback: revert the bootstrap commit. Historical sample commits remain intact
on either path.

## Phase 1 — Administrator export and public-content review

**Status:** `BLOCKED/NOT QUALIFIED`; administrator action required.

Work:

- create a verified mirror backup;
- export repository settings and dependency inventory;
- preserve PR #1, Actions history, and current repository metadata;
- complete a public-content and secret-history review;
- close every `UNKNOWN` item in the administrator checklist or explicitly
  accept it as a blocker.

Exit gate: backup restoration is tested, settings export is reviewable, and no
package, Action, Page, domain, webhook, App, deploy key, or external consumer
would be destroyed by moving the placeholder.

Rollback: no rename is attempted; repeat the export after fixing gaps.

## Phase 2 — Move the public placeholder

**Status:** `TARGET`; separate explicit authorization required.

Work: rename this repository to `SteamCloud-bootstrap-archive` or another
approved archive name. Do not delete it, change visibility, or toggle the
GitHub Archived setting as part of the rename.

Exit gate:

- the archive repository resolves under the approved name;
- settings, refs, PR history, and required integrations survived;
- `NegativeNine/SteamCloud` is verified available for the subsequent rename;
- rollback instructions are still valid.

Rollback: before any private repository rename, rename the archive back to
`SteamCloud` if a dependency or settings loss is detected.

## Phase 3 — Authorize the history-bearing rename

**Status:** `BLOCKED/NOT QUALIFIED`; administrator and security review required.

Work: authorize the private `steam-platform` repository to be renamed to
`SteamCloud` in place. Keep it private. Architecture, history, and secret review
completion does not authorize a visibility change. Do not copy its history
through this public archive.

Exit gate: history, settings, tags, releases, deployment references, packages,
webhooks, Actions, and rollback references are preserved under the canonical
name. Repository naming changes no runtime authority.

Rollback: use the separately approved private-repository rollback plan. Never
recreate the old repository name casually because doing so can invalidate Git
redirects.

## Phase 4 — Architecture migration in the canonical repository

**Status:** `TARGET`; out of scope for this placeholder.

The history-bearing repository performs capability-by-capability migration:
legacy authority, model-only shadow, decision parity, no-effect replay,
allowlisted read-only canary, exercised rollback, and only then an explicit
authority change. Ember and Campfire qualification, SteamGraph semantic
authority, secret placement, and durable aliases are proven there—not inferred
from this archive.

Exit gate: the canonical repository records independent qualification,
capability/cohort authority, parity, canary, and rollback evidence for every
approved slice.

Rollback: the previously named live authority remains authoritative until an
explicit cutover decision; each later cutover retains and exercises its own
legacy rollback target.
