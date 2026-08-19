# Bootstrap Report

**Report date:** 2026-08-19

**Repository:** `NegativeNine/SteamCloud` public naming placeholder

**Reviewed pre-edit HEAD:** `541ff226a963ffa9acc1fcc6062b6878c2832592`

**v1 sample provenance tip:** `069c2448ee3c5e7c352d096494d15e8f120cf433`

**Package:** `SteamCloud-SteamGraph-Refined-Architecture-v2.0`, version
`2.0.0-draft`

It is not the production SteamCloud implementation.

No live authority, remote repository, visibility, or production secret was changed.

## 1. Repository and HEAD reviewed

| Field | Evidence |
|---|---|
| Root | `/home/scdb/SteamCloud` |
| Branch | `main`, tracking `origin/main` |
| Pre-edit HEAD | `541ff226a963ffa9acc1fcc6062b6878c2832592` |
| Pre-edit tree | `967d1cac973e3b2bfc537a0ff4939141b6cc272b` |
| Remote | `origin https://github.com/NegativeNine/SteamCloud` (fetch and push) |
| Tags | None |
| Notes / stash | None |
| Pre-edit `git status` | Clean tracked tree; up to date with `origin/main`; no uncommitted work |
| Identity gate | PASS: public placeholder with generated v1 sample plus PR #1 and the PR #2 archive handoff. This is not private `steam-platform` and no private history was imported. |

Visible commits:

