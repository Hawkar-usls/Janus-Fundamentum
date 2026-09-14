# APMA Trinity bounded-interface unicyclic transfer — formal scoped proof

Status: `HQ_FORMAL_PROOF_REVIEW_CANDIDATE`

Scientific scope only:

`GENERAL_3CNF_AFTER_EXACT_TYPED_MOSAIC_RECOMPOSITION`

with a connected simple module-interaction graph of cycle rank exactly one, no interface hyperedge (every source variable occurs in at most two distinct modules), and for every module the union of incident shared variables has cardinality at most

`w = floor(log2(max(2,L)))`,

where

`L = 1 + n + clause_count + literal_occurrence_count`.

This theorem does **not** claim universal SAT, universal invariant discovery, or P=NP.

## Definitions

The exact typed mosaic partitions the original source clauses into modules. Full recomposition is checked against the unchanged source before this successor is admitted. Two distinct modules are adjacent exactly when they share at least one source variable. The edge label `S_uv` is the complete set of source variables shared by modules `u` and `v`.

The no-hyperedge condition implies that every shared variable belongs to exactly the two endpoint modules of one interaction edge. Consequently, for two distinct module pairs, their edge-label variable sets are disjoint unless the pairs are identical.

Let the connected module interaction graph be `G=(V,E)`. The successor admits only `|E|=|V|`. For a connected finite simple graph this is equivalent to cyclomatic number

`|E|-|V|+1 = 1`.

Hence `G` is unicyclic.

## P1 — canonical cut edge removal yields a tree

In a connected unicyclic graph there is exactly one simple cycle. An edge is a non-bridge iff it lies on that cycle. The implementation scans interaction edges in deterministic lexicographic order and selects the first edge whose removal leaves the graph connected. Therefore the selected edge `e*=(a,b)` lies on the unique cycle.

Removing `e*` decreases the edge count from `|V|` to `|V|-1` while preserving connectivity. A connected graph on `|V|` vertices with `|V|-1` edges is a tree. Thus the cut graph `T=G-e*` is a tree.

This proves `P1_CUT_EDGE_REMOVAL_YIELDS_TREE_FOR_CONNECTED_UNICYCLIC_GRAPH`.

## P2 — conditioning the cut separator is semantically exhaustive

Let `S=S_ab` be the complete shared-variable set on the cut edge. Every total assignment `A` satisfying the original CNF has a unique restriction `sigma=A|S`. Therefore

`SAT(F) => exists sigma in {0,1}^S such that SAT(F | S=sigma)`.

Conversely, any satisfying assignment of `F | S=sigma`, extended by `sigma` on `S`, satisfies every original clause because conditioning changes no clause semantics: it only fixes source variables to their selected Boolean values. Therefore

`exists sigma SAT(F | S=sigma) => SAT(F)`.

Hence

`SAT(F) iff exists sigma in {0,1}^S SAT(F | S=sigma)`.

The implementation enumerates all `2^|S|` assignments exactly. No scoring, sampling, or heuristic selection occurs.

Because interface hyperedges are forbidden, every variable in `S` appears in exactly the two cut-endpoint modules and in no third module. Fixing the same `sigma` in both endpoints therefore removes precisely the semantic dependency represented by the removed interaction edge. All remaining inter-module dependencies are exactly the edges of tree `T`.

This proves `P2_SIGMA_CONDITIONING_IS_SEMANTICALLY_EXHAUSTIVE_AND_NONOVERLAPPING_ENOUGH_FOR_SAT_EXISTENCE`.

## P3 — exactness of the conditioned tree dynamic program

Fix one `sigma`. Root `T` arbitrarily using the deterministic forest-parent routine. For a module `u`, let `p(u)` be its parent, let `P_u` be the complete separator shared with `p(u)` (empty for the root), and let the child separators be `C_{u,v}`.

The DP table for `u` contains a parent key `tau on P_u` iff there exists:

1. a complete assignment to all other boundary variables of `u`, together with the frozen cut assignment `sigma` when `u` is a cut endpoint;
2. a satisfying assignment of the clauses of module `u` consistent with that boundary assignment; and
3. for every child `v`, a child-table row whose parent key equals the induced assignment on `C_{u,v}`.

We prove this statement by induction from leaves to root.

### Leaf

A leaf has no children. The algorithm exhaustively enumerates every assignment to its unfrozen boundary variables. `_native_solve` solves the conditioned local module exactly in its frozen tractable language (`2CNF`, `HORN`, or `DUAL_HORN`). Therefore a parent key is stored iff the leaf clauses have a satisfying extension consistent with that parent key and the fixed cut assignment, if applicable.

### Inductive step

Assume the statement holds for all children of `u`. The algorithm exhaustively enumerates the remaining boundary assignment of `u`, solves the local module exactly, and accepts that row only when every child table contains the exact separator key induced by the same boundary assignment. By the induction hypothesis, each accepted child key is equivalent to existence of a satisfying extension of the entire child subtree under that separator assignment.

Because every inter-module shared variable belongs to exactly the two modules incident to its interaction edge, child subtrees have no hidden shared variable with each other or with the rest of the already processed tree beyond their explicit separator with `u`. Thus the local satisfying witness and the child-subtree witnesses can be joined consistently iff all separator keys match.

Therefore the table invariant holds for `u`.

At the root, the empty key exists iff the whole conditioned tree formula `F | S=sigma` has a satisfying assignment.

Storing only one witness row for a parent key is sufficient for SAT existence: once one compatible extension exists, additional extensions with the same parent key are irrelevant to the existential decision; for UNSAT, absence of the key occurs only after every boundary assignment inducing that key has been tested and rejected.

This proves `P3_INNER_TREE_DP_REMAINS_EXACT_UNDER_FIXED_CUT_SEPARATOR_ASSIGNMENT`.

