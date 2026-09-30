# C024 — Unshielded handoff localization

Status: **FINITE_ROUTE_COMPLETE / ARBITRARY_N_REACHABILITY_OPEN**  
Scope: immediate-local component-spanning non-tail bridge occurrences at the branch handoff of exact Policy-0A on `GT_n`.

## 1. Correct distinction

Two populations must not be conflated.

The first contains the 42 immediate-local lineages that later appear as non-tail bridge occurrences in a parent-eligible exact key through `GT_8`:

```text
later-surviving immediate-local lineages      42
already shielded before their branch          30
singleton/singleton before their branch       12
those twelve at root                          12
those twelve non-root                          0
```

The second contains **all** immediate-local unshielded occurrences present in a post-unit residual `P`, whether or not the same non-tail bridge later survives:

```text
all unshielded P-occurrences                  19
root                                          16
non-root                                       3
unsafe unshielded K' descendants               0
```

Thus non-root unshielded intermediate forms exist. What is absent is an admitted child exact key carrying the same lineage as an unsafe unshielded non-tail bridge.

## 2. Canonical shield

For a non-tail bridge

```text
l : a -> b,
```

the root non-minimality clause `N_a` supplies a canonical complementary shield whenever

```text
component(a) = {a}
and
|component(b)| >= 2.
```

Its residual contains `-l` plus a parallel quotient edge, so `-l` is component-spanning but non-bridge. This implication is already proved graph-theoretically and is independently replayed in every finite child classified as `CANONICALLY_SHIELDED`.

## 3. Complete finite P-to-K' fate census through GT_8

The nineteen unshielded P-occurrences generate thirty-eight branch-polarity transitions:

```text
CANONICALLY_SHIELDED      12
CLAUSE_EXTINCT            20
SPANNING_NONBRIDGE         2
TAIL_SINGLETON_SAFE        4
UNSAFE_UNSHIELDED          0
```

Selected relations at the parent stage:

```text
HEAD_TO_OTHER  12
TAIL_TO_OTHER   4
TAIL_HEAD       2
DISJOINT        1
```

Every accepted canonical shield is proof-carrying: the checker reconstructs the original `N_a`, reduces it under the child assignment, verifies membership in `K'`, checks the complementary literal, proves it is non-bridge, and emits an explicit parallel edge.

## 4. Root route

The full recursive trace through `GT_8` contains sixteen root unshielded P-occurrences. A separate exact root-only execution extends the same analysis through `GT_12` without exploring the recursive search tree.

Across `GT_4,...,GT_12`:

```text
root unshielded local occurrences            62
endpoint-touching selected branches          49
disjoint selected branches                   13
canonical-shield descendants                 40
unsafe child descendants                      0
disjoint unsafe descendants                   0
```

A disjoint branch is therefore not itself forbidden. In every observed disjoint case—already at `GT_4`, and again at `GT_11` and `GT_12`—both polarities make the bad pivot `SPANNING_NONBRIDGE`.

The correct root theorem target is:

### Root Endpoint-or-Shield-or-Destruction

Every root immediate-local unshielded occurrence must, under each deterministic branch polarity, become one of:

```text
terminal or extinct;
component-spanning non-bridge;
tail-singleton safe;
canonically N_a-shielded.
```

No arbitrary-`n` selector formula is assumed.

## 5. Non-root route

Exactly three non-root unshielded P-occurrences occur through `GT_8`. They are sibling clauses in one `GT_8` state at depth two:

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13)
```

For each bad pivot, the bridge cut has a two-node tail side. The selected literal `-8` is the unique clause edge internal to that tail wing.

```text
branch -8 satisfied  -> CLAUSE_EXTINCT
branch -8 falsified  -> tail wing contracted -> TAIL_SINGLETON_SAFE
```

The underlying **Two-Node Tail-Wing Handoff Lemma** is proved for arbitrary quotient graphs under these explicit hypotheses. What remains GT-specific is reachability:

### Non-Root Wing Reachability

Prove that every reachable non-root unshielded P-occurrence either is already disposed of by another safe route or has the two-node tail-wing template required by the proved lemma.

## 6. Why the frequency route is no longer primary

Quotient-component frequency factorization is false:

```text
nonuniform component-pair groups          1,133 / 1,851
nonuniform selected component pairs         463 / 604
```

The clause-history contribution profile is also heterogeneous. But route localization avoids needing one global frequency inequality:

```text
root:     direct endpoint/shield/destruction route;
non-root: proved tail-wing implication + GT reachability;
already shielded: canonical N_a argument.
```

History-sensitive frequency accounting remains a fallback diagnostic.

## 7. Remaining branch obligations

```text
PURE_BRANCH_ROUTE_CLASSIFICATION        PROVED
TWO_NODE_TAIL_WING_HANDOFF              PROVED
ROOT_ROUTE_THROUGH_GT_12                FINITE_CERTIFIED
ALL_BIRTH_HANDOFF_THROUGH_GT_8          FINITE_CERTIFIED
ROOT_ROUTE_ARBITRARY_N                   OPEN
NONROOT_WING_REACHABILITY_ARBITRARY_N   OPEN
```

Once the last two GT-specific reachability statements are proved, T2b closes and T3 becomes the direct temporal induction over

```text
K -> R -> P -> B -> K'.
```

## Falsification conditions

The route package is falsified by any reachable arbitrary-`n` occurrence with:

1. an admitted child retaining an unsafe unshielded non-tail bridge;
2. a claimed canonical shield whose root residual is absent or whose complement remains a bridge;
3. a non-root unshielded occurrence outside every proved safe route, including the two-node tail-wing template;
4. a root branch polarity outside extinction, non-bridge, tail-singleton, or canonical shield;
5. a lineage labelled extinct while still present in the exact child key.

## Claim boundary

The complete fate partition is mechanically certified for every unshielded P-occurrence through `GT_8`; the root route is extended exactly through `GT_12`; and the two-node tail-wing implication is proved for arbitrary quotient graphs. Root-route reachability for arbitrary `n`, non-root wing reachability for arbitrary `n`, completed T2b/T3, the global cache lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
