# Placeholder v1 Sample Provenance

**Artifact status:** `REFERENCE/PROTOTYPE`, superseded and non-authoritative.
It was never observed as `CURRENT LIVE`, `IMPLEMENTED BUT NOT LIVE`, or
`SHADOW/CANARY`. Any production use remains `BLOCKED/NOT QUALIFIED`.

## Why this record exists

The refined v2.0 architecture expected this public repository to be empty.
Discovery found a small generated v1 sample with meaningful public history.
The sample is removed from the current branch tip so it cannot be confused with
the history-bearing SteamCloud implementation, while its exact content and
knowledge remain recoverable from Git.

No private `steam-platform` history is present or imported.

## Provenance

| Item | Identity |
|---|---|
| Initial v1 sample commit | `f18a068adad4ccc987dbbfcc2debacdb78b4bbdc` |
| Reviewed sample tip / merged PR #1 | `069c2448ee3c5e7c352d096494d15e8f120cf433` |
| Reviewed tree | `dcc70bd212ff8d1499aa5f2141a429629bf066a5` |
| PR #1 head | `0b8550eb80995082714773a4390bc8165da26234` |
| Original manifest SHA-256 | `5aed9828ef4b8069eea0eb53ccf04a58373208ad66fd8d0d191f3e6aedc3e2b4` |
| Original tracked tree | 83 files, 110,805 bytes, approximately 3,530 lines |

The complete original content digest inventory is
[V1_SAMPLE_MANIFEST.sha256](V1_SAMPLE_MANIFEST.sha256). It covers all original
tracked subjects except the manifest itself, whose digest is recorded above.

## Preserved knowledge

The history retains:

- operation admission and explicit policy status;
- forbidden-field rejection and closed action intent;
- account, credential, runtime, and egress generation fencing;
- in-memory lease and duplicate-settlement semantics;
- WorldView projection examples;
- sample schemas, fixtures, operation definitions, and Campfire packs;
- Node tests, one Rust reference crate/test, validation logic, and CI history;
- adversarial review evidence and the correction merged through PR #1.

These are sample/reference artifacts, not proof of deployed services, durable
storage, current contracts, or runtime qualification.

## Original tree categories

- Root architecture and review documents.
- `.github/workflows/ci.yml` sample CI.
- `src/` and `test/` JavaScript sample/runtime tests.
- `crates/steamcloud-agent/` Rust reference code.
- `schemas/`, `operations/`, `packs/`, and `profile/` generated samples.
- `review/` reports and schemas.
- `scripts/validate_repository.py` and integrity metadata.

Every original path is named in the archived manifest or is the original
`MANIFEST.sha256` itself.

## Recovery and verification

Recover the exact reviewed sample without changing the current checkout:

```bash
git archive --format=tar \
  --output=/tmp/steamcloud-placeholder-v1.tar \
  069c2448ee3c5e7c352d096494d15e8f120cf433
```

Verify it using the commands in
[Acceptance and validation gates](../../migration/ACCEPTANCE.md). Do not deploy,
publish, or promote the recovered sample based on those checks.

## Reconciliation with refined v2.0

The v1 sample described a greenfield SteamCloud and used `Steam Hypergraph`,
`steam.*`, `asf-*`, and an unversioned `steamcloud` profile. Refined v2.0 instead
requires a history-preserving rename of private `steam-platform`, the canonical
SteamGraph name, versioned `steamcloud.*` operations, durable aliases, and a
capability-by-capability authority migration. The sample schemas are not copied
forward as target contract authorities.
