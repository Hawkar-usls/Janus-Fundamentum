# C024 — Merged-tail frontier-localization lemma

Status: **FORMALIZING**  
Scope: fresh local-Resolution non-tail bridge literals with non-singleton oriented tail in deterministic Policy-0A on `GT_n`.

## 1. Why extinction is no longer the critical lower-bound gate

The complete finite trace through `GT_8` shows:

```text
fresh merged-tail non-tail births             18
born with exactly two Hasse components        18
born at novelty level n-2                     18
born before the historical target              0
```

Thus every observed merged-tail birth occurs only after the historical restriction frontier has already been reached.  Its later fate—causal unit contradiction in seventeen cases and recursive extinction in one `GT_4` case—is needed for exact solver semantics, but not to justify the first `n-2` component joins.

The critical arbitrary-`n` statement should therefore be localization, not extinction:

> A fresh merged-tail non-tail bridge cannot be born while three or more Hasse components remain.

## 2. Binary-origin graph lemma — proved

### Lemma 2.1

Let a Resolution event have parents

```text
L = (l OR p)
R = (l OR -p)
```

and resolvent

```text
Q = (l).
```

Project the clauses to the current undirected Hasse-component quotient.  Assume:

1. `L` or `R` is component-spanning;
2. `l` is an external edge;
3. `l` is non-bridge in that component-spanning parent.

Then the quotient has exactly two vertices.

### Proof

The component-spanning parent contains exactly two quotient edges: the edge of `l` and the pivot edge.  Since `l` is non-bridge, deleting it leaves the parent graph connected.  The remaining graph has one edge, so a connected spanning graph can have at most two vertices.  Because `l` is external, its endpoints are distinct, so the quotient has at least two vertices.  Hence it has exactly two vertices.  ∎

### Corollary 2.2

Any fresh merged-tail bridge born by this binary/binary-to-unit pattern is born only after the current comparison graph has contracted to two Hasse components.

No unit-reason analysis is required for this localization.

## 3. Finite binary-origin certificate through GT_8

For the seventeen post-unit-conflict merged-tail origins:

```text
origin resolvent width                         1
left/right parent widths                    2,2
both parents contain the bad literal          17
one parent component-spanning                 17
one parent directed-cycle                     17
bad literal nonbridge in both parents          17
quotient component count                       2
novelty level                                n-2
```

The exact parent-orientation pattern is:

```text
one parent: UNDIRECTED_CYCLE_ONLY
one parent: HAS_DIRECTED_CYCLE
```

Consequently the event has the symbolic form

```text
(l OR p), (l OR -p)  |-  (l),
```

where `p` and `l` project to the same undirected quotient edge.  One parent uses the pivot orientation parallel to `l`; the other uses the opposite orientation and forms a directed 2-cycle.

The unique `GT_4` recursive-extinction case is also certified at two quotient components and novelty `n-2`; it is retained as a finite base case until its exact origin pattern is absorbed into a uniform proof.

## 4. Correct arbitrary-n localization theorem

### Merged-Tail Frontier Localization

For every fresh local resolvent `Q` containing a component-spanning non-tail bridge literal `l : a -> b` with

```text
|component(a)| > 1,
```

prove that the origin Resolution event satisfies the binary-origin hypotheses of Lemma 2.1, or belongs to a separately proved finite/base structural case.  Therefore

```text
current component count = 2.
```

Equivalently, no fresh merged-tail non-tail bridge is born while at least three Hasse components remain.

## 5. What remains to prove

The finite data establish the binary pattern, but the arbitrary-`n` proof must derive it from the GT residual family rather than assume it.  The required structural statement is:

> If a Resolution step first turns a literal `l` into a non-tail bridge, then every alternate path for `l` in both parents uses the complementary pivot.  In a reachable pre-frontier GT residual, this forces both parent residuals to be binary and the pivot to be quotient-parallel to `l`.

The universal graph part after binary reduction is already proved by Lemma 2.1.  The remaining GT-specific burden is the **binary-origin reduction**.

Candidate ingredients:

1. every reachable parent clause before the target is either component-spanning or contains a directed cycle;
2. one-pass Resolution removes only one complementary pivot pair;
3. the bad literal is nonbridge in both parents but a bridge in the resolvent;
4. every pivot-avoiding alternate path would survive into the resolvent, so all alternate paths must use the pivot;
5. GT transitivity and non-minimality residuals may restrict such pivot-dominated paths to quotient-parallel two-edge clauses.

A counterexample is a reachable fresh merged-tail bridge born with at least three quotient components or from a wider pivot-dominated parent pair.

## 6. Consequence for the C024 route

If Merged-Tail Frontier Localization is proved, merged-tail clauses cannot reduce the number of historical restrictions required to reach the two-component frontier.  Their terminal semantics can be charged after the frontier:

```text
17 causal post-unit contradictions
1 GT_4 recursive extinction
```

The pre-frontier local-Resolution obstruction then depends only on the singleton-tail family:

```text
surviving singleton tail
    -> lexicographic branch avoids tail
    -> singleton head is merged, or shield already active
    -> untouched N_a root shield
    -> no same-cut complementary double bridge.
```

A global theorem must still relate component joins, unit-paid joins, terminal frontier leaves, and exact-cache keys to the historical `2^(n-2)` counting argument.

## Claim boundary

The binary-origin graph lemma is proved, and all eighteen merged-tail births are exhaustively localized to two components and novelty `n-2` through `GT_8`.  The arbitrary-`n` binary-origin reduction, singleton-tail lexicographic handoff, global cache-frontier transfer, and `P` versus `NP` remain open.
