# R5 E9 — Projective-Tope Bounded Augmentation and Prime-Tower Stress

Date: 2026-09-28

Status: `JANUS_DERIVED_CONDITIONAL_POLY_AUGMENTATION_META_THEOREM__EXACT_RADIUS_5_TO_9_HOSTILE_STRESS__UNBOUNDEDNESS_NOT_PROVED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_KERNEL_TOPE_GREEDY_LOCAL_MINIMUM_BARRIER_2026-09-28_v1.0.md`
- `research/R5_E9_KERNEL_TOPE_RAW_RADIUS_2LIFT_AMPLIFIER_2026-09-28_v1.0.md`
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_prime_tower_geometric_tope_radius_stress.py`

Scientific ceiling:

```text
THE CHAMBER GRAPH OF THE SIMPLIFIED PROJECTIVE KERNEL ARRANGEMENT IS THE
CORRECT GEOMETRIC AUGMENTATION METRIC.

A UNIVERSAL CONSTANT ESCAPE RADIUS WOULD GIVE A DETERMINISTIC POLYNOMIAL
DESCENT ALGORITHM FOR THE RATIONAL-KERNEL DEPTH OBJECTIVE.

THE FROZEN PRIME-TOWER CONTROLS FORCE THE REQUIRED RADIUS TO BE AT LEAST 9:
EXACT COMPLETE ARRANGEMENTS GIVE 5 AT n=30,d=2 AND 9 AT n=60,d=3.

THIS DOES NOT PROVE THAT THE REQUIRED RADIUS IS UNBOUNDED.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Simplified projective arrangement

Let `B in Q^{n x d}` be a rational kernel-basis matrix for a square cubic
Exact-One incidence matrix, so every rational kernel vector is `y=B alpha`.
Assume no row of `B` is zero; a zero row is already an UNSAT terminal because a
SAT witness would provide the full-support vector `3x-1`.

Rows of `B` that are nonzero scalar multiples define the same central
hyperplane in coefficient space.  Collapse them to projective classes

```text
H_1,...,H_m.
```

Choose one oriented representative `b_j` for each class. Every original row in
class `j` is

```text
lambda_i b_j, lambda_i != 0.
```

Record only

```text
epsilon_i = sign(lambda_i).
```

A full-dimensional chamber has a projective sign vector

```text
s in {+1,-1}^m,
s_j = sign(b_j dot alpha).
```

The raw sign of original coordinate `i` is `epsilon_i s_j`.

Thus the positive-coordinate objective is a weighted linear objective on the
tope set:

\[
p(s)=\sum_j |\{i\in H_j:\epsilon_i s_j>0\}|.
\]

Equivalently, if

```text
w_j = # {epsilon=+1 in H_j} - # {epsilon=-1 in H_j},
```

then

\[
p(s)=\frac n2+\frac12\sum_j w_j s_j.
\]

The source theorem already proves

```text
p(s) >= n/3
```

for every full-support tope, and SAT iff the lower boundary `n/3` is attained.

## 2. Correct chamber metric

For a real hyperplane arrangement, the chamber/tope graph is a partial cube:
the graph distance between two chambers is exactly the number of distinct
projective hyperplanes separating them.

Hence after simplifying parallel/proportional rows,

```text
d_G(s,t) = Hamming(s,t)
```

on the `m` projective signs.

This is the metric that matters algorithmically. Raw coordinate Hamming
 distance is not invariant under repeated proportional rows and was therefore
correctly separated from this gate by the 2-lift amplifier note.

Classical source binding:
- tope graphs of oriented matroids are partial cubes / isometric subgraphs of
  hypercubes;
- equivalently for realizable arrangements, a segment/gallery between two
  chambers crosses each separating hyperplane once and no nonseparating
  hyperplane is required.

No novelty claim is made for the partial-cube theorem.

## 3. Constant-radius augmentation would be polynomial

Define the **escape radius** of a nonminimum chamber `s` by

\[
r(s)=\min\{d_G(s,t): p(t)<p(s)\}.
\]

Suppose there is a universal constant `R` such that for every source-generated
projective kernel arrangement and every nonminimum chamber,

