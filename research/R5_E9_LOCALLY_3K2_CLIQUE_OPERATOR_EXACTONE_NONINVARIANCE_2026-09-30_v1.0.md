# R5 E9 — Locally-3K2 Clique Operator Exact-One Non-Invariance

Date: 2026-09-30

Status:
`JANUS_EXACT_ANTI_LOOP_COUNTERCONTROL__CLIQUE_OPERATOR_PRESERVES_CARRIER_NOT_EXACTONE_SEMANTICS__NO_D1_PROMOTION`

## 1. Motivation

For every connected square linear-cubic Exact-One source `A`, its conflict graph on source variables has

```text
Adj(G)=A^T A-3I.
```

It is 6-regular, locally `3K2`, and every edge belongs to exactly one source triangle.  The clique graph `K(G)` has one vertex per source triangle and adjacency when two source rows intersect.  Therefore

```text
Adj(K(G))=A A^T-3I,
```

so passing to the clique graph is exactly the incidence duality `A -> A^T`.

Recent graph-theoretic work observes that the class `locally 3K2` is closed under the clique operator.  That carrier closure does not imply preservation of Exact-One satisfiability.

## 2. Explicit n=12 source

Let four colors be `0,1,2,3` and let the remaining eight source variables be `4,...,11`, corresponding to graph vertices `0,...,7` after subtracting four.

Take the following four color classes, each a 3-edge matching on vertices `0,...,7`:

```text
color 0: (3,4), (1,2), (0,6)
color 1: (4,7), (0,1), (3,5)
color 2: (0,5), (2,7), (4,6)
color 3: (2,6), (5,7), (1,3)
```

The union is a simple cubic graph `H` on eight vertices.  For every graph edge `(u,v)` of color `c`, create one Exact-One row

```text
{c, 4+u, 4+v}.
```

Thus the 12 source rows are

```text
(0,7,8)
(0,5,6)
(0,4,10)
(1,8,11)
(1,4,5)
(1,7,9)
(2,4,9)
(2,6,11)
(2,8,10)
(3,6,10)
(3,9,11)
(3,5,7)
```

in zero-based indexing.

## 3. Source structure

Every row has size three.

Each color variable occurs in exactly the three rows of its color.  Each graph-vertex variable occurs in exactly the three rows corresponding to its incident cubic-graph edges.  Hence every column also has degree three.

Linearity follows because:

- two edges of one color are disjoint, so same-color rows intersect only in the color variable;
- two distinct graph edges share at most one endpoint;
- different colors use different color variables.

The Levi graph is connected because the underlying cubic graph is connected and each color node is attached to three graph-edge rows.

Thus `A` is a connected square linear-cubic `12_3` source.

## 4. Primal source is SAT

Select the four color columns

```text
S={0,1,2,3}.
```

Every source row contains exactly its own color and no other selected coordinate. Therefore

```text
A chi_S = 1,
```

so `A` is Exact-One SAT.

## 5. Dual source is a rainbow perfect-matching problem

A Boolean vector `y` satisfying

```text
A^T y=1
```

selects source rows such that every source column is covered exactly once.

For a color column `c`, this requires exactly one selected row from color class `c`.

For a graph-vertex column `4+u`, this requires exactly one selected row corresponding to an edge incident with `u`.

Therefore a dual Exact-One witness is exactly a perfect matching of `H` containing one edge of each of the four colors: a rainbow perfect matching.

For the displayed colored cubic graph, an exact finite backtracking check over the `3^4=81` one-edge-per-color choices finds no rainbow perfect matching.

Consequently

\[
\boxed{
A\text{ is Exact-One SAT},
\qquad
A^T\text{ is Exact-One UNSAT}.
}
\]

## 6. Conflict/clique interpretation

The variable conflict graph of `A` is locally `3K2`.  Its clique graph is the row-intersection conflict graph and corresponds exactly to `A^T`.

Hence this control proves:

```text
G locally 3K2 and Exact-One-positive
DOES NOT IMPLY
K(G) Exact-One-positive.
```

Closure of the carrier under the clique operator is not a satisfiability-preserving representation change.

## 7. External boundary

The graph-theoretic fact used only as motivation is that locally-`3K2` graphs have triangles as their maximal cliques, every edge belongs to exactly one triangle, and the clique operator preserves the locally-`3K2` property.  This does not state or imply any Exact-One semantic invariance.

The JANUS countercontrol above is self-contained and exact.

## 8. Ceiling

```text
LOCALLY-3K2 CARRIER UNDER CLIQUE OPERATOR
= CLOSED / EXTERNAL GRAPH FACT

CLIQUE OPERATOR ON SOURCE
= INCIDENCE DUALITY A -> A^T

EXACT-ONE SAT INVARIANCE UNDER A -> A^T
= FALSE

EXPLICIT CONNECTED LINEAR-CUBIC CONTROL
A SAT / A^T UNSAT
= PROVED

CLIQUE-OPERATOR UNIVERSAL CONTRACTION ROUTE
= CLOSED

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```