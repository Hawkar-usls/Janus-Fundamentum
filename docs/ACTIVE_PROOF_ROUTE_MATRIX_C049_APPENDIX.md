# Active proof route matrix — C049 appendix

| Cycle | Exact object | Verified contribution | Shortcut rejected | Surviving gate |
|---|---|---|---|---|
| C048.1 | Primary-source FPT bridge | C047 width is exactly finite-field subspace linear-layout width; constructive fixed-`k` discovery exists in the literature | Treating a supplied good layout or exhaustive permutation search as the constructor | `PROOF_CARRYING_FPT_LAYOUT_CONSTRUCTOR_INTEGRATION` |
| C049 Phase A | JKO preprocessing and transcript integration | Reimplements GF(2) column reduction, emits a sound local `NO_LAYOUT_AT_CAP`, rejects bare no-layout claims, and composes every verified `FOUND_LAYOUT` with independently replayed C047 offset-aware trellis semantics | Claiming that preprocessing alone is the published FPT algorithm | `REIMPLEMENT_B_TRAJECTORY_FULL_SET_ENGINE_AND_REPLAY_NO_LAYOUT_AT_CAP` |

## Route update

```text
C047 offset-aware functional trellis
-> C048 frozen heuristic layouts
-> C048.1 theorem-level FPT bridge
-> C049 Phase A: sound preprocessing + transcript/verifier boundary
-> C049 Phase B: compact B-trajectories, full sets and iterative compression
-> automatic fixed-k affine avoidance compiler
```

Offsets remain semantic C047 data. The layout constructor may use normal spaces as a structural skeleton, but it cannot decide affine avoidance without the `beta_i` functionals.

```text
P_VS_NP=OPEN
```