```text
r(s) <= R.
```

Then one obtains a deterministic polynomial descent algorithm.

### Step A — enumerate the radius-R sign candidates

There are at most

\[
\sum_{q=1}^{R}{m\choose q}=O(m^R)
\]

projective sign vectors at Hamming distance at most `R` from the current tope.

### Step B — exact realizability test is polynomial

For a candidate sign vector `t`, chamber realizability is the strict rational
system

```text
t_j (b_j dot alpha) > 0 for every j.
```

Because the system is homogeneous, strict feasibility is equivalent to
ordinary rational LP feasibility of the scaled system

```text
t_j (b_j dot alpha) >= 1 for every j.
```

Indeed any strict solution has a positive minimum margin and can be scaled to
margin at least one; the converse is immediate.

Thus each candidate can be checked by polynomial-time rational linear
programming.

### Step C — strict progress

If the current chamber is not globally minimum, the radius hypothesis
 guarantees at least one realizable candidate with smaller integer `p`.
Move to such a chamber.

Since

```text
0 <= p <= n,
```

there are at most `n` strict decreases.

Therefore for fixed `R` the total running time is

```text
O(n * m^R * poly(input bit length)),
```

which is polynomial because `m<=n`.

At termination the chamber is globally minimum.  The rational-kernel boundary
theorem then decides SAT by testing whether

```text
p_min = n/3.
```

When equality holds, the Boolean witness is reconstructed directly by

```text
x_i = 1 iff (B alpha)_i > 0.
```

### Meta-theorem PGA-1

A universal constant geometric escape radius for the source-generated
rational-kernel tope objective would therefore supply a deterministic
polynomial exact decision/search algorithm for this Exact-One source route.

This is a conditional algorithm theorem, not evidence that such a constant
exists.

## 4. Why radius one already failed

The frozen SAT control `PG15_SAT_R11` has a genuine projective chamber with

```text
p=6
```

that is a strict geometric local minimum although the SAT boundary has

```text
p=5=n/3.
```

Its nearest boundary chamber is at projective chamber distance four.

Therefore

```text
R=1,2,3
```

are already impossible as universal augmentation radii.

The raw-coordinate 2-lift amplifier does not improve this geometric lower
bound because it duplicates proportional rows without adding projective
hyperplanes.

## 5. Prime-tower hostile carrier

Use the frozen connected cubic UNSAT source from the two-edge exact-UNSAT
linear-nullity prime tower.

The 15-variable seed has

```text
rank_Q(A0)=14
```

and rational kernel generator

