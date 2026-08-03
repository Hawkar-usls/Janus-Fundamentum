# Active proof route matrix — C049.1 appendix

| Cycle | Exact object | Verified contribution | Shortcut rejected | Surviving gate |
|---|---|---|---|---|
| C049 | Grouped-subspace partition obstruction | Basis expansion cannot discard factor blocks: grouped width may be `d` while the unpartitioned ordinary matroid has width `1` | Substituting an ordinary represented-matroid constructor after forgetting the subspace partition | `PARTITION_AWARE_PROOF_CARRYING_FPT_CONSTRUCTOR_INTEGRATION` |
| C049.1 Phase A | JKO preprocessing and transcript integration | Reimplements GF(2) column reduction, emits the sound local Proposition-2.2 obstruction, binds verified layouts, and preserves every C047 offset | Claiming preprocessing or a supplied layout is the FPT constructor | `REIMPLEMENT_B_TRAJECTORY_FULL_SET_ENGINE` |
| C049.1 Phase B1 | Compact B-trajectory normal form | Canonical compactification, removal transcript, idempotence, width preservation, and published length bound | Comparing unreduced trajectory encodings as distinct semantic states | `EXTENSION_PREORDER_AND_UP_K` |
| C049.1 Phase B2 | Extension preorder and `up_k` | Exact lattice-path witnesses, preorder-minimal generators with direct deletion receipts, complete admitted `U_k(B)` enumeration, and exact closure | Deleting a trajectory without a retained predecessor; treating an incomplete state search as `NO_LAYOUT_AT_CAP` | `PARTITION_AWARE_EXPAND_JOIN_SHRINK` |

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
-> C049.1 B4: iterative compression
-> C049.1 B5: FOUND_LAYOUT or replayable NO_LAYOUT_AT_CAP + C047
```

B2 proves that generator deletion preserves the complete upward closure: every removed generator has a retained predecessor under the published preorder, and transitivity transports every later coverage witness. This is necessary for a future honest empty-full-set replay, but it is not yet sufficient for `NO_LAYOUT_AT_CAP`; B3 and B4 remain absent.

```text
C049.1 Phase A  = IMPLEMENTED / FULL_CI_GREEN
C049.1 Phase B1 = IMPLEMENTED / FULL_CI_GREEN
C049.1 Phase B2 = IMPLEMENTED / LOCAL_AUDIT_GREEN / CI_PENDING
C049.1 Phase B3 = NEXT_GATE
FULL FPT CONSTRUCTOR = NOT_YET_COMPLETE
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
