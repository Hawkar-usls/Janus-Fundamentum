# Active proof route matrix — C049.1 appendix

| Cycle | Exact object | Verified contribution | Shortcut rejected | Surviving gate |
|---|---|---|---|---|
| C049 | Grouped-subspace partition obstruction | Basis expansion cannot discard factor blocks: grouped width may be `d` while the unpartitioned ordinary matroid has width `1` | Substituting an ordinary represented-matroid constructor after forgetting the subspace partition | `PARTITION_AWARE_PROOF_CARRYING_FPT_CONSTRUCTOR_INTEGRATION` |
| C049.1 Phase A | JKO preprocessing and transcript integration | Reimplements GF(2) column reduction, emits the sound local Proposition-2.2 obstruction, binds verified layouts, and preserves every C047 offset | Claiming preprocessing or a supplied layout is the FPT constructor | `REIMPLEMENT_B_TRAJECTORY_FULL_SET_ENGINE` |
| C049.1 Phase B1 | Compact B-trajectory normal form | Canonical compactification, complete removal transcript, idempotence, width preservation, and the published length bound | Digest-only or noncanonical trajectory acceptance | `EXTENSION_PREORDER_AND_UP_K` |
| C049.1 Phase B2 | Extension preorder and `up_k` | Exact lattice-path witnesses, preorder-minimal generators with direct deletion receipts, complete admitted `U_k(B)` enumeration, and full producer-transcript replay | Deleting a trajectory without a retained predecessor; treating incomplete closure as `NO_LAYOUT_AT_CAP` | `PARTITION_AWARE_EXPAND_JOIN_SHRINK` |
| C049.1 Phase B3 | Partition-aware expand / join / shrink | Replays boundary transports, every lattice path, pre-compact joined sequences, exact join/projection corrections, B1 compactification, bounded exact `up_k`, and grouped-block preservation | Hiding a large join behind a small compact result; discarding factor blocks during composition | `ITERATIVE_COMPRESSION_WITH_FAILED_REFINEMENTS_CHARGED` |
| C049.1 Phase B4.1 | Compression-round ledger | Freezes every insertion candidate, retains all failed refinements, carries per-round and global cumulative work, verifies selected layouts against exhaustive bounded prefix oracles, and preserves grouped blocks | Keeping only the successful refinement; resetting accounting between rounds; treating insertion failure as no-layout | `COMPLETE_3K_BRANCH_DECOMPOSITION_FULL_SET_REFINEMENT` |

## Current route

```text
C046 affine offsets are semantically mandatory
-> C047 offset-aware functional trellis for one order
-> C048 frozen heuristic layout discovery
-> C048.1 theorem-level fixed-k FPT bridge
-> C049 grouped-subspace partition obstruction
-> C049.1 Phase A: column reduction + transcript boundary
-> C049.1 B1: compact B-trajectories
-> C049.1 B2: extension preorder + domination receipts + up_k
-> C049.1 B3: partition-aware expand/join/shrink
-> C049.1 B4.1: cumulative compression-round ledger
-> C049.1 B4.2: complete 3k branch-decomposition/full-set refinement
-> C049.1 B5: FOUND_LAYOUT or replayable NO_LAYOUT_AT_CAP + C047
```

## B4.1 boundary

B4.1 records `47` candidate refinements and charges `130` units of cumulative work without resetting the ledger between failed candidates or rounds.

It also proves that insertion-only compression is incomplete. For the six grouped one-dimensional blocks

```text
<e1>, <e2>, <e3>, <e4>, <e1+e2>, <e3+e4>
```

at `k=1`, the selected five-factor order admits no successful insertion of the sixth factor, while the independent exhaustive oracle contains exactly `72` width-`1` orders. Therefore insertion failure remains `OPEN_TRAJECTORY_ENGINE_INCOMPLETE`; it cannot become `NO_LAYOUT_AT_CAP`.

The surviving obligation is the published branch-decomposition/full-set refinement across each compression round. B4.1 is the accounting shell and a decisive shortcut obstruction, not the complete FPT constructor.

```text
C049.1 Phase A   = IMPLEMENTED / FULL_CI_GREEN
C049.1 Phase B1  = IMPLEMENTED / HARDENED / FULL_CI_GREEN
C049.1 Phase B2  = IMPLEMENTED / HARDENED / FULL_TRANSCRIPT_REPLAY / FULL_CI_GREEN
C049.1 Phase B3  = IMPLEMENTED / HARDENED / FULL_TRANSCRIPT_REPLAY / FULL_CI_GREEN / DRAFT
C049.1 Phase B4.1 = IMPLEMENTED / HARDENED / FULL_TRANSCRIPT_REPLAY / FULL_CI_GREEN
C049.1 Phase B4.2 = ACTIVE
FULL FPT CONSTRUCTOR = NOT_YET_COMPLETE
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
