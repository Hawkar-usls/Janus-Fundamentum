# R5 E124 — Tutte-12 One-Check Affine-Closure Support Firewall and Nullity-Descent Control

Date: 2026-10-10

Status:
GLOBAL_SUPPORT_LOCAL_AFFINE_CLOSURE_REFUTED_ON_E123
+ UNIFORM_FINITE_NULLITY_DESCENT_OBSERVED

P_VS_NP = OPEN.

## 1. Purpose

E123 rebinds the E64 Tutte-12 / GH(2,2) q=63 carrier as the strongest current
finite post-router negative control:

    connected square/cubic/linear,
    3 | 63,
    rank_Q = 49,
    rational nullity d = 14,
    E18-projective-clean,
    all arbitrary-coordinate KLOC1/KLOC2/KLOC3 tests clean,
    Exact-One UNSAT.

The active solver target is GLOBAL SYMBOLIC SUPPORT CONSTRUCTION: for one
check c, construct the exact three-bit mask of incident variables that extend
to global Exact-One solutions.

E124 applies the complete fixed-point pin / unit-propagation / XOR-contraction /
repeated-component Boolean affine closure to EVERY one-check state of E123.

There are

    63 checks x 3 Exact-One states = 189 branches.

## 2. Exact result: local affine closure rejects none

For every check c and every one of its three candidate selected variables:

1. pin that variable to 1 and the other two variables of c to 0;
2. run Exact-One unit propagation;
3. convert every two-unknown residual clause to x_u xor x_v = 1;
4. contract all XOR components;
5. simplify every ternary constraint with repeated quotient components by its
   exact Boolean truth table;
6. repeat to fixed point.

Result:

    immediate contradiction branches = 0 / 189.

Thus every local one-check state survives the complete currently admitted
affine closure even though E123 has no global Exact-One solution.

Equivalently, affine closure alone returns the apparent support mask

    111

at every one of the 63 checks.

This is a direct firewall against identifying SUPPORT_c solely by local
pin/propagate/XOR/affine contradiction.

## 3. Uniform quotient profile

All 189 surviving branches have exactly the same combinatorial quotient profile:

    unknown original variables = 56,
    XOR quotient components    = 44,
    proper ternary constraints = 48.

The component-size multiset is

    12 components of size 2,
    32 components of size 1.

At fixed point every surviving ternary constraint uses three distinct affine
components; there are no repeated-component constraints left.

So the q63 carrier is not failing because one exceptional pin state was chosen:
the local closure behavior is uniform across the entire one-check support
surface.

## 4. Exact rational quotient rank

For each surviving branch, write every affine literal as

    t_C xor p.

Each proper Exact-One ternary then becomes an integer signed equation

    sum_C a_C t_C = b,

with three nonzero coefficients in {+1,-1}.

The checker performs exact Fraction Gaussian elimination separately on all 189
signed quotient matrices.

For every branch:

    quotient variables = 44,
    rank_Q(M)           = 34,
    affine nullity d'   = 10.

Hence the finite Tutte-12 control exhibits the uniform descent

    d : 14 -> 10

after one one-check pin plus complete affine closure.

The ratio is

    d'/d = 5/7.

This is positive finite evidence for using effective affine nullity as a
recursion potential.

It is NOT a universal shrink theorem.

## 5. Why this matters more than raw quotient size

The earlier affine-closure stress tests showed that the number of surviving
quotient variables need not shrink by a known constant factor. Therefore raw
quotient size cannot currently justify a recurrence

    T(n) <= 3 T(alpha n) + poly(n).

E124 identifies a distinct potential:

    effective rational affine nullity.

If one could prove a universal post-router dichotomy of the form

    either a branch enters an already-certified polynomial terminal,

    or there is a polynomially discoverable check c such that every surviving
    pin branch satisfies

        d' <= alpha d

    for one uniform constant alpha < 1,

    or a certified polynomial separator/decomposition terminal applies,

then

    T(d) <= 3 T(alpha d) + poly(n)

would have only polynomially many recursion nodes because d <= n.

No such theorem is proved here.

## 6. Necessary separator clause

A pure multiplicative-nullity statement cannot be expected without excluding
easy decomposable constructions: disjoint unions or low-interface compositions
can make total nullity arbitrarily large while a pin changes only one
component.

Therefore the meaningful target is not

    EVERY connected instance has multiplicative nullity shrink,

but the stronger router-compatible dichotomy:

    NULLITY-SHRINK OR CERTIFIED DECOMPOSITION.

This must be tested only after the existing E18/E20/E61-E119 router and must
not reintroduce explicit exponential separator tables forbidden by the
general-SAT contraction-state firewalls.

## 7. Updated support-construction target

E124 rules out:

    SUPPORT_c bit = 1
    iff
    pin(c,bit) survives local affine closure.

All three bits survive everywhere on a globally UNSAT carrier.

The next legal question is whether the 10-dimensional signed affine quotient
can be compressed by a GLOBAL symbolic invariant, or whether effective
nullity itself admits the shrink/decomposition dichotomy above.

E123/E124 must now be mandatory negative controls for any proposed
one-check-support constructor.

## Claim boundary

E123_BASE_UNSAT = PRESERVED.
ALL_189_PIN_STATES_SURVIVE_AFFINE_CLOSURE = PROVED_BY_REPLAY.
UNIFORM_QUOTIENT_PROFILE_56_44_48 = PROVED_BY_REPLAY.
ALL_189_SIGNED_QUOTIENT_RANKS = 34.
ALL_189_EFFECTIVE_AFFINE_NULLITIES = 10.
LOCAL_AFFINE_CONTRADICTION_SUPPORT_CONSTRUCTION = REFUTED.
FINITE_NULLITY_DESCENT_14_TO_10 = OBSERVED_AND_REPLAYED.
UNIVERSAL_MULTIPLICATIVE_NULLITY_DESCENT = OPEN.
NULLITY_SHRINK_OR_CERTIFIED_DECOMPOSITION = OPEN.
GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
