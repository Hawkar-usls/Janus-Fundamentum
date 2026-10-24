# BABEL-40 — signed-flux counterexample to global 2-SAT closure; exact all-n reciprocal arc-consistency extension

**24 October 2026, RESEARCH ONLY.** Stacked on BABEL-39 Draft PR #565 at exact HEAD \`f535d0c969d764831b366d80f486f077fce8a261\`. This addresses the actually missing case: arbitrary legal connected SCL in which **both positive and negative local net flux states** are feasible, so global \`ΣΔ=0\` cannot eliminate a non-bijunctive relation. This is a new **falsifier of a universality shortcut** and a generic sound preprocessing extension, not a general polynomial SolveLinearCubicXSAT. No frozen TRUMP authority or mainline changes.

## 1. Complete concrete SCL54 witness: local +3 and -3 states genuinely match

Take two independent copies of the frozen connected square cubic linear U=SCL27 with SHA256 \`9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed\`. In each copy select exactly four occurrences in **distinct rows AND distinct original variables**.

Positive-side ports in index order:

    A = (row0,var0), (row1,var3), (row2,var7), (row26,var20).

This is BABEL-37's exact local R4, established independently by complete Boolean DPLL and rational echelon. Its three valid boundary signatures and fluxes \`Δ=Σa−Σb\` are

    A0 = 0001|0010   Δ=0;
    A1 = 0110|0110   Δ=0;
    A2 = 1110|0000   Δ=+3.       [NON-BIJUNCTIVE MAJORITY WITNESS]

Choose DIFFERENT negative-side ports, also in the precise edge connection order:

    B = (row0,var0), (row7,var5), (row8,var10), (row1,var6).

Its untouched 23 original rows admit exactly TWO Boolean assignments with valid Boolean imports:

    B0 = 0000|0000   Δ=0
    B1 = 0000|1110   Δ=−3.

The B1 local physical ones are \`(3,7,9,13,17,19,23,24)\`, i.e. eight true variables; B0 has the frozen nine true indices \`(2,3,7,9,13,17,19,23,24)\`.

Join via exactly FOUR reciprocal incidence exchanges \`(A_i,B_i)\` for i=0,1,2,3, adding27 to all B row/variable indices. The result is a **legal connected** original SCL with n=m=54, every row/variable degree3, pair-linear incidence and no disjoint padding. Both factors remain connected after their four port edges are deleted, and inverse swaps reproduce the original blocks.

The actual SAT witness is:

    side A (offset0):   (0,2,3,7,9,13,17,19,23,24)   [A2, Δ=+3]
    side B (offset27):  (3,7,9,13,17,19,23,24)     [B1, Δ=−3]

Their boundary signatures exactly match reciprocally, and every ORIGINAL joined Exact-One row is satisfied. INDEPENDENT full GF2 nullspace enumeration confirms kernel dimension d=3, precisely 8 parity-space candidates and EXACTLY ONE physical SAT assignment (the above).

**Crucial falsifier:** Each local domain also has a zero-flux state, so the complete integer prefix/suffix global flux support algorithm of BABEL39 retains ALL THREE A states and BOTH B states. In particular A2=+3 survives because B1=−3, and both A0/A1=0 survive because B0=0. R4 remains **not majority-closed**, so it cannot be exactly compiled into 2-CNF with any existential auxiliaries. Therefore the direct BABEL39 \`GLOBAL_FLUX → EXACT_2CNF\` strategy has an unavoidable \`UNKNOWN_NOT_BIJUNCTIVE\` on this ACTUAL SAT legal connected SCL54, even though its SAT witness exists.

This is not a claim that the special small system is computationally hard. It is a valid, independently checkable **counterexample to a proposed general representation-completeness lemma**. The previous BABEL38 all-positive \`C\` exclusion does not apply when negative flux can balance it.

## 2. Generic all-n reciprocal port arc-support theorem

Let F be ANY original legal SCL input with a **certified exact component decomposition** and complete local boundary-state sets \`R_i⊆{0,1}^{2r_i}\`, not necessarily isomorphic or small U copies. For a reciprocal swapped port edge \`(i,p)↔(j,q)\`, the *actual* constraints are

    export_i[p] = need_j[q],
    export_j[q] = need_i[p].

A local state s∈R_i has arc support across that edge iff at least one t∈R_j satisfies **both** equations. A state with no such neighbor support can NEVER belong to a global physical SAT assignment. Therefore it may be deleted safely. Repeatedly remove states that lack support along ANY incident edge until no table changes. This operation preserves ALL physical SAT assignments for arbitrary local relations, even with positive and negative Δ states.

**Proof:** Restrict any physical SAT assignment to all components. Its boundary signatures satisfy the two reciprocal edge equations, so each such signature has the neighboring one as support. By induction over deletion rounds, no globally SAT signature is ever deleted. If a domain empties, the original input is UNSAT. A nonempty arc-consistent fixed point is only NECESSARY for SAT; it is NOT a universal complete decision procedure.

**Time:** Let \`M=Σ_i|R_i|\`, \`E\` the number of reciprocal port edges, \`N\` the total original variable size. At most M strict deletion rounds are possible. Directly checking all pairs of states per edge costs conservatively \`O(M·E·max_i|R_i|²)\` bit-comparison operations; hashing each neighbor's two-port projection improves this but is not essential. Given complete tables built by BABEL39 using \`2^{k_i}poly(n_i)\` local rational projections and ports \`r_i\`, the total operation is polynomial for max local k_i and port count r_i bounded by \`O(log N)\`. The all-n soundness proof itself does NOT depend on these bounds; they apply to the overall time.

After arc consistency, reapply the exact integer global zero-flux support filter and then independently construct/check the exact 2-CNF for every surviving majority-closed local relation. On acceptance the existing 2-CNF decision and witness reconstruction remain semantically exact. On residual non-bijunctive relations, return **UNKNOWN** rather than misclassifying them.

## 3. Exact ALL-n signed four-port macro family, genuinely surviving flux

Let H=(L⊔R,E) be ANY connected simple 4-regular bipartite macro graph with **any proper 4-edge coloring** c:E→{0,1,2,3}. By the standard bipartite edge coloring theorem, such a coloring exists and is computable in polynomial time (but can also be supplied and verified). At each macro vertex in L place U with positive port tuple A; at each macro vertex in R place U with negative port tuple B. Swap corresponding original row-variable occurrences across each macro edge of color c at both ends.

The result J±(H) is a connected legal SCL with n=27|V(H)| rows and variables: both four-port-deleted U incidence graphs remain connected; every port's row and variable occurrence is unique, and a simple macro graph has no repeated pair of blocks. Preserve the **local planted physical SAT assignment A2 on EVERY left macro vertex and B1 on EVERY right macro vertex**. Since A2 exports 1110 and demands 0000, while B1 exports0000 and demands1110, every colored reciprocal edge matches and all original Exact-One clauses are satisfied.

**All-n exact uniqueness stronger than mere SAT:** On any right block, BOTH B0 and B1 export four zeros. Therefore on its neighboring left block, every required imported bit is 0. Only A2 has all four \`need_A=0000\`; A0 needs0010 and A1 needs0110. Hence every left block is FORCED to A2. Its exported 1110 bits force every right block to B1, since only B1 has \`need_B=1110\`. Therefore:

    #SAT(J±(H)) = 1 for EVERY such properly edge-colored connected 4regular bipartite H.

The exact local relation census and reciprocal edge semantics prove this for ALL macro sizes; no global enumeration is needed. The pure additive flux DP by itself still retains all local states because there are both ±3 and 0 candidate choices and |L|=|R|, so it cannot make the non-bijunctive A relation majority-closed. The new **GENERIC arc consistency**, however, reduces every domain to one state in at most two rounds, after which exact 2-CNF and full physical witness verification complete in polynomial time on the admitted class.

With t=|V(H)| blocks, the GF2 incidence rank of the original U is 24t. The 4-regular macro graph contributes exactly 2t swaps, each a rank-one update over GF2. Therefore the joined graph has

    dim_GF2 ker A >= 27t − (24t+2t) = t = n/27.

For infinite families of *properly edge-colored 4regular bipartite macro expanders* (existence via standard regular bipartite expander graph and edge-coloring results), the fixed deleted-port internal U graphs are connected, so BABEL33's balanced frontier argument also gives Ω(n) incidence separator width. This large-width/high-nullity family is nevertheless trivially solvable by the local support rule. Such constructions **do not** establish NP hardness or complexity lower bounds on all SAT algorithms.

## 4. User's actual universal target remains OPEN

This is a scientific falsification of an overbroad completion claim plus a valid all-input *conditional-on-complete-local-tables* sound pruning theorem. It does NOT solve arbitrary connected legal SCL in polynomial time, nor remove BABEL39's open requirements of automatically finding a polynomially describable decomposition, constructing arbitrary component relations and solving any residual non-bijunctive CSPs.

In particular a nonempty arc-consistent network can be globally UNSAT (e.g. two-coloring an odd cycle), and large local state tables can still be exponential in N. Do not equate arc consistency or fixed-template compilers with universal P. The exact no-UNKNOWN/no-exponential-gap target for \`SolveLinearCubicXSAT\` remains an open mathematical problem.

## 5. Reproducibility and gates

Files:
- \`experiments/babel40/signed_flux_arc_adversary.py\`: verifies the frozen original U SHA, computes A and B partial local tables by **independent complete Boolean DPLL** and exact producer Fraction echelon; checks flux values/majority failure/additive pruning support; constructs joined SCL54 and verifies legality + SAT, uses INDEPENDENT full GF2 parity census (d3, eight assignments, count1), and compares generic arc results, then constructs edge-colored 4regular bipartite macro instances t8,12,20 with all original row witnesses rechecked.
- \`experiments/babel39/generic_scl_component_compiler.py\` has a new generic \`exact_reciprocal_port_arc_consistency\` stage before exact bijunctivity. Its SAT/UNSAT/UNKNOWN behavior and proof-contract remain intact.
- CI regression and scientific scope gate in \`.github/workflows/babel40-signed-flux-arc.yml\`.

\`\`\`
BABEL40_CONNECTED_SCL54_SIGNED_FLUX_COMPENSATION = EXACT_SAT_UNIQUE
BABEL40_BABEL39_ZERO_FLUX_SUPPORT_ALWAYS_BIJUNCTIVE = DISPROVED
BABEL40_GENERIC_ALL_N_RECIPROCAL_ARC_PRUNING = PROVED_SOUND
BABEL40_ARC_CONSISTENCY_GLOBALLY_COMPLETE_FOR_ALL_SCL = NOT_PROVED
BABEL40_SIGNED_BIPARTITE_MACRO_ALL_N_UNIQUE_SAT = PROVED
BABEL40_UNIVERSAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
\`\`\`
