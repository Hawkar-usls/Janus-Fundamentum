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

**Stronger all-input theorem within its stated graph promise.**
Let G be ANY connected, simple, **3-edge-connected** cubic graph
with N vertices, M=3N/2 edges, binary cycle rank r=M-N+1>=4.
Let b3 and b4 count **distinct edge cutsets** of cardinality
three and four respectively, including nontrivial 3-cuts.

For binary circulations (f,g) in C(G)^2 put
w(f,g)=|supp(f) union supp(g)| and

  H_k(G) = sum_{f,g in C(G)} binom(w(f,g), k).

This is a moment of unrestricted 4-valued flows; it includes pairs
whose union does not cover all edges, and does not itself decide SAT.

**Exact uniform identities:**

  H_0 = 4^r
  H_1 = 3 M 4^(r-1)
  H_2 = 9 binom(M,2) 4^(r-2)
  H_3 = [27 binom(M,3) - 3 b3] 4^(r-3)
  H_4 = [81 binom(M,4) - 9 b3(M-3) + 3 b4] 4^(r-4).

**Complete proof:**
For each edge set S, the projected F2 binary cycle space on S
has as its dual the F2 cut relations **supported entirely in S**.
If S contains no nonempty cut, then edge colours in F2^2 are
independent, and the number of projected all-nonzero labels is
3^|S|, each lifting to 4^(r-|S|) global flow pairs.

For |S|<=2 no cut exists by 3-edge-connectivity.
For |S|=3, a three-edge cut contributes exactly 6 pairwise
distinct nonzero labels (the triple XORs to zero), lifting
to 6*4^(r-2) instead of 27*4^(r-3): difference
-3*4^(r-3). There are b3 such cuts.

For |S|=4, at most one independent cut relation fits:
two distinct three-edge cuts in S would have intersection >=2,
so their binary XOR would form a cut of size <=2, impossible;
a three-edge cut and a distinct four-edge cut supported on S
would XOR to a cut of size one, also impossible.
There are two **disjoint** exceptional cases.

(a) S contains a 3-cut and one of M-3 remaining edges:
exactly 6*3=18 all-nonzero labelings, lifting to
18*4^(r-3) instead of 81*4^(r-4).
Correction: -9*4^(r-4), repeated b3(M-3) times.

(b) S itself is a 4-cut:
exactly 21 nonzero labels have XOR zero on its four edges,
lifting to 21*4^(r-3), rather than 81*4^(r-4).
Correction: +3*4^(r-4), repeated b4 times.

Summing contributions proves H0--H4 for EVERY connected simple
3-edge-connected cubic graph with r>=4. Neither cubic girth
nor cyclic four-edge connectivity is assumed. This is a
specialized coding-theory / cut-cycle duality identity;
no mathematical priority over the literature is asserted.

**Independent exhaustive controls, matched to the analytic identities:**

  graph         N   M  r  b3  b4        H3          H4    #colourings
  triangular     6   9  4   7   9       8988        9855         6
  K3,3           6   9  4   6   9       9000        9909        12
  cube           8  12  5   8  15      94656      157968        24
  pent. prism   10  15  6  10  20     784320     1752720        30
  Petersen      10  15  6  10  15     784320     1752480         0
  hex. prism    12  18  7  12  27    5630976    15764544        72

The triangular prism has b3=7>N=6 because the three cross
edges separating the two triangles form a nontrivial 3-edge cut:
this **refutes** replacing b3 with N unconditionally.
The generalization above repairs precisely that assumption.

For the pentagonal prism and Petersen, H0,H1,H2,H3 coincide:
  (4096, 46080, 241920, 784320).
Their H4 differ by 240, because the prism has five extra
four-edge cuts: 5*3*4^(6-4)=240.
Yet Boolean 3-edge-colouring counts are 30 versus 0.
Thus a decision procedure observing **only** graph size and
these first four moment values H0..H3 cannot distinguish this
finite SAT/UNSAT pair. This is a finite information firewall,
NOT a lower bound on unrestricted algorithms.

The high-order moment or the whole flow-support enumerator still
contains global NP-complete information. No polynomial-time
evaluation or compression of the necessary high-order term has
been proved.

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

## III-C. New matched SAT/UNSAT 20-vertex pair and all-fixed-k exact deletion theorem

Fix two simple 3-regular connected graphs with |V|=20, |E|=30 and
binary cycle dimension r=11:
 * UNSAT: standard Isaacs flower snark J5 generated by the already
   frozen standard flower recipe.
 * SAT: the graph with 30 literal edges in
   experiments/r5_universal_cubic_flow_lowmoment_collision_20v.py,
   independently identified by networkx random_regular_graph(3,20,seed=114)
   and then frozen as a dependency-free edge list.

