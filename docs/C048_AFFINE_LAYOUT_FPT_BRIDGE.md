# C048.1 — Affine layout FPT bridge

```text
P_VS_NP = OPEN
C048.1 = THEOREM_LEVEL_PRIMARY_SOURCE_BRIDGE
       / EXECUTABLE_IDENTITY_AUDIT
       / PUBLISHED_CONSTRUCTOR_NOT_REIMPLEMENTED
       / DRAFT
```

## 1. Route correction

C047 defines, for an order `pi` of factor normal spaces `N_i`,

\[
P_t=\sum_{j\le t}N_{\pi(j)},\qquad
S_t=\sum_{j>t}N_{\pi(j)},\qquad
B_t=P_t\cap S_t,
\]

and uses

\[
w(\pi)=\max_t\dim B_t
\]

as its trellis width.

This is not a new unresolved layout parameter. It is exactly the linear-layout
width of a finite-field subspace arrangement studied by Jeong, Kim and Oum.
Their constructive theorem receives the subspaces themselves and an integer
`k`, and constructs a layout of width at most `k` if one exists in fixed-
parameter tractable total work over every fixed finite field.

Therefore the abstract fixed-`k` existence of a polynomial/FPT layout discovery
algorithm is already known. C048.1 must not rename that theorem or continue to
list it as an unlocated invariant-discovery problem.

## 2. Exact identity

For every cut,

\[
\dim(P_t\cap S_t)
=\dim P_t+\dim S_t-\dim(P_t+S_t).
\]

The right-hand side is the connectivity value used in the published subspace-
arrangement linear-layout problem. Hence the equality is per order and per cut,
not merely an asymptotic comparison.

Offsets `beta_i` do not enter the layout width. This is sound because C046/C047
retain them in the separator semantics: the layout constructor chooses only the
normal-space skeleton, while C047 leaf and transition messages carry the
distinguished affine functionals.

## 3. Published constructive theorem

Primary source:

```text
Jisu Jeong, Eun Jung Kim, Sang-il Oum
Constructive algorithm for path-width of matroids
SODA 2016, DOI 10.1137/1.9781611974331.ch116
extended version: arXiv:1507.02184
```

The theorem is stated directly for `n` subspaces of a finite-dimensional vector
space over a fixed finite field. It constructs a linear layout of width at most
`k` if such a layout exists, in FPT time parameterized by `k`.

This direct subspace-arrangement theorem is the load-bearing source. Results on
matroid path-width and code trellis complexity align the one-dimensional case,
but are not substituted for the grouped-subspace statement.

## 4. Composition with C047

Let `F(k) poly(L)` be the published layout-construction bound. C047 compiles a
verified width-`k` order in

\[
2^{O(k)}\operatorname{poly}(L)
\]

work with offset-aware affine-functional states. Their composition gives

\[
F(k)2^{O(k)}\operatorname{poly}(L)
\]

exact SAT/UNSAT compilation for affine arrangements of linear-layout width at
most `k`.

For every fixed `k`, this is polynomial total work. It is only FPT when `k` is
part of the input and is not promoted to a universal polynomial algorithm.
A `NO_LAYOUT_AT_CAP` result does not imply hardness or `P != NP`.

## 5. What the repository package proves

The executable package independently checks:

- the per-cut equality between explicit intersection dimension and the rank
  connectivity formula;
- offset invariance of the layout skeleton;
- exact small-instance optimum layouts by finite exhaustive audit;
- C046 equal-normal width one;
- forty independent normal spaces at width zero;
- the C045 hidden-prefix-normal control at width zero;
- rejection of any claim that the finite exhaustive audit implements the
  published FPT constructor.

Frozen audit:

```text
220 random arrangements
90 exhaustive small arrangements
81,106 layouts checked
0 random identity failures
0 exhaustive identity failures
220 offset-invariance controls
```

Finite enumeration validates the bridge implementation only. The universal
fixed-parameter theorem comes from the primary source.

## 6. Remaining proof-carrying obligation

The JANUS repository does not yet reimplement the Jeong-Kim-Oum constructor.
A supplied good order is therefore still forbidden as a claimed C048 discovery
result.

The next implementation must expose and charge:

```text
normal-space extraction and canonicalization
all constructor states and failed probes
FOUND_LAYOUT or NO_LAYOUT_AT_CAP terminal
complete order and per-cut bases
standard-model work and coefficient bits
certificate fixed point and volume
independent constructor replay
C047 solve, witness lifting, and UNSAT replay
```

Until that integration exists, the exact status is a theorem-level bridge, not
an end-to-end proof-carrying implementation.

## 7. Branch-decomposition alignment

Jeong-Kim-Oum also give an FPT constructor for branch-decompositions of finite-
field subspace arrangements (`arXiv:1711.01381`). This supports the sibling
route `OFFSET_AWARE_BRANCH_DECOMPOSITION_COMPOSITION`.

The 2026 Choi-Korhonen-Oum algorithm improves branch-width construction for
represented matroids (`arXiv:2605.14428`). It is important current alignment,
but it does not automatically replace the direct grouped-subspace theorem used
here.

## 8. Cycle allocation

```text
C048   frozen affine-layout portfolio (PR #72)
C048.1 primary-source FPT layout bridge (this PR)
```

PR #72 remains canonical C048. This bridge is stacked on it and does not compete for that identifier. The branch/file paths retaining `c048` are pre-admission replay aliases.

## 9. Surviving gate

```text
PROOF_CARRYING_FPT_LAYOUT_CONSTRUCTOR_INTEGRATION
OR
OFFSET_AWARE_BRANCH_DECOMPOSITION_COMPOSITION
```

C048.1 does not prove that arbitrary affine arrangements have bounded layout
width, does not close the NAND3+NEQ image, and does not resolve P versus NP.
