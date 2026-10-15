# JANUS R5 — OPTIMAL_MOMENT_LP / COMPONENT_FACTOR / CONNECTED_COVERAGE / LOW_DUAL_SPECTRUM
**Scientific checkpoint: 2026-10-15**

**Base**: research/r5-moment-hierarchy-20261015, head 2680f397c53b59731db2181c0ab102e9f5a8c83d (stacked PR #521). **New branch**: research/r5-optimal-moment-lp-components-20261015. No changes made to main.

## Gate A: optimal exact moment LP (PROVED and finite CI)

Source: `experiments/r5_optimal_moment_lp_20261015.py`.
For k<=5 and a legal SCL size n, let `N_j=sum_{Ax=1 mod2} binom(t(x),j)`.
The primal linear program is
```
maximize p_0
subject to sum_{t=0,3,...,n} binom(t,j)*p_t = N_j, j=0..k
           p_t >= 0.
```
The dual minimizes `sum_j lambda_j*N_j` under
`q(t)=sum_j lambda_j*binom(t,j)>=1[t=0]`, for all t=0,3,...,n.
The verifier does not trust the optimizer: it checks exact primal
nonnegative masses, all moment equalities, every dual inequality,
complementary slackness, and rational primal-dual objective equality.
The program uses a two-phase Fraction-only simplex with Bland's rule;
phase-II forbids artificial variables from entering the basis. The
first CI exposed this forbidden artificial reentry and recorded a
FAIL; commit a34b4dd fixed it. These failures are provenance,
not erased.

This is a polynomial LP in n for a FIXED k only if moments are
available using polynomial methods. Generic fixed-k moments are
available by O(n^k) source-row GF(2) rank/restriction queries as
proved in PR #521. This finite experiment instead uses a separate
exhaustive oracle where 2^d<=n^3, or a sound independent component
factor/convolution. The finite oracle is NOT silently billed as a
universal algorithm.

Source: `experiments/r5_optimal_moment_gates_20261015.py`
Exact optimum LP checked on all permitted support points:
```
              k=3          k=4          k=5    True solutions
Petersen45    480          193          147              0
SCL72 K4x4 1,310,720      367,001      262,799         1,296
```
Rational exact upper bounds before floor:
```
Petersen45   k3=480, k4=1352/7, k5=3088/21
SCL72        k3=1310720, k4=1835008/5, k5=6569984/25.
```
All 45 Petersen single-variable splits have sum of degree3
OPTIMAL LP child FLOOR bounds =467, passing c=1 geometric progress.
All 72 SCL72 single-variable splits have sum degree3
OPTIMAL LP child FLOOR bounds =1,310,719, failing c=1 geometric
progress. These are exact finite tests, with primal+dual
optimality separately certified for each LP, not only for selected
templates. Note that adding floor at child level can cause a 1-unit
artificial reduction even if a common linear certificate stays
exactly additive.

Scientific scope: this proves a FINITE obstruction to any OTHER
degree3 moment-only LP certificate with the SAME moment data,
support constraints and singleton grammar for this SCL72 root.
It is NOT a lower bound for stronger proof systems, multi-step
propagation, connected source instances, or all polynomial solvers.

## Gate B: COMPONENT_FACTOR (PROVED under component-nullity cap)

Source: `experiments/r5_component_factor_20261015.py`.
Derive row/variable connectivity from the actual SCL incidence
hypergraph (not from provenance). Relabel each component and
validate cubicity/linearity again. For each component with GF(2)
affine dimension d_i and `2^d_i <= n^3`, enumerate all parity
words, independently validate Exact-One and count local SAT.
Multiply exact solution counts and convolve violation distributions
t. Cost: `poly(n)*sum_i 2^d_i` for independently enumerable
components. This is polynomial if every d_i=O(log n) with
ONE fixed exponent. It can decline if any component too large.

The DISCONNECTED SCL72 source obtained from four independent
Holyer-K4 encodings is verified to have exactly four components
n_i=18, d_i=6. The code checks 4*64=256 local parity words,
finds 6 exact colorings per K4, and reports exact SAT count
6^4=1296. The product histogram contains 2^24 global parity
words WITHOUT enumerating them. SAT witness independently verified.

This example is a POSITIVE control for structural factorization,
not a universal hard case merely because the global nullity is 24.

## Gate C: CONNECTED_COVERAGE_BREAKER (FINITE CONSTRUCTION)

Source: `experiments/r5_connected_coverage_breaker_20261015.py`.
Construct source-valid connected SCL via cross-component 2-switches
of incidence graph edges (rowA,varA),(rowB,varB) →
(rowA,varB),(rowB,varA). Each step enforces preserved degrees and
reruns the full no-4-cycle/source-linearity validator. Choose
matching witness bits at endpoints so a known solution survives.
Connectivity is rechecked on the final source hypergraph.

Frozen seed 20261015:
- Two K4 blocks, n36: ONE connected source component,
  full affine 2^11=2048 parity words, **20 actual SAT solutions**.
- Four K4 blocks, n72: ONE connected source component,
  affine dimension d=21, 2^d=2,097,152,
  **LOG_KERNEL(c=3) DECLINES**, because 72^3=373,248.
  SAT witness is known and independently verified.
- Incidence 2-switches create small separators between old blocks;
  connectedness alone is not proof of global mathematical hardness.
  A separator-aware exact expert might still solve this cheaply.

These are useful connected controls but DO NOT refute any fixed
degree progress condition without separately testing moment LP and
the actual successor states.

## Gate D: MOMENT_INDISTINGUISHABILITY / signed dual spectrum

Source: `experiments/r5_connected_coverage_breaker_20261015.py`.
For affine `S=x0+L`, compute signed low-weight dual spectrum
```
b_j = sum_{u in L^perp, |u|=j} (-1)^(u · x0), j<=k.
```
The code enumerates size-j subsets of source variable coordinates
for FIXED small k<=3 and checks orthogonality to the exact GF(2)
affine basis. These coefficients determine the first k derivatives
of the affine weight enumerator at z=1, by the exact affine
MacWilliams transform. Since t=(3|x|-n)/2 for legal parity
solutions, with n and affine |L| fixed, equality of these signed
low-weight spectra also forces equality of the first k moments
of t. However it does NOT force equality of the SAT count.

**First strict finite positive result:** The original 24
single-cross-component swaps produced identical signatures and
identical SAT counts. After adding multiple additional legal
witness-preserving 2-switches INSIDE the connected n36 source,
the seeded search discovered two DIFFERENT connected legal
n36 SCL instances with equal GF(2) affine dimension **d=7**,
identical signed dual low-weight spectrum up to degree2
`(b0,b1,b2)=(1,0,10)`, identical raw violation moments
`(N0,N1,N2)=(128,1152,6624)`, and DIFFERENT EXACT solution
counts **2** and **3** respectively.

Frozen reproducibility:
```text
seed 0:  sha256 afc007f7654d59af6d918dbe9d7a25e14f178a26710377aae61a687abac7e7ce
         #SAT 2, signed dual k<=2=(1,0,10)
seed 13: sha256 3adc96ebb00fc6c28330dce9c6bd1ef53e0dc1eeb7ba5b030e8584e5d950c1b2
         #SAT 3, signed dual k<=2=(1,0,10)
```
Both are independently rebuilt, validated connected/cubic/linear,
their SAT counts checked by full **2^7=128** parity-word
enumerations, and their raw moments recomputed from the EXACT
histogram. The frozen test also verifies both produce the
**SAME OPTIMAL DEGREE-2 LP bound** by separately replaying the
rational primal/dual simplex.

At degree3 their signed spectrum ALREADY diverges:
`b3=-122` versus `b3=-110`. Thus this pair proves a finite
degree-2 insufficiency, **NOT** a fixed-degree-3 insufficiency,
and not a complexity lower bound for all legal SCL.

The fact both instances are SAT also matters: they demonstrate
inability to COUNT precisely with low moments, but NOT inability
to distinguish SAT from UNSAT. A collision with different
SAT/UNSAT statuses would be a stronger decision-oriented gate.

## Reproduction commands
```bash
python3 experiments/r5_optimal_moment_lp_20261015.py --self-test
python3 experiments/r5_component_factor_20261015.py --self-test
python3 experiments/r5_connected_coverage_breaker_20261015.py --self-test
python3 experiments/r5_optimal_moment_gates_20261015.py --self-test
```
Workflow: `.github/workflows/r5-optimal-moment-components.yml`.

## Strict gates and next action
| Gate | Scientific status |
| --- | --- |
| Two-phase exact-rational LP and primal/dual certificate checker | PROVED, CI VERIFIED |
| Optimal LP(3,4,5) on Petersen45 and SCL72 | CI FINITE VERIFIED |
| 117 optimal degree3 singleton root tests | CI FINITE VERIFIED |
| Automatic source-component factor with small affine dimensions | PROVED / CI VERIFIED |
| SCL72 exact local SAT count =1296 | CI FINITE VERIFIED |
| Connected legal n36 and n72 controls | CI FINITE VERIFIED |
| Fixed-k signed dual low-weight enumeration | PROVED / CI VERIFIED |
| Connected signed-spectrum degree2 collision with differing exact SAT count | CI FINITE VERIFIED |
| Connected source proven moment LP stall | NOT TESTED FOR ALL BRANCHES |
| Uniform polynomial cooperative progress for all legal SCL | NOT PROVED |
| SolveLinearCubicXSAT n^O(1) total solver | NOT CONSTRUCTED |
| P vs NP | OPEN |

**Next substantive move**: build connected/irreducible SCL with no
cheap 2-edge separator, verify optimal moment LP and all branching
variables; extend signed-dual collision search to pairs with different SAT/UNSAT statuses or indistinguishable degree3 signatures; and test separator-aware factor expert. The
finite optimality of k=3 is a meaningful grammar-level negative
certificate, not a universal complexity lower bound.