The fixed edge list is authoritative; no dependency on networkx or a
random generator exists at replay time. The matching-complement
enumerator independently computes EXACTLY 72 labelled 3-edge-colourings
for the SAT graph and 0 for the flower snark.
Both have edge-cut profiles
  b3=20, b4=30,
and consequently identical moments H0 through H4,
while their *minimal 5-edge-cut* profiles separate:
  b5(SAT)=68, b5(UNSAT)=61.

This yields a strict **finite low-moment collision** with identical
complete Smith form as well as graph size, connectivity, and low
cut counts:
  Smith(A) = 1^68, 2^2, 0^20
  SAT Boolean models = 72; UNSAT Boolean models = 0.

### All-graph fixed-k edge deletion identity

For any connected loopless finite graph G with n vertices, m edges,
r=m-n+1, and its two-bit F2 cycle-space pair ensemble,
define H_k=sum_{f,g in C(G)} C(|supp(f) union supp(g)|,k).
Then, for EVERY k from 0 to m,

  H_k = sum_{j=0}^k (-1)^j C(m-j,k-j)
             sum_{T subset E, |T|=j} 4^{m-j-n+c(G-T)}.

**Proof.** For a particular k-set S, use inclusion-exclusion on
edge positions required to have nonzero F2^2 labels. A pair of
binary cycles vanishing on all edges of T is exactly a pair of
binary cycles in G-T, whose number is 4^{m-|T|-n+c(G-T)}.
Sum over all k-subsets S, interchange the sums, and observe that
each j-subset T is contained in C(m-j,k-j) such sets S.
All exponents are nonnegative integers. No cancellation-free or
polynomial bound for varying k follows from this exact identity.

For any FIXED integer k, direct computation takes
O(sum_{j=0}^k C(m,j) * poly(n,m)) BIT operations, and integer
arithmetic uses O(m) bits since 4^r <=4^m.
When k=Theta(m) the number of deletion subsets is exponential.
In particular **do not replace k by m and call this a polynomial
solver**. This is an inclusion-exclusion / flow polynomial identity
related to classical Tutte evaluations, not a novelty claim.

### Independent finite exact output

The graph-deletion connected-component histograms for j<=4 are
identical, while at j=5 they are:

  SAT20:  {c=1:134698, c=2:7778, c=3:30}
  J5:     {c=1:134705, c=2:7771, c=3:30}.

Both moments H0..H4 are:
  4194304, 94371840, 1026293760, 7180124160, 36291133440.

The **first** difference in the computed range is at H5:
  H5(SAT20)=141091037184
  H5(J5)   =141091123200
  H5(J5)-H5(SAT20)=86016=7*3*4^6.

Each graph has 20 distinct 3-cuts and 30 distinct 4-cuts; this
proves that using only the first five support moments H0..H4,
even with the complete SNF, does NOT decide the 20-vertex
SAT/UNSAT pair. It does not show that any fixed number of
moments is insufficient for ALL graphs, nor that H5 universally
decides the target.

Runnable:
  python experiments/r5_universal_cubic_flow_lowmoment_collision_20v.py

CI includes this exact finite replay on the PR516 research branch.

### Post-collision universal research gate

A genuine worst-case polynomial algorithm must exploit GLOBAL
information beyond any prescribed bounded number of these moments,
or provide a rigorous uniform polynomial computation of the
relevant high-order zero/nonzero criterion. This is a necessary
discriminator for the moment-only proposal, NOT a claim that
every conceivable algorithm must calculate moments.

ALL_INPUT_POLYNOMIAL_FLOW_SUPPORT_NONZERO_DECIDER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

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
LOW_FLOW_SUPPORT_MOMENTS_0_TO_4_FROM_CUT_PROFILE = PROVED_ALL_3EDGE_CONNECTED_CUBIC_G.
PETERSEN_PRISM_FIRST_FOUR_SUPPORT_MOMENTS_EQUAL = VERIFIED_FINITE.
FLOWER_J5_VS_SAT20_FIRST_FIVE_SUPPORT_MOMENTS_EQUAL = VERIFIED_FINITE.
FLOW_SUPPORT_MOMENT_DELETION_IDENTITY_ALL_GRAPHS = PROVED_AS_EXACT_IDENTITY.
NONTRIVIAL_THREE_EDGE_CUT_B3_VS_N_FIREWALL = PROVED_FINITE.
FLOW_MOMENTS_0_TO_3_ONLY_DECIDER = REFUTED_FINITE_PAIR.
SMITH_ONLY_UNIVERSAL_SCL_SOLVER = REFUTED.
NOWHERE_ZERO_4FLOW_POLYNOMIAL_EVALUATION = NOT_PROVED.
UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Reference: I. Holyer, The NP-Completeness of Edge-Coloring,
SIAM J. Comput. 10(4) (1981), doi:10.1137/0210055.
