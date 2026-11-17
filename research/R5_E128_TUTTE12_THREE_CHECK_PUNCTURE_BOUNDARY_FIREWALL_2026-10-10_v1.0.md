# R5 E128 — Tutte-12 Three-Check Puncture Boundary Collapse Firewall

Date: 2026-10-10

Status:
THREE_CHECK_PUNCTURE_IS_SAT_BUT_BOUNDARY_COLLAPSES_TO_TWO_STATES
+ DEGREE_RESTORING_SPLICE_UNSAT_BY_FORCED_OUTER_COUNT

P_VS_NP = OPEN.

## 1. Purpose

E126 shows the E125 one-check splice is not a genuine scalable hard family
because every block retains a constant-size UNSAT core.

A natural repair is to delete more checks from each E64/Tutte-12 block until
the punctured block itself becomes satisfiable, then reconnect the freed
incidences globally.

E128 tests the first exact boundary where this happens.

For the canonical E64 q=63 carrier, delete checks

    {33,34,39}.

These three checks are

    {32,33,61},
    {23,33,34},
    {33,38,39}.

They form a 3-star around central variable 33.

The remaining 60-check block is satisfiable.

However its exact Boolean boundary relation is so rigid that every
degree-restoring 3-uniform splice is immediately UNSAT by counting.

Thus this puncture does not yield the desired scalable post-router hard family.

## 2. Exact punctured-block enumeration

Let R be the frozen E64 Tutte-12 incidence matrix.

Delete rows 33,34,39 and retain the other 60 Exact-One equations.

Exact rational elimination gives

    rank_Q = 48,
    affine free dimension = 15.

The companion checker enumerates all 2^15 assignments to the free coordinates
of the exact RREF affine solution space and reconstructs pivot coordinates.

Result:

    Boolean solutions of the 60 retained checks = 8.

So unlike the E125 one-check puncture, this block is genuinely SAT.

## 3. Seven-variable boundary relation

The deleted checks touch the seven distinct variables

    P = {23,32,33,34,38,39,61}.

Across all eight Boolean solutions of the retained 60 checks, only two
different boundary states occur.

In the ordered port list

    (23,32,33,34,38,39,61)

the exact relation is

    (1,1,0,1,1,1,1),
    (1,1,1,1,1,1,1).

Equivalently:

* the six outer variables
      {23,32,34,38,39,61}
  are forced to 1;
* the central variable 33 is the only free boundary bit.

Thus the entire seven-port relation is just one Boolean degree of freedom.

## 4. Why any degree-restoring splice is immediately UNSAT

Deleting the three checks removes nine incidences per block:

* each of the six outer variables loses one incidence;
* central variable 33 loses all three incidences.

To restore cubicity in a square 3-uniform instance, m punctured blocks must
therefore contribute

    9m

freed variable incidences to exactly

    3m

new three-variable checks.

Any assignment satisfying every punctured block forces all six outer ports of
every block to 1.

Hence, before considering the central variables, the new checks receive

    6m

already-selected incidences.

But Exact-One on 3m new checks permits exactly

    3m

selected incidences in total.

Since

    6m > 3m,

no degree-restoring splice can be satisfied.

This argument is independent of how the nine incidence deficits are wired,
provided each deficit is used once and the replacement constraints are
ordinary three-variable Exact-One checks.

## 5. Algorithmic meaning

The punctured block no longer contains an UNSAT core, so E126's specific
bounded-UNSAT-core objection has been removed.

But the exact boundary relation has constant arity and only two states.
A block can therefore be replaced by a one-bit symbolic interface after its
boundary relation is recognized.

The resulting global UNSAT certificate is then the elementary forced-incidence
count above.

So this construction is still not a genuine hard benchmark.

It merely moves from

    constant UNSAT core

to

    constant-state boundary gadget.

## 6. New benchmark requirement

A valid scalable post-router benchmark should avoid not only bounded UNSAT
cores but also decompositions into repeated constant-size blocks whose exact
boundary relations have polynomially enumerable constant state.

The desired family should therefore have no fixed-block decomposition whose
interfaces remain O(1) while the number of blocks grows.

This is consistent with the general-SAT contraction-state firewalls: global
width must be genuine, not manufactured by wiring many constant semantic
modules.

## Claim boundary

E64_THREE_CHECK_PUNCTURE_ROWS = {33,34,39}.
PUNCTURED_BLOCK_BOOLEAN_SOLUTIONS = 8.
EXACT_SEVEN_PORT_BOUNDARY_STATES = 2.
SIX_OUTER_PORTS_FORCED_ONE = PROVED_BY_EXACT_REPLAY.
ANY_DEGREE_RESTORING_THREE_UNIFORM_SPLICE = UNSAT_BY_COUNTING.
E128_SCALABLE_HARD_FAMILY = REFUTED.
NO_BOUNDED_UNSAT_CORE = NOT_SUFFICIENT.
NO_CONSTANT_STATE_BLOCK_DECOMPOSITION = NEW_REQUIRED_BENCHMARK_GATE.
SCALABLE_POST_ROUTER_UNSAT = OPEN.
GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
