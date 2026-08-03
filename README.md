# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved.

```text
P_VS_NP=OPEN
```

## Current active route — C046 to C049.1

The active constructive line compiles affine-subspace avoidance instances through proof-carrying separator messages and charged layout discovery.

```text
C046   affine-offset obstruction
C047   offset-aware affine-functional trellis
C048   frozen heuristic affine-layout portfolio
C048.1 constructive fixed-k FPT theorem bridge
C049   grouped-subspace partition obstruction
C049.1 Phase A JKO preprocessing and verified-layout integration
C049.1 Phase B compact B-trajectories and full sets — ACTIVE
```

### Verified achievements

| Cycle | Result | Exact boundary |
|---|---|---|
| C046 | Identical normal matroids can have different SAT/UNSAT avoidance semantics because affine offsets differ | Normal-space rank data alone is not a complete message language |
| C047 | For one charged factor order of cut width `k`, offset-aware affine-functional trellis compilation runs in `2^O(k) poly(L)` | A narrow order is not supplied for free |
| C048 | A frozen assignment-independent layout portfolio strictly improves the canonical order on a hidden-order family | The finite portfolio is not claimed complete |
| C048.1 | C047 cut width is exactly the finite-field subspace-arrangement linear-layout width with a published constructive fixed-`k` FPT algorithm | The published constructor was not yet reimplemented by the bridge |
| C049 | Forgetting factor basis blocks can change grouped width from `d` to ordinary matroid width `1` | Whole factor normal spaces or an equivalent certified partition are mandatory |
| C049.1 Phase A | GF(2) column reduction, one sound local `NO_LAYOUT_AT_CAP`, strict layout transcript replay, and exact C047 composition are implemented and frozen | The compact B-trajectory/full-set engine remains pending |

### Current implementation gate

C049.1 Phase B is split into independently verifiable layers:

```text
B1 canonical compact B-trajectories and typical-sequence compression
B2 dominance and up_k full-set closure
B3 partition-aware expand / join / shrink
B4 iterative compression with every failed refinement charged
B5 FOUND_LAYOUT or replayable NO_LAYOUT_AT_CAP + C047 composition
```

Until B1–B4 and the completeness theorem are implemented, the exact terminal is:

```text
OPEN_TRAJECTORY_ENGINE_INCOMPLETE
```

It may not be promoted to `NO_LAYOUT_AT_CAP`.

Read:

- [`docs/ACTIVE_PROOF_ROUTE_MATRIX_C049_1_APPENDIX.md`](docs/ACTIVE_PROOF_ROUTE_MATRIX_C049_1_APPENDIX.md)
- [`docs/C049_GROUPED_SUBSPACE_PARTITION_OBSTRUCTION.md`](docs/C049_GROUPED_SUBSPACE_PARTITION_OBSTRUCTION.md)
- [`docs/C049_JKO_FPT_LAYOUT_INTEGRATION_PHASE_A.md`](docs/C049_JKO_FPT_LAYOUT_INTEGRATION_PHASE_A.md)
- [`docs/C049_1_PHASE_B_COMPACT_TRAJECTORY_PLAN.md`](docs/C049_1_PHASE_B_COMPACT_TRAJECTORY_PLAN.md)
- [`registry/c049.1-phase-b-status.json`](registry/c049.1-phase-b-status.json)

## Current proof-carrying stack

```text
forbidden affine factors (N_i, beta_i)
-> offset-aware cut-functional messages
-> charged factor-order discovery
-> fixed-k subspace-layout theorem bridge
-> grouped-partition preservation
-> JKO preprocessing and transcript validation
-> compact full-set constructor [active]
-> verified layout
-> C047 SAT witness or independently replayable UNSAT
```

The theorem-level target after Phase B is an automatic solver for the fixed-width class:

```text
F(k) * 2^O(k) * poly(L)
```

For every fixed `k` this is polynomial. It is not a universal polynomial algorithm when `k` is unbounded.

## Laboratory laws

