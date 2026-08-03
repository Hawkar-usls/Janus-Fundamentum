# C024 — Non-root transitivity tree-exchange lemma

Status: **PURE_GRAPH_LEMMA_PROVED / COMPLETE_FINITE_EXCHANGE_CENSUS_GREEN / ARBITRARY_N_REACHABILITY_OPEN**  
Scope: the producer step of a non-root unshielded bridge before the already proved two-node tail-wing handoff.

## 1. Tree-exchange setup

Let `D` be a tree on the current quotient vertices. Let

```text
p = {a,r}
s = {r,b}
```

be distinct edges of `D`, and let `l={a,b}` be the third edge of the triangle on `a,r,b`. Define

```text
Q = (D - p) + l.
```

This is the undirected graph operation induced when a root transitivity clause containing `p,s,l` is resolved against a component-spanning tree clause containing the complementary pivot `-p` and the common edge `s`.

## 2. Lemma — cut preservation under transitivity exchange

### Transitivity Tree-Exchange Lemma

Under the setup above:

1. `Q` is a tree;
2. `l` is a bridge of `Q`;
3. deleting `l` from `Q` produces exactly the same vertex bipartition as deleting `p` from `D`.

### Proof

Deleting the tree edge `p` splits `D` into two connected components. The vertex `a` is in one component. Because `s={r,b}` remains in `D-p`, both `r` and `b` are in the other component. Therefore `l={a,b}` joins the two components of `D-p` by one edge. Hence `Q` is connected with the same number of edges as a tree, so it is a tree. Its new edge `l` is the unique edge joining those two components, and its deletion restores `D-p`. Thus the `l`-cut in `Q` equals the `p`-cut in `D`. ∎

## 3. Two-node corollary

Assume additionally that the side of the `p`-cut containing `a` is exactly

```text
{a,x}
```

and that `f={a,x}` is its unique internal tree edge. Then the same side is the tail side of the new bridge `l` in `Q`. If deterministic branching selects the comparison underlying `f`, the already proved Two-Node Tail-Wing Handoff applies:

```text
satisfying polarity -> clause extinct
falsifying polarity -> contract {a,x} -> l becomes TAIL_SINGLETON_SAFE
```

Therefore the producer and handoff obligations separate cleanly:

```text
producer normal form
+ two-node pivot-side
+ selected internal edge
=> safe child handoff.
```

## 4. Complete finite exchange census

The broad checker enumerates every non-root frozen Resolution event through `GT_8` having one component-spanning in-arborescence parent and one directed-cycle parent.

```text
candidate cycle x arborescence events       121
simple arborescence parents                 121
exact one-edge tree exchanges                17
new unshielded bridges                        3
```

The background class is genuinely broader:

```text
star arborescences: height 1, nonstar 0       81
one-subdivision stars: height 2, nonstar 1    40
pivot-side sizes observed:
  (1,2), (1,3), (1,4), (1,5), (1,6),
  (2,2), (2,3), (2,4)
selected relation:
  CROSS_CUT                                  25
  INTERNAL_PIVOT_SIDE                       89
  PIVOT                                       7
```

Thus two-node safety is not built into the census. Wider pivot sides and other selected relations really occur.

### Exact localization of all unshielded outputs

All three and only the three unshielded new bridges lie in one cell:

```text
order size                                  GT_8
state / call                                615 / 1182
tree shape                                  height 2
non-star edges                              1
one-subdivision star                        true
pivot-cut side sizes                        (2,4)
cycle parent                                ROOT_TRANSITIVITY
exact one-edge exchange                     true
selected relation                           INTERNAL_PIVOT_SIDE
selected edge                               unique edge of the two-node side
```

Their resolvents are

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13).
```

For each event, the new bad bridge cut equals the former pivot-edge cut. The two-node side is joined internally by selected literal `-8`. The already proved handoff then gives one extinct child and one tail-singleton-safe child.

## 5. Exact recursive ancestry classification

The first ancestry candidate failed because its structural matcher was stronger than its reconstructed proof object. It was not admitted. The replacement classifier enumerates every exact root proof path instead of selecting a convenient path.

For all three finite occurrences it finds:

```text
proof paths per occurrence                  1
minimum local Resolution count              1
minimum path kind                           LOCAL_RESOLUTION
minimum root-label signature                ROOT_NON_MINIMALITY
                                             + ROOT_TRANSITIVITY
one-subdivision path exists                 3 / 3
one-subdivision path is minimum             3 / 3
one-subdivision path is unique              3 / 3
```

The inherited tree parent is therefore not merely compatible with a one-subdivision explanation in the finite trace: it has exactly one reconstructed root ancestry, consisting of one `N/T` Resolution followed only by post-unit reduction, branch restriction and pre-unit reduction.

This remains a finite ancestry certificate. It is not promoted to arbitrary `n`.

## 6. Sharpened remaining gate

The former vague obligation

```text
NONROOT_WING_REACHABILITY_ARBITRARY_N
```

is now reduced to the following exact producer theorem.

### Non-Root One-Subdivision Exchange Reachability

Prove for arbitrary `n` that every reachable non-root immediate-local unshielded bridge occurrence either is already safe, or satisfies all of:

1. its tree parent has a unique root ancestry from one non-minimality/transitivity Resolution;
2. subsequent lineage steps only restrict leaves and do not add another local Resolution;
3. the resulting arborescence is a one-subdivision star;
4. the producing event resolves a root-transitivity cycle against its center edge;
5. the exchange pivot has a two-quotient-node side;
6. the deterministic selected comparison is the unique internal edge of that side.

Once these hypotheses hold, the graph surgery and child handoff are already proved. What remains is GT-specific arbitrary-`n` reachability and selector structure, not cut preservation.

A decisive counterexample is a reachable non-root unshielded occurrence with a different ancestry signature, a tree of height at least three, two or more non-star edges, a pivot side of size at least three on the tracked side, or a selected comparison outside that side.

## Mechanical certificates

```text
experiments/direct/janus_tear_gt_nonroot_transitivity_tree_exchange.py
experiments/direct/janus_tear_gt_nonroot_wing_recursive_ancestry.py
experiments/direct/janus_tear_gt_nonroot_arborescence_exchange_census.py
.github/workflows/validate-c024-nonroot-tree-exchange.yml
.github/workflows/validate-c024-nonroot-wing-recursive-ancestry.yml
.github/workflows/validate-c024-nonroot-arborescence-exchange-census.yml
```

## Claim boundary

The tree-exchange and cut-preservation lemma is proved for arbitrary finite graphs under its explicit hypotheses. The complete `GT_4,...,GT_8` exchange census and exact ancestry replay isolate all finite unshielded events in the one-subdivision/two-node cell. Arbitrary-`n` one-subdivision exchange reachability, complete T2b/T3, the global cache-DAG lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
