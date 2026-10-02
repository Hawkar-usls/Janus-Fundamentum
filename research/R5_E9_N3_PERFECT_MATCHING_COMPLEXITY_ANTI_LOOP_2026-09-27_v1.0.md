# R5 E9 — n3 Perfect-Matching Complexity Anti-Loop

Date: 2026-09-27

Status:
`SOURCE_AUDIT__EXACT_INTERSECTION_HARDNESS_NOT_IMPORTED`

Scientific ceiling:

```text
NO NEW NP-HARDNESS THEOREM FOR THE EXACT n3 CLASS IS CLAIMED HERE.
NO POLYNOMIAL SOLVER IS IMPORTED.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Exact JANUS combinatorial identification

Let `A` be the incidence matrix of a connected linear cubic 3-uniform square
carrier.  Regard the columns of `A` as 3-subsets of the row set.  Because every
column has size three, every row occurs in exactly three columns, and distinct
columns meet in at most one row, the dual hypergraph

```text
H_A = (rows(A), {support(column_j): j in columns(A)})
```

is a linear 3-uniform 3-regular hypergraph with the same number `n` of vertices
and hyperedges; equivalently it is a combinatorial `n_3` configuration.

For `x in {0,1}^n`,

```text
A x = 1
```

holds iff the hyperedges whose columns have `x_j=1` are pairwise disjoint and
cover every row exactly once.  Therefore:

```text
CUBIC-LINEAR EXACT-ONE
=
PERFECT MATCHING / PARALLEL CLASS IN THE DUAL n_3 CONFIGURATION.
```

This is an exact polynomial-time identity, not a reduction with gadgets.

## 2. What public complexity results really give

### 2.1 Linear 3-uniform perfect matching is NP-complete without regularity

The paper on almost-perfect matchings in uniform hypergraphs explicitly uses
`PM_lin(3)`, the perfect-matching problem restricted to linear 3-uniform
hypergraphs, and reduces triangle decomposition to it.  Hence linearity alone
does not create a polynomial matching algorithm.

Source:

- D. Kühn, D. Osthus, T. Townsend, *The complexity of almost perfect
  matchings and other packing problems in uniform hypergraphs with high
  codegree*, European Journal of Combinatorics 34 (2013), 632–646,
  DOI `10.1016/j.ejc.2011.12.009`.

### 2.2 3-uniform 3-regular exact cover is NP-complete without linearity

Restricted Exact Cover by 3-Sets (RXC3) has exactly three elements per set and
exactly three occurrences per element.  Thus its incidence matrix is square
with all row and column sums equal to three.  RXC3 is NP-complete.

Primary attribution used throughout the literature:

- T. F. Gonzalez, *Clustering to minimize the maximum intercluster distance*,
  Theoretical Computer Science 38 (1985), 293–306.

This gives hardness of the regular/uniform surface but does not by itself give
the JANUS pairwise-linearity promise.

### 2.3 Partial Steiner triple systems are NP-complete for a parallel class,
with point degree at most three

Li and Toulouse prove that deciding whether a partial Steiner triple system has
a parallel class is NP-complete.  Their Corollary 2.2 preserves the restriction
that every point occurs in at most three triples.

Source:

- P. C. Li, M. Toulouse, *Some NP-Completeness Results on Partial Steiner
  Triple Systems and Parallel Classes*, Ars Combinatoria 80 (2006), 45–51.

A partial Steiner triple system is linear 3-uniform, so this result reaches
linearity plus maximum degree three, but not the exact 3-regular square `n_3`
promise.

### 2.4 3-regular 3-partite 3-uniform perfect matching is NP-complete

Bounded 3-dimensional matching remains NP-complete when every vertex belongs to
exactly three triples.  This supplies another exact-regular control, but a
3-partite hypergraph may contain two hyperedges sharing two coordinates, so
3-partiteness does not imply JANUS linearity.

A convenient source statement is Theorem 10 in:

- K. Bérczi, A. Bernáth, M. Vizer, *A note on V-free 2-matchings*,
  EGRES Quick-Proof 2015-04.

## 3. The exact intersection must not be silently inferred

The JANUS carrier simultaneously requires

```text
3-uniform
AND 3-regular
AND linear
AND square n edges / n vertices
(and usually connected).
```

The sources above establish hardness for neighboring supersets/subclasses after
one of these promises is relaxed.  None of the checked source statements alone
licenses the assertion

```text
PERFECT MATCHING IN CONNECTED n_3 CONFIGURATIONS = NP-COMPLETE.
```

A separate source theorem or a proof-carrying regularization reduction is
required before that hardness statement can be promoted.

This distinction is mandatory anti-loop: do not cite RXC3 as if it were linear,
and do not cite `PM_lin(3)` as if it were 3-regular.

## 4. Interaction with the Hoffman bridge

The companion theorem

`R5_E9_CUBIC_LINEAR_HOFFMAN_COCLIQUE_EQUIVALENCE_2026-09-27_v1.0.md`

proves for this exact `n_3` carrier

```text
parallel class / perfect matching
iff Ax=1
iff Hoffman coclique of size n/3 in G(A)
iff equitable quotient [[0,6],[3,3]]
iff {-1,2}-valued vector in E_{-3}(G(A)).
```

Thus all of these are merely exact representations of the same residual
problem.  None should be counted as a solver unless it creates a deterministic
polynomial construction or polynomial rejection certificate.

## 5. Productive frontier

The current constructive gate remains

```text
R5_E9_OET_IRREDUCIBLE_HOFFMAN_COCLIQUE_GATE_V1.
```

The useful external lesson is sharper now:

- dropping regularity leaves an NP-complete linear perfect-matching problem;
- dropping linearity leaves an NP-complete cubic exact-cover problem;
- keeping linearity but only bounding degree by three is already NP-complete;
- therefore any polynomial JANUS route must exploit the exact simultaneous
  `n_3` promises and/or an additional decomposition invariant, not merely one
  of the individual properties.

Candidate proof task:

```text
Either
  prove a polynomial exact quotient/decomposition theorem for every
  OET-irreducible high-nullity n3 carrier,
or
  construct a source-bound family that falsifies the proposed quotient rule.
```

A separate reduction project may try to regularize the degree-<=3 partial-STS
hardness construction while preserving linearity and a parallel class.  Until
such a gadget is proved and independently replayed, exact `n_3` NP-completeness
is deliberately left unpromoted.
