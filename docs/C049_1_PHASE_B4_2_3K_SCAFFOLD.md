# C049.1 Phase B4.2 — charged 3k scaffold lemma

Given a width-at-most-k layout of the previous grouped factors and a new reduced whole-factor block of dimension at most 2k, append the new block as the final leaf of the old layout caterpillar. For every old cut, adding the new block to one side can increase the boundary dimension by at most dim(V_new) <= 2k, hence its width is at most 3k. The final leaf cut has width at most dim(V_new) <= 2k.

The executable producer retains every whole factor block, affine offset, scaffold node, candidate edge, exact cut boundary RREF, width, cumulative work and semantic digest. The independent verifier recomputes all boundaries and rejects digest-repaired semantic tampering.

The six-block B4.1 insertion obstruction is included: it has no width-1 insertion in the previous order but the emitted append caterpillar is certified at width at most 3. This does not infer NO_LAYOUT_AT_CAP.

This closes only scaffold construction. Node full sets, branch-edge refinement, reconstruction completeness and empty-root NO_LAYOUT_AT_CAP remain open.

```text
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
