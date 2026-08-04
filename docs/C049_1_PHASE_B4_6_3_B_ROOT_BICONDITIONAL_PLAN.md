# C049.1 B4.6.3-B — Root Full-Set Biconditional Plan

The B-gate must replace fixture-level terminal checks with a semantic induction.

## Published target

Jeong–Kim–Oum, arXiv:1507.02184v4, Proposition 5.8 states the exact terminal theorem used by their constructive algorithm:

```text
path-width(V) <= k  iff  F_root != empty
```

Their proof first establishes, by induction over the full-set algorithm, the exact node identities

```text
F_v       = FS_k(V_v, B_v)
F'_v      = FS_k(V_v, B'_v)
F_v^(i)   = FS_k(V_wi, B'_v)
```

using the leaf initialization and the published expand, join and shrink propositions. The root terminal follows only after those equalities are established. Therefore B4.6.3-B must replay this induction inside the JANUS certificate; citation alone is not an admission.

Primary source:

```text
Jisu Jeong, Eun Jung Kim, Sang-il Oum
The “art of trellis decoding” is fixed-parameter tractable
arXiv:1507.02184v4
Proposition 5.8; Theorem 5.10; iterative-compression use in Section 6.1
```

## JANUS semantic language

For each scaffold node `t`, define a language `L_t(k)` of all width-at-most-`k` whole-factor partial layouts of the factors covered by `t`, represented at the exact boundary of `t`.

The required machine theorem is:

```text
Gamma is represented by FullSet(t)
iff
Gamma is induced by some member of L_t(k)
```

The proof must be split into independently replayable obligations:

1. **Leaf base case.** The canonical leaf generator and its `up_k` closure represent exactly the one-factor partial layouts at the leaf boundary.
2. **Expand completeness.** Every child language element transports to the common boundary, and no transported semantic state is omitted.
3. **Join completeness.** Every compatible interleaving is represented by an enumerated Delannoy lattice path.
4. **Shrink completeness.** Projection to the parent boundary preserves the exact represented partial-layout semantics.
5. **Width filter soundness and reflection.** A failed refinement is infeasible at cap `k`; a feasible parent semantic state has at least one successful refinement.
6. **B2 preservation and reflection.** Duplicate deletion, extension-preorder minimization and `up_k` closure preserve the represented language, not merely the finite trajectory set.
7. **Root specialization.** At empty boundary, represented width-at-most-`k` trajectories correspond exactly to complete whole-factor layouts.

Only after obligations 1–7 are machine-bound may the engine execute:

```text
accepting root entry -> FOUND_LAYOUT
no accepting root entry + complete transcript -> NO_LAYOUT_AT_CAP
capacity or budget stop -> OPEN_*
```

## Counterexample-first implementation order

Before admitting the general induction, the B-gate attack generator must enumerate bounded grouped arrangements and compare every computed node full set with a direct semantic oracle. It must search independently for the smallest witness to each possible failure:

```text
false positive trajectory in a node full set
missing feasible trajectory at a leaf
missing compatible child pair
missing lattice-path interleaving
successful semantic state lost by width filtering
language lost by duplicate or dominance deletion
language lost or invented by up_k closure
root nonempty while no layout exists
root empty while a layout exists
```

Every discovered mismatch must retain the complete grouped fixture, affine offsets, scaffold, child entries, pair, lattice path, refinement, deletion witness, work ledger and certificate-volume receipt.

## Admission boundary

```text
PUBLISHED_ROOT_BICONDITIONAL = IDENTIFIED
JANUS_ROOT_BICONDITIONAL     = NOT_YET_PROVED
NO_LAYOUT_AT_CAP             = FORBIDDEN
CURRENT_GLOBAL_TERMINAL      = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                      = OPEN
```
