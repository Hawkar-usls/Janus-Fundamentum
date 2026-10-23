# BABEL-36 — exhaustive 72,954-port classification and a COMPLETE polynomial 2-SAT compiler for ALL admitted U-macro substitutions

**2026-10-23. Research-only.** Stacked on [BABEL-35 #561] exact head \`f80620b74553e136bdc717b3908ed7c0b4920257\`. This is a strong **fixed-template** polynomial algorithm, not a universal polynomial Exact-One 3SAT solver, P=NP proof, or historically novel result. Main and TRUMP scientific authority remain unchanged.

## 1. Full finite local classification, not sampled candidate selection

Let U be the frozen 27×27 square, cubic and linear positive Exact-One instance from BABEL24 (SHA256 \`9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed\`). Choose ANY three occurrences \`p_i=(row r_i, variable v_i)\` satisfying all:
- distinct row indices \`r_i\`;
- distinct original variables \`v_i\`;
- each chosen variable actually occurs in its selected row.

Select rows in canonical increasing row-index order. There are EXACTLY 72,954 admissible triples. For each, delete all three modified rows and enumerate the complete set of 27-variable Boolean assignments satisfying the remaining 24 rows. For every assignment x, record six boundary bits
\`a_i=x_(v_i)\`, \`b_i=1−sum_(j∈r_i\{v_i}) x_j\`, rejecting any b_i outside {0,1}. Every retained local state has a uniquely reconstructible physical 27-bit assignment.

**Exact finite exhaustive classification:**

| Number of admissible local physical states | Number of distinct port triples |
| ---: | ---: |
| 1 | 71,067 |
| 2 | 1,871 |
| 3 | 16 |
| **TOTAL** | **72,954** |

Moreover in **ALL SIXTEEN** triples with three states, the complete boundary relation is *exactly*:

    R3 = { (a=000,b=000), (a=000,b=111), (a=111,b=000) }.

No selected triple has four or more admissible states. This finite U-specific fact is verified independently TWO ways for EACH of the C(27,3)=2,925 deleted-row subsets: complete unit-propagating Exact-One Boolean DPLL **and** rational Gaussian row echelon followed by complete enumeration of all Boolean free-coordinate assignments (with full original-row verification). The exact boundary classification then checks all selected port triples on that independently equal set of physical models. This is a machine-checkable finite lemma, not an unproved general restriction on every other 27-variable SCL gadget.

## 2. ALL-n full exact reduction of arbitrary U-macro splices to 2-SAT

Let H be ANY simple 3-regular connected graph of t macro vertices (t even), and at every macro vertex choose one of the 72,954 legal triples of U port incidences and any bijection of those ports to H's three incident edges. Swap endpoints of the designated row-variable occurrences across every edge as in BABEL33. The resulting J(H,ports) is square, cubic and linear; if connectedness is wanted, validate it independently. No equality of original port truth values or planted global SAT model is assumed; some macro inputs will be UNSAT.

A polynomial-time verifier checks a supplied macro-template partition and port receipts against EVERY original row and variable occurrence. After this admission, use the exact local tables from the finite classification.

For each macro block i, let \`R_i\` be its complete six-bit (3 exported, 3 required imported) local relation with one physical model per table entry (or, in general, store a representative model and multiplicity; our frozen classification verifies uniqueness per signature). There are ONLY three cases:

1. \`|R_i|=1\`: every port bit is a constant 0 or1.
2. \`|R_i|=2\`: introduce ONE Boolean selector z_i choosing between the two exact local physical models. EVERY one of its six individual boundary bits is either a constant, z_i or ¬z_i.
3. \`|R_i|=3\`: by the fully checked finite lemma the relation is R3. Introduce TWO Boolean selectors a_i,b_i, encode the sole local restriction \`not(a_i and b_i)\` by the 2-CNF clause \`(¬a_i ∨ ¬b_i)\`. The block's three exported bits all equal a_i and its three required incoming bits all equal b_i; reconstruct its unique physical model from the chosen pair.

For each undirected macro edge \`{i,j}\` joining port k of i and port ℓ of j, impose the TWO exact Boolean equalities

    export_(i,k) = import_(j,ℓ),
    export_(j,ℓ) = import_(i,k).

Both sides are literals or constants of the ≤2t selectors. Literal equality converts to two 2-CNF implications; equality to a constant becomes one unit clause; contradictory constants immediately prove UNSAT. Therefore the whole arbitrary macro substitution is equivalent, preserving satisfiability, to a **2-SAT formula on at most 2t Boolean variables and O(t) clauses**. All physical SAT models are reconstructible from 2-SAT assignments plus exact local tables.

**Formal exactness (all n):** Any SAT assignment of original J restricts to one of the fully enumerated local punctured models. The local selector encoding represents it exactly; the cross-edge equations are necessary and sufficient to repair all swapped rows. Conversely any satisfying assignment of the constructed 2-CNF fixes a valid local physical assignment at each block, and the two edge-port equalities guarantee every edited original row has exactly one true literal; all untouched rows are satisfied by local-table construction. The mapping is bijective at the level of physical assignments (up to tautologically duplicate choices, absent in this frozen U table). Hence sound SAT and UNSAT, exact witness restoration and re-verification against every original row.

**Complexity:** The U-specific 72,954-case census is a fixed finite proof/data artifact. Per admitted instance with t template blocks, local relation lookup can be done in fixed table time (or recomputed at constant finite U cost per block), incidence/port-check O(n), 2-CNF compilation O(n), implication SCC O(n), witness reconstruction/recheck O(n). Thus **T_total=O(n)** in the conventional uniform RAM model treating fixed U as a constant gadget; ordinary bit overhead is polynomial. No exponential global state tables or global parity cube enumeration. This is a TRUE complete polynomial decision algorithm for the entire **certified U-macro class** regardless macro graph expansion, rational kernel dimension or whether its global SAT count is 0,1,3 or more. Computing arbitrary exact #SAT through a general 2SAT formula is NOT part of the theorem and must not be claimed polynomial.

### Critical admission firewall

This is NOT a universal algorithm on **arbitrary connected legal SCL**:
- the input must have a verified decomposition into THIS specific frozen U and exactly three spliced occurrences at each block;
- a general unlabeled arbitrary SCL need not admit this template, and no universal polynomial discovery/replacement theorem has been proved;
- other source gadgets can have richer local ternary relations for which boundary CSP need not be 2-SAT.
- there is NO assertion that all connected square cubic linear SCL can be compressed to 2-CNF in polynomial time.

Thus \`P=NP\` is NOT proved. This result shows a third kind of exact long-range carrier that can solve some cases where BOTH graph width and algebraic kernel are linear, without extrapolating from them.

## 3. Exact independent regression protocol

- \`experiments/babel36/u_three_port_census.py\`: check SHA of U, enumerate ALL 2,925 triples of deleted rows, independently compute complete physical models by Boolean DPLL and exact Fraction echelon with 2^k Boolean projections, check equality of model sets; enumerate ALL 72,954 triples with distinct variables, compute exact port relations, confirm 71,067 / 1,871 / 16 and that ALL sixteen size3 tables are R3.
- \`experiments/babel36/u_macro_2sat_solver.py\`: WITHOUT the constructor metadata, derive port triple and corresponding reciprocal edge pairing from raw joined SCL rows plus a supplied *block partition* and frozen U row alignment. Verify legality, source-template rows and port constraints. Build a 2CNF formula using constants, one selector for every two-state local block and two for R3 blocks; solve by independent implication-SCC and reconstruct and check physical models. Negative cases receive a complete 2SAT UNSAT proof from unit contradiction or literal and negation in the same SCC.
- Controls: homogeneous R3 blocks with bipartite and nonbipartite cubic prisms, singleton incompatible mixed-port connected UNSAT, deterministic mixed 1/2/3-state macros, independently enumerate the Cartesian product of local states for small t to cross-check 2SAT SAT status. High-t cases verify all original SCL rows and 2CNF but do not brute-force \`3^t\`.
- Scientific CI gate distinguishes a finite complete U-template theorem from arbitrary SAT input universality.

\`\`\`
BABEL36_U_ALL_72954_THREE_PORT_TABLES = VERIFIED_FINITE
BABEL36_U_RELATION_SPECTRUM = 71067_SINGLE;1871_DOUBLE;16_TRIPLE
BABEL36_U_ALL_TRIPLE_RELATIONS = R3_000_000_000_111_111_000
BABEL36_ALL_N_CERTIFIED_U_MACRO_2SAT_EQUIVALENCE = PROVED
BABEL36_CERTIFIED_U_MACRO_SAT_UNSAT_AND_WITNESS_IN_P = PROVED
BABEL36_EXACT_ALL_INPUT_SAT_COUNTING_IN_P = NOT_PROVED
BABEL36_ALL_CONNECTED_SCL_TEMPLATE_DISCOVERY = NOT_PROVED
BABEL36_UNIVERSAL_SolveLinearCubicXSAT = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
