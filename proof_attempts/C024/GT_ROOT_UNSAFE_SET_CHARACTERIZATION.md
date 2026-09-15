# C024 — Root unsafe-set characterization

Status: **CONDITIONAL GRAPH CHARACTERIZATION PROVED / GT ROOT TEMPLATE REACHABILITY FINITE-CERTIFIED**  
Scope: one root post-result clause/literal occurrence before child unit propagation.

## 1. Root occurrence template

Let `C` be a component-spanning clause over the current relation quotient and let

```text
l : A -> B
```

be a non-tail bridge whose endpoint components `A` and `B` are singleton. Let deleting `l` split the clause graph into bridge sides `S` and `T`, with `A in S` and `B in T`.

The exact root unsafe family through `GT_12` has the shape

```text
|S| = 2,
|T| = n-2.
```

Let `H = T \ {B}`. Thus `|H|=n-3`.

For a comparison variable `u`, call its quotient edge **head-disjoint internal** when both endpoints lie in `H`. Call it **clause-absent** when neither polarity of `u` occurs in `C`.

Define

```text
B(C,l) = {u : u is head-disjoint internal and clause-absent}.
```

Then

```text
|B(C,l)| = C(n-3,2)
```

whenever every pair of distinct quotient vertices in `H` is represented by an unassigned comparison variable.

## 2. Unsafe preservation implication

### Lemma 2.1 — Absent head-disjoint contraction preserves the bad bridge

Assume `u in B(C,l)` and branch on `u`.

Because `u` is absent from `C`, neither polarity satisfies `C` and neither polarity deletes a literal from `C`. The clause support is unchanged.

Because both endpoints of `u` lie in `H subset T`, relation contraction occurs strictly inside the head bridge side. It does not cross the bridge cut, does not identify `A` with any vertex of `T`, and does not merge the distinguished head endpoint component `B`.

Therefore:

1. `l` remains present in the residual clause;
2. deleting `l` still separates the contracted image of `S` from the contracted image of `T`;
3. the endpoint components of `l` remain singleton `A` and singleton `B`;
4. no canonical `N_A` shield is activated, because `B` is not merged with another quotient component.

Before any additional child unit assignments, the tracked lineage remains an unshielded non-tail bridge under both branch polarities.

```text
ABSENT_HEAD_DISJOINT_CONTRACTION_IS_UNSAFE = PROVED
```

This is a pure quotient-graph/CNF-restriction statement.

## 3. Safe complement under the certified root templates

For the exact root template family, every variable outside `B(C,l)` falls into one of the already proved safe implications when selected:

```text
PIVOT:
    tracked literal assigned -> lineage extinct;

CROSS_CUT:
    contraction crosses the bridge cut -> l becomes non-bridge;

HEAD_INCIDENT_INTERNAL:
    selected clause literal merges B inside T -> clause extinction or canonical N_A shield;

TWO_NODE_TAIL_INTERNAL:
    selected clause literal is the unique edge inside S -> clause extinction or tail-singleton safety.
```

Under these support hypotheses, no fifth unsafe branch geometry remains.

## 4. Exact semantic equality through GT_12

The exhaustive two-polarity child replay mechanically compares the true unsafe set `U(C,l)` with `B(C,l)` for every root unshielded occurrence through `GT_12`:

```text
root occurrences checked                 62
U = B                                    62
U proper subset of B                      0
B proper subset of U                      0
incomparable                               0
```

The unsafe-set sizes are exactly

```text
C(n-3,2)
```

for every nonvacuous order:

```text
n=5..12: 1,3,6,10,15,21,28,36.
```

The four `GT_4` occurrences have `H` of size one and therefore `B=U=empty`.

## 5. Child-unit boundary

Lemma 2.1 describes the raw branch child `B`. In general, later child unit propagation could remove, contract, or terminate the lineage. Therefore the equality

```text
U(C,l) = B(C,l)
```

for admitted exact children includes an additional GT/Policy-0A reachability fact: on the certified root family, child units do not rescue any member of `B(C,l)` before exact-key admission, and do not create any unsafe variable outside it.

This boundary is independently replayed in the all-variable audit. The graph implication alone must not be overstated as a universal statement about arbitrary CNFs with arbitrary child unit consequences.

## 6. Root selector theorem after characterization

Since the exact unsafe alternatives are geometrically explicit, the root selector obligation becomes:

### Frozen Unsafe-Surplus Separation

For every root unshielded occurrence `(C,l)` and every

```text
u in B(C,l),
```

prove

```text
fresh_surplus(selected) > fresh_surplus(u).
```

The symmetric root baseline `2(n-1)` cancels. Minimum-index tie-breaking is not needed against unsafe alternatives on the certified frontier.

The structural class `B(C,l)` remains strictly below the selected frequency on 249 exact root occurrences through `GT_18`.

## 7. Falsification conditions

The characterization route is falsified by any reachable arbitrary-`n` root occurrence with:

1. an unsafe variable outside `B(C,l)`;
2. a variable in `B(C,l)` rescued before exact-key admission by child units;
3. a root bad bridge cut outside the certified two-versus-`n-2` template and outside every separately proved safe route;
4. a selected variable outside PIVOT, CROSS_CUT, HEAD_INCIDENT_INTERNAL, or TWO_NODE_TAIL_INTERNAL;
5. an unsafe member of `B(C,l)` tying or exceeding the selected fresh surplus.

## Claim boundary

The absent head-disjoint contraction implication is proved for arbitrary quotient graphs under its explicit hypotheses. Exact semantic equality `U=B` is certified through `GT_12`, and strict structural frequency separation is extended through `GT_18`. Frozen unsafe-surplus separation for arbitrary `n`, child-unit preservation of the characterization for arbitrary `n`, Non-Root Wing Reachability, T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
