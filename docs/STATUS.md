# Status

- **Repository:** `NegativeNine/SteamCloud-bootstrap-archive`
- **Pinned D0 baseline:** `main@f395c6c922124c716d216d80fee42dba7d3547d2`
- **Documentation stage:** D0 complete; D1 archive index in review
- **Disposition:** `KEEP_HISTORICAL_ARCHIVE`
- **Archive classification:** `HISTORICAL_NON_AUTHORITATIVE`
- **Architecture/schema classification:** `HISTORICAL_SEED_NON_NORMATIVE`
- **Authority change permitted:** false
- **Runtime/data/credential/execution/semantic authority:** none
- **Deployment or package:** none
- **Qualification or observed-live claim:** none

## Repository-local state

| Area | State |
|---|---|
| Public archive entrypoint | Present |
| Authority/no-runtime map | Present |
| Freeze, closeout, phase ledger, and validation evidence | Present |
| Compact archive notice, source manifest, and provenance index | D1 candidate |
| Restorable mirror and settings export | `BLOCKED_EXTERNAL` |
| Secret-history and public-content review | `BLOCKED_EXTERNAL` |
| Independently verified branch protection or approved equivalent | Not evidenced here |
| Final retention/settings owner closeout receipt | Not accepted |

## Reading path

1. [Archive notice](ARCHIVE-NOTICE.md)
2. [Source manifest](SOURCE-MANIFEST.md)
3. [Provenance](PROVENANCE.md)
4. [D0 inventory](refactoring/D0-DOCUMENT-INVENTORY.md)
5. Existing [authority map](architecture/AUTHORITY_AND_BOUNDARIES.md)
6. Existing [closeout](migration/CLOSEOUT.md)

Historical and machine evidence remains in place. The new index does not supersede those artifacts unless a later reviewed receipt explicitly says so.

The sealed Phase 00/01 artifacts preserve historical observations and schemas;
they are not current normative architecture. Nothing in this index freezes
G1-G5 or a consumer schema, enables production effect dispatch or blue
multiwriter operation, moves `CurrentAuthority`, proves destructive erasure,
promises protocol 1.0, or authorizes a product migration without authority
routing.

No runtime, provider, secret, deployment, repository setting, or authority was changed by this documentation branch.
