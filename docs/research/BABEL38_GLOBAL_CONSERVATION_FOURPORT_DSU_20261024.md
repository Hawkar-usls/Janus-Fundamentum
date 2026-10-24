# BABEL-38 — ALL-n global boundary conservation eliminates non-bijunctive state; exact DSU #SAT for four-port U macros

**2026-10-24, RESEARCH ONLY.** Successor to BABEL-37 Draft PR #563, exact source head \`5333d4a7c1f806424d60ee51f6a06c7973906bfc\`. No changes to \`main\` or TRUMP frozen authority. No P=NP claim, no generic CSP hardness or generalized tractability asserted.

## 1. The exact BABEL-37 local relation

The previous exact independently certified four-port U=SCL27 relation (ports in canonical order (r0,v0),(r1,v3),(r2,v7),(r26,v20)) is the three-member relation on four exported bits a and four demanded imported bits b:

    A = 0001 | 0010
    B = 0110 | 0110
    C = 1110 | 0000.

The one-to-one physical assignments for A/B/C are exactly certified by BABEL37's full DPLL and Q-projection. An arbitrary connected simple 4-regular macro graph H is wired by swapping one incidence from each end of every macro edge. The joined formula is a connected legal square/3-uniform/3-regular/linear Exact-One instance with n=27t variables, given a certified U-block mapping.

## 2. ALL-n boundary balance theorem (extends earlier BABEL29 mod-3 lemma)

Take ANY finite collection of components with any number of selected distinct row-variable ports; in particular the four-port U components. Let a_(v,i) be the original value of the exported variable and b_(v,i) the required Boolean imported bit on each modified row. For each local punctured assignment to block v, row-counting gives

    3|x_v| = (n_v-r) + sum_i ((1-b_(v,i))+a_(v,i))
            = n_v + sum_i (a_(v,i)-b_(v,i))

provided each original block was square, 3-regular and all its n_v original rows were considered. This exact identity is stronger than the congruence mod3: the local net flux Δ_v is exactly 3|x_v|-n_v.

Across ANY closed incidence-swap network, each macro edge {u,v} with ports i,j imposes a_(u,i)=b_(v,j) and a_(v,j)=b_(u,i), so by summing all incidences every exported bit occurs as one imported bit:

    Σ_v Σ_i(a_(v,i)-b_(v,i))=0.          (GLOBAL CONSERVATION)

For the FROZEN R4 relation, net fluxes are **Δ(A)=0, Δ(B)=0, Δ(C)=3**. Therefore every satisfying joined physical assignment obeys

    0 = Σ_v Δ(state_v) = 3 * N_C    =>  N_C=0.

**Theorem:** NO globally satisfying four-port U-macro instance can use local state C, for ANY macro graph and ANY bijection of ports to edges. This theorem is ALL-n and exact, not a finite check or a heuristic propagation rule. It does not say C is locally invalid: C is locally valid, but globally excluded by conservation.

## 3. Exact classification of ALL 16 directed port-pair link relations after C elimination

With only states A=0 and B=1, a link from port i at u to port j at v imposes the two directed reciprocal equalities. The exact allowed binary pairs (state_u,state_v) are:

| i→j | allowed pairs | logical normal form |
| --- | --- | --- |
| 0→0 | 00,01,10,11 | TRUE |
| 0→1 | 00,10 | state_v=0 |
| 0→2 | none | FALSE |
| 0→3 | 01,11 | state_v=1 |
| 1→0 | 00,01 | state_u=0 |
| 1→1 | 00,11 | state_u=state_v |
| 1→2 | 11 | both1 |
| 1→3 | 01 | u0,v1 |
| 2→0 | none | FALSE |
| 2→1 | 11 | both1 |
| 2→2 | 11 | both1 |
| 2→3 | 00 | both0 |
| 3→0 | 10,11 | state_u=1 |
| 3→1 | 10 | u1,v0 |
| 3→2 | 00 | both0 |
| 3→3 | 11 | both1 |

These 16 entries are exhaustively generated from the original BABEL37 8-bit R4 A/B states, NOT manually trusted in source. Every edge is thus either (a) immediately inconsistent, (b) local unit pins, (c) equality, or (d) tautology. No disequality or higher-arity coupling survives global conservation.

## 4. FULL polynomial SAT, UNSAT AND EXACT #SAT algorithm on the admitted four-port U-macro family

Input: original full SCL incidence rows with a **certified partition into aligned copies of frozen U** and exactly four cross-incidence swaps per U block. The checker verifies every original row, every imported port occurrence and inverse matching, square/3regular/linear connectedness, and the simple 4regular macro graph. The solver receives NO planted model, macro edge list or construction receipt; it extracts actual port edges from raw original row incidences and the declared aligned U partition.

