# R5 E9 — Affine F3 Line-Free Proper-Blocking Source Countercontrol

Date: 2026-09-30

Status:
`JANUS_EXACT_FINITE_HOSTILE_COUNTERCONTROL__PCQ_AND_PROJECTIVE_LINE_UNIVERSALIZATION_FALSIFIED`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PROJECTIVE_BLOCKING_LINE_TERMINAL_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_CLASS_FIXED_POINT_QUOTIENT_2026-09-30_v1.0.md`

## 1. Purpose

The affine-F3 route recently produced two exact polynomial preprocessors:

1. the parallel-class fixed-point quotient (PCQ), which solves complete three-offset classes and contracts two-offset classes;
2. the projective-line terminal, which returns UNSAT whenever the homogenized blocking set contains a full `PG(1,3)`.

A tempting conjecture was that the source-specific clause geometry might force every UNSAT source to expose one of those certificates.

This note gives an explicit literal connected square linear-cubic countercontrol. It is UNSAT, survives PCQ, contains no complete projective line, and every source clause is a nondegenerate rooted four-circuit through the distinguished point at infinity.

Thus

```text
SOURCE-GENERATED + ROOTED-QUADRANGLE GEOMETRY
=> PCQ OR PROJECTIVE-LINE CERTIFICATE
```

is false.

This is a finite falsifier of that proposed route, not a lower bound against other algorithms and not evidence that P!=NP.

## 2. Explicit source

Use 0-based variable indices and the 15 rows

```text
(0,1,2)
(0,9,10)
(0,11,12)
(1,8,10)
(1,11,13)
(2,3,6)
(2,4,5)
(3,8,12)
(3,9,13)
(4,7,8)
(4,9,14)
(5,7,13)
(5,12,14)
(6,7,14)
(6,10,11)
```

Call its incidence matrix `A*`.

This source is only one degree-preserving two-edge switch away from the frozen PG15 SAT control.  The two changed rows are

```text
PG15: (4,7,12), (5,8,14)
A*:   (4,7,8),  (5,12,14).
```

The switch preserves every row degree and column degree.

Exact checker facts:

```text
n = 15
row degree = 3
column degree = 3
linear hypergraph = YES
Levi connected = YES
rank_Q(A*) = 11
rank_F3(A*) = 11
affine dimension d = 4
```

## 3. Exact UNSAT

The checker independently verifies UNSAT in two finite exact ways.

First, because every Exact-One witness in a square cubic source has support `n/3=5`, it checks all `C(15,5)=3003` candidate supports and finds none.

Second, it computes the affine F3 solution space

```text
A* r = 1,
r = r0 + B alpha,
alpha in F3^4.
```

There are exactly

```text
3^4 = 81
```

affine solutions.  Every one has at least one zero coordinate, so there is no nowhere-zero affine solution. By AF3-1 the source is Exact-One UNSAT.

Hence the UNSAT status is exact and does not depend on an external SAT oracle.

## 4. PCQ survives completely

Run the affine-F3 parallel-class fixed-point quotient on `A*`.

It reaches a residual with

```text
initial d = 4
final d   = 4
Case-2 dimension-drop pins = 0
Case-3 complete parallel covers = 0
surviving projective normal classes = 15
```

Thus every coordinate has a distinct surviving projective normal direction with exactly one forbidden offset.

So the rank-one affine cover mechanism is fully exhausted and does not solve this UNSAT instance.

## 5. No projective-line certificate

Homogenize coordinate constraints as in PBL-1:

```text
h_i = (b_i, r0_i) in F3^5,
p_inf = (0,0,0,0,1).
```

After projective normalization the 15 source coordinates remain 15 distinct projective points. Add `p_inf`, giving 16 points in `PG(4,3)`.

The exact checker enumerates every projective line determined by every pair of these 16 points and verifies:

```text
number of complete PG(1,3) lines contained in B = 0.
```

Therefore the projective-line UNSAT terminal returns `UNKNOWN`, as required.

## 6. Every clause is a genuine rooted four-circuit

For every source row `{i,j,k}`, the affine parameterization gives

```text
b_i + b_j + b_k = 0,
r0_i + r0_j + r0_k = 1  (mod 3).
```

Therefore

```text
h_i + h_j + h_k = p_inf.
```

On this particular countercontrol, for all 15 source rows the four projective points

```text
{h_i, h_j, h_k, p_inf}
```

have vector rank exactly 3 and every three-point subset has rank 3.  Thus each source row is a genuine four-element circuit (a projective quadrangle), not a rank-two degeneration.

So the failure of PCQ/PBL cannot be blamed on degenerate source clauses.

## 7. The blocking set is genuinely proper and high-rank

The 15 affine zero-hyperplanes cover all 81 points of `F3^4`.
The checker exhaustively searches the `2^15` coordinate subfamilies and finds:

```text
minimum number of coordinate hyperplanes covering F3^4 = 11.
number of minimum 11-hyperplane covers = 36.
```

For every one of those 36 minimum covers, adjoining `p_inf` yields a 12-point projective blocking set with:

```text
vector span rank = 5  (spans PG(4,3)),
complete projective lines contained = 0.
```

Hence the obstruction is not merely a hidden rank-one parallel class, a four-line pencil, or a blocking set contained in a projective plane.  It is a literal source-generated line-free proper blocking configuration spanning the full ambient `PG(4,3)`.

This is fully consistent with finite-geometry literature: proper blocking sets (blocking all hyperplanes while containing no line) are known to exist.  No novelty claim is made for proper blocking sets themselves.

## 8. Consequence for the universal route

The following proposed implication is now closed:

```text
linear-cubic source
+ AF3
+ PCQ fixed point
+ rooted nondegenerate four-circuits
+ no projective line
=> SAT
```

It is false already at `n=15`.

The next finite-field universal primitive must handle line-free proper blocking sets.  A correct next gate is therefore

```text
R5_E9_AFFINE_F3_PROPER_BLOCKING_GLOBAL_CONTRACTION_GATE_V1
```

Input may assume:

```text
Ar=1 is consistent;
PCQ is at fixed point;
no full projective line exists;
source is connected square linear-cubic;
all source clauses may be nondegenerate rooted four-circuits.
```

Required PASS:

```text
construct a disjoint projective hyperplane / nowhere-zero affine point,
or construct a polynomially discoverable blocking certificate/contraction,
with exact witness reconstruction and a strict polynomial progress measure.
```

The explicit `A*` above is now a mandatory hostile control for every proposed continuation.

## 9. Ceiling

```text
A* CONNECTED / SQUARE / LINEAR / CUBIC = PASS
A* EXACT-ONE = UNSAT
rank_F3(A*) = 11
affine dimension = 4
PCQ = RESIDUAL / NO PIN / NO PARALLEL COVER
PROJECTIVE LINE TERMINAL = NO LINE
ALL 15 SOURCE CLAUSES = NONDEGENERATE ROOTED 4-CIRCUITS
MINIMUM AFFINE COVER SIZE = 11
MINIMUM PROJECTIVE BLOCKING SET WITH p_inf = 12 POINTS / FULL RANK 5 / LINE-FREE

PCQ + LINE TERMINAL UNIVERSALIZATION = FALSIFIED
PROPER-BLOCKING GLOBAL CONTRACTION = OPEN
UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```