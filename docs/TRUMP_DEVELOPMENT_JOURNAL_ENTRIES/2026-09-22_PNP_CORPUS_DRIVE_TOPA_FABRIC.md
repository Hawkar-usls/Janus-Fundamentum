# 2026-09-22 — P=NP corpus / Drive / TOPA fabric binding

Status: **SYSTEM-INTEGRATION / NO SCIENTIFIC AUTHORITY DELTA**

This entry records the architecture that binds the user-owned Google Drive P=NP research pack to the JANUS research constellation while keeping `Janus-Fundamentum` as scientific authority.

## Dataflow

```text
Janus-Fundamentum authority
        ↓
Google Drive research pack / machine index
        ↓
TOPA PNP spider
  discovery + hard dedupe + sidecar attention weights
        ↓
janus/pnp-autoresearch-state
        ↓
Janus-Demiurge read-only PNP corpus memory
        ↓
native JANUS / research supervisor
        ↓
Terminal observability
```

TOPA may write normalized discovery material to the Drive `AUTO_INGEST` folder and weight state to `WEIGHT_STATE` only when private OAuth credentials are available through GitHub Actions secrets. No credential is stored in Git.

## Critical separation

Source documents are immutable. TOPA changes a sidecar attention ledger rather than rewriting papers, theorem receipts, or source notes.

Automatic weights are routing metadata only:

- `source_quality_hint`
- `frontier_relevance_weight`
- `novelty_weight`
- `attention_priority`

They are not truth scores, proof scores, or theorem promotion authority.

## Duplicate firewall

Hard merge is permitted only on stable publication/source identities: DOI, canonical arXiv id, normalized title + first author, normalized source URL, or exact content SHA-256. Near-semantic duplicates are flagged for review rather than auto-merged.

## Failure mode

If live Drive authentication is unavailable, runtime must use a pinned GitHub fallback/snapshot and explicitly mark Drive status degraded. It must not silently behave as if the Drive corpus was current.

## Scientific state

```text
P_VS_NP = OPEN
D1 = EMPTY
SUCCESSOR_ALGORITHM = LOCKED
CORPUS_BINDING = ACTIVE
SCIENTIFIC_AUTHORITY_DELTA = 0
```

Canonical machine contract:
`registry/JANUS_P_VS_NP_CORPUS_FABRIC_2026-09-22_v1.0.json`


## Implementation receipts

Drive service surfaces:

```text
ROOT
= 1afNpNkT1KcTZie1SJQz6drmIg5kEfVMZ

MATERIALS_INDEX
= 1lL5lftT64eojjeNcd0RqvS9XpCFyaqE9

AUTO_INGEST
= 1JPo-GtCtIO6yMDIsOvB9RTCDdZMNFDAk

WEIGHT_STATE
= 1IwRcwQ9VCvku8P4AKJd2TkKiG1CU4b2F
```

Runtime draft lineages:

```text
TOPA
PR #56
validated head ed038fce31805009f80277a5fda137f36bc0c4cd
TOPA PNP Corpus Fabric CI = PASS (run 35678519212)
JANUS Secret Persistence Guard = PASS (run 35678519198)

Janus-Demiurge
PR #196
validated head 64fd6acaab5f32788a1fbbcc350390eb01f55a23
JANUS PNP Corpus Memory CI = PASS
JANUS Self-Evolution v2 CI = PASS
JANUS Secret Persistence Guard = PASS

Terminal
PR #31
validated head 01a1a4df4c9d2f47f4661bb1c32f080032403d6a
Terminal PNP Corpus Fabric CI = PASS

janus-meta-registry
PR #250
validated head 481aa92462e0fd4d6075f47e15aba500955a23c7
JANUS Secret Persistence Guard = PASS
JANUS autonomous site curator = PASS
```

Fundamentum itself additionally pins the exact Drive JSON snapshot:

`registry/P_VS_NP_MATERIALS_INDEX_DRIVE_SNAPSHOT_2026-09-22_v1.0.json`

with a read-only snapshot receipt. Registry validation passes after the binding.

## Current activation boundary

Code, fallbacks, dedupe, weight ledger, native corpus adapter, Terminal observability, and constellation mirror are implemented.

Live GitHub Actions access to the private Google Drive is deliberately **not** bootstrapped from ChatGPT's connected Drive authorization. Those credentials are private to that environment and are not exportable to GitHub.

Until a separate TOPA GitHub OAuth authorization is configured:

```text
LIVE_DRIVE_FROM_GITHUB
= NOT_CONFIGURED

PINNED_GITHUB_FALLBACK
= ACTIVE

TOPA_OPEN_SOURCE_DISCOVERY
= CODE_READY

DRIVE_AUTO_PUBLISH
= SKIPPED_AUTH_NOT_CONFIGURED

SCIENTIFIC_AUTHORITY_DELTA
= 0
```

This degraded operational state is not scientific evidence and cannot affect P vs NP status.


## Driveless Meta Registry fallback

The corpus fabric no longer depends on Google Drive availability for continued operation.

A self-contained JSON mirror is now bound in:

`Hawkar-usls/janus-meta-registry@integration/pnp-corpus-fabric-v1`

under:

`registry/p_vs_np/corpus/`

with these machine-readable layers:

```text
P_VS_NP_CORPUS_MANIFEST_2026-09-22_v1.0.json
P_VS_NP_MATERIALS_INDEX_META_FALLBACK.json
P_VS_NP_AUTHORITY_AND_FRONTIER_2026-09-22_v1.0.json
P_VS_NP_ANTI_LOOP_MAP_2026-09-22_v1.0.json
P_VS_NP_INTERNAL_CONTROLS_2026-09-22_v1.0.json
P_VS_NP_OPEN_ACCESS_LIBRARY_2026-09-22_v1.0.json
P_VS_NP_AUTOMATION_CONTRACTS_2026-09-22_v1.0.json
P_VS_NP_DRIVE_MIRROR_MAP_2026-09-22_v1.0.json
```

TOPA workflow fallback order is now:

```text
1. LIVE_PRIVATE_GOOGLE_DRIVE
2. JANUS_META_REGISTRY_JSON_CORPUS
3. TOPA_LOCAL_PINNED_FALLBACK
```

Therefore missing Google Drive authorization does not block P=NP research continuity. Drive remains the live mutable external-memory layer, Meta Registry is the cross-repository JSON corpus mirror, and TOPA keeps the final local fail-closed snapshot.

```text
P_VS_NP = OPEN
D1 = EMPTY
SUCCESSOR_ALGORITHM = LOCKED
DRIVE_REQUIRED_FOR_CONTINUITY = FALSE
SCIENTIFIC_AUTHORITY_DELTA = 0
```