1. Create Boolean state variable z_v for each U block, where 0=A and 1=B.
2. For each recovered macro edge, look up its exact A/B allowed pair from the generated 16-case truth table. If empty return UNSAT (proven by conservation and the exact R4 local relation); if it is an equality, union v,u in a disjoint-set union (DSU); if it pins one/both states, store the required 0/1 value; if tautological, do nothing.
3. Collapse the DSU. If ANY DSU class has contradictory pins, return UNSAT with an independently checkable contradiction certificate (exact edge-state restrictions and class equality/pin provenance). Otherwise each unpinned DSU class admits BOTH A and B, independently of other classes. Let c be their count. Then **exactly** \`2^c\` physical SCL SAT models exist. Produce one witness by picking 0 for every unpinned class and instantiating the BABEL37 certified physical U assignments. Verify EVERY original Exact-One clause.

All-n theorem: By BABEL37's exact local-to-global semantic bijection, EVERY global physical model corresponds to an assignment to A/B/C. Global flux removes all C. The 16-case finite table is exact, hence satisfying A/B networks are **precisely** the finite systems of equality and pins classified above. DSU computes all equivalence classes and exact model cardinality; each class assignment yields one physical U model per block, bijectively. Moreover, in the exact FULL-port 4-regular macro setting, port2 forces every class, so c=0 in every satisfiable case and #SAT is 0 or1. Thus SAT/UNSAT/count/witness are COMPLETE for ALL admitted four-port U macro inputs, including arbitrary connected simple degree4 macro graphs and all port bijections.

**Time & bit complexity:** extraction and certification O(poly(n)), 16-entry fixed table, DSU O(n α(n)), exact integer output 2^c uses ≤n bits, witness construction/replay O(n). For a supplied aligned U-block partition (not necessarily a universally available one), this is a **polynomial exact #SAT/SAT/UNSAT algorithm on that entire family**. The stronger exact-count property distinguishes this from the generic BABEL36 2-SAT reduction, where arbitrary 2-SAT #SAT is not asserted polynomial.

The generic Boolean CSP({R4}) with UNRESTRICTED 8-tuple placements remains NP-complete by Schaefer. The reciprocal macro incidence-swaps are a **strictly smaller** constraint class with a forced global balance invariant. Thus there is no contradiction: NP-completeness does not transfer automatically across the wiring restriction.

### Generalized safe pruning: one-sided sign flux

On any certified closed network with exact local tables T_v, if all candidate rows have Δ>=0 then every global solution must choose Δ=0 locally; likewise if all Δ<=0. This is an **all-n sound polynomial local pruning step given the exact tables**, but it is NOT sufficient to solve all networks when positive and negative Δ co-occur. The latter can balance, and conservation alone cannot decide global satisfiability. Determining whether arbitrary local tables have polynomially bounded construction and composition remains OPEN.

## 4B. STRONGER all-n uniqueness lemma: every port-2 link fixes its block

The 16-case table above has an even stronger implication for the **complete** degree-4 macro family, where EVERY U block uses each port exactly once. Consider the edge incident to the distinguished port2 on any block v:

- port2 ↔ port0: allowed set EMPTY => UNSAT.
- port2 ↔ port1: allowed pair is B,B, so v MUST be B.
- port2 ↔ port2: allowed pair is B,B, so v MUST be B.
- port2 ↔ port3: allowed pair is A,A, so v MUST be A.

Therefore **each block's state is uniquely determined by the location of the opposite endpoint of its port2 edge** in ANY satisfiable network. All states on all t blocks are forced. Checking these states against all original cross-edge equations is complete, and the full physical SAT model, if it exists, is UNIQUE:

    #SAT(J4(H))∈{0,1} for EVERY connected or disconnected certified full-port H.

This is stronger than the generic DSU theorem's \`2^c\` count: in the genuine complete 4-regular U macro family c=0 always if satisfiable. The simpler **linear-time direct port2 forcing solver** and the generic equality/pin DSU solver must give the SAME answer and reconstructed physical model; the independent CI compares both. SAT and UNSAT certificates consist of the full extracted port mapping, exact local R4 lemma, global balance exclusion of C, the forced A/B states from port2, and complete replay of every edge relation. This is an all-n uniqueness theorem, not a claim that the representation cannot encode computationally difficult relations under different, less constrained wiring.

## 5. Independent reproducibility and scientific limits

- \`experiments/babel38/fourport_global_balance_dsu.py\` builds the exact 16 table from independently recited R4 A/B bits, recognizes and audits original SCL row input and all four reciprocities, computes DSU exact #SAT and reconstructs witnesses. On K5 and K4,4 and several seeded random 4regular connected graphs, compares the result with a **FULL 3^t** local-state brute-force oracle (small t only); on larger instances performs exact template verification and row replay without 3^t enumeration.
- \`experiments/babel38/independent_fourport_csp_oracle.py\` independently enumerates macro states from actual punctured U rows, rather than importing the DSU table, tests label/port permutations and separate contradiction cases, and checks the full physical SAT rows for witnesses.
- CI additionally checks the scientific no-general-claim guard.

\`\`\`
BABEL38_ALL_N_CLOSED_NETWORK_EXACT_NET_FLUX_ZERO = PROVED
BABEL38_R4_STATE_C_ELIMINATION = PROVED_ALL_N
BABEL38_REDUCED_16_LINK_TABLE = VERIFIED_EXACT
BABEL38_FOURPORT_U_MACRO_FULL_SAT_UNSAT_EXACT_COUNT = PROVED
BABEL38_ADMITTED_FOURPORT_U_MACRO_COMPOSITION_IN_P = PROVED
BABEL38_ARBITRARY_CONNECTED_SCL_LOCAL_RELATION_DISCOVERY = OPEN
BABEL38_UNIVERSAL_SolveLinearCubicXSAT = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
