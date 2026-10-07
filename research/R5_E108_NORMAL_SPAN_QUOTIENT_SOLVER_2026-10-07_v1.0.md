# R5 E108 — Normal-Span Quotient Solver

Date: 2026-10-07

Status:
RANK2_FLAT_AVOIDANCE_FACTORS_THROUGH_THE_SPAN_OF_FLAT_NORMALS

Scientific ceiling:

E108 does not yet prove a universal polynomial ExactOne algorithm.

It proves that the E106 pure rank-2 residual problem has an exact
fixed-parameter quotient: only the span of the active flat normals matters.

If r is the rank of that normal span, the complete residual search needs at
most 2^r states, regardless of the ambient zero-boundary kernel dimension.

P_VS_NP = OPEN.

## 1. Input from E106

After affine unit propagation, the residual domain D is affine and every active
forbidden check fiber has relative codimension exactly two.

Translate D by one base point and write its direction space as U.

Every active check c can be written using two independent linear forms

a_c, b_c in U*

with one forbidden affine value pair.

## 2. Normal span

Define

W = span{a_c,b_c : c active}

and let

r = dim W.

Every active forbidden predicate depends only on the evaluations of forms in W.

Therefore two points x,y in U with

g(x)=g(y) for every g in W

have exactly the same violated-check set.

Equivalently, all constraint information is constant on cosets of

W^perp.

Hence the residual problem factors through the quotient

U / W^perp.

This quotient has exactly

2^r

states.

## 3. Exact algorithmic consequence

Compute a basis of W by Gaussian elimination.

Enumerate all 2^r quotient signatures.

For each quotient state, evaluate all active check predicates.

This decides whether one quotient state avoids every forbidden flat.

Therefore the residual E106 problem is exact fixed-parameter tractable in r.

Since each active rank-2 flat contributes at most two normals,

r <= 2m

for m active flats.

Thus:

* r=O(log n) gives a polynomial exact terminal;
* m=O(log n) gives a polynomial exact terminal;
* constant m gives a constant-size quotient independent of the full kernel
  dimension.

## 4. E107 threshold becomes algorithmically closed

E107 proved that a NO-RAW8 pure rank-2 core needs at least twelve active flats.

At the threshold

m=12,

NO RAW8 forces an exact three-fold affine cover.

Even without using the extra Fourier structure, E108 gives

r<=24,

so the threshold instance is decidable by a constant 2^24-state quotient.

E107's Fourier balance improves this further.

There are twelve rank-two dual lines, each containing three nonzero dual
directions, so there are 36 line-point incidences.

Exact three-fold Fourier balance makes every used nonzero dual direction occur
an even positive number of times.

Therefore there are at most

36/2 = 18

distinct used nonzero dual directions.

Their span has rank at most 18.

Hence the exact threshold NO-RAW8 case has a quotient of at most

2^18

states.

So m=12 is fully inside a polynomial/constant terminal and does not need a
separate universal structural classification for decision.

## 5. E104 replay

The E104/E105 residual domain has

dim D=3

and 18 active rank-2 forbidden flats.

The normal span has full rank three.

The quotient therefore has all eight ambient kernel states.

Exactly four quotient states avoid every forbidden flat, matching exactly the
four raw8 witnesses independently enumerated in E104.

This confirms that the normal-span quotient preserves the nonlinear full-kernel
repair space exactly.

## 6. Solver architecture after E108

The raw8 branch now has the following exact sequence:

1. Build K0 by Gaussian elimination.
2. Build one forbidden affine fiber per ordinary check.
3. E106: propagate rank-0/rank-1 fibers.
4. Form the pure rank-2 residual core.
5. E108: quotient by the span W of all surviving flat normals.
6. Enumerate if r=O(log n).
7. Only if r grows superlogarithmically does the branch remain asymptotically
   hard.

This removes large ambient nullity as a false source of complexity.

The relevant parameter is now the effective normal-span rank r.

## 7. Relation to E17/E53

E17 already warned that raw kernel dimension may consist mostly of local gauge
modes.

E108 supplies the corresponding statement for the raw8 repair CSP:

even a large residual affine domain is harmless when the active forbidden
predicates see only a low-rank normal span.

Thus the correct algorithmic quantity is not

dim K0

but

rank(span of active local restriction normals).

## 8. E109 target

The universal route is now sharply stated.

E109 LARGE-NORMAL-RANK DECOMPOSITION

Assume after E106:

* every active forbidden fiber has codimension two;
* m>=12;
* normal-span rank r is superlogarithmic.

Use the original Tanner incidence geometry to prove one of:

A. the active flat system decomposes into independent low-rank normal-span
   blocks, each handled by E108;
B. a large-rank system yields represented binary-delta modules for E78;
C. large rank forces an avoiding kernel point by expansion / Fourier /
   discrepancy;
D. construct the first exact TARGET6/no-raw8 large-normal-rank obstruction.

A proof of A, B, or C with a polynomial decomposition would close the current
raw8-repair branch algorithmically.

Scientific status:

E108 = EXACT NORMAL-SPAN QUOTIENT SOLVER.
r=O(log n) = POLYNOMIAL TERMINAL.
m=O(log n) = POLYNOMIAL TERMINAL.
E107 THRESHOLD m=12 = CONSTANT-SIZE TERMINAL.
LARGE_NORMAL_RANK PURE_RANK2 CORE = OPEN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
