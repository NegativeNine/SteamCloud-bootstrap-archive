# Review Findings — SteamCloud

## STEAMCLOUD.BLOCKER-001 — SteamCloud cannot be production authority until Campfire and Ember qualify

- Severity: **P0**
- Confidence: `INFERRED`
- Category: `production-dependency`
- Sources: `docs/CURRENT_STATE.md`, `docs/DEPENDENCIES.md`
- Claim: SteamCloud is a new Campfire profile and therefore inherits Campfire C1-C5 and Ember trust/durability blockers.
- Scenario: The new domain is deployed with real Steam credentials or persistent sessions against reference orchestration.
- Impact: Lost, duplicated or cross-account operations.
- Remediation: Develop against mock agents, but gate real account authority on signed Campfire/Ember qualification evidence.
- Runtime verification required: `true`

## STEAMCLOUD.SECRET-002 — Credential vault and opaque secret lease path are not implemented

- Severity: **P1**
- Confidence: `INFERRED`
- Category: `credential-custody`
- Sources: `docs/SECURITY.md`
- Claim: The proposed architecture requires Campfire/Ember to hold only references and generations; no production vault integration exists.
- Scenario: A shortcut stores refresh tokens, passwords, cookies or authenticator secrets in a run, queue or database projection.
- Impact: Fleet-wide credential compromise.
- Remediation: Implement KMS-backed envelope encryption and one-runtime short-lived secret leases with audit and revocation.
- Runtime verification required: `true`

## STEAMCLOUD.AGENT-003 — External account/scraper agents and resource fencing are not implemented

- Severity: **P1**
- Confidence: `INFERRED`
- Category: `agent-runtime`
- Sources: `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`
- Claim: The package contains contracts and samples only; no deployed regional agent gateway, scheduler or egress controller exists.
- Scenario: Two agents own one account or stale action grants execute after reassignment.
- Impact: Duplicate and cross-account Steam effects.
- Remediation: Implement authenticated agent registration, account/credential/egress resource leases and generation-fenced action settlement.
- Runtime verification required: `true`
