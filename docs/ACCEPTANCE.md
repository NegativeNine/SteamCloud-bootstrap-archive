# Acceptance Gates — SteamCloud

## Static gates

- JSON schemas parse and validate positive/negative fixtures.
- Sample source has no forbidden secret fields or generic proxy command.
- Dependency and authority documents agree with `REPO-METADATA.json`.
- Every finding has owner, impact, remediation and runtime-verification flag.
- SHA-256 manifest matches every packaged file.

## Runtime gates

- Duplicate delivery creates one logical effect.
- Stale account, credential, runtime or egress generation is rejected before effect.
- An ambiguous effect becomes `UNCERTAIN` and is reconciled; it is not blindly replayed.
- Cross-tenant reads, signals, cancels, artifacts and credentials are refused.
- Restart and dependency outage preserve the documented authority and rollback path.
- Privacy withdrawal and erasure reach database, object storage, projections and CDN.

## Repository-specific next gate

Run four mock-backed packs end-to-end on a qualified Campfire service, then add a public profile collection canary.
