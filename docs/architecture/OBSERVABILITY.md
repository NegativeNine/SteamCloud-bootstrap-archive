# Observability and Correlation Vocabulary

**Document status:** Current placeholder audit vocabulary and target runtime
vocabulary. The target fields are `TARGET`, not implemented here.

## Status

| Status | Evidence |
|---|---|
| `CURRENT LIVE` | This repository emits no runtime telemetry. |
| `IMPLEMENTED BUT NOT LIVE` | None in the current tree. |
| `SHADOW/CANARY` | None observed. |
| `REFERENCE/PROTOTYPE` | Historical v1 sample fields remain in Git history. |
| `BLOCKED/NOT QUALIFIED` | Any runtime telemetry claim based on this repository. |
| `TARGET` | The correlation chain and attributes below. |

## Migration audit vocabulary

Every repository-name operation should record, without secret values:

```text
decision_id
actor_identity
repository_id
source_repository_name
target_repository_name
source_head
settings_export_id
backup_artifact_digest
public_content_review_id
started_at
completed_at
rollback_target
```

Store this audit record in the access-controlled administrator evidence
location described in the
[administrator handoff](../migration/ADMINISTRATOR_HANDOFF.md), never in this
public repository.

## Target runtime correlation chain

```text
ProductRequestId
  -> Campfire RunId
  -> WorkItemId
  -> ActionIntentId
  -> AttemptId
  -> SteamCloud DeliveryId
  -> ProviderRequestId / ProviderReceiptId
  -> SourceArtifactDigest
  -> SteamGraph MutationIdentity
  -> SteamGraph CommitReceipt
  -> ProjectionGeneration
```

Target OpenTelemetry service names include `ember-campfire`,
`ember-steamgraph`, `campfire-api`, `campfire-scheduler`,
`steamcloud-control`, `steamcloud-edge-bff`, `steamcloud-agent-gateway`,
`steamcloud-agent-host`, `steamcloud-auth-runner`, `steamcloud-scraper`,
`steamgraph-api`, `steamgraph-cdc`, and `steamgraph-projector`.

Target OpenTelemetry attributes include `campfire.run.id`,
`campfire.work.id`, `campfire.action_intent.id`, `campfire.attempt.id`,
`steamcloud.operation.name`, opaque SteamCloud resource IDs and generations,
`steamcloud.execution.authority`, `steamgraph.mutation.id`,
`steamgraph.profile.digest`, `artifact.digest`, and `deployment.release.id`.

Never place credentials, cookies, challenge material, usernames, raw account
identifiers, arbitrary URLs, request bodies, or other high-cardinality payloads
in metric labels. Correlation never substitutes for idempotency or authority
fencing.
