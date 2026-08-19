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

Use the commands in
[Acceptance and validation gates](docs/migration/ACCEPTANCE.md) before review.
That currently means `python3 scripts/validate_placeholder.py` and
`python3 scripts/test_validate_placeholder.py` after the pinned PyYAML
validation dependency is available.
