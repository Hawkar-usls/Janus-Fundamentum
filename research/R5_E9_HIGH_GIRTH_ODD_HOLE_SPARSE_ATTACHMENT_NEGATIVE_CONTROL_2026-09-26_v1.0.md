# R5 E9 — High-Girth Odd-Hole Sparse-Attachment Negative Control

Date: 2026-09-26

Authority:
`JANUS_DERIVED_UNIFORM_LOCAL_GEOMETRY_AFTER_PA0024__SOURCE_BACKED_CAGE_CONTROL__NO_COMPLEXITY_LOWER_BOUND`

Authorizing audit:
`PA-0024-ODD-HOLE-HIGH-GIRTH-ATTACHMENT`

Immediate mathematical predecessor:
`NM-0027-REGULAR-UNIFORM-CONFLICT-EXPANSION`

Checker:
`experiments/r5_e9_high_girth_odd_hole_sparse_attachment.py`

## 1. General girth theorem

Let B be a simple cubic bipartite incidence graph of a square positive
Exact-One-3 source.  Assume

```
girth(B) >= 10
```

and B contains a 10-cycle

```
x_0-C_0-x_1-C_1-...-x_4-C_4-x_0,
```

where x_i are variable-side vertices and C_i are clause-side vertices.

Write

```
C_i={x_i,x_{i+1},w_i}.
```

Let D_i be the third clause incident with x_i and write

```
D_i={x_i,a_i,b_i}.
```

Then the following hold.

### T1 — the conflict projection is an induced C5

Consecutive x_i,x_{i+1} share C_i.

If two nonconsecutive x_i,x_j shared any clause, that clause together with the
shorter arc of the incidence 10-cycle would create an incidence cycle of
length at most six, contradicting girth at least ten.

Hence

```
x_0 x_1 x_2 x_3 x_4 x_0
```

is an induced conflict C5.

### T2 — all fifteen external ports may be distinct; in fact girth forces it

Consider the fifteen labeled ports

```
w_0,...,w_4,
a_0,b_0,...,a_4,b_4.
```

Any equality between two distinct port labels creates a short incidence cycle.

There are only three distance types.

1. `w_i=w_j`: the common variable gives a length-2 path between C_i,C_j;
   the shorter cycle arc between those clause vertices has length at most 4,
   producing a cycle of length at most 6.

2. `w_i=a_j` or `w_i=b_j`: the common variable gives
   `C_i-port-D_j-x_j`, a length-3 path to the original 10-cycle.
   The shorter cycle arc from x_j to C_i has length at most 5, producing a
   cycle of length at most 8.

3. a port in `{a_i,b_i}` equals a port in `{a_j,b_j}`, i!=j:
   the common variable gives a length-4 path
   `x_i-D_i-port-D_j-x_j`; the shorter x_i--x_j arc has length at most 4,
   producing a cycle of length at most 8.

The same shorter-cycle argument excludes equality of an external port with a
hole vertex.

Therefore

```
boxed(
|{w_i,a_i,b_i : i in Z_5}| = 15.
)
```

So NM-0027 two-expansion does **not** force local port aliasing around an odd
hole.

### T3 — every hole vertex is a claw center

At x_i choose the three neighbors

```
w_{i-1}, w_i, a_i.
```

They come from the three distinct clauses incident with x_i.

If any two of these leaves were adjacent in the conflict graph, an outside
clause witnessing that adjacency together with their two source clauses and
x_i would form an incidence 6-cycle.

Thus the leaves are pairwise nonadjacent and

```
boxed(
x_i is the center of an induced K_{1,3}
for every i.
)
```

Hence the sparse high-girth control is not swallowed by the claw-free
polynomial terminal.

### T4 — the whole conflict graph is 6-regular and has no closed-neighborhood domination

For any source variable u, its three incident clauses each contribute two
co-clause variables.

If a co-clause variable were repeated across two of those clauses, the
incidence graph would contain a 4-cycle.  Hence all six are distinct:

```
deg_C(F)(u)=6.
```

Suppose `N[u] subseteq N[v]`.  Since the conflict graph is 6-regular, both
closed neighborhoods have size seven, so they must be equal.

If u,v are nonadjacent this is impossible because u belongs to N[u] but not
N[v].

If they are adjacent, let C be their unique common clause and let D be another
clause incident with u.  Pick q in D-{u}.  If q were adjacent to v, the two
source clauses plus the witnessing q-v clause would create an incidence
6-cycle.  Hence q belongs to N[u]\N[v], contradiction.