```text
g=(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

Its first signed lift uses

```text
F0={(0,12),(2,9)}
```

in 0-based `(row,column)` indexing and the signed-sector kernel generator

```text
z=(-7,-4,3,1,-2,2,-1,-4,6,8,2,-3,-5,1,5).
```

The resulting `n=30` source has the full rational kernel basis

```text
(sym(g), asym(z))
```

and nullity two.

The recursive distinguished pair

```text
F={(0,5),(1,1)}
```

then gives the `n=60` source.  The zero-evaluation subspace at coordinate 5 has
dimension one, and the exact lift basis is

```text
sym(W) plus asym(W0),
```

with total nullity three.

These are already-proved tower identities; the present checker replays the
finite ranks and binds them to complete arrangement enumeration.

## 6. Exact n=30 arrangement

For the `n=30,d=2` stage:

```text
projective hyperplanes = 12
full-dimensional chambers = 24
source depth floor = 10
exact minimum p = 12
```

The arrangement is rank two, so the chamber graph is a cycle.  The checker
exactly sorts the rational critical directions in two affine charts and emits
all 24 topes.

Among its strict non-global local minima, the largest exact escape radius is

\[
\boxed{5}.
\]

Thus any universal constant in PGA-1 must satisfy at least

```text
R >= 5.
```

This instance is UNSAT because its exact minimum `12` remains above the source
boundary `10`.

## 7. Exact n=60 arrangement

For the `n=60,d=3` stage:

```text
projective hyperplanes = 23
full-dimensional chambers = 288
source depth floor = 20
exact minimum p = 24
```

The checker exhausts the complete rank-three central arrangement without
sampling:

1. every chamber closure has an extreme ray;
2. every extreme ray is an intersection of at least two projective
   hyperplanes;
3. for every pair-intersection ray, collect every hyperplane containing it;
4. enumerate the exact rank-two local sectors around that ray;
5. repeat for both orientations of the ray;
6. deduplicate emitted topes and verify the resulting tope graph is connected.

This gives exactly 288 chambers.

Among strict non-global local minima, the largest exact escape radius is

\[
\boxed{9}.
\]

Moreover the checker binds one radius-five stage-30 trap to its duplicated
stage-60 chamber and verifies the amplification

```text
p:      15 -> 30
radius:  5 -> 9.
```

Therefore the current exact lower bound on any universal constant geometric
augmentation radius is

\[
\boxed{R\ge 9}.
\]

The stage remains UNSAT because `24>20`.

## 8. What the 5 -> 9 growth does not prove

It is tempting to infer a recurrence such as

```text
r_(t+1) = 2 r_t - 1.
```

That inference is currently forbidden.

Only two complete tower stages have been exhaustively bound:

```text
n=30,d=2 -> radius 5,
n=60,d=3 -> radius 9.
```

The next frozen tower stages have dimensions

```text
n=120,d=5,
n=240,d=9,
```

and their full arrangements are much larger.  No arbitrary-size theorem yet
proves that a corresponding trap continues to amplify geometrically.

Therefore:

```text
UNBOUNDED GEOMETRIC ESCAPE RADIUS = OPEN.
```

## 9. Sharpened next gate

Freeze

```text
R5_E9_PROJECTIVE_KERNEL_ESCAPE_RADIUS_9_PLUS_GATE_V1
```

A material PASS must do one of:

1. prove a universal constant `R` and give the complete polynomial
   neighborhood-descent algorithm from PGA-1;
2. prove an arbitrary-size source-valid family with escape radius tending to
   infinity, killing all constant-radius augmentation;
3. prove a weaker radius `R(n)` small enough that the resulting exact search is
   still polynomial by some additional source compression;
4. replace chamber augmentation by another exact polynomial contraction with
   witness reconstruction;
5. close the full universal algorithm contract by another route.

Highest-priority hostile continuation:
- analyze the explicit `n=120,d=5` prime-tower chamber obtained by duplicating
  the radius-nine `n=60` trap;
- search first for an exact lower-radius certificate before attempting full
  chamber enumeration;
- if growth persists, derive a symbolic lift recurrence rather than merely
  accumulating finite data.

Forbidden pseudo-progress:
- count raw proportional coordinates as geometric distance;
- infer unbounded radius from only `5 -> 9`;
- use floating-point chamber sampling as an exact certificate;
- enumerate all chambers in unbounded dimension and call that polynomial;
- promote D1 or claim P=NP from this stress result.

## 10. Ceiling

```text
KERNEL DEPTH OBJECTIVE
= WEIGHTED LINEAR OBJECTIVE ON PROJECTIVE TOPES

TOPE GRAPH METRIC
= NUMBER OF SEPARATING PROJECTIVE HYPERPLANES
= HAMMING DISTANCE AFTER SIMPLIFICATION

UNIVERSAL CONSTANT ESCAPE RADIUS R
=> DETERMINISTIC POLYNOMIAL EXACT DESCENT

PG15 SAT CONTROL
= GEOMETRIC ESCAPE DISTANCE 4 TO BOUNDARY

PRIME TOWER n=30,d=2
= 12 PROJECTIVE HYPERPLANES
= 24 CHAMBERS
= MIN p 12 > 10
= MAX NONGLOBAL LOCAL ESCAPE RADIUS 5

PRIME TOWER n=60,d=3
= 23 PROJECTIVE HYPERPLANES
= 288 CHAMBERS
= MIN p 24 > 20
= MAX NONGLOBAL LOCAL ESCAPE RADIUS 9

UNIVERSAL CONSTANT R
>= 9 IF IT EXISTS

UNBOUNDED GEOMETRIC ESCAPE RADIUS
= NOT PROVED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```