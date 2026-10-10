# Universal Polynomial-Solver Attack: Degree-2 SoS Moment Projector, R vs R^T

Date: 2026-10-10
Source authority: Hawkar-usls/Janus-Fundamentum PR #515;
pre-existing E64 q63 generalized hexagon, E65 transpose asymmetry,
**E68 degree-2 SDP transpose firewall (original authority for the SDP
incompleteness finding)**, and E123 post-E18/KLOC3 controls. New runnable witness:
`experiments/r5_universal_degree2_moment_projector_attack.py`.

STATUS = EXACT_INTEGER_PROJECTOR_REPRODUCTION_AND_STRONGER_MOMENT_DETAILS.
ANTI-DUPLICATION: E68 ALREADY PROVED the basic R/R^T level-1 SDP
counterexample; do NOT count that basic conclusion as a new theorem.
What is newly checked here: integer shell projector H^2=36H,
all local pair moments, genuine SAT transpose pair-counts from all 36
Boolean models, and the link to 189 conditional first moments.
UNIVERSAL_POLYNOMIAL_SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.

## 1. Universal candidate actually being tested

A proposed deterministic algorithm could solve the Boolean Exact-One CSP
by a polynomial-size second-moment semidefinite relaxation instead of
explicit branching or coefficient extraction.

For every legal square, cubic, C4-free incidence matrix A define the
following first and second moments for formal Boolean variables x:

    mu_i = E[x_i],
    M_ij = E[x_i x_j],
    B = [[1, mu^T],
         [mu, M]] >= 0.

Necessary for a true distribution supported on satisfying assignments:

    A mu = 1,
    M_ii = mu_i,
    M_ij = 0 if variables i!=j occur together in an Exact-One check,
    A M = 1 mu^T.

The moment matrix is positive semidefinite (PSD) for every actual
probability distribution over satisfying Boolean witnesses. These
constraints constitute a strong version of level-1/degree-2
Boolean/Exact-One moment consistency. Any SAT solution yields an
obvious rank-one feasible B; therefore SDP infeasibility is a SOUND
UNSAT criterion.

If this polynomial-size SDP relaxation were also complete for every
square/cubic/linear instance, it could support a polynomial solver
subject to rigorous SDP decision bit-complexity and witness recovery.
**That proposed completeness theorem is false, as already established by E68.**

## 2. Exact rational pseudo-moment matrix on UNSAT E123

Let R be the E64/E123 q63 UNSAT orientation of the Tutte 12-cage
generalized hexagon (2,2). On its **variable** side, let d(i,j)
denote the even distance in the bipartite Levi graph.

The distance shell populations around each variable are

    distance:  0   2   4   6
    count:     1   6  24  32.

Define a 63 x 63 **integer** matrix H by

    d(i,j):      0   2   4   6
    H_ij:        8  -4   2  -1.

The checker verifies exact integer identities, for every entry,

    H = H^T,
    H 1 = 0,
    R H = 0,
    H^2 = 36 H,
    tr(H) = 63*8 = 504.

Consequently P = H/36 is a **symmetric idempotent** and therefore an
orthogonal projector, P >= 0, with rank 504/36=14.
Because R P=0 and E64 proves dim ker_Q(R)=14,
P is exactly the orthogonal projector onto ker_Q(R).

Set

    mu = (1/3) * 1,
    M = mu mu^T + P = (J*4 + H)/36.

Then the full moment block B is PSD by its Schur complement
M - mu mu^T = P >=0. Entrywise:

    d(i,j):   0     2     4     6
    M_ij:    1/3    0    1/6   1/12.

All Boolean degree-2 constraints hold:

* R mu=1 because R1=3*1.
* M_ii=mu_i=1/3.
* Adjacent variables (sharing a source check) have d=2, so
  M_ij=0.
* R M = 1 mu^T, since R H=0 and R J=3J.
* For every check c, E[(sum_{j in c} x_j-1)^2]=0, since its
  three diagonal moments sum to 1 and its three offdiagonal
  pairs have moment 0.

But E64/E65/E123 independently certify R is Boolean UNSAT:
ker_F2(R) has dimension14, maximum weight40, while Exact-One would
require a kernel word of weight2*63/3=42.

