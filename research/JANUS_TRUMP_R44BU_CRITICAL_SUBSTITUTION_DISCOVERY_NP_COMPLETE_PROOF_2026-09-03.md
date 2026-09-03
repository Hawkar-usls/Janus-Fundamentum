# R44BU — substitution discovery remains NP-complete on maxdef-critical siblings

## The problem

Given a width-3 CNF parent `P` with distinguished pivot `z`, promised maximum-deficiency-critical, let

`A=P[z=0]`,

`B=P[z=1]`

after simplification.

Ask whether there exists a many-to-one signed literal substitution `phi` from variables of target `A` to signed literals over variables of source `B` such that every target clause image is either tautological or contains some source clause as a subset.

A supplied map is polynomially verifiable. Hence the problem is in NP.

## Reduction from Graph 3-Coloring

Let `G=(V,E)` be an arbitrary graph.

First add one new universal vertex `u` adjacent to every original vertex. Call the new graph `G+`.

Then

`G is 3-colorable iff G+ is 4-colorable`.

The forward direction gives `u` a fresh fourth color. Conversely, in every proper 4-coloring of `G+`, every original vertex is adjacent to `u`, so the original graph uses only the other three colors.

Let

`N=|V(G+)|`, `M=|E(G+)|`.

For every vertex `v` of `G+`, add three private vertices `a_v,b_v,c_v` and all six edges of the complete graph on

`{v,a_v,b_v,c_v}`.

Retain every edge of `G+`. Call the resulting graph `H_G`.

Define target CNF `A_G` as the monotone graph-CNF of `H_G`: for every edge `{p,q}` use clause

`(x_p OR x_q)`.

Define fixed source CNF `B_K4` on `y1,y2,y3,y4` as all six monotone edge clauses of `K4`.

Finally introduce fresh pivot `z` and define

`P_G = {z OR C : C in A_G} union {NOT z OR D : D in B_K4}`.

Every parent clause has width exactly three and

`P_G[z=0]=A_G`,

`P_G[z=1]=B_K4`.

## Substitution theorem

For a monotone target edge clause, the image under a signed literal substitution has at most two literals. It is accepted exactly when either:

1. the image is one of the positive `K4` source edges; or
2. the image is tautological, i.e. the two endpoints are mapped to opposite signs of the same source variable.

Thus the allowed adjacency graph on the eight signed source literals is:

- the positive `K4` on `+y1,+y2,+y3,+y4`;
- one negative leaf `-yi` attached only to `+yi` for each `i`.

The only 4-clique in this graph is the positive `K4`.

Each private `K4` in `H_G` must therefore map bijectively to the four positive source literals. In particular each original vertex of `G+` receives one positive color.

Every original edge of `G+` then forces its endpoints to have distinct positive colors.

Therefore

`A_G -> B_K4 substitution exists`

iff

`G+ is 4-colorable`

iff

`G is 3-colorable`.

This proves NP-hardness once the promised parent criticality is established.

## Maximum-deficiency criticality

For any monotone graph-CNF and any nonempty clause subset corresponding to graph edge set `S`, deficiency is exactly graph excess

`ex(S)=|E(S)|-|V(S)|`,

where `V(S)` contains only vertices incident to selected edges.

### Target excess

The full graph `H_G` has

`4N` vertices and `M+6N` edges,

so

`ex(H_G)=M+2N`.

We prove that the full edge set is the unique maximizer.

Take any selected edge subset `S` of `H_G`.

Let:

- `E0` be the selected original `G+` edges;
- `O` be the original `G+` vertices incident to at least one selected edge;
- `T_v` be the selected edges from the private `K4` attached at `v`;
- `P_v` be the private vertices of that gadget incident to `T_v`.

The private vertex sets are disjoint, hence

`ex(S)=|E0|-|O| + sum_v (|T_v|-|P_v|)`.

If `v` is not in `O`, the selected gadget edges can use only private vertices, so

`|T_v|-|P_v| <= 0`.

If `v` is in `O`, let `p=|P_v|<=3`. At most all edges on `{v} union P_v` can be selected, giving

`|T_v|-|P_v| <= C(p+1,2)-p <= 3`.

Equality `3` is possible only for `p=3` with all six private-`K4` edges selected.

Therefore

`ex(S) <= |E0|-|O|+3|O| = |E0|+2|O| <= M+2N`.

Equality throughout forces:

- `|E0|=M`;
- `|O|=N`;
- every private `K4` is complete.

Thus equality occurs only for the full edge set of `H_G`. Every proper target clause subset has excess at most

`M+2N-1`.

Hence

`delta*(A_G)=M+2N`,

with the full target clause set as its unique maximizing subset.

### Source excess

For `K4`, the full edge set has excess

`6-4=2`.

Every proper nonempty edge subset has excess at most `1`, and the empty set has excess `0`. Thus the full source clause set is also the unique maximum-excess subset.

Hence

`delta*(B_K4)=2`.

### Parent rank

Target and source variables are disjoint, and every nonempty parent clause subset contains the common pivot variable `z`.

Write a nonempty parent clause subset as `Q=Q_A union Q_B`. Then

`delta(Q)=ex(Q_A)+ex(Q_B)-1`.

For the full parent,

`delta(P_G)=(M+2N)+2-1=M+2N+1`.

If `Q` is proper, at least one side is not full.

- If `Q_A` is proper, `ex(Q_A)<=M+2N-1`, so `delta(Q)<=M+2N`.
- If `Q_A` is full but `Q_B` is proper, `ex(Q_B)<=1`, so again `delta(Q)<=M+2N`.

Therefore the full parent is the unique maximum-deficiency clause subset:

`delta*(P_G)=M+2N+1`.

So `P_G` is maximum-deficiency-critical.

Its two siblings are strict descendants:

`delta*(P_G[z=0])=M+2N`,

`delta*(P_G[z=1])=2`.

## Conclusion

The many-to-one signed literal substitution discovery problem is NP-hard even when the two sibling formulas arise from a promised maximum-deficiency-critical width-3 parent. Together with membership in NP:

`CRITICAL_SIBLING_SIGNED_LITERAL_SUBSTITUTION_TRANSPORT_DISCOVERY is NP-complete.`

Thus the last criticality-only escape left by R44BT is closed:

`MAXDEF_CRITICALITY_ALONE != POLYTIME_SUBSTITUTION_DISCOVERY` unless `P=NP`.

This does **not** prove `P!=NP`, does not invalidate supplied substitution certificates, and does not block a different safe-deletion relation or a stronger structural restriction than maximum-deficiency criticality.

`TRUMP_finished=false`  
`SAT_IN_P=NOT_PROVED`  
`P_VS_NP=OPEN`
