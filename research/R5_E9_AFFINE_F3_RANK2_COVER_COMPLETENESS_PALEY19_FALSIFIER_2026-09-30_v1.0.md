# R5 E9 — Affine F3 Rank-2 Cover Completeness Falsifier: Paley(19)

Date: 2026-09-30

Status:
`JANUS_EXACT_STRUCTURAL_FALSIFIER__COVER_NORMAL_RANK_AT_MOST_TWO_NOT_COMPLETE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_RANK2_QUOTIENT_COVER_UNSAT_ROUTER_2026-09-30_v1.0.md`
- `research/R5_E9_PALEY19_GRADIENT_KERNEL_POST_RKPR_CONTROL_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THE RANK-2 ROUTER REMAINS SOUND AND POLYNOMIAL.
THIS NOTE PROVES IT IS NOT COMPLETE, EVEN ON A CONNECTED LINEAR-CUBIC
POST-RKPR UNSAT SOURCE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen Paley(19) source

Use the existing Paley(19) tournament control with the nine translation-orbit representatives

```text
(0,1,2)
(0,1,10)
(0,2,4)
(0,3,6)
(0,3,11)
(0,4,8)
(0,5,10)
(0,5,12)
(0,6,12)
```

on the Paley tournament of order 19.

The existing exact artifact proves that the resulting triangle-versus-arc incidence matrix `A` has

```text
n=171,
row degree = column degree = 3,
linear source,
Levi-connected,
rank_Q(A)=153,
nullity_Q(A)=18,
RKPR zero rows = 0,
RKPR proportional pairs = 0,
Exact-One = UNSAT.
```

The UNSAT certificate is structural: over Q the kernel is exactly the gradient space of vertex potentials on the 19 tournament vertices. A Boolean Exact-One word would force all pairwise potential differences to lie in `{-1,2}`, impossible for 19 vertices.

## 2. Ternary affine system is consistent and high-dimensional

Work over `F3`. Exact Gaussian elimination gives

```text
rank_F3(A)=152,
dim ker_F3(A)=19.
```

Because `n=171` is divisible by 3, the trivial left-all-ones obstruction does not reject the affine equation. Direct exact elimination confirms

```text
A r = 1
```

is consistent.

Thus the AF3 hyperplane-avoidance instance is a genuine 19-dimensional affine space, not an inconsistent linear terminal.

## 3. Coordinate-zero hyperplanes are projectively simple

Write all affine solutions as

```text
r=r0+B alpha,
alpha in F3^19.
```

For every coordinate `i`, normalize the nonzero kernel-row functional to

```text
c_i alpha=t_i.
```

Exact enumeration of the 171 coordinate equations gives

```text
zero normal rows = 0,
projective normal classes = 171,
maximum offsets per projective normal class = 1.
```

Hence all 171 projective normals are distinct.

Immediate consequences:

1. no rank-zero identically-zero-coordinate certificate exists;
2. no rank-one parallel-triple cover exists.

The source is nevertheless UNSAT, so the complete 171-hyperplane family covers the whole affine parameter space by AF3-1.

## 4. Rank-two cover criterion under one-offset-per-direction

Take any two distinct projective normals `u,v`. Since they are not proportional they span a 2-dimensional normal plane `U`.

The projective line `P(U)` over `F3` contains exactly four projective directions:

```text
[u], [v], [u+v], [u+2v].
```

Because the Paley(19) affine cover has at most one coordinate hyperplane in each projective direction, the subfamily whose normals lie in `U` contains at most four induced affine lines in the quotient `F3^2`.

A family containing fewer than four distinct-direction lines cannot cover all nine points of `F3^2`.

With exactly one line in each of the four directions, the four lines cover `F3^2` iff they form the complete affine pencil through one quotient point. Equivalently, after choosing quotient coordinates

```text
x=u alpha,
y=v alpha,
```

if the `u`- and `v`-lines have offsets `a,b`, then the normalized `u+v` and `u+2v` lines must have exactly the offsets induced by the same point `(a,b)`, with the appropriate projective rescaling.

This criterion is checked exactly for every pair of the 171 observed normals.

## 5. Exhaustive exact rank-two rejection

There are

```text
C(171,2)=14535
```

pairs of observed projective normals.

For each pair, the checker:

1. constructs the other two projective directions in their span;
2. checks whether those directions occur among the 171 coordinate normals;
3. if all four directions occur, transports the actual normalized offsets into the `(u,v)` quotient;
4. tests whether the four lines are concurrent / cover all nine quotient points.

Result:

```text
rank-2 quotient covers = 0.
```

Therefore no subfamily of coordinate-zero hyperplanes with normal rank at most two covers `F3^19`.

## 6. Theorem

### PALEY19-R2-FALSIFIER

There exists a connected square linear-cubic Positive-1-in-3 source `A` such that

```text
A is Exact-One UNSAT,
A r=1 over F3 is consistent,
dim ker_F3(A)=19,
all coordinate-zero projective normals are distinct,
and every covering subfamily has normal rank >=3.
```

Consequently

```text
UNSAT => existence of a rank<=2 affine-F3 cover certificate
```

is false even on the exact JANUS hard carrier.

The rank-2 router remains a correct polynomial terminal whenever it fires; only universality is falsified.

## 7. Why random testing was misleading

Low/moderate random cubic sources overwhelmingly have small ternary nullity, so if `dim ker_F3(A)<=2`, every affine cover automatically has normal rank at most two. The earlier large finite sample therefore strongly biased toward the rank-2 island.

Paley(19) is the correct adversarial stress test because it combines:

```text
high ternary nullity,
linearity,
connectedness,
projective simplicity,
post-RKPR cleanliness,
and a symbolic UNSAT certificate.
```

This is why it detects the missing higher-rank phenomenon immediately.

## 8. New live gate

The live finite-field target must no longer be a fixed-rank-2 cover classification.

Freeze

```text
R5_E9_AFFINE_F3_PALEY19_HIGH_RANK_COVER_STRUCTURE_GATE_V1
```

Immediate tasks:

1. determine the minimum normal rank of a covering subfamily for Paley(19);
2. identify a polynomially recognizable structural motif for that minimum cover;
3. test whether the motif extends to the infinite Paley gradient-kernel family and to prime SAT/UNSAT lift towers;
4. only then propose a general decomposition/augmentation theorem.

Fixed-rank enumeration alone cannot be universal unless a constant-rank coverage theorem is proved; Paley(19) already rules out constants 0,1,2.

## 9. Ceiling

```text
PALEY19 Exact-One
= UNSAT

F3 AFFINE SYSTEM
= CONSISTENT, DIMENSION 19

PROJECTIVE NORMAL CLASSES
= 171 DISTINCT

RANK-1 COVER
= NONE

RANK-2 COVER
= NONE

MINIMUM COVER NORMAL RANK
>= 3

RANK<=2 UNIVERSAL COMPLETENESS
= FALSIFIED

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
