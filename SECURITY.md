# Security Architecture — SteamCloud

## Trust model

Trust is explicit, external and versioned. A repository cannot manufacture its own production authority merely because it can compile or sign a fixture. Production verification binds algorithm, key ID, issuer/audience where applicable, schema/profile version, generation, digest, expiry and purge watermark.

## Highest-priority findings

| Finding | Severity | Summary |
|---|---|---|
| `STEAMCLOUD.BLOCKER-001` | P0 | SteamCloud cannot be production authority until Campfire and Ember qualify |
| `STEAMCLOUD.SECRET-002` | P1 | Credential vault and opaque secret lease path are not implemented |
| `STEAMCLOUD.AGENT-003` | P1 | External account/scraper agents and resource fencing are not implemented |

## Required controls

- Least-privilege service identities and per-tenant authorization context.
- No secrets in logs, queues, manifests, product DTOs, Campfire atoms or Hypergraph facts.
- Bounded request/response bodies and untrusted allocation counts.
- Short-lived one-action capabilities with replay protection.
- Durable idempotency and monotonic resource fencing before external effects.
- Stable egress accounting; a throttle stays with the egress that earned it.
- Separate test, preview and production trust roots.
- Signed release manifest, SBOM and dependency capability pins.
- Immediate logical suppression plus verified physical erasure for every live copy.

## Prohibited production functionality

AutoSteamFarm/SteamCloud public production excludes automated account creation, fake gameplay/playtime, reward or card farming, automated trade/market mutation, CAPTCHA solving, stealth/fingerprint evasion and rate-limit or ban circumvention.
