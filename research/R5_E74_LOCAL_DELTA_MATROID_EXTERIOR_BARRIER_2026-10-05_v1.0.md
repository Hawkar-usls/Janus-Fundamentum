# R5 E74 — Local Delta-Matroid / Exterior Barrier

Date: 2026-10-05

Status:
`LOCAL_SUPPORT_PRESERVING_PROJECTED_LINEAR_OR_MATCHING_COMPILATION_BLOCKED_AT_STAR_C5_AND_FULL_E12_GADGET_SCALES`

Scientific ceiling:

```text
This is a structural impossibility result for a specific LOCAL algebraic route.
It is not an impossibility result for all global determinant/Pfaffian methods,
and it is not a P-vs-NP separation.

P_VS_NP = OPEN.
```

## 1. Why E74 follows E73

E73 localizes the surviving hard atom in the square-cubic Exact-One carrier to
an all-or-none variable star:

```text
Equality_3 = {000,111}
           = degree list {0,3}.
```

The check-side relation is

```text
ExactOne_3 = {100,010,001}.
```

A natural exterior/Pfaffian escape is to replace local constraint fragments by
matching or projected-linear delta-matroid gadgets, because those admit compact
skew-symmetric/rank representations and polynomial algebraic algorithms.

E74 proves that the E12 hard image does not enter that tractable language by
any support-preserving LOCAL contraction at the three natural scales already
present in the R5 ledger.

## 2. Delta-matroid exchange axiom

For a set system `(E,F)`, the symmetric-exchange axiom requires that for every
`X,Y in F` and every `e in X triangle Y`, there exists
`f in X triangle Y` such that

```text
X triangle {e,f} in F.
```

When `e=f`, `{e,f}` is the singleton `{e}`.

Every projected linear delta-matroid is still a delta-matroid.  Koana and
Wahlstrom explicitly use existential projection from a larger linear
delta-matroid and note that the result is a delta-matroid, even though it need
not remain even/linear.  Their STACS 2025 algorithms then exploit compact matrix
representations of this class.

Therefore failure of symmetric exchange is an unconditional support-level
obstruction to representation as a projected linear delta-matroid.

## 3. Scale 0 positive control: ExactOne_3

`ExactOne_3` has feasible subsets

```text
{ {1}, {2}, {3} }.
```

This is exactly the set of bases of the uniform matroid `U_{1,3}`.  Hence it is
a matroid, therefore a delta-matroid.

So E74 does not blame the check side.  The obstruction is on the variable
all-or-none side.

## 4. Scale 1 obstruction: Equality_3

`Equality_3` has feasible family

```text
F = { empty, {1,2,3} }.
```

Take

```text
X = empty,
Y = {1,2,3},
e = 1.
```

For every possible `f in {1,2,3}`:

```text
f=1 -> X triangle {1}       has size 1,
f=2 -> X triangle {1,2}     has size 2,
f=3 -> X triangle {1,3}     has size 2.
```

None is feasible.  Therefore

```text
boxed: Equality_3 is not a delta-matroid.
```

Since twisting/coordinate complementation preserves the delta-matroid class,
no twist repairs this obstruction.

This is already stronger than a bounded local gadget search: it rules out the
entire projected-linear delta-matroid support class for a single Equality_3
star, with arbitrarily many hidden projection coordinates.

It does not rule out weighted cancellations that intentionally change support
after summation.

## 5. Scale 2 obstruction: E63 strong-C5 interface

E63 froze the four-port relation

```text
P5 = {
  0001,
  0010,
  1000,
  1100,
  1111
}.
```

The E74 checker applies the complete symmetric-exchange test and finds a
failure.  Thus

```text
boxed: P5 is not a delta-matroid.
```

So contracting one of the canonical strong-C5 motifs of an E12 gadget does not
move the instance into projected-linear delta-matroid territory.  E63 had
already shown this relation is non-affine; E74 adds the strictly relevant
matching/exterior obstruction.

## 6. Scale 3 obstruction: complete E53 gadget quotient

E53 exactly eliminates all internal elements of one 17-column E12 gadget and
proves that the six boundary ports have only the four states

```text
(a,a,a,b,b,b),  (a,b) in {0,1}^2.
```

Therefore the support is

```text
Equality_3 x Equality_3.
```

It contains both

```text
000000
111000.
```

Taking these as `X,Y` repeats the Equality_3 exchange failure inside the first
three coordinates.  Consequently

```text
boxed: the complete one-gadget E53 quotient is not a delta-matroid.
```

