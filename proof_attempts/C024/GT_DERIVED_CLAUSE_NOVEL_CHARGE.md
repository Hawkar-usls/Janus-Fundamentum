# C024 — Derived-Clause Novelty Potential

**Status:** exact finite certificate for `GT_4..GT_8` / universal invariant under attack.

## Motivation

C024 showed that every observed component-joining unit occurs only after the
historical target level `n-2` has already been reached. The remaining concern was
that a clause learned earlier by Policy-0A local Resolution might be inherited
and later collapse to a unit without paying the missing historical novel joins.

The exact provenance audit rejects that concern for every observed pre-unit
component merge through `GT_8`.

## Exact provenance result

There are twelve pre-unit component merges in the verified range. Direct
comparison with the original root axioms classifies all twelve as derived-only.
One parent generation backward:

```text
3 arise from a local binary resolvent in the immediate parent state;
9 arise from a binary clause inherited in the parent residual key.
```

Recursive replay of pre-units, branch simplification, post-units and local
Resolution reaches one unique first origin for every event:

```text
all 12 originate at an explicit local Resolution event;
none requires an unexplained parent-output clause;
none has a shorter root-axiom origin under the recorded execution;
maximum minimum ancestry length = 5 transitions.
```

## Novel-branch charge certificate

For every certified path, let:

- `r` be the novelty level of the call where the origin resolvent is created;
- `w` be the width of that origin clause;
- `t = n-2` be the historical target novelty;
- `k` be the number of later branch restrictions that narrow the clause before
  it becomes a component-joining unit.

The executable audit verifies simultaneously:

```text
k = w - 1
r + k = t
```

and, at every one of the `k` transitions:

1. the selected branch variable occurs in the active provenance clause;
2. the branch removes exactly one literal;
3. the branch joins two distinct Hasse components and is therefore novel;
4. no pre-unit or post-unit stage removes a provenance literal;
5. no nonnovel branch narrows the provenance clause.

Thus the derived clause does not replace the historical joins. It stores a
conditional consequence whose conversion to a unit still consumes exactly the
missing novel branches.

## Finite data

```text
origin width      occurrences      required novel narrowing steps
2                      3                         1
3                      4                         2
4                      2                         3
5                      1                         4
6                      2                         5
```

For `GT_8`, both pre-unit merges originate at novelty level `1` from width-six
resolvents:

```text
(-2,-4,-5,-6,-7, 8)
(-1,-4,-5,-6,-7,-8)
```

Each clause is narrowed through five novel branches:

```text
width 6 -> 5 -> 4 -> 3 -> 2 -> 1
novelty 1 -> 2 -> 3 -> 4 -> 5 -> 6
```

## Candidate potential

For an active derived clause `C` under partial order `P`, define

```text
Phi(P,C) = novelty(P) + active_width(C under P) - 1.
```

Along all twelve certified paths:

```text
Phi(P,C) = n-2
```

at origin and after every narrowing step. This suggests the following universal
invariant.

## Derived-clause novelty-potential conjecture

Let `C` be a clause emitted by one Policy-0A local Resolution pass on `GT_n`.
Suppose some descendant restriction turns the inherited residual of `C` into a
component-joining unit before or at the first historical target frontier. Then:

1. every width-decreasing restriction on the relevant provenance path is a
   novel branch;
2. each such branch decreases active width by at most one;
3. unit propagation does not decrease active width before the target without an
   independently chargeable proof event;
4. consequently

```text
origin_novelty + origin_width - 1 >= n-2.
```

A stronger form would show that `Phi` never decreases while `C` remains capable
of producing an early component-joining unit.

## Why the conjecture is nontrivial

The finite certificate follows the clauses that actually become component-
joining units. It does not yet quantify over:

- all local resolvents emitted in all states;
- clauses that disappear, become satisfied or participate in later Resolution;
- multiple possible provenance paths for the same residual clause;
- unit cascades capable of removing several literals;
- exact-cache identification of descendants with different clause ancestry.

Therefore extrapolating the observed equality to all `n` would be invalid.

## Next falsification test

Track every local resolvent through every descendant occurrence in `GT_4..GT_8`
and report any transition where:

```text
active width decreases
but historical novelty does not increase.
```

The test must distinguish harmless clauses from clauses still capable of
producing a component-joining unit before the target. A counterexample kills the
simple potential. Survival yields the precise combinatorial statement that must
be proved asymptotically.

## Claim boundary

This is a machine-verified finite charge pattern and a conjectured invariant. It
is not an asymptotic lower bound for `JANUS-FC_local` and does not resolve P
versus NP.
