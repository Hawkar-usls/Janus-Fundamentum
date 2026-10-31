# R5 E10A — Zero-Sum Cycle Compression for Labelled T-Joins

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_STRUCTURE_AFTER_AUDIT__NO_DETERMINISTIC_SOLVER_CLAIM`

Authorizing audit:
`PA-0005-TWO-ROW-GRAPH-LIFT`

Continuation of:
`NM-0003-XLC-BIPARTITE-EXACT-MATCHING-TRANSFER`

Parent scope:
`R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1`

Checker:
`experiments/r5_e10a_gf2_squared_zero_sum_cycle_compression.py`

## 1. Purpose

The exact transfer to Bipartite Exact Matching is sealed, but the current
external deterministic candidate is quarantined because its own Appendix A
describes only a partial Lean formalization with eight remaining top-level
hypotheses.

This artifact therefore pursues a deterministic **bypass** inside the original
two-row graph-lift object.

It proves that an optimum labelled T-join never needs an unbounded number of
independent label-correction cycles.

## 2. Setting

Let `G=(V,E)` be an undirected graph with nonnegative edge weights and an
edge labelling

```
lambda : E -> Gamma
```

into a finite abelian group `Gamma`.

Fix two terminals `u,v` and target label `g`.

A feasible labelled T-join is an edge set `J` with

```
boundary(J) = {u,v}
sum_{e in J} lambda(e) = g.
```

For the current JANUS gate,

```
Gamma = GF(2)^2.
```

## 3. Decomposition lemma

Choose, among all minimum-weight feasible labelled T-joins, one with the
minimum number of edges.

Because the odd-degree set of `J` is exactly `{u,v}`, its edges can be
partitioned into

```
J = P dot-union C_1 dot-union ... dot-union C_q
```

where:

- `P` is a simple `u-v` path;
- each `C_i` is a simple cycle;
- all pieces are pairwise edge-disjoint.

The cycles may meet the path or each other at vertices; only edge-disjointness
is asserted and needed.

Define

```
gamma_i = sum_{e in C_i} lambda(e) in Gamma.
```

### Theorem — zero-sum-free correction sequence

The sequence

```
gamma_1,...,gamma_q
```

is zero-sum-free: no nonempty subcollection sums to zero.

### Proof

Suppose a nonempty index set `I` satisfies

```
sum_{i in I} gamma_i = 0.
```

Delete the cycles `C_i`, `i in I`, from `J`.

Every cycle has empty odd-degree boundary, so the new edge set still has
boundary `{u,v}`.

The deleted cycle labels sum to zero, so the total group label remains `g`.

All edge weights are nonnegative, hence total weight cannot increase.

If it decreases, `J` was not minimum weight.
If it stays equal, at least one edge was deleted, contradicting the tie-break
choice of minimum cardinality.

Contradiction.

Therefore the correction-cycle labels are zero-sum-free.

## 4. Davenport bound

Let `D(Gamma)` denote the Davenport constant: the least integer such that
every sequence of `D(Gamma)` group elements has a nonempty zero-sum
subsequence.

The theorem immediately gives

```
q <= D(Gamma)-1.
```

For an elementary binary group

```
Gamma = GF(2)^r = C_2^r,
```

the standard p-group formula gives

```
D(C_2^r) = r+1.
```

Hence

```
boxed(q <= r).
```

Equivalently, in `GF(2)^r` the nonzero cycle labels are linearly independent.

This is stronger than merely bounding the number of distinct labels.

## 5. Exact consequence for the audited r=2 gate

For

```
Gamma = GF(2)^2
```

there are only three nonzero labels:

```
01, 10, 11.
```

An optimum can be chosen with at most two correction cycles, and if two are
present their labels are distinct and linearly independent.

Therefore the complete cycle-label pattern list has only seven cases:

```
{}
{01}
{10}
{11}
{01,10}
{01,11}
{10,11}.
```

Once a cycle-label pattern is fixed, the required path label is determined:

```
lambda(P)
=
g - sum_i gamma_i.
```

Over `GF(2)^2`, subtraction is XOR.

Thus the exact optimization reduces from an unbounded correction multiset to
seven structural pattern classes.

## 6. Finite exact controls

The checker compares two quantities on random small labelled graphs:

1. unrestricted brute-force optimum over every edge subset with the required
   T-boundary and target label;
2. optimum restricted to a simple `u-v` path plus at most two pairwise
   edge-disjoint simple cycles whose nonzero labels are linearly independent.

The comparison is exact.

Controls include zero edge weights, so the minimum-cardinality tie-break in the
proof is exercised rather than hidden behind strict positivity.

The development control used 1000 random instances; the committed checker uses
a deterministic seeded regression set sized for CI.

## 7. Source audit / anti-duplication

The exact T-join decomposition above was searched under:

- zero-sum-free labelled T-join;
- Davenport constant T-join;
- group-labelled T-join cycle decomposition;
- prescribed-label T-join;
- fixed-number cycle correction.

No source located in this audit stated the exact optimum decomposition theorem
for the present labelled T-join objective.

Two nearby bodies of literature are source-bound:

1. **Zero-sum theory.** Davenport's constant is the canonical invariant for
   zero-sum-free sequences. For finite abelian p-groups,
   `D(C_{p^{a_1}}+...+C_{p^{a_r}})=1+sum_i(p^{a_i}-1)`; in particular
   `D(C_2^r)=r+1`.

2. **Min-Sum Cycle Packing.** Bentert et al. give polynomial algorithms for
   minimum-total-weight packing of a fixed number of edge-disjoint cycles.
   That result does not solve the present mixed object because JANUS also needs
   one terminal path and prescribed group labels on each correction component.

Accordingly the theorem is retained as a JANUS-derived structural compression,
not as a claim that Davenport theory or fixed-k cycle packing is new.

## 8. Algorithmic ceiling

This theorem does **not** prove deterministic polynomial solvability.

The unresolved object is now exactly:

```
minimum total weight of

one simple u-v path
+
at most two edge-disjoint simple cycles

with one of seven prescribed GF(2)^2
component-label patterns.
```

Known randomized GCC / Bipartite Exact Matching remains a valid source-bound
solver.

Known unlabelled fixed-k cycle packing does not enforce the required labels and
does not include the terminal path interaction.

Therefore:

```
UNBOUNDED CORRECTION-CYCLE MULTIPLICITY
=
ELIMINATED

GF(2)^2 CORRECTION PATTERNS
=
7

DETERMINISTIC LABELLED MIXED PACKING
=
OPEN
```

## 9. Next gate

```
R5_E10A_GF2_SQUARED_LABELLED_PATH_PLUS_TWO_CYCLES_BYPASS_GATE_V1
```

Target:

either

1. solve the seven labelled path-plus-cycle pattern classes deterministically
   in polynomial time with witness reconstruction; or
2. derive a strict exact contraction that bypasses them.

Forbidden:

- invoking the quarantined Du-2026 theorem as authority;
- assuming general Exact Matching derandomization;
- full syndrome/trellis tables;
- replacing the T-join by a path and dropping correction cycles;
- treating unlabelled cycle packing as label-preserving.

## 10. Scientific ceiling

```
ZERO-SUM-FREE OPTIMUM CYCLE LABELS
=
PROVED

q <= D(Gamma)-1
=
PROVED

GF(2)^r: q <= r
=
PROVED

GF(2)^2: SEVEN CORRECTION PATTERNS
=
PROVED

DETERMINISTIC SOLVER
=
NOT PROVED

D1
=
EMPTY

P_VS_NP
=
OPEN
```
