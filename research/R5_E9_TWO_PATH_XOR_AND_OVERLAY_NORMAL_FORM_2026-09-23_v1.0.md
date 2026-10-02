# R5 E9 — Two-Path XOR/AND Overlay Normal Form

Date: 2026-09-23

Authority:
`PROVED_EXACT_LINEAR_NORMAL_FORM__CROSS_LAYER_OVERLAY_IS_THE_ONLY HARD INTERFACE__NO_D1_PROMOTION`

Parent:

`R5_E9_NONLOCAL_RANK1_JOINT_CONTRACTION_PIVOT_GATE_V1`

Checker:

`research/tools/r5_e9_two_path_xor_and_overlay_normal_form_checker.py`

## 1. Goal

The APAC sharpness theorem already proved that

```text
2-affine
+
FULL products
```

can encode arbitrary 3CNF.

This note strengthens that statement structurally.

The universal encoding can be chosen so that **each layer separately is a
forest of paths**.

Therefore any useful contraction potential must measure the interaction
between the layers, not a static width/cycle parameter of either layer alone.

## 2. Occurrence variables

Let an original signed 3CNF formula be given.

For each literal occurrence `ell` introduce one Boolean occurrence variable
`a_ell` representing the negation of that literal:

```text
a_ell = NOT ell.
```

For an original variable `x` define the sign bit

```text
c_ell = 1  if ell = x,
c_ell = 0  if ell = NOT x.
```

Then

```text
a_ell = x XOR c_ell.
```

Suppose the occurrences of `x` are ordered
`ell_1,...,ell_d`.

Instead of one high-degree equality/star constraint, impose only the path
equations

```text
a_{ell_i} + a_{ell_{i+1}}
=
c_{ell_i} + c_{ell_{i+1}}
over F2
```

for `i=1,...,d-1`.

These equations imply that

```text
a_ell XOR c_ell
```

is constant along the path, hence reconstruct one unique original Boolean
value `x`.

Thus variable coherence is represented by a disjoint union of XOR2 paths.

## 3. Clause gadget

For one clause

```text
ell_1 OR ell_2 OR ell_3
```

write

```text
a_i = NOT ell_i.
```

The clause is true iff not all `a_i` are one:

```text
NOT(a_1 a_2 a_3).
```

Introduce private variables `t_C,u_C` and impose

```text
t_C = a_1 a_2

u_C = t_C a_3

u_C = 0.
```

This is exact.

The nonlinear clause gadget is a two-AND chain.

Different clauses use disjoint occurrence and product variables, so the
product-factor layer is a disjoint union of constant-length paths.

## 4. Exactness

### Theorem E9-TPA1

The construction is satisfiability preserving in both directions.

#### Forward

Given an assignment of the original variables:

1. set every occurrence `a_ell = NOT ell`;
2. all XOR2 coherence path equations hold;
3. set `t_C=a_1a_2`, `u_C=t_Ca_3`;
4. `u_C=0` iff the original clause is satisfied.

#### Backward

Given a satisfying transformed assignment:

1. each coherence path makes `a_ell XOR c_ell` constant for each original
   variable;
2. use that common value as the reconstructed `x`;
3. the two product identities make `u_C=a_1a_2a_3`;
4. `u_C=0` implies at least one original literal is true.

Therefore the reconstructed assignment satisfies the original formula.

The construction and reconstruction are linear-time up to ordinary indexing.

The checker exhaustively verifies all `2^8=256` signed-clause subsets on
three variables against all eight assignments, i.e. 2048 formula/assignment
cases.

## 5. Layer structure

### Affine layer

For each original variable:

```text
occurrence coherence
=
one path of XOR2 equations.
```

Hence the affine coherence graph is a disjoint union of paths.

### Product layer

For each original clause:

```text
a_1,a_2 -> t_C
t_C,a_3 -> u_C
```

with private variables.

Hence the AND-factor incidence structure is a disjoint union of two-edge
paths.

In particular:

```text
TREEWIDTH OF EACH LAYER SEPARATELY
<=
1
(up to the constant-size factor-node convention).
```

All variable/factor degrees can also be kept constant.

## 6. Complexity classification

The transformed problem is in NP.

The exact linear-size reduction from arbitrary signed 3CNF proves that the
class of these two-path overlay instances is NP-hard.

Therefore the corresponding decision problem is NP-complete.

This is a complexity classification of the representation class. It is not an
assumption that P differs from NP.

## 7. Main structural consequence

Neither of the following can be the missing universal currency by itself:

```text
PRODUCT LAYER HAS SMALL TREEWIDTH

AFFINE COHERENCE LAYER HAS SMALL TREEWIDTH
```

Both properties can hold simultaneously while the overlay still represents
arbitrary 3CNF exactly.

Likewise, a potential based only on:

- number of product cycles;
- product-layer feedback set;
- affine-equation arity/width <=2;
- layerwise bounded degree;
- layerwise forest decomposability

cannot certify universal polynomial progress.

The difficulty is the **cross-layer incidence permutation**: which occurrence
path vertices are grouped together by clause-product paths.

## 8. Sharpened active object

Define the representation type

```text
TWO_PATH_XOR_AND_OVERLAY_CSP.
```

It consists of:

1. one family of disjoint XOR2 occurrence paths;
2. one family of disjoint two-AND clause paths;
3. unary product-output zero constraints;
4. arbitrary overlay between the two path families induced by clause
   membership.

The universal SAT problem already lives inside this highly sparse form.

Hence the active contraction question becomes:

```text
Can the overlay itself admit
an exact polynomial quotient/contraction currency
with a decreasing global potential?
```

not:

```text
Can either layer separately
be made sparse/acyclic?
```

## 9. Candidate joint potentials that survive this theorem

A candidate must depend on the overlay, for example:

- cut-rank of the bipartite incidence between variable paths and clause paths;
- a certified quotient of path-boundary extension behavior;
- nonlocal syndrome rank coupling both colors;
- a contraction potential defined on the two-edge-colored overlay graph;
- another algebraic invariant provably reduced by exact quotient/lift steps.

These are candidates only, not claims.

## 10. Ceiling

```text
3CNF
-> TWO-PATH XOR/AND OVERLAY
=
PASS EXACT LINEAR NORMAL FORM

AFFINE LAYER TREEWIDTH
=
1

PRODUCT LAYER TREEWIDTH
=
1

LAYERWISE SPARSITY / ACYCLICITY
=
INSUFFICIENT

CROSS-LAYER OVERLAY COMPRESSION
=
OPEN <<< ACTIVE MICRO-GAP

D1
=
EMPTY

P_VS_NP
=
OPEN
```
