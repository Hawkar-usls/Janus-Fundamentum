# R5 E9 — Source-Kernel Tope Geodesic Augmenting-Path Bound

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_TOPE_GEODESIC_LENGTH_BOUND__ROUTE_SELECTION_REMAINS_OPEN__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_TUKEY_DEPTH_MONOTONE_TOPE_DESCENT_BARRIER_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_source_kernel_tope_geodesic_bound.py`

Scientific ceiling:

```text
IF A SOURCE-KERNEL BOUNDARY TOPE EXISTS, THEN FROM EVERY FULL-SUPPORT
SOURCE-KERNEL TOPE THERE EXISTS A FACET-GALLERY TO A BOUNDARY TOPE OF
LENGTH AT MOST THE NUMBER OF DISTINCT PROJECTIVE KERNEL HYPERPLANES <= n.

THUS EXPONENTIAL REQUIRED PATH LENGTH IS NOT THE OBSTRUCTION.
THE OPEN PROBLEM IS POLYNOMIAL ROUTE SELECTION WITHOUT KNOWING THE
BOUNDARY TOPE / EXACT-ONE WITNESS.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A` be a cubic square Exact-One source matrix and let

```text
B in Q^{n x d}
```

be a rational kernel-basis matrix, so every rational kernel vector is

```text
y=B alpha.
```

Assume the zero-row terminal has already failed, so every row `b_i` of `B` is
nonzero. Each row defines the central hyperplane

```text
H_i={alpha : b_i dot alpha = 0}.
```

Rows which are nonzero scalar multiples define the same geometric hyperplane.
Collapse them into one projective hyperplane class. Let

```text
Q={H_1,...,H_q}
```

be the resulting set of distinct hyperplanes. Necessarily

```text
q <= n.
```

The connected components of

```text
R^d minus union(Q)
```

are the full-support kernel chambers/topes.

For two topes `C,D`, let

```text
Sep(C,D)
```

be the set of distinct projective hyperplanes whose two open halfspaces contain
`C` and `D` on opposite sides.

## 2. Geodesic theorem

### Theorem SKTG-1

For every two source-kernel topes `C,D`, the minimum number of facet crossings
in a chamber gallery from `C` to `D` is exactly

\[
\boxed{\operatorname{dist}(C,D)=|\operatorname{Sep}(C,D)|}.
\]

In particular

\[
\boxed{\operatorname{dist}(C,D)\le q\le n.}
\]

### Lower bound

Every continuous path from `C` to `D` must cross every hyperplane which
separates the endpoints. A facet-gallery step crosses at most one distinct
projective hyperplane. Therefore every gallery has length at least

```text
|Sep(C,D)|.
```

### Upper bound

Choose interior points

```text
alpha in C,
beta in D.
```

For a defining linear functional `ell_H`, along the line segment

```text
gamma(t)=(1-t) alpha+t beta, 0<=t<=1,
```

we have

```text
ell_H(gamma(t))=(1-t)ell_H(alpha)+t ell_H(beta).
```

If `H` does not separate `C,D`, the endpoint values have the same strict sign,
so the whole convex combination has that sign and the segment never crosses
`H`.

If `H` separates `C,D`, the endpoint values have opposite signs, so the affine
function has exactly one zero in `(0,1)`. Thus the segment crosses each
separating hyperplane exactly once and no nonseparating hyperplane.

A generic arbitrarily small perturbation of `alpha` and/or `beta` inside their
open chambers makes the crossing parameters distinct for distinct geometric
hyperplanes; coincident hyperplanes were already collapsed into one projective
class. Reading the chambers along the perturbed segment gives a gallery with
exactly

```text
|Sep(C,D)|
```

facet crossings.

Together with the lower bound this proves SKTG-1.

This is the realizable hyperplane-arrangement form of the standard fact that
tope graphs are partial cubes.

## 3. Exact consequence for the 1/3 boundary

The rational-kernel depth theorem gives, when `3|n`,

```text
A is Exact-One SAT
iff
there exists a boundary tope D with p(D)=n/3.
```

Combine this with SKTG-1. If `A` is SAT, then for **every** full-support
kernel tope `C` there exists a boundary-directed gallery

```text
C=C_0,C_1,...,C_k=D
```

such that

```text
k=|Sep(C,D)|<=q<=n,
```

and no projective hyperplane class is crossed twice.

Therefore:

```text
SAT => a simple boundary-reaching augmenting cascade of length <= n exists
       from every starting tope.
