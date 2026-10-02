# R5 E9 — Acyclic grouped matching delta-matroid barrier

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_SIZE_REPRESENTATION_BARRIER__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS RULES OUT ORDINARY MATCHING REALIZATION OF EVERY CONNECTED ACYCLIC
EQ3/EXACT1 GROUPED BLOCK THAT CONTAINS AN EQ3 NODE.
IT DOES NOT RULE OUT CYCLIC GROUPED BLOCKS OR OTHER CARRIERS.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Factor-tree model

Let `T` be a finite connected acyclic factor graph. Every factor has arity three and is one of

```text
EQ3      = {000,111},
EXACT1_3 = {001,010,100}.
```

Internal incidences are edges of `T`. If a factor has internal degree `d`, its other `3-d` incidences are exposed as Boolean boundary ports. Let `R_T` be the exact projected relation on all boundary ports: a boundary tuple belongs to `R_T` iff it extends to a satisfying assignment of every factor in the tree.

The source application is any connected tree-shaped grouped region of the cubic Exact-One Levi factor graph. Such a region alternates EQ3 variable nodes and EXACT1 clause nodes, but the proof below only needs the stated local signatures and acyclicity.

## 2. Difference-forest lemma

Take two satisfying full incidence assignments `sigma,tau`. Mark every internal edge and every boundary half-edge on which they differ.

At a factor node:

- if an `EQ3` state changes, `000 <-> 111`, so all three incident bits differ and the node has difference-degree exactly `3`;
- if an `EXACT1_3` state changes, two distinct one-hot words differ in exactly two coordinates, so the node has difference-degree exactly `2`;
- if the local state does not change, its difference-degree is `0`.

Because the underlying factor graph is a tree, the nonempty difference object is a forest whose only degree-one vertices are changed boundary ports. Every internal changed factor has degree `2` or `3`.

For any connected component of this difference forest, let `L` be its number of boundary leaves and let `n3` be its number of changed EQ3 factors. The standard degree identity for a finite tree gives

```text
L = n3 + 2.
```

Therefore:

### Lemma AGMB-1

If two satisfying assignments differ at any EQ3 factor, their boundary tuples differ in at least three coordinates.

In particular, any feasible boundary-to-boundary move of Hamming distance at most two leaves the state of every EQ3 factor unchanged.

## 3. Boundary uniqueness on a factor tree

Suppose two satisfying full assignments have the same boundary tuple. Their difference forest would have `L=0` in every component. But every nonempty finite forest component has at least two leaves, while changed factor nodes have degree only `2` or `3` and there are no changed boundary leaves. Contradiction.

Hence:

### Lemma AGMB-2

Every feasible boundary tuple of `R_T` has a unique internal extension.

Thus the local state of each internal EQ3 factor is a well-defined function of the boundary tuple.

## 4. Both states of every EQ3 node extend

Fix any EQ3 factor `r` and prescribe its common incident value `s in {0,1}`. Root the factor tree at `r` and extend outward.

- At an EQ3 node whose parent incidence is fixed to `b`, set both remaining incidences to `b`.
- At an EXACT1 node whose parent incidence is `1`, set both remaining incidences to `0`.
- At an EXACT1 node whose parent incidence is `0`, set exactly one of the two remaining incidences to `1` and the other to `0`; if a remaining incidence is internal, recurse into that child, and if it is a boundary port simply set the boundary bit.

Because the graph is a finite tree, this recursively reaches boundary ports and produces a satisfying full assignment. No consistency cycle can arise.

Therefore:

### Lemma AGMB-3

For every EQ3 factor `r`, there exist feasible boundary tuples `X_0,X_1 in R_T` whose unique extensions put `r` in states `000` and `111`, respectively.

## 5. Delta-matroid exchange forces short-move connectivity

Let `F` be the family of feasible support sets of a delta-matroid. For any two feasible sets `X,Y` and any `e in X triangle Y`, the symmetric-exchange axiom supplies `f in X triangle Y` such that

```text
X' = X triangle {e,f}
```

is feasible (with the standard singleton interpretation when `e=f`). Since `e,f` are chosen from the current symmetric difference with `Y`, this move changes one or two coordinates and strictly reduces `|X triangle Y|`.

Iterating yields a sequence of feasible sets from `X` to `Y` in which every consecutive pair has Hamming distance at most two.

## 6. Main theorem

### Theorem AGMB-4 — no acyclic grouped matching realization

If `T` contains at least one EQ3 factor, then its exact boundary relation `R_T` is not a delta-matroid.

### Proof

Choose an EQ3 factor `r`. By AGMB-3 there are feasible boundary tuples `X_0,X_1` whose unique internal extensions give different states to `r`.

If `R_T` were a delta-matroid, Section 5 would give a feasible exchange sequence from `X_0` to `X_1` with every step changing at most two boundary bits. By AGMB-1, no such step can change the state of `r`. By AGMB-2 that state is determined by the boundary tuple, so it remains constant along the entire sequence, contradicting the different endpoint states.

Therefore `R_T` is not a delta-matroid. QED.

Matching-realizable Boolean boundary relations are even delta-matroids and hence delta-matroids. Consequently no such `R_T` can be realized by an ordinary perfect-matching gadget.

The single-node EQ3 block is included: its two feasible boundary tuples `000` and `111` already lie at distance three and violate symmetric exchange. A single EXACT1 node is deliberately excluded from the theorem; its one-hot relation is an even delta-matroid and is matching-realizable.

## 7. Consequence for the current grouped-matching route

This replaces finite small-block census evidence by an arbitrary-size theorem:

```text
CONNECTED ACYCLIC GROUPED REGION
+ CONTAINS SOURCE EQ3 CHOICE
=> NOT DELTA-MATROID
=> NOT ORDINARY MATCHING-REALIZABLE.
```

Therefore any future exact matching contraction that genuinely absorbs rank-3 source choices must use at least one of:

1. a grouped region containing a cycle;
2. a non-ordinary matching representation with additional globally proved structure;
3. a different polynomial carrier.

Do not reopen larger tree gadgets: increasing the tree size cannot cross the delta-matroid barrier.

This theorem does not solve the current 3-cut-irreducible/unbalanced residual and does not rule out cyclic grouped contractions.

## 8. Source boundary

The external implication

```text
matching-realizable relation => even delta-matroid
```

is source-bound to Kazda--Kolmogorov--Rolínek and the modern matching-realizable delta-matroid/general-factor literature. The arbitrary-size difference-forest obstruction AGMB-1--4 is the JANUS-derived part.

## 9. Checker

Executable regression:

`experiments/r5_e9_acyclic_grouped_matching_delta_matroid_barrier.py`

It enumerates exact boundary relations for deterministic alternating tree fixtures, verifies boundary-extension uniqueness, verifies the >=3 boundary-distance rule whenever an EQ3 state changes, and checks symmetric exchange failure directly.

## 10. Ceiling

```text
ACYCLIC EQ3/EXACT1 GROUPED BLOCK WITH EQ3
= NOT A DELTA-MATROID / PROVED FOR ARBITRARY SIZE

ORDINARY MATCHING REALIZATION OF SUCH A BLOCK
= IMPOSSIBLE

TREE-SIZE ESCALATION AS MATCHING ESCAPE
= CLOSED

CYCLIC GROUPED MATCHING CONTRACTION
= OPEN

3-CUT-IRREDUCIBLE UNBALANCED CORE
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
