# JANUS TRUMP R44BM — sibling split-activator merge conserves maximum deficiency

Let a CNF `G` be split on a variable `x` occurring in both polarities:

`G = H ∪ {x ∨ A_i}_i ∪ {¬x ∨ B_j}_j`,

where no clause of `H` contains `x`.

The two cofactors are

`G[x=0] = H ∪ {A_i}_i`,

`G[x=1] = H ∪ {B_j}_j`.

R44AS already refutes the ordinary Davis-Putnam sibling merge as a descent-preserving maximum-deficiency operator, even on a parent with exact branchwise `delta*` descent. R44BM therefore tests a different compact merge that avoids the pairwise resolvent product.

Introduce fresh activation variables `a,b` and define

`M = H ∪ {¬a ∨ A_i}_i ∪ {¬b ∨ B_j}_j ∪ {(a ∨ b)}`.

## Exact sibling semantics

If the `x=0` sibling is satisfiable, set `a=1,b=0`. Then the `A_i` residues are enforced and the `b` branch is disabled.

If the `x=1` sibling is satisfiable, set `a=0,b=1`.

Conversely, every model of `M` satisfies `a∨b`. If `a=1`, then `H` and every `A_i` hold, so the remaining original-variable assignment extends to a model of `G` with `x=0`. If `a=0`, then `b=1`, so `H` and every `B_j` hold and the assignment extends with `x=1`.

Thus

`exists_{a,b} M ≡ exists_x G`,

and in particular

`SAT(M) iff SAT(G[x=0]) or SAT(G[x=1])`.

## Incidence matching theorem

For every CNF `F`, maximum deficiency satisfies

`delta*(F)=|C(F)|-nu(I(F))`,

where `I(F)` is the bipartite clause-variable incidence graph and `nu` is maximum matching size.

Passing from `I(G)` to `I(M)` performs one graph operation:

1. replace the pivot variable vertex `x` by two variable vertices `a,b`;
2. redirect the incidences of positive-pivot clauses to `a` and negative-pivot clauses to `b`;
3. add one new clause vertex `c_ab` adjacent to `a,b`.

We prove

`nu(I(M)) = nu(I(G))+1`.

### Lower bound

Take a maximum matching `Q` of `I(G)`.

- If `x` is unmatched, retain every edge of `Q` and add `c_ab--a`.
- If `x` is matched to a positive-pivot clause, replace that matched edge by the corresponding edge to `a`, then add `c_ab--b`.
- If `x` is matched to a negative-pivot clause, replace it by the corresponding edge to `b`, then add `c_ab--a`.

Each case produces a matching of size `nu(I(G))+1`, hence

`nu(I(M)) >= nu(I(G))+1`.

### Upper bound

By König's theorem take a minimum vertex cover `K` of `I(G)` with

`|K|=nu(I(G))`.

If `x∈K`, replace `x` in the cover by both `a` and `b`. All redistributed pivot edges and the new edge-pair through `c_ab` are covered. The cover size increases by exactly one.

If `x∉K`, every old clause neighbor of `x` already belongs to `K`. Keep those vertices and add the new clause vertex `c_ab`; again the cover size increases by exactly one and all new edges are covered.

Therefore `I(M)` has a vertex cover of size `nu(I(G))+1`. König's theorem gives

`nu(I(M)) <= nu(I(G))+1`.

Combining both inequalities,

`boxed(nu(I(M)) = nu(I(G))+1)`.

## Rank consequence

The split merge adds exactly one clause while replacing one variable by two, and the matching number also rises exactly by one. Hence

`delta*(M)`
`= (|C(G)|+1) - (nu(I(G))+1)`
`= delta*(G)`.

Therefore

`boxed(delta*(M)=delta*(G))`.

For an R44BD critical parent of rank `k>0`, the two cofactors may individually have rank at most `k-1`, yet this compact exact sibling merge returns rank exactly `k`. It satisfies exact OR semantics but fails the required single-state rank descent.

This is distinct from R44AS: raw DP can rebound above the parent rank; R44BM's split-activation representation avoids that blow-up but exactly conserves the parent rank.

So:

`RAW_DP_SIBLING_MERGE -> CAN_REBOUND`,

`TWO_ACTIVATOR_SIBLING_SPLIT -> EXACTLY_CONSERVES_MAXDEF`,

and neither discharges R44BD M2.

Scope remains strict. This does not refute all sibling-specific semantic compression, other ranks, or non-CNF representations.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.