```

This is an arbitrary-size structural theorem. It rules out one possible source
of hardness for the new representation: a SAT instance cannot require every
boundary-reaching chamber path to have exponential length.

## 4. What this does NOT give

SKTG-1 is an **existence and length** theorem, not a route-selection algorithm.
The endpoint boundary tope `D` encodes an Exact-One witness. Knowing `D` makes
the separating set and a geodesic easy to describe, but finding such a `D` is
precisely the unresolved semantic task.

The number of topes of an arrangement can be exponential in the input, so the
following inference is forbidden:

```text
POLYNOMIAL SHORTEST-PATH LENGTH
=> POLYNOMIAL METHOD TO FIND THE UNKNOWN SAT BOUNDARY TOPE.
```

Likewise, breadth-first search over the entire tope graph is not admitted as a
polynomial algorithm merely because the winning path, if one exists, has
length at most `n`.

## 5. PG15 trap is already a geodesic cascade

Use the exact SAT control from the monotone-descent barrier.

Start chamber:

```text
P0={3,7,9,10,13,14}, p=6.
```

Boundary chamber:

```text
P4={3,11,13,14,15}, p=5.
```

Their element-sign symmetric difference is

```text
{7,9,10,11,15}.
```

Under the exact projective kernel classes

```text
{1,5}, {2,6}, {3}, {4}, {7}, {8,12},
{9}, {10}, {11,15}, {13}, {14},
```

this is precisely four separating hyperplanes:

```text
{7}, {9}, {10}, {11,15}.
```

The already materialized escape cascade

```text
6 -> 8 -> 7 -> 6 -> 5
```

crosses exactly those four classes, each once:

```text
{11,15}, {7}, {9}, {10}.
```

Therefore it is not merely some escape path. It is a shortest chamber gallery:

```text
dist(P0,P4)=4.
```

The temporary rise from `p=6` to `p=8` is consequently unavoidable on **every
one-step-monotone rule**, even though a globally shortest route exists.

## 6. Sharpened algorithmic frontier

The previous gate asked whether a polynomially describable nonmonotone cascade
always exists. SKTG-1 answers the length/existence part positively on SAT
instances.

The live gate can therefore be sharpened to

```text
R5_E9_SOURCE_KERNEL_BOUNDARY_GEODESIC_DIRECTION_ORACLE_GATE_V1
```

Input:

```text
source-induced rational-kernel arrangement,
current full-support tope C,
source depth floor n/3,
unknown status of boundary attainment.
```

A PASS must supply at least one of:

1. a deterministic polynomial rule which, whenever a boundary tope exists,
   chooses a facet that lies on some geodesic from `C` to some boundary tope;
2. a polynomial algorithm producing an entire boundary-directed geodesic
   without first knowing the boundary witness;
3. a polynomially checkable UNSAT certificate excluding every boundary tope;
4. another complete source-specific polynomial solver satisfying the global
   construction/reconstruction/verification contract.

Mandatory hostile controls:
- PG15 strict local minimum `p=6`, whose first successful geodesic step raises
  `p` to `8`;
- singular rank-14 UNSAT depth `6/15` control;
- high-nullity lift families;
- projective fractional-support closure survivors.

Forbidden pseudo-progress:
- BFS/DFS over exponentially many topes;
- guessing the target boundary tope;
- nondeterministically guessing a length-`<=n` path and calling that a
  deterministic polynomial algorithm;
- fixed bounded lookahead justified only by PG15;
- using shortest-path existence as a P=NP conclusion.

## 7. Prior-art / anti-loop note

The partial-cube property of hyperplane-arrangement / oriented-matroid tope
graphs is standard. This note does **not** claim literature novelty for SKTG-1.
Its JANUS contribution is to bind that standard geometric fact to the newly
proved source-kernel `1/3` boundary representation and thereby remove
exponential required path length as the live obstruction.

Relevant background includes the standard statement that tope graphs of
oriented matroids are partial cubes, and the direct arrangement proof that
gallery distance equals the number of separating hyperplanes.

## 8. Ceiling

```text
SOURCE KERNEL SAT BOUNDARY
= p=n/3

TOPE GRAPH
= PARTIAL CUBE AFTER PROJECTIVE SIMPLIFICATION

DIST(C,D)
= # DISTINCT SEPARATING PROJECTIVE HYPERPLANES
<= q
<= n

SAT
=> FROM EVERY FULL-SUPPORT TOPE THERE EXISTS A SIMPLE BOUNDARY GEODESIC
   OF LENGTH <= n

PG15 LOCAL-MINIMUM ESCAPE
= GEODESIC LENGTH 4
= 6 -> 8 -> 7 -> 6 -> 5

EXPONENTIAL REQUIRED PATH LENGTH
= ELIMINATED AS OBSTRUCTION

POLYNOMIAL BOUNDARY-DIRECTION ORACLE
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```