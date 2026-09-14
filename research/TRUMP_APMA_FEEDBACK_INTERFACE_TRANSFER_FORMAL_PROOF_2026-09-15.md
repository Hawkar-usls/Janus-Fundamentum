# TRUMP APMA canonical feedback-interface exact transfer — formal proof ledger

Authority: `SCOPED_FORMAL_PROOF_LEDGER__NOT_GENERAL_SAT__NOT_P_VS_NP`

This note proves only the preregistered class in
`TRUMP_APMA_FEEDBACK_INTERFACE_TRANSFER_PREREGISTRATION_2026-09-15.json`.
Finite GitHub runs are counterexample/implementation attacks and are not used as theorem premises.

## Frozen setting

Let the exact typed mosaic partition a width-1..3 CNF `F` into modules
`M_1,...,M_m`, each in one of the exact tractable languages 2CNF, Horn, or
Dual-Horn. The module interaction graph `G=(V,E)` has one vertex per module.
Because interface hyperedges are forbidden, every shared variable occurs in
exactly two modules and labels exactly one simple interaction edge.

Let `L = 1+n+#clauses+#literal_occurrences`.

The candidate discovers a deterministic BFS spanning tree `T`: root is the
lexicographically least module id and neighbors are visited lexicographically.
Let `C=E\\T` be the feedback edges and

`B = union_{e in C} S_e`,

where `S_e` is the exact shared-variable separator on edge `e`.
Admission requires cycle rank at least two, `|B|<=floor(log2 L)`, and after
removing `B` from every module boundary, each remaining tree boundary has width
at most `floor(log2 L)`.

## F1 — canonical discovery is deterministic and polynomial

Module discovery, variable-to-module incidence construction, the simple
interaction graph, sorted-neighbor BFS, set difference `E\\T`, separator union,
and all width checks use only explicit input/module data. They require a
polynomial number of operations in the encoded input size. No search over
alternative spanning trees is performed. Therefore the discovered `(T,C,B)` is
canonical for this algorithm and polynomially discoverable.

This proves only a theorem for the canonical `B`. It does not claim that an
instance rejected by this tree lacks some other low-width feedback set.

## F2 — deleting feedback edges yields exactly a tree

For an admitted connected graph, deterministic BFS first discovers every vertex
except the root through exactly one parent edge. Hence `T` contains `|V|-1`
edges, spans all vertices, and is connected, so `T` is a tree. By definition
`C=E\\T`; deleting every edge in `C` leaves exactly `T`.

## F3 — exhaustive conditioning on B preserves SAT exactly

For every Boolean formula and variable set `B`,

`SAT(F) <=> exists sigma in {0,1}^B : SAT(F | B=sigma)`.

Forward direction: restrict any satisfying assignment of `F` to `B`; the
remaining assignment satisfies the corresponding conditioned formula.
Reverse direction: combine a satisfying assignment of a conditioned formula
with its fixed `sigma`; this satisfies `F`.

Every variable on every deleted feedback edge is in `B`. Because interface
hyperedges are forbidden, a boundary variable belongs to exactly the two
modules incident to its unique interaction edge. Thus fixing `B` fixes both
copies of every deleted-edge interface consistently; no unrepresented equality
or compatibility constraint remains after feedback-edge deletion.

## F4 — conditioned tree DP is exact

Fix one `sigma_B`. After deleting feedback edges, the remaining module
interaction is the tree `T`. Every variable in `B` occurring in a module is
fixed to the same global value from `sigma_B`. Every remaining inter-module
variable belongs to one tree edge.

For each rooted subtree and each assignment to the parent separator, define the
semantic DP predicate:

`R_u(tau)=1` iff the conjunction of all module formulas in the subtree rooted at
`u` has an extension satisfying the subtree while agreeing with `tau` on the
parent separator and with `sigma_B` on `B`.

The implementation enumerates the full remaining boundary assignment of module
`u`, calls the exact native solver for the conditioned local 2CNF/Horn/Dual-Horn
module, and retains a parent row exactly when every child table contains the
induced child-separator row.

Induction on subtree height proves equality with `R_u`:
- Leaf: a row exists exactly when the exact native module solver finds a local
  extension for the fixed boundary values.
- Internal node: by the induction hypothesis each child row exists exactly when
  that child subtree has an extension. Tree separators are the only remaining
  cross-module variables, so simultaneous child compatibility plus local module
  satisfiability is necessary and sufficient for a subtree extension.

At the root, the empty parent key exists iff the whole conditioned formula is
SAT. Therefore each fixed-sigma DP decision is exact.

Conditioning preserves each native language: restrictions of 2CNF remain 2CNF,
restrictions of Horn remain Horn, and restrictions of Dual-Horn remain
Dual-Horn. The frozen native solvers are exact polynomial algorithms for those
languages.

## F5 — SAT reconstruction is globally valid

Every retained table row stores a local witness and the complete boundary
assignment used for that row. Reconstruction recursively chooses the recorded
child key induced by the parent boundary assignment. `_merge_witness` rejects
any conflicting overlap. Variables in `B` are inserted from one global
`sigma_B`, so feedback-edge endpoints agree by construction.

Thus a reconstructed witness satisfies every module and all shared-variable
compatibility constraints. The candidate additionally replays the reconstructed
assignment against the original root CNF before `COMMIT_SAT`. Therefore an
accepted SAT result cannot be committed without a root-valid witness.

## F6 — rejection of all sigma implies UNSAT

By F4, `REJECTED_SIGMA` is issued exactly when `F | B=sigma` is UNSAT. The
algorithm issues `CERTIFIED_UNSAT_MODULE_FEEDBACK` only after enumerating every
`sigma in {0,1}^B` and receiving `REJECTED_SIGMA` for each. By F3, if no
conditioned formula is satisfiable then `F` is UNSAT.

As in the unicyclic predecessor, this semantic UNSAT conclusion is independently
polynomially replayable by deterministic recomputation. This successor does not
yet claim a new compact serialized rejection-proof language for all sigma.

## F7 — total lifecycle is polynomial

Admission gives `|B|<=floor(log2 L)`, therefore

`2^|B| <= L`.

For each fixed sigma and each module, the remaining boundary width is at most
`floor(log2 L)`, so the number of enumerated remaining-boundary rows is at most
`L`.

With `M` modules, at most `M*L` native module-solver calls occur per sigma, and
at most

`M*L^2`

native calls occur over all sigma. Since `M<=L` and each native 2SAT/Horn/
Dual-Horn solve is polynomial in `L`, solve time is polynomial. Table keys,
merges, construction, canonical discovery, reconstruction, and root replay are
also polynomial in their explicitly bounded tables/input.

Hence

`T_construct + T_discover + T_solve + T_reconstruct + T_verify <= poly(L)`

for the frozen admitted class.

## Scoped theorem

For every formula in the preregistered scope, deterministic canonical BFS
feedback discovery followed by exhaustive exact conditioning on its canonical
feedback interface `B` and exact typed-module tree DP decides SAT exactly in
polynomial total lifecycle time whenever the frozen feedback and conditioned
boundary width admission bounds hold.

This theorem does **not** prove polynomial time for formulas with canonical
`|B|>log L`, conditioned tree-boundary overflow, interface hyperedges, arbitrary
mixed representations, or general SAT.

`GENERAL_SAT_IN_P = NOT_PROVED`  
`P_VS_NP = OPEN`