- `f18a068` — Initialize SteamCloud from the v1.0 rearchitecture sample
- `069c244` — Separate sample policy from catalog I/O (#1)
- `7eba30f` — Prepare SteamCloud placeholder archive
- `541ff22` — Merge pull request #2 from `NegativeNine/agent/bootstrap-placeholder-archive`

The 2026-08-18 bootstrap already resolved the source/history collision (populated v1 sample instead of an empty placeholder) by preserving that sample in Git history and leaving a documentation-only archive tip. This 2026-08-19 run is a discovery refresh and validator strengthening on that merged tip. It is not a greenfield replacement.

Pre-existing modifications: none. Unrelated uncommitted work: none. Nothing was committed or pushed.

## 2. Architecture package digest and validation result

The architecture ZIP is absent from this checkout (removed after the PR #2
integration). It was re-verified from a non-committed copy of the same bytes.
The ZIP was not added to this tree.

| Check | Result |
|---|---|
| Required outer SHA-256 | `b3103485838efa9bc1e129a6ea24a0ea362ba704fc365fd783b82b3c5c41a1a9` — PASS |
| Extraction | temporary extract under the private implementer scratch directory — PASS |
| Package `MANIFEST.sha256` | every listed artifact — PASS |
| `python3 validate.py` | `validation passed` — PASS |
| Package version | `2.0.0-draft` |

The package was read in the prescribed order, including the repository-relevant
SteamCloud architecture document, ADRs, manifests, contracts, examples,
reference adapters, and diagrams. It is `TARGET` / `REFERENCE/PROTOTYPE`
guidance only. It is not proof that any target capability is implemented or
production-qualified. Package contracts, examples, adapters, and diagrams were
not copied into this public tree.

The extract directory is deleted after integration. `.gitignore` ignores
`SteamCloud-SteamGraph-Refined-Architecture-*.zip` and the extracted
`SteamCloud-SteamGraph-Refined-Architecture-v2.0/` directory.

## 3. Files created, updated, moved, archived, deleted, and retained

### Created in this refresh

- `scripts/test_validate_placeholder.py` — drives the shipped validator entry
  point and its failure paths (ZIP present, application scaffold present,
  duplicate JSON keys, ledger COMPLETE-without-commit, and admin-phase
  COMPLETE refusal).
- `docs/roadmap/PHASE_LEDGER.json` — machine-verifiable phase and wave
  ledger for Phases 0–4.

### Updated in this refresh

- `README.md` — validation section; still states this is not the production
  SteamCloud implementation.
- `CONTRIBUTING.md` — names the validator and test commands.
- `.gitignore` — also ignores an extracted package directory.
- `.github/workflows/ci.yml` — still `placeholder-archive-validation`; now
  also runs the failure-path tests.
- `docs/architecture/OBSERVABILITY.md` — records TARGET OpenTelemetry service
  names from the package without claiming they are live.
- `docs/decisions/ADR-002-placeholder-archive-disposition.md` — notes the
  2026-08-19 refresh still accepts the archive disposition.
- `docs/roadmap/MIGRATION_ROADMAP.md` — Phase 0 is the merged PR #2 handoff;
  this refresh is documentation-only.
- `docs/migration/ACCEPTANCE.md` — includes the test command.
- `docs/migration/ADMINISTRATOR_HANDOFF.md` — distinguishes the v1 snapshot
  HEAD from the merged archive-handoff HEAD.
- `docs/migration/REPOSITORY_INVENTORY.json` — retains the 069c244 snapshot
  and adds `archive_handoff` / `this_bootstrap` observations for `541ff22`.
- `docs/migration/BOOTSTRAP_REPORT.md` — this file.
- `scripts/validate_placeholder.py` — asserts ZIP/scaffold absence, six
  status labels, archive-only workflow, UNKNOWN siblings, alias coverage,
  bootstrap-report evidence, and high-confidence secret patterns.

### Moved

None.

### Archived

No additional archive. Unique v1 sample content remains under
`docs/archive/placeholder/` with provenance, plus immutable Git history at
`f18a068` / `069c244`.

### Deleted

None from the tracked tree. The architecture ZIP was already absent. The
temporary 2026-08-19 extract is removed from the implementer scratch
directory and is not a repository path.

### Intentionally retained

- All PR #2 archive-handoff documents and the allowlisted tree.
- `docs/archive/placeholder/README.md` and `V1_SAMPLE_MANIFEST.sha256`.
- Canonical/legacy aliases, sibling `UNKNOWN` pins, security rules, and the
  unexecuted administrator handoff.
- Historical sample knowledge (state machines, fences, retry/uncertainty,
  schemas, tests) only as Git history, not as current contracts.

### Not created (deliberate)

- No application scaffold, schemas, queues, packages, or runtime.
- No generic Steam proxy.
- No `TARGET_ARCHITECTURE_2.md`, `NEW_ROADMAP.md`, `AGENTS.md`, or `CLAUDE.md`.
- No copy of the refined architecture package or private `steam-platform`
  history.

## 4. Current authority and target authority

| Concern | Status | Authority |
|---|---|---|
| This public repository | `CURRENT LIVE` | Naming placeholder only; no runtime, data, credential, execution, or semantic authority. |
| Archive documentation and validator | `IMPLEMENTED BUT NOT LIVE` | Present on the branch tip; not a SteamCloud service. |
| Live canary / shadow runtime | `SHADOW/CANARY` | None observed. |
| v1 sample at `069c244` | `REFERENCE/PROTOTYPE` | Recoverable in Git history; never observed live. |
| Refined architecture v2.0 | `REFERENCE/PROTOTYPE` / `TARGET` | Verified draft package; not copied here. |
| Any use as SteamCloud service, package, schema, or deployment | `BLOCKED/NOT QUALIFIED` | Explicitly forbidden in this repository. |
| Ember | `UNKNOWN` here / `TARGET` generic durable data substrate | Not evidenced from this checkout. |
| Campfire | `UNKNOWN` here / `TARGET` generic durable execution on Ember | Not evidenced from this checkout. |
| SteamCloud implementation | `UNKNOWN` here / `TARGET` Steam operational domain on Campfire | History-bearing code remains private `steam-platform` until a separately authorized rename. |
| SteamGraph | `UNKNOWN` here / `TARGET` Steam semantic/evidence domain on a separate Ember authority | History-bearing predecessor remains `steam-hypergraph` until a separately authorized rename. |
| Product / evidence planes | `UNKNOWN` here / `TARGET` bounded owners | Invoke SteamCloud only through named Steam actions; use SteamGraph only through closed semantic contracts. |

A repository rename does not change runtime authority.

## 5. Migration scaffolding implemented

Non-authoritative scaffolding only:

- README-led documentation authority under `docs/architecture`,
  `docs/decisions`, `docs/migration`, `docs/roadmap`, `docs/security`, and
  `docs/archive/placeholder`.
- Naming alias registry for recorded legacy operation, profile, pack, and
  repository names.
- Sibling dependency pins remain `reviewed_sha: null` and
  `observed_status: UNKNOWN`, with empty `runtime_dependencies`.
- Security and secret-placement rules for this public tree plus TARGET
  vault/edge/runtime placement.
- Observability/correlation vocabulary, including TARGET service names.
- Phased roadmap with gates and rollback.
- Administrator export/dependency checklist and unexecuted rename sequence.
- Archive validator and failure-path tests. They qualify only this
  placeholder archive, not Ember, Campfire, SteamCloud, or SteamGraph.

No timer, cohort, credential, datastore, or live read/write path was added.

## Validation evidence

## 6. Tests and checks run with exact outcomes

Recorded under the private implementer scratch directory. Commands were run
from `/home/scdb/SteamCloud` after the documentation/validator refresh.

| Check | Outcome |
|---|---|
| Architecture package SHA-256 / MANIFEST / `validate.py` | PASS (`validation passed`) |
| `python3 -c 'import yaml; assert yaml.__version__ == "6.0.3"'` | PASS |
| `python3 scripts/validate_placeholder.py` run 1 | PASS: `placeholder archive validation passed` |
| `python3 scripts/validate_placeholder.py` run 2 | PASS: `placeholder archive validation passed` |
| `python3 scripts/test_validate_placeholder.py` | PASS: 7 tests, `placeholder archive tests passed` |
| `git diff --check` | PASS (no output) |
| `git diff --cached --check` | PASS (no output) |
| `git fsck --full` | PASS (exit 0). One dangling blob warning (`9829df3...`) was reported; it is not a reachability failure and does not block bootstrap. |
| High-confidence secret-pattern scan in the shipped validator | PASS (part of both validator runs) |
| Independent secret scan over 19 git-visible files | PASS: `no high-confidence secret patterns found` |
| Application lint / type-check / schema-parity / runtime tests | NOT APPLICABLE: no application package remains. Does not block bootstrap. |
| `gitleaks` binary | NOT RUN: no `gitleaks` executable on PATH. Does not block bootstrap because the shipped validator and the independent regex scan cover the same high-confidence classes. |

## 7. Unresolved tensions or blockers

These do not block this documentation bootstrap. They block administrator
rename and any runtime cutover:

- Deployed authority and qualification of Ember, Campfire, `steam-platform`,
  and `steam-hypergraph` remain `UNKNOWN` from this public checkout.
- Private/internal package state and consumers (`UNKNOWN`: token lacked
  `read:packages`).
- Repository-linked Projects v2 (`UNKNOWN`: token lacked `read:project`).
- Organization/GitHub App hooks and external repository-name consumers.
- External DNS, custom-domain, registry, and hosted Action references.
- Private `steam-platform` history/content safety and exact settings. Those
  must be reviewed in the private repository, not copied here.
- Administrator choice of final archive name if not
  `SteamCloud-bootstrap-archive`.
- This working tree is intentionally uncommitted (operator did not request a
  commit or push).

## 8. Next safe PR wave

Administrator evidence only. No rename. No live authority change.

- Mirror backups and settings exports for this placeholder and, separately,
  for private `steam-platform`.
- Package / Action / Page / domain / webhook / App / deploy-key dependency
  review.
- Public-content and secret-history review of this archive.
- Dry-run and rollback review of the rename sequence.

## 9. Administrator-only actions still required

Prepare, do not execute from this bootstrap:

1. Rename this placeholder away from `SteamCloud` to
   `SteamCloud-bootstrap-archive` or another explicitly approved archive name
   without toggling the GitHub Archived setting or changing visibility.
2. Verify the canonical `NegativeNine/SteamCloud` name is free and that
   reclaiming it will not destroy a required redirect or hosted Action
   reference.
3. Separately authorize the private history-bearing `steam-platform`
   repository to be renamed to `SteamCloud` and kept private.
4. Complete public-content review of this archive before the placeholder
   move.
5. Independently review private `steam-platform` history before any
   visibility decision. Do not copy that history into this public repository.

The exact unexecuted checklist is
[ADMINISTRATOR_HANDOFF.md](ADMINISTRATOR_HANDOFF.md).

## 10. Confirmation

No live authority, remote repository, visibility, or production secret was changed.

Specifically: no production source of truth was switched; no timer or live
cohort was armed; no credentials were moved; no private service was exposed;
no remote GitHub repository was renamed, archived, published, or had its
visibility changed; no Pages, package, webhook, or production secret was
modified. Publication of this refresh, if an operator later commits it,
changes only public archive documentation and archive-validation workflow
content.

---

## Prior 2026-08-18 discovery (preserved)

The remainder of this report retains the unique evidence collected when the
populated placeholder was first converted into an archive handoff. The HEAD
and workflow names in that section describe the pre-archive v1 sample tip,
not the current published tip.

### Outcome at 2026-08-18

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

### Package verification at 2026-08-18

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

### Local checkout before the 2026-08-18 edit

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

### Visible GitHub inventory at 2026-08-18T22:38:13Z

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

### Current implementation and operational inventory at the v1 tip

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

### Package conflicts reconciled

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

### Files and artifact disposition at PR #2

#### Updated

- `.gitignore`: excludes the reviewed architecture ZIP.
- `README.md`: minimal public-placeholder notice and documentation authority.
- `CONTRIBUTING.md`: documentation-only and safety rules.
- `.github/workflows/ci.yml`: replaces sample application CI with archive-only
  validation and no production identity or secret access.

#### Created

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

#### Archived and intentionally retained

- commits `f18a068` and `069c244`, tree `dcc70bd`, and PR #1 history;
- every old content digest and path in
  `docs/archive/placeholder/V1_SAMPLE_MANIFEST.sha256`;
- the old manifest's own digest in the provenance README;
- unique sample state, fencing, idempotency, uncertainty, schema, fixture, test,
  policy, review, and CI knowledge through immutable Git history.

#### Removed from the current tip

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

#### Cleanup at PR #2

- Architecture ZIP: removed after successful integration; its digest and
  package version remain recorded in this report and `.gitignore` prevents
  recurrence.
- Temporary package extraction: removed.
- Temporary package-verification and audit-tool directories: removed after the
  final secret scan; no downloaded audit binary or package remains.
- Generated Rust `target/` and empty superseded sample directories: removed.

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

### Final archive checks at PR #2

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
