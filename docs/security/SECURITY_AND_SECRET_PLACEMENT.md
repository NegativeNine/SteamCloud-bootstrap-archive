# Security and Secret Placement

**Document status:** Current public-placeholder rules plus target boundaries.

## Status

| Status | Rule |
|---|---|
| `CURRENT LIVE` | This public repository stores no operational secret or production credential. |
| `IMPLEMENTED BUT NOT LIVE` | None in the current tree. |
| `SHADOW/CANARY` | None observed. |
| `REFERENCE/PROTOTYPE` | Historical samples remain non-authoritative in Git history. |
| `BLOCKED/NOT QUALIFIED` | Any credential custody, agent trust, or runtime security claim. |
| `TARGET` | Vault/edge/runtime-only placement described below. |

## Public repository boundary

Do not commit or paste secret values, secret-looking fixtures, production data,
private repository history, internal deployment topology, or non-public
operational detail. A public-content review is mandatory before the
administrator rename sequence.

This repository must not contain application code, operational workflows,
deployment configuration, production schemas, service credentials, or a
generic Steam request/command proxy. The repository-local archive validator and
its CI workflow are the only executable exceptions and have no production
identity or secret access.

## Target placement

- Persistent operational secrets belong only in an approved KMS/Vault system
  and are leased just in time to a fenced runtime.
- Owner browser tokens remain edge-only and ephemeral.
- Active clients, sockets, browser processes, and provider request handles
  remain runtime-only.
- No durable store—including SteamCloud, Campfire, Ember, or SteamGraph—and no
  queue, log, artifact, example, or product store receives a plaintext Steam
  credential.
- Large approved source bytes belong in object storage by digest, subject to
  retention, privacy, and erasure policy.
- Services receive workload identities and closed, audience-bound
  capabilities; customer credentials are never agent capabilities.

## Effect safety target

Every external effect requires durable intent, an exact request digest,
generation fences, a bounded action kind, a local execution journal, and typed
settlement. An ambiguous effect becomes `UNCERTAIN` and is reconciled rather
than blindly repeated. No timer, scheduler, authority lease, or cohort is armed
by this bootstrap.
