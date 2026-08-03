# C024 — Unshielded root localization

Status: **FINITE_CERTIFIED / ARBITRARY_N_OPEN**  
Scope: immediate-local non-tail bridge lineages that survive into a later pre-frontier exact key of deterministic Policy-0A on `GT_n`.

## 1. Why this reduction matters

The earlier branch-handoff target asked for a history-sensitive frequency theorem covering every one of the 42 surviving immediate-local dangerous lineages through `GT_8`.

That target is unnecessarily broad. A dangerous non-tail bridge literal

```text
l : a -> b
```

is already canonically shielded whenever

```text
component(a) = {a}
and
|component(b)| >= 2.
```

The untouched root non-minimality clause `N_a` then contains the complementary literal `-l` together with at least one parallel quotient edge, so `-l` is not a bridge in that root parent.

Therefore branch selection matters only while both endpoint components are singleton.

## 2. Exact finite split through GT_8

The 42 immediate-local lineages that survive into a later parent-eligible exact key split exactly as follows:

```text
all surviving immediate-local lineages      42
already shielded before branch              30
unshielded singleton/singleton               12
unshielded non-root                           0
unshielded at root                           12
```

Head-component sizes:

```text
head size 1     12
head size 2     11
head size 3     14
head size 4      5
```

Thus every non-root surviving lineage in the finite trace already has a merged head and an active canonical root shield before the branch is selected.

## 3. Exact root family

The twelve unshielded surviving lineages are all in the root state:

```text
GT_4: 1
GT_5: 2
GT_6: 2
GT_7: 3
GT_8: 4
```

For all twelve, the deterministic selected comparison has relation

```text
HEAD_TO_OTHER.
```

The selected branch therefore merges the singleton head with another component while leaving the singleton tail untouched. The child lineage, when admitted, satisfies the canonical shield condition.

Selected variables in the finite family:

```text
variable 2: 2 occurrences
variable 3: 10 occurrences
```

These counts are finite data only; the arbitrary-`n` root selector formula is not inferred from them.

## 4. Correct replacement for the broad history theorem

The local handoff proof no longer needs one frequency theorem over every surviving lineage. It splits into two narrower obligations.

### U1 — Non-root unshielded-survivor exclusion

Prove for arbitrary `n`:

> Every immediate-local non-tail bridge lineage that survives to a non-root pre-frontier parent state already has singleton tail and merged head, hence an active canonical `N_a` shield.

Equivalently, no singleton-tail/singleton-head dangerous lineage survives into a non-root parent state.

The proof may use extinction, post-unit contradiction, prior branch geometry, and root-clause preservation. It need not determine the exact selected variable once the head is already merged.

### U2 — Root endpoint-or-shield-or-extinction

At the root, follow every immediate-local singleton/singleton dangerous lineage through the deterministic branch and child pre-unit closure. Prove that each polarity yields one of:

```text
terminal or clause extinction;
loss of spanning or bridge status;
tail-singleton safe form;
canonical N_a shield after head merge.
```

A disjoint selected branch is not forbidden by itself. It is forbidden only if it carries an unshielded non-tail bridge into an admitted child exact key.

## 5. Relation to the frequency obstruction

Quotient-component frequency factorization remains false:

```text
nonuniform component-pair groups          1,133 / 1,851
nonuniform selected component pairs         463 / 604
```

The clause-history contribution profile also remains heterogeneous. Those negative results are still valuable, but the root-localization reduction means they may not be needed for the final proof:

```text
non-root surviving family: shield already active;
root unshielded family: explicit root-only calculation.
```

The history-sensitive frequency route is retained as a fallback, not the primary gate.

## 6. Falsification conditions

The reduction is falsified by any arbitrary-`n` reachable execution containing:

1. a non-root surviving immediate-local dangerous lineage with singleton head;
2. an admitted root child carrying the same unshielded non-tail bridge;
3. a claimed canonical shield whose root residual is absent;
4. a complementary root literal which remains a bridge;
5. a lineage classified as extinct despite remaining in the child exact key.

The finite localization checker attacks condition 1 through `GT_8`. The root-only handoff checker attacks conditions 2–5 and extends the root calculation beyond the full-search frontier.

## 7. Consequence if U1 and U2 are proved

Together with the already proved frozen fresh-side barrier, post-unit total-component collapse barrier, and pure branch route classification, U1 and U2 imply that no same-cut double-bridge pair becomes co-eligible in a later exact key.

This would complete T2b and make T3 a direct temporal induction over

```text
K -> R -> P -> B -> K'.
```

The global Formula-Caching lower-bound transfer would remain separate.

## Claim boundary

Root localization is exhaustively certified for the 42 surviving immediate-local lineages through `GT_8`. U1 and U2 for arbitrary `n`, completed T2b/T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
