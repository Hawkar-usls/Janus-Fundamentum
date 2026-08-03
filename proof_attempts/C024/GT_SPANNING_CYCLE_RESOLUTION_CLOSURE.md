# C024 — Spanning/Cycle Resolution Closure

## Status

**PROVED — pure quotient-graph lemma.**

This lemma closes the mixed parent class that appears in every fresh non-tail
bridge birth observed in the exact `GT_4,...,GT_8` Policy-0A traces.

It does **not** assert that arbitrary Resolution preserves the cycle-or-spanning
dichotomy.  The remaining abstract obstruction is confined to
`COMPONENT_SPANNING + COMPONENT_SPANNING` and is classified separately in
`GT_RESOLUTION_UNSAFE_ROUTE_CLASSIFICATION.md`.

## Setting

Fix a residual state and contract the current Hasse components.  A clause is
viewed as a directed multigraph on the quotient components:

- internal literals become loops and are irrelevant to quotient connectivity;
- external literals become directed quotient edges;
- parallel literals are allowed;
- opposite literals are opposite orientations of the same comparison variable.

Let `A` and `B` be non-tautological clauses with complementary pivot literals
`p in A` and `-p in B`.  Let

```text
R = (A \ {p}) union (B \ {-p})
```

be a legal, non-tautological Resolution resolvent after duplicate removal.

Assume:

1. the quotient graph of `A` is component-spanning; and
2. the quotient digraph of `B` contains a directed cycle.

## Theorem

The quotient graph of `R` is component-spanning **or** the quotient digraph of
`R` contains a directed cycle.

Equivalently, a legal Resolution inference with one `COMPONENT_SPANNING` parent
and one `DIRECTED_CYCLE` parent cannot produce an
`UNSAFE_ACYCLIC_LOW_RANK` resolvent.

## Proof

If removing `p` from `A` leaves a component-spanning graph, then
`A \ {p} subseteq R` already spans every quotient component.  Hence `R` is
component-spanning.

Suppose instead that `A \ {p}` is disconnected.  Since `A` was connected, the
external pivot edge `p` is a bridge of the quotient graph of `A`.  Let

```text
S | T
```

be the nontrivial quotient cut formed by deleting that bridge.

Assume for contradiction that `R` is not component-spanning.  Then no edge of
`B \ {-p}` crosses the cut `S | T`; otherwise that edge, together with the two
connected sides inherited from `A \ {p}`, would reconnect the quotient graph.

Now choose a directed cycle `Z` in `B`.

- If `Z` does not use `-p`, all of its literals occur in `B \ {-p}` and hence in
  `R`.
- If `Z` uses `-p`, then `Z` crosses `S | T` through `-p`.  A directed closed
  walk that leaves one side of a cut must cross the cut again to return to its
  starting side.  Therefore `Z` contains another cross-cut edge distinct from
  `-p`.  That edge belongs to `B \ {-p}`, contradicting the conclusion above
  that no such edge exists.

Thus every directed cycle available under the assumption that `R` is
non-spanning avoids the pivot and survives in `R`.  Because the resolvent is
legal and non-tautological, no surviving cycle literal is cancelled by an
opposite literal; duplicate removal also cannot destroy the cycle.

Therefore, whenever `R` is not component-spanning, `R` contains a directed
cycle.  This proves the dichotomy.

## Internal-pivot case

If the pivot is internal to one contracted component, deleting it cannot change
quotient connectivity of the component-spanning parent.  The first case of the
proof applies immediately, so the resolvent remains component-spanning.

## Regression witness against a stronger false claim

The stronger statement

> every new non-tail bridge from a spanning/cycle pair is born only on a
> two-component quotient

is false already on three quotient vertices.

Take

```text
A = {0->1, 0->2, 1->2}      (transitive spanning triangle)
B = {0->1, 1->2, 2->0}      (directed cycle)
pivot = 0->2 / 2->0
R = {0->1, 1->2}
```

The shared edge `0->1` is non-bridge in both parents and becomes a bridge in
`R`.  Nevertheless, `R` remains component-spanning.  The witness falsifies the
binary-origin reduction while fully respecting the proved safety theorem.

## Role in the complete classification

A second pure graph lemma closes `DIRECTED_CYCLE + DIRECTED_CYCLE`: a
pivot-avoiding cycle survives, while two pivot-using cycles leave opposite
directed paths whose union contains a directed cycle.  Internal-only parents
also preserve the external graph of the other parent.

Consequently, any unsafe legal resolvent between branch-safe parents must come
from two component-spanning parents.  The exact remaining route is a pivot that
is a bridge in both parents and induces the same quotient cut in both.  See
`GT_RESOLUTION_UNSAFE_ROUTE_CLASSIFICATION.md` for the complete proof.

The finite observation that all 77 fresh non-tail occurrences through `GT_8`
use the mixed spanning/cycle parent class is retained as replayable evidence,
but it is no longer required as the principal arbitrary-`n` reduction.

## Claim boundary

This is a pure one-inference quotient-graph theorem.  It does not prove the
arbitrary-`n` GT same-cut double-bridge exclusion, the lexicographic
singleton-tail handoff used as a candidate supporting mechanism, the global
Formula-Caching frontier transfer, a lower bound for unrestricted SAT or clause
learning, or `P != NP`.
