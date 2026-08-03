# C049.1 Phase B4.1 — proof-carrying compression-round ledger

This independently verifiable sublemma hardens the outer iterative-compression accounting before the complete branch-decomposition refinement engine is integrated.

For round `ell`, the previous certified order is extended by the new whole-factor block. The insertion manifest is canonical and frozen before selection. Every candidate records its full cut-width vector, decision, digest, per-round cumulative work, and global cumulative work.

The audit proves that failed candidates are retained, work never resets between candidates or rounds, selection is deterministic, selected bounded fixtures belong to an independently enumerated width-`k` oracle, and grouped factor blocks remain indivisible.

A decisive boundary also appears: insertion into the previous linear order is not complete. When insertion fails while the exhaustive oracle still contains a width-`k` order, the terminal remains `OPEN_TRAJECTORY_ENGINE_INCOMPLETE`; it is never promoted to `NO_LAYOUT_AT_CAP`. The next layer must implement the published branch-decomposition/full-set refinement.

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

This is B4.1, not complete iterative compression.

```text
NEXT_GATE = C049.1_PHASE_B4_COMPLETE_BRANCH_DECOMPOSITION_REFINEMENT
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
