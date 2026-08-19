# Administrator Handoff

**Document status:** `TARGET` procedure. Nothing in this document has been
executed. Repository and sibling state not proven at action time is
`UNKNOWN` and blocks the rename.

The placeholder itself is `CURRENT LIVE`; its documentation is
`IMPLEMENTED BUT NOT LIVE`; no `SHADOW/CANARY` exists; old sample content is
`REFERENCE/PROTOTYPE`; and all runtime or rename actions remain
`BLOCKED/NOT QUALIFIED` until their gates pass.

## Intended outcome

1. Preserve and move this public placeholder to
   `SteamCloud-bootstrap-archive` or another explicitly approved archive name.
2. Verify the canonical `NegativeNine/SteamCloud` name is available.
3. Separately authorize the private history-bearing `steam-platform`
   repository to be renamed to `SteamCloud`.
4. Keep the renamed implementation private. Review completion does not
   authorize a visibility change; that requires a separate explicit decision.

This sequence changes repository names only. It must not change live execution
or semantic authority, deploy a service, arm a timer/cohort, move credentials,
or change visibility.

## Reviewed public-placeholder state

The detailed machine-readable snapshot is in
[REPOSITORY_INVENTORY.json](REPOSITORY_INVENTORY.json). That file keeps two
distinct observations:

- `repository.head` remains the v1 sample tip `069c244` (PR #1), because that
  is the unique content that must survive as provenance.
- `archive_handoff.head` is the merged PR #2 archive-handoff tip `541ff22`,
  which is the current published tree before later uncommitted bootstrap
  refreshes.

At the v1 snapshot the repository had one branch, no tags/releases/issues,
merged PR #1, and the sample CI workflow. At the 2026-08-19 refresh the
published HEAD was `541ff22`, PR #2 was merged, the active workflow name was
`placeholder-archive-validation`, and there were still no tags, releases,
issues, repository webhooks, Pages site, environments, or deployments. Private
or internal package state and external integration state remain `UNKNOWN`.

Re-run every inventory immediately before the administrator action; this is a
snapshot, not a lock.

All settings exports, backups, secret-name inventories, audit identities,
private SHAs, and integration evidence belong in an access-controlled location
outside this public checkout. Record only a redacted approval/evidence reference
here; never commit the export or backup itself.

## Export and dependency checklist

- [ ] Record repository ID, visibility, default branch, description, topics,
  features, merge settings, collaborators, teams, and GitHub App installations.
- [ ] Mirror all refs, including branches, tags, notes, and pull-request refs;
  checksum the backup and perform a test restore.
- [ ] Export issues, PRs, discussions, projects, wiki state, releases, release
  assets, Git LFS objects, and attachments where enabled.
- [ ] Export branch protection, rulesets, CODEOWNERS state, environments,
  deployment protection rules, and required checks.
- [ ] Export Actions permissions, workflow definitions, run metadata,
  artifacts, caches, variables, and **secret names only**. Never export secret
  values into this repository or handoff document.
- [ ] Inventory deploy keys, repository webhooks, organization hooks, GitHub
  Apps, OAuth integrations, and external automation keyed by repository ID or
  full name.
- [ ] Inventory GitHub Packages and external registries using credentials with
  the required read scope; record consumers, immutability rules, and retention.
- [ ] Verify no sibling workflow uses this repository as a reusable Action.
  GitHub repository redirects do not preserve hosted Action references.
- [ ] Verify GitHub Pages, custom domains, DNS records, CDN routes, certificates,
  and external links. Record explicit `NONE` evidence where appropriate.
- [ ] Inventory security settings, alerts, Dependabot, secret scanning, push
  protection, private vulnerability reporting, and audit-log events.
- [ ] Complete a public-content and secret-history review of this archive.
- [ ] Independently review the private `steam-platform` history before any
  visibility decision; do not copy it into this public repository.

## Administrator sequence — prepare, do not automate here

1. Freeze repository-setting changes for the maintenance window.
2. Complete and approve the checklist above.
3. Create and verify mirror/settings backups for both repositories.
4. Rename this placeholder to the approved archive name, preserving visibility,
   `archived=false`, and all history. Do not toggle the GitHub Archived setting.
5. Verify archive refs, PRs, settings, integrations, Actions history, and links.
6. Verify `NegativeNine/SteamCloud` is available and that reclaiming it will not
   destroy a required redirect or hosted Action reference.
7. Obtain separate authorization for the private history-bearing rename.
8. Rename private `steam-platform` to `SteamCloud` in place and keep it private;
   review completion does not authorize publication.
9. Update remotes, dependency manifests, images, registries, deploy keys,
   webhooks, Apps, CI, service discovery, documentation, and deployment units in
   their owning systems.
10. Prove existing deployments still point at the same commits and artifacts.
    A repository rename is not a runtime cutover.

## Rollback

Before step 8, rename the archive back to `SteamCloud` if any placeholder
dependency, setting, or history is lost. After step 8, use the separately
reviewed private-repository rollback procedure; do not improvise by creating a
new `steam-platform` repository because that can invalidate redirects.

Record the actor, decision ID, source and target names, source HEAD, backup
digest, settings export ID, public-content review ID, completion time, and
rollback target for every administrator action.
