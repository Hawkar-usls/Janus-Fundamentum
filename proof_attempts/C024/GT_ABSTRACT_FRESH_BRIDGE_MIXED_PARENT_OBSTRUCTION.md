# C024 — Abstract obstruction to mixed-parent necessity

Status: **EXACT FINITE OBSTRUCTION / GT-SPECIFIC ANCESTRY REQUIRED**  
Scope: the remaining non-root Gate A in exact Policy-0A graph-tautology analysis.

## 1. Tempting but false graph claim

The complete `GT_4,...,GT_8` fresh-birth replay reports that every fresh non-tail bridge occurrence has parent safety classes

```text
COMPONENT_SPANNING x DIRECTED_CYCLE.
```

It is tempting to promote this to a pure graph theorem:

> Every legal Resolution birth of a fresh non-tail bridge from branch-safe
> clauses must have one component-spanning parent and one directed-cycle parent.

This statement is false.

## 2. Abstract legal-clause universe

For `n=3,4` singleton quotient vertices, enumerate every legal directed clause by choosing, for each unordered vertex pair, exactly one of

```text
absent
low -> high
high -> low.
```

Opposite literals of the same comparison variable cannot coexist in one clause.
Retain the branch-safe classes

```text
DIRECTED_CYCLE
COMPONENT_SPANNING
INTERNAL_ONLY.
```

For every pivot pair with complementary orientations in two parents:

1. delete both pivot occurrences;
2. take the legal union of the remaining edges;
3. retain component-spanning resolvents;
4. inspect every resolvent bridge occurrence;
5. call it fresh when the same directed occurrence was not a bridge in any parent containing it;
6. classify its bridge role as `TAIL_SINGLETON` or `NON_TAIL`.

## 3. Exhaustive result

Independent replay on all legal safe clauses gives:

```text
fresh bridge occurrences                 13,896
fresh non-tail occurrences                7,380
fresh tail-singleton occurrences          6,516
spanning resolvents                       47,052
inherited bridge occurrences             13,776
```

Fresh parent-class pairs:

```text
COMPONENT_SPANNING x COMPONENT_SPANNING    9,984
COMPONENT_SPANNING x DIRECTED_CYCLE         3,912
```

Fresh **non-tail** parent-class pairs:

```text
COMPONENT_SPANNING x COMPONENT_SPANNING    5,304
COMPONENT_SPANNING x DIRECTED_CYCLE         2,076
```

Thus most abstract fresh non-tail births in this finite universe come from two
component-spanning parents.

```text
ABSTRACT_FRESH_BRIDGE_MIXED_PARENT_NECESSITY = FALSIFIED
```

## 4. Consequence for Gate A

The finite GT fact

```text
all 77 fresh non-tail births are mixed cycle x spanning
```

cannot follow from legality, connectedness, bridge freshness, or the non-tail
cut condition alone.

Any arbitrary-`n` proof that reachable GT non-root unshielded producers have a
directed-cycle parent must retain additional exact Policy-0A information, such
as:

```text
GT root-clause origin
frozen Resolution ancestry
pivot schedule
clause provenance
literal polarity
cache-key reachability
```

A proof which forgets this history and keeps only the abstract quotient clause
graph is incomplete.

## 5. Updated Gate-A decomposition

The remaining producer reachability obligation should be attacked through two
GT-specific exclusions:

### A1 — mixed-parent lineage reachability

```text
GT_NONROOT_UNSHIELDED_MIXED_PARENT_REACHABILITY_ARBITRARY_N = OPEN
```

Show that every reachable non-root immediate-local unshielded producer is safe
or has one directed-cycle parent and one component-spanning parent. Abstract
graph semantics alone cannot prove this.

### A2 — tree parent/result reachability

```text
GT_NONROOT_UNSHIELDED_TREE_PARENT_RESULT_REACHABILITY_ARBITRARY_N = OPEN
```

Given the mixed parent pair, show that the spanning parent is a simple K-normal
in-arborescence and the external resolvent is a simple tree, or else an existing
shield/safe route applies.

Once A1 and A2 hold, the already proved directed-cycle/tree theorem supplies
same-root exact one-edge exchange automatically.

## 6. Claim boundary

```text
ABSTRACT_MIXED_PARENT_NECESSITY = FALSIFIED
GT_MIXED_PARENT_REACHABILITY_ARBITRARY_N = OPEN
GT_TREE_PARENT_RESULT_REACHABILITY_ARBITRARY_N = OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N = OPEN
GLOBAL_CACHE_DAG_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```
