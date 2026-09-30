# C024 — Original-Axiom Unit Safety for Smart Graph Tautologies

**Status:** proved for original GT axioms / derived-clause extension open.

## Setting

Let `GT_n` use one comparison variable for every unordered vertex pair. A partial
assignment is interpreted as an acyclic strict partial order `P`; two vertices
are in the same component when they are connected in the undirected
comparability graph of the transitive closure of `P`.

A unit comparison is **component-joining** when its endpoints lie in different
components immediately before the unit is applied.

The historical Formula-Caching target is reached after `n-2` novel branches,
leaving at most two components. The question is whether unit propagation can
join components earlier and thereby replace a required binary novel branch.

## Lemma 1 — transitivity units are component-internal

A smart GT transitivity axiom has the cyclic form

```text
(a < b) OR (b < c) OR (c < a).
```

Suppose simplification under the acyclic partial order makes `(c < a)` the only
unassigned literal. Then the other two literals are false:

```text
NOT(a < b), hence b < a;
NOT(b < c), hence c < b.
```

Thus the assigned relation already contains the path

```text
c < b < a.
```

Vertices `c` and `a` are therefore already in the same Hasse/comparability
component before the unit is propagated. The same argument applies after cyclic
renaming to either of the other literals.

Hence an original transitivity axiom cannot produce a component-joining unit.

## Lemma 2 — a non-minimality unit occurs only at the final component gap

The non-minimality axiom for vertex `v` is

```text
OR over u != v of (u < v).
```

Suppose it simplifies to the unit `(w < v)`. Every other literal `(u < v)` is
false, so the assignment contains

```text
v < u
```

for every `u` distinct from `v` and `w`.

Therefore `v` is already connected to `n-2` other vertices. These `n-1` vertices
belong to one connected component, while only `w` may remain outside it. The
partial order has at most two components immediately before the unit.

Starting from `n` singleton components, reaching at most two components requires
at least `n-2` component joins. Thus an original non-minimality axiom cannot
replace any of the first `n-2` required novel joins. It may only close the final
`2 -> 1` gap at or after the historical target level.

## Corollary — exact remaining source of danger

Before novelty level `n-2`, no original GT axiom can produce a component-joining
unit. Consequently any counterexample to C024 early-merge exclusion must use a
clause with derived ancestry:

```text
inherited local resolvent
or
residual of an inherited local resolvent.
```

This reduces the transfer theorem to a derived-clause robustness problem rather
than a general unit-propagation problem.

## Machine cross-check

The C024 source and timing audits independently verify through `GT_8` that:

- every observed pre-unit component merge happens exactly at novelty level
  `n-2`;
- every observed merge closes `2 -> 1` components;
- every post-local merge has an explicit one-pass Resolution source;
- no unit-induced component merge appears before the target.

The next audit traces every pre-unit merge back to a root GT axiom whenever such
an axiom exists, separating original-axiom events from genuinely derived-only
ancestry.

## Missing extension

Prove that a clause derived and inherited under Policy-0A's bounded one-pass
Resolution discipline also cannot produce a component-joining unit before level
`n-2`, or charge every such event strongly enough to preserve an exponential
frontier.

The original-axiom lemmas alone do not establish this derived-clause extension.

## Claim boundary

This file proves a structural property of original smart graph-tautology axioms.
It does not prove the complete `JANUS-FC_local` lower bound and does not resolve
P versus NP.
