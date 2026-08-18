# SteamCloud Adversarial Review

## Snapshot

- Repository: `NegativeNine/steamcloud`
- Frozen SHA: `0000000000000000000000000000000000000000`
- Acquisition: GitHub connector static review
- Review date: `2026-08-18`

## Role and authority

- Role: Steam operational and automation domain platform on Campfire
- Authority: Steam accounts, credential references/generations, sessions, runtime placement, egress, bot affinity, collection policies, Steam-specific operation catalog and effect adapters
- Maturity: NEW PROPOSAL / NOT IMPLEMENTED / NOT DEPLOYED

## Strengths

- Clear architectural role derived from existing operational code in Hypergraph, SCDB and steam-platform patterns

## Findings

- **STEAMCLOUD.BLOCKER-001 (P0)** — SteamCloud cannot be production authority until Campfire and Ember qualify: SteamCloud is a new Campfire profile and therefore inherits Campfire C1-C5 and Ember trust/durability blockers.
- **STEAMCLOUD.SECRET-002 (P1)** — Credential vault and opaque secret lease path are not implemented: The proposed architecture requires Campfire/Ember to hold only references and generations; no production vault integration exists.
- **STEAMCLOUD.AGENT-003 (P1)** — External account/scraper agents and resource fencing are not implemented: The package contains contracts and samples only; no deployed regional agent gateway, scheduler or egress controller exists.

## Cross-repository blockers

- Campfire
- Steam Hypergraph
- credential vault
- regional execution platform

## Roadmap correction

Run four mock-backed packs end-to-end on a qualified Campfire service, then add a public profile collection canary.

## Limitations

- Static review only for the frozen original repository.
- No original runtime, production database, secrets, deployment, browser or network evidence was available.
- Post-snapshot changes are listed separately and were not mixed into findings.
- Generated sample tests validate this archive only.
