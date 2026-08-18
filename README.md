# SteamCloud

**Proposed rearchitected repository package — not a production deployment.**

Provide the operational Steam domain on Campfire, analogous to Steam Hypergraph on Ember.

## Platform role

- Role: Steam operational and automation domain platform on Campfire
- Authority: Steam accounts, credential references/generations, sessions, runtime placement, egress, bot affinity, collection policies, Steam-specific operation catalog and effect adapters
- Built on: Campfire
- Current assessment: NEW PROPOSAL / NOT IMPLEMENTED / NOT DEPLOYED
- Frozen source SHA: `0000000000000000000000000000000000000000`

## Repository shape

```text
CURRENT_STATE.md      frozen production-status assessment
TARGET_ARCHITECTURE.md
AUTHORITY_AND_BOUNDARIES.md
ROADMAP.md
docs/                 implementation, migration, acceptance, observability, ADRs
review/               machine-readable adversarial review output
schemas/              shared cross-repository contracts and fixtures
operations/           named SteamCloud operation catalog
packs/                data-only Campfire packs
profile/              Campfire domain profile
src/                  JavaScript sample implementation
test/                 Node conformance tests
crates/               Rust reference crate
scripts/              package validator
.github/workflows/    required CI gates
MANIFEST.sha256       file integrity manifest
```

## Sample implementation

The executable sample is a small in-process Campfire domain. Dependencies point toward policy, not the filesystem.

```text
src/index.js          public API and mock runtime construction
src/operations.js     admit, pack compile, argument digest, regional-agent exclusions
src/secrets.js        forbidden-field policy (reads schemas/forbidden-fields.json)
src/catalog.js        load operations/ and packs/ from disk
src/resource-leases.js
src/mock-agent.js     settlement + idempotent replay
src/projector.js      WorldView fold
crates/steamcloud-agent   credential/runtime generation fence
```

```js
import {
  admitOperation,
  createMockRuntime,
  loadOperationCatalog,
} from './src/index.js';

const catalog = loadOperationCatalog();
const admitted = admitOperation(
  { operation: 'steam.profile.public.refresh', accountClass: 'PLATFORM_PUBLIC_BOT', arguments: { subject: 'steam:1' } },
  catalog,
);
const { agent, leaseBook } = createMockRuntime();
```

Policy functions take an explicit catalog. They do not read `operations/` themselves.

## Local validation

```bash
python3 -m pip install jsonschema PyYAML
npm run check
npm test
```

`npm run check` syntax-checks `src/*.js` and runs `python3 scripts/validate_repository.py` (schemas, review JSON, forbidden-field scan, `MANIFEST.sha256`). `npm test` runs `node --test`.

CI also runs `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace`. Those need a Rust toolchain with a C linker (`cc`); `rustc` alone is not enough.

## Read first

1. `CURRENT_STATE.md`
2. `TARGET_ARCHITECTURE.md`
3. `AUTHORITY_AND_BOUNDARIES.md`
4. `ROADMAP.md`
5. `review/report.json`
