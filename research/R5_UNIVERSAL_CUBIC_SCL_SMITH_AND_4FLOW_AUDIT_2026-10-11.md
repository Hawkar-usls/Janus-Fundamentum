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

## III-A. General 4-flow support-moment / cut-profile theorem

For a connected simple cubic graph G that is 3-edge-connected and
whose size-three edge cuts are all vertex-stars, put N=|V|, M=|E|,
r=M-N+1 (binary cycle-space dimension), and let b4 denote the
number of **distinct four-edge cutsets**. Assume r>=4.

For each pair of binary circulations (f,g) in C(G)^2 let
w(f,g)=|supp(f) union supp(g)|, and define the *unrestricted*
(non-nowhere-zero included) binomial support moments

  H_k(G) = sum_{f,g in C(G)} binom(w(f,g), k).

These count exactly the pairs and a chosen k-edge set S on which
both bits are not simultaneously zero.

**Exact uniform theorem (all graphs satisfying this promise):**

  H_0 = 4^r
  H_1 = 3 M 4^(r-1)
  H_2 = 9 binom(M,2) 4^(r-2)
  H_3 = [27 binom(M,3) - 3N] 4^(r-3)
  H_4 = [81 binom(M,4) - 9N(M-3) + 3 b4] 4^(r-4).

**Proof:** On edge set S, the projected binary cycle space has
orthogonal dependencies precisely the binary cut vectors supported
inside S. For |S|=k<=4, no cut dependency gives an unconstrained
F2^2 labelling with all labels nonzero: 3^k possibilities, each
lifting to 4^(r-k) global cycle-pairs.

For k=3, the only possible nontrivial cut dependence is a single
vertex-star: the three edge labels have XOR sum zero, and exactly
3*2=6 choices are all nonzero, each lifting 4^(r-2).
This contributes 6*4^(r-2) instead of 27*4^(r-3),
a difference of -3*4^(r-3), N times.

For k=4, because minimum cut size is three and all 3-cuts are
vertex-stars, at most one cut relation is supported inside S.
The exceptional S are:
 (a) a star triple plus one of M-3 other edges, N(M-3) sets;
     three star labels are pairwise distinct nonzero (6 choices),
     and the fourth has 3 choices, giving 18*4^(r-3)
     instead of 81*4^(r-4): correction -9*4^(r-4);
 (b) an exact 4-cutset, b4 sets, with XOR of all four labels zero.
     There are precisely 21 all-nonzero labelings, each lifting
     4^(r-3): correction +3*4^(r-4).
The exceptional classes cannot overlap, else their cut XOR would
create a cut of size one, contradicting 3-edge-connectivity.
Summing proves the formula. This is a specialized finite-moment
consequence of binary cut/cycle duality, not a polynomial SAT solver.

**Finite bridge controls independently replayed:**
  Graph        N  M  r  #3-cuts  #4-cuts  H4
  K3,3         6  9  4      6         9       9,909
  Cube         8 12  5      8        15     157,968
  Prism C5    10 15  6     10        20   1,752,720
  Petersen    10 15  6     10        15   1,752,480

For Prism C5 and Petersen, ALL FOUR moments H0,H1,H2,H3 agree:
(4096, 46080, 241920, 784320), while H4 splits by exactly 240.
Since their true Boolean 3-edge colouring counts are respectively
30 and 0, **no procedure whose only observations are N and
these first four numbers H0..H3 can decide the two cases**.
This is a finite indistinguishability certificate for those
statistics, NOT a universal complexity lower bound.
The initial separation at H4 detects five additional size-4
edge cutsets (the prism's side faces) rather than detecting
Boolean satisfiability directly.

Asymptotic warning: higher moments or a compressed full
flow-support enumerator may encode all SAT information;
there is no proof that computing their relevant final
coefficient can be done in n^O(1) operations.

## III-B. Literature anti-duplicate

These are specializations of classical cycle/cut-space orthogonality
and graph flow-polynomial / Tutte-polynomial identities, not claims
of mathematical priority. A contemporary SODA 2026 result provides
quadratic time for genus-one cubic graph edge colouring and
classifies toroidal snarks, but does not solve general-graph
3-edge-colouring:
https://doi.org/10.1137/1.9781611978971.218
See also the 2002 cubic edge-colouring / Penrose-cycle-space count:
https://doi.org/10.1006/eujc.1999.0440

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
LOW_FLOW_SUPPORT_MOMENTS_0_TO_4_FROM_CUT_PROFILE = PROVED_ALL_PROMISED_GRAPHS.
PETERSEN_PRISM_FIRST_FOUR_SUPPORT_MOMENTS_EQUAL = VERIFIED_FINITE.
FLOW_MOMENTS_0_TO_3_ONLY_DECIDER = REFUTED_FINITE_PAIR.
SMITH_ONLY_UNIVERSAL_SCL_SOLVER = REFUTED.
NOWHERE_ZERO_4FLOW_POLYNOMIAL_EVALUATION = NOT_PROVED.
UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Reference: I. Holyer, The NP-Completeness of Edge-Coloring,
SIAM J. Comput. 10(4) (1981), doi:10.1137/0210055.
