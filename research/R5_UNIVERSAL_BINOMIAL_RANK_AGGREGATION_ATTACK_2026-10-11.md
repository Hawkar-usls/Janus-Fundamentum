# Universal Solver Attack: Top-Shell Binomial Indicator -> Exact GF(2) Projection-Rank Aggregator

Date: 2026-10-11
Research branch: `research/parity-isolation-trade-checkpoint-20261009`, PR #515.
Predecessor authorities: E56/E58, E61 two-level/Hoffman, E65 parity-defect
quantization, E67/E68 MacWilliams/Krawtchouk moment firewalls, E70
rank/nullity envelope, E118 NP-hardness-preserving reduction, and
`research/R5_UNIVERSAL_SUPPORT_COEFFICIENT_EXTRACTION_ATTACK_2026-10-10.md`.

**Scientific status: mathematical identity and exact executable checks,
NOT a universal polynomial-time algorithm.** Do not promote to P=NP proof.

## I. General top-shell weight bound and exact indicator

Let A be an n x n {0,1} matrix with exactly three ones in each
row and column, and n=3m.  The linearity/C4-free promise is permitted,
but the algebraic identities in this section do not need it.

Define K = ker_{F2}(A), d=dim(K).  Since A*1=1 over F2,
every GF2 parity solution of Ax=1 is x=1+k with k in K.

For each k in K, let w=|k|. Each INTEGER row sum of Ak is 0 or 2.
Since every selected column contributes three incidences,

    3w = 2 * (# rows having integer Ak row sum 2) <= 2n=6m.

Therefore w is an even integer and 0<=w<=2m.

If w=2m then every row has integer Ak row sum 2.
The Boolean complement x=1-k has every row sum exactly 1.
Conversely, every Exact-One solution x has |x|=n/3=m,
so k=1-x has weight 2m.  Thus

    Z(A) := number of Boolean Exact-One solutions
          = sum_{k in K} indicator(|k|=2m)
          = sum_{k in K} binom(|k|/2,m).

The polynomial

    q_m(w)=binom(w/2,m)
          = [product_{j=0}^{m-1}(w-2j)]/(2^m m!)

is exactly 0 at w=0,2,...,2m-2 and exactly 1 at w=2m.

This uses an orientation-sensitive kernel, so it does NOT conflict
with E65's SAT transpose vs UNSAT orientation.

This binomial indicator is a uniform exact arithmetic substitute for
explicitly comparing every enumerated Hamming weight. By itself,
the sum still has 2^d terms; no complexity improvement is claimed.

## II. Convert top-shell count to projection-rank aggregates

Any degree-m polynomial f(w) has a unique Newton expansion
f(w)=sum_{s=0}^m c_s binom(w,s), where

    c_s = (Delta^s f)(0)
        = sum_{j=0}^s (-1)^(s-j) * binom(s,j) * f(j).

Use f(w)=binom(w/2,m).  Then

    Z(A) = sum_{s=0}^m c_s B_s(A),

    B_s(A) := sum_{k in K} binom(|k|,s)
            = sum_{S subseteq [n], |S|=s}
                #{k in K: k_i=1 for all i in S}.

Every summand is a **single exact GF2 rank calculation**, no
search through kernel words. Pick any n x d binary kernel generator B
such that k=B t for t in F2^d. Let B_S denote its rows indexed by S.
The number of t satisfying B_S t = 1_S is

       0                 when the system is inconsistent,
       2^(d-rank(B_S))    when consistent.

This calculation uses Gaussian elimination, has polynomial total
bit complexity for ONE specified S, and the count uses at most n+1 bits.

Consequently the entire Exact-One count can be expressed as an
explicit signed rational linear combination of exact polynomial-time
rank observations. All coefficients c_s have polynomial-size
numerators and denominators (m=O(n)).

**Integer-only stronger form (no rational coefficients):**
let D_m=2^m m! and a_s=D_m c_s. Every a_s is an integer,
as it is the s-th finite difference of the integer-coefficient
polynomial

    F_m(w) = product_{j=0}^{m-1}(w-2j).

Then the exact identity is

    D_m * Z(A,pi) = sum_{s=0}^m a_s * B_s(A,pi).

For m=4 (n=12), an explicit one-line exact formula is

    384 * Z = -15 B_1 + 30 B_2 - 36 B_3 + 24 B_4,

with B_s the *pinned or unpinned* rank moments.
These integer coefficients are checked independently by the executable
replay. In general D_m and all a_s require only O(n log n) bits.
The final scalar is a NONNEGATIVE integer multiple of D_m, despite
signed intermediate cancellations. This avoids any hidden
rational-precision requirement; it does not avoid subset explosion.

The computational obstruction is **not** a single difficult rank,
the integer size of Z(A), or calculating the coefficients c_s.
It is **combining the ranks over exponentially many coordinate sets**.

## III. The precise required constructive theorem for this route

Define an affine pin assignment pi on some x coordinates. Because
x_i=1+k_i in F2, the equivalent kernel pin is k_i=1-x_i.

Define

    B_s(A,pi) =
      sum_{S subseteq [n], |S|=s}
        #{k in K:
          k obeys pi and k_i=1 for all i in S}.

