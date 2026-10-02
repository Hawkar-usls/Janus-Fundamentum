# R5 E9 — Conflict Odd-Hole / Hypergraph Perfect-Matching Source Audit

Date: 2026-09-25

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED__GROUPED_QUOTIENT_CANONICALIZED`

Immediate predecessors:

```
PA-0017-PERFECT-KERNEL-CONFLICT-GRAPH-SOURCE-AUDIT
NM-0022-CUBIC-CONFLICT-GRAPH-OBSTRUCTION
NM-0023-CONFLICT-ODD-HOLE-COVERAGE-SELECTOR-CONSERVATION
```

## G0 — exact object

The live cubic Exact-One instance is a square 0/1 matrix A with row and column
sum three.  Form the dual hypergraph H(A):

- vertices of H are the clauses / rows of A;
- one hyperedge e_j is the 3-row support of each variable / column j.

Thus H(A) is exactly:

```
3-uniform
3-regular
```

and a Boolean Exact-One witness is exactly a perfect matching of H(A).

The variable conflict graph from PA-0017 is the line/intersection graph:

```
C(A) = L(H(A)).
```

The new audit question is whether the unbounded induced odd-hole obstruction
of NM-0022/NM-0023 is already covered by standard hypergraph matching,
balanced-hypergraph, odd-cycle-polytope, or tight-cut decomposition theory.

## G1 — internal anti-duplication

Repository-first replay found the following adjacent internal material:

- the rank-3 all-or-none / 3-uniform 3-regular exact-cover hard core;
- balanced and signed-balanced polynomial islands in transformed E9 coordinates;
- strong-odd-cycle language in pair-defect / bicoloring artifacts;
- witness-dominance grouped contraction as a generic exact meta-theorem;
- NM-0023, which blocks one-coverage-bit-per-hole-vertex elimination.

No existing JANUS artifact was found that binds the **direct cubic Exact-One
odd-hole residual** to the standard hypergraph perfect-matching tight-cut
decomposition machinery, or that proves a grouped quotient for this direct
3-uniform 3-regular hypergraph.

## G2 — canonical external language

Let

```
v_0,v_1,...,v_{k-1}
```

be an induced odd hole of C(A).  Let e_i be the corresponding hyperedges of
H(A).

Because consecutive conflict vertices are adjacent,

```
e_i intersect e_{i+1} != empty.
```

Because the hole is induced, nonconsecutive e_i,e_j are disjoint.
Furthermore one hypergraph vertex cannot witness two distinct consecutive
intersections, otherwise one e_i would meet an extra nonconsecutive cycle
edge and create a chord in C(A).

Therefore the e_i together with their consecutive intersection vertices form
a **strong odd cycle** of H(A).

Conversely, the cycle edges of a strong odd cycle induce the corresponding
odd cycle in the line graph whenever no nonconsecutive cycle hyperedges
intersect.

Hence the canonical grouped object is:

```
STRONG ODD CYCLE
IN A 3-UNIFORM 3-REGULAR HYPERGRAPH
PERFECT-MATCHING INSTANCE.
```

The direct conflict graph and dual hypergraph views are exact witness-preserving
representations of the same Exact-One problem.

## G3 — public-source exhaustion

### S1 — balanced hypergraphs are the exact no-strong-odd-cycle donor

Berge's balanced-hypergraph language defines balanced hypergraphs by absence of
strong odd cycles.

Classical balanced-hypergraph matching theory supplies König-type min-max
properties and integral matching/covering polyhedra.  Conforti, Cornuéjols,
Kapoor and Vušković study perfect matchings in balanced hypergraphs.

Thus:

```
NO STRONG ODD CYCLE
=
SOURCE-BOUND BALANCED-HYPERGRAPH POLYNOMIAL ISLAND.
```

This does not close the present residual because NM-0022 explicitly enters
through a strong odd cycle.

### S2 — odd-cycle stable-set polyhedra give a second donor, not a universal recognizer

For t-perfect graphs the stable-set polytope is described by nonnegativity,
edge and odd-cycle inequalities and maximum-weight stable set is polynomial.
For h-perfect graphs clique inequalities are also allowed.

This is a natural direct-conflict-graph carrier for handling whole odd holes
without retaining one selector per hole vertex.

However general recognition of t-perfect graphs is not known polynomially;
the polynomial recognition theorem located in the audit is for the claw-free
subclass.  The present cubic conflict graphs are not guaranteed claw-free:
the cubic incidence structure only gives the weaker local K_1,4-free bound.

Therefore h/t-perfect machinery is a valid source donor / terminal certificate
when membership is independently certified, not an end-to-end residual solver.

### S3 — hypergraph tight-cut decomposition is the closest grouped-contraction donor

Beckenbach, Hatzel and Wiederrecht generalize tight cuts, tight-cut
contractions and tight-cut decomposition from graphs to hypergraphs.  For
uniformable hypergraphs they prove uniqueness properties, perfect-matching
polytope decomposition, and polynomial recognition of tight cuts.

This is directly aligned with the JANUS target:

```
GROUP MULTIPLE LOCAL MATCHING SELECTORS
AND CONTRACT THE BLOCK THROUGH AN EXACT INTERFACE.
```

But the source theory is formulated in the perfect-matching /
matching-covered setting.  Its contraction theorems preserve and compose
perfect matchings once the relevant matching-covered context and a tight cut
are available.

It does not supply a free polynomial YES/NO algorithm for arbitrary
3-uniform 3-regular Exact Cover / RXC3 instances.  Using existence of a
perfect matching or matching-coveredness as an oracle would be circular.

Classification:

```
HYPERGRAPH_TIGHT_CUT_CONTRACTION
=
SOURCE-BOUND GROUPED-QUOTIENT DONOR

