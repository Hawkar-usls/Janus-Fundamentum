# R5 E122 — Post-E18 KLOC3-Clean Small-Nullity UNSAT Counterexample

Date: 2026-10-10

Status:
POST_E18_KLOC3_CLEAN_UNSAT_EXISTS__SMALL_NULLITY_TERMINAL_STILL_APPLIES

P_VS_NP = OPEN.

## 1. Purpose

E121 produced a SAT-admissible connected q=36 square+cubic+linear UNSAT
instance that was clean for every KLOC subset of size at most three, but it
still had 57 projectively proportional rational-kernel coordinate-row pairs.
Therefore E18 equality quotient remained available.

E122 removes that loophole.

It gives an explicit connected q=36 cyclic 3-lift that is simultaneously:

* SAT-admissible: 3 divides n;
* square/cubic/linear and Levi-connected;
* KLOC1/KLOC2/KLOC3 clean on every coordinate subset;
* post-E18 projectively clean: no zero kernel-coordinate row and no
  proportional pair at all;
* Exact-One UNSAT by the exact E58 binary-kernel endpoint test.

However its rational nullity is only three. Therefore it is already covered by
the pre-existing O(2^d poly(n)) small-nullity terminal.

So this is a theorem-level counterexample to the implication

    post-E18 clean + KLOC3 clean + 3|n => SAT,

but it is NOT yet the desired asymptotic high-nullity hard core.

## 2. Base source

Use the frozen E57 n=12 source in row convention

    row i = {i,P[i],Q[i]}

with

    P = [6,3,7,10,11,1,4,8,9,5,2,0]
    Q = [3,4,5,8,7,0,9,6,2,11,1,10].

A primitive rational kernel generator of the base source is

    a = (-1,-1,2,-1,2,2,2,-4,2,-4,-1,2).

## 3. Explicit cyclic 3-lift

Gauge the identity incidence in every base row to voltage zero.

For the P- and Q-incidences use

    (s_P,s_Q) =
    [(2,1),
     (0,1),
     (2,1),
     (2,0),
     (2,2),
     (1,0),
     (2,0),
     (1,1),
     (0,2),
     (2,1),
     (1,0),
     (0,1)].

Thus the lifted row (i,c) uses

    (i,    c),
    (P[i], c+s_P[i]),
    (Q[i], c+s_Q[i])

with copy indices modulo three.

The checker verifies exactly:

    n = 36,
    all row degrees = 3,
    all column degrees = 3,
    pairwise row intersections <= 1,
    Levi graph connected,
    3 | 36.

## 4. Exact rational kernel

Let omega satisfy

    omega^2 + omega + 1 = 0.

The three character blocks of the cyclic lift have exact ranks

    rank A(1)       = 11,
    rank A(omega)   = 11,
    rank A(omega^2) = 11.

Hence

    rank_Q(A_lift) = 33,
    nullity_Q(A_lift) = 3.

A rational kernel-row representation is formed from:

1. the lifted copy-constant base-kernel mode; and
2. the real two-dimensional span of one full-support twisted mode and its
   conjugate.

Every one of the 36 coordinate rows is nonzero.

## 5. E18 projective-clean certificate

For all

    C(36,2) = 630

coordinate-row pairs, exact rational proportionality is tested.

Result:

    proportional pairs = 0.

Thus there are no E18 zero-coordinate certificates and no E18 equality or
complement pairs to quotient.

This is strictly stronger than E121.

## 6. Complete KLOC <=3 replay

For every coordinate subset S of sizes one, two and three, the checker tests

    pi_S(ker_Q A) intersect {-1,2}^S != empty

using exact rational Gaussian elimination.

Counts include all

    C(36,1) + C(36,2) + C(36,3)

subsets.

Result:

    KLOC1 clean,
    KLOC2 clean,
    KLOC3 clean.

There are dependent projected triples, but every such projected plane still
contains at least one {-1,2}^3 corner.

Therefore arbitrary-coordinate KLOC3 gives no UNSAT certificate.

## 7. Exact UNSAT certificate

Over GF(2), the lifted kernel has dimension three.

Its eight codeword weights are exactly

    [0,12,20,20,20,20,20,20].

Hence

    w_max = 20.

For n=36 the exact E58 endpoint is

    2n/3 = 24.

Therefore

    w_max < 24

and E58 proves the lift is Exact-One UNSAT.

This is an exact finite certificate, not a failed search.

## 8. What E122 refutes

E122 proves that the implication

    3|n
    + connected square/cubic/linear
    + E18 projective-clean
    + all KLOC3 coordinate subsets clean
      => Exact-One SAT

is FALSE.

So E18 + fixed KLOC3 is not a complete universal decision rule.

The same result also shows that the first genuine obstruction after E18/KLOC3
need not require projective repetitions.

## 9. Why E122 is not the asymptotic hard core

The rational nullity is

    d_Q = 3.

The already-established rational-kernel terminal solves any instance in

    O(2^d poly(n)).

Thus E122 is polynomially routed immediately by the small-nullity branch.

A genuinely new universal benchmark must strengthen E122 to an infinite or
scalable family with, after every exact E18 quotient,

    d_eff = omega(log n)

(or otherwise beyond every already admitted small-parameter terminal), while
retaining KLOC3 cleanliness and UNSAT.

That strengthened target remains open.

## 10. Updated benchmark target

The previous target

    POST_E18_KLOC3_UNSAT

is now achieved at finite small nullity.

The correct next target is:

    POST_E18_KLOC3_HIGH_EFFECTIVE_NULLITY_UNSAT

Required properties:

    3 | n,
    connected square/cubic/linear,
    no zero or proportional rational-kernel coordinate rows after quotient,
    all KLOC3 coordinate subsets alphabet-compatible,
    effective rational nullity superlogarithmic,
    no already-admitted low-width/low-rank terminal,
    Exact-One UNSAT with an exact certificate.

## Claim boundary

SAT_ADMISSIBLE = YES.
CONNECTED_SQUARE_CUBIC_LINEAR = YES.
RATIONAL_NULLITY = 3.
E18_PROJECTIVE_CLEAN = YES.
E18_PROPORTIONAL_PAIRS = 0.
KLOC1_KLOC2_KLOC3 = CLEAN.
EXACT_ONE = UNSAT.
GF2_KERNEL_MAX_WEIGHT = 20 < 24.
POST_E18_KLOC3_UNSAT = ACHIEVED_AT_SMALL_NULLITY.
POST_E18_KLOC3_HIGH_EFFECTIVE_NULLITY_UNSAT = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
