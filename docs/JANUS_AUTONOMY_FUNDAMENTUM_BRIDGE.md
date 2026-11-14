# JANUS autonomy → Fundamentum proof-spine bridge (v1, draft)

This is a **scoped offline consistency/falsification gate**, not a new production coordinator.
Canonical organism: [JANUS_ORGANISM_v1](https://github.com/Hawkar-usls/Janus/blob/main/organism/JANUS_ORGANISM_v1.json), member \`proof_spine\`.
Existing \`.janus/JANUS_ORGANISM_LINK.json\`, \`.janus/NEXUS_LINK.json\` and the Beetle inbox remain authoritative about capabilities and limitations.

## Why

The 2026-10-28 ecosystem audit found a difference between successful individual workflow runs and *confirmed, correctly consumed* outcomes. Candidate gaps include Beetle → Genesis pending ACKs, Rowan → Meta Registry pointer lag, unproven real HRAiN/iNaiHR recovery, Habitat worker handoff and GOLEM's live-provider gate. Audit counts are a dated observation, **not** verified by this PR.

The proof spine can test **claims about invariants** but does not itself deliver packets, obtain Rowan credits, repair out-of-date pointers, perform handoffs or operate an external model.

## Contract and entry point

- Machine-readable expected routes: [\`registry/JANUS_AUTONOMY_CONSISTENCY_CONTRACT_v1.json\`](../registry/JANUS_AUTONOMY_CONSISTENCY_CONTRACT_v1.json)
- Offline checker: [\`tools/autonomy_consistency_gate.py\`](../tools/autonomy_consistency_gate.py)
- Membership bridge: [\`.janus/AUTONOMY_PROOF_LINK.json\`](../.janus/AUTONOMY_PROOF_LINK.json)
- CI runs **synthetic adversarial tests only**. No public live receipts are assumed.

\`\`\`sh
python tools/autonomy_consistency_gate.py --self-test
python tools/autonomy_consistency_gate.py --evidence /path/to/explicit-exported-snapshot.json
\`\`\`

The second command defaults to **BLOCKED** when any required route is absent, a declared receipt is missing, a digest is stale, or a replay claims two applications / the same worker. It does not retrieve receipt URLs or authenticate external observations. \`DECLARED_CONSISTENCY_PASS_EXTERNAL_VERIFICATION_REQUIRED\` means only that *supplied statements agree internally*.

## Required external work before any live status

1. Each source exports a versioned, non-sensitive checkpoint / delivery receipt at an immutable reference, with actual source and receiving commits. Private SkinGPT identifiers and Rowan data must stay in their authorized storage.
2. Independent witness fetches and verifies provenance and receipt content; source and consumer acknowledgements must be independently attributable.
3. Meta Registry publishes an auditable, content-addressed snapshot **without rewriting upstream evidence**; source head and registry pointer must be compared using the same declared identity.
4. Genesis performs the worker-A → worker-B handoff with exact SHA, lease fencing, idempotency and recovery on real state. HRAiN and iNaiHR also replay real checkpoint state.
5. GOLEM external-provider availability and expense policy are proven separately. No automatic credit spend or provider enablement.
6. Only after live independent verification may Guardian / gateway consider scoped operational status. No automatic scientific or access-rights promotion.

## Scientific firewall

A successful local or synthetic check cannot establish E2E autonomy, exact-once distributed execution, external model activity, Rowan calibration, any theorem about algorithms, or a solution to \`P=NP\`. **P versus NP remains OPEN.**

All cross-repository writes, autonomous repair and external effects remain disabled here. The formal lab, live supervisor, Meta Registry authority and Genesis runtime stay separate.