This reproduces E68's basic SDP obstruction with a new compact
integer-squared projector and explicit local Boolean pair identities.
The degree-2 moment SDP is not a universal decision oracle (E68).

No floating eigenvalue computations, external SDP solver,
randomized search or approximate rational reconstruction are used
for this assertion. H^2=36H and RH=0 are independently checked
over the integers.

## 3. The transpose has identical shell moments from REAL solutions

Let T=R^T. E65 proves that T has exactly 36 genuine Boolean
Exact-One solutions (and R has none). Rebuild the Levi distance
matrix on T's variable side. Its 63-variable association scheme has
the same shell cardinalities and satisfies the same integer projector
identities.

Enumerate all 36 SAT witness bitvectors of T from its exact GF2
coset. For *every* ordered variable pair (i,j), count the actual
witnesses selecting both variables:

    d(i,j):                   0   2   4   6
    number among 36 models:   12  0   6   3.

Thus the **actual** moments for the SAT transpose are *exactly*
M^T_ij = 1/3,0,1/6,1/12 depending on the distance.

On the UNSAT orientation R the same distance-shell formula yields
only a consistent *pseudo* distribution, not a real one.

Warning: this is equality of the distance-class moment **profiles**,
not equality of two matrices under an arbitrary fixed labeling,
and it does not rule out algorithms using the entire oriented graph
or higher-degree signatures.

## 4. Previously observed 189 pinned LP solutions are its marginals

For a variable j, the formal conditional first moment
M_ij / mu_j = 3 M_ij has exactly the distance-shell values

    distance:       0   2   4   6
    conditional:    1   0  1/2 1/4.

These are exactly the 63 fractional global solutions previously
independently constructed by the LP-distance-shell checker.
Every j is in three clauses, so all 189 first-check pin choices are
LP-feasible even though there is no Boolean witness.

Important distinction: the conditional first moments are feasible
LP vectors. We have NOT claimed to construct a valid degree-2
moment SDP on the pinned residual formula by conditioning B;
such a claim would require third/fourth moments.

## 5. What is actually missing for a universal polynomial algorithm

The complete problem still requires polynomial-time construction of
a Boolean witness or a correct unsatisfiability decision for **every**
instance. Feasibility at moment degree 2 is not enough.

A route using semidefinite moment hierarchies would need a theorem
that some universally polynomial-size, polynomial-bit constructible
level or *other* symbolic invariant is sound AND complete and permits
polynomial-time witness extraction. No such theorem has been proved.

Higher hierarchy levels may separate this finite example.
One finite example does NOT imply that *every* level or every
positive semidefinite algorithm requires superpolynomial work.

This establishes a concrete exact obstruction, not a new polynomial
terminal or a claim of P=NP.

## 6. Reproducibility

    python experiments/r5_universal_degree2_moment_projector_attack.py

Executable checks: E123 independent GF2 UNSAT, 63x63 exact integer
AH=0, H^2=36H, moment identities, 189 pinned LP conditional marginals,
R^T independent 36 Boolean SAT models, and **every** transpose
pair-count = 4 + H_ij at distance d(i,j).

Only fixed fixture enumeration establishes the 36/0 witness counts;
the moment PSD identity is an exact constructive certificate.

## Claim ledger

EXACT_UNSAT_E123_PSEUDOMOMENT = E68 PREDECESSOR; INDEPENDENT INTEGER REPLAY.
H_OVER_36_IS_ORTHOGONAL_KERNEL_PROJECTOR = PROVED.
DISTANCE_SHELL_MOMENTS_OF_R_AND_RT = EXACTLY_EQUAL_PROFILES.
REAL_36_WITNESS_TRANSPOSE_PAIR_COUNTS = PROVED_BY_ENUMERATION.
PREVIOUS_189_PINNED_LP_VECTORS_ARE_CONDITIONAL_FIRST_MOMENTS = PROVED.
DEGREE2_MOMENT_SDP_IS_COMPLETE_FOR_ALL_SCL = ALREADY REFUTED IN E68.
UNIVERSAL_POLYNOMIAL_SDP_HIERARCHY = NOT ESTABLISHED.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.