## P4 — exact witness reconstruction and root replay

For an accepted `sigma`, reconstruction recursively selects the stored row for the root and the unique stored child row addressed by each exact separator key. Adjacent module witnesses agree on every shared variable because the child key was derived from the parent boundary row.

The two cut-endpoint modules are no longer adjacent in tree `T`, but every variable of the removed separator `S` was explicitly fixed to the same `sigma` in both endpoint local solves. Therefore their reconstructed witnesses also agree on `S`.

No other cross-module overlap exists outside interaction-edge labels under the no-hyperedge condition. Repeated witness merging can therefore introduce no inconsistent source-variable value. The implementation nevertheless checks merge consistency and finally replays the reconstructed total witness against the unchanged original source CNF.

Thus every `COMMIT_SAT` has a root-valid witness for the original formula.

This proves `P4_RECONSTRUCTED_WITNESS_REPLAYS_ON_UNMODIFIED_ROOT_SOURCE`.

## P5 — rejection of every cut assignment certifies UNSAT

Suppose every `sigma in {0,1}^S` is rejected by the exact conditioned tree DP. By P3, for every `sigma`, `F | S=sigma` is UNSAT. By P2,

`SAT(F) iff exists sigma SAT(F | S=sigma)`.

The right-hand side is false, therefore `F` is UNSAT.

Equivalently, assume toward contradiction that `F` had a satisfying assignment `A`. Its restriction `A|S` would be one enumerated `sigma`; by P2 and P3 that conditioned tree run would contain an accepting root row, contradicting rejection of every `sigma`.

This proves `P5_ALL_SIGMA_REJECTION_CERTIFIES_ROOT_UNSAT`.

## P6 — polynomial total lifecycle under the frozen scope

Let `M=|V|` be the number of modules. Since every module contains at least one source clause, `M <= clause_count <= L`.

For the cut separator, `|S| <= w <= floor(log2 L)`, hence

`2^|S| <= L`.

So the outer exact enumeration performs at most `L` conditioned tree runs.

For a fixed `sigma`, each module enumerates assignments to a subset of its original full boundary. The frozen scope gives full boundary size at most `w`, hence each module has at most

`2^w <= L`

boundary rows. Across all modules there are at most `M L` local-row attempts per `sigma`, and across all cut assignments at most

`M L^2`

local-row attempts.

Each local-row attempt invokes an exact solver for one of the frozen tractable module languages. Standard 2-SAT SCC, Horn forward chaining, and dual-Horn-by-complement solving are polynomial in the conditioned module encoding size, which is at most `O(L)`. Denote this bound by `P_native(L)`.

Therefore the solve phase is bounded by

`O(M L^2 P_native(L))`,

which is polynomial because `M <= L` and `P_native` is polynomial.

The remaining lifecycle is polynomial:

- typed clause extraction and exact recomposition: polynomial scans/sorts/hashing over the source representation;
- module connected-component discovery: polynomial in clauses and variable incidences;
- interaction construction and cycle-rank checks: polynomial in modules and shared-variable incidences;
- canonical non-bridge cut selection: at most polynomially many graph-connectivity checks;
- witness reconstruction: linear in the number of stored selected module rows and witness sizes;
- final root replay: linear in source literal occurrences.

Thus

`T_construct + T_discover + T_solve + T_reconstruct + T_verify <= poly(L)`

throughout the frozen scoped class.

This proves `P6_TOTAL_DISCOVERY_SOLVE_RECONSTRUCT_VERIFY_COST_IS_POLYNOMIAL_IN_L_UNDER_FROZEN_BOUNDARY_BUDGET`.

## Implementation correspondence audit

The successor candidate implements exactly the proof construction:

- `unicyclic_certificate`: connectedness, `|E|=|V|`, deterministic cycle-edge cut, logarithmic full-boundary guard;
- `_canonical_cycle_edge`: deterministic non-bridge search;
- `_solve_conditioned_tree`: cut-edge removal, fixed `sigma` at both endpoints, exact bottom-up tree DP;
- `compile_unicyclic`: exhaustive `sigma` enumeration, SAT root replay, UNSAT only after all sigma rejections;
- successor `akinator_propose/captain_verify/janus_sovereign_decide`: deterministic admission, tamper rejection, root-hash preservation, fail-closed behavior outside scope.

Frozen Trinity v1.0 bytes are not modified.

## Counterexample attack status

Finite diagnostics are not used as the proof. They are only hostile falsifiers of the implementation/proof correspondence.

The preregistered 256-orientation cycle product reproduced 128 historical OPEN cases and the successor closed all 128 with zero exact mismatches. Multi-cycle and width-overflow negative controls remained OPEN.

A later deterministic hostile attack exhaustively tested 8,128 one- and two-clause augmentations of the frozen cycle base. 1,477 fell inside the admitted unicyclic scope and there were zero exact mismatches. The attack additionally exercised:

- genuine `COMMIT_UNSAT` by rejection of all cut assignments;
- unicyclic graphs with tree modules attached to the cycle;
- a cut separator containing more than one variable.

These finite facts support implementation correspondence only; they are not substituted for P1–P6.

## Scoped theorem

Under the frozen scope above, the successor decides satisfiability exactly and has polynomial construction/discovery/solve/reconstruction/verification cost.

Authorized scoped statement after HQ review:

`PASS_SCOPED_BOUNDED_INTERFACE_UNICYCLIC_TRANSFER`

Explicit non-claims:

- arbitrary connected multi-cycle interaction graphs: OPEN;
- arbitrary/wide exact interfaces: OPEN;
- universal invariant discovery: NOT CLAIMED;
- general SAT in P: NOT PROVED;
- `P_VS_NP`: OPEN.
