# Test Assessment — SteamCloud

## Original frozen repository

Commands in `review/commands.md` were not executed for existing repositories. Static source inspection must not be reported as runtime qualification.

## Generated sample repository

- Primary local command: `node --test`
- JSON/schema validation: `python3 scripts/validate_repository.py`
- Manifest validation: included in the same script

- The Rust reference crate is included but was not compiled locally because the environment has no Rust toolchain. CI installs stable Rust and runs `cargo test`.

## Required production tests

- Contract positive and negative fixtures
- Cross-tenant authorization
- Duplicate delivery and idempotency
- Stale generation/resource fencing
- Secret-leak scans
- Dependency outage, restart and rollback
- Privacy/erasure propagation
- Repository-specific acceptance gates in `docs/ACCEPTANCE.md`