UNIVERSAL RXC3 DECISION
=
NOT SUPPLIED.
```

### S4 — ordinary graph line-graph h-perfect theory does not silently apply

Cao--Nemhauser characterize h-perfect and t-perfect line graphs of ordinary
graphs.  Our conflict graph is the line graph of a 3-uniform hypergraph, not
in general the line graph of an ordinary graph.  The ordinary-line-graph
classification is therefore adjacent only.

## G4 — collision matrix

```
CUBIC EXACT-ONE
<-> PERFECT MATCHING IN 3-UNIFORM 3-REGULAR HYPERGRAPH
=
EXACT CANONICAL REPRESENTATION

CONFLICT GRAPH
=
HYPERGRAPH LINE / INTERSECTION GRAPH

INDUCED CONFLICT ODD HOLE
=
STRONG ODD CYCLE IN THE DUAL HYPERGRAPH

BALANCED / NO STRONG ODD CYCLE
=
SOURCE-BOUND POLYNOMIAL ISLAND

h/t-PERFECT STABLE-SET CARRIER
=
SOURCE-BOUND DONOR / CERTIFIED P-ISLAND
GENERAL RECOGNITION DOES NOT CLOSE RESIDUAL

UNIFORMABLE-HYPERGRAPH TIGHT CUT
=
SOURCE-BOUND GROUPED CONTRACTION DONOR

UNIVERSAL EXACT GROUPED QUOTIENT
FOR THE CURRENT 3-REGULAR STRONG-ODD-CYCLE RESIDUAL
=
NO SOURCE CLOSURE LOCATED
```

## Audit decision

The canonical object changed materially from a per-vertex odd-hole boundary
projection to a hypergraph perfect-matching block containing a strong odd
cycle.  A fresh audit is therefore required and now complete.

```
PA-0018
=
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E9_HYPERGRAPH_STRONG_ODD_CYCLE_GROUPED_QUOTIENT_GATE_V1
```

Allowed targets include:

1. an exact tight-cut-like contraction with a polynomially recognizable
   certificate that does not assume the unknown perfect matching;
2. a grouped witness-dominance certificate eliminating multiple selector
   dimensions at once;
3. a certified h/t-perfect or balanced terminal carrier;
4. a theorem proving a structural interaction invariant on strong odd cycles
   that strictly decreases under an exact quotient.

## Mandatory anti-loop controls

Do not:

- rederive balanced-hypergraph strong-odd-cycle language as JANUS novelty;
- treat h/t-perfect recognition as generally polynomial without the required
  subclass certificate;
- invoke hypergraph tight-cut decomposition after silently assuming a perfect
  matching / matching-covered input;
- replace the strong odd cycle by one Boolean state per cycle hyperedge;
- use ordinary graph line-graph theorems as if the 3-uniform hypergraph were a
  graph;
- branch over all perfect matchings or all odd-hole selector states.

## Scientific ceiling

```
BALANCED DIRECT HYPERGRAPH
=
SOURCE-BOUND P ISLAND

CERTIFIED h/t-PERFECT CONFLICT GRAPH
=
SOURCE-BOUND P CARRIER

TIGHT-CUT HYPERGRAPH CONTRACTION
=
SOURCE-BOUND DONOR

GENERAL STRONG-ODD-CYCLE GROUPED QUOTIENT
=
OPEN

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
