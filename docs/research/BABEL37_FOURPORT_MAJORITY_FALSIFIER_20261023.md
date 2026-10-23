# BABEL-37 — exact four-port non-bijunctive interface in the SAME U=SCL27

**2026-10-23 — research-only, stacked on BABEL36 Draft PR #562**, exact base head \`4a5f8ddfeedaad0d294b877c2b7b83fe0bd9e5c3\`. Does not modify \`main\` or existing TRUMP gates. This is a concrete **proof-system/representation obstruction** to the direct BABEL36 2-SAT generalization, not a complexity lower bound on general SAT or a resolution of P vs NP. Elementary majority/polymorphism facts are known (Schaefer 1978): https://www.khoury.northeastern.edu/home/lieber/courses/csg260/f06/materials/papers/max-sat/p216-schaefer.pdf .

## 1. Context and finite complete local witness

Frozen connected, square, 3-regular and linear positive Exact-One U has 27 original rows, 27 variables, original-row SHA256 \`9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed\` (BABEL24-36). The FULL 72,954-case BABEL36 census established every **distinct-row/distinct-variable THREE-port** U interface admits only size1/2/3 relations, and all size3 relations are 2-SAT expressible (canonical \`{00,01,10}\` on two uniform port bits). It did **NOT** establish the same for four or more ports.

Choose FOUR distinct row-variable incidences, in this exact index order:

    (r0,v0), (r1,v3), (r2,v7), (r26,v20).

Drop WHOLE rows 0,1,2,26 and keep the other 23 untouched Exact-One equations. The resulting 23×27 rational incidence matrix has rank **23**, with four original free coordinates \`(0,23,25,26)\`. Independently enumerate ALL 2^4=16 rational Boolean-free-coordinate projections, reconstruct pivot values exactly over Q and verify each accepted physical assignment satisfies all 23 untouched rows. Independently execute a Boolean Exact-One DPLL with complete unit propagation over the same 23 rows. Both procedures yield EXACTLY FOUR Boolean assignments:

| Punctured physical true-variable set | Export a=(x0,x3,x7,x20) | Required import b | Admitted Boolean boundary |
| --- | --- | --- | --- |
| (2,6,11,12,16,18,20,22,26) | \`0001\` | \`0010\` | YES |
| (2,3,7,9,13,17,19,23,24) | \`0110\` | \`0110\` | YES |
| (0,2,6,11,12,16,18,20,22,26) | \`1001\` | \`0,-1,0,0\` | NO |
| (0,2,3,7,9,13,17,19,23,24) | \`1110\` | \`0000\` | YES |

Here for port (r,v) the outgoing bit is \`x_v\`, and required incoming bit is \`1−sum_(j in old row r except v)x_j\`. Any required incoming -1 makes the original swapped Exact-One row impossible for a Boolean imported variable. The FULL exact local four-port relation on ordered 8 coordinates (four exports followed by four required imports) is therefore

    R4 = { 0001|0010, 0110|0110, 1110|0000 }.

The incidence graph of U with precisely these four port EDGES (not full rows) deleted is STILL CONNECTED; finite BFS certifies this separately. Four distinct port variables and row indices guarantee legal cross-incidence swaps along a simple 4-regular macro graph.

## 2. Exact non-bijunctive obstruction with explicit majority falsifier

Take the three elements of R4:

    A = (0,0,0,1 | 0,0,1,0)
    B = (0,1,1,0 | 0,1,1,0)
    C = (1,1,1,0 | 0,0,0,0).

Their coordinatewise 3-majority (bit is 1 iff at least 2 of 3 bits are 1) is

    m = maj(A,B,C) = (0,1,1,0 | 0,0,1,0).

This m is NOT in R4. Thus R4 is **not majority closed** and in particular **not bijunctive**.

Stronger, no formula of pure 2-CNF over these 8 original boundary variables plus ANY collection of existentially eliminated auxiliary Boolean variables can have exactly R4 as its projection onto those boundary variables. **Proof:** every 2-literal Boolean clause is closed under coordinatewise majority: otherwise the majority assignment makes both literals false, implying by pigeonhole that some original one of the three satisfying assignments made both false. Intersections (conjunction) preserve majority closure. Existential projections preserve it as well: choose arbitrary witnesses for three projected tuples, take the majority of their full satisfying assignments, then project the resulting satisfying assignment. Therefore ANY existentially represented 2CNF boundary relation is majority closed, contradicting this explicit m.

This theorem **ONLY blocks exact port-preserving 2CNF-relation representations**. It does not exclude a separate polynomial method with non-literal port encodings, more expressive constraint relations, polynomial-size circuits, structural exploitation of macro graphs, or another still-undiscovered universal algorithm. It does not prove this finite R4 macro family itself NP-hard.

**Sharp local contrast:** the known BABEL36 classification is complete for THREE-port U interfaces; this found FOUR-port U instance shows that simply extending its 2SAT method to one extra boundary occurrence FAILS. Minimality here means only "3 ports from frozen U already certified bijunctive; this 4-port instance is not", not a universal CSP arity minimum.

## 2B. Stronger classification: GENERIC CSP({R4}) is NP-complete (not the special macro family)

The full six-case Schaefer dichotomy applies to the Boolean relation R4 regarded as an **unrestricted 8-ary constraint**, where a CSP instance can place its eight argument positions on arbitrary Boolean variables (possible identifications included), rather than only on the reciprocal port-edge wiring of our U macro graph. R4 has neither all-zero nor all-one 8-bit tuple. The three explicit R4 states A,B,C above supply counterexamples to all remaining tractable closure classes:

    A AND B = 0000|0010  NOT IN R4.  [not Horn]
    A OR  B = 0111|0110  NOT IN R4.  [not dual-Horn]
    A XOR B XOR C = 1001|0100  NOT IN R4.  [not affine]
    maj(A,B,C) = 0110|0010  NOT IN R4. [not bijunctive]

By Schaefer's Boolean CSP dichotomy (1978; cited above), **unrestricted CSP({R4}) is NP-complete**. This theorem is about the generic CSP language consisting of ONE exactly specified 8-ary relation R4. It does not establish an NP-hardness reduction preserving the actual reciprocal directed edge-swap wiring, four-regular macro restriction, cubic/linear legality, connectedness or witness reconstruction of the physical original SCL construction. Applying the generic CSP classification directly to that STRICT macro subclass would be an invalid leap. No such transfer is claimed here.

This makes the scientific boundary sharply visible: an already verified tiny SCL gadget can realize a **non-Schaefer relation** at four ports, whereas all its legal three-port relations in BABEL36 remained bijunctive. Any purported universal simple 2SAT boundary compiler must address that counterexample with genuinely more expressive operations and a proven global polynomial decision mechanism; mere polynomial size of a CSP representation does not solve an NP-complete CSP.

## 3. Exact all-n mapping to a 3-state graph constraint network

For any simple connected 4-regular macro graph H with an arbitrary bijection between its four incident macro edges and the four designated U ports at each macro vertex, exchange the incidence endpoints for each macro edge as BABEL33-36. The resulting explicit J4(H) is connected square cubic linear SCL with n=27|V(H)| original variables (note: macro degree4 does NOT alter the original SCL degree3; it assigns four DISTINCT occurrence slots from different rows/variables of each 3-regular base U).

Each physical SAT model restricts on each U copy to one of the above four punctured assignments; the inadmissible negative import candidate is excluded. Thus each macro vertex selects exactly one of three states A,B,C in R4. Each macro edge between vertex u port i and vertex v port j imposes EXACTLY the two equalities

    export_u[i] = import_v[j],
    export_v[j] = import_u[i].

This exact 3-state constraint-network representation is SEMANTICALLY BIJECTIVE to physical SAT assignments for ALL admissible H, independent of expansion, tree width or Q/GF2 nullity. It yields a compact **representation O(|V(H)|)** of the CSP but **NOT** a polynomial SAT solver for arbitrary H: solving the resulting general 3-state graph CSP still requires proof of a polynomial algorithm or a special global invariant. Explicit representation size ≠ polynomial satisfiability.

### Finite exact SAT and UNSAT controls

1. A simple 4-regular complete macro graph K5, with deterministic sorted-neighbor-to-port mapping, is a legal connected SCL135. Its complete 3^5=243 macro-state census gives **ZERO** satisfying state assignments, hence an exact UNSAT result via the all-n bijection; independently verify every original SCL incidence.
2. A simple 4-regular bipartite K4,4 macro graph with four-edge-coloring \`port(i,4+j)=(i+j) mod4\` at BOTH endpoints is a legal connected SCL216. Independent 3^8=6561 state enumeration gives **ONE** global physical SAT assignment, and it is explicitly verified against all 216 original Exact-One rows. The macro coloring ensures the B-state \`0110|0110\` is locally compatible everywhere.
3. Exact proof of local BOUNDARY relation and non-bijunctivity is checked by independent DPLL/Fraction and a literal majority falsifier; no probabilistic claim. Macro counts are complete brute-force enumerations of **3^t states**, NOT of 2^dim(K) parity points, and for large t no finite brute force claim is made.

These are connected legal positive Exact-One SCLs that expose the first exact step BEYOND BABEL36's local bijunctive carrier.

## 4. Universal target remains OPEN

The actual requested all-SCL polynomial \`SolveLinearCubicXSAT\` would require one **uniform polynomial procedure on every admissible connected SCL input**, with exact semantics, intermediate representation size, discovery and construction, SAT witness, UNSAT decision and total bit complexity. A port-CSP with three local choices is not sufficient if its global consistency can be hard. Here we only refute the unproven "all compact SCL port relations are directly 2SAT" hypothesis. The finite U gadget counterexample does not show that no other compressed carrier can succeed.

\`\`\`
BABEL37_FOUR_PORT_U_PUNCTURED_Q_RANK = 23
BABEL37_FOUR_PORT_TWO_INDEPENDENT_COMPLETE_CENSUSES = 4
BABEL37_EXACT_FEASIBLE_R4 = {0001|0010,0110|0110,1110|0000}
BABEL37_MAJORITY_FALSIFIER = 0110|0010_NOT_IN_R4
BABEL37_R4_EXISTENTIAL_2CNF_REPRESENTATION = IMPOSSIBLE
BABEL37_GENERIC_UNRESTRICTED_CSP_R4 = NP_COMPLETE_BY_SCHAEFER
BABEL37_SPECIAL_U_MACRO_NP_HARDNESS = NOT_ESTABLISHED
BABEL37_ALL_N_CONNECTED_MACRO_TO_3STATE_CSP = PROVED
BABEL37_GLOBAL_3STATE_CSP_IN_P = NOT_PROVED
BABEL37_UNIVERSAL_SCL_SOLVER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
