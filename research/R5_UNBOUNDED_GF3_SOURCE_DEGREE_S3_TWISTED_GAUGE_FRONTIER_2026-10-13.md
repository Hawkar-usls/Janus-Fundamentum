# R5 — Unbounded GF3 source degree assault: S3 twisted native SCL, all-input tree gauge, exhaustive K4 and K3,3 elimination

Date: 2026-10-13 Europe/Kyiv.
Branch: research/r5-cubic-flow-smith-pair-20261011
PR: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/516 (DRAFT); main untouched.
Authenticated starting HEAD: bf5fe0c6f5fa5519a62a8023f8f02758b0f65110.

## 0. NONNEGOTIABLE global theorem target

User's goal is ONE deterministic uniform n^C bit-time sound-and-complete SolveLinearCubicXSAT on EVERY square+cubic+linear positive Exact-One original SCL, returning original SAT witness or correct UNSAT. Equivalent required positive missing piece is a polynomial GLOBAL exact source LoopZeroTest. No such solver is constructed and P vs NP is OPEN.

The prior checkpoint gave an infinite connected 3-edge-connected original SCL90+9k family whose independent GF3 Boolean PC proof degree is at least FOUR (frozen J5 degree3 dual plus source-preserving triangle inflation). That does NOT demonstrate DEGREE→INFINITY. Such a proof would require an independently verified native SCL sequence with `deg_min(F_k)` unbounded, or a rigorous bounded-degree-back-simulation reduction importing a known independent unbounded-degree family. Both gates remain UNPROVED.

This checkpoint tests one mathematically new original-source construction for that purpose: local S3-twisted cubic edge-color constraints, source isomorphism by tree gauge, and two complete finite graph tests. Its scientifically accurate outcome is NEGATIVE for the unbounded-degree aim on K4 and K3,3, while offering a source-certified larger-graph construction framework.

## 1. ALL-CUBIC-GRAPH exact S3-twisted native SCL theorem (PROVED)

Let G=(V,E) be any finite SIMPLE 3-regular graph. For EVERY incidence (v,e), independently choose a permutation `p_(v,e) ∈ S3` on {0,1,2}, without assuming a globally untwisted color system.

Create one ORIGINAL 0/1 variable `x_(e,c)` per global edge e and c in {0,1,2}.
Create:
- One Exact-One3 row `sum_c x_(e,c)=1` per original graph edge.
- For each graph vertex v and each LOCAL color a∈{0,1,2}, one Exact-One3 row
  `sum_(e incident to v) x_(e,p_(v,e)(a))=1`.

For any simple cubic G, `|E|=3|V|/2`. There are exactly `3|E|` Boolean original SCL variables and `|E|+3|V|=3|E|` rows. Every row has three distinct variables. Every variable x_(e,c) occurs EXACTLY in its own edge row and in one vertex-row for EACH endpoint of e, therefore in exactly three rows. Two rows share at most one variable: distinct edge rows disjoint; any edge-row and vertex-row intersect in ≤1; and vertex rows at distinct vertices can share an edge indicator only for the unique graph edge between them (G SIMPLE). Hence original square/cubic/linear C4-free Positive Exact-One SCL source, no unary clauses and no altered CSP.

Exact semantic bijection:
A source SAT assignment chooses one global color c_e per e; the three LOCAL colors seen at each v are `p_(v,e)^(-1)(c_e)`, and the vertex Exact-One rows require exactly one incident edge of each local color. Conversely every such locally-compatible signed coloring gives the unique native source SAT witness. This is an all-input theorem, not an empirical guess.

Thus the signed local-color gain-graph family is a legal stress-test SUBCLASS inside the user's NP-complete original SCL. No result restricted to this family proves the goal for ALL SCL.

## 2. ALL-CUBIC-GRAPH S3 spanning tree gauge normalization (PROVED)

For arbitrary local vertex color gauge g_v∈S3 and global edge color gauge h_e∈S3, define transformed ports
 `p'_(v,e)=h_e ∘ p_(v,e) ∘ g_v`.
This is an exact variable/row ISOMORPHISM of the native original source:
original variable x_(e,c) is relabeled x'_(e,h_e(c)) and old vertex row at local color a maps to the new vertex row at `g_v^(-1)(a)`. Therefore source SAT count, exact original Boolean GF3 polynomial calculus proof degree, existence of source primal, and dual certificates are all INVARIANT under this gauge.

