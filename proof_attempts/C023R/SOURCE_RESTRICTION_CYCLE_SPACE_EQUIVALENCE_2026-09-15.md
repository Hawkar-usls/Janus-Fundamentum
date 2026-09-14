# C023R theorem note — exact source-restriction cycle-space equivalence

Authority: `HQ_SYMBOLIC_THEOREM_NOTE__NO_GLOBAL_PROMOTION`

## Setting

Use the frozen q=4 canonical encoding. Let `H` be any set of original edges. For each `e in H`, freeze the same two coordinate positions of its MAJ3 block in two partial assignments `alpha` and `alpha'`, and require those two coordinates to be equal within each assignment so the MAJ3 output of the block is forced.

Assume:

- `alpha` and `alpha'` assign the same coordinate set;
- they agree on every assigned coordinate outside the selected equal-pair values in blocks of `H`;
- all restrictions on blocks outside `H` are identical.

Let `z_e` and `z'_e` be the forced MAJ3 outputs on edge `e`, and set

`d = z xor z' in F_2^H`.

Let `B_H` be the mod-2 vertex-edge incidence matrix restricted to `H`.

## Lemma 1 — forced-edge outputs shift only local vertex charges

At a vertex `v`, every fully forced incident edge output contributes a fixed bit to the local equation

`XOR_{e incident v} MAJ3(block_e) = charge(v)`.

After restricting the selected blocks, the remaining local relation has effective charge

`charge_alpha(v) = charge(v) xor XOR_{e in H incident v} z_e`.

Therefore the effective charge-vector difference between `alpha` and `alpha'` is exactly

`B_H d`.

## Lemma 2 — source truth-table CNF is determined by the restricted local relation

For the historical complete truth-table encoding, restriction of the source CNF by a partial assignment equals the complete blocking-clause CNF of the restricted Boolean relation after canonical duplicate removal.

Thus, when the assigned variable set and all non-`H` restrictions are fixed, the source residual at vertex `v` is byte-identical between `alpha` and `alpha'` iff the effective restricted vertex relation is identical, which here is equivalent to equality of the effective charge bit.

## Theorem — exact source-key equivalence

Under the setting above, the complete restricted **source** CNFs are byte-identical iff

`B_H d = 0`.

Proof.

- If `B_H d=0`, every vertex has the same effective charge and the same remaining variables/restrictions under both histories. Lemma 2 gives identical canonical local CNFs at every vertex, hence identical global source CNFs.
- If `B_H d != 0`, at least one vertex has opposite effective charge. The two restricted local Boolean relations at that vertex are complements over the same remaining scope. Their complete truth-table blocking CNFs differ, so the global source CNFs differ.

QED.

## Corollary — cycle-space ambiguity is syntactic, not merely semantic

The kernel of an undirected incidence matrix is the cycle space. Hence every fixed source residual syndrome on `H` has exactly

`2^{beta(H)}`

forced-output preimages, where

`beta(H)=|E(H)|-|V(H)|+c(H)`

for the incident subgraph.

Therefore, once the same coordinate positions have been stifled, source restriction alone forgets the cycle-space component of the forced-output history **exactly at the byte-CNF level**.

This strengthens the earlier semantic preimage observation: the quotient already exists in the historical source syntax before considering cache equality.

## What can still break the collision

A historical Policy-0A cache key may contain inherited clauses derived by earlier local-Resolution passes. Those clauses are not part of the pure source restriction and may distinguish two cycle-equivalent histories even when the restricted source CNF is identical.

Thus the nearest remaining gate is now exact:

`C023R_INHERITED_RESOLUTION_CYCLE_SPACE_BREAKING`

Question:

> For histories whose pure source restrictions differ only by a cycle-space flip and are therefore byte-identical, do the inherited clauses preserve enough information to separate all but `2^{o(L)}` such histories, or can an `Omega(L)`-dimensional family of cycle flips survive to one full historical cache key?

## Firewalls

`SOURCE_RESTRICTION_COLLISION != HISTORICAL_CACHE_COLLISION`.

`CYCLE_SPACE_DIMENSION != REACHABLE_EXECUTION_FIBER`.

No reachability or asymptotic cache lower bound is claimed by this theorem.