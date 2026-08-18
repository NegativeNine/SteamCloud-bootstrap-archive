# Bootstrap Report

**Report date:** 2026-08-18

**Repository:** `NegativeNine/SteamCloud` public placeholder

**Bootstrap base:** `069c2448ee3c5e7c352d096494d15e8f120cf433`

**Package:** `SteamCloud-SteamGraph-Refined-Architecture-v2.0`, version
`2.0.0-draft`

## Outcome

The checkout was not empty: it contained two commits of generated v1
architecture/sample material and merged PR #1. That was classified as a
source/history collision, not a production-runtime collision. After explicit
operator direction to resolve it, the sample was preserved in immutable Git
history plus a complete provenance/digest inventory, and the current tree was
prepared as a minimal public archive handoff.

No private history was imported. No live authority, datastore, scheduler,
cohort, credential, deployment, repository name, visibility, Pages setting,
package-registry publication/setting, webhook, or production secret was
changed. Publication changes Git branch and archive-validation workflow content
only, as explicitly requested; external workflow consumers remain `UNKNOWN`.

## Package verification

| Check | Result |
|---|---|
| Required outer SHA-256 | `b3103485838efa9bc1e129a6ea24a0ea362ba704fc365fd783b82b3c5c41a1a9` — PASS |
| Extraction | `unzip -q` to a temporary directory — PASS |
| Package `MANIFEST.sha256` | Every listed artifact — PASS |
| `python3 validate.py` | `validation passed` — PASS |

The package was read in the prescribed order, including SteamCloud-relevant
ADRs, manifests, contracts, examples, reference adapters, and diagrams. It was
treated as draft target architecture, never as proof of current
implementation, deployment, or qualification. The package content was not
copied into the repository.

## Repository discovery

### Local checkout before editing

| Field | Evidence |
|---|---|
| Root | `/home/scdb/SteamCloud` |
| Branch | `main` |
| HEAD | `069c2448ee3c5e7c352d096494d15e8f120cf433` |
| Remote | `origin https://github.com/NegativeNine/SteamCloud` |
| Relevant tags | None |
| Status | Clean tracked tree; pre-existing untracked architecture ZIP only |
| Commit count | 2 |
| Tracked content | 83 files, 110,805 bytes, approximately 3,530 lines |

The untracked ZIP was operator-provided task input. It was not staged or
overwritten, was ignored by the new `.gitignore` during integration, and was
removed only after its digest, manifest, and validator passed.

### Visible GitHub inventory

Read-only inventory at `2026-08-18T22:38:13Z` established:

- public repository ID `1338764433`, created `2026-08-18T19:21:58Z`;
- default and only branch `main`; no tags, releases, or issues;
- merged PR #1, head `0b8550e`, merge commit `069c244`;
- one active `architecture-sample-ci` workflow and four historical runs
  (three success, one initial failure);
- no Actions artifacts/caches, repository Actions secrets/variables,
  environments, deployments, repository webhooks, deploy keys, or Pages site;
- no issue, discussion, release, PR comment, PR review, or PR review comment;
- wiki and Projects features enabled, but no wiki content observed and
  repository-linked Projects v2 state `UNKNOWN` because the inventory
  credential lacked `read:project`;
- no branch protection or rulesets;
- public user package count zero, while private/internal package state is
  `UNKNOWN` because the inventory credential lacked `read:packages`;
- GitHub App subscriptions, webhooks beyond the repository-hooks API, external
  DNS, hosted Action consumers, and other external integration state remain
  `UNKNOWN`.

See [REPOSITORY_INVENTORY.json](REPOSITORY_INVENTORY.json) for the structured
snapshot. Every item must be rechecked at administrator-action time.

### Original document authority map

The old README directed readers to `CURRENT_STATE.md`,
`TARGET_ARCHITECTURE.md`, `AUTHORITY_AND_BOUNDARIES.md`, `ROADMAP.md`, and
`review/report.json`. Those files described a generated greenfield v1 sample
and conflicted with refined v2.0. The current README now points to one coherent
authority under `docs/architecture`, `docs/roadmap`, `docs/migration`, and
`docs/security`. Historical documents remain available at the recorded commit
but are explicitly non-authoritative.

### Original build, test, lint, and format commands

| Command | Source |
|---|---|
| `npm run check` | JavaScript syntax plus `scripts/validate_repository.py` |
| `npm test` | Node built-in test runner |
| `cargo fmt --all -- --check` | Sample Rust formatting |
| `cargo clippy --workspace --all-targets -- -D warnings` | Sample Rust lint |
| `cargo test --workspace` | Sample Rust tests |

