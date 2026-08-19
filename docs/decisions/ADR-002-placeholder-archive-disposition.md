# ADR-002: Preserve the Populated Placeholder as Archive History

**Decision status:** Accepted for this bootstrap on 2026-08-18; still accepted
after the 2026-08-19 discovery refresh on merged PR #2.

**Runtime status:** `CURRENT LIVE` naming placeholder;
`REFERENCE/PROTOTYPE` historical sample; `TARGET` administrator rename.

The current documentation and validator are `IMPLEMENTED BUT NOT LIVE`; no
`SHADOW/CANARY` exists, and all runtime use remains
`BLOCKED/NOT QUALIFIED`.

## Context

The refined architecture expected an empty public `SteamCloud` placeholder.
Discovery found two public commits instead: a generated v1 architecture sample
and a follow-up change merged through PR #1. The tree included sample Node and
Rust code, schemas, operation definitions, packs, fixtures, tests, review
artifacts, and CI. Its own metadata stated that it was not implemented,
qualified, deployed, canary, or authoritative.

## Decision

The current branch tip becomes a minimal, documentation-only archive handoff.
The v1 sample is preserved by:

1. retaining the complete Git history in this repository;
2. recording both commits, PR provenance, tree identity, content inventory, and
   recovery commands under `docs/archive/placeholder/`;
3. retaining the original SHA-256 content manifest there;
4. prohibiting any import of private `steam-platform` history.

The sample application, schemas, packs, workflow commands, and duplicate
governing documents are removed from the current branch tip so they cannot be
mistaken for the canonical implementation or a live contract authority. The
workflow path is retained with archive-only validation.

## Consequences

- No historical commit or unique sample knowledge is discarded.
- The archive repository remains intentionally minimal and safe to keep public.
- No repository-controlled production runtime was identified. External
  consumers remain `UNKNOWN`; replacing sample CI and branch-tip material does
  not change a proven live authority.
- The administrator must still back up and rename the repository; this decision
  does not execute or authorize a remote rename, visibility change, or private
  repository publication.
