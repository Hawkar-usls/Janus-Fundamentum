# C024 — Non-root transitivity tree-exchange lemma

Status: **PURE_GRAPH_LEMMA_PROVED / FINITE_GT_INSTANTIATION_CERTIFIED / PRODUCER_NORMAL_FORM_REACHABILITY_OPEN**  
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

## 4. Exact GT_4,...,GT_8 instantiation

The complete non-root provenance transcript has exactly three occurrences. All three are in one depth-two `GT_8` state and satisfy the same producer normal form:

```text
producing events                         3
root-transitivity + inherited-tree       3
DIRECTED_CYCLE + COMPONENT_SPANNING      3
HAS_DIRECTED_CYCLE + IN_ARBORESCENCE     3
one producing event per occurrence       3
pivot variable                           1 x3
unique maximum selected variable         8 x3
pivot-side quotient size                 2 x3
selected edge unique inside pivot-side   3
exchange cut equality                    3
unsafe children                          0
```

The three resolvents are

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13).
```

Each is obtained by replacing the tree edge represented by pivot `1` with the bad literal `11`, `12`, or `13` along a root transitivity triangle. The cut of the new bad bridge is exactly the former pivot cut. That pivot side consists of the two quotient nodes joined by selected literal `-8`.

## 5. Sharpened remaining gate

The vague non-root wing reachability obligation is reduced to the following producer theorem.

### Non-Root Producer Normal-Form Reachability

Prove for arbitrary `n` that every reachable non-root immediate-local unshielded bridge occurrence either is already safe, or its unique producing Resolution event has:

1. one root-transitivity directed-cycle parent;
2. one component-spanning in-arborescence parent;
3. the tree-exchange form of Section 1;
4. a pivot-side of exactly two quotient vertices;
5. the deterministic selected comparison as the unique internal edge of that side.

The pure graph implication after these hypotheses is now proved. What remains is GT-specific reachability and selector structure, not graph surgery.

A counterexample is a reachable non-root unshielded occurrence produced by a different parent family, by a wider pivot-dominated exchange, with a pivot-side of size at least three, or with the selected comparison outside that side.

## Mechanical certificate

```text
experiments/direct/janus_tear_gt_nonroot_transitivity_tree_exchange.py
.github/workflows/validate-c024-nonroot-tree-exchange.yml
```

## Claim boundary

The tree-exchange and cut-preservation lemma is proved for arbitrary finite graphs under its explicit hypotheses. The exact three non-root occurrences through `GT_8` instantiate those hypotheses. Arbitrary-`n` producer normal-form reachability, complete T2b/T3, the global cache-DAG lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
