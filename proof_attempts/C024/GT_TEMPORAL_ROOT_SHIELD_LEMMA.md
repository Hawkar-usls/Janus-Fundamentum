# C024 — Temporal root-shield lemma

Status: **FORMALIZING**  
Scope: deterministic Policy-0A on the graph-tautology family `GT_n` before the historical `n-2` novelty frontier.

## 1. Why the invariant must be temporal

A raw local-Resolution output is not yet a parent-eligible state.  Policy-0A builds the parent indices once, emits resolvents into the output set, and never re-indexes fresh clauses during the same pass.

Therefore it is unnecessary—and false—to require every fresh resolvent to be structurally safe at the instant of birth.  The relevant requirement is:

> A fresh clause must be safe by the first later exact key in which it can be used as a Resolution parent.

This distinction survives the strongest finite attacks:

```text
raw local non-tail occurrences              93
fresh non-tail births                        77
raw non-singleton-tail occurrences           18

later exact-key non-tail occurrences         62
with immediate local ancestry                42
with inherited ancestry                      20
later occurrences with non-singleton tail     0
```

## 2. Canonical root shield

For a non-tail bridge `l : a -> b`, the root graph-tautology axiom

```text
N_a = OR_{x != a} (x -> a)
```

contains the complementary literal `-l : b -> a`.

If the Hasse component of `a` is `{a}`, then no comparison involving `a` has been assigned and `N_a` is untouched.  If the component of `b` has another vertex `c`, the literals `b -> a` and `c -> a` become parallel quotient edges.  Hence `-l` is non-bridge in `N_a`.

Thus the target eligibility condition is

```text
tail component is singleton
and
head component has size at least two.
```

## 3. Temporal Root-Shield Lemma — open for arbitrary n

Let `R` be a fresh local resolvent containing a non-tail bridge `l : a -> b`.
Before `R` or a restriction of `R` becomes a parent in a later exact residual key, exactly one of the following must hold:

1. **Extinction:** the lineage is satisfied, contradicted, subsumed, terminal, or absent from the next exact key;
2. **Shielded survival:** the lineage reaches the next parent-eligible exact key with

   ```text
   component(a) = {a},
   |component(b)| >= 2,
   ```

   so the untouched root clause `N_a` makes `-l` non-bridge.

Because `R` is not parent-eligible in its birth state, this lemma is sufficient to exclude a same-cut double-bridge use of `l`.

## 4. Exact finite handoff through GT_8

Every one of the 42 immediate-local lineages that survives into an exact key has a unique local origin and a unique intervening branch:

```text
unique local origin event                    42
post-local unit endpoint changes              0
child pre-unit events                         0
novel intervening branches                   42
branches touching the bad tail                0
branches joining the head to another part    39
branches disjoint from both endpoints         3
```

The branch deletes exactly one falsified source literal in all 42 cases.

The endpoint transitions are:

```text
local event shape      child exact-key shape
(1,1)  x12             (1,2)  x12
(1,2)  x11             contributes to shielded heads
(1,3)  x14             contributes to shielded heads
(1,4)   x5             contributes to shielded heads
```

Aggregated over all immediate and inherited exact-key occurrences:

```text
child shape (1,2)      12
child shape (1,3)      21
child shape (1,4)      17
child shape (1,5)      12
```

These are exactly the 62 canonical root-shield occurrences.

### Branch geometry

For 39 lineages, the branch comparison joins the current head component to a different singleton component and leaves the tail untouched.  Therefore the head size increases by exactly one.

For the remaining three lineages, the head already has size three; the branch is disjoint from the bad endpoints.  The root shield is already active and remains active.

No surviving branch merges the tail.

## 5. Inherited lineages

Twenty exact-key occurrences have inherited rather than immediate-local ancestry.  They enter their source exact key already satisfying the root-shield hypotheses.  Any later occurrence counted as the same bad lineage again has singleton tail and merged head, so the untouched `N_a` shield is re-certified at every parent-eligible key rather than assumed to persist syntactically without checking.

## 6. Remaining induction split

The arbitrary-`n` proof can now be divided into two sharply local claims.

### Lemma A — merged-tail extinction

A raw local non-tail occurrence whose tail component is non-singleton cannot become a component-spanning non-tail bridge in a later parent-eligible pre-frontier exact key.

Finite evidence: all 18 such raw occurrences have zero representatives among the 42 immediate-local surviving lineages.

### Lemma B — singleton-tail handoff

For a surviving fresh non-tail bridge with singleton tail:

- post-local units do not merge the tail;
- the selected branch does not merge the tail;
- if the head is singleton, the selected branch merges the head with another component;
- otherwise the root shield is already active.

The branch is chosen by the exact Policy-0A rule:

```text
maximum residual variable frequency,
minimum variable index on ties,
false branch first.
```

The remaining proof must derive the observed branch geometry from this rule and the GT-specific shape of a surviving resolvent lineage.

## 7. Consequence if Lemmas A and B are proved

At every parent-eligible pre-frontier key, every complementary double-bridge pair is tail/tail.  Complementary tail/tail bridges isolate opposite pivot endpoints, so their cuts differ.  The resolvent remains component-spanning; no unsafe acyclic low-rank clause is born at an eligible state.

Together with the graphic-rank accounting, this would close the local-Resolution obstruction in C024.  The historical Formula-Caching frontier counting still has to be transferred globally to the exact cache DAG.

## 8. Falsification conditions

The temporal lemma is rejected by any arbitrary-`n` execution containing:

1. a later exact-key non-tail bridge with non-singleton tail;
2. a surviving `(1,1)` non-tail lineage whose intervening branch avoids the head;
3. a surviving lineage whose branch or units merge the tail;
4. a fresh bad resolvent reused as a parent in its own local pass;
5. a parent-eligible shielded lineage in which `N_a` is absent, satisfied, or lacks a parallel complement.

The finite certificate searches directly for all five conditions through `GT_8`.

## Claim boundary

The one-pass temporal reduction and canonical root-shield implication are proved.  The complete survivor handoff is exhaustively certified through `GT_8`.  Lemmas A and B for arbitrary `n`, the global cache-frontier counting theorem, and `P` versus `NP` remain open.
