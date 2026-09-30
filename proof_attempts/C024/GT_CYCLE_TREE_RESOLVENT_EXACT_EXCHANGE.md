# C024 — Directed-cycle/tree resolvent exact-exchange lemma

Status: **PURE QUOTIENT-GRAPH LEMMA PROVED UNDER EXPLICIT CYCLE/TREE/TREE-RESULT HYPOTHESES**  
Scope: the graph-surgery part of non-root unshielded producer reachability.

## 1. Setting

Fix a residual quotient and ignore internal loops. Let `D` be the simple external graph of one Resolution parent and assume `D` is an in-arborescence with root `r`.

Choose its pivot edge

```text
p = a -> b.
```

Let the other parent contain the complementary literal `b->a` and at least one directed cycle. Form the legal non-tautological resolvent by deleting `a->b` and `b->a`, taking the union of the remaining external directed edges, and collapsing duplicate copies of an identical directed quotient edge.

Call the resulting simple external digraph `R`. Assume the underlying undirected graph of `R` is a tree.

## 2. A directed cycle must use the pivot

Suppose the cycle parent contains a directed cycle which avoids `b->a`. Every edge of that cycle survives Resolution. Duplicate removal cannot destroy the cycle, and legality excludes cancellation by opposite edges. Then `R` contains a directed cycle, contradicting the assumption that its underlying graph is a tree.

Therefore every directed cycle in the cycle parent uses `b->a`. Choose one such simple cycle. Removing `b->a` from it leaves a directed path

```text
P : a = v_0 -> v_1 -> ... -> v_t = b.
```

## 3. Edge-count rigidity

Deleting `a->b` from the tree `D` gives a two-component forest

```text
F = D - {a->b}
```

with exactly `|V|-2` undirected edges. The tree `R` has exactly `|V|-1` undirected edges. Hence, among all external edges contributed by the cycle parent after pivot deletion, exactly one undirected edge can be new relative to `F`.

The path `P` connects `a` to `b`, which lie in different components of `F`, so at least one path edge crosses the pivot cut and is new. Therefore:

1. exactly one edge of `P` is new relative to `F`;
2. every other edge of `P` already occurs in `F`;
3. every additional external edge contributed by the cycle parent also already occurs in `F`.

Because the resolvent is legal, an edge whose undirected support already occurs in `F` must have the same orientation as the tree edge; the opposite orientation would form a complementary pair.

## 4. The unique new edge is the first path edge

In `F`, vertex `a` has no outgoing edge: its unique outgoing tree edge was the deleted pivot `a->b`.

The first path edge is

```text
a -> v_1.
```

It cannot already occur in `F`. Thus it is the unique new edge identified above.

Consequently it crosses the pivot cut immediately, so `v_1` lies in the root-side component of `F`. Every later path edge

```text
v_1 -> v_2 -> ... -> b
```

is an existing directed tree edge of `F`.

All other external edges from the cycle parent are duplicates of existing edges of `F`. After duplicate removal,

```text
R = (D - {a->b}) union {a->v_1}.
```

## 5. Root preservation

Every vertex other than `a` retains its unique outgoing tree edge. Vertex `a` replaces `a->b` by `a->v_1`, and the surviving path

```text
v_1 -> v_2 -> ... -> b -> ... -> r
```

is already contained in `D`.

Therefore `R` is an in-arborescence with the same root `r`.

## 6. Theorem

### Directed-Cycle/Tree Resolvent Exact Exchange

Let one legal Resolution parent have a simple external in-arborescence `D`, let the other parent contain a directed cycle and the complementary pivot, and suppose the simple external resolvent has an underlying tree. Then the resolvent is necessarily a same-root exact one-edge exchange:

```text
R = (D - {p}) union {l}
```

for one unique new external edge `l`.

```text
CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE_ARBITRARY_N = PROVED
```

The result is uniform in the number of quotient components and does not require the cycle parent to be a triangle or the tree parent to be K-normal.

## 7. Relation to the triangle theorem

For a transitivity triangle

```text
b->a, a->c, c->b,
```

the path after pivot deletion is `a->c->b`. Treehood forces `c->b` to be the existing sibling edge, recovering the previously proved triangle/tree exact-exchange lemma as the length-two special case.

## 8. Sharpened reachability gate

Exact exchange no longer needs to be proved directly from GT ancestry. The remaining producer obligation is only:

```text
NONROOT_UNSHIELDED_CYCLE_TREE_TREE_RESULT_REACHABILITY_ARBITRARY_N = OPEN
```

Every arbitrary-`n` reachable non-root immediate-local unshielded producer must be shown either safe or to have:

1. one directed-cycle parent carrying the complementary pivot;
2. one simple in-arborescence parent;
3. a simple tree resolvent.

Under those three hypotheses, exact same-root one-edge exchange follows from this theorem.

## 9. Claim boundary

```text
PURE_CYCLE_TREE_EXACT_EXCHANGE = PROVED_UNDER_EXPLICIT_HYPOTHESES
ARBITRARY_N_REACHABILITY_OF_CYCLE_TREE_TREE_RESULT = OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N = OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = OPEN
GLOBAL_CACHE_DAG_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```
