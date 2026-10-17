# R5 E9 — Odd-Hole Full-Boundary Matching-Realizability Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__MATCHING_REALIZABILITY_TEST_AUTHORIZED`

Immediate predecessors:

```
PA-0018-CONFLICT-ODD-HOLE-HYPERGRAPH-MATCHING-SOURCE-AUDIT
NM-0023-CONFLICT-ODD-HOLE-COVERAGE-SELECTOR-CONSERVATION
```

## G0 — exact changed object

For an induced odd hole

```
v_0,...,v_{k-1},  k>=5 odd,
```

the source clauses are

```
C_i={v_i,v_{i+1},w_i},
D_i={v_i,a_i,b_i}.
```

NM-0023 proved that retaining one derived coverage selector

```
d_i=a_i+b_i=1-v_i
```

recreates Exact-One-3 and gives no selector-dimension drop.

The changed question is genuinely grouped:

> existentially eliminate **all** hole variables v_i at once and study the exact
> relation induced on the already-existing external ports.

There are two interfaces to distinguish.

### Belt-only interface

```
R_belt^k(w)
=
exists v
for all i:
v_i+v_{i+1}+w_i=1.
```

### Full source interface

```
R_full^k(w,a,b)
=
exists v
for all i:
v_i+v_{i+1}+w_i=1
and
v_i+a_i+b_i=1.
```

The audit asks whether either relation is already a standard
matching-realizable / delta-matroid object.

## G1 — internal anti-duplication

Repository-first replay found:

- NM-0023, which blocks the derived selector d_i but does not project directly
  to the original ports w,a,b;
- R5_E9_RANK3_ALL_OR_NONE_LOCAL_MATCHING_BARRIER, which source-binds
  matching-realizable relations and delta-matroid exchange for a **single**
  rank-3 all-or-none atom;
- older direct-delta-matroid and projected-linear barriers in different E8/E9
  representations;
- the NAE odd-hole projection theorem, whose boundary relation is universal and
  has different semantics.

No internal artifact was found that classifies R_belt^k or R_full^k above.

## G2 — canonical external language

Kazda--Kolmogorov--Rolínek define, for a graph G with distinguished boundary
vertices, the matching-realizable relation consisting of boundary deletion
patterns for which the remaining graph has a perfect matching.

They prove/use the fundamental implication:

```
MATCHING REALIZABLE
=>
EVEN DELTA-MATROID.
```

Their blossom-generalization solves edge CSP when every constraint is an even
delta-matroid relation.

Therefore the correct canonical test for an ordinary-matching grouped quotient
is not whether a boundary truth table "looks matching-like", but whether its
feasible-set family passes delta-matroid symmetric exchange; failure is an
unconditional representation barrier to ordinary matching realizability.

## G3 — source collision for the belt-only projection

For a fixed boundary word w, let

```
W={i:w_i=1}.
```

Interpret the k belt clauses C_i as the vertices of an ordinary cycle graph
C_k.  The variable v_i covers the two adjacent belt clauses C_{i-1},C_i and is
therefore the ordinary cycle edge between those two vertices.  A selected w_i
covers the single belt vertex C_i.

Hence:

```
w in R_belt^k
iff
C_k-W has a perfect matching.
```

This is **exactly** the standard matching-realizable relation represented by
the cycle with all cycle vertices exposed as boundary terminals.

For odd k every feasible W is nonempty.  The remaining graph is a disjoint
union of paths, and feasibility is equivalent to every path having even order.
Each such path has a unique perfect matching.  Therefore the eliminated v-word
is uniquely reconstructible from w in O(k).

Classification:

```
BELT_ONLY_PROJECTION
=
SOURCE-BOUND MATCHING-REALIZABLE OBJECT
+ ELEMENTARY JANUS IDENTIFICATION.
```

No novelty is claimed for the matching relation itself.

## G4 — full boundary is the legitimate new test

The third-occurrence clauses D_i couple the selected/unselected status of the
cycle matching edge v_i to two additional external ports a_i,b_i.

No located source theorem states that this particular full relation
R_full^k is matching realizable, an even delta-matroid, or belongs to another
standard tractable delta-matroid class for every odd k.

Thus the first permitted mathematical test is exact and finite:

```
DOES R_full^k SATISFY DELTA-MATROID SYMMETRIC EXCHANGE?
```

A failure for a uniform all-k witness blocks ordinary matching-gadget
replacement of the whole odd-hole block.  A pass would authorize the next
representation/construction test.

## G5 — source ceiling

Important distinctions:

```
R_belt^k matching-realizable
!=
R_full^k matching-realizable.

matching-realizable
=>
even delta-matroid,

but

even delta-matroid
does not imply
matching-realizable at arbitrary arity.
```

Kazda--Kolmogorov--Rolínek explicitly exhibit higher-arity even delta-matroids
that are not matching realizable, so passing exchange would still not by itself
finish the construction problem.

## Audit decision

```
PA-0019
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E9_ODD_HOLE_FULL_BOUNDARY_MATCHING_REALIZABILITY_GATE_V1
```

First killer test:

```
R_full^k
DELTA-MATROID SYMMETRIC EXCHANGE
FOR ALL ODD k>=5.
```

## Mandatory anti-loop controls

Do not:

- call R_belt^k a new matching theorem;
- confuse the unique internal reconstruction from w with a solver for the full
  source interface;
- discard D_i while claiming an exact source contraction;
- infer matching realizability merely from delta-matroid exchange;
- re-run the single rank-3 {000,111} matching barrier as if it were the grouped
  odd-hole boundary;
- materialize an exponential boundary truth table as the proposed algorithm.

## Scientific ceiling

```
BELT-ONLY MATCHING PROJECTION
=
SOURCE-BOUND / EXACT

FULL ODD-HOLE BOUNDARY
=
UNCLASSIFIED

ORDINARY MATCHING REALIZABILITY OF FULL BOUNDARY
=
OPEN PENDING KILLER TEST

D1
=
EMPTY

P_VS_NP
=
OPEN
```
