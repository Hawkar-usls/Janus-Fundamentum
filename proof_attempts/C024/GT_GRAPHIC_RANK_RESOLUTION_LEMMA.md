# C024 — Graphic-Rank Resolution Lemma

**Status:** proved combinatorial inference lemma / cumulative lower-bound charge open.

## Setting

Fix one partial-order component partition `P`. For every clause `C`, let
`G_P(C)` be its external-literal multigraph on the current Hasse components and
let `rho_P(C)` be its graphic-matroid rank.

Consider a non-tautological Resolution inference on pivot variable `x`:

```text
L = A OR x
R = B OR NOT x
----------------
Q = A OR B
```

Canonicalization may remove duplicate literals, but does not remove any distinct
nonpivot edge from both parent remainders.

## Lemma

```text
rho_P(Q) >= max(rho_P(L), rho_P(R)) - 1.
```

Equivalently, one Resolution inference lowers graphic rank relative to the
larger-rank parent by at most one.

## Proof

Delete the pivot literal from `L`. In a graphic matroid, deleting one edge lowers
rank by at most one. Hence

```text
rho_P(A) >= rho_P(L)-1.
```

Likewise,

```text
rho_P(B) >= rho_P(R)-1.
```

The resolvent graph contains every external edge occurring in `A` or `B`.
Graphic rank is monotone under adding edges, so

```text
rho_P(Q) >= rho_P(A)
rho_P(Q) >= rho_P(B).
```

Combining the inequalities gives

```text
rho_P(Q) >= max(rho_P(L)-1, rho_P(R)-1)
         = max(rho_P(L), rho_P(R)) - 1.
```

Duplicate literals and parallel edges do not invalidate the argument because
removing duplicate or parallel copies does not decrease graphic rank. Literals
internal to a Hasse component are loops and also contribute no rank.

## Equality and zero-loss cases

Rank loss of one is possible only when the pivot is rank-essential in every
larger-rank parent witness used by the bound and the remaining nonpivot edges of
the other parent do not restore the lost connectivity.

If the pivot is a loop, a parallel redundant edge or lies on a cycle in a
larger-rank parent, deleting it does not lower that parent's rank and the
resolvent has no rank loss relative to that parent.

## Proof charge interpretation

At fixed novelty level, the potential

```text
Psi(P,C) = novelty(P) + rho_P(C)
```

can decrease across one Resolution inference by at most one. Every such decrease
is attached to an explicit, independently replayable event with two parent
clauses and one pivot.

Thus Policy-0A cannot create an arbitrarily lower-rank clause in one local step.
Any cumulative rank decrease along a Resolution provenance DAG is bounded by the
number of rank-losing inference events on that provenance.

## What this does not yet prove

A polynomial number of unit rank losses is not automatically harmless. The
transfer theorem must still show that rank-losing inferences cannot collectively
collapse exponentially many historical target restrictions without a matching
proof-size charge.

The executable C024 census measures:

- the actual maximum rank loss per inference;
- how many events lose rank relative to both parents;
- whether certified dangerous origins have frontier score `n-2`;
- whether any direct cross-component unit is derived before the target.

## Claim boundary

This file proves a one-inference graphic-rank inequality. It does not prove the
cumulative Formula-Caching lower bound for `JANUS-FC_local` and does not resolve
P versus NP.
