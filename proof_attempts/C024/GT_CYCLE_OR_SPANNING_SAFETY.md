# C024 — Cycle-or-Spanning Clause Safety

**Status:** branch-safety lemmas proved / Resolution closure false in general.

## Component quotient

Fix an acyclic partial order `P` and quotient graph-tautology vertices by the
connected components of its Hasse diagram. For a clause `C`, every comparison
literal becomes:

- an external directed edge between two components; or
- an internal edge whose endpoints already belong to one component.

Call `C` branch-safe at `P` if it belongs to one of the following classes.

### Directed-cycle class

The external literal graph contains a directed cycle.

### Component-spanning class

The external undirected graph has graphic rank `m-1`, where `m` is the current
number of Hasse components. Equivalently, it connects all current components.

### Internal-only class

The clause has no external edge.

The remaining class is an acyclic external graph of rank below `m-1`; C024 calls
it an **unsafe acyclic low-rank clause**.

## Lemma 1 — directed-cycle clauses cannot create an external contradiction

Suppose the clause contains the directed cycle

```text
K_1 -> K_2 -> ... -> K_t -> K_1.
```

Falsifying all these literals would assert all reverse comparisons

```text
K_2 -> K_1, ..., K_1 -> K_t,
```

which form the reverse directed cycle and are inconsistent with an acyclic
partial order.

More locally, if branch restrictions falsify all cycle literals except
`K_t -> K_1`, the reverse assignments to the other edges already give a path

```text
K_1 -> K_2 -> ... -> K_t.
```

Hence the remaining literal's endpoints are already in one Hasse component. If
it becomes unit, it is internal rather than component-joining.

Contraction of components preserves a directed closed walk; after deleting
repetitions, it either leaves a directed cycle or makes all surviving cycle
edges internal. Therefore branches cannot turn this class into an early external
unit without first paying the component joins represented by the contraction.

## Lemma 2 — component-spanning clauses pay graphic rank

A component-spanning clause has graphic rank `m-1`. By the graphic-rank branch
lemma, a nonnovel branch does not lower rank and a novel branch lowers rank by at
most one while increasing novelty by one.

To reach a one-edge external unit, rank must fall from `m-1` to one. Branch
restriction alone therefore requires at least `m-2` novel component joins. For a
spanning tree this is exact edge contraction; cycles and parallel redundancy can
only delay, not accelerate, the required rank loss.

## Lemma 3 — internal-only clauses do not join components

Every literal has both endpoints in one current component. A unit or conflict
arising solely from such literals may constrain the order inside a component,
but it does not directly merge two Hasse components. Its treatment belongs to
the original graph-tautology partial-order argument rather than to the new
cross-component shortcut analysis.

## Corrected safety dichotomy

The earlier candidate “directed cycle or one sink reachable from every
component” was too narrow. Resolving two original non-minimality stars can create
an outward-oriented spanning tree with no common sink. Such a clause is still
safe by graphic rank.

The corrected branch-safe disjunction is

```text
directed cycle
OR component-spanning external graph
OR internal-only.
```

## Generic Resolution closure is false

Even the corrected class is not closed under arbitrary Resolution. On three
components:

```text
L = {0->1, 2->1}       component-spanning
R = {1->0, 2->1}       component-spanning
resolve on 0<->1
Q = {2->1}             acyclic rank-one graph with component 0 isolated
```

Both parents are safe and the resolvent is unsafe. The executable C024
counterexample verifies minimality at three components.

## Why Policy-0A may still preserve the historical frontier

Policy-0A uses frozen one-pass parent lists. A fresh resolvent cannot participate
in another inference until execution crosses a state boundary. Every such
boundary exposes branch novelty, unit propagation and exact residual identity as
explicit charges.

Thus the remaining theorem is temporal and GT-specific, not a static closure
claim:

> An unsafe low-rank clause cannot be generated and exploited before the first
> `n-2` novel frontier without accumulating enough novel transitions or explicit
> rank-losing Resolution events.

## Claim boundary

This file proves branch safety for the three structural classes and records a
minimal generic Resolution counterexample. It does not prove the temporal
Policy-0A theorem, an asymptotic lower bound, or P versus NP.