This is the key multi-scale point: even perfect local elimination of the entire
E12 gadget does not produce a projected-linear interface.

## 7. Twists do not help

Delta-matroids are closed under twist, and twist is an involution.  Therefore a
non-delta set system cannot become a delta-matroid merely by complementing a
fixed subset of coordinates.

The checker nevertheless exhausts every twist explicitly for the small frozen
relations:

```text
Equality_3:       2^3  twists,
E63 P5:           2^4  twists,
E53 full quotient:2^6  twists.
```

All remain non-delta.  As a sanity check, all twists of `ExactOne_3` remain
delta-matroids.

## 8. Consequence for matching/Pfaffian compilation

Classical matching-realizable Boolean relations are even delta-matroids, and
projected linear delta-matroids extend the skew-symmetric/matrix framework while
remaining delta-matroids.  Hence a support-preserving local replacement of any
of the three frozen E12 interfaces by such a gadget is impossible.

This sharpens the exterior-algebra frontier:

```text
NOT ENOUGH:
  one-star matching gadget;
  strong-C5 local matching gadget;
  one-E12-gadget projected-linear contraction;
  twists / fixed coordinate complements.

STILL LIVE:
  a genuinely GLOBAL weighted cancellation identity coupling multiple source
  gadgets at once, where intermediate supports need not themselves be
  delta-matroids.
```

That distinction matters.  Hyperpfaffian-style or other higher-order algebra can
use cancellation and is not equivalent to a support-preserving local matching
gadget.  E74 does not claim to rule such global constructions out.

## 9. External anti-loop

### Projected linear delta-matroids

Tomohiro Koana and Magnus Wahlstrom,
"Faster Algorithms on Linear Delta-Matroids",
STACS 2025, LIPIcs 327, Article 62,
DOI `10.4230/LIPIcs.STACS.2025.62`, arXiv:2402.11596.

Relevant point: existential projections of linear delta-matroids are projected
linear delta-matroids and remain delta-matroids; several decision problems over
this class reduce to matrix-rank computations.

### Matching-realizable relations

The matching-realizable relation framework and its connection to even
delta-matroids is developed in the Boolean edge-CSP literature; see also the
appendix discussion in the recent General Factor work below.

### The exact {0,3} obstruction

Shuai Shao and Stanislav Zivny,
"Real-weighted general factors on subcubic graphs",
Mathematical Programming (2026),
DOI `10.1007/s10107-026-02416-3`.

Their subcubic dichotomy singles out the arity-three degree constraint `{0,3}`
as the known NP-hard exceptional constraint when mixed with the other degree
constraints relevant here.  This matches E73's localization exactly.

### Generic higher-order Pfaffian warning

Christian Ikenmeyer and Michael Walter,
"Hyperpfaffians and Geometric Complexity Theory",
arXiv:1912.09389.

They prove the hyperpfaffian VNP-complete.  Thus replacing the ordinary Pfaffian
by a generic higher-order analogue is not a polynomial shortcut.  Any surviving
R5 exterior route has to exploit the exact source alignment rather than generic
3-uniform tensor algebra.

## 10. Replay

Companion checker:

```text
experiments/r5_e74_local_delta_matroid_exterior_barrier.py
```

It derives the E53 quotient from `local_states()` and imports the canonical E63
`P5` relation, rather than copying their conclusions as unverified constants.

It verifies:

```text
ExactOne_3                  DELTA
Equality_3                  NON_DELTA
E63 strong-C5 P5            NON_DELTA
E53 Equality_3 x Equality_3 NON_DELTA
all twists                  preserve the respective status
```

## 11. Next attack

The local route is now narrow enough that the next exterior-algebra experiment
should not search larger one-gadget matchgates.

The first admissible positive target is a **multi-gadget global cancellation**:
find a polynomial-size algebraic state that contracts at least two coupled E12
gadgets while allowing non-delta intermediate support, and then test whether the
state dimension remains polynomial under composition over the actual RXC3
incidence pattern.

A candidate is only useful if all three conditions hold:

```text
1. exact SAT support is preserved globally;
2. representation size remains polynomial under repeated composition;
3. the transition/contraction is polynomial-time and replayable.
```

Anything that merely re-encodes the full `2^q` source quotient is not progress.

Scientific status:

```text
E74 = PROVED LOCAL REPRESENTATION BARRIER.
GLOBAL_SOURCE_ALIGNED_WEIGHTED_CANCELLATION = OPEN.
UNIVERSAL_POLYNOMIAL_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
```
