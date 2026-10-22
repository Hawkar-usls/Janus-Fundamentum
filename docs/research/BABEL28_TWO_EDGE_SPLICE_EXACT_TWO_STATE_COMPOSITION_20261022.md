# BABEL-28 — exact two-state compositional rule across an incidence 2-edge splice

**22 October 2026.** Research-only successor to BABEL-27 #553. The result is a provably sound **polynomial composition operator**, conditional on local boundary tables. It is not a polynomial construction of such tables for arbitrary SCL. Known graph-separator dynamic programming is not asserted as historically new mathematics. Main remains untouched; P vs NP OPEN.

## The exact all-n bijection: SAT across a cross-incidence 2-edge cut

Take TWO DISJOINT square, 3-uniform 3-regular linear Exact-One instances L and R of sizes n_L,n_R, each divisible by 3. Choose a row r in L and a variable a in that row; choose a row s in R and variable b in that row. Exchange just the two row-variable incidences, replacing (r,a),(s,b) by (r,b),(s,a). Let J be the resulting joint instance. Denote by S_L(z) the set of SAT models of L with x_a=z, and S_R(z) the SAT models of R with x_b=z, for z∈{0,1}.

**Theorem, for all such L,R:**

    SAT(J) <=> (SAT(L,a=0) and SAT(R,b=0))
          or (SAT(L,a=1) and SAT(R,b=1)).

More precisely, physical solution sets are in an exact bijection:

    SAT(J) == [S_L(0) × S_R(0)] disjoint_union [S_L(1) × S_R(1)].

Therefore the exact number of models satisfies

    #SAT(J) = N_L(0)*N_R(0) + N_L(1)*N_R(1).

**Proof (both directions).** In any J model, all original rows of L except r and of R except s are unchanged and satisfied. By the all-n BABEL-27 row-deletion redundancy lemma for each old square 3regular component of size multiple3, the restrictions are true SAT models of L,R, including old r and old s. The swapped joint row r now has count \`1-x_a+x_b\`; demanding count1 forces \`x_a=x_b\`. The same holds for joint row s. Conversely, any two old SAT models with equal boundary bits continue to satisfy all unmodified rows and both new rows after the incidence exchange. This proves the bijection with no information loss.

Note this is stronger than the BABEL-27 uniqueness-preserving splice theorem: **neither original component needs to have a unique model**. For arbitrary local SAT spectra the exact two-state boundary tables suffice.

## Complexity and precise scoped solvability

If each component supplies exactly verified Boolean feasibility tables \`B_i(0),B_i(1)\` plus a reconstructible witness for each TRUE entry, then deciding the joined instance and reconstructing its witness requires **constant-size Boolean table intersection** and O(n_L+n_R) witness concatenation/verification. For exact #SAT, supply correctly verified counts \`N_i(z)\`; their integer product-and-sum takes polynomial bit complexity because the binary lengths of numbers of assignments are O(n_L+n_R). The **discovery/construction of local tables** may be NP-hard and is NOT bounded by this theorem.

The inverse-splice certificate can be audited in polynomial time: on a supplied pair of cross-incidence edges, cut both, check exactly two disjoint legal row-variable regions, restore one local row-variable incidence in each, verify square/cubic/linear structure and the n_i mod3=0 hypothesis. One can also enumerate candidate pairs among O(n) incidence edges in O(n^2) candidate choices and check each in O(poly(n)) time, but an arbitrary connected SCL need not admit any qualifying cut. Repeating such cuts into a tree is a separator-DP algorithm ONLY if the accumulated boundary-message state remains polynomial; a cut search alone does not prove such an all-input bound.

## Explicit connected examples with opposite outcomes

Use U, the frozen BABEL-24 connected SCL27 with exactly ONE model and true indices \`(2,3,7,9,13,17,19,23,24)\`.

1. Choose row0 on each copy, swap zero literal \`a=0\` with zero literal \`b=27\`. Both local boundary count spectra are (N0=1,N1=0), so the connected SCL54 join has **exactly 1 SAT model**.
2. Choose row0 on each copy, swap zero literal \`a=0\` with true literal \`b=29\` (local index2 is true). Their spectra are (1,0) and (0,1), so their connected legal SCL54 join is **UNSAT** even though EACH original component is SAT. The UNSAT conclusion is the exact all-n bijection specialized to frozen certified local spectra, not a failed search.

The independent checker \`experiments/babel28/twoedge_splice_composition.py\` reconstructs both joins, verifies legality/connectedness, independently computes their GF2 ranks/nullities, exhaustively enumerates all parity states for these two 54-variable controls, and independently recovers both original components by removing the two supplied cross incidences and restoring the local incidences. It recomputes the exact 2-state spectra and verifies the bijection and full-model replay.

## Relation to the universal goal

This is an honest **exact polynomial composition theorem** for one real connected separator architecture, not the universal polynomial composition theorem that would imply P=NP. Missing: every connected input must admit some discoverable set of small interfaces or another bounded-state exact carrier; certificate construction and bit complexity must remain polynomial over the entire decomposition history. The fixed-degree Gram obstruction of BABEL-27 remains valid on its connected unique SAT family but does not prevent this splice-aware exact decomposition.

\`\`\`
BABEL28_TWO_EDGE_SPLICE_EXACT_SOLUTION_BIJECTION = PROVED
BABEL28_TWO_STATE_BOUNDARY_COMPOSITION_POLYNOMIAL_CONDITIONAL = PROVED
BABEL28_CONNECTED_SCL54_UNIQUE_SAT_AND_UNSAT_CONTROLS = EXACT_LOCAL
BABEL28_ALL_CONNECTED_SCL_SEPARATORS_SMALL = NOT_PROVED
BABEL28_GLOBAL_POLYNOMIAL_SOLVER = NOT_PROVED
P_VS_NP = OPEN
\`\`\`
