# C024 — Temporal root-shield lemma

Status: **FORMALIZING**  
Scope: deterministic Policy-0A on the graph-tautology family `GT_n` before the historical `n-2` novelty frontier.

## 1. Why the invariant must be temporal

A raw local-Resolution output is not yet parent-eligible.  Policy-0A constructs the parent indices once, emits resolvents into the output set, and never re-indexes fresh clauses during the same local pass.

Therefore the false requirement

> every fresh resolvent is immediately structurally safe

is unnecessary.  The correct requirement is:

> Every fresh bad lineage is either extinct or canonically shielded before the first later exact key in which it can become a Resolution parent.

The exhaustive trace through `GT_8` separates the two stages:

```text
raw local non-tail resolvent-literal occurrences       93
fresh non-tail births                                   77
raw occurrences with non-singleton tail                 18

later exact-key non-tail occurrences                    62
with immediate local ancestry                           42
with inherited ancestry                                 20
later occurrences with non-singleton tail                0
```

## 2. Canonical root shield

For a non-tail bridge `l : a -> b`, the root graph-tautology axiom

```text
N_a = OR_{x != a} (x -> a)
```

contains `-l : b -> a`.

If the Hasse component of `a` is `{a}`, no comparison involving `a` has been assigned, so `N_a` remains literally untouched.  If the component of `b` contains another vertex `c`, then `b -> a` and `c -> a` become parallel quotient edges.  Hence `-l` is non-bridge in `N_a`.

The parent-eligibility shield condition is therefore

```text
component(a) = {a}
and
|component(b)| >= 2.
```

This implication is a direct graph argument, independent of width, Resolution budget, and parent enumeration order.

## 3. Temporal Root-Shield Lemma — open for arbitrary n

Let `R` be a fresh local resolvent containing a non-tail bridge `l : a -> b`.  Before `R` or a restriction of `R` becomes a parent in a later pre-frontier exact key, prove that one of the following holds:

1. **Extinction.** The lineage is involved in a terminal contradiction, is eliminated in every recursive child, is satisfied, deleted, subsumed, becomes nonspanning, or otherwise does not enter a later exact key as the same bad bridge.
2. **Shielded survival.** The lineage enters the later exact key with

   ```text
   component(a) = {a},
   |component(b)| >= 2,
   ```

   so the untouched root clause `N_a` makes the complementary literal non-bridge.

Because a fresh resolvent is not a parent during its birth pass, this temporal statement is sufficient to exclude its use in a same-cut double-bridge pair.

## 4. Shielded exact-key family through GT_8

Every one of the 62 exact-key non-tail occurrences is canonically root-shielded:

```text
singleton tail                                  62
head size at least two                          62
untouched N_a                                   62
parallel alternatives exactly head_size - 1    62
```

```text
head size                  2   3   4   5
exact-key occurrences     12  21  17  12
parallel alternatives      1   2   3   4
```

Twenty occurrences are inherited from an earlier shielded exact key.  Forty-two have immediate local-resolvent ancestry and pass through one intervening branch before entering their first parent-eligible exact key.

## 5. Singleton-tail handoff through GT_8

For all 42 immediate-local surviving lineages:

```text
unique local origin event                      42
post-local endpoint changes                     0
child pre-unit events                           0
novel intervening branch                       42
branch touching the bad tail                    0
branch joining head to another component       39
branch disjoint after head already merged       3
one falsified source literal deleted           42
```

The endpoint-shape transition is:

```text
local event shapes:
(1,1) x12
(1,2) x11
(1,3) x14
(1,4)  x5

child exact-key shapes, including inherited occurrences:
(1,2) x12
(1,3) x21
(1,4) x17
(1,5) x12
```

Every `(1,1)` surviving lineage becomes `(1,2)` before parent eligibility.  No surviving branch merges the tail.

### Exact branch-selection mechanism

Policy-0A chooses the minimum-index variable among those with maximum residual frequency.  Tail exclusion uses both parts of this lexicographic rule:

