# Migration from the Old Shape — SteamCloud

## Old shape

Operational collection, product orchestration, source truth and presentation were sometimes colocated or connected by repository-local queues and mutable status files. The earlier AutoSteamFarm design also combined the SaaS product with the Steam account execution domain.

## New shape

- `steamcloud` is the Steam operational domain built on Campfire.
- `autosteamfarm.com` is only the SaaS product plane over SteamCloud.
- `steam-hypergraph` is the Steam semantic domain built on Ember.
- `steamcloud` retains the target role: **Steam operational and automation domain platform on Campfire**.

## Migration strategy

1. Freeze the current authority and contract version.
2. Add typed adapters and shadow publication without changing live reads.
3. Introduce a durable outbox/receipt where work currently spans authorities.
4. Run parity and privacy/erasure drills on an explicit canary allowlist.
5. Cut over one operation or projection at a time with a documented rollback.
6. Remove duplicate execution or semantic state only after the new authority is qualified.

## Rollback

The old live authority remains available until an explicit gate says otherwise. A feature flag may select a canary only from operator configuration; request parameters, cookies and customer input cannot select authority.
