# Reproduce the historical v1 sample

This note preserves a bounded way to retrieve and test the public v1 architecture sample without
restoring it to the archive branch. The sample is `REFERENCE` history. It is not a current contract,
package, runtime, deployment, qualification result, or authority source.

## Exact identities

| Item | Identity |
|---|---|
| Reviewed sample commit | `069c2448ee3c5e7c352d096494d15e8f120cf433` |
| Reviewed sample tree | `dcc70bd212ff8d1499aa5f2141a429629bf066a5` |
| Deterministic Git archive SHA-256 | `e9667fd5da1f20aa933b0503ff2249fc7b6c42f66e94f4c671658085592a9197` |
| Original content-manifest SHA-256 | `5aed9828ef4b8069eea0eb53ccf04a58373208ad66fd8d0d191f3e6aedc3e2b4` |

The original per-path digest inventory remains in
[`placeholder/V1_SAMPLE_MANIFEST.sha256`](placeholder/V1_SAMPLE_MANIFEST.sha256).

## Read-only retrieval

Run these commands from a clean clone. Choose a fresh temporary directory; do not extract the sample
over the current archive checkout.

```bash
history_dir="$(mktemp -d /tmp/steamcloud-v1-history.XXXXXX)"
git archive --format=tar \
  --output="$history_dir/steamcloud-v1.tar" \
  069c2448ee3c5e7c352d096494d15e8f120cf433
sha256sum "$history_dir/steamcloud-v1.tar"
mkdir "$history_dir/source"
tar -xf "$history_dir/steamcloud-v1.tar" -C "$history_dir/source"
```

The SHA-256 output must equal the deterministic archive identity above. Treat any mismatch as
`INCOMPLETE` evidence and stop.

## Historical checks

The JavaScript sample declares Node 22 or newer and has no package dependency. The Rust sample uses
the toolchain and cached/downloaded crates selected by its historical workspace. These commands test
only the recovered sample:

```bash
npm test --prefix "$history_dir/source"
npm run check --prefix "$history_dir/source"
cargo test --manifest-path "$history_dir/source/Cargo.toml" --workspace --all-targets
```

On 2026-08-24, the two Node commands passed locally with 20 tests. The local coordinator host could
not complete the Rust command because its `cc` linker was absent; this retained limitation is not a
source failure and is not represented as a passing result. A future result must name its toolchain,
host, exact sample identity, and exit status.

Do not publish a package, deploy the sample, copy its schemas into an active repository, or infer that
its green tests qualify any current SteamCloud capability. Historical verification has no external
effect and selects no authority generation.
