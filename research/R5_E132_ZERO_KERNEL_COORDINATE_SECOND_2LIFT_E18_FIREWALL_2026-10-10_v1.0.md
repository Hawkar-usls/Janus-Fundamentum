# R5 E132 — Zero-Kernel-Coordinate Persistence Under a Second 2-Lift

Date: 2026-10-10

Status:
PROVED_ITERATED_2LIFT_E18_FIREWALL
+ DIRECT_NONSPLIT_4COVER_ROUTE_REMAINS_OPEN

P_VS_NP = OPEN.

## 1. Context

E129 supplies a connected q24 2-lift of a rationally invertible q12 base.
E131 proves that every singular 2-lift of an invertible base is already
rejected by E18/KLOC2.  On the frozen E129 q24 lift the rational kernel has
dimension two and six coordinate functionals are identically zero.

A tempting repair is to take a second, differently signed 2-lift, hoping the
new antisymmetric kernel mode fills those zero coordinates and breaks the
first-layer E18 degeneracy.

E132 proves that this cannot work.

## 2. General second-2-lift decomposition

Let R be any square matrix and form an arbitrary 2-lift

    L = [[A,B],
         [B,A]]

with

    A+B=R

and signed block

    S=A-B.

Over Q the Hadamard sheet transform gives

    L ~ diag(R,S).

Therefore

    ker_Q(L) ~= ker_Q(R) direct_sum ker_Q(S).

Choose bases U of ker(R) and V of ker(S).
For one original coordinate i, let

    u_i = its coordinate row in U,
    v_i = its coordinate row in V.

The two lifted copies of coordinate i have kernel-coordinate rows

    b_(i,0) = (u_i,  v_i),
    b_(i,1) = (u_i, -v_i).

## 3. Zero-coordinate persistence firewall

Assume coordinate i is identically zero on ker(R):

    u_i=0.

Then the two lifted coordinate rows are

    (0,v_i)
    and
    (0,-v_i).

There are only two cases.

If

    v_i=0,

both lifted coordinate rows are zero, so E18 has an immediate zero-coordinate
obstruction.

If

    v_i != 0,

the two rows are projectively proportional with ratio

    lambda=-1.

But for centered Boolean values in {-1,2}, the relation

    y_1 = - y_0

has no solution.

Hence E18/KLOC2 rejects this pair.

Therefore:

    boxed:
    IF R HAS EVEN ONE ZERO RATIONAL-KERNEL COORDINATE,
    NO SECOND 2-LIFT OF R CAN BE POST-E18 CLEAN,
    REGARDLESS OF THE SECOND SIGNING.

This is a representation theorem, not an empirical search result.

## 4. Application to E129

The frozen E129 q24 carrier has rational nullity two.

Exact replay gives six zero kernel-coordinate rows, namely both sheet copies of
base variables

    3, 8, 10.

Therefore every possible second 2-lift of that q24 carrier contains, for each
of those coordinates, either:

* two new zero coordinate rows; or
* one projectively proportional lambda=-1 pair.

So the proposed iterated route

    q12 -> q24 -> q48

cannot produce an E18-clean q48 survivor from the frozen E129 seed.

This holds for all second-stage signings, not merely sampled signings.

## 5. What remains open

E132 does NOT rule out arbitrary 4-sheet covers of the original invertible
q12 base.

A direct 4-cover need not factor through the E129 q24 intermediate cover and
need not inherit its six zero kernel-coordinate functionals.

The E131 fibre-sum theorem still gives global UNSAT automatically because

    3 does not divide 4.

Thus the corrected cover target is:

    DIRECT_Q48_FOUR_SHEET_COVER

Find a connected non-factorizing 4-sheet cover of the q12 invertible base whose
rational kernel is nontrivial and which is:

    E18 projective-clean,
    KLOC3-clean,
    free of bounded local UNSAT cores / constant-state decomposition,
    and outside admitted width/normal-span terminals.

Only after such a finite seed exists should a scalable cover tower be pursued.

## Claim boundary

SECOND_2LIFT_ZERO_COORDINATE_FIREWALL
  = PROVED.

E129_ITERATED_Q48_POST_E18_SURVIVOR
  = IMPOSSIBLE.

DIRECT_NONFACTORIZING_4COVER
  = OPEN.

SCALABLE_POST_ROUTER_UNSAT
  = OPEN.

GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION
  = OPEN.

UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER
  = NOT CONSTRUCTED.

P_VS_NP
  = OPEN.
