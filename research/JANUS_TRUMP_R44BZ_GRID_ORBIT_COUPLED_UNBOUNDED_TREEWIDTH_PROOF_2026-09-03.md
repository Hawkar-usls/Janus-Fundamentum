# R44BZ — Grid-coupled orbit family escapes fixed bounded-treewidth terminals

Let `r>=2`, and place `k=r^2` renamed R44AS blocks on the vertices of an `r x r` grid. All blocks share one pivot `x`; their five nonpivot variables are disjoint. For every grid edge `uv`, add the full 12-clause orbit under the R44BP signed permutation `pi` of the seed `(x1_u ∨ ¬x3_v ∨ x4_u)`.

There are `E=2r(r-1)` grid edges and therefore `12E=24r(r-1)` connector clauses, with no new variables.

## Rank

The raw shared-pivot parent on `r^2` blocks is maxdef-critical with rank `3r^2-1`. Each connector clause uses only existing variables. By the critical-extension lemma, adding each such clause preserves maxdef-criticality and raises maxdef by exactly one. Hence

`delta*(G_r)=3r^2-1+24r(r-1)=27r^2-24r-1`.

After fixing the common pivot, the raw child is a variable-disjoint union of `r^2` base siblings and has maxdef/full deficiency `r^2`. Adding `c=24r(r-1)` clauses raises maxdef by at most `c`, while the full child has deficiency `r^2+c`. Thus

`delta*(A_r)=delta*(B_r)=25r^2-24r`.

The branch drop is therefore

`(27r^2-24r-1)-(25r^2-24r)=2r^2-1`.

## SAT, connectedness, and congruence rigidity

Use the common local R44AS sibling model `(x1,x3,x4,x5,x6)=(0,0,0,0,1)` in every block. As in R44BX, the first two literals of every connector orbit clause are consecutive phases of the alternating truth orbit of `x1`, so every connector is satisfied. Both siblings are SAT.

Each local block is connected, and each grid edge receives a cross-block connector, so both child primal graphs are connected.

All connectors have width three and add no binary implication edges. The base siblings have no nontrivial binary SCC equivalences, so exhaustive polynomial binary-congruence quotienting leaves singleton classes.

## Transport support

Applying the R44BP signed permutation independently in every block transports local `B` clauses to local `A` clauses and permutes every connector orbit into itself. Therefore a forward transport exists with support at most `5r^2`.

If a target block is pointwise fixed, its purely local target clauses can only be witnessed by same-block local source clauses: connectors span two blocks and clauses from other blocks use disjoint local variables. This would induce the forbidden identity base transport. Hence every block contributes a moved variable and every signed transport has support at least `r^2`. The same untouched-block proof lower-bounds fixed-deviation many-to-one substitutions by `r^2`.

## Unbounded treewidth

In either child primal graph, each block induces a connected subgraph on five variables. Contract every block subgraph to one vertex. Every edge of the block grid has at least one connector containing variables from both endpoint blocks, hence becomes an edge after contraction. Thus the child primal graph contains the `r x r` grid as a minor.

Treewidth is minor-monotone, and square-grid treewidth grows linearly with `r`; consequently the child treewidth is unbounded. In particular, unlike R44BX's path coupling, this family is not contained in any fixed bounded-treewidth SAT class.

## R44BC terminal check

Encoded CNF size is `Theta(r^2)`, while child maxdef is `25r^2-24r=Theta(r^2)`. Therefore for sufficiently large `r`, `delta* > floor(log2 S)`, so R44BC's low-maxdef polynomial terminal does not apply.

## Claim ceiling

This removes two specific terminal escapes: fixed bounded treewidth and the R44BC logarithmic-maxdef terminal. It is not an NP-hardness theorem. The family still has an explicitly repeated global generator `pi`, which may itself be polynomially recognizable.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
