# R5 — Cubic SCL: Smith invariants, matched SAT/UNSAT pair, and exact 4-flow audit

Date: 2026-10-11.
Parent checkpoint: `f91ed13f23f027277aeda85ec9b8cbbe1b8b3e8f`.
Goal: all-input deterministic polynomial `SolveLinearCubicXSAT` with SAT witness or UNSAT, soundness, completeness, and polynomial bit runtime.
**Goal remains OPEN. This memo is not a solver or P=NP proof.**

## I. Integer normal form for every simple cubic graph

Let G have N vertices, M=3N/2 edges, c connected components, b bipartite connected components.
Let B be its **unoriented** vertex-edge incidence matrix, and let
```
A = [ I_M  I_M  I_M
      B     0    0
      0     B    0
      0     0    B ].
```
Perform the unimodular integer column change
t=x0+x1+x2, u=x0, v=x1; equivalently x2=t-u-v.
Then A outputs (t, Bu, Bv, Bt-Bu-Bv).
Integral row operations subtract Bt, add Bu and Bv, producing
```
A ~_Z diag(I_M, B, B, 0_{N x M}).
```
This is an integer-equivalence, not just a rational row reduction.

A connected bipartite component's unoriented incidence matrix has Smith
invariants 1^(N_i-1), 0. A connected nonbipartite component has
1^(N_i-1), 2. This follows by switching signs on a spanning tree to
reduce it to a standard tree incidence block; the remaining chord
relations are 0 for bipartite components and even, with an odd cycle
producing an entry 2, for nonbipartite components.

Thus A has Smith invariants
```
1^(M+2(N-c)), 2^(2(c-b)), 0^(N+2b).
```
Equivalently:
```
coker_Z(A) ~= Z^(N+2b) direct_sum (Z/2Z)^(2(c-b)).
nullity_Q(A)  = N+2b.
nullity_F2(A) = N+2c.
```
This proves that the Smith invariants depend **only** on N, c, b
within this cubic-graph image, and do not decide Boolean feasibility.

## II. Two independent exact counting routes

(1) For every perfect matching P, G-P is a disjoint union of cycles.
Fix colour 0 on P; if all these cycles are even, each cycle has two
alternations of colours 1 and 2; otherwise no extension exists:
```
#3EdgeColourings(G) = sum_{P perfect matching}
  (0 if any residual cycle odd else 2^(number of residual cycles)).
```
This remains potentially exponential in the number of perfect matchings.

(2) Encode three colours as the three nonzero elements of F2^2.
At a cubic vertex, three nonzero values sum to zero iff they are
pairwise distinct. Therefore a proper 3-edge-colouring is exactly
a nowhere-zero F2^2-flow. Let C(G) be the GF2 cycle space of G.
Then
```
#3EdgeColourings(G) =
  #{(f,g) in C(G)^2 : for all edges e, (f_e,g_e) != (0,0)}.
```
This is the classical nowhere-zero 4-flow correspondence, not an
assertion of a new polynomial evaluation of the Tutte flow polynomial.
If r=M-N+c, direct enumeration costs about 2^(2r) tests.
It is *not* a universal polynomial evaluator.

## III. Matched full-Smith pair

Both Petersen and the pentagonal prism C5 x K2 are simple, connected,
nonbipartite cubic graphs with N=10, M=15. Thus both have:
```
SCL dimensions 45 x 45
SNF          1^33, 2^2, 0^10
rank_Q       35
rank_F2      33
```
But independent exact finite counts give:
```
Petersen:  0 edge-colourings;  6 perfect matchings, 0 extendable
5-prism:  30 edge-colourings; 11 perfect matchings, 10 extendable
```
So **an algorithm depending only on the complete Smith invariants**
cannot decide SAT/UNSAT even on the cubic bridge subfamily.
This does NOT exclude methods using the unimodular basis-transform
matrices, full incidence structure, or more powerful algebraic objects.

## IV. Independent executable check

Run:
```
python experiments/r5_universal_cubic_flow_snf_discriminator.py
```
Small cases K4, K3,3, cube, 5-prism and Petersen are counted by three
independent exact methods. The script separately checks the SCL
3-regular/C4-free promise, SAT witnesses, and GF2/GF3 ranks.
All exhaustive methods are explicitly exponential.

This adds a diagnostic counterexample and exact control, not a
new polynomial algorithm. The actual missing theorem remains an
all-input polynomial evaluator or an alternate polynomial SAT/UNSAT
decision procedure with proof.

## Gate ledger

CUBIC_SCL_FULL_SMITH_INVARIANTS = PROVED_FOR_ALL_SIMPLE_CUBIC_G.
PETERSEN_VS_5PRISM_SAME_SMITH_DIFFERENT_BOOLEAN = PROVED_FINITE_PAIR.
THREE_EXACT_COUNTING_ROUTES_AGREE = VERIFIED_FINITE.
SMITH_ONLY_UNIVERSAL_SCL_SOLVER = REFUTED.
NOWHERE_ZERO_4FLOW_POLYNOMIAL_EVALUATION = NOT_PROVED.
UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Reference: I. Holyer, The NP-Completeness of Edge-Coloring,
SIAM J. Comput. 10(4) (1981), doi:10.1137/0210055.
