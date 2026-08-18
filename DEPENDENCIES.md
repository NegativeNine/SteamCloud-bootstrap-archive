# Dependency Contract — SteamCloud

| Dependency | Relationship | Release requirement |
|---|---|---|
| `Campfire` | Required | Must be pinned to exact SHA/capability evidence |
| `Steam Hypergraph` | Required | Must be pinned to exact SHA/capability evidence |
| `credential vault` | Required | Must be pinned to exact SHA/capability evidence |
| `regional execution platform` | Required | Must be pinned to exact SHA/capability evidence |

## Rules

- Dependency status is evidence, not prose copied between repositories.
- `UNKNOWN`, stale or unreadable evidence fails closed.
- `IMPLEMENTED` is not `QUALIFIED`; `QUALIFIED` is not `DEPLOYED`; `DEPLOYED` is not `AUTHORITATIVE`.
- Current-head drift does not change this frozen assessment. It opens a revalidation task.

## Next dependency gate

Run four mock-backed packs end-to-end on a qualified Campfire service, then add a public profile collection canary.
