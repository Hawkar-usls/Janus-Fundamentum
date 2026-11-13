# R5 E131 — Invertible-Base Fibre-Sum Kernel Theorem and 2-Lift E18 Firewall

Date: 2026-10-10

Status:
PROVED_GENERAL_FIBRE_SUM_OBSTRUCTION
+ EVERY_SINGULAR_2LIFT_OF_INVERTIBLE_BASE_IS_E18_KILLED
+ HIGHER_COVER_ROUTE_REMAINS_OPEN

P_VS_NP = OPEN.

## 1. Context

E129 proves that if A is a rationally invertible square cubic incidence
matrix, then every r-sheet Levi cover is Exact-One UNSAT whenever 3 does not
divide r.

This note rewrites that arithmetic obstruction directly in the homogeneous
rational kernel and identifies an important anti-loop for the E129 seed.

## 2. Fibre-sum theorem

Let L be any r-sheet graph cover of the Levi graph of A.

For a lifted variable vector z, define the base-fibre sum

    s_v = sum_{q=0}^{r-1} z_(v,q).

Sum the r lifted homogeneous equations above one base check c.  Every lifted
base incidence is a perfect matching between the two fibres, so each variable
fibre contributes exactly s_v once.  Therefore

    L z = 0
      =>
    A s = 0.

If A is invertible over Q, then

    s = 0.

Hence every rational kernel vector of the cover obeys, for every base
variable v,

    boxed:
    sum_q z_(v,q) = 0.

This holds for every cover, independently of voltage/signing choices.

## 3. Centered Boolean consequence

An Exact-One witness x corresponds to

    y = 3x - 1 in ker_Q(L) intersect {-1,2}^{nr}.

Fix one base-variable fibre.  If t of its r lifted copies have y=2, then the
fibre sum is

    2t - (r-t) = 3t-r.

The fibre-sum theorem requires

    3t-r=0.

Therefore

    t=r/3.

If 3 does not divide r this is impossible.

So the E129 cover-UNSAT theorem is equivalently the statement that the
kernel has a constant-description fibre-sum obstruction incompatible with the
centered Boolean alphabet.

## 4. Special case r=2: direct E18/KLOC2 obstruction

For a 2-lift,

    z_(v,0)+z_(v,1)=0

for every kernel vector.

Let b_(v,0), b_(v,1) be the two coordinate functionals on a rational kernel
basis.  Then

    b_(v,1) = - b_(v,0).

If b_(v,0)=0, E18 has a zero-coordinate rejection.

Otherwise the two coordinate rows are projectively proportional with ratio

    lambda=-1.

But no pair in {-1,2} satisfies

    y_1 = - y_0.

Thus arbitrary-coordinate KLOC2/E18 rejects every singular 2-lift of a
rationally invertible base.

If the 2-lift has zero rational nullity instead, the existing small-nullity
terminal rejects it immediately.

Therefore:

    boxed:
    NO 2-SHEET COVER OF A RATIONALLY INVERTIBLE BASE CAN BE A POST-E18
    HARD BENCHMARK.

This applies to the frozen E129 q24 lift.

## 5. Frozen E129 seed replay

For the E129 q12 base:

    det(A)=36.

For signing 1934:

    nullity_Q(S)=2.

The q24 2-lift therefore has rational nullity two.

The companion replay constructs its exact rational kernel and verifies for
all twelve base-variable fibres:

    coordinate_row(sheet1) = - coordinate_row(sheet0).

Three base-variable fibres have zero coordinate rows in the frozen basis
representation; all remaining nonzero fibre pairs have ratio -1.

Hence E18/KLOC2 already certifies that this q24 seed is UNSAT.

Its gauge-clean property from E129 remains valid, but it is not an E18-clean
survivor.

## 6. Why higher covers remain live

For r>=4 the fibre-sum equation has arity r.

For a bare sum-zero hyperplane on one fibre, every strict coordinate projection
can be full even though the complete r-coordinate alphabet intersection is
empty when 3 does not divide r.

Thus fixed KLOC3 does not automatically see the r-sheet obstruction once
r>3.

Moreover an iterated 2-lift of the q24 seed has kernel contributions from both
the previous symmetric mode and a new signed antisymmetric mode.  Those extra
coordinates can destroy the sheet-pair projective proportionalities that make
the first 2-lift trivial under E18.

Therefore E131 does NOT close the cover route.

The next admissible finite target is:

    Q48 FOUR-SHEET COVER SURVIVOR

Find a second connected 2-lift of the E129 q24 carrier such that the resulting
4-sheet cover of the invertible q12 base is:

    square/cubic/linear and connected,
    Exact-One UNSAT by the fibre-count theorem,
    rationally singular with nontrivial growing kernel,
    E18 projective-clean after exact preprocessing,
    KLOC3-clean,
    and not gauge-trivial.

If achieved, then iterate and attack width/local-core structure.

## Claim boundary

INVERTIBLE_BASE_COVER_FIBRE_SUM
  = PROVED.

3_NOT_DIVIDE_r_COVER_UNSAT
  = REPROVED IN CENTERED-KERNEL FORM.

EVERY_SINGULAR_2LIFT_E18_KILLED
  = PROVED.

E129_Q24_POST_E18_SURVIVOR
  = NO.

Q48_FOUR_SHEET_POST_E18_KLOC3_SURVIVOR
  = OPEN.

SCALABLE_POST_ROUTER_UNSAT
  = OPEN.

GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION
  = OPEN.

UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER
  = NOT_CONSTRUCTED.

P_VS_NP
  = OPEN.
