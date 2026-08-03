# C024 — K-normal one-edge exchange growth

Status: **PURE ROOTED-TREE LEMMA PROVED UNDER EXACT ONE-EDGE EXCHANGE HYPOTHESES**  
Scope: the graph-shape part of the remaining non-root exact-key induction.

## 1. Definitions

Let `D` be a finite simple in-arborescence with sink/root `r`.

An edge is **non-star** when its head is not `r`.  A root-directed path of
length `h` contains exactly `h-1` non-star edges.

`D` is **K-normal** when

```text
height(D) <= 2
and
nonstar(D) <= 1.
```

Thus `D` is a star or a one-subdivision star.

An **exact one-edge exchange** is

```text
Q = (D - p) + l,
```

where `p` is an edge of `D`, `l` is not an edge of `D-p`, and `Q` is again a
simple in-arborescence with the same root `r`.

## 2. Non-star bound

Deleting `p` cannot increase the number of non-star edges.  Adding `l` adds at
most one non-star edge.  Therefore

```text
nonstar(Q) <= nonstar(D) + 1 <= 2.
```

## 3. Height bound

Every root-directed path of length `h` in an in-arborescence has `h-1`
non-star edges.  Since `Q` contains at most two non-star edges,

```text
height(Q) - 1 <= 2,
```

and hence

```text
height(Q) <= 3.
```

Thus a single exact exchange from K-normal form cannot create arbitrary depth.

## 4. Marked-extension recovery

If `Q` is K-normal, no transient marked layer is needed.

Suppose `Q` is not K-normal.  The bounds above force

```text
nonstar(Q) = 2.
```

Choose any non-star edge `e` of `Q` and contract it.  Tree contraction preserves
connectedness and acyclicity.  The contracted rooted tree `Q/e` has at most one
non-star edge.  Its height is at most two because every root-directed path in
`Q/e` contains at most one non-star edge.

Therefore

```text
Q/e is K-normal.
```

Equivalently, `Q` is a one-step marked extension of the K-normal tree `Q/e`,
with `e` as a valid marked edge.

## 5. Theorem

### K-normal One-Edge Exchange Growth

Let `D` be a K-normal finite simple in-arborescence rooted at `r`, and let
`Q=(D-p)+l` be an exact one-edge exchange which is again a simple
in-arborescence rooted at `r`.  Then:

1. `nonstar(Q) <= 2`;
2. `height(Q) <= 3`;
3. either `Q` is K-normal, or every non-star edge of `Q` is a valid marked edge
   whose contraction gives a K-normal tree.

```text
K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH_ARBITRARY_N = PROVED
```

The theorem is independent of the number of GT vertices.

## 6. Policy-0A boundary

This theorem proves only the graph consequence of an exact one-edge exchange.
It does not prove that every reachable non-root dangerous Resolution event:

- has a K-normal exact-key tree parent;
- is an exact one-edge exchange rather than a larger external-edge update;
- exposes a marked edge between singleton relation components;
- causes Policy-0A to select such a marked edge.

Those remaining obligations are now separated as

```text
K_TREE_NORMAL_FORM_ARBITRARY_N                         OPEN
NONROOT_EXACT_EXCHANGE_REACHABILITY_ARBITRARY_N        OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N     OPEN
```

Together with the separately proved Marked Singleton-Edge Absorption theorem,
this lemma prevents accumulation of tree depth once the reachability and
selector hypotheses are supplied.

## 7. Claim boundary

```text
PURE_ONE_EDGE_GROWTH = PROVED_UNDER_EXPLICIT_HYPOTHESES
REACHABILITY_OF_EXACT_EXCHANGE_HYPOTHESES = OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = OPEN
GLOBAL_CACHE_DAG_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```
