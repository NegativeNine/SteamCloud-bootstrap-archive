# Observability and Audit — SteamCloud

Every event carries the smallest applicable set of:

```text
trace_id, tenant_id, principal_id, product_id,
run_id, work_id, action_intent_id, attempt_id,
account_id, operation, policy_revision,
runtime_generation, credential_generation, egress_id,
artifact_digest, publication_id, source_class
```

Never emit plaintext authorization headers, Steam credentials, browser owner tokens, Rust+ pairing tokens, signing private keys or raw challenge responses.

Required metrics include admission decisions, work/attempt state, uncertain outcomes, resource lease conflicts, egress throttles, artifact bytes, publication latency, parity mismatches, stale dependency pins and privacy/erasure propagation lag.
