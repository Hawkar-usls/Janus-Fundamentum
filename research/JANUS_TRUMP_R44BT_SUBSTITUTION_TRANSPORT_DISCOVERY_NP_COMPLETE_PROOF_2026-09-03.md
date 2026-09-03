# R44BT — Generic many-to-one substitution transport discovery is NP-complete

## Discovery problem

Input: target CNF `A`, source CNF `B`.

Question: does there exist a map `phi` from variables of `A` to signed literals over variables of `B`, repetitions allowed, such that for every target clause `C`, the image `phi(C)` is either tautological or contains some source clause `D` as a subset?

A supplied map and clause witnesses are checkable in polynomial time, so the problem is in NP.

## Reduction from Graph 3-Coloring

Given a graph `G=(V,E)`, for each original vertex `v` add two private vertices `a_v,b_v` and the private triangle edges

`{v,a_v}, {a_v,b_v}, {b_v,v}`.

Retain all original edges of `G`. Call the resulting graph `G_triangle`.

Create the monotone 2CNF target `A_G` with one clause `(x_u OR x_v)` for every edge of `G_triangle`.

Create the fixed monotone 2CNF source

`B_K3 = {(y1 OR y2),(y1 OR y3),(y2 OR y3)}`.

## Allowed signed adjacency

For a target edge clause, a signed image is accepted exactly if it either contains a positive K3 edge or is tautological because its endpoints are opposite signs of the same source variable.

Hence on the six signed literals `+y1,+y2,+y3,-y1,-y2,-y3`, the allowed adjacency graph is:

- the positive triangle on `+y1,+y2,+y3`;
- one leaf `-yi` attached only to `+yi` for each `i`.

The only triangle in this six-vertex graph is the positive K3.

## Forward implication

If `G` has a proper 3-coloring, map each original vertex to the corresponding positive `yi`. For each private triangle, assign its two private vertices the other two positive colors. Every target edge then maps to a source K3 edge, so the substitution certificate exists.

## Reverse implication

Suppose a substitution certificate exists. Every private triangle of `G_triangle` must map to a triangle of the allowed signed adjacency graph. The only triangle available is the positive K3. Therefore each original vertex maps to one of the three positive source literals.

For every original edge `{u,v}`, the two positive images must be distinct, otherwise the image is a singleton and contains no 2-literal source clause. Thus the induced positive labels give a proper 3-coloring of `G`.

Therefore substitution-transport discovery is NP-hard. Together with membership in NP, it is NP-complete.

## 3CNF sibling lift

Introduce fresh pivot `z` and define

`P_G = {z OR C : C in A_G} union {NOT z OR D : D in B_K3}`.

All clauses have width three, and simplification gives

`P_G[z=0]=A_G`,

`P_G[z=1]=B_K3`.

So the NP-completeness already occurs for genuine sibling formulas of one 3CNF parent.

## Scope ceiling

The construction does not force `P_G` to be maximum-deficiency-critical. Thus it blocks generic unrestricted discovery, not a future algorithm exploiting additional maxdef-critical structure.

`TRUMP_finished=false`  
`SAT_IN_P=NOT_PROVED`  
`P_VS_NP=OPEN`
