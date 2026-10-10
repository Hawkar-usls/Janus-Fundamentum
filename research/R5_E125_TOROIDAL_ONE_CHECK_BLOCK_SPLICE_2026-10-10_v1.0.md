# R5 E125 — Toroidal One-Check Block Splice: Scalable High-Nullity / High-Width UNSAT Family

Date: 2026-10-10

Status:
PROVED_RAW_HIGH_NULLITY_HIGH_WIDTH_UNSAT_FIREWALL__CONSTANT_LOCAL_UNSAT_CORE_ROUTER

P_VS_NP = OPEN.

## 1. Purpose

E124 gives a scalable connected UNSAT tower with linear rational nullity, but
its one-edge 2-lift construction exposes a balanced two-edge separator at every
level.

E125 removes that specific weakness.

Starting from the frozen E64 Tutte-12 / GH(2,2) q=63 UNSAT carrier, splice
many copies through exactly one modified check per copy according to an
explicit 3-regular toroidal skeleton.

The result is an explicit infinite family with

    Exact-One UNSAT,
    square+cubic+linear,
    connected,
    rational nullity Omega(n),
    Levi treewidth Omega(sqrt(n)).

Thus scalable high-nullity UNSAT need not come with the constant separator of
the one-edge 2-lift construction.

However this construction is NOT a post-router survivor: the 62 retained local
checks in every E64 block are already UNSAT by one-check redundancy. Therefore
each member contains a constant-size UNSAT subformula. E125 is a firewall
showing that raw nullity and raw Levi width can both be large while the formula
remains locally easy.

## 2. Base authority

Let R be the frozen E64 Tutte-12 incidence matrix.

Exact E64 facts:

    n0 = 63,
    rank_Q(R)=49,
    nullity_Q(R)=14,
    square/cubic/linear,
    Levi-connected,
    Exact-One UNSAT.

Choose one base check c0 such that deleting c0 from the Levi graph leaves the
remaining 125-vertex block core connected. The companion checker verifies this
for the canonical E64 check c0=0.

Let its three incident variables be

    v0,v1,v2.

Because 3 divides 63, the proved one-check redundancy theorem applies:

    any Boolean assignment satisfying the other 62 base checks
    automatically satisfies c0.

Since R is UNSAT, there is therefore no Boolean assignment satisfying those
62 checks.

This is the semantic engine of the splice.

## 3. Explicit toroidal skeleton

For integer t>=2 define a bipartite 3-regular graph H_t with

    L = R = Z_t x Z_t.

For each left vertex (i,j), connect it to the three right vertices

    (i,j),
    (i+1,j),
    (i,j+1)

with indices modulo t.

For t>=2 these three neighbors are distinct, so H_t is simple and 3-regular.

For t>=3, contracting every matching edge

    L(i,j) -- R(i,j)

produces the toroidal grid

    C_t square C_t.

Hence

    tw(H_t) >= tw(C_t square C_t) >= t.

## 4. One-check block splice

Create one copy of the 63 base VARIABLES for every left skeleton vertex
h=(i,j).

Inside each copy retain the 62 base checks other than c0.

Do NOT retain its original c0 check.

Instead create one cross-check for every right skeleton vertex r=(i,j).

Assign the three deleted c0 ports of left block (i,j) as follows:

    v0 -> right check (i,j),
    v1 -> right check (i+1,j),
    v2 -> right check (i,j+1).

Equivalently the cross-check at right vertex (i,j) uses

    v0 from left block (i,j),
    v1 from left block (i-1,j),
    v2 from left block (i,j-1).

Thus every cross-check again has exactly three variables.

Let M_t be the resulting incidence matrix.

There are

    m=t^2

left blocks.

Variables:

    63m.

Checks:

    62m + m = 63m.

Therefore M_t is square.

## 5. Cubicity and linearity

A base variable not incident with c0 keeps all three local incidences.

Each of v0,v1,v2 loses its one incidence with the deleted local c0 and gains
exactly one incidence with a cross-check.

Hence every variable still has degree three.

Every retained local check has degree three and every cross-check has degree
three.

For linearity:

* two retained local checks obey base linearity;
* retained checks in distinct blocks are disjoint;
* a cross-check contains at most one variable from any left block, so it can
  meet any retained local check in at most one variable;
* distinct cross-checks use distinct deleted-port endpoints, so they share no
  variable.

Thus M_t is square+cubic+linear.

## 6. Connectedness

Delete c0 from one base Levi block. The companion checker verifies the remaining
block core is connected and contains every base variable.

