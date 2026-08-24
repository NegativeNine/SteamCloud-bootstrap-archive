# Phase 01 historical usability

This additive candidate implements the final-synthesis Phase 01 archive boundary. It inventories and
checks every supported repository-local inline Markdown, reference-definition, HTML, and heading-
fragment destination while ignoring fenced and inline code. The exact destination inventory is
digest-bound by the validator. It records exact read-only recovery for the historical v1 source and
supplies a closed issue form for link, provenance, and archive-safety corrections.

The phase accepts no feature work. It adds no runtime, package, contract, schema dialect, provider
adapter, deployment workflow, data collection, telemetry, effect, or authority role. The current
archive setting, default branch, freeze tag, private SteamCloud incumbent, deployments, traffic,
secrets, DNS, and CurrentAuthority are unchanged.

## Commands

```bash
python3 phase-01/validate.py
python3 phase-01/test_validate.py
```

The ordinary hosted workflow first validates the exact Phase 00 commit in an isolated detached
worktree, then runs these Phase 01 checks. Command rows in the closeout are narrative records; hosted
check identities and an independent review remain separate evidence.

The exact historical source archive is reproducible. The retained Node checks are bounded execution
observations. The Rust build is explicitly `NOT_REPRODUCIBLE_STRUCTURALLY_UNPINNED`; no passing Rust
result is claimed because the historical tree has no lockfile or pinned toolchain/environment.

The executable fault corpus maps each exact positive and negative case to one retained test method.
Machine status, closeout, artifact paths, issue intake, and YAML/JSON parsing are closed and reject
unknown fields, claim inflation, duplicate keys, non-finite JSON, traversal, and symlinks.

## Rollback

Before merge, close the Phase 01 pull request and remove only its candidate branch. If separately
merged, revert every Phase 01 seal and source commit newest-first to exact Phase 00 head
`9554180db2b73b426a87128e10fbe12c097ee786` and tree
`e0a9e141f14bdfd3b90131ff0ec55551393777a8`. No runtime drain, data reconciliation, deployment
rollback, or authority selection is required because this phase creates none.
