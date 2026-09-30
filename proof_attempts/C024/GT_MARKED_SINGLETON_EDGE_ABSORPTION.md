# C024 — Marked singleton-edge absorption

Status: **PURE GRAPH/ENCODING LEMMA PROVED UNDER EXPLICIT MARKED-EXTENSION HYPOTHESES**  
Scope: one branch from a transient marked in-arborescence in `P` to the raw
child and then to the next exact key.

## 1. K-normal trees

A simple quotient in-arborescence is **K-normal** when its undirected tree is
one of:

```text
STAR
ONE_SUBDIVISION_STAR
```

Equivalently, with the root at the unique sink, its height is at most two and
there is at most one non-star edge.

## 2. Marked transient extension

Let `S` be a K-normal in-arborescence.  Choose one directed tree edge

```text
u -> v
```

and replace it by

```text
u -> w -> v,
```

where `w` is a new quotient component.  The resulting in-arborescence `T` is a
**one-step marked extension** of `S`.

Choose either new edge as the marked edge `e`.  Contracting `e` in `T` recovers
`S` up to the canonical relabeling which identifies the endpoints of `e`.

For the Policy-0A application, assume the two endpoint relation components of
`e` are singleton sets of original GT vertices.  Then there is exactly one GT
comparison variable between them, and the marked tree occurrence contains one
polarity of that variable.

## 3. Branch semantics

Let the marked literal be `l_e` and branch on its variable.

### Satisfying polarity

If the branch satisfies `l_e`, the whole clause is satisfied and disappears.

```text
MARKED_SAT_POLARITY = CLAUSE_EXTINCT
```

### Falsifying polarity

If the branch falsifies `l_e`, CNF restriction removes `l_e` from the clause.
The branch relation also identifies the two singleton endpoint components of
`e`.

On the external clause graph, this operation is exactly

```text
(T - e) / endpoints(e).
```

Because the endpoints are identified after the marked edge is removed, this is
canonically isomorphic to the ordinary tree contraction `T/e`.

By the definition of one-step marked extension,

```text
T/e is isomorphic to S.
```

Therefore the surviving external graph is K-normal.  Additional pre-unit
relations can only identify more vertices or make literals internal/extinct;
they cannot recreate the removed marked subdivision layer.

## 4. Theorem

### Marked Singleton-Edge Absorption

Let a legal Policy-0A clause have a simple quotient in-arborescence `T` which is
a one-step marked extension of a K-normal in-arborescence `S`.  Suppose the
marked edge occurrence is the selected comparison and its endpoint relation
components are singleton.  Then:

1. the satisfying branch polarity makes the clause extinct;
2. the falsifying polarity transports the clause to a graph isomorphic to
   `T/e`, hence to `S`, before any further child pre-unit simplification;
3. the next exact-key residual is extinct, non-tree, or K-normal;
4. no additional subdivision layer from this marked extension survives to the
   next exact key.

```text
MARKED_SINGLETON_EDGE_ABSORPTION_ARBITRARY_N = PROVED
```

The theorem is uniform in the number of original GT vertices.  It depends only
on the explicit marked-extension, selected-edge, singleton-endpoint, and legal
single-variable hypotheses.

## 5. What this does not prove

The theorem does not show that every reachable transient deep tree is a
one-step marked extension.  It also does not show that Policy-0A selects its
marked edge.  Those are separate reachability/selector obligations:

```text
K_TREE_NORMAL_FORM_ARBITRARY_N                      OPEN
ONE_EXCHANGE_MARKED_GROWTH_ARBITRARY_N              OPEN
EXPOSED_SUBDIVISION_SELECTOR_DOMINANCE_ARBITRARY_N  OPEN
```

The finite `GT_8` deep rows instantiate the theorem because each selected
literal `-8` joins singleton components, one polarity kills the clause, and the
other returns shape `(3,2,false)` to `(2,1,true)`.

## 6. Claim boundary

```text
PURE_MARKED_ABSORPTION = PROVED_UNDER_EXPLICIT_HYPOTHESES
ARBITRARY_N_REACHABILITY_OF_THE_HYPOTHESES = OPEN
NONROOT_SINGLETON_BRANCH_REACHABILITY_ARBITRARY_N = OPEN
GLOBAL_CACHE_DAG_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```