The final archive tree has no application package or operational workflow. A
repository-local archive validator and CI workflow replace the sample
application commands; this is intentional and does not assert runtime
qualification.

## Current implementation and operational inventory

The reviewed tree contained seven JavaScript sample modules, three Node test
files, one Rust reference crate, ten JSON schemas plus fixtures, nine operation
definitions, six `asf-*` packs, one sample profile, a Python validator, generated
review reports, and sample CI.

The exact package inventory was:

- private npm `steamcloud-architecture-sample@0.1.0`;
- Rust reference crate `steamcloud-agent@0.1.0` via workspace version;
- generated package metadata `steamcloud@0.1.0-architecture`.

No tracked dependency lockfile or publishing configuration existed.

It contained no actual Steam client, network adapter, vault, database client,
database migration, queue client, server/CLI entry point, Docker/Compose file,
Kubernetes/Helm resource, Terraform, systemd unit, release artifact, production
configuration, operator runbook, deployment record, or canary evidence.
Runtime state and settlement behavior in the sample used in-memory objects.

The sample secret boundary was documentation and forbidden-key rejection; it
had no credential custody or vault path. `DEPENDENCIES.json` held one old
Campfire reference and all-zero/`UNKNOWN` placeholders for other dependencies.
No sibling runtime was proven from this checkout.

Files with generated/historical or configuration-like significance were the
package/source snapshots, review corpus, integrity manifest, schemas, fixtures,
operation policy JSON, profile/packs, tests, and CI. They were preserved through
the exact commit, tree identity, original manifest, and PR record before leaving
the current branch tip. No deployed or operator-owned data asset was found.

## Package conflicts reconciled

1. V1 modeled a greenfield SteamCloud; v2 requires private `steam-platform` to
   become SteamCloud through a history-preserving rename.
2. V1 used “Steam Hypergraph”; v2 establishes the canonical SteamGraph name.
3. V1 operation/profile names (`steam.*`, `asf-*`, `steamcloud`) differ from v2
   canonical versioned names; directional aliases are now recorded.
4. V1 ActionGrant and related schemas are incompatible with v2 drafts and are
   not promoted as current contract authorities.
5. V1 marked synthetic gameplay `REMOVED`; v2 retains the knowledge as
   `research_only`. Its code/tests remain recoverable in history, not registered
   in a live profile.
6. V1 sample operations used `ENABLED` and `PRIVATE_CANARY` labels despite no
   deployment evidence. The current authority map prevents those labels from
   being read as live state.
7. The package snapshot assumed `commit: null` for this repository; the actual
   two-commit history and PR are preserved rather than overwritten.

## Current and target authority

| Concern | Current evidence | Target |
|---|---|---|
| This repository | `CURRENT LIVE`: naming placeholder only | Public bootstrap archive |
| Steam operational execution | `UNKNOWN` from this checkout | SteamCloud on Campfire |
| Generic durable execution | `UNKNOWN` | Campfire on Ember |
| Steam semantic/evidence authority | `UNKNOWN` | SteamGraph on a separate Ember authority |
| Product/evidence planes | `UNKNOWN` | Bounded owners using named actions and closed semantic contracts |
| V1 sample | `REFERENCE/PROTOTYPE` | Historical provenance only |
| Live migration/canary | None observed | `BLOCKED/NOT QUALIFIED` pending independent gates |

No repository rename alone changes any authority.

## Files and artifact disposition

### Updated

- `.gitignore`: excludes the reviewed architecture ZIP.
- `README.md`: minimal public-placeholder notice and documentation authority.
- `CONTRIBUTING.md`: documentation-only and safety rules.
- `.github/workflows/ci.yml`: replaces sample application CI with archive-only
  validation and no production identity or secret access.

### Created

- `docs/architecture/AUTHORITY_AND_BOUNDARIES.md`
- `docs/architecture/OBSERVABILITY.md`
- `docs/decisions/ADR-002-placeholder-archive-disposition.md`
- `docs/roadmap/MIGRATION_ROADMAP.md`
- `docs/security/SECURITY_AND_SECRET_PLACEMENT.md`
- `docs/migration/ACCEPTANCE.md`
- `docs/migration/ADMINISTRATOR_HANDOFF.md`
- `docs/migration/BOOTSTRAP_REPORT.md`
- `docs/migration/NAMING_ALIASES.json`
- `docs/migration/SIBLING_DEPENDENCIES.json`
- `docs/migration/REPOSITORY_INVENTORY.json`
- `docs/archive/placeholder/README.md`
- `docs/archive/placeholder/V1_SAMPLE_MANIFEST.sha256`
- `scripts/validate_placeholder.py`

