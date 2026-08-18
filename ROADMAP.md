# Production Roadmap — SteamCloud

## S0 — Repository and profile foundation

    **Work**

    - Operation catalog
- Schemas
- Data-only packs
- Generated SDK contracts
- Policy statuses

    **Exit gate:** All contracts validate and no secret field exists in grants.

## S1 — Mock agent vertical

    **Work**

    - Campfire agent gateway
- Mock account/scraper agents
- Action grant and settlement
- WorldView projector

    **Exit gate:** Duplicate delivery produces one logical effect.

## S2 — Credential and resource plane

    **Work**

    - KMS-backed vault
- Opaque references
- Account/credential/egress leases
- Generation fencing

    **Exit gate:** Revocation and stale-generation tests pass.

## S3 — Hypergraph publication

    **Work**

    - Collection permit adapter
- Artifact storage
- Observation publication
- Receipt wait

    **Exit gate:** Public fixture collection seals through Hypergraph.

## S4 — SCDB owner edge path

    **Work**

    - Edge-only delegated token action
- No token persistence
- Companion signal/wait
- Publication receipt

    **Exit gate:** Owner token never enters Campfire, Ember, queue or vault.

## S5 — Public and market collectors

    **Work**

    - Web API
- Community XML
- market surface roles and pacers
- Catalog/PICS

    **Exit gate:** Egress and source-class accounting is complete.

## S6 — Legacy runtime adapters

    **Work**

    - Node WorkerHost bridge
- Optional isolated ASF bridge
- Canary and rollback

    **Exit gate:** External implementation is hidden behind typed actions.

## S7 — Native Rust agents

    **Work**

    - Session coordinator
- Challenge broker
- Web session
- Approved GC subset

    **Exit gate:** Per-operation parity and recovery gates pass.

## S8 — Production qualification

    **Work**

    - Multi-region failover
- Security review
- Privacy/erasure drills
- Cost and SLO evidence

    **Exit gate:** SteamCloud is declared production authority for operations only.

## Production declaration

Production status changes only through a reviewed evidence record that names the exact commit, environment, commands, outputs, approvers and rollback target.
