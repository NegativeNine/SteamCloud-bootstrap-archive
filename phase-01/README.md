# Phase 01 historical usability

This additive candidate implements the final-synthesis Phase 01 archive boundary. A pinned
markdown-it-py 3.0.0 CommonMark token traversal inventories every active link and image occurrence,
including reference uses, autolinks, nested images, links nested in images, and active inner links when
an enclosing bracket construct is not a link. Raw HTML `href` and `src` attributes are also checked;
fenced code, inline code, and inactive Markdown inside raw HTML blocks are not treated as links. Each
occurrence retains its containing CommonMark block line span and document-local ordinal, so repeated
destinations are never deduplicated. A separate bounded syntax audit gives stable typed failures for
malformed angle destinations, titles, tails, multiline forms, and depth or size limits. Quoted titles
may contain unmatched literal parentheses. Reference-definition auditing runs inside the pinned parser
rule and maps parser positions to exact original offsets across blockquotes, nested blockquotes, wide
and nested lists, list-plus-blockquote combinations, multiline forms, tabs, and CRLF input. Definition
order and source spans are retained, and case-equivalent duplicates are rejected across containers.
The exact 26-destination repository inventory and its
location identities are digest-bound by the validator. It records exact read-only recovery for the
historical v1 source and supplies a closed issue form for link, provenance, and archive-safety
corrections.

The phase accepts no feature work. It adds no runtime, package, contract, schema dialect, provider
adapter, deployment workflow, data collection, telemetry, effect, or authority role. The current
archive setting, default branch, freeze tag, private SteamCloud incumbent, deployments, traffic,
secrets, DNS, and CurrentAuthority are unchanged.

## Commands

```bash
python3 -m pip install --disable-pip-version-check markdown-it-py==3.0.0 mdurl==0.1.2 PyYAML==6.0.3
python3 phase-01/validate.py
python3 phase-01/test_validate.py
```

The ordinary hosted workflow first validates the exact Phase 00 commit in an isolated detached
worktree, then runs these Phase 01 checks. Command rows in the closeout are narrative records; hosted
check identities and an independent review remain separate evidence.

The exact historical source archive is reproducible. The retained Node checks are bounded execution
observations. The Rust build is explicitly `NOT_REPRODUCIBLE_STRUCTURALLY_UNPINNED`; no passing Rust
result is claimed because the historical tree has no lockfile or pinned toolchain/environment.

The executable fault corpus maps 24 positive and 58 negative cases to 82 retained test methods.
Machine status, closeout, artifact paths, issue intake, and YAML/JSON parsing are closed and reject
unknown fields, claim inflation, duplicate keys, non-finite JSON, traversal, and symlinks.
Closeout command results, limitations, blockers, non-claims, and unblocks are exact structural
allowlists. Rollback is a typed newest-first record: the validator resolves the current seal, binds
each prior commit and expected intermediate tree in order, and requires the exact Phase 00 target.

## Rollback

Before merge, close the Phase 01 pull request and remove only its candidate branch. If separately
merged, revert every Phase 01 seal and source commit newest-first to exact Phase 00 head
`9554180db2b73b426a87128e10fbe12c097ee786` and tree
`e0a9e141f14bdfd3b90131ff0ec55551393777a8`. No runtime drain, data reconciliation, deployment
rollback, or authority selection is required because this phase creates none.
