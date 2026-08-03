# C049.1 Phase B4.1 — proof-carrying compression-round ledger

B4.1 hardens the **outer accounting discipline** of iterative compression before the complete Jeong–Kim–Oum branch-decomposition/full-set refinement engine is integrated.

For compression round `ell`, the previous certified order is extended by the new whole-factor block. The complete insertion manifest is deterministic and frozen before selection. Every candidate records:

```text
candidate position
whole-factor order
full cut-width vector
maximum width
accept/reject decision
layout digest
per-round cumulative work
global cumulative work
```

The independent verifier rebuilds every cut space, every candidate order, every bounded exhaustive prefix oracle, every cumulative counter and the selected state. Grouped factor blocks remain indivisible.

## Cumulative accounting

Failed candidates are retained. Work never resets between candidates or rounds:

```text
47 candidate refinements retained
130 cumulative work charged
```

An `OPEN_WORK_BUDGET` terminal stores the exact tested prefix of the frozen manifest. It cannot erase already charged failed refinements.

## Decisive insertion-only obstruction

Insertion into the previous linear order is not a complete iterative-compression engine.

For the registered arrangement

```text
d = 4
k = 1
blocks = [<e1>, <e2>, <e3>, <e4>, <e1+e2>, <e3+e4>]
```

the first five factors close with the selected order

```text
(0, 4, 2, 3, 1).
```

At the sixth round, none of the six insertion positions for the new block yields width at most `1`. Nevertheless, the independent exhaustive oracle finds exactly `72` width-`1` orders of the six whole factors.

Therefore:

```text
no successful insertion
DOES NOT IMPLY
NO_LAYOUT_AT_CAP.
```

The terminal remains `OPEN_TRAJECTORY_ENGINE_INCOMPLETE`. This obstruction rules out only the insertion-only shortcut. It does not obstruct the published branch-decomposition/full-set refinement algorithm.

## Hardened audit

```text
5 cases
2 LAYOUT_CANDIDATE
2 OPEN_TRAJECTORY_ENGINE_INCOMPLETE
1 OPEN_WORK_BUDGET
47 candidate refinements retained
130 cumulative work charged
3 digest-repaired tamper classes rejected
partition-loss control REJECTED
```

Producer-issued artifact:

```text
bytes  = 42,202
sha256 = a7bece691313b6aa5d0d5b134b490b69279567974184f5cbc14479c9a13eaf8d
semantic digest = 1ffb4f040b8676144b197f5c44219b79db993eba3a5e50f77c820a3f0affa9f5
```

The three repaired-digest tamper controls alter a candidate order, a cut-width vector, or a global cumulative-work counter. All are rejected semantically.

A verifier bug in round-state replay was found after the initial implementation: two one-line Python suites failed to advance `prev` and `last` on successful checks. The verifier was corrected; the producer and frozen artifact were unchanged. Exact-head CI then passed again.

## Strict boundary

B4.1 is not the complete iterative-compression constructor. It does not implement the `3k` branch-decomposition refinement, node full sets across the scaffold, deterministic reconstruction from that refinement, or complete `NO_LAYOUT_AT_CAP` replay.

```text
NEXT_GATE = C049.1_PHASE_B4_COMPLETE_BRANCH_DECOMPOSITION_REFINEMENT
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
