# R5 — INFINITE THREE-EDGE-CONNECTED SCL90+9k NO-V3 THEOREM

2026-10-13 (Europe/Kyiv). Research branch research/r5-cubic-flow-smith-pair-20261011; PR #516 DRAFT; main unchanged.

Authenticated CI: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38384437400 — SUCCESS.
Source executable: experiments/r5_universal_infinite_3edge_connected_scl_triangle_degree3_dual.py.
Workflow: .github/workflows/r5-infinite-triangle-3edge-scl-v3-dual.yml.

## 0. Goal and exact limitation

User target remains a deterministic sound complete original SAT-witness / UNSAT uniform bit-polynomial SolveLinearCubicXSAT for ALL original square+cubic+linear positive 1-in-3 SAT sources. A general polynomial LoopZeroTest is NOT CONSTRUCTED; P vs NP remains OPEN.

This checkpoint proves an UNCONDITIONAL infinite family of original legal UNSAT SCL that have NO GF3 Boolean polynomial-calculus degree3 refutation and, unlike the earlier n=90+18k two-edge sum, the source cubic graphs are THREE-EDGE-CONNECTED. The proof-degree lower bound is still only >=4, NOT unbounded. No arbitrary-method runtime lower bound follows.

## 1. Frozen root witness, not a guessed source

Base graph G0 = exact 20-vertex Isaacs flower snark J5, independently original-source authenticated and UNSAT by its 27-state twist-transfer obstruction. The direct Holyer cubic-edge-colouring reduction makes n0=90 square, cubic, linear source clauses. The actual 6656-byte frozen F3 orbit dual vector has SHA256:

f2944e1a4fb474ebaac3aa2fcc19689139d1bee256f3f01af1f4ecebfd7c1edd

and was already independently verified to satisfy y0(1)=1, y0(E_i*x_M)=0 for every ORIGINAL clause i and squarefree |M|<=2. Certified prior runs: #38331387342 full direct 121576-monomial F3 elimination; #38332355302 independent symmetrized dual; #38332775987 standalone frozen witness checking all 368640 original generators.

## 2. EXACT cubic triangle inflation (Delta-Y) on EVERY step

Let G be a simple 3-edge-connected cubic graph with even number V of vertices, choose a vertex v and its distinct neighbors u0,u1,u2. Remove v and all three old edges e_i=(v,u_i). Add new triangle t0,t1,t2 with edges t0t1,t0t2,t1t2, and external edges (u_i,t_i).

The resulting graph G':
- vertex count V'=V+2;
- cubic edge count M'=M+3 (3 removed, 6 inserted);
- simple and cubic (each u_i recovers one incident edge; each t_i has one external and two internal edges);
- 3-edge-connected whenever G is 3-edge-connected: if a cut separates zero or all three t_i together, contraction to v gives an equally small old cut. If it splits the triangle, exactly two internal triangle edges cross; any cut with ≤2 edges would have NO external triangle crossing, so after contracting the triangle to v and choosing v on either side yields an old cut with ≤2 edges, contradicting 3-edge connectivity. The source proof checks all finite size1/size2 edge deletions independently.

The old 20-vertex J5 source graph passes exact 3-edge-connectivity check. Thus every G_k obtained by repeated inflation also has edge connectivity at least THREE, unlike the prior n90+18k family which had obvious 2-edge cuts.

After k steps V=20+2k, M=30+3k and native original Holyer source F_k has precisely n=3M=90+9k positive Exact-One rows and variables. It remains square, cubic, linear and source Tanner connected.

## 3. ORIGINAL graph UNSAT transfer by 3-edge-cut parity

In any 3-edge-coloring of cubic G', each color class is a perfect matching. Choose U={t0,t1,t2}; |U|=3 odd. Every perfect matching crosses the cut delta(U) in an ODD number of edges. The cut consists of exactly three external edges. Since each external edge has precisely one of three colors, EACH of the three colors occurs exactly once on the boundary.

Therefore external colors on edges (u0,t0), (u1,t1), (u2,t2) are pairwise DISTINCT. Shrink the triangle back to one old cubic vertex v, and assign the boundary colors to its three original edges e_i=(v,u_i): this gives a valid 3-edge coloring of G, contradiction whenever G was uncolorable. This is an independently valid polynomial-time UNSAT proof rule; it uses original graph/color certificates, not the GF3 dual.

Base J5 uncolorable => every G_k uncolorable => every original SCL F_k UNSAT by exact Holyer witness bijection.

## 4. STRONGER exact degree-one native source homomorphism

Let x_(e,c) be the original Boolean color-c edge indicator of G, and x'_(h,c) the ORIGINAL Boolean color indicator for edge h of inflated graph G'. Define a Boolean-variable-to-Boolean-variable map phi as follows:

