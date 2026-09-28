# R5 E9 — Source-Kernel Boundary Nonconvex / Nongated Barrier

Date: 2026-09-28

Status: `JANUS_EXACT_SAT_COUNTERCONTROL__BOUNDARY_TOPE_SET_NONCONVEX_NONGATED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_SOURCE_KERNEL_TOPE_GEODESIC_AUGMENTING_PATH_BOUND_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_source_kernel_boundary_nonconvex_barrier.py`

Scientific ceiling:

```text
THE EXACT p=n/3 SAT-BOUNDARY TOPES NEED NOT FORM A CONVEX OR GATED SUBSET
OF THE SOURCE-KERNEL TOPE GRAPH.

ON THE FROZEN PG15 SAT CONTROL THE FOUR BOUNDARY TOPES ARE PAIRWISE
DISTANCE 6, AND A SHORTEST PATH BETWEEN TWO BOUNDARY TOPES LEAVES THE
BOUNDARY IMMEDIATELY THROUGH AN EXACT p=6 CHAMBER.

THEREFORE PARTIAL-CUBE GEOMETRY DOES NOT PROVIDE A FREE CONVEX/GATED
PROJECTION OR GREEDY METRIC ROUTE TO THE UNKNOWN SAT BOUNDARY.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Boundary target

For a cubic square Exact-One source with `3|n`, the rational-kernel depth
boundary theorem gives

```text
boundary tope
<=> full-support y in ker_Q(A) with exactly n/3 positive coordinates
<=> the positive set is an Exact-One witness.
```

For the frozen `PG15_SAT_R11` source, `n=15`, so the boundary is `p=5`.

The exact source has four Boolean witnesses:

```text
X1={1,5,7,9,14}
X2={2,6,7,10,13}
X3={3,8,9,10,12}
X4={3,11,13,14,15}.
```

Using the frozen `15 x 4` rational-kernel basis `B`, their exact coefficient
vectors for `y=3 1_X-1` are

```text
alpha_1=(-1,-1, 2,-1)
alpha_2=(-1, 2,-1,-1)
alpha_3=( 2,-1,-1,-1)
alpha_4=(-1, 2, 2, 2).
```

Therefore these are four actual boundary chambers of the source-kernel
arrangement.

## 2. Projective hyperplane classes

The simplified PG15 arrangement has the eleven distinct projective classes

```text
{1,5}, {2,6}, {3}, {4}, {7}, {8,12},
{9}, {10}, {11,15}, {13}, {14}.
```

By the source-kernel tope geodesic theorem, chamber distance is Hamming distance
on these projective signs, equivalently the number of separating classes.

Direct exact evaluation shows every pair among the four boundary topes is
separated by exactly six projective hyperplanes. Hence

```text
dist(X_i,X_j)=6 for every i!=j.
```

In particular no two boundary chambers are adjacent. On this finite control the
boundary-induced subgraph consists of four isolated vertices.

## 3. Explicit shortest path that leaves the boundary

Take the boundary chambers

```text
C1: alpha_1=(-1,-1,2,-1),
    P(C1)={1,5,7,9,14},
    p(C1)=5,

C2: alpha_2=(-1,2,-1,-1),
    P(C2)={2,6,7,10,13},
    p(C2)=5.
```

They differ on exactly six projective classes, so

```text
dist(C1,C2)=6.
```

Now take

```text
Z: alpha_Z=(-1,-1,2,-3).
```

Then

```text
B alpha_Z
=(-1? evaluated only by signs here)
```

has positive set exactly

```text
P(Z)={1,5,7,9,10,14},
```

so

```text
p(Z)=6.
```

`C1` and `Z` differ only on the projective singleton class `{10}`, hence

```text
dist(C1,Z)=1.
```

`Z` and `C2` differ on exactly five projective classes,

```text
{1,5}, {2,6}, {9}, {13}, {14},
```

so

```text
dist(Z,C2)=5.
```

Therefore

```text
dist(C1,Z)+dist(Z,C2)=1+5=6=dist(C1,C2).
```

Thus `Z` lies on a shortest gallery between two boundary topes, while `Z` is
not itself a boundary tope.

## 4. Nonconvexity and nongatedness

In a graph, a convex vertex set contains the interval between each pair of its
vertices, i.e. every vertex lying on a shortest path between them.

The two boundary topes `C1,C2` belong to the boundary set, but the interval
between them contains `Z` with `p=6`. Therefore the boundary-tope set is not
convex.

Every gated vertex set is convex. Consequently the PG15 boundary-tope set is
also not gated.

Hence the standard partial-cube mechanism

```text
convex/gated target
=> canonical metric projection
=> repeated distance-reducing halfspace choices
```

cannot be imported for free: the actual SAT boundary target already violates
the premise on a 15-variable positive control.

## 5. Relation to the geodesic theorem

There is no contradiction with the previous result.

The tope graph itself is a partial cube, so between any **known** current tope
and any **known** target boundary tope there is a shortest gallery crossing each
separating class once and of length at most `n`.

What fails is convexity of the **union of all boundary targets**. A shortest
path between two optimal boundary chambers can pass through strictly worse
chambers. Therefore knowing only the objective value `p` or the metric geometry
of the target set does not supply a canonical local projection.

This sharpens the remaining obstruction:

```text
PATH LENGTH = POLYNOMIALLY BOUNDED,
TARGET SET = NONCONVEX / NONGATED,
CORRECT ROUTE SELECTION = OPEN.
```

## 6. Anti-loop consequence

Freeze the following shortcuts as falsified:

```text
BOUNDARY_TOPES_ARE_CONVEX
BOUNDARY_TOPES_ARE_GATED
PARTIAL_CUBE_NEAREST-POINT_PROJECTION_SOLVES_SOURCE_BOUNDARY
```

Forbidden future pseudo-progress:
- assume the `p=n/3` topes form a convex face of the tope graph;
- invoke gated-set projection without proving a stronger source-specific target;
- infer that every geodesic between boundary witnesses stays optimal;
- use partial-cube isometry alone as a boundary-selection algorithm.

## 7. Refined live gate

Keep

```text
R5_E9_SOURCE_KERNEL_BOUNDARY_GEODESIC_DIRECTION_ORACLE_GATE_V1
```

but strengthen its hostile controls:

A PASS must work on the PG15 pair `C1,C2` above and cannot rely on convexity or
gatedness of the set of all boundary topes.

Promising admissible shapes now include:

1. a source-specific orientation / potential on projective classes which selects
   one boundary basin without requiring global target convexity;
2. a polynomial symbolic augmenting-cascade constructor based on source defect
   structure plus exact arrangement-feasibility tests;
3. a compact global certificate separating all boundary topes on UNSAT;
4. a different complete exact representation change.

## 8. Ceiling

```text
PG15 BOUNDARY TOPES
= 4

PAIRWISE BOUNDARY DISTANCE
= 6 PROJECTIVE HYPERPLANES

EXPLICIT INTERVAL WITNESS
C1 (p=5)
-> Z (p=6)
-> ...
-> C2 (p=5)
WITH dist(C1,Z)+dist(Z,C2)=dist(C1,C2)

BOUNDARY SET CONVEX
= FALSE

BOUNDARY SET GATED
= FALSE

PARTIAL-CUBE GEODESIC LENGTH <= n
= TRUE

POLYNOMIAL TARGET / DIRECTION SELECTION
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```