Each summand remains a single polynomial-time affine GF2
linear-system rank and consistency check. The same polynomial
indicator applies because every pinned k still lies in K.

    Z(A,pi) = sum_{s=0}^m c_s B_s(A,pi),

where Z(A,pi) counts all genuine Exact-One solutions extending pi.

**Sufficient, not proved, global theorem:**

    UNIVERSAL_PROJECTED_RANK_MOMENT_AGGREGATION

For every square+cubic+linear A, n=3m, and every partial Boolean pin
pi, compute the *single combined scalar*

    RANK_AGG(A,pi) = sum_{s=0}^m c_s B_s(A,pi)

exactly (or merely its positive/zero status) in deterministic
poly(n) worst-case BIT operations, without enumerating coordinate
subsets, boundary states or parity-kernel words, and without hiding
exponential precision.

If proved, a deterministic polynomial-time SolveLinearCubicXSAT
follows: query RANK_AGG(A,empty). If zero output UNSAT. If positive,
for j=1..n query RANK_AGG(A,pi together with x_j=0). If nonzero
fix x_j=0; otherwise fix x_j=1. By induction the remaining feasible
count stays positive. Verify Ax=1 and output the witness.

This takes <=n+1 oracle calls, O(n^2) pin representation,
plus straightforward polynomial overhead. Output count
Z(A,pi) <= binom(n,m) <= 2^n, so the desired exact result has O(n)
bits. If the rank-aggregate theorem held with poly(n) bit cost,
soundness, completeness and polynomial total bit complexity would
follow. The theorem is presently **unproved**. E118's NP-hardness
means it would be a genuine P=NP breakthrough, not a routine
application of Gaussian elimination.

This theorem is **a sufficient route**, not a necessary condition
for every conceivable general algorithm. Alternative algorithms
can avoid the explicit rank moments entirely.

## IV. Quantitative size of direct aggregation

The straightforward implementation calls the rank counter for

    M(n) = sum_{s=0}^{n/3} binom(n,s)

coordinate subsets, each individually polynomial-time.

For the checked and prospective problem sizes:

    n=12:  794
    n=30:  53,009,102
    n=63:  51,380,672,802,765,632
    n=90:  1,275,242,689,014,875,290,400,960

Stirling's approximation yields

    binom(n,n/3) = 2^((H_2(1/3)+o(1))*n)
                 = 2^((0.918295834...+o(1))*n),

with H_2(p)=-p log2 p-(1-p)log2(1-p).
Thus naive rank-subset enumeration remains exponentially expensive.

The polynomial q_m(w) has degree EXACTLY m because it has m
distinct roots at w=0,2,...,2m-2 and is nonzero at w=2m.
Therefore any polynomial that equals the exact top-weight
indicator on the FULL abstract grid {0,2,...,2m} must have degree
at least m. This is a univariate interpolation-degree statement,
NOT a lower bound on general algorithms or even on a given
instance's minimal useful weight certificate. Some small
weights may be unrealizable by legal cubic-linear kernels.

Nor does the exponential number of subsets prove that a compressed
rank aggregate cannot be computed in polynomial time: the entire
hypothesis is precisely the possibility of a clever compression.

## V. Exact executable replay

    python experiments/r5_universal_binomial_rank_aggregation_attack.py

Independent controls:

- SAT12 E61: exact 1 top-shell witness;
- UNSAT12 E57/E61: exact 0 top-shell witnesses;
- for each of those n12 matrices, five pinned/unpinned slices:
  enumerate all GF2 kernel words, compute every ordinary
  binomial moment, compare with independent GF2-rank counts
  over all 794 subsets, reconstruct Z via Newton coefficients;
- E123 q63 R: exact 0 top-weight words;
- E65 q63 R^T: exactly 36 top-weight words;
- exact decimal subset-count and asymptotic exponent checks.

The small-n kernel enumerations validate the **identity**, not
the polynomial complexity of the proposed global aggregate.
The n63 control enumerates 2^14 kernel words because the finite
fixture has nullity 14; it is not a worst-case poly-time algorithm.

## VI. Computed moment-discrimination depth: E123 q63 R vs SAT transpose

The exact E64/E65 q63 kernel word enumerators, from 2^14 words each,
yield binomial weight moments

    B_s = sum_{k in ker_F2(A)} binom(|k|,s).

For the UNSAT orientation R and SAT orientation T=R^T,

    B_s(R) == B_s(T)   for every 0 <= s <= 5,

but

    B_6(R) = 16,915,325,952;
    B_6(T) = 16,915,411,968;
    B_6(T) - B_6(R) = 86,016.

The exact SAT witness counts differ already in top shell:

    Z(R) = 0, Z(T)=36.

Thus **no scalar criterion obtained solely as a fixed rational linear
combination of B_0,...,B_5** can distinguish the two orientations,
regardless of how efficiently those five values are computed. The
same holds for any deterministic procedure whose ONLY observable
data about the input are these five moment values and n.
This is an exact *finite indistinguishability certificate* for the
weight-moment approach, not a computational complexity lower bound
on methods inspecting the full incidence matrix.

The first moment divergence at s=6 does NOT imply sixth-order
moments universally decide Exact-One. The general exact indicator
q_m has degree m=n/3 (21 for this q63 case), and a compressed
global procedure or totally different invariants would still need
an all-input theorem.

## VII. Anti-duplicate / literature audit

This is a Newton/binomial-moment re-expression of the E61/E65
top-shell criterion and the general coding theory rank-polynomial
connection. It must NOT be called a discovery of an efficient
solver or a new matrix-theory breakthrough.

Known relevant prior art:
- Greene's theorem / the binary-code weight enumerator and
  the Tutte/rank polynomial correspondence; see Alexander Barg,
  SIAM J. Discrete Math. 15 (2002), DOI 10.1137/S0895480199364148.
- Berlekamp, McEliece, van Tilborg, IEEE Trans. Inf. Theory (1978),
  DOI 10.1109/TIT.1978.1055873, on NP-completeness of general
  linear-code weight problems.
- E118 provides hardness for this exact structural JANUS carrier.

Neither source proves a complexity lower bound for every possible
algorithm or for this specific exact moment aggregate in a restricted
complexity model. P vs NP remains OPEN.

## VIII. Verdict

TOP_SHELL_BINOMIAL_FILTER = PROVED_FOR_ALL_SQUARE_CUBIC_INPUTS.
WEIGHT_GRID_EXACT_INTERPOLATION_DEGREE = n/3 (abstract full-grid only).
INDIVIDUAL_SUBSET_PROJECTION_RANK_COUNT = POLYNOMIAL_EXACT.
PINNED_RANK_AGGREGATION_FORMULA = PROVED.
E123_R_VS_RT_FIRST_WEIGHT_MOMENT_DIVERGENCE_AT_S6 = EXACT_FINITE_REPLAY.
DEGREE_LE5_WEIGHT_MOMENT_ONLY_DISTINGUISHER_FOR_THIS_PAIR = REFUTED.
GLOBAL_POLY_RANK_AGGREGATION = OPEN.
SOUND_COMPLETE_POLY_SOLVER_VIA_AGGREGATOR = CONDITIONAL_ONLY.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
