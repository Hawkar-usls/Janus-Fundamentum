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
