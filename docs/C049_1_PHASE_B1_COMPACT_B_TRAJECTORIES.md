# C049.1 Phase B1 — compact B-trajectories

This stacked draft implements only the compactification normal form `tau` from Jeong–Kim–Oum, arXiv:1507.02184v4, Section 3.1.

A statistic is `(L,R,lambda)` with `L,R <= B`. A valid B-trajectory has increasing `L`, decreasing `R`, and `R(first)=L(last)`. Compactification repeatedly removes consecutive duplicate statistics and removes the interior of a constant-`(L,R)` interval when all intermediate lambda values lie between its endpoint values.

The executable records every removal. The independent verifier does not import the producer and regenerates 120 deterministic GF(2) coordinate-subspace trajectories. It checks deterministic normal form, idempotence, width preservation and the published bound

```text
length(tau(Gamma)) <= (2 dim(B)+1)(2k+1).
```

This closes a constructive sublemma only. It does not implement the extension preorder, domination, `up_k`, full sets, join, shrink, expand, iterative compression, `FOUND_LAYOUT`, or complete `NO_LAYOUT_AT_CAP`.

```text
NEXT_GATE = C049.1_PHASE_B2_EXTENSION_PREORDER_AND_UP_K
P_VS_NP = OPEN
```