Choose root vertex, a BFS spanning tree T. At root set g_root=id. Traverse tree outward. For its parent u and child v linked by edge e, choose
 `h_e=(p_(u,e) ∘ g_u)^(-1)`,
 `g_v=(h_e ∘ p_(v,e))^(-1)`.
Then BOTH port incidences on e become identity. For any non-tree chord e=(u,v) choose `h_e=(p_(u,e) ∘ g_u)^(-1)`: one endpoint becomes identity and the other retains ONE arbitrary S3 permutation, its cycle holonomy. Therefore EVERY signed source on G is SOURCE-ISOMORPHIC to a native canonical source determined by at most
 `6^beta,  beta=|E|-|V|+1`
choices, where beta is the dimension of G's cycle space (number independent chords). We DO NOT falsely assert these forms are pairwise non-isomorphic; the upper bound suffices to be exhaustive.

The algorithm is linear in graph size apart from manipulating constant-sized S3 permutations. Finite source audits randomly generate arbitrary old incidence permutations and construct the exact source variable permutation and row map; all original rows are checked for exact multiset equality after mapping.

**Important frontier:** for cubic graphs `beta=|V|/2+1`, and hence `6^beta` is EXPONENTIAL in graph size. The gauge theorem does NOT deliver a polynomial all-SCL algorithm and cannot be used to assume fixed effective holonomy dimension on hard sources.

## 3. Exhaustive K4/SCL18 outcome — 216/216 forms, all UNSAT degree2

Graph K4: |V|=4, |E|=6, beta=3, n=3|E|=18. EXACT 6^3=216 canonical S3 chord-holonomy patterns checked, not merely sampled. Independent native construction audited original square cubic linear promises for each.

Scientific counts:
- 186 canonical patterns SAT, with directly verified original SAT witnesses from independent graph-color assignment checker;
- 30 canonical patterns UNSAT;
- **ALL 30 UNSAT sources have independently source-replayed GF3 Boolean degree-TWO polynomial-calculus refutations**;
- ZERO UNSAT sources lack V2 certificates; zero unknown/truncated scientific status.

Because EVERY arbitrary incidence twist on K4 gauge-normalizes by an actual SOURCE isomorphism to one of these 216 forms, theorem for arbitrary K4 port permutations:
```
F(K4,p) UNSAT ⇒ 1 ∈ V2(F(K4,p))
```
for ALL p, unconditionally proved by symbolic gauge theorem + exhaustive finite exact source proof.

Authoritative CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38385940499 — SUCCESS.
Files:
`experiments/r5_universal_twisted_s3_cycle_gauge_normal_forms.py`,
`.github/workflows/r5-twisted-s3-cycle-gauge-exhaustive.yml`.

Prior random K4 control:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38385637923 — SUCCESS, 20 random twisted K4 sources, four UNSAT, all V2 refuted. The complete gauge audit supersedes this finite sample.

## 4. Exhaustive K3,3/SCL27 outcome — 1296/1296 forms, all UNSAT degree2

Graph K3,3: |V|=6, |E|=9, beta=4, n=27. EXACT 6^4=1296 canonical S3 chord-holonomy patterns checked, no sampling.

For EVERY form, a deterministic source exact-cover DFS returned either a source-verified original SAT assignment, or a COMPLETE source UNSAT DAG with all original Exact-One branches covered, independently source-replayed:
- **1186 SAT** sources, witnesses original-source checked;
- **110 UNSAT** sources, all with source-replayed exact-cover DAG (largest dead-mask DAG 40 states);
- ALL 110 original UNSAT sources possess independently source-verified GF3 Boolean DEGREE-TWO polynomial-calculus refutations;
- ZERO V2-resistant sources; ZERO resource-limit statuses.

Hence by the all-input tree-gauge/source-isomorphism theorem:
```
For EVERY arbitrary signed incidence twist p on K3,3,
  F(K3,3,p) UNSAT ⇒ 1∈V2(F(K3,3,p)).
```
This is a finite EXACT theorem for this graph, not a general theorem for all cubic graphs or for all native SCL.

