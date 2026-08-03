# C049.1 Phase B3 — partition-aware expand / join / shrink

This stacked draft implements the three full-set composition operations from Jeong–Kim–Oum, `arXiv:1507.02184v4`, Sections 3.3–3.5 and Propositions 4.2–4.4, while retaining the whole-subspace partition required by C049.

## Algebra

For child boundaries `B1`, `B2`, define the common join boundary

```text
B' = B1 + B2.
```

The pipeline is

```text
F1' = up_k(F1, B')
F2' = up_k(F2, B')
F'  = up_k(F1' ⊕ F2', B')
F   = up_k(F'|B_parent, B_parent).
```

### Expand

A trajectory over `B_child` is transported to a larger boundary `B_parent` only after verifying `B_child <= B_parent` and the Proposition 4.2 side condition. The transcript records the raw child and parent bases and coordinates of every child basis vector in the parent basis.

### Join

For every compatible child pair, every lattice path with steps `(1,0)`, `(0,1)`, `(1,1)` is materialized. At path point `(i,j)`, the output statistic uses

```text
L = L_i + L_j
R = R_i + R_j
lambda = lambda_i + lambda_j
       + dim(R_1(first) ∩ R_2(first))
       - dim((L_i+R_i) ∩ (L_j+R_j)).
```

The certificate stores the complete pre-compact joined sequence and every correction term. Intermediate volume is charged before B1 compactification.

### Shrink

Projection to `B0 <= B` applies

```text
L' = L ∩ B0
R' = R ∩ B0
lambda' = lambda + dim(L∩R) - dim(L∩R∩B0).
```

Every projected statistic, correction, and subsequent B1 compactification is recorded.

## Hardened audit

```text
8 proof cases
6 CLOSED_EXACT
1 OPEN_WORK_BUDGET
1 OPEN_CERTIFICATE_VOLUME

6 lattice paths replayed
27 pre-compact statistics charged
11 -> 5 intermediate-spike control
1 exact root entry in the complete small expand/join/shrink/up_k pipeline
noncanonical boundary basis transport replayed
partition-losing split rejected
```

The independent verifier imports neither producer nor B3 core. It reconstructs all subspaces, coordinate transports, lattice paths, join corrections, projections, compact normal forms, bounded `up_k` closures, fixed-point byte counts, and outer integrity.

Three semantic tamper controls are rejected after case and artifact digests are repaired:

```text
altered lattice path
truncated pre-compact join
altered shrink lambda correction
```

Frozen full-artifact digest:

```text
5a1d8801b2f34265ba6f9b1b2c7c185ff211afd6e50206fd48b2ac4e335e7b0e
```

## Strict boundary

B3 does not implement the branch-decomposition dynamic program, iterative compression, deterministic `FOUND_LAYOUT`, complete `NO_LAYOUT_AT_CAP`, or C047 composition from a discovered layout.

```text
NEXT_GATE = C049.1_PHASE_B4_ITERATIVE_COMPRESSION
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
