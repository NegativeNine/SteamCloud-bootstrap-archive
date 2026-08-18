# Contracts — SteamCloud

## Shared envelopes

The repository consumes or produces only versioned contracts. Shared examples are included under `schemas/`.

| Contract | Purpose | Authority |
|---|---|---|
| `command-capability/v1` | Admit one product request | Product identity/SteamCloud |
| `campfire-action-grant/v1` | Execute one immutable ActionIntent | Campfire |
| `resource-lease/v1` | Fence account, credential, egress or artifact resource | Campfire/SteamCloud |
| `collection-permit/v1` | Authorize source/scope/class before collection | Steam Hypergraph |
| `source-artifact/v1` | Content-addressed source evidence without secrets | SteamCloud/R2 |
| `observation-publication/v1` | Publish admitted evidence | Steam Hypergraph |
| `world-view/v1` | Project current operational state | SteamCloud projector |
| `dependency-status/v1` | Pin sibling capability evidence | Releasing repository |
| `forbidden-fields/v1` | Names that must never appear on grants, arguments or domain JSON | SteamCloud |

## Repository-specific contract rule

Provide the operational Steam domain on Campfire, analogous to Steam Hypergraph on Ember.

- Inputs use exact schemas and reject unknown high-risk fields.
- A route cannot select an arbitrary adapter, URL, HTTP method, credential, trust root or storage authority.
- An effect result is `COMPLETED`, `FAILED`, `RETRYABLE`, `WAITING`, `DECLINED`, `UNSUPPORTED` or `UNCERTAIN`; a bare success boolean is insufficient.
- Every release pins the exact dependency SHA and required capability status.
