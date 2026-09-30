# C024 — Canonical root-shield lemma

Status: **FORMALIZING**  
Scope: parent-eligible pre-frontier exact residual keys of deterministic Policy-0A on `GT_n`.

## 1. Pairwise safety target

The surviving pairwise invariant is:

```text
non-tail bridge l in a component-spanning clause C
    => every component-spanning complementary occurrence -l is a non-bridge.
```

The universal single-clause claim

> every spanning bridge is tail-singleton

is false: 62 explicit non-tail bridge occurrences exist through `GT_8`.  Safety is intrinsically pairwise.

## 2. Root non-minimality clauses

For every vertex `a`, `GT_n` contains

```text
N_a = OR_{x != a} (x -> a),
```

asserting that `a` has a predecessor.

Let `l : a -> b`.  The complementary literal `-l : b -> a` belongs to `N_a`.

## 3. Conditional root-shield lemma — proved

### Lemma 3.1 — singleton tail leaves `N_a` untouched

Assume the current Hasse component of `a` is `{a}`.  Any assigned comparison involving `a` would add an undirected comparison edge incident to `a` and merge it with another component.  Hence no comparison involving `a` has been assigned and

```text
N_a | alpha = N_a.
```

The root clause remains literally present in the exact residual key.

### Lemma 3.2 — merged head supplies parallel shields

Let `B` be the current Hasse component containing `b`, with `|B| >= 2`.  For each `c in B`, `c != b`, the untouched `N_a` contains both

```text
b -> a
c -> a.
```

After quotienting Hasse components, these are parallel edges between `{a}` and `B`.  Therefore deleting `b -> a` leaves an alternate edge, so `-l` is not a bridge in `N_a`.

The exact number of parallel alternatives is

```text
|B| - 1.
```

### Corollary 3.3 — canonical root shield

If a parent-eligible non-tail bridge `l : a -> b` satisfies

```text
component(a) = {a}
and
|component(b)| >= 2,
```

then the untouched root axiom `N_a` is a component-spanning complementary parent in which `-l` is non-bridge.  Thus `l` cannot participate in a complementary double-bridge pair.

This graph argument uses no width bound, Resolution budget, pair order, or cache assumption.

## 4. Exhaustive exact-key certificate through GT_8

Every one of the 62 pre-frontier exact-key non-tail bridge occurrences satisfies the hypotheses:

```text
non-tail exact-key bridge occurrences       62
singleton tail                              62
head size at least two                      62
untouched root clause N_a                   62
parallel multiplicity exactly |B|-1         62
```

```text
head component size       2   3   4   5
occurrences              12  21  17  12
parallel alternatives     1   2   3   4
```

The broader complement audit reconstructs 119 pivot-avoiding paths:

```text
length 1, orientation F      71
length 2, orientation FR     48
```

Exactly 62 witnesses are canonical untouched `N_a` shields—one per bad exact-key occurrence.  Other inherited clauses provide redundant alternate paths.

## 5. Co-resolvable bridge census

Across the same pre-frontier exact keys:

```text
component-spanning clause occurrences       7,918
spanning bridge literal occurrences          2,828
  tail-singleton                             2,766
  head-singleton                                18
  non-singleton cut                             44

complementary double-bridge pairs              611
  tail/tail                                    611
  different bridge cuts                        611
  same bridge cut                                0
```

For a complementary pivot `l : a -> b` and `-l : b -> a`, tail-singleton bridges isolate opposite endpoints.  Their cuts differ, so the union of the pivot-deleted parent graphs remains connected and the resolvent remains component-spanning.

The only unresolved issue is why every non-tail bridge becomes shielded before parent eligibility.  That is temporal, not a property of raw local output.

## 6. Raw local output falsifies immediate safety

Through `GT_8`, one-pass local Resolution exposes:

```text
non-tail resolvent-literal occurrences       93
fresh non-tail births                        77
preexisting non-tail ancestry                16
raw occurrences with non-singleton tail      18
```

Endpoint shapes across all 93 occurrences include singleton/singleton, singleton-tail/merged-head, and non-singleton-tail cases.  Therefore the stronger claim

> every fresh non-tail bridge is born with an active root shield

is false.

This does not threaten the parent-pair invariant because a fresh resolvent is not re-indexed as a parent during the same one-pass stage.

## 7. Exact temporal handoff through GT_8

### Shielded survivors

The later exact-key family contains:

```text
non-tail occurrences                         62
immediate local-resolvent ancestry            42
inherited shielded ancestry                   20
non-singleton-tail exact-key occurrences       0
```

For the 42 immediate-local surviving lineages:

```text
post-local endpoint changes                   0
child pre-unit events                         0
novel branch                                 42
branch touching tail                          0
branch joins head to another component       39
branch disjoint after shield already active   3
```

Tail exclusion follows the exact lexicographic Policy-0A selector:

```text
strict tail frequency gap                    23
maximum-frequency tail tie                   19
minimum-index tie-break excludes tail        19
```

Thus frequency alone is insufficient; indices are part of the required arbitrary-`n` invariant.

### Merged-tail extinction

The 18 raw non-singleton-tail occurrences split exactly:

```text
causal post-unit contradiction               17
GT_4 branch-UNSAT extinction                  1
later bad exact-key descendant                0
```

Among the 17 contradiction cases, the merged-tail resolvent is:

```text
direct conflict source                        4
ancestor in all-source unit-reason DAG        13
merely co-located                              0
```

The unique `GT_4` branch case executes two UNSAT children; both terminate before yielding an exact key carrying the bad lineage.

## 8. Correct remaining theorem gate

The arbitrary-`n` proof now consists of two exact temporal lemmas.

### A. Merged-Tail Extinction Disjunction

A fresh non-tail bridge with non-singleton tail must be causally consumed by post-unit contradiction, eliminated in every recursive child, or transformed into a safe structure before any later parent-eligible exact key.

### B. Lexicographic Singleton-Tail Handoff

If a fresh non-tail bridge with singleton tail survives, the exact selector

```text
minimum (-frequency(variable), variable_index)
```

must avoid every tail-touching comparison.  If the head is singleton it must merge the head before the next exact key; otherwise the root shield is already active and may be preserved by a disjoint branch.

Once A and B are proved, every parent-eligible non-tail bridge has the canonical `N_a` shield, every complementary double-bridge pair is tail/tail with different cuts, and local Resolution cannot create an unsafe acyclic low-rank parent clause before the historical frontier.

## 9. Remaining global step

Closing the local structural obstruction is not yet the final Policy-0A lower bound.  A separate theorem must transfer the historical `2^(n-2)` restriction frontier to the exact cache DAG, accounting for:

```text
novel branches;
unit-paid component joins;
local proof events;
cache reuse.
```

The finite frontier-injectivity and component-merge audits support this route, but the arbitrary-`n` counting theorem remains open.

## Claim boundary

The canonical root-shield implication and different-cut graph lemma are proved.  Their complete temporal realization is exhaustively certified through `GT_8`, including causal extinction provenance and lexicographic branch selection.  The two arbitrary-`n` temporal lemmas, global cache-frontier transfer, and `P` versus `NP` remain open.
