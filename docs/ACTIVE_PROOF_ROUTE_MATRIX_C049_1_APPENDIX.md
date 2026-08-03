# Active proof route matrix — C049.1 appendix

| Cycle | Exact object | Verified contribution | Shortcut rejected | Surviving gate |
|---|---|---|---|---|
| C049 | Grouped-subspace partition obstruction | Basis expansion cannot discard factor blocks: grouped width may be `d` while the unpartitioned ordinary matroid has width `1` | Substituting an ordinary represented-matroid constructor after forgetting the subspace partition | `PARTITION_AWARE_PROOF_CARRYING_FPT_CONSTRUCTOR_INTEGRATION` |
| C049.1 Phase A | JKO preprocessing and transcript integration | Reimplements GF(2) column reduction, emits a sound local `NO_LAYOUT_AT_CAP`, rejects bare no-layout claims, and composes every verified `FOUND_LAYOUT` with independently replayed C047 offset-aware trellis semantics | Claiming that preprocessing alone is the published FPT algorithm | `REIMPLEMENT_B_TRAJECTORY_FULL_SET_ENGINE_AND_REPLAY_NO_LAYOUT_AT_CAP` |

## Route update

```text
C047 offset-aware functional trellis
-> C048 frozen heuristic layouts
-> C048.1 theorem-level FPT bridge
-> C049 grouped-subspace partition obstruction
-> C049.1 Phase A: sound preprocessing + transcript/verifier boundary
-> C049.1 Phase B: compact B-trajectories, full sets and iterative compression
-> automatic fixed-k affine avoidance compiler
```

The constructor must retain whole normal spaces as leaves or an equivalent certified basis-block partition. Offsets remain semantic C047 data.

```text
P_VS_NP=OPEN
```
