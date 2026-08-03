# C024 — Graphic-Rank Branch Monotonicity

**Status:** proved combinatorial branch lemma / local-Resolution rank generation open.

## Clause graph and rank

Fix an acyclic partial order `P` on the graph-tautology vertices. Let

```text
K_1, ..., K_m
```

be the connected components of its Hasse diagram, equivalently of the undirected
comparability graph of its transitive closure.

For a clause `C`, form a multigraph `G_P(C)` on these `m` components:

- a comparison literal whose endpoints lie in different components becomes an
  edge between those components;
- a literal whose endpoints already lie in one component becomes a loop;
- parallel edges are allowed.

Loops do not contribute to graphic-matroid rank. Define

```text
rho_P(C) = m - cc(G_P(C)),
```

where `cc` counts connected components after retaining all `m` vertices,
including isolated vertices.

Thus `rho_P(C)` is the size of a maximal forest in the external-literal graph.
For a component-spanning tree clause, `rho_P(C)=m-1=width(C)`.

## Branch operation

Let a branch assign comparison variable `x_(u,v)` and let `P'` be the resulting
acyclic partial order. Let `C'` be the residual clause when the branch does not
satisfy `C`.

The branch is **novel** precisely when `u` and `v` belong to different
components of `P`. Write `delta=1` for a novel branch and `delta=0` otherwise.

## Lemma

For every unsatisfied residual clause,

```text
rho_P'(C') >= rho_P(C) - delta.
```

Consequently the potential

```text
Psi(P,C) = novelty(P) + rho_P(C)
```

is nondecreasing along every branch edge:

```text
Psi(P',C') >= Psi(P,C).
```

The shifted potential `novelty + rho - 1` has the same monotonicity and is
normalized to `n-2` on a final component-joining unit at novelty `n-2`.

## Proof: nonnovel branch

If the branch is nonnovel, `u` and `v` already lie in one Hasse component.
Adding their comparison does not merge components, so the vertex set of
`G_P(C)` is unchanged.

If the branch variable does not occur in `C`, then `C'=C` and the external-edge
graph is unchanged.

If it occurs and is falsified, its literal is a loop because both endpoints are
already in one component. Deleting a loop does not change graphic rank.

Hence

```text
rho_P'(C') = rho_P(C).
```

## Proof: novel branch

If the branch is novel, it joins exactly two Hasse components. Passing from `P`
to `P'` contracts those two component vertices in every clause graph.

Graph contraction of one pair of vertices can reduce graphic rank by at most
one. If the branch literal occurs in `C` and is falsified, the corresponding
external edge is removed while its endpoints are simultaneously contracted.
This is exactly graphic-matroid contraction of a nonloop edge and reduces rank
by one. If the branch variable does not occur in `C`, or if parallel paths make
the contraction redundant, rank decreases by zero or one but never more.

Therefore

```text
rho_P'(C') >= rho_P(C)-1.
```

Since novelty increases by one, `Psi` cannot decrease.

## Why rank repairs the false width potential

C024 found 612 pre-frontier nonnovel clause-width decreases, including 269 on
immediate local resolvents. Width was therefore the wrong universal measure.

The branch literal in every such nonnovel event is internal to an existing Hasse
component. It is a loop in `G_P(C)`. Removing it decreases width but not graphic
rank. Likewise, deleting a redundant cycle edge can decrease width without
changing rank.

Graphic rank keeps only the independent cross-component connectivity carried by
the clause and discards precisely the loops and cycle redundancy that generated
the counterexamples.

## Relation to the component-tree lemma

For a spanning tree clause every edge is rank-essential. A falsifying branch
contracts one tree edge, so rank decreases by exactly one and novelty increases
by exactly one. The component-tree contraction lemma is therefore the equality
case of this more general rank lemma.

## Remaining theorem gate

Branch monotonicity alone does not prove the graph-tautology lower bound for
`JANUS-FC_local`. Policy-0A creates new clauses by local Resolution. The missing
question is whether a Resolution event can create a clause with dangerously low

```text
novelty + rho_P(C) - 1
```

without paying a corresponding proof charge.

The next executable audit checks every pre-frontier clause across every actual
branch edge, and a second audit measures rank loss at every local Resolution
inference.

## Claim boundary

This file proves only a graph-theoretic branch monotonicity statement. It does
not classify local Resolution generation, does not transfer the Formula-Caching
lower bound, and does not resolve P versus NP.
