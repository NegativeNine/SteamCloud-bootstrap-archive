# Test Assessment — SteamCloud

## Original frozen repository

Commands in `review/commands.md` were not executed for existing repositories. Static source inspection must not be reported as runtime qualification.

## Generated sample repository

- Primary local command: `npm test` (`node --test`)
- Syntax, schema, forbidden-field and manifest validation: `npm run check` (runs `python3 scripts/validate_repository.py`)
- Manifest validation: included in the same script
- Rust: CI runs `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, and `cargo test --workspace`. A local `cargo test` needs a C linker (`cc`), not only `rustc`.

## Required production tests

- Contract positive and negative fixtures
- Cross-tenant authorization
- Duplicate delivery and idempotency
- Stale generation/resource fencing
- Secret-leak scans
- Dependency outage, restart and rollback
- Privacy/erasure propagation
- Repository-specific acceptance gates in `docs/ACCEPTANCE.md`
