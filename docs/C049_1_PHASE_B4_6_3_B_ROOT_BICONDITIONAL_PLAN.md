# C049.1 B4.6.3-B — Root Full-Set Biconditional Plan

The B-gate must replace fixture-level terminal checks with a semantic induction.

For each scaffold node `t`, define a language `L_t(k)` of all width-at-most-`k` whole-factor partial layouts of the factors covered by `t`, represented at the exact boundary of `t`.

The required theorem is:

```text
Gamma is represented by FullSet(t)
iff
Gamma is induced by some member of L_t(k)
```

The proof must be split into independently replayable obligations:

1. **Leaf base case.** The canonical leaf generator and its `up_k` closure represent exactly the one-factor partial layouts at the leaf boundary.
2. **Expand completeness.** Every child language element transports to the common boundary, and no transported semantic state is omitted.
3. **Join completeness.** Every compatible interleaving is represented by an enumerated Delannoy lattice path.
4. **Shrink completeness.** Projection to the parent boundary preserves the exact represented partial layout semantics.
5. **Width filter soundness and reflection.** A failed refinement is infeasible at cap `k`; a feasible parent semantic state has at least one successful refinement.
6. **B2 preservation and reflection.** Duplicate deletion, extension-preorder minimization and `up_k` closure preserve the represented language, not merely the finite trajectory set.
7. **Root specialization.** At empty boundary, represented width-at-most-`k` trajectories correspond exactly to complete whole-factor layouts.

Only after obligations 1–7 are machine-bound may the engine execute:

```text
accepting root entry -> FOUND_LAYOUT
no accepting root entry + complete transcript -> NO_LAYOUT_AT_CAP
capacity or budget stop -> OPEN_*
```

The attack generator for this phase should enumerate bounded arrangements and compare every node full set with a direct semantic oracle, searching for the smallest counterexample to each local biconditional before the general proof is admitted.
