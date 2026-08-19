# SteamCloud naming placeholder

> **CURRENT LIVE:** This public repository is a naming placeholder and owns no
> runtime, data, credential, execution, or semantic authority. It is not the
> production SteamCloud implementation.

The history-bearing implementation remains in the private `steam-platform`
repository until a separately authorized, history-preserving rename. Do not
copy operational code, schemas, credentials, secrets, or private history into
this public repository.

The administrator target for this repository is
`SteamCloud-bootstrap-archive`, or another archive name explicitly approved at
the time of the change. No remote rename, archive operation, visibility change,
or runtime cutover is performed by this bootstrap.

## Status

| Status | This repository |
|---|---|
| `CURRENT LIVE` | Public naming placeholder only; no runtime authority. |
| `IMPLEMENTED BUT NOT LIVE` | Archive documentation and validation only; no runtime implementation. |
| `SHADOW/CANARY` | None observed. |
| `REFERENCE/PROTOTYPE` | The superseded v1 sample remains recoverable in Git history. |
| `BLOCKED/NOT QUALIFIED` | Any use as a SteamCloud service, package, schema authority, or deployment. |
| `TARGET` | Rename this placeholder to an archive name without changing its GitHub Archived setting, then separately rename the private history-bearing repository to `SteamCloud`. |

The deployed state of sibling systems is `UNKNOWN` from this public checkout.
The architecture package is target guidance, not evidence of implementation or
qualification.

## Documentation authority

- [Authority and boundaries](docs/architecture/AUTHORITY_AND_BOUNDARIES.md)
- [Observability and correlation vocabulary](docs/architecture/OBSERVABILITY.md)
- [Placeholder disposition decision](docs/decisions/ADR-002-placeholder-archive-disposition.md)
- [Migration roadmap](docs/roadmap/MIGRATION_ROADMAP.md)
- [Phase ledger](docs/roadmap/PHASE_LEDGER.json)
- [Administrator handoff](docs/migration/ADMINISTRATOR_HANDOFF.md)
- [Canonical and legacy aliases](docs/migration/NAMING_ALIASES.json)
- [Sibling dependency status](docs/migration/SIBLING_DEPENDENCIES.json)
- [Acceptance and validation gates](docs/migration/ACCEPTANCE.md)
- [Security and secret placement](docs/security/SECURITY_AND_SECRET_PLACEMENT.md)
- [Bootstrap report](docs/migration/BOOTSTRAP_REPORT.md)
- [Placeholder history and provenance](docs/archive/placeholder/README.md)

Historical root documents and sample code are non-authoritative. Use the files
linked above for all current decisions.

## Validation

The only executable in this tree is the archive validator and its tests. They
do not deploy, qualify, or operate SteamCloud. Commands are listed in
[Acceptance and validation gates](docs/migration/ACCEPTANCE.md).
