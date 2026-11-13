# R5 E129 — Invertible-Base Cover UNSAT Theorem and Gauge-Clean q12 2-Lift Seed

Date: 2026-10-10

Status:
PROVED_COVER_UNSAT_ARITHMETIC_THEOREM
+ CONNECTED_GAUGE_CLEAN_SINGULAR_2LIFT_SEED
+ SCALABLE_POST_ROUTER_FAMILY_STILL_OPEN

P_VS_NP = OPEN.

## 1. Purpose

E126/E128 show that simply wiring copies of the E64 UNSAT block can leave
either a bounded UNSAT core or a constant-state boundary gadget.

E129 takes a different route.

Instead of preserving UNSAT because a finite block is already contradictory,
preserve UNSAT through a global fibre-count obstruction that holds for every
graph cover of a rationally invertible cubic base.

Then choose a non-balanced signing whose connected 2-lift already creates
nonzero rational kernel while avoiding any fibre gauge in which a purely
parallel set of base checks is itself UNSAT.

This is a seed for a genuinely distributed cover construction. It is not yet
the final scalable post-router family.

## 2. General invertible-base cover theorem

Let A be any square 0/1 incidence matrix with every row and column of weight 3.

Assume A is invertible over Q.

Let L be an r-sheet graph cover of the bipartite Levi graph of A: every base
incidence (c,v) is lifted to a perfect matching between the r copies of c and
the r copies of v.

Suppose L had an Exact-One assignment.

For each base variable v define the fibre count

    y_v = number of selected lifted copies of v.

Then y_v is an integer in {0,...,r}.

Sum the r lifted Exact-One equations above one base check c. Because each
lifted base incidence is a perfect matching, the contribution from the fibre of
variable v is exactly y_v.

Therefore

    A y = r * 1.

But cubicity gives

    A 1 = 3 * 1.

Since A is invertible over Q, the unique rational solution is

    y = (r/3) * 1.

If 3 does not divide r, this vector is not integral.

Contradiction.

Hence

    boxed:
    A invertible over Q and 3 not dividing r
      => every r-sheet Levi cover is Exact-One UNSAT.

This theorem is independent of the voltage/signing pattern and introduces no
bounded local UNSAT block.

## 3. Explicit q12 base

Use row convention

    row i = {i,P[i],Q[i]}

with

    P = [4,6,11,2,5,7,8,1,9,0,3,10]

    Q = [7,9,1,6,2,3,0,10,11,5,8,4].

The checker verifies:

    n=12,
    square,
    cubic,
    linear/C4-free,
    Levi-connected.

Exact Bareiss elimination gives

    det(A)=36.

Thus A is rationally invertible and therefore Exact-One UNSAT.

Over GF(2),

    rank_2(A)=10,
    nullity_2(A)=2.

So this base is rationally rigid while already carrying a nontrivial binary
endpoint code.

## 4. Switching-class search for a singular connected 2-lift

The q12 Levi graph has

    E=36,
    V=24,

so its signing space modulo row/column switching has dimension

    E-V+1 = 13.

There are exactly

    2^13 = 8192

switching classes.

A complete finite search found many non-balanced classes whose signed incidence
matrix is singular.

The frozen class used here is the canonical cotree bit mask

    1934.

In the deterministic spanning-tree gauge of the checker, its negative
incidences are:

    (check 1, variable 9)
    (check 2, variable 11)
    (check 2, variable 1)
    (check 5, variable 5)
    (check 7, variable 10)
    (check 8, variable 9)
    (check 8, variable 11)

The corresponding signed q12 matrix S has exact rational rank

    rank_Q(S)=10,

hence

    nullity_Q(S)=2.

Because the signing is non-balanced, the associated 2-lift is connected.

By the standard Hadamard decomposition of a 2-lift,

    rank/nullity(L)
      = rank/nullity(A) + rank/nullity(S)

over Q, so the connected 24-variable lift has

    nullity_Q(L)=2.

The checker independently verifies this directly.

## 5. Exact UNSAT of the first lift

The first lift is a 2-sheet cover of the invertible q12 base.

Since

    3 does not divide 2,

the general fibre-count theorem already proves it UNSAT.

The checker also independently enumerates its two-dimensional rational kernel
and finds

    ker_Q(L) intersect {-1,2}^24 = empty.

Thus the finite seed has an exact replayed UNSAT certificate.

## 6. Gauge-clean parallel-core test

A cover built from a signing must not be mistaken for progress if some fibre
relabeling exposes an unchanged UNSAT copy of a bounded base subformula.

Row/column switching of the signed base matrix is exactly independent swapping
of the two sheet labels in check/variable fibres.

Fix any assignment of signs to the 12 variable fibres.

For each base check, ask whether its three signed incidences become equal. If
they do, a check-fibre relabeling can make that base check completely parallel
inside the two sheets.

Let U be the set of all such parallelizable base checks.

The checker exhausts all

    2^12 = 4096

variable-fibre gauges.

For the frozen signing 1934:

    every resulting U is Exact-One satisfiable as a base row subset.

Moreover:

    maximum number of simultaneously parallel base checks = 7,
    minimum number of genuinely affected checks = 5.

Therefore no fibre gauge exposes a purely parallel UNSAT base-row subset.

This specifically removes the hidden-copy-core defect that invalidated the
first q12 signing tried during the search and the block-copy defect of E125.

It does NOT prove absence of every possible bounded UNSAT subformula in the
24-variable lift; it proves the stated gauge-invariant parallel-copy criterion.

## 7. Why this seed matters

E129 gives three ingredients simultaneously:

1. global UNSAT preserved under arbitrary covers of degree not divisible by 3;
2. a connected 2-lift that creates nonzero rational kernel;
3. no sheet gauge exposing a parallel UNSAT subset of the q12 base.

This makes iterated irregular covers a live route to the scalable benchmark.

A future tower must still prove, asymptotically:

    effective nullity beyond O(log n),
    no bounded UNSAT core of any form,
    E18-cleanliness,
    KLOC3-cleanliness,
    no constant-state block decomposition,
    no admitted normal-span/component/branchwidth terminal.

## 8. Active next theorem target

The immediate construction target is now:

    DISTRIBUTED COVER NULLITY / WIDTH THEOREM

Build iterated covers of the q12 seed such that:

    cover degree remains not divisible by 3,
    rational nullity grows superlogarithmically,
    signing distance from every switching-trivial class grows,
    no bounded local contradiction is inherited,
    global width escapes admitted polynomial routers.

The general cover-UNSAT theorem then supplies exact UNSAT automatically.

## Claim boundary

Q12_BASE_DET = 36.
Q12_BASE_RATIONAL_INVERTIBLE = YES.
Q12_BASE_GF2_NULLITY = 2.
ARBITRARY_R_SHEET_COVER_UNSAT_IF_3_NOT_DIVIDE_R = PROVED.
FROZEN_2LIFT_SIGNING = 1934.
SIGNED_Q12_NULLITY = 2.
FIRST_2LIFT_CONNECTED = YES.
FIRST_2LIFT_RATIONAL_NULLITY = 2.
FIRST_2LIFT_EXACT_ONE = UNSAT.
PARALLEL_BASE_CORE_IN_ANY_FIBRE_GAUGE = ABSENT.
SCALABLE_POST_ROUTER_UNSAT = OPEN.
GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
