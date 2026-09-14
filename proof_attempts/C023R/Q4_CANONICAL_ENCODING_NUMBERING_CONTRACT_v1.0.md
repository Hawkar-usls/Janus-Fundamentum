# C023R q=4 canonical encoding / numbering contract v1.0

Authority: `PRE_ASYMPTOTIC_RUN_ENCODING_FREEZE__NO_SCIENTIFIC_PROMOTION`

## Why this contract is required

The q=4 Morgenstern binding froze the abstract graph family and hard-width premise, but historical Policy-0A is not invariant under arbitrary variable renaming: local Resolution pivots are traversed by numeric variable ID and branching breaks frequency ties by minimum numeric ID.

Therefore an exact Policy-0A asymptotic claim requires one deterministic encoding-level enumeration of graph vertices, edges and MAJ3 coordinates.

No asymptotic Policy-0A run on the q=4 family has been observed before this freeze.

## Frozen field element encoding

Use the already frozen field model

`F4 = F2[a]/(a^2+a+1)`

with codes

`0 -> 0, 1 -> 1, a -> 2, a+1 -> 3`.

For

`K_t = F4[x]/(g_t)`

with `deg(g_t)=d_t`, represent each field element by the unique coefficient vector

`(c_0,...,c_{d_t-1})`

of the polynomial representative `sum_i c_i x^i`.

Define its integer code

`code_K(c) = sum_i code_F4(c_i) * 4^i`.

This is a bijection from `K_t` to integers `[0,4^{d_t}-1]` and is independent of implementation hash-table ordering.

## Frozen group element encoding

Because the field has characteristic 2, the frozen group is represented concretely by determinant-one 2x2 matrices over `K_t`; the scalar `-I` equals `I`, so the PSL projective sign ambiguity is absent.

Represent a vertex matrix

`h = [[h00,h01],[h10,h11]]`

by the 4-tuple

`(code_K(h00), code_K(h01), code_K(h10), code_K(h11))`.

Enumerate all determinant-one matrices in strict lexicographic order of this tuple. Assign vertex IDs

`0,1,...,N_t-1`

in that order.

No runtime discovery order, BFS order or generator-walk order is admissible as a replacement.

## Frozen Cayley edge construction

Use the five already frozen generator matrices `Gamma_0,...,Gamma_4` in the exact pair order

`(0,a), (1,0), (1,a+1), (a,a), (a,a+1)`.

For every enumerated vertex matrix `h` and every generator `Gamma_i`, form the neighbor by **left multiplication**

`Gamma_i * h`.

Convert both endpoints to their frozen vertex IDs. Store the undirected edge as

`(min(u,v), max(u,v))`.

Deduplicate identical undirected edges, then sort the complete edge set lexicographically by endpoint pair.

The previous simple-edge binding proves no loop and five distinct neighbors per vertex; this contract only fixes enumeration, not graph semantics.

## Frozen charge placement

Use the historical generator convention exactly:

- charge `1` on frozen vertex ID `0`;
- charge `0` on every other vertex.

The charge vector has odd Hamming weight. No search for a more convenient charge location is permitted.

## Frozen MAJ3 variable numbering

Let the sorted undirected edges be

`e_0 < e_1 < ... < e_{M_t-1}`.

Assign edge `e_j` the MAJ3 coordinate block

`(3j+1, 3j+2, 3j+3)`.

Within every vertex factor, incident edges are taken in global sorted-edge order and each edge contributes its coordinate triple in the displayed coordinate order.

Build each vertex relation with the existing exact truth-table CNF routine and canonicalize clauses with the historical `canonical_cnf` ordering.

## Frozen policy dependence

The resulting variable IDs are the IDs used without renaming by:

- numeric pivot order in historical one-pass Resolution;
- minimum-ID tie-break in `branch_variable`;
- canonical residual keys;
- exact formula caching.

No structural renaming, graph automorphism canonicalization or post-result permutation is permitted for this C023R route.

## Complexity

The enumeration is a mathematical encoding definition, not a claim that naive enumeration code must be used. A future generator implementation must construct this exact ordered object in time polynomial in the explicit output size or else the generation cost must be charged separately.

## Firewalls

`CANONICAL_NUMBERING_FREEZE != CACHE_LOWER_BOUND`.

`GRAPH_ISOMORPHISM != POLICY0A_EXECUTION_EQUIVALENCE`.

No q=4 asymptotic execution result may be used to revise this numbering contract.

## Status

`FROZEN_PRE_ASYMPTOTIC_RUN_ENCODING_CONTRACT`

Next allowed step: all C023R symbolic or executable claims about the q=4 family must refer to this exact numbering.