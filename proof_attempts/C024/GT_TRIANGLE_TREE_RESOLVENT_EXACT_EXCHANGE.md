# C024 — Triangle/tree resolvent exact-exchange lemma

Status: **PURE ROOTED-GRAPH LEMMA PROVED UNDER EXPLICIT TRIANGLE/TREE HYPOTHESES**  
Scope: the graph-surgery part of non-root unshielded producer reachability.

## 1. Setting

Let `D` be a finite simple in-arborescence with root `r`. Choose a tree edge

```text
p = a -> b.
```

Let the other Resolution parent contain the directed transitivity triangle

```text
b -> a,
a -> c,
c -> b,
```

where `a,b,c` are distinct. Resolve the complementary pair `a->b / b->a`.
Ignoring internal loops and duplicate copies of an identical directed edge, the external resolvent graph is

```text
R = (D - {a->b}) union {a->c, c->b}.
```

Assume the resolvent is legal: it contains no pair of opposite directed edges.

## 2. Pivot cut

Deleting `a->b` from `D` separates the undirected tree into two components:

```text
A = the subtree rooted at a,
B = the component containing b and r.
```

The two residual triangle edges form an `a`-to-`b` path through `c`. Exactly one of them crosses the cut `A | B`; the other lies inside one side.

## 3. The third vertex cannot lie in A when R is a tree

Suppose `c in A`. Then `c->b` crosses the pivot cut and is necessarily new. The other residual edge is `a->c`, internal to `A`.

But `a->c` cannot already be an edge of `D`: in the in-arborescence `D`, vertex `a` already has its unique outgoing edge `a->b`. Therefore both residual triangle edges are new relative to `D-{a->b}`.

The forest `D-{a->b}` has `|V|-2` edges. Adding two new edges yields `|V|`? More precisely, it yields `(|V|-2)+2=|V|` directed occurrences and `|V|`? For a simple graph on `|V|` vertices a tree has `|V|-1` edges, so the result has one edge too many. Since the cross edge reconnects the two forest components, the additional internal edge creates an undirected cycle. Hence `R` is not a tree.

Therefore, if the underlying graph of `R` is a tree,

```text
c in B.
```

## 4. The internal triangle edge must already be the sibling edge

Now `a->c` crosses `A | B`, so it is new and reconnects the two components. The second residual edge `c->b` lies inside the tree component `B`.

If `c->b` were not already an edge of `D-{a->b}`, adding it to the tree component `B` would create an undirected cycle inside `B`. Therefore treehood of `R` forces

```text
c->b in D.
```

Thus `a` and `c` are siblings in `D`, both pointing to the common parent `b`.

Duplicate removal deletes the repeated occurrence of `c->b`, and the resolvent edge set becomes exactly

```text
R = (D - {a->b}) union {a->c}.
```

This is an exact one-edge exchange.

## 5. Root and orientation

Every vertex other than `a` retains its unique outgoing tree edge. Vertex `a` replaces `a->b` by `a->c`, and `c->b` remains in the tree. Therefore the new root-directed path from `a` is

```text
a -> c -> b -> ... -> r.
```

The resolvent is a simple in-arborescence with the same root `r`.

## 6. Theorem

### Triangle/Tree Resolvent Exact Exchange

Under the setting above, if the underlying external graph of the legal resolvent `R` is a tree, then necessarily

```text
c->b in D,
```

and

```text
R = (D - {a->b}) union {a->c}.
```

Consequently `R` is a same-root exact one-edge exchange and the triangle redirects one sibling edge through the other sibling.

```text
TRIANGLE_TREE_RESOLVENT_EXACT_EXCHANGE_ARBITRARY_N = PROVED
```

The theorem is uniform in the number of vertices and does not require K-normality of `D`.

## 7. Reachability boundary

This theorem does not prove that every arbitrary-`n` reachable non-root immediate-local unshielded producer has:

- a directed triangle parent of the stated orientation;
- a simple in-arborescence parent;
- a tree resolvent.

Those are the remaining GT-specific reachability obligations. Once supplied, exact exchange and common-root preservation follow automatically from this lemma.

The exact-exchange gate may therefore be sharpened to:

```text
NONROOT_UNSHIELDED_TRIANGLE_TREE_REACHABILITY_ARBITRARY_N = OPEN
```

## 8. Claim boundary

```text
PURE_TRIANGLE_TREE_EXCHANGE = PROVED_UNDER_EXPLICIT_HYPOTHESES
ARBITRARY_N_REACHABILITY_OF_THE_HYPOTHESES = OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N = OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = OPEN
GLOBAL_CACHE_DAG_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```
