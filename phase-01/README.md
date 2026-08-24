# Phase 01 historical usability

This additive candidate implements the final-synthesis Phase 01 archive boundary. It checks every
repository-local Markdown link and heading fragment, records exact read-only recovery commands for the
historical v1 sample, and supplies a constrained issue form for link, provenance, and archive-safety
corrections.

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

## Rollback

Before merge, close the Phase 01 pull request and remove only its candidate branch. If separately
merged, revert the Phase 01 seal and source commits newest-first to exact Phase 00 head
`9554180db2b73b426a87128e10fbe12c097ee786` and tree
`e0a9e141f14bdfd3b90131ff0ec55551393777a8`. No runtime drain, data reconciliation, deployment
rollback, or authority selection is required because this phase creates none.