Contract each such core in the global Levi graph to one left supervertex.

Keep every cross-check as a right vertex.

The resulting minor is exactly H_t.

Since H_t is connected, the full E125 Levi graph is connected.

## 7. Exact UNSAT theorem

Suppose M_t had a satisfying Boolean assignment.

Fix any left block h.

All 62 retained local checks of h are unchanged E64 checks and involve only
variables of that block.

Therefore the restriction to the 63 variables of h satisfies every original
E64 check except possibly c0.

Because 3|63, one-check redundancy forces the deleted original c0 equation as
well.

So the restriction would be a complete Exact-One solution of the E64 q63
carrier.

But E64 is UNSAT.

Contradiction.

Therefore

    boxed:
    M_t is Exact-One UNSAT for every t>=2.

The proof is block-local and does not depend on how the cross-check values
behave.

## 8. Linear rational-nullity lower bound

Let D_t be the block diagonal matrix containing m=t^2 copies of R.

Then

    rank_Q(D_t)=49m,
    nullity_Q(D_t)=14m.

Order the rows of M_t so that each new cross-check replaces one deleted c0 row
position.

The difference

    Delta_t = M_t - D_t

has nonzero entries in at most m rows.

Therefore

    rank_Q(Delta_t) <= m.

By rank subadditivity,

    rank_Q(M_t)
      <= rank_Q(D_t) + rank_Q(Delta_t)
      <= 49m + m
      = 50m.

Since M_t has 63m columns,

    nullity_Q(M_t) >= 63m-50m = 13m.

Thus

    boxed:
    nullity_Q(M_t) >= 13 t^2 = (13/63) n = Omega(n).

So the small-nullity O(2^d poly(n)) branch is asymptotically unavailable.

## 9. Growing width

As proved in Section 6, H_t is a minor of the E125 Levi graph.

For t>=3, C_t square C_t is a minor of H_t.

The toroidal grid contains the ordinary t by t grid as a subgraph after
deleting wrap edges, so its treewidth is at least t.

By minor monotonicity,

    boxed:
    tw(Levi(M_t)) >= t.

Since

    n=63 t^2,

this is

    tw = Omega(sqrt(n)).

Therefore E125 is not routed by the constant-separator defect that killed E124,
nor by any claimed universal O(sqrt(log n)) width bound.

## 10. Constant local UNSAT core

The same semantic proof of Section 7 gives a stronger anti-overclaim fact.

For every left block, the 62 retained E64 checks involve only that block's 63
variables. Any Boolean assignment satisfying those 62 checks would, by
one-check redundancy, also satisfy the deleted E64 check c0 and hence solve the
frozen E64 base.

Therefore those 62 retained checks alone are UNSAT.

So every E125 instance contains an UNSAT subformula of constant size
independent of t.

Consequently E125 is NOT a candidate SCALABLE_POST_ROUTER_UNSAT family even
before E18/KLOC3/normal-span testing. A polynomial router may detect the frozen
local obstruction once and reuse it.

The correct use of E125 is narrower:

    large rational nullity + growing raw Levi treewidth
    do not by themselves imply a globally hard support relation.

A genuine scalable benchmark must ensure that every bounded-size induced/local
region remains extendible while global UNSAT survives.

## 11. Scientific consequence

E124 showed

    high nullity + UNSAT

can hide behind a constant separator.

E125 proves that this is not forced:

    high nullity + UNSAT + growing raw structural width

can coexist in an explicit connected square+cubic+linear family.

But the same family is locally trivial through a constant 62-check UNSAT core.

Therefore the next benchmark must add a LOCAL-EXTENDIBILITY requirement:
bounded-size regions must not already certify UNSAT.

## Claim boundary

SCALABLE_UNSAT_FAMILY
  = PROVED.

CONNECTED_SQUARE_CUBIC_LINEAR
  = PROVED.

RATIONAL_NULLITY
  >= 13 t^2 = Omega(n).

RAW_LEVI_TREEWIDTH
  >= t = Omega(sqrt(n)).

CONSTANT_SEPARATOR_FIREWALL_FROM_E124
  = REMOVED.

CONSTANT_LOCAL_UNSAT_CORE
  = PRESENT (62 retained checks per block).

POST_ROUTER_SURVIVOR
  = NO.

SCALABLE_POST_ROUTER_UNSAT
  = OPEN.

GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION
  = OPEN.

UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER
  = NOT CONSTRUCTED.

P_VS_NP
  = OPEN.
