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
docs/                 current state, target architecture, boundaries and roadmap
review/               machine-readable adversarial review output
schemas/              shared cross-repository contracts and fixtures
src/ or crates/       executable reference/sample implementation
test/ or tests/       sample conformance tests
scripts/              package validator
.github/workflows/    required CI gates
MANIFEST.sha256       file integrity manifest
```

## Local validation

```bash
python3 -m pip install jsonschema PyYAML
python3 scripts/validate_repository.py
```

```bash
node --test
```

Rust reference crates, where included, are exercised by GitHub Actions. This generation environment did not contain a Rust toolchain.

## Read first

1. `CURRENT_STATE.md`
2. `TARGET_ARCHITECTURE.md`
3. `AUTHORITY_AND_BOUNDARIES.md`
4. `ROADMAP.md`
5. `review/report.json`
