# R5 theorem — Infinite CONNECTED, BRIDGELESS native SCL family with original UNSAT and no GF3 degree-three refutation

Scientific checkpoint: 2026-10-13 (Europe/Kyiv). PR #516 DRAFT; main unchanged.
Authoritative CI: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38383919925 — SUCCESS.
Executable: experiments/r5_universal_infinite_connected_scl_degree3_dual_two_edge_sum.py
Workflow: .github/workflows/r5-infinite-connected-scl-v3-dual.yml

## Global goal / non-overclaiming

The goal remains ONE sound, complete uniform polynomial BIT-time SolveLinearCubicXSAT for all native square, cubic, linear monotone Exact-One sources, with original SAT witness or correct UNSAT. The general polynomial LoopZeroTest does NOT exist in the present work. P vs NP is OPEN.

This theorem is a genuine **INFINITE**, CONNECTED, original-source proof-complexity obstruction against the SINGLE frozen degree-three GF3 Boolean polynomial-calculus method. **It does NOT show UNBOUNDED refutation degree**: all constructed sources have the same verified lower bound degree>=4. It is not a lower bound for arbitrary polynomial algorithms.

## 1. Initial independently certified degree-three obstruction

Take the 20-vertex, 30-edge Isaacs flower snark J5. The native Holyer map creates legal original SCL source F0 with 90 variables/rows. Each row positive Exact-One, each variable occurs three times, every row contains exactly three variables and distinct rows share at most one. Source UNSAT is independently proved by its authenticated 27-state twisted-seam flower transfer.

Frozen base dual in repo:
research/certificates/R5_J5_SCL90_GF3_V3_ORBIT_DUAL_2026-10-13.b64z
The decompressed 6656 GF3 orbit values have SHA256
f2944e1a4fb474ebaac3aa2fcc19689139d1bee256f3f01af1f4ecebfd7c1edd

The standalone prior CI #38332775987 confirmed after expansion to 121576 squarefree monomial moments y0 that
y0(1)=1;
y0(E_i*x_M)=0 for all 90 native source rows i and all squarefree |M|<=2 (368640 independently replayed source generators).
Thus no V3 refutation of F0 exists, and F0 UNSAT.

## 2. ALL-d source-homomorphism lemma — the central new exact theorem

Let original SCL sources F_old and F_new have n and m Boolean variables and cubic positive exact-one rows. Suppose a mapping phi:{0,..,m-1}->{0,..,n-1} satisfies:

EVERY ORIGINAL row (a,b,c) in F_new maps under phi to some ORIGINAL row (phi(a),phi(b),phi(c)) of F_old, as an EQUALITY OF MULTISETS, not just an implicit SAT reduction.

For any d and a dual y_old on multilinear original monomials degree<=d with
y_old(1)=1
and y_old(E_i*x_M)=0 for all old clauses i and |M|<=d-1,
define y_new(x_M)=y_old(x_set(phi(M))) for each new squarefree monomial |M|<=d.

