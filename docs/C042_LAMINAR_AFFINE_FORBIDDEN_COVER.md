# C042 — Laminar Affine Forbidden-Subspace Cover

```text
P_VS_NP=OPEN
```

## Exact coordinate object

After an affine parameterization

```text
x_i = p_i XOR <b_i, lambda>,
```

the falsifying set of one CNF clause is the solution set of one affine system over `lambda`: every literal is required to be false simultaneously. Thus each clause defines either an empty forbidden set or an affine subspace `U_C` of `GF(2)^d`.

The coordinate formula is satisfiable exactly when

```text
GF(2)^d \ union_C U_C
```

is nonempty.

## Constructive theorem

Assume the nonempty forbidden subspaces form a laminar family: for every pair `U,V`, either

```text
U intersect V = empty,
U subseteq V,
or V subseteq U.
```

This property is discovered, not supplied. Pairwise intersection and inclusion are decided by provenance-compatible Gaussian elimination.

Delete duplicate and nonmaximal subspaces. Laminarity implies that the remaining maximal members are pairwise disjoint. Hence their union size is exactly

```text
sum_i 2^dim(U_i).
```

- If the sum is `2^d`, the maximal members form a disjoint affine cover and certify UNSAT.
- Otherwise a SAT coordinate is constructed bit by bit. At each prefix, intersect every maximal subspace with each candidate prefix cell, count the disjoint covered points exactly by rank, and choose a child whose covered count is smaller than its cell size.

All construction, recognition, counting, witness recovery and replay cost is polynomial in the coordinate dimension, number of clauses and emitted trace volume. No assignment enumeration, SAT oracle or formula-equivalence oracle is used.

## Proof objects

The certificate records:

- canonical RREF for every clause-falsifying affine system;
- every pair relation (`DISJOINT`, `SUBSET`, or strict rejection as `CROSSING`);
- maximal forbidden-subspace identifiers and exact cardinalities;
- for UNSAT, a disjoint-cover cardinality equality;
- for SAT, conditional-counting choices and the final uncovered coordinate.

Crossing arrangements return `OPEN_NON_LAMINAR`. Explicit work exhaustion returns `OPEN_BUDGET`.

## Frozen controls

```bash
python experiments/direct/janus_c042_laminar_affine_forbidden_cover.py --self-test
```

The deterministic audit includes:

```text
180 random laminar coordinate instances checked exhaustively on d <= 8
64-dimensional SAT without enumerating 2^64 coordinates
64-dimensional UNSAT from two disjoint halfspaces
32 nested factors compressed to one maximal forbidden subspace
crossing-subspace control -> OPEN_NON_LAMINAR
24-variable NAND3+NEQ coordinate image -> OPEN_NON_LAMINAR
corrupt digest detection
```

## Literature alignment

Counting points on and off unions of affine subspaces is classical subspace-arrangement theory and can be expressed through intersection-poset methods. C042 uses the elementary laminar specialization, where the intersection structure collapses to containment plus disjointness and exact counting needs no exponential inclusion-exclusion. This is an alignment and constructive proof package, not a new general arrangement invariant.

## Decisive boundary

C041 showed that affine coordinates reproduce arbitrary source 3-CNF on the C023 hard image. C042 adds a genuine tractable certificate, but the hard image contains crossing forbidden subspaces and is rejected.

The surviving gate is:

```text
POLYNOMIAL_DECOMPOSITION_OF_CROSSING_AFFINE_FORBIDDEN_SUBSPACES
```

A next route must discover a broader arrangement decomposition or symbolic cover with polynomial join, projection, counting, SAT witness and UNSAT evidence. Failure remains `OPEN`.
