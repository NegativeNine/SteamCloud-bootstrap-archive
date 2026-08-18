# Target Architecture — SteamCloud

## Target role

**Steam operational and automation domain platform on Campfire.** A Campfire domain profile with data-only packs, typed action kinds, account/credential/egress resource leases, Rust agents and adapters. It publishes immutable source artifacts to Steam Hypergraph and never becomes a second Steam fact store.

## Governing platform hierarchy

```text
Ember
├── Steam Hypergraph — Steam semantic truth
└── Campfire
    └── SteamCloud — Steam operational execution

Product planes
├── Steam Powered Database
├── Steam Market Database
├── Steam Community Database
├── CS2ED
├── Subticked
├── AutoTurret
└── AutoSteamFarm.com

Libraries / producers
├── DB Jump
└── CS2 Demo Parser
```

## This repository owns

- Steam operational accounts and classes
- Credential references and generations
- Runtime/session/egress WorldViews
- Steam-specific Campfire profile and packs
- Effect adapters and agents
- Collection attempt provenance

## This repository does not own

- Canonical Steam facts
- Steam privacy semantics
- Product HTML
- Plaintext secrets in Campfire/Ember
- Generic workflow semantics

## Primary request/data flow

```text
product/user intent
  → product BFF and named capability
  → SteamCloud domain API
  → Campfire Run / WorkItem / ActionIntent
  → typed SteamCloud agent or adapter
  → immutable artifact or typed outcome
  → Steam Hypergraph prepared publication command
  → product projection
```

Components that are not on a given flow remain optional. Product pages read semantic truth from Hypergraph-derived projections. They do not infer success from HTTP liveness, and they do not accept arbitrary upstream URLs, credentials, protocol messages or bot commands.

## Old-to-new shape

The old shape allowed operational account, collection or scheduling concerns to accumulate in product and semantic repositories. The new shape separates them:

- Campfire owns generic work semantics.
- SteamCloud owns Steam-specific operational semantics and adapters.
- Steam Hypergraph owns admitted Steam facts, source classes, privacy and erasure.
- `SteamCloud` retains only the role listed above.
