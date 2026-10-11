# R5 — Exact 21-State Four-Edge-Cut Transfer and Polynomial Cyclic Cut Search

Date: 2026-10-12. Location: `Hawkar-usls/Janus-Fundamentum`.
Research successor to PR #516 on branch
`research/r5-cubic-flow-smith-pair-20261011`.

**Ultimate target remains:** all-input deterministic
`SolveLinearCubicXSAT` with verified SAT witness or UNSAT
and proved worst-case n^{O(1)} BIT operations.

**Current result:** exact all-cubic 4-edge boundary contraction
and polynomial cut discovery. These are VALID but INSUFFICIENT
for a universal solver; unresolved four-pole signature
evaluation and irreducible cubic cores are left OPEN.

## 1. Four-edge boundary alphabet has exactly 21 values

Take ANY finite simple cubic graph G=(V,E) and ANY bipartition
V=S disjoint_union T with exactly FOUR crossing edges
e0,e1,e2,e3. Identify the three proper colours with
the three nonzero elements of H=(F2)^2:

    colour 0 -> (1,0)
    colour 1 -> (0,1)
    colour 2 -> (1,1)

At every cubic vertex, proper 3-edge-colouring means that the
three nonzero incident H-labels are all distinct, and therefore
their sum in H is zero. Summing over every vertex in shore S,
each internal edge appears twice and cancels, leaving

    colour(e0)+colour(e1)+colour(e2)+colour(e3)=0 in H.  (1)

There are EXACTLY 21 ordered nonzero 4-tuples obeying (1):
- THREE choices with all four colours identical;
- THREE choices of an unordered PAIR of colours, times
  SIX ways to assign two of each on four ordered edges:
  3 * 6 = 18.

No 3+1 and no 2+1+1 patterns satisfy XOR=0.
The argument uses the four-edge boundary size, not bounded
treewidth, genus, a snark hypothesis or special graph family.

**Proven all simple cubic graphs**, subject only to the
stated four-edge cut.

## 2. Exact count contraction and SAT witness gluing

For each boundary colour tuple a in H_nonzero^4 let
  L_S(a)
be the number of proper colourings of the *S-side four-pole*
obtained by taking all edges with both endpoints in S, adding
a dangling boundary half-edge at each original crossing
incidence, and pinning those half-edge colours to a.
Define L_T analogously with the SAME edge order.

A global proper 3-edge-colouring restricts uniquely to
one pair of half-pole colourings with identical cut colours.
Conversely, each such pair glues to exactly one global
proper colouring: at every vertex the three incident
colours remain a permutation of (0,1,2).

Therefore there is a **sign-free exact all-input identity**:

   #Col3(G) = sum_{a in allowed21} L_S(a)*L_T(a).       (2)

Even when multiple cut edges meet the same boundary vertex,
the formula works: the half-pole vertex checks account
for repeated port vertices and all three local slots.

The SAT criterion is that at least one of those 21 products
is strictly positive. With a representative witness for
each nonzero half-pole signature entry, a chosen matching
boundary tuple glues in O(|V|+|E|) time. A global
vertex-by-vertex independent verifier checks the result.

Neither L_S nor L_T is assumed easy to calculate.

**Important:** this is classical binary-flow parity /
multipole transfer machinery; no priority is claimed.
It is different from the previous THREE-edge cut 1/6
scalar product formula because four-edge interfaces have
genuinely different possible boundary signatures.

## 3. A deterministic polynomial cyclic 4-cut finder

On a simple cubic graph with n vertices, m=3n/2 edges:
enumerate all unordered four-edge subsets Q of E.
For each, temporarily remove Q, run DFS/BFS from a fixed
root, and let S be its reachable vertex set. If the
resulting cut delta(S) has exactly four edges, both
shores have at least two vertices and each induced shore
contains a cycle, output it.

Every *connected-shore* cyclic 4-edge cut is detected:
when Q equals its crossing edge set, removal disconnects
the two connected cyclic shores, so the reachability
partition returns exactly one of the shores.

The straightforward implementation runs in

    O(C(m,4) * (n+m)) = O(n^5)

operations on O(log n)-bit vertex and edge indices.
It does not find a magical separator in arbitrary
cyclically 5-edge-connected cubic graphs: a return of
NONE is valid and may leave a hard SAT or UNSAT core.

## 4. What this does NOT prove

The dimension of a SINGLE four-edge cut boundary signature
is only 21, but computing each 21-entry half-pole
signature exactly from a large arbitrary component is
itself a counting/search problem, and the provided oracle
uses exponential backtracking. Neither the total number
of separators nor a proposed compression of *multiple*
simultaneous interfaces is automatically polynomial,
because many boundaries can coexist and grow in effective
width.

The previous Kettani/treewidth audit produced LEGAL
unbounded-treewidth SCL graphs, so no universal
bounded-width decomposition assumption is permitted.

A deterministic polynomial-time evaluation of arbitrary
four-pole signatures, plus valid compositional
compression for all graphs, could be decisive, but it
has NOT been established. Likewise a graph with no
eligible four-edge cut cannot be declared SAT or UNSAT.

## 5. Executable independent finite checks

    python experiments/r5_universal_cubic_four_cut_21_state_interface.py

The test constructs simple cubic graphs by removing two
vertex-disjoint edges on each of two source graphs and
reconnecting the eight half-edges to form four cut edges.
It checks all 81 boundary colour tuples, verifies that
only the 21 XOR-zero tuples can have nonzero signatures,
independently counts the whole joined graph by ordinary
edge-colouring backtracking, compares to (2), and tests
witness gluing. It also independently re-discovers a
cyclic four-edge cut on each joined graph.

Source controls: K4, K3,3, cube Q3 and Petersen;
joins: K4+K4, K4+K3,3, K3,3+K3,3, K4+cube, K4+Petersen.

This is finite proof replay only; its colour-count
component has exponential worst-case time.

## 6. Gate ledger

ALL_CUBIC_4EDGE_BOUNDARY_21_LABELS = PROVED_ALL_4CUTS.
FOUR_POLE_SIGN_FREE_COUNT_CONTRACTION = PROVED_ALL_4CUTS.
FOUR_POLE_SAT_WITNESS_GLUE = PROVED_ALL_4CUTS.
CYCLIC_FOUR_CUT_POLYNOMIAL_DETECTION = PROVED_O_N5.
CORE_FOUR_POLE_SIGNATURE_POLYNOMIAL_EVALUATION = NOT_CONSTRUCTED.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

Reference for binary 4-flow / 3-edge colour equivalence:
I. Holyer, `The NP-Completeness of Edge-Coloring`,
SIAM J. Comput., 10(4):718-720, 1981, DOI:10.1137/0210055.
