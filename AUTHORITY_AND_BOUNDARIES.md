# Authority and Boundary Contract — SteamCloud

## Authority statement

Steam accounts, credential references/generations, sessions, runtime placement, egress, bot affinity, collection policies, Steam-specific operation catalog and effect adapters.

## Incoming dependencies

- Campfire
- Steam Hypergraph
- credential vault
- regional execution platform

## Downstream consumers

- all product planes

## Non-negotiable boundaries

1. A product plane does not become a second semantic or operational store.
2. A capability JWT authorizes one named action; it never contains a Steam password, refresh token, cookie, Web API key, Guard secret, player token or pairing token.
3. Campfire state is accessed through its service/profile contracts, never by writing Ember internals from a product or agent.
4. SteamCloud publishes artifacts and observations through authenticated Hypergraph prepared commands; it does not write facts directly.
5. Hypergraph does not obtain plaintext operational credentials.
6. Unknown, missing, declined, rate-limited, partial, unsupported and absent remain distinct.
7. N-ary participants retain role, ordinal and multiplicity.
8. Every projection is rebuildable and inherits privacy, erasure and purge watermarks.

## Secret keep-outside set

- Steam passwords and refresh tokens
- Steam Guard shared/identity secrets and challenge responses
- Steam web cookies and owner browser JWTs
- Publisher and platform Web API keys
- Rust+ AuthToken/playerToken, push credentials and active socket objects
- Signing private keys and product session secrets

These values belong only in browser session storage for the delegated owner flow, or in a dedicated KMS-backed vault/runtime lease for persistent operational accounts. The sample rejects them as JSON object keys using `schemas/forbidden-fields.json`.
