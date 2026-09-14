# C023R theorem note — descendant clause provenance causal cone

Authority: `HQ_SYMBOLIC_THEOREM_NOTE__NO_GLOBAL_PROMOTION`

## Provenance definition

Associate every original MAJ3-lifted vertex-factor clause with the singleton provenance set containing that source vertex. Restriction and unit propagation retain the provenance of every surviving clause. When a Resolution event derives clause `C` from parents `A,B`, assign

`Prov(C) = Prov(A) union Prov(B)`.

This provenance is proof bookkeeping only; it is not added to the historical cache key.

## Lemma 1 — literals cannot appear outside provenance endpoints

Resolution and restriction never introduce a new literal. Therefore if a derived clause contains lifted variable `x` belonging to edge `e={u,v}`, at least one source ancestor of that clause contained `x`. Only the two endpoint vertex factors `u,v` contain coordinates of edge block `e`. Hence

`Prov(C) intersect {u,v} != empty`.

## Lemma 2 — provenance connectedness

For every clause appearing in any historical Policy-0A key or one-pass Resolution output, `Prov(C)` induces a connected vertex set in the original graph.

Proof by induction over derivation events.

- A source clause has singleton provenance and is connected.
- Restriction/UP preserve provenance.
- Suppose `C` resolves parents `A,B` on lifted variable `x` of edge `{u,v}`. By Lemma 1, each parent provenance contains at least one endpoint of this edge. By induction each parent provenance is connected. If both contain the same endpoint their union is connected. Otherwise one contains `u`, the other `v`, and source edge `{u,v}` connects the two sets. Thus their union is connected.

QED.

## Lemma 3 — one search level can at most double provenance size

Let `M_d` be the maximum provenance cardinality among clauses in the canonical cache key at search depth `d`.

The frozen one-pass Resolution implementation builds all positive/negative parent lists from clauses present at pass entry. Newly added clauses are not re-indexed and cannot be parents in the same pass.

Therefore every new clause has two entry parents and provenance size at most `2 M_d`. Subsequent post-pass unit propagation and child restriction do not increase provenance.

Hence

`M_{d+1} <= 2 M_d`.

At the root, source clauses and the accepted root-local resolvents have provenance size 1, so

`M_d <= min(N, 2^d)`.

## Consequence

Inherited local Resolution has an exact causal structure:

- each clause depends on one connected source region;
- that region can expand by at most one binary provenance merge generation per search level;
- before depth `log2 N`, no single inherited clause can have provenance over all `N` source vertices.

This does NOT prove a subexponential cache fiber. Depth may be linear, and connected provenance can become global after logarithmically many levels.

## Nearest missing link

The next decisive proposition is not provenance size alone. It is the relation between connected provenance, expander boundary, residual clause width, and assigned history:

`C023R_EXPANDER_BOUNDARY_VS_RESIDUAL_FINGERPRINT`

Candidate statement to attack:

> A derived clause whose connected provenance contains `s` source vertices must expose either Omega(boundary(s)) live gadget information in its residual clause or charge the missing boundary information to the current assignment/context.

If true with an exact injective/accounting map, it can turn expansion into a history fingerprint. If false, a counterexample may yield a compact provenance clause that forgets enough boundary history to seed serial diamonds.

No heuristic score or finite fit is used here.