Authoritative CI:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38386102119 — SUCCESS.
Files:
`experiments/r5_universal_twisted_k33_1296_exact_gf3_degree_frontier.py`,
`.github/workflows/r5-k33-1296-twisted-native-proof.yml`.

Additional supporting theorem/engine:
`experiments/r5_universal_twisted_cubic_edge_coloring_native_scl_degree_gate.py`
workflow `.github/workflows/r5-twisted-cubic-s3-native-scl-gate.yml`
CI #38385637923 SUCCESS.
This checks the semantic signed edge-color matching directly on graph color labels and matches independent ORIGINAL source SAT/UNSAT answers.

## 5. Actual external PC hardness and exact unmatched transfer gate

Austrin–Risse, *Perfect Matching in Random Graphs is as Hard as Tseitin*, ECCC TR21-021 revised 2022:
https://eccc.weizmann.ac.il/report/2021/021/
Proves degree Ω(n/log n) for certain regular odd-vertex perfect-matching systems in Polynomial Calculus over fields of characteristic ≠2, which DOES include our F3 field, but DOES NOT automatically apply to our positive 3-uniform source with every column and row degree3.

Conneryd–de Rezende–Nordström–Pang–Risse, *Graph Colouring Is Hard on Average for Polynomial Calculus and Nullstellensatz*, FOCS 2023 / ECCC TR25-032:
https://eccc.weizmann.ac.il/report/2025/032/
Proves LINEAR original proof-degree lower bounds for sparse random GRAPH VERTEX 3-coloring over any field, also including F3. It does NOT itself prove an original SCL lower bound.

General all-input degree-transfer lemma needed:
Given base hard polynomial system A(z)=0 with known degree lower bound D(N), and source-legal target SCL B(x)=0, construct for EVERY target source indicator x_j a Boolean-valued polynomial P_j(z) of bounded degree C independent of N, plus explicit bounded-degree base-original generator identities certifying:
- every target ORIGINAL Exact-One polynomial B_i(P(z)) belongs to the base ideal with low-degree multipliers/certificate;
- every P_j(z) satisfies the Boolean identities modulo base Boolean equations with low-degree certificates.

Then substituting P_j(z) for x_j in a hypothetical degree-d target SCL refutation gives a base refutation of degree O(C d + C_0). Thus degree(SCL)≥Ω(D(N)) under suitable constant degree costs. This direction is essential; ordinary semantic NP-hardness reduction, or the EXISTENCE of a satisfying gadget extension, does not prove such a degree-preserving polynomial interpretation.

**MISSING:** A source-legal gadget/reduction with this explicit bounded-degree algebraic back-simulation. The new signed S3 color ports provide a useful native target normal form, but NO currently verified mapping from hard Tseitin/odd perfect-matching/vertex coloring systems to them satisfies the strong degree transfer criterion. Accordingly UNBOUNDED native SCL degree remains NOT PROVED.

## 6. SCIENTIFIC terminal, not a solver

```
S3_ALL_SIMPLE_CUBIC_PORT_TWISTS_CREATE_LEGAL_NATIVE_SCL = PROVED
S3_SPANNING_TREE_GAUGE_SOURCE_ISOMORPHISM_ALL_SIZES = PROVED
S3_CANONICAL_COUNT_LE_6_POWER_BETA = PROVED
S3_TWISTED_K4_ALL_216_GF3_V2_COMPLETENESS = PROVED
S3_TWISTED_K33_ALL_1296_GF3_V2_COMPLETENESS = PROVED
S3_TWISTED_LARGE_GRAPH_UNBOUNDED_PC_DEGREE = NOT_PROVED
HARD_PM_OR_VERTEX_COLORING_TO_SCL_DEGREE_TRANSFER = NOT_CONSTRUCTED
ALL_SCL_ANY_FIXED_D_COMPLETENESS = OPEN
UNIVERSAL_EXACT_POLY_LOOPZERO = NOT_CONSTRUCTED
SolveLinearCubicXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```

NO P=NP announcement, no false claim of a native expander proof lower bound, no semantic contradiction with prior J5/SCL90 degree>=4 (the latter is an UNTWiSTED cubic graph on TWENTY vertices; its graph topology and cycle rank are much larger than K4/K33).