Therefore

```
boxed(
NO closed-neighborhood domination move exists anywhere
in a cubic incidence-girth>=10 source.
)
```

Degree-2 folding is also impossible because every conflict degree is six.

### T5 — NM-0027 still applies

Nothing in the girth argument changes uniformity or regularity.

The source remains the 2-section of a 3-uniform 3-regular dual hypergraph, so
NM-0027 gives for every conflict independent set I:

```
|N(I)| >= 2|I|.
```

Thus we have simultaneously:

```
2-expanding
+
induced odd hole
+
claw at every hole vertex
+
no local port aliasing
+
no neighborhood domination
+
no degree-2 folding.
```

This directly falsifies the proposed implication

```
2-expansion + odd hole
=>
mandatory useful local overlap/domination.
```

## 2. Source-backed finite replay: Harries 10-cage

PA-0024 source-binds the three classical (3,10)-cages as bipartite Levi graphs
of (35_3) configurations.

The checker reconstructs the Harries graph from the open Sage LCF sequence

```
[-29,-19,-13,13,21,-27,27,33,-13,13,19,-21,-33,29]^5.
```

It independently verifies:

```
order = 70
edges = 105
bipartition = 35+35
degree = 3
girth = 10.
```

Using the explicit incidence cycle

```
0-1-2-3-4-5-6-7-40-41-0
```

it obtains the conflict hole

```
{0,2,4,6,40}.
```

The exact fifteen external variable ports are all distinct, every one of the
five hole vertices is a claw center, the entire 35-vertex conflict graph is
6-regular, and the checker finds zero closed-neighborhood domination pairs.

So the general theorem has a literal reproducible source witness.

## 3. This is not yet the fully filtered PA-0001 survivor

The epistemic firewall matters.

The checker computes the exact rational rank of the Harries 35x35 incidence
matrix:

```
rank_Q = 35
nullity_Q = 0.
```

Therefore this particular finite cage is caught by the already sealed E9
low-rational-nullity polynomial lane.

Accordingly NM-0028 does **not** claim:

```
Harries cage
=
hard residual survivor.
```

What it proves is narrower and decisive:

```
NM-0027 TWO-EXPANSION
+
LITERAL CUBIC SOURCE GEOMETRY
+
ODD HOLE
+
CLAW PRESENCE
+
NO DOMINATION/FOLDING
```

still do not force the local attachment overlap hoped for in the proposed next
contraction.

Any theorem that uses additional live promises such as high rational nullity,
phase inconsistency, or noncommuting structure must audit those promises
explicitly.

## 4. Family-level source control

He--Luo--Xu (2026) source-bind regular bipartite constructions with prescribed
girth.  Their theorem includes the regular bipartite setting and explicitly
relates incidence 2g-cycles to hypergraph g-cycles.

Thus girth-ten sparse incidence geometry is not merely one accidental 70-vertex
graph.  The present JANUS theorem is local and applies to every such cubic
source containing a 10-cycle.

No statement about rational nullity or the other PA-0001 promises is imported
from that existence theorem.

## 5. Consequence for the universal-algorithm search

The proposed immediate route

```
2-expansion
-> mandatory odd-hole external overlap
-> grouped domination
```

is closed.

The next useful leverage must depend on information not present in the local
girth-ten geometry, for example:

- the **actual long-range external context** of the hole;
- the promise that the low-rational-nullity lane has already been removed;
- noncommuting / phase-inconsistent permutation structure;
- a representation-changing MIS move whose resulting graph creates a known
  reducible structure.

Because that is a changed combined object, further new mathematics requires a
fresh pre-math audit.

## 6. Verdict

```
NM-0028
HIGH-GIRTH ODD-HOLE SPARSE ATTACHMENT
=
PASS

2-EXPANSION FORCES LOCAL PORT ALIAS
=
FALSIFIED

2-EXPANSION FORCES NEIGHBORHOOD DOMINATION
=
FALSIFIED

GIRTH-10 C5 EXTERNAL PORTS
=
15 / 15 DISTINCT

EVERY HOLE VERTEX
=
CLAW CENTER

CONFLICT GRAPH DEGREE
=
6

CRITICAL / CROWN ON UNTOUCHED SOURCE
=
IMPOSSIBLE BY NM-0027

HARRIES FINITE CONTROL
=
LOW-NULLITY P-ISLAND / NOT FULL RESIDUAL

NEXT
=
FRESH AUDIT OF LONG-RANGE + HIGH-NULLITY / PHASE-FAIL INTERACTION

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
