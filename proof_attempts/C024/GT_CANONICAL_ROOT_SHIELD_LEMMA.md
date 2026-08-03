# C024 — Canonical root-shield lemma

Status: **FORMALIZING**  
Scope: parent-eligible pre-frontier exact residual keys of the deterministic Policy-0A run on `GT_n`.

## 1. Pairwise safety target

The co-resolvable tail-bridge certificate isolates the correct pairwise invariant:

```text
non-tail bridge l in a spanning clause C
    => every spanning complementary occurrence -l is a non-bridge.
```

The trace exposes a canonical complementary shield already present in the original graph-tautology formula.

## 2. Root non-minimality clauses

For every vertex `a`, `GT_n` contains

```text
N_a = OR_{x != a} (x -> a),
```

asserting that `a` has a predecessor.

Let `l : a -> b`.  Its complement `-l : b -> a` belongs to `N_a`.

## 3. Conditional root-shield lemma — proved

### Lemma 3.1 — singleton tail leaves `N_a` untouched

Assume the current Hasse component of `a` is `{a}`.  Any assigned comparison between `a` and another vertex would add an undirected comparison edge incident to `a` and merge it with another component.  Therefore no comparison involving `a` has been assigned, and

```text
N_a | alpha = N_a.
```

So `N_a` remains literally present in the exact residual key.

### Lemma 3.2 — merged head supplies a parallel shield

Assume the Hasse component `B` containing `b` has size at least two.  For any `c in B`, `c != b`, the untouched root clause `N_a` contains both

```text
b -> a
c -> a.
```

After quotienting Hasse components these are parallel edges between `{a}` and `B`.  Deleting `b -> a` therefore leaves an alternate edge.  Thus `-l` is not a bridge in `N_a`.

The number of parallel alternatives is exactly

```text
|B| - 1.
```

### Corollary 3.3 — canonical root shield

If a parent-eligible non-tail bridge `l : a -> b` has

```text
component(a) = {a}
and
|component(b)| >= 2,
```

then the untouched root axiom `N_a` is a component-spanning complementary parent in which `-l` is non-bridge.  Hence `l` cannot participate in a same-cut double-bridge pair.

This graph argument uses no width bound, Resolution budget, or parent enumeration order.

## 4. Exhaustive exact-key certificate through GT_8

Every one of the 62 non-tail bridge occurrences in a pre-frontier exact key satisfies the hypotheses:

```text
non-tail bridge occurrences                 62
singleton tail component                    62
head component of size at least two         62
untouched root non-minimality axiom N_a      62
exact parallel multiplicity |B|-1           62
```

```text
head component size       2   3   4   5
occurrences              12  21  17  12
parallel alternatives     1   2   3   4
occurrences              12  21  17  12
```

The broader path audit finds 119 complementary alternate paths.  Exactly 62 are canonical untouched root shields—one for each exact-key bad occurrence.

## 5. Falsified stronger birth claim

The earlier proposed lemma

> every fresh non-tail bridge is born with singleton tail and merged head

is false at the raw output of local Resolution.

Through `GT_8`, the local pass exposes 93 non-tail resolvent-literal occurrences.  Of these, 77 are first births and 16 already have non-tail ancestry in a parent.  The endpoint-shape census over all 93 occurrences is:

```text
singleton / singleton                       19
singleton tail / merged head                 56
non-singleton tail                           18
```

The v2 audit intentionally does not infer a first-birth shape cross-tabulation that it has not explicitly recorded.  The decisive falsifier is that raw local output can contain both singleton/singleton and non-singleton-tail non-tail bridges.

This does not contradict the root-shield lemma because fresh resolvents are not indexed as parents again during the same one-pass local stage.

## 6. Correct remaining gate: temporal parent eligibility

The required arbitrary-`n` statement is now:

### Temporal Root-Shield Lemma

For every fresh local-Resolution non-tail bridge literal `l : a -> b`, before its clause can appear in any later parent-eligible exact residual key, one of the following occurs:

1. the clause is satisfied, contradicted, subsumed, or otherwise absent from the next exact key; or
2. it survives with

   ```text
   component(a) = {a}
   and
   |component(b)| >= 2.
   ```

In case 2, Lemmas 3.1–3.2 activate the untouched root shield `N_a` before the clause can participate in another Resolution step.

Equivalent operational form:

```text
fresh bad resolvent
    -- not parent-eligible in the same state -->
next exact key, if any
    -- either absent or canonically root-shielded -->
no same-cut double-bridge pair.
```

## 7. Finite temporal evidence through GT_8

The exact-key lifecycle contains:

```text
exact-key non-tail occurrences              62
immediate local-resolvent ancestry           42
inherited ancestry                            20
```

For all 42 immediate local lineages:

```text
event tail size = 1                          42
post-unit endpoint change                     0
child pre-unit events                         0
intervening branch is novel                  42
intervening branch touches tail               0
branch joins head to another component       39
branch is disjoint; head already merged       3
one falsified branch literal is deleted      42
```

All 12 lineages entering the local event with shape `(1,1)` reach the child exact key with shape `(1,2)`.  None of the 18 raw local non-tail occurrences with non-singleton tail appears among the 42 immediate local lineages that survive as exact-key bad occurrences.

Thus every surviving immediate lineage is root-shielded by its first future parent-eligible key.  The 20 inherited occurrences are already shielded in the exact key from which they are inherited.

## 8. Remaining proof obligations

The arbitrary-`n` proof must establish two survivor claims from the exact Policy-0A rules and GT clause geometry:

1. **Merged-tail extinction.** A local non-tail bridge occurrence with non-singleton tail cannot survive as a component-spanning non-tail bridge into a later parent-eligible exact key.
2. **Singleton-tail handoff.** If a local non-tail bridge with singleton tail survives, the intervening transition never merges the tail; when the head is singleton, it merges the head before the next exact key.

The deterministic branch rule is most-frequent-variable with minimum-index tie breaking.  The finite surviving lineages show that the selected branch literal is always the complement of one source-clause literal and either joins the bad head to a singleton component or is disjoint after the head is already merged.  Deriving this pattern uniformly is the current induction gate.

## 9. Consequence for C024

The Temporal Root-Shield Lemma, together with the graphic-rank and different-cut lemmas, would exclude unsafe acyclic low-rank clauses from every parent-eligible pre-frontier key.  A separate global counting argument would still be needed to transfer the historical Formula-Caching lower bound to Policy-0A.

## Claim boundary

The conditional root-shield argument is proved, and its hypotheses plus the complete temporal handoff are exhaustively certified through `GT_8`.  The arbitrary-`n` temporal survivor lemma and final lower-bound transfer remain open.  Nothing here resolves `P` versus `NP`.
