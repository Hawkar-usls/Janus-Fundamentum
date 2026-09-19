# U-PAIR-1J Post-Mixed Prior-Art Decision — 2026-09-19

**Authority:** READ_ONLY_DECISION_NOTE__NO_FROZEN_VERDICT_MUTATION  
**Prior-art audit parent:** `ad7fbd302ff3de7e0f05ce583ec3e2003dbc0921`  
**Completed mixed reconciliation:** `89d2a2de8573dc4410af2fbd2de513103af7931e`

## Verified completed result

The frozen mixed lineage is accepted exactly as recorded:

- prereg: `6097218416d0a8a244cf526d01ba8a00fc0ba1fa`
- source freeze: `19e385405c3eaa8736553edcd5f3e6e2b139d899`
- independent source check: `80645e7ddae908f4f547569663d856bbe520fe9f`
- killer control: `9d794acc97c127bada6c4f092293c3256ea08472`
- implementation review: `5f3d63734db163efee04e55e3387cd94c88c9c4c`
- one blind run: `384e145f8968382dcf1b1283577bc8f0b68a5aca`
- reconciliation: `89d2a2de8573dc4410af2fbd2de513103af7931e`

Verdict remains:
`PASS_SCOPED_MIXED_GUARD_HOSTILE_SYNTHESIS`.

## What this run genuinely established for V1.1

The high-value part is the mandatory killer control:

[
O=P\lor Q\lor R
]
[
\neg O=ITE(O,0,1)
]
[
G=A\oplus O=ITE(A,\neg O,O)
]

was accepted using only frozen `CONST`, `AFFINE_XOR`, and `GUARDED_ITE`, with no new nonlinear-XOR rule and no illicit guard typing.

Therefore the frozen V1.1 implementation demonstrated that a verified nonlinear DAG root can participate in further local proof composition under the frozen rule semantics.

The five-size hostile series additionally verified the implementation/accounting and independent-domain-proof plumbing across the frozen source family.

## What it should NOT be interpreted as

The series should not be interpreted as discovering that the family has polynomial-size proofs: the preexecution review already froze the constructor-specific bounds

[
S_{guards}\le 5n+2,
]
[
S_{selector,exclusive}\le(n-1)\log_2n,
]

so the source design itself had an explicit polynomial architecture.

This is therefore a valid scoped implementation/proof-calculus result, but not evidence for a new general tractability class.

## Prior-art consequence

Do not automatically continue to `PAIR_SELECTOR_HITTING_3_RANDOM_MIXED_CONTROLS`.

A new synthetic heterogeneous family is scientifically justified only if a pre-run audit shows that it answers a question not already covered by:
- standard Boolean functional synthesis semantics;
- factored/local synthesis;
- SynNNF/SAUNF tractable representations;
- proof-based QBF Skolem extraction / SynQBF;
- existing public BFS benchmark suites and synthesis engines;
- an immediate explicit polynomial circuit/proof construction.

## Higher-value next target

Prefer a **published discriminating family with a known separation**.

Primary candidate:
**Juba & Meel, AAAI 2026 — pigeonhole-based functional-synthesis family**, where small Skolem functions exist but resolution-based interpolation is forced to generate exponential-size circuits.

Janus question:
> Can frozen V1.1 synthesize/certify a compact proof-carrying witness on a family for which a published synthesis route has a proved exponential bottleneck?

This is substantially more informative than another random synthetic mixed family.

## External baseline lane

Before broad practical-synthesis claims, compare selected Janus inputs/results against:
- BFSS;
- Manthan/Manthan2;
- c2syn/cnf2syn;
- BooleanFunctionalSynthesis public benchmarks (Arithmetic, Disjunctive Decomposition, Factorization, QBFEval 2017/2018).

These are baselines only; they do not become Janus scientific authority.

## Theory-comparison lane

Before broad proof-system claims, compare V1.1 with SAT 2026 SynQBF:
- translation of selected SynQBF proof fragments to V1.1;
- translation of V1.1 `AFFINE_XOR + GUARDED_ITE + domain certificate` proofs to SynQBF;
- polynomial-overhead questions, not generic rediscovery of proof-carrying Skolem extraction.

## Scientific firewall

`GENERAL_SAT_IN_P = NOT_PROVED`  
`P_EQ_NP = NOT_PROVED`  
`P_VS_NP = OPEN`

No frozen verdict is altered by this decision note.
