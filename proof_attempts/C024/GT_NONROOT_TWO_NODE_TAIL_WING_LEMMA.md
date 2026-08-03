# C024 — Two-node tail-wing handoff lemma

Status: **PURE_GRAPH_LEMMA_PROVED / GT_REACHABILITY_OPEN**  
Scope: a single clause/literal lineage at the branch handoff from a post-result `P` to a child exact-key boundary `K'`.

## 1. Setup

Let `C` be a component-spanning clause over the current relation quotient. Let

```text
l : A -> B
```

be a bridge edge of the undirected clause graph. Deleting `l` separates the graph into a tail side `S` containing `A` and a head side `T` containing `B`.

Assume:

1. `S = {A,X}` has exactly two quotient nodes;
2. the selected branch variable has clause literal `f` whose external edge joins `A` and `X`;
3. `f` is the unique clause edge internal to `S`;
4. the branch operation assigns the comparison underlying `f`, so its endpoints `A,X` are contracted in the relation quotient;
5. the clause is handled by ordinary restriction: the polarity satisfying `f` deletes `C`, while the opposite polarity deletes literal `f` from `C`.

No assumption is made about the size or internal structure of `T`.

## 2. Lemma

### Two-Node Tail-Wing Handoff

Under assumptions 1–5, the two branch polarities have exactly the following safe outcomes:

```text
polarity satisfying f:
    C is satisfied and disappears;

polarity falsifying f:
    f is removed from C;
    A and X are contracted to one quotient node AX;
    l remains the only edge crossing from AX to T;
    deleting l isolates AX;
    l is therefore TAIL_SINGLETON safe.
```

Thus the original non-tail bridge lineage cannot enter the child exact key as an unshielded non-tail bridge.

## 3. Proof

Because `l` is a bridge, no clause edge other than `l` crosses the cut `(S,T)`. Because `S={A,X}` and `f` is the unique internal edge of `S`, the subgraph induced by `S` consists exactly of edge `f`.

On the satisfying branch, CNF restriction removes the whole clause. The lineage is extinct.

On the falsifying branch, restriction removes `f` from the clause while the assigned comparison contracts `A` and `X` in the relation quotient. After contraction, all of `S` is represented by the single quotient node `AX`. No edge other than `l` joins `AX` to `T`, since any such edge before contraction would have crossed the original bridge cut and contradicted bridgehood of `l`.

Therefore `l` is a bridge whose deletion isolates exactly the tail quotient node `AX`. This is the `TAIL_SINGLETON` role. Complementary tail-singleton bridges isolate opposite endpoint nodes and induce different cuts, so this lineage is outside the unsafe same-cut route.

The proof is purely graph-theoretic plus standard CNF restriction semantics. It does not depend on the GT encoding, clause width, cache, novelty level, or frequency selector.

```text
TWO_NODE_TAIL_WING_HANDOFF = PROVED
```

## 4. Exact Policy-0A realization through GT_8

The complete pre-frontier handoff census finds exactly three non-root unshielded post-result occurrences:

```text
non-root unshielded P-occurrences             3
orders containing them                        GT_8 only
unique parent state                           1
parent depth                                  2
selected relation                             TAIL_TO_OTHER x3
```

All three satisfy every lemma hypothesis:

```text
tail bridge side has two quotient nodes       3
selected edge lies inside tail side           3
selected literal is present in clause         3
selected edge is unique tail-internal edge     3
satisfying polarity -> CLAUSE_EXTINCT          3
falsifying polarity -> TAIL_SINGLETON_SAFE     3
unsafe child descendant                        0
```

The clauses are the three sibling templates

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13)
```

in the same `GT_8` state. The selected variable is `8`, joining the bad tail component to the second node of its two-node wing.

## 5. Remaining GT-specific theorem

### Non-Root Wing Reachability

Prove for arbitrary `n`:

> Every non-root immediate-local component-spanning clause occurrence that reaches `P` with an unshielded non-tail bridge and singleton endpoint components either already has a safe branch fate, or satisfies the two-node tail-wing hypotheses above for the deterministic selected comparison.

Equivalent falsifiers include:

1. a non-root unshielded occurrence with a tail bridge side of size at least three;
2. a selected comparison outside the tail wing which leaves the bad bridge unshielded;
3. more than one internal clause edge in the tail wing;
4. a selected variable absent from the source clause;
5. an admitted child retaining the same non-tail bridge without a canonical root shield.

The finite all-birth census searches for all five through `GT_8` and finds none.

## 6. Relation to T2b

The branch handoff is now split into:

```text
root unshielded occurrences:
    endpoint / canonical shield / bridge destruction / extinction;

non-root unshielded occurrences:
    two-node tail-wing handoff;

already shielded occurrences:
    canonical N_a shield is preserved or redundant safety applies.
```

Proving Non-Root Wing Reachability and the corresponding root route theorem would close the remaining GT-specific branch handoff obligation. T3 would then be the direct temporal induction over `K -> R -> P -> B -> K'`.

## Claim boundary

The two-node tail-wing handoff lemma is proved for arbitrary quotient graphs under its explicit hypotheses. Its realization is exhaustively certified for all three non-root unshielded P-occurrences through `GT_8`. The arbitrary-`n` GT reachability theorem, completed T2b/T3, global cache-frontier transfer, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
