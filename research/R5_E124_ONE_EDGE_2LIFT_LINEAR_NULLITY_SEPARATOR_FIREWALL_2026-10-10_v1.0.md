# R5 E124 — One-Edge 2-Lift Linear-Nullity UNSAT Tower / Two-Edge-Separator Firewall

Date: 2026-10-10

Status:
PROVED_SCALABLE_HIGH_NULLITY_UNSAT_TOWER__ROUTED_BY_BALANCED_TWO_EDGE_SEPARATOR

P_VS_NP = OPEN.

## 1. Purpose

E123 rebinds the frozen E64 Tutte-12 / GH(2,2) carrier as a strong finite
post-E18/KLOC3-clean UNSAT benchmark:

    n_0 = 63,
    d_Q(R_0)=14,
    Exact-One UNSAT.

The next benchmark request is asymptotic: obtain a scalable UNSAT family whose
effective rational nullity escapes the O(log n) small-nullity terminal.

A natural construction exists and is exact.

However it immediately exposes a constant balanced edge separator and is
therefore not a post-router hard family.

E124 freezes both facts together to prevent a future high-nullity construction
from being mistaken for universal progress.

## 2. One-edge crossed 2-lift

Let R be any n x n square+cubic Exact-One incidence matrix with

    3 | n.

Choose one incidence edge

    e=(c,v)

such that the Levi graph remains connected after deleting e.

Construct a 2-lift with sheet labels s in {0,1}:

* every incidence edge other than e is parallel:
      (check i,s) -- (variable j,s);

* the two lifts of e are crossed:
      (check c,0) -- (variable v,1),
      (check c,1) -- (variable v,0).

The lifted incidence matrix L has size

    2n x 2n.

A graph cover preserves local degree, and any two distinct lifted checks cannot
share two lifted variables unless their projections already do.

Therefore if R is square+cubic+linear, so is L.

If the base Levi graph is connected and e is not a bridge, then the two copies
of the connected graph G-e are joined by the two crossed lifts of e, so the
lift is connected.

## 3. Exact UNSAT-preservation theorem

Assume the base instance R is Exact-One UNSAT.

Suppose for contradiction that the one-edge crossed lift L has a satisfying
assignment.

For each sheet s define a Boolean assignment x^(s) on the base variables by

    x_v^(s) = value of lifted variable (v,s).

For every base check i != c, all three incidences are parallel. Therefore the
lifted check (i,s) says exactly

    (R x^(s))_i = 1.

So x^(s) satisfies every base check except possibly c.

But 3|n. By the proved one-check redundancy theorem, ANY Boolean assignment
satisfying the other n-1 Exact-One checks automatically satisfies check c as
well.

Hence each x^(s) is a complete Exact-One solution of R.

This contradicts base UNSAT.

Therefore

    boxed:
    BASE UNSAT + 3|n
      =>
    ONE-EDGE CROSSED 2-LIFT UNSAT.

The argument is semantic and does not depend on kernel dimension.

## 4. Rational-kernel decomposition

Order the lifted variables by sheets. The lifted matrix has block form

    L = [[A, B],
         [B, A]]

for suitable n x n matrices A,B with

    A+B = R.

Applying the Hadamard change of basis on the sheet coordinate gives

    L ~ diag(A+B, A-B)
      = diag(R, R^e),

where R^e is obtained from R by changing exactly the selected incidence entry

    +1 -> -1.

Thus over Q

    nullity_Q(L)
      =
    nullity_Q(R) + nullity_Q(R^e).

The signed matrix is a rank-one perturbation:

    R^e = R - 2 E_{cv}.

Hence

    rank(R^e) <= rank(R)+1,

so, writing d=nullity_Q(R),

    nullity_Q(R^e) >= d-1.

Therefore

    boxed:
    d_new >= 2d - 1.

## 5. Recursive tower

Repeat the construction, choosing at each stage a non-bridge incidence edge.

Graph coverings of a bridgeless graph are bridgeless, so the process may be
continued from the bridgeless E64 Tutte-12 base.

Let n_k and d_k be size and rational nullity after k lifts.

Then

    n_{k+1}=2 n_k,

and

    d_{k+1} >= 2d_k-1.

Solving the recurrence gives

    d_k >= (d_0-1) 2^k + 1.

For the E64 base

    n_0=63,
    d_0=14,

so

    d_k >= 13*2^k + 1
        = Omega(n_k).

Thus there is an explicit scalable connected square+cubic+linear UNSAT family
with LINEAR rational nullity.

In particular, high nullity alone cannot be the missing universal obstruction.

## 6. Frozen first lift from E64

Take the frozen E64 Tutte-12 incidence matrix R and choose its first incidence

    e=(0,0)

in the canonical E64 labeling.

The companion checker verifies:

    R[0][0]=1,
    rank_Q(R)=49,
    nullity_Q(R)=14.

After sign-flipping exactly that incidence:

    rank_Q(R^e)=50,
    nullity_Q(R^e)=13.

Therefore the first 2-lift has

    n_1=126,
    d_Q(L)=14+13=27.

This meets the lower bound 2*14-1 with equality.

The checker also constructs the actual 0/1 2-lift and verifies it is:

    square,
    cubic,
    linear,
    connected.

By Section 3 it is Exact-One UNSAT.

## 7. Exact two-edge separator

There are exactly two edges in the lifted Levi graph that cross the sheet
partition: the two lifted copies of e.

Deleting those two edges separates the lifted Levi graph into exactly two
components, each containing one copy of G-e.

For the E64 first lift the checker verifies equal component sizes.

Thus the family has a balanced edge separator of order two at every top-level
lift.

If the recursive construction chooses a non-separator edge inside the inherited
copy structure, the earlier two-edge separators remain available recursively.

So the tower is precisely the kind of scalable high-nullity family that the
existing small-separator / branch-DP routers are designed to exploit.

## 8. Scientific consequence

The construction proves:

    SCALABLE CONNECTED UNSAT
    + d_Q = Omega(n)

can coexist with a polynomially visible constant separator.

Therefore the benchmark target cannot be weakened to

    scalable high-nullity UNSAT.

The real target remains a scalable carrier that simultaneously escapes the
already admitted routers:

    high effective nullity
    AND
    post-E18 clean
    AND
    KLOC3 clean
    AND
    no small balanced separator / low branchwidth route
    AND
    no low normal-span/component route
    AND
    no cube-root/rainbow-Z3 SAT terminal
    AND
    exact UNSAT.

## 9. Relation to GLOBAL SYMBOLIC SUPPORT CONSTRUCTION

E124 does not weaken the main algorithmic target.

The one-check support theorem still asks for a deterministic polynomial
construction of the exact three-bit SUPPORT_c on EVERY carrier.

E124 only shows that one tempting asymptotic negative benchmark family is
already structurally easy for a different admitted router.

This is an anti-loop theorem, not a universal solver.

## Claim boundary

ONE_EDGE_2LIFT_UNSAT_PRESERVATION_FOR_3DIVIDES_N
  = PROVED.

ONE_EDGE_2LIFT_NULLITY_RECURRENCE
  = d_new >= 2d-1.

E64_FIRST_LIFT
  = n=126, d_Q=27.

SCALABLE_LINEAR_NULLITY_UNSAT_TOWER
  = PROVED.

BALANCED_TWO_EDGE_SEPARATOR
  = EXPLICIT.

SCALABLE_POST_ROUTER_UNSAT
  = NOT ACHIEVED.

GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION
  = OPEN.

UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER
  = NOT CONSTRUCTED.

P_VS_NP
  = OPEN.
