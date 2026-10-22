# BABEL-30 — deterministic end-to-end polynomial solver for an explicitly ADMITTED two-edge-atom-tree subclass

**23 October 2026. Research-only.** Direct successor to BABEL-29 (#555); base \`f1f42093bcf2c25999d4c88a1cf6bf83184090ad\`. This document presents a correct **bounded-atom special-class** algorithm, not a universal polynomial-time solver. Graph bridge decomposition and tree belief propagation are established techniques, NOT historically novel discoveries.

## Exact input contract

Input: a connected legal square 3-uniform, 3-regular, linear positive Exact-One system F with n variables and n rows. In any SAT instance, 3|x|=n, so if n is not divisible by3, return UNSAT by a constant-time counting certificate.

For n divisible by3, define the deterministic algorithm below with fixed **atom-size cutoff** w (e.g. 27), independent of total n.

### Phase 1 — discover and CERTIFY a 2-incidence-edge splice tree

Construct the undirected bipartite incidence graph (row nodes, variable nodes; 3n edges). Search for pairs of distinct incidence edges \`(r,b)\` and \`(s,a)\` whose deletion disconnects the graph into exactly two connected sides, A and B, with r and a on A and s and b on B, and such that **restoring local incidences** \`(r,a)\` inside A and \`(s,b)\` inside B produces two legal square cubic linear systems with counts n_A,n_B divisible by3. The restoration is checked exactly by incidence lists and degree/pair uniqueness, not inferred from a graph drawing.

The algorithm can find candidates in deterministic polynomial time: for each incidence edge e, remove it and find graph bridges using ordinary DFS/Tarjan, then test whether some bridge f supplies the second cut edge and the required oriented restoration. Complete pair enumeration is at most O(n^2) candidates, with polynomial validation per candidate. This **does NOT** imply that an arbitrary input has an admissible candidate.

If one is found, recursively split BOTH restored components. Save the equality link \`x_a=x_b\` associated with this exact splice. If a component has at most w variables, admit it as a leaf atom; if it is larger and there is no admissible splice, return \`UNKNOWN_NOT_ADMITTED\`, **not** SAT/UNSAT. The outcome is a set of pairwise disjoint small legal atoms connected by equality links. The link graph is a tree by recursion: splitting a component into two introduces one edge joining their trees.

This discovery and checking procedure is deterministic polynomial in total input size, for every input, including rejected ones. A conservative worst-case bound O(n^5) suffices for pair search+validation over at most O(n) splits; it is not an optimized implementation claim.

### Phase 2 — exact local leaf model enumeration

For each atom A with at most fixed w variables, enumerate ALL its physical Exact-One assignments by exact Boolean DPLL (or brute force \`2^w\`), storing each satisfying local model. This costs \`O(num_atoms * 2^w poly(w))\`. The atom models are independently verifiable against all restored atom rows. **No global 2^n Cartesian product is materialized.**

### Phase 3 — integer two-state tree messages and exact reconstruction

Each equality link connects a boundary variable in one atom to a boundary variable in another. Root the atom tree. For child atom c with parent p and link boundary variable b_c, define \`msg_(c->p)(z)\` as the number of satisfying assignments of the entire child subtree with \`x_{b_c}=z\`. For atom c with local models \`M_c\` and children u, compute EXACTLY

    msg_(c->p)(z)
       = sum_(m in M_c, m[b_c]=z)
           product_(u child of c) msg_(u->c)(m[b_(c,u)]).

At root the count has the same sum without a parent bit restriction. These are **two integer states PER TREE EDGE** regardless of depth or how many atoms were joined. The only potentially exponential enumeration is inside each atom of size<=w. Each intermediate count is at most \`2^n\`, so addition/multiplication has polynomial bit complexity.

- If root count is zero, return UNSAT, with replayable exact completed message table and local exhaustive atom certificates.
- If positive, choose a local model with positive child-message product; recurse down choosing a matching nonzero child model per link. Concatenate the disjoint variable assignments and VERIFY every ORIGINAL input row is Exact-One before returning \`SAT + witness\`.

**All-n soundness/completeness within ADMITTED class** follows inductively from BABEL-28's exact single-splice solution bijection, verified restoration, and exact tree dynamic programming. Discovery + local enumeration + messaging + reconstruction + final verification are bounded by \`poly(n) * 2^w\`. If w is a fixed constant, this is a deterministic polynomial-time solver on the admitted subclass. For general F, this is a sound THREE-WAY algorithm: SAT, UNSAT, or UNKNOWN_NOT_ADMITTED.

The complexity proof **does not** imply all SCL admit small atoms or a bounded-width decomposition. It is also not sufficient to show every input that *might* have such a decomposition is always recognized by a greedy selection; the claim applies only if the deterministic routine successfully builds its certified decomposition. Do not rename the resulting subclass universal.

## Independent exact controls and negative admission

Script \`experiments/babel30/automatic_twoedge_atom_solver.py\`, Python standard library only:

1. Reconstruct canonical frozen SCL27 with one exact model (base U) and its GF2 consistency.
2. Independently generate BABEL27's legal connected unique-SAT chains of sizes n=54,81,135,243 (t=2,3,5,9) WITHOUT handing the construction history to the solver. It must discover cuts, restore atoms no larger than w=27, compute exact integer root SAT count1, and physically verify the returned model on all original rows.
3. Independently generate BABEL28's connected SCL54 with a zero↔true single splice: two formerly SAT atoms give joined UNSAT. The solver must discover the cut and return zero with completed two-state tables.
4. Use a connected legal SCL54 formed by TWO cross-splices from BABEL29 (with two actual solutions). It is NOT admitted at w=27 by this particular one-swap decomposition (unless an independently validated alternate cut is found); if rejected, it must return UNKNOWN_NOT_ADMITTED and MUST NOT falsely claim UNSAT.
5. The verifier independently checks every recovered original row, each restored atom's structure, equality-link tree, count and model. A concrete non-admission is a scope control, NOT evidence of intrinsic complexity.

\`\`\`
BABEL30_ADMITTED_TWOEDGE_ATOM_TREE_SOLVER = PROVED_ALL_N
BABEL30_AUTOMATIC_CUT_DISCOVERY_IN_P = PROVED
BABEL30_INTEGER_2STATE_MESSAGE_COMPOSITION = PROVED_ALL_N
BABEL30_GLOBAL_WITNESS_RECONSTRUCTION = PROVED_ON_ADMITTED
BABEL30_ARBITRARY_CONNECTED_SCL_ADMISSION = NOT_PROVED
BABEL30_GENERAL_SCL_POLYNOMIAL_DECIDER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`

Canonical scientific firewall applies: an admitted subclass proof must not be promoted to P=NP; exact semantics, coefficient bits and full history must all be counted.
