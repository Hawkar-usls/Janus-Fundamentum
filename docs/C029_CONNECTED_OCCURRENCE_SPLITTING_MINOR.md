# C029 — Connected Occurrence-Splitting Minor Barrier

**Status:** `THEOREM-LEVEL STRUCTURAL LEMMA / P_VS_NP=OPEN`

## Target

C028 located `SEMANTIC_SUPPORT_OVERLAP`. A natural attempted shortcut is to replace every repeated variable occurrence by a fresh copy and connect all copies by a variable-local equality tree, hoping to reduce incidence width.

## Theorem

Let `F'` be obtained from a CNF `F` by replacing each occurrence of every variable `x` by a fresh copy, retaining each original clause node, and connecting all copies of `x` by a connected equality gadget that is vertex-disjoint from the gadgets of other variables. Then:

```text
inc(F) is a graph minor of inc(F').
```

Therefore, by minor monotonicity of treewidth,

```text
tw(inc(F)) <= tw(inc(F')).
```

## Proof

For each original variable `x`, use as its branch set all occurrence copies of `x` together with all nodes of the local equality gadget. This branch set is connected. For each original clause `C`, use the unchanged clause node as a singleton branch set. These branch sets are pairwise disjoint. Every original incidence edge `x--C` is witnessed by the edge from `C` to the occurrence copy of `x` used in `C`. Contract every variable branch set and delete surplus gadget edges. The original incidence graph is recovered.

## Machine audit

`experiments/direct/janus_c029_occurrence_splitting_minor.py` verifies explicit branch-set certificates on 600 deterministic random CNFs. It checks domain equality, branch-set disjointness and connectivity, and a target-edge witness for every source incidence edge. A disconnected equality-gadget control is rejected.

```bash
python experiments/direct/janus_c029_occurrence_splitting_minor.py --self-test
```

## Consequence

The following route is refuted:

```text
copy variables
+ connect copies by local equality constraints
=> universally smaller incidence/support-overlap width
```

Any universal low-width compiler must perform genuinely non-minor-preserving semantic compression rather than definitional occurrence splitting.

## Surviving route

The next candidate is a proof-carrying semantic quotient across a cut, with polynomial construction, exact SAT equivalence, witness recovery, independently checkable UNSAT handling, and polynomial boundary-message operations.

## Claim boundary

This blocks one broad compiler pattern. It does not exclude semantic elimination, algebraic compression, non-minor-preserving transformations, or prove `P!=NP`.
