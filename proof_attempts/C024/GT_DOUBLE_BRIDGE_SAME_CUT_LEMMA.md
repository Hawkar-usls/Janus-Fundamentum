# C024 — Double-Bridge Same-Cut Lemma

**Status:** proved graph lemma / GT-specific exclusion under audit.

## Setting

Fix one partial-order component partition with `m` vertices. Let `L` and `R` be
two clauses whose external undirected component graphs are connected. Suppose
`L` contains pivot edge `e` and `R` contains the complementary orientation of
the same component edge. Let `Q` be their non-tautological resolvent.

Ignore edge orientation temporarily and retain all nonpivot external edges.

## Lemma

The resolvent external graph is disconnected if and only if:

1. the pivot edge is a bridge in the external graph of `L`;
2. the pivot edge is a bridge in the external graph of `R`;
3. deleting the pivot from both parents induces the same bipartition of the `m`
   components.

In this case the resolvent graph has exactly two connected components and

```text
rho(Q) = m-2.
```

## Proof

If the pivot is not a bridge in `L`, then `L` without the pivot remains
connected. Its edges are contained in the resolvent, so the resolvent is
connected. The same argument applies to `R`. Therefore disconnectedness requires
the pivot to be a bridge in both parents.

Deleting a bridge from a connected graph gives exactly two connected parts.
Write the parent cuts as

```text
A_L | B_L
A_R | B_R.
```

If the cuts differ, then at least one edge path in one parent remainder crosses
the other parent's cut. Since each parent remainder is connected inside each of
its two sides, the union of the two remainders connects all component vertices.
Hence the resolvent is connected.

If the cuts are identical, neither remainder contains an edge crossing the
common cut. Their union therefore remains disconnected across that cut. Each
side is connected in each parent remainder, so the union has exactly two
connected components.

A graph on `m` vertices with exactly two connected components has graphic rank
`m-2`.

## Unsafe directed refinement

A common-cut resolvent is `UNSAFE_ACYCLIC_LOW_RANK` precisely when its directed
external graph contains no directed cycle. If a directed cycle survives inside
one side of the cut, the clause belongs to the directed-cycle safety class even
though its undirected rank is deficient.

Thus a generic unsafe Resolution step requires the conjunction:

```text
double bridge
AND same cut
AND no directed cycle in the nonpivot union.
```

## Relation to the minimal counterexample

For

```text
L = {0->1, 2->1}
R = {1->0, 2->1},
```

the complementary pivot `0<->1` is a bridge in both parents. Deleting it gives
the same cut

```text
{0} | {1,2}.
```

The common remainder `{2->1}` is acyclic, so the resolvent is unsafe.

## Remaining GT-specific theorem

To prove closure for the exact pre-frontier `GT_n` residual family, it suffices
to prove one of the following equivalent safety statements for every legal
frozen parent pair:

1. no complementary pivot is a same-cut double bridge; or
2. whenever a same-cut double bridge occurs, the nonpivot union contains a
   directed cycle.

The accompanying executable audit distinguishes these two possibilities through
`GT_8`.

## Claim boundary

This file proves only an elementary graph characterization. It does not prove
that Policy-0A GT residuals exclude the configuration for all `n`, and it does
not resolve P versus NP.