### Archived and intentionally retained

- commits `f18a068` and `069c244`, tree `dcc70bd`, and PR #1 history;
- every old content digest and path in
  `docs/archive/placeholder/V1_SAMPLE_MANIFEST.sha256`;
- the old manifest's own digest in the provenance README;
- unique sample state, fencing, idempotency, uncertainty, schema, fixture, test,
  policy, review, and CI knowledge through immutable Git history.

### Removed from the current tip

The 79 old tracked paths other than the four updated files were removed.
Every old path is enumerated by the archived manifest, except the old
`MANIFEST.sha256` itself, which is copied as that archived manifest. Categories
removed from the tip include root duplicate authorities, `crates`, `src`,
`test`, `schemas`, `operations`, `packs`, `profile`, `review`, the old sample
validator, Cargo/npm package metadata, generated metadata, and sample fixtures.
The existing workflow path was retained but its sample application commands
were replaced with archive-only checks.

The removal prevents public sample material from being mistaken for the
history-bearing implementation while retaining exact recovery evidence.

### Cleanup

- Architecture ZIP: removed after successful integration; its digest and
  package version remain recorded in this report and `.gitignore` prevents
  recurrence.
- Temporary package extraction: removed.
- Temporary package-verification and audit-tool directories: removed after the
  final secret scan; no downloaded audit binary or package remains.
- Generated Rust `target/` and empty superseded sample directories: removed.

## Validation evidence

### Original sample baseline

| Command | Outcome |
|---|---|
| `npm test` | PASS, 20 tests |
| `cargo fmt --all -- --check` | PASS |
| `npm run check` | FAIL only because the untracked v2 ZIP was an extra old-manifest subject |
| Direct old tracked-manifest audit | PASS, all 82 listed subjects |
| `cargo clippy --workspace --all-targets -- -D warnings` | NOT RUN TO COMPLETION: linker `cc` unavailable during the baseline attempt |
| `cargo test --workspace` | NOT RUN TO COMPLETION: linker `cc` unavailable during the baseline attempt |
| Latest remote sample CI at base HEAD | PASS |

The Rust prerequisite failure does not block archival bootstrap because the
Rust package is a preserved historical prototype, not current scaffolding.

### Final archive checks

| Check | Outcome |
|---|---|
| `python3 scripts/validate_placeholder.py` | PASS |
| Exact current-tree allowlist and ZIP/app/operational-workflow absence | PASS |
| JSON syntax, duplicate-key, required-field, status, alias, dependency, and inventory semantics | PASS |
| Workflow YAML syntax, triggers, read-only permission, and non-persisted checkout credentials | PASS |
| Markdown relative paths and anchors | PASS |
| Base ancestry, Git archive reconstruction, original manifest identity, and all 82 content digests | PASS |
| High-confidence secret-pattern scan over every allowed file | PASS |
| `gitleaks detect --no-git --source . --no-banner --redact --exit-code 1` over the final bytes | PASS; `no leaks found` |
| Manual public-content/private-detail review | PASS; only migration names required by the directive are disclosed, with no private sibling SHA or settings export |
| `git diff --check` | PASS |
| `git fsck --full` | PASS |

The validator used `PyYAML==6.0.3` as a validation-only dependency. It is not a
runtime package or publication dependency.

## Remaining `UNKNOWN` state and blockers

- Deployed authority and qualification of all sibling systems.
- Private/internal package state and consumers.
- Repository-linked Projects v2 state (`UNKNOWN`: inventory token lacked
  `read:project`).
- Organization/GitHub App hooks and external repository-name consumers.
- External DNS, custom-domain, registry, and hosted Action references.
- Private `steam-platform` history/content safety and exact settings.
- Administrator choice of final archive name if not
  `SteamCloud-bootstrap-archive`.
- All runtime migration and authority gates.

These do not block the documentation bootstrap. They explicitly block the
administrator rename or any runtime cutover until resolved.

## Next safe PR wave

After this bootstrap lands, the next safe wave is administrator evidence only:
mirror backups, settings exports, package/Action/Page/domain/webhook dependency
review, public-content review, and a dry-run/rollback review. No rename or live
authority change belongs in that PR wave.

## Administrator-only actions

The exact unexecuted sequence is in
[ADMINISTRATOR_HANDOFF.md](ADMINISTRATOR_HANDOFF.md): move this placeholder,
verify the canonical name is free, then separately authorize the private
history-bearing rename. Visibility changes, production-secret movement, and
runtime cutovers remain separate decisions.
