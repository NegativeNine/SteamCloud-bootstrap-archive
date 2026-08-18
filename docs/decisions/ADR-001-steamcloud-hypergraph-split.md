# ADR-001 — Adopt the SteamCloud / Hypergraph split

**Status:** Proposed  
**Date:** 2026-08-18

## Decision

`steamcloud` adopts the platform hierarchy in `TARGET_ARCHITECTURE.md`.

- Steam Hypergraph owns admitted Steam semantic truth on Ember.
- SteamCloud owns Steam operational execution as a Campfire profile.
- AutoSteamFarm.com and the other `.com` repositories remain product planes.
- Campfire owns generic durable work semantics.
- Product and agent code never writes Ember internals.

## Consequences

Existing local schedulers, credentials, collectors or fact copies may remain temporarily as rollback authorities, but each receives a named extraction/cutover phase. New work is added only behind versioned contracts and named operations.