Because phi sends each new E'_r EXACTLY to some old original E_i, and Boolean reduction commutes with variable identification,
y_new(E'_r*x_M)=y_old(E_i*x_set(phi(M)))=0
for EVERY original new row r and every permitted monomial M. The cardinality of set(phi(M)) is <=|M|, so source proof degree NEVER increases. And y_new(1)=1.

Hence:
NO degree-d original source refutation for F_old
IMPLIES
NO degree-d original source refutation for F_new.

Equivalently, any new degree-d GF3 Boolean PC refutation would pull back under the exact source variable substitution into an old degree<=d refutation. This is a general all-d, all-field statement for this exact monomial-to-monomial original-row map. It is substantially STRONGER than ordinary SAT-equivalence, and the low-degree back-simulation is explicit.

Caveat: The source map F_new -> F_old preserves satisfaction only in the direction old SAT => new SAT; it does NOT on its own show new UNSAT. The next separate graph parity lemma independently proves that.

## 3. Cubic graph 2-edge-sum and source map, all k

Let G be a connected bridgeless SIMPLE cubic graph, e=(u,v) one edge, H=K4 with 3-edge-colouring psi:
psi(0,1)=psi(2,3)=0;
psi(0,2)=psi(1,3)=1;
psi(0,3)=psi(1,2)=2.

Take disjoint G and a newly indexed H. Delete e from G and f=(0,1) from H; add the two edges (u,new0), (v,new1). Denote G'=G ⊕_2 H.

Graph construction verifies:
- G' remains cubic and simple: exactly one old edge deleted at each of four endpoints, replaced by exactly one external edge.
- G' remains connected and bridgeless: G-e and H-f stay connected because G,H were bridgeless; there are TWO cross edges, and an alternative path replacing e through H-f witnesses no new bridge; the connectivity of every original old edge can similarly be restored by replacing e via the H detour. The source verifier independently removes each graph edge in finite controls and checks connectivity.
- |V(G')|=|V(G)|+4, |E(G')|=|E(G)|+6.
- The source-authenticated direct Holyer construction makes legal SCL source of size n'=n+18.

**Exact native source variable pullback phi:**
Let original source variable x_(h,c) represent the indicator 'old edge h has colour c'. For target source variable x'_(g,c):

(A) retained old graph edge g≠e:
   phi(x'_(g,c)) = x_(g,c).
(B) either new cross edge:
   phi(x'_(cross,c)) = x_(e,c).
(C) internal K4 edge h≠f with base 3-edge colour psi(h)=s:
   phi(x'_(h,c)) = x_(e,(c-s) mod3).

Thus every TARGET source variable is mapped to ONE OLD source variable, no affine polynomial or degree increase.

Every target original edge Exact-One clause maps to an old original edge clause, either its retained original edge or the old edge e. Every target vertex-colour Exact-One clause at G vertices maps to the old original corresponding vertex-colour clause. Every target K4 vertex-colour clause maps to the old edge e Exact-One clause, since base psi uses each colour once around every K4 vertex (with the deleted f replaced by a cross edge of the same base colour0). The CI checks ALL these target source clauses by sorted original variable-ID triples; no handwavy colour-gauge assertion.

Therefore the all-d source-homomorphism lemma applies under this explicit exact native source map.

## 4. INDEPENDENT UNSAT lemma from 2-edge-cut parity

For any graph 3-edge-colouring of a cubic graph, each colour class is a perfect matching. For the vertex set U corresponding to original G inside G', |U| is even (starting J5 with 20 vertices, adding K4 keeps |U| even). Every perfect matching crosses the cut δ(U) in |U| mod2 = 0 edges. This cut has EXACTLY TWO edges, so for each colour its crossing count is 0 or2. Since both crossing edges receive colours, they must receive the SAME colour.

Restoring old e between u and v and colouring it with that common cross colour yields a valid proper edge 3-colouring of old G. This is impossible when old G was already uncolourable. Hence G' uncolourable and its ORIGINAL Holyer SCL source UNSAT, independently from the polynomial dual.

Inductively every G_k is connected, bridgeless, uncolourable, cubic, simple. Native sources F_k all UNSAT.

## 5. INFINITE all-source theorem

Set G_0=J5, G_(k+1)=G_k ⊕_2 K4 by the preceding fixed algorithm. All native sources F_k have:
- 20+4k vertices in cubic graph;
- 30+6k edges;
- n_k=90+18k original square/cubic/C4-free positive Exact-One variables and clauses;
- source Tanner connected, cubic source graph bridgeless;
- UNSAT original source via the 2-edge-cut parity and base flower UNSAT;
- no F3 Boolean degree-three V3 refutation, because all stepwise native source maps compose to a map F_k -> F0 and pull the independent source dual y0 forward.

More generally, the source-homomorphism lemma holds for ANY d and suitable seed G for which an independently checked degree-d dual exists, thus this construction gives infinitely many connected legal sources inheriting that proof-degree lower bound. It does not amplify d.

FORMAL STATEMENT:
For each integer k>=0 there exists an independently source-constructible connected bridgeless legal original SCL F_k of size n=90+18k such that
    F_k UNSAT AND 1 NOT IN V3(F_k).

This disproves any claim that degree-three obstruction occurs only in a finite set of small connected anomalous SCL instances.

## 6. Finite exact independent CI controls

One-HEAD CI #38383919925 SUCCESS; original sources independently rebuilt from direct Holyer make_scl each step; legal source rows independently source-validated; graphs checked connected, simple, cubic and *bridgeless* by deleting each graph edge.

Direct degree-three source-dual verification with composed maps into the FIXED authenticated J5 proof:
- k=1: SCL108, exactly 635796 target original source generators E'_i*x'_M checked mod3, PASS.
- k=2: SCL126, exactly 1008252 target original generators checked, PASS.
- k=3: SCL144 full native source map checked, and ALL source dual equations follow symbolically by exact monomial pullback. No claim of direct enumeration at k3.
- forged source-variable pullback maps rejected at k1 and k2.
- the base frozen 6656-byte J5 orbit dual is authenticated by SHA256 and source-checked.

Code: experiments/r5_universal_infinite_connected_scl_degree3_dual_two_edge_sum.py
Workflow: .github/workflows/r5-infinite-connected-scl-v3-dual.yml

## 7. Central unfinished P=NP-level theorem

This infinite family proves ONLY a degree-three method obstruction. A hypothetical universal fixed degree d≥4, an alternative non-flat implicit polynomial exact zero test, or another universal solver is NOT excluded. The existence of ANY all-SCL degree bound independent of n remains OPEN in this research; the available degree lower bound is merely at least4 for the constructed family. Need explicit unbounded-degree source-dual family or a degree-preserving source translation of a published hard proof-complexity family. Neither has been delivered here.

GATES:
- NATIVE_J5_SOURCE_V3_DUAL = PROVED / FROZEN
- TWO_EDGE_SUM_COLORABLE_K4_GRAPH_AND_SOURCE_MAP = PROVED
- NATIVE_SOURCE_MONOMIAL_RETRACTION_ALL_D = PROVED
- ORIGINAL_2EDGE_CUT_PARITY_UNSAT_PRESERVATION = PROVED
- CONNECTED_BRIDGELESS_INFINITE_N90_PLUS18K_NO_V3 = PROVED
- NATIVE_SCL108_DUAL_REPLAY = 635796 ALL GENERATORS PASS
- NATIVE_SCL126_DUAL_REPLAY = 1008252 ALL GENERATORS PASS
- NATIVE_SCL144_SOURCE_MAP = PASS
- UNBOUNDED_NATIVE_SOURCE_GF3_PC_DEGREE = NOT_PROVED
- ALL_SCL_FIXED_DEGREE_COMPLETENESS = OPEN
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
