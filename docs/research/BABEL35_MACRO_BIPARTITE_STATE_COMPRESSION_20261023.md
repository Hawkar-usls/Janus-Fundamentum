# BABEL-35 — high-frontier connected macro SCL with genuine THREE-state local relations, yet exact O(n) SAT by bipartiteness

**23 October 2026. Research-only successor to BABEL-34 [PR #560] on exact head \`86c94ab40d44655a9f2587fb14bd81905cca88c2\`.** Distinguishes a genuinely interactive macro-boundary CSP from BABEL-34's completely frozen singleton local table. This is a scoped exact high-width **compression theorem**; NOT a general SCL polynomial algorithm and not a claimed historical priority result (finite-state factor reductions and graph bipartiteness are established techniques). Main and frozen TRUMP authority unchanged.

## 1. Repaired benchmark: three NEW ports on the identical legal U=SCL27

Use U from BABEL24/BABEL34, with frozen row SHA256 \`9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed\` and original one-index set \`(2,3,7,9,13,17,19,23,24)\`. Select three DIFFERENT zero-valued row/variable incidences:

    p0=(row0,variable1), p1=(row8,variable10), p2=(row16,variable4).

All three rows and all three variables are distinct, and removing these incidences leaves the internal 54-vertex bipartite U factor graph CONNECTED (independent finite BFS test).

Dropping WHOLE rows 0,8,16 leaves 24 original untouched Exact-One rows. These admit EXACTLY THREE complete 27-bit physical assignments. Independently certify them by full Boolean Exact-One DPLL AND rational echelon with exhaustive Boolean free-coordinate projection (the Q rank of 24 kept rows is 24; free coordinates are (23,25,26), all 8 Boolean projections are checked).

The exact table of exports \`a=(x1,x10,x4)\` and REQUIRED imports \`b=(1−retained_count_row0,1−retained_count_row8,1−retained_count_row16)\` is:

| Local exact-one model one-indices | exported a | required b |
| --- | --- | --- |
| \`(2,3,7,9,13,17,19,23,24)\` | (0,0,0) | (0,0,0) |
| \`(5,6,11,12,16,18,22,26)\` | (0,0,0) | (1,1,1) |
| \`(0,1,4,8,10,14,15,20,21,25)\` | (1,1,1) | (0,0,0) |

All three states are physically possible under Boolean port imports; NO additional local state exists. Every port bit within each side of each state is identical (independent of which incident macro edge receives which named port).

Compress each U block to a 2-bit pair \`(a,b)∈R\`, where the complete feasible local relation is

    R = {(0,0),(0,1),(1,0)}.

Each of the three local physical models is in ONE-TO-ONE correspondence with exactly one such pair. The isolated U's original SAT solution uses (0,0); the other two are temporarily punctured models whose removed rows are repaired only through compatible incoming edge bits.

## 2. ALL-n EXACT correspondence to bipartite coloring of the macro graph

Let H be ANY connected simple 3-regular macro graph with t even vertices, equipped with any bijection of the three incident edges at each macro vertex to p0,p1,p2. As in BABEL33, exchange the two endpoint incidences across every macro edge. The resulting J_R(H) is a legal connected square cubic linear SCL with n=27t. The concatenation of the (0,0) local models always satisfies it.

**Exact full model theorem**: The global SAT models of J_R(H) are exactly the admissible local state assignments \`s_u=(a_u,b_u)∈R\` for which every macro edge \`{u,v}\` obeys

    a_u=b_v   AND   a_v=b_u.                          (*)

This is a bijection: all unmodified local rows force each block to one of the three enumerated punctured physical models; the exchanged rows enforce exactly (*). Conversely any compatible state assignment repairs all edited rows, and concatenating its local physical assignments satisfies every original joined row.

Given connected H, if ANY macro state is (0,0), (*) forces every neighboring state (0,0), and connectivity forces the globally all-zero state. If no vertex is (0,0), the only possibilities are (0,1) and (1,0); (*) forces adjacent vertices to have OPPOSITE states. Therefore such assignments exist iff H is bipartite, and then there are exactly TWO orientations of its unique bipartition.

Hence, for EVERY connected admissible cubic macro graph:

    #SAT(J_R(H)) = { 3, if H is bipartite;
                   { 1, if H is not bipartite.

SAT always holds, but the exact global model COUNT and the two extra physically reconstructed models depend on a GLOBAL property (bipartiteness), not just one frozen local relation. The reduction plus one BFS 2-coloring test takes **O(t)=O(n)** time and O(n) output/verification, GIVEN a polynomially certified port-template partition and edge assignments. Count-independent decision, exact count and constructive witnesses are all correctly reconstructed without full 2^n parity enumeration. This is a genuine long-range consistency mechanism on arbitrary macro graphs.

## 3. High-width expander macro case and all representation firewalls

The three designated port incidences of U are distinct and leave its internal factor graph connected. Therefore the previous BABEL33 proof applies: for genuine simple connected cubic-expander H families, every balanced incidence cut in J_R(H) has B=Omega(n). Swapping \`3t/2\` incidences is a sequence of rank-one updates, so \`dim_Q ker A>=t/2=n/54\` and \`dim_GF2 ker A>=3t/2=n/18\`. These hold for EVERY cubic H, independently of bipartiteness.

The macros with **multiple real local admissible states** thus exhibit a nontrivial global constraint even with high width and large kernels, but a compact state relation plus graph 2-coloring solves them. This reinforces: large separator width, high algebraic nullity and non-singleton local interfaces alone do NOT prove NP-hardness.

The SAT indicator's expanded Fourier representation could remain huge: even in the 3-model bipartite case, the general support lower bound \`2^d / s\` with s<=3 is exponential in n. By BABEL25's idempotence theorem, fixed-degree Gram idempotence cannot be universally complete on this family, despite easy O(n) macro coloring. This does not prove a generic SAT runtime lower bound.

## 4. Explicit discovery and universal-completion ceiling

The O(n) algorithm assumes an **input certificate** identifying the 27-variable U blocks, their three port incidences, and macro edges. Such a receipt is checked in polynomial time by recomputing EVERY original joined row and verifying the local-port matching; it is NOT assumed that every unlabeled arbitrary legal SCL comes from this template, nor is any general algorithm to discover arbitrary unknown polynomial-size semantic templates established.

The all-n theorem works for any cubic expander H; deterministic finite prism graphs tested below are not themselves claimed to form a uniform expander family. No inference from a finite list of bipartite examples to the all-n theorem is made.

To reach P=NP, one needs an all-input polynomial-time semantic carrier DISCOVERY plus exact description/composition/witness reconstruction, not more constructed template examples.

## 5. Exact independent regression

\`experiments/babel35/bipartite_macro_compression.py\`: tests the identical 27-row U checksum, computes the three new-port local models independently by Boolean DPLL and rational echelon, checks the exact 3-entry \`R\` relation and internal graph connectivity, constructs connected 3-regular prisms with even-cycle/bipartite and odd-cycle/nonbipartite macro graph, verifies every row and graph incidence in the global 27t-variable SCL, reconstructs all 1 or 3 global SAT models, checks GF2 rank/nullity lower bounds, and performs an independent finite exhaustive search over all \`3^t\` macro state assignments for small t. No enumeration of the enormous 2^dim(K) parity cube is used for large t. The program records precise local and global counts and never promotes a width/degree restriction to a general SAT lower bound.

\`\`\`
BABEL35_FIXED_U_THREE_PORT_COMPLETE_MODELS = 3
BABEL35_FIXED_U_Q_RANK = 24
BABEL35_EXACT_PORT_RELATION = {00,01,10}
BABEL35_ALL_N_MACRO_BIPARTITE_COUNT_THEOREM = PROVED
BABEL35_ALL_N_GIVEN_TEMPLATE_SOLVER = O_N
BABEL35_HIGH_WIDTH_AND_Q_GF2_NULLITY_BARRIERS = PRESERVED
BABEL35_UNLABELED_UNIVERSAL_TEMPLATE_DISCOVERY = NOT_PROVED
BABEL35_GENERAL_POLYNOMIAL_SCL_SOLVER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
