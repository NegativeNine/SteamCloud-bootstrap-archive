# Implementation Guide — SteamCloud

## Delivery order

1. Land schemas and generated bindings without changing live authority.
2. Add a compatibility adapter around the existing implementation.
3. Commit immutable intent before every cross-process or remote effect.
4. Add durable receipts and parity comparison before enabling a canary.
5. Gate canaries by operator configuration and exact subject/account allowlists.
6. Exercise rollback, dependency outage, restart, privacy withdrawal and erasure.
7. Remove duplicate state only after the new authority is qualified.

## Code rules

- Prefer narrow named operations over generic proxy or command endpoints.
- Treat all JSON from another process or repository as untrusted.
- Pin profile, pack, policy, schema and dependency versions in durable state.
- Preserve `UNKNOWN`, `UNSUPPORTED`, `DECLINED`, `RATE_LIMITED`, `PARTIAL`, `ABSENT` and `UNCERTAIN` independently.
- Never retry an ambiguous external mutation without a reconciliation read.
- Keep secrets in edge session memory or a KMS-backed vault lease only.
- Every product response names its source, observation time and evidence state.

## First vertical slice

Run four mock-backed packs end-to-end on a qualified Campfire service, then add a public profile collection canary.

## Deployment rule

A merged scaffold is not a cutover. A cutover requires a signed evidence record containing the exact commit, dependency pins, environment, commands, raw outputs, reviewers, rollback target and observed authority state.
