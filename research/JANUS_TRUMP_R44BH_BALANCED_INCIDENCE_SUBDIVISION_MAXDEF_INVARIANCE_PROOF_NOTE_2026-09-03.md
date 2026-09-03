# JANUS TRUMP R44BH — balanced incidence subdivisions preserve maximum deficiency

For a CNF `F`, let `I(F)` be its bipartite clause-variable incidence graph. Maximum deficiency satisfies

`delta*(F)=|C(F)|-nu(I(F))`,

where `nu` is maximum matching size.

Consider replacing any incidence edge `c--v` by an alternating odd path

`c--y1--d1--y2--d2--...--yt--dt--v`,

where `y_i` are new variable-side vertices and `d_i` are new clause-side vertices. Thus every subdivided edge receives the same number `t` of new clause and variable vertices. Perform this independently on any set of original edges.

We prove that maximum deficiency is unchanged.

## Matching lower bound

Let `M` be a maximum matching of the original incidence graph.

For a subdivided edge not used by `M`, retain all original matching edges and match each new clause node `d_i` to a distinct adjacent new variable inside its path. This adds exactly `t` matches without using either original endpoint.

For a subdivided edge used by `M`, replace its old matched edge by a perfect matching of the new path. The path has `2t+2` vertices and hence contributes `t+1` matched edges instead of one, again a net gain of `t`.

Path interiors are disjoint, so all replacements coexist. Hence

`nu(I') >= nu(I)+sum_e t_e`.

## Vertex-cover upper bound

By Konig's theorem, take a minimum vertex cover `K` of the original bipartite graph with `|K|=nu(I)`. Every original edge has at least one endpoint in `K`.

On the odd path replacing an edge, retain the original endpoint(s) already in `K` and add exactly `t` internal alternating vertices to cover every new path edge. This can be done independently for all subdivided edges. Therefore the new graph has a vertex cover of size

`nu(I)+sum_e t_e`.

Konig's theorem implies

`nu(I') <= nu(I)+sum_e t_e`.

Together with the lower bound,

`boxed(nu(I')=nu(I)+sum_e t_e)`.

The subdivision also adds exactly `sum_e t_e` clause-side vertices. Consequently

`|C'|-nu(I') = |C|+sum t_e - (nu(I)+sum t_e) = |C|-nu(I)`,

and therefore

`boxed(delta*' = delta*)`.

## TRUMP consequence

R44BG is the `t=1` occurrence-splitting instance of this graph theorem. More generally, no construction that merely stretches clause-variable incidences through balanced alternating clone/link chains can reduce the R44BD maximum-deficiency rank. Any successful successor must add genuinely different nonlocal incidence topology or use a non-incidence representation whose exact rank accounting is separately proved.

`INCIDENCE_EDGE_STRETCHING != MAXDEF_DESCENT`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