(A) retained edge h of G:
 phi(x'_(h,c)) = x_(h,c).

(B) new external edge (u_i,t_i):
 phi(x'_(u_i,t_i,c)) = x_(e_i,c).

(C) new internal triangle edge (t_i,t_j), with {i,j,k}={0,1,2}:
 phi(x'_(t_i,t_j,c)) = x_(e_k,c).

There is NO multiplication and no affine combination: every new original Boolean variable goes to ONE original Boolean variable.

Check ALL original new source Exact-One clause generators E'_r = sum_(j in row r) x'_j -1:
- a new edge Exact-One clause maps to the old edge clause for h or one of e0,e1,e2;
- each untouched graph vertex-colour clause maps to the same old original vertex-colour clause;
- every new triangle vertex t_i has THREE incident edges whose ancestor labels are exactly e0,e1,e2 (external e_i plus internal opposite-vertex e_j/e_k), so each of its new vertex-colour clauses maps EXACTLY to the old v vertex-colour clause for that color.

Thus EVERY target original exact-one clause maps **literally** to SOME old exact-one source clause, as a three-variable multiset equality. Boolean equations x'^2-x' map literally to corresponding original Boolean equations.

## 5. ALL-d PC-degree retraction lemma (uniform mathematical proof)

Given ANY two Boolean exact-one source systems F',F and a monomial variable map phi such that each new source row maps EXACTLY to an old source row, ANY original degree-d dual y for F induces a new degree-d dual y' by

  y'(x'_M) = y(x_(set(phi(M)))),

where duplicate identified Boolean variables are collapsed using x²=x. The degree of the image monomial is at most |M|, so never rises; y'(1)=y(1)=1.

For EACH original new source generator E'_r*x'_M with |M|<=d-1:

 y'(E'_r*x'_M)
 = y(E_(old(r))*x_(set(phi(M))))
 = 0.

Hence no degree-d GF3 Boolean PC certificate of UNSAT on F' can exist if none existed on F. This is a source-verifiable degree-NONINCREASING BACK-SIMULATION / DUAL TRANSPORT, valid for EVERY integer d and over ANY field (the exact GF3 encoding of Exact-One SAT is used for our case).

In particular, the frozen J5 V3 dual maps through every triangle expansion by composition of source-variable indices. The resulting F_k is independently UNSAT, yet it has no degree-three native GF3 refutation.

THEOREM:
For every integer k>=0 there is a connected 3-edge-connected simple cubic graph G_k and its original legal SCL source F_k with n_k=90+9k and
    F_k UNSAT,   1 NOT IN V3(F_k).

The construction and the dual generator are effective using O(k) graph edits and the fixed original frozen J5 certificate, with polynomial size original source and exact degree3 verification.

## 6. Exact CI with independent original-source replay

One-HEAD CI #38384437400 SUCCESS:
- k=1: original legal, 3edge-connected SCL99, all **490149** original degree3 generators rebuilt and checked on imported dual, PASS;
- k=2: original legal, 3edge-connected SCL108, all **635796** generators checked, PASS;
- k=3: original legal 3edge-connected SCL117, all **807768** generators checked, PASS;
- k=4: original legal 3edge-connected SCL126, complete source clause pullback authenticated; no claim to re-enumerate all generators (the all-d theorem already supplies them symbolically);
- forged source index maps for k=1,2,3 were rejected by full row-level source checker;
- independent checking that every graph remains cubic, simple, and 3edge connected: delete each single and each pair of edges and independently verify source-graph connectivity.

This is not extrapolating from four samples. Universal source correctness and degree3 dual transport follow from elementary inductive proofs, while CI controls catch code/model provenance errors.

## 7. Proof-complexity novelty and exact next target

Delta-Y triangle vertex expansion itself is a standard known graph operation; see e.g. classical graph-colouring equivalence results. The new restricted research point is the **literal one-variable native Holyer source retraction** that transports an ACTUAL independently frozen GF3 dual without proof-degree increase and constructs an infinite THREE-edge-connected family from the exact J5 witness.

This family still contains obvious triangles and 3-edge cuts. It may be easy for an independent graph-contraction solver and it does not refute higher-degree or general polynomial methods. To make a true claim of UNBOUNDED GF3 source degree one must construct a sequence F_k with separately verified lower bound degree(F_k) >= f(k) -> infinity. No such proof is yet present. Candidate route: degree-preserving native source simulation of published expander Tseitin/graph vertex-coloring PC hardness, with an explicit LOW-DEGREE BACK-SIMULATION, not just semantic NP-completeness.

GATES:
- J5_ROOT_SCL90_UNSAT_AND_GF3_V3_DUAL = PROVED_FROZEN
- CUBIC_TRIANGLE_INFLATION_SOURCE_VALIDITY = PROVED
- INFLATION_3EDGE_CONNECTIVITY = PROVED
- GRAPH_3EDGE_CUT_UNSAT_TRANSFER = PROVED
- ALL_D_DEGREE_ONE_SOURCE_RETRACTION = PROVED
- INFINITE_N90_PLUS9K_CONNECTED_3EDGE_NO_GF3_V3 = PROVED
- F99_F108_F117_ALL_GENERATOR_DUAL_REPLAY = CI_SUCCESS
- UNBOUNDED_NATIVE_GF3_PC_DEGREE = NOT_PROVED
- ANY_UNIVERSAL_FIXED_D = OPEN
- GENERAL_POLY_LOOPZERO = NOT_CONSTRUCTED
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
