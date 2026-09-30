# C024 — Component-Tree Contraction Lemma

**Status:** proved combinatorial lemma / dangerous-clause necessity open.

## Definitions

Fix an acyclic partial order `P` on the graph-tautology vertices and let

```text
K_1, ..., K_m
```

be the connected components of its Hasse diagram, equivalently of the undirected
comparability graph of its transitive closure.

For a clause `C`, map every comparison literal on vertices `u,v` to the
undirected edge between the components containing `u` and `v`.

Call `C` a **component-tree clause at P** when:

1. every literal has endpoints in two different components;
2. the resulting edge multiset is an acyclic connected graph on all `m`
   components.

Equivalently, the component graph is a spanning tree and

```text
width(C) = m - 1.
```

## Lemma

Let `C` be a component-tree clause at `P`. Suppose a branch assignment strictly
narrows `C` without satisfying it. Then:

1. the branch variable is the variable of exactly one literal `l` of `C`;
2. the branch falsifies `l`;
3. the endpoints of `l` lie in different Hasse components, so the branch is
   novel;
4. the branch joins those two components;
5. the residual clause `C \ {l}` is a component-tree clause on the contracted
   component partition.

## Proof

Because the branch strictly narrows rather than satisfies `C`, its variable
occurs in `C` and the chosen truth value falsifies that literal. A clause contains
no duplicate variable under canonical CNF normalization, so exactly one literal
is removed.

By the component-tree definition, the removed literal is an edge of the spanning
tree and its endpoints belong to different current components. Assigning their
comparison therefore joins two distinct components. This is exactly a novel
branch.

Contract the removed tree edge. Edge contraction in a tree cannot create a
cycle. It reduces both the number of vertices and the number of edges by one and
preserves connectedness. Hence the remaining literal edges form a spanning tree
on the contracted component graph. Therefore `C \ {l}` is again a
component-tree clause.

## Iterated corollary

Starting from a component-tree clause of width `w`, any sequence that narrows it
to a unit solely by branch assignments contains exactly `w-1` novel branches.
At every intermediate point:

```text
current component count = current clause width + 1.
```

If the origin novelty is `r`, the potential

```text
Phi = r + width - 1
```

is preserved through every tree contraction.

## Relation to C024 evidence

The finite C024 provenance audit verifies through `GT_8` that all twelve derived
pre-unit component-merge origins satisfy the component-tree predicate and every
one of their 31 narrowing transitions is precisely the contraction described
above.

That evidence is not needed for the lemma itself; it supports the separate
hypothesis that every frontier-dangerous Policy-0A resolvent belongs to this
class.

## Remaining theorem gate

The unresolved statement is **necessity**, not contraction:

> Every Policy-0A derived clause capable of producing a component-joining unit
> before the historical graph-tautology frontier must either be a
> component-tree clause or incur an equivalent lower-bound-preserving proof
> charge.

A clause that is not a component tree may contain internal component edges,
cycles, disconnected support or omitted components. The global C024 census shows
that such ordinary clauses can shrink along nonnovel branches, so the necessity
statement cannot be replaced by an all-clause invariant.

## Claim boundary

This file proves only the elementary component-tree contraction property. It
does not prove that all dangerous learned clauses are component trees, does not
transfer the graph-tautology lower bound to `JANUS-FC_local`, and does not resolve
P versus NP.
