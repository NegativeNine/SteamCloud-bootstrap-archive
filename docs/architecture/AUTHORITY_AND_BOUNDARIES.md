# Authority and Boundaries

**Document status:** Current governing architecture for this placeholder.

## Status vocabulary

| Status | Meaning here |
|---|---|
| `CURRENT LIVE` | Directly observed current state; for runtime concerns, deployed authority. |
| `IMPLEMENTED BUT NOT LIVE` | Implemented and evidenced, but not authoritative. |
| `SHADOW/CANARY` | Explicitly bounded non-authoritative or allowlisted operation. |
| `REFERENCE/PROTOTYPE` | Design or sample material only. |
| `BLOCKED/NOT QUALIFIED` | Must not be promoted without named evidence and approval. |
| `TARGET` | Intended architecture; not proof of current state. |
| `UNKNOWN` | Not evidenced from this checkout; never infer `NONE`, live, safe, or qualified. |

These labels are not interchangeable. In particular, passing a sample test
does not establish deployment, qualification, canary status, or authority.

## Current authority

| Concern | Status | Authority evidenced by this checkout |
|---|---|---|
| This public repository | `CURRENT LIVE` | Naming placeholder only. |
| Steam operational execution | `UNKNOWN` | No authority evidence is present here; external/deployed state remains `UNKNOWN`. |
| Steam semantic/evidence state | `UNKNOWN` | No authority evidence is present here; external/deployed state remains `UNKNOWN`. |
| Generic durable execution | `UNKNOWN` | No Campfire qualification evidence is present here. |
| Generic durable data | `UNKNOWN` | No Ember qualification evidence is present here. |
| v1 sample at `069c244` | `REFERENCE/PROTOTYPE` | Historical in-process sample; never observed live. |
| Refined architecture v2.0 | `REFERENCE/PROTOTYPE` | Verified draft target package; not copied into this tree. |

The migration premise identifies private `steam-platform` as the
history-bearing operational implementation and the current semantic system as
the predecessor to SteamGraph. Their deployed state is not independently
visible from this repository and therefore remains `UNKNOWN` here.

## Target authority

```text
Ember      = generic durable data substrate
Campfire   = generic durable execution system built on Ember
SteamCloud = Steam operational/execution domain built on Campfire
SteamGraph = Steam semantic/evidence domain built on a separate Ember authority
```

Campfire and SteamGraph must use independently recoverable Ember services or
databases. They coordinate through closed, idempotent commands and durable
receipts, not a shared writable namespace or cross-database transaction.

## Bounded planes

- Product and evidence repositories retain their user journeys and evidence
  production.
- Products invoke SteamCloud only through named, versioned Steam actions.
- Products use SteamGraph only through closed semantic contracts, APIs, and
  projections.
- No product, agent, collector, or adapter writes Ember storage directly.
- Collection success is not semantic publication; only SteamGraph decides what
  becomes canonical Steam meaning.
- No user input may select arbitrary URLs, hosts, methods, headers, credentials,
  commands, scripts, protocol messages, or authority paths.

## Rename is not cutover

The target repository names do not change runtime authority. Moving this
placeholder, renaming the private history-bearing repository, or renaming the
semantic repository is vocabulary and history work only. Any live read, write,
scheduler, cohort, credential, or datastore change requires its own
evidence-backed decision, rollback target, and administrator approval.