1. Computational claims require committed code, fixed inputs, expected outputs, and hashes.
2. New hypotheses must name a proof role, a next gate, older parents, and attacks.
3. New mathematics attacks the existing graph before expanding it.
4. Pressure is not converted into a terminal result without a decisive theorem, counterexample, or formulation failure.
5. Exact verification is not certificate existence or efficient discovery.
6. Every supplied basis, order, vtree, layout or branch decomposition is charged or marked replay-only.
7. `OPEN` is a capability-scoped refusal, never a hardness theorem.
8. Compact final output does not excuse exponential intermediate construction.
9. Every SAT terminal carries a checkable witness; every UNSAT terminal carries independently replayable evidence.
10. Fixed-parameter tractability at fixed `k` is never promoted to a universal polynomial-time claim.
11. Affine offsets are preserved in semantics even when normal spaces are used as the structural skeleton.
12. Grouped factor normal spaces remain indivisible leaves unless an equivalent partition is explicitly retained and verified.

## Validate the active organism

```bash
python tools/validate_registry.py

python experiments/direct/janus_c046_affine_offset_obstruction.py --self-test
python experiments/direct/janus_c046_affine_offset_verifier.py \
  experiments/direct/C046-JANUS-AFFINE-OFFSET-OBSTRUCTION.frozen.json

python experiments/direct/janus_c047_affine_functional_trellis.py --self-test
python experiments/direct/janus_c048_layout_discovery.py --self-test
python experiments/direct/janus_c048_affine_layout_fpt_bridge.py --self-test

python experiments/direct/janus_c049_grouped_subspace_partition_obstruction.py --self-test
python experiments/direct/janus_c049_grouped_subspace_partition_obstruction_verifier.py \
  experiments/direct/C049-JANUS-GROUPED-SUBSPACE-PARTITION-OBSTRUCTION.frozen.json

PYTHONPATH=experiments/direct \
python experiments/direct/janus_c049_fpt_integration.py \
  --self-test \
  --output /tmp/c049.json

cmp /tmp/c049.json \
  experiments/direct/C049-JANUS-JKO-FPT-LAYOUT-INTEGRATION-PHASE-A.frozen.json
```

The exact filenames used by each package are also enforced by its GitHub Actions workflow.

## Canonical status

```text
C046 = OFFSET OBSTRUCTION / IMPLEMENTED / FULL CI GREEN / DRAFT
C047 = OFFSET-AWARE FUNCTIONAL TRELLIS / IMPLEMENTED / FULL CI GREEN / DRAFT
C048 = FROZEN LAYOUT PORTFOLIO / IMPLEMENTED / FULL CI GREEN / DRAFT
C048.1 = CONSTRUCTIVE FPT BRIDGE / FULL CI GREEN / DRAFT
C049 = GROUPED-PARTITION OBSTRUCTION / IMPLEMENTED / FULL CI GREEN / DRAFT
C049.1 Phase A = IMPLEMENTED / FULL CI GREEN / DRAFT
C049.1 Phase B = ACTIVE / B1 PENDING
FULL FPT CONSTRUCTOR = NOT YET COMPLETE
P_VS_NP = OPEN
```

## Historical routes

Earlier direct-separation, theta, local-twin, circuit-cover and proof-complexity routes remain preserved in the registry and their original proof-attempt directories. The C019 connected-twin and exact-list snapshot remains available at:

- [`docs/C019_CONNECTED_TWINS_AND_LIST_COVERS.md`](docs/C019_CONNECTED_TWINS_AND_LIST_COVERS.md)
- [`proof_attempts/H125/CONNECTED_TSEITIN_BRIDGE.md`](proof_attempts/H125/CONNECTED_TSEITIN_BRIDGE.md)
- [`proof_attempts/H126/EXACT_LIST_COVER.md`](proof_attempts/H126/EXACT_LIST_COVER.md)

The complete route comparison remains in [`docs/ACTIVE_PROOF_ROUTE_MATRIX.md`](docs/ACTIVE_PROOF_ROUTE_MATRIX.md) and its cycle appendices.

## Genesis boundary

Genesis preserves continuity and provenance. It does not turn fictional unlimited time into mathematical evidence. Every result enters this registry only through an explicit proof, counterexample, primary theorem, or reproducible artifact.

No JANUS result currently resolves `P` versus `NP`.