```text
strict frequency gap excludes every tail variable       23
some tail variable ties for maximum                      19
minimum-index tie-break excludes the tail                19
selected variable is first among maximum-frequency set   42
```

Selected branch relation:

```text
HEAD_TO_OTHER   39
DISJOINT         3
TAIL_TO_OTHER    0
TAIL_HEAD        0
```

The three disjoint cases already have a merged head and active root shield.  Thus a frequency-only theorem would be false; the arbitrary-`n` proof must preserve variable indices and use the exact lexicographic selector.

## 6. Merged-tail extinction through GT_8

The stronger conjecture

> all 18 raw merged-tail occurrences die by post-unit conflict

is false.  The exact split is:

```text
fresh merged-tail occurrences                 18
causal post-unit contradiction                17
GT_4 branch-UNSAT extinction                   1
later bad exact-key descendant                 0
```

For the 17 contradiction cases:

```text
EMPTY_ON_UNIT_ASSIGNMENT                      12
OPPOSITE_UNITS                                 5
merged-tail resolvent is direct conflict source   4
merged-tail resolvent is ancestor source         13
merely co-located                                 0
executed child calls                              0
```

The all-source backward reason-DAG therefore contains every conflict-state merged-tail resolvent: four directly and thirteen through earlier unit reasons.

The unique `GT_4` exception executes two UNSAT children without post-unit propagation.  Both children terminate before yielding an exact key carrying the bad lineage.

The correct arbitrary-`n` extinction statement is consequently a disjunction of causal unit-conflict extinction, recursive extinction, and any separately proved structural-safety transition.

## 7. Remaining induction split

### Lemma A — Merged-Tail Extinction Disjunction

A fresh non-tail bridge with non-singleton tail cannot enter a later parent-eligible pre-frontier exact key unchanged.  It must be causally consumed by contradiction, eliminated throughout the recursive children, or transformed into a safe structure.

The next proof attack should classify the seventeen finite reason closures by root-axiom ancestry and directed quotient geometry.  The single `GT_4` recursive case may be treated as a finite base case only if a uniform conflict theorem is proved for `n >= 5`.

### Lemma B — Lexicographic Singleton-Tail Handoff

For a surviving fresh non-tail bridge with singleton tail, prove from GT clause geometry and the exact selector that:

```text
for every tail-touching variable t,
(-frequency(selected), selected_index)
    <
(-frequency(t), t_index),
```

and that a singleton head is joined to another component before the next exact key.  If the head is already merged, a disjoint selected branch may preserve the existing root shield.

## 8. Consequence if Lemmas A and B are proved

At every parent-eligible pre-frontier exact key, every complementary double-bridge pair is tail/tail.  The complementary pivot orientations isolate opposite endpoints, so the two bridge cuts differ.  Their resolvent remains component-spanning and cannot be an unsafe acyclic low-rank clause.

Together with graphic-rank deficit accounting, this would close the **local-Resolution obstruction** in C024.

A separate theorem is still required to transfer the historical `2^(n-2)` Formula-Caching frontier to the exact Policy-0A cache DAG and state the final asymptotic lower bound.

## 9. Falsification conditions

The temporal lemma is rejected by any arbitrary-`n` execution containing:

1. a later exact-key non-tail bridge with non-singleton tail;
2. a contradictory merged-tail birth whose all-source reason closure excludes the lineage;
3. a recursive child carrying the merged-tail bad bridge into a parent-eligible exact key;
4. a surviving singleton-tail lineage whose transition merges the tail;
5. a surviving `(1,1)` lineage whose transition does not merge the head;
6. a parent-eligible lineage whose `N_a` clause is absent or lacks a parallel complement;
7. a fresh resolvent reused as a parent in its own local pass.

The finite certificates search directly for all seven conditions through `GT_8`.

## Claim boundary

The one-pass temporal reduction and canonical root-shield implication are proved.  The full extinction/handoff package is exhaustively certified through `GT_8`, including causal reason provenance and exact branch-selection mechanisms.  Lemmas A and B for arbitrary `n`, the global cache-frontier transfer, and `P` versus `NP` remain open.
