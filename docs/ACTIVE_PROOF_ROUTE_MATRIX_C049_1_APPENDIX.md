# Active proof route matrix — C049.1 appendix

| Cycle | Exact object | Verified contribution | Shortcut rejected | Surviving gate |
|---|---|---|---|---|
| C046 | Affine-offset obstruction | Identical ordered normal spaces and complete rank data can have different SAT/UNSAT avoidance semantics | Treating normal-matroid data as a complete separator language | `OFFSET_AWARE_AFFINE_FUNCTIONAL_MESSAGES` |
| C047 | Offset-aware affine-functional trellis | Exact `2^O(k) poly(L)` compilation for one charged factor order; states are functionals on cut-normal spaces and every factor retains `beta_i` | Rank-only, bitset-only or offset-free cut messages | `PROOF_CARRYING_LAYOUT_DISCOVERY` |
| C048 | Frozen affine-layout portfolio | Assignment-independent candidate orders strictly improve C047 on a hidden-order family; all candidates are frozen before probes | Treating one canonical factor order as without loss of generality | `FIXED_WIDTH_LAYOUT_CONSTRUCTOR` |
| C048.1 | Primary-source FPT bridge | C047 cut width is exactly finite-field subspace-arrangement linear-layout width; constructive fixed-`k` discovery exists in Jeong–Kim–Oum | Treating exhaustive permutation checks or a supplied layout as the published constructor | `PROOF_CARRYING_FPT_LAYOUT_CONSTRUCTOR_INTEGRATION` |
| C049 | Grouped-subspace partition obstruction | Basis expansion cannot discard factor blocks: grouped width may be `d` while the unpartitioned ordinary matroid has width `1` | Substituting an ordinary represented-matroid constructor after forgetting the subspace partition | `PARTITION_AWARE_PROOF_CARRYING_FPT_CONSTRUCTOR_INTEGRATION` |
| C049.1 Phase A | JKO preprocessing and transcript integration | Reimplements GF(2) column reduction, emits a sound local `NO_LAYOUT_AT_CAP`, rejects bare no-layout claims, and composes every verified `FOUND_LAYOUT` with independently replayed C047 semantics | Claiming that preprocessing alone is the published FPT algorithm | `REIMPLEMENT_B_TRAJECTORY_FULL_SET_ENGINE_AND_REPLAY_NO_LAYOUT_AT_CAP` |
| C049.1 Phase B | Compact B-trajectories and full sets | Active implementation plan is fixed to corrected arXiv v4; B1–B5 separately expose canonical compactification, `up_k`, partition-aware joins, iterative compression and terminal replay | Implementing one opaque constructor, hiding failed refinements, or converting incomplete search into `NO_LAYOUT_AT_CAP` | `B1_CANONICAL_COMPACT_TRAJECTORY_NORMAL_FORM` |

## Current route

```text
C046 affine offsets are semantically mandatory
-> C047 offset-aware functional trellis for one order
-> C048 frozen heuristic layout discovery
-> C048.1 theorem-level fixed-k FPT bridge
-> C049 grouped-subspace partition obstruction
-> C049.1 Phase A: sound preprocessing + transcript/verifier boundary
-> C049.1 Phase B:
     B1 compact trajectories
     B2 dominance and up_k
     B3 expand/join/shrink
     B4 iterative compression
     B5 FOUND_LAYOUT or replayable NO_LAYOUT_AT_CAP + C047
-> automatic fixed-k affine avoidance compiler
```

## Phase-B proof obligations

The constructor must retain whole normal spaces as leaves or an equivalent certified basis-block partition. Offsets remain semantic C047 data.

Soundness is not enough. The completed full-set engine must prove both:

```text
every retained trajectory is realizable
and
every layout of width at most k is represented by a retained trajectory
```

Until both directions and B1–B4 are implemented, the exact terminal is:

```text
OPEN_TRAJECTORY_ENGINE_INCOMPLETE
```

It may not be promoted to `NO_LAYOUT_AT_CAP`.

Detailed plan:

```text
docs/C049_1_PHASE_B_COMPACT_TRAJECTORY_PLAN.md
registry/c049.1-phase-b-status.json
```

```text
C049.1 Phase A = IMPLEMENTED / FULL_CI_GREEN
C049.1 Phase B = ACTIVE / B1_PENDING
FULL FPT CONSTRUCTOR = NOT_YET_COMPLETE
P_VS_NP=OPEN
```
