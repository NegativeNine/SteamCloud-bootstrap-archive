# Contributing

This is a public naming placeholder being prepared for archival. Contributions
must remain documentation-only and must follow the authority map linked from
the [README](README.md).

Do not add:

- application code, operational workflows, deployment configuration, schemas,
  or packages (the archive validator and its CI workflow are the only
  executable exceptions);
- private `steam-platform` history or implementation detail;
- credentials, secret values, secret-looking fixtures, or production data;
- a generic Steam proxy, arbitrary command surface, or user-selected upstream;
- claims that a target, reference, shadow, or canary capability is live.

All dependency state not proven from authoritative evidence stays `UNKNOWN`.
Repository renames, visibility changes, and live authority changes require
separate administrator authorization.

Use the repository's archive-record issue form only for a broken documentation
link, historical provenance correction, or archive-safety issue. Blank issues
are disabled. Feature, runtime, package, deployment, production, and authority
requests are out of scope. Never place a credential, token, personal datum,
private source, or production datum in an issue.

Use the commands in
[Acceptance and validation gates](docs/migration/ACCEPTANCE.md) before review.
That currently means `python3 scripts/validate_placeholder.py` and
`python3 scripts/test_validate_placeholder.py` after pinned PyYAML 6.0.3,
markdown-it-py 3.0.0, and mdurl 0.1.2 validation dependencies are available.
Run `python3 phase-00/validate.py` and `python3 phase-00/test_validate.py` on
the exact Phase 00 commit, and `python3 phase-01/validate.py` plus
`python3 phase-01/test_validate.py` on exact historical Phase 01 commit
`4ec31555d6b94d5f2a51638c37be11575d3a1740`, using detached worktrees as the
hosted workflow does. Those phase validators seal historical boundaries; they
must not be repurposed as current architecture or schema authority.
