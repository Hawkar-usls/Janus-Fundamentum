# JANUS TRUMP R44CD — Global Transport / 3-Color Reduction Seal

## Frozen parent

Parent gate: `R44CC_INTERNAL_TERNARY_TRANSPORT_INEQUALITY_REALIZABILITY` at `a990d54140b7ddd45583a2e265d873c1fc4d69f7`.

## Reduction

For a finite simple graph `G=(V,E)` with `n=|V|`, `m=|E|`, construct the R44CC sibling-CNF pair `(A_G,B_G)`.

Each graph vertex receives one 3-variable local block using the frozen R44CC local CNF. Each graph edge contributes one target cross-clause and six source cross-clauses.

Therefore:

- variables: `3n`
- target clauses: `4n+m`
- source clauses: `4n+6m`

The construction is direct local emission and hence polynomial in the graph representation size.

## Formula-only recovery

The recovery procedure receives only `(A_G,B_G)`.

The common local clauses recover the 3-variable blocks. Exact signed-map filtering leaves exactly three local candidates per block. For every recovered target interaction, exact transport-clause checking against the source derives the relation

`NEQ3 = {(i,j) : i,j in {0,1,2}, i != j}`.

No coloring, graph generator, candidate IDs, or truth labels are supplied to recovery.

## Completeness

Let `c:V->{0,1,2}` be a proper 3-coloring. Select on each recovered block the local transport candidate whose decoded cyclic phase is `c(v)`. For every edge `(u,v)`, proper coloring gives `c(u) != c(v)`, and the recovered compatibility relation is exactly `NEQ3`. Hence every target cross-clause transports into the source. Thus a global transport exists.

## Soundness

Let a global transport exist. Each recovered block must use one of the exactly three local candidates. Decode its cyclic phase as `c(v)`. For every edge `(u,v)`, global transport validity requires the selected candidate pair to belong to the recovered edge relation, which is exactly `NEQ3`. Therefore `c(u) != c(v)` on every edge, so `c` is a proper 3-coloring.

Hence:

`G is 3-colorable  <=>  GLOBAL_TRANSPORT_EXISTS(A_G,B_G)`.

## Consequence and claim ceiling

This seals a polynomial many-one reduction from graph 3-coloring to global transport existence on this specific R44CC family.

Therefore, any polynomial-time algorithm solving global transport existence on this family would yield a polynomial-time algorithm for graph 3-coloring by construction followed by that solver.

This does **not** prove `P != NP`, does not rule out an additional polynomial invariant, and does not prove or disprove polynomiality of the full TRUMP algorithm.

Firewalls remain:

- `TRUMP_finished=false`
- `SAT_IN_P=NOT_PROVED`
- `P_VS_NP=OPEN`
