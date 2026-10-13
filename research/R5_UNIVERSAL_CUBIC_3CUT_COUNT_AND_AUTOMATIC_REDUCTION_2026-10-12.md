# R5 — Polynomial Nontrivial 3-Cut Discovery and Exact Cubic Colour Count Factorization

Date: 2026-10-12 (Europe/Kyiv). Research successor stacked onto
PR #515 / checked parent f91ed13f23f027277aeda85ec9b8cbbe1b8b3e8f.
PR #516 research-only. **No universal polynomial SCL algorithm obtained.**

## I. Theorem: factorization of exact labelled 3-edge-colourings

Let G be a connected simple 3-edge-connected cubic graph. Suppose
delta(S) is a nontrivial three-edge cut with both |S|>=2 and
|V-S|>=2. Form G_S and G_T by removing the cut edges, and capping
each shore with a fresh degree-three vertex whose three neighbours
are the three distinct boundary endpoints.

The three cut edges cannot share an endpoint on a shore:
if exactly two met a shore vertex, moving that vertex across the
cut would turn a 3-cut into a 2-cut, contradicting 3-edge
connectivity. If all three met one endpoint, that shore would
be a singleton since the vertex is cubic, contradicting
nontriviality. Thus the capped G_S and G_T are simple cubic.

**Exact identity, all graphs with this promise:**

    #Col3(G) = #Col3(G_S) * #Col3(G_T) / 6.

The counts use three FIXED, distinguishable colour names.

**Proof:** Identify the three colours with nonzero F2^2 elements.
At each cubic vertex, conservation of the two-bit flow is equivalent
to all three incident colours being different. Sum conservation
over S; internal edges cancel in F2^2, so the XOR of the three
boundary colours is zero. Because they are all nonzero, the three
boundary colours are pairwise distinct.

Every colouring of each capped graph gives an ordered permutation
of the three boundary colours. For each of the six permutations,
the number of colourings of G_S with that exact boundary assignment
is #Col3(G_S)/6, because global permutation of colour names is a
free and transitive action on all six possible boundary labels.
Likewise for G_T.

When joining shores, colourings must agree on the three boundary
edges. Thus six identical products contribute:
    6 * (#Col3(G_S)/6) * (#Col3(G_T)/6)
    = #Col3(G_S)#Col3(G_T)/6.
No double counting, no missing assignments, no existential gadget.
A witness for each cap can be glued by the unique S3 permutation
on one side to agree on the three crossing edges; the resulting
global 3-colouring is directly checkable in O(m) time.

## II. Polynomial discovery of a *nontrivial* three-edge cut

Given connected simple cubic 3-edge-connected G on n vertices,
enumerate all ordered disjoint vertex pairs {a,b}, {c,d}.
For each such pair-of-pairs run an integer-capacity max-flow with
unit capacities on original undirected edges, super-source joined
with capacity m+1 to a,b and c,d joined with capacity m+1 to
super-sink. If the max flow is exactly 3, take the residual
source-reachable shore S. It has at least two vertices on each
side, and exactly three crossing edges.

There are O(n^4) pair-of-pairs. With adjacency matrix residual
capacity and BFS augmenting paths, each flow call builds an
O(n^2) residual array and tests no more than four augmentations:
for a 3-cut, flow is 3 and the fourth path is absent; if a
fourth path exists, discard that pair immediately. Each BFS
takes O(n^2), so one test O(n^2) time, total O(n^6)
arithmetic operations on O(log n)-bit integers in this
unoptimized implementation (bound is deliberately loose).

**Completeness of search:** if a nontrivial 3-cut exists, choose
two distinct vertices inside S and two outside. That anchored
mincut is <=3. Since G is 3-edge-connected it is >=3, so the
maxflow exposes some nontrivial three-edge cut. Conversely, any
returned cut is independently verified against the input edges.

A 1- or 2-edge-cut graph is outside the theorem's connectivity
promise; general recursive software must route such cases via a
separate sound treatment, never apply the 1/6 factor blindly.
A graph with no nontrivial 3-cut is an unresolved core, NOT
automatically SAT or UNSAT.

## III. Recursive factorization and the real bottleneck

Recursively split every nontrivial 3-cut. For t capped terminal
cubic graphs (leaves), the exact count is

    #Col3(G) = prod_{i=1}^t #Col3(H_i) / 6^(t-1).

The product identity follows inductively and the witness
permutations lift along the decomposition tree.
Each split produces strictly smaller capped graphs: on
a nontrivial 3-cut, each shore has at least three vertices
in a simple cubic 3-edge-connected graph; each cap adds one
vertex, so each child has at most n-1 vertices. At most
O(n) splits occur and the factoring search has polynomial
total runtime apart from the unresolved core-solving calls.

**CRITICAL:** No polynomial-time algorithm is established for
the irreducible terminal cores. This decomposition does not
imply a polynomial-time 3-edge-colouring algorithm for all
simple cubic graphs, and hence does NOT imply P=NP.

The JANUS target is the WHOLE square+cubic+linear SCL Exact-One
class, not just the cubic graph image. A future polynomial
solver for *all* cubic 3-edge-colouring inputs would nevertheless
be sufficient for SCL: SCL lies in NP and cubic 3-edge-colouring
is NP-complete (Holyer 1981), so there is a deterministic
polynomial Karp reduction from any pinned SCL decision formula
to cubic 3-edge-colouring. Apply the hypothetical polynomial
oracle to decide the original instance; recover a witness using
at most n further pinned decision queries, and verify A*x=1.
Thus no separate special-purpose SCL theorem is required AFTER
a genuinely universal polynomial cubic 3-edge-colouring decider.
The latter remains NOT CONSTRUCTED.

## IV. Exact independent checked controls

    K4 JOIN K4:          6 * 6 /6 = 6
    K4 JOIN K3,3:        6 *12 /6 =12
    K3,3 JOIN K3,3:     12 *12 /6 =24
    K4 JOIN cube:        6 *24 /6 =24
    K4 JOIN Petersen:    6 * 0 /6 = 0 (UNSAT)

Each combined graph was checked by direct graph colour enumeration
independent of capping. For all SAT cases the witness was
actually reassembled and checked edge-by-edge.

The automated polynomial finder also locates a nontrivial 3-cut
on every joined fixture, while correctly returning NONE for
K4, K3,3, cube, and Petersen. This is *finite* regression data
in support of the all-input combinatorial proofs above.

Executable:
    python experiments/r5_universal_cubic_three_edge_cut_factorization.py
    python experiments/r5_universal_cubic_nondegenerate_threecut_recognizer.py

CI:
    https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38181891687
    https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38181976426

Both runs SUCCESS. The code's direct exhaustive colour-count
oracle is explicitly worst-case exponential and used only as
a finite independent control.

## V. Literature and anti-duplicate

The parity lemma for 3-poles, colour permutation symmetry,
and small-cut decomposition of cubic graphs/snarks are
classical graph-colouring concepts. Do NOT claim priority.
Relevant source: R. Nedela and M. Skoviera, Decompositions
and reductions of snarks, Journal of Graph Theory (1996),
DOI: 10.1002/(SICI)1097-0118(199607)22:3<253::AID-JGT6>3.3.CO;2-7.
For complexity: I. Holyer, The NP-Completeness of
Edge-Coloring, SIAM J. Comput. 10(4), 1981,
DOI: 10.1137/0210055.

## VI. Gate ledger

CUBIC_NONTRIVIAL_THREE_EDGE_CUT_COUNT_DIVIDE_SIX = PROVED.
CUBIC_THREE_EDGE_CUT_SAT_WITNESS_GLUING = PROVED.
CUBIC_THREE_EDGE_CUT_DETECTION_POLYNOMIAL = PROVED_FOR_3EDGE_CONNECTED.
CUT_FINDER_AND_FACTOR_FIVE_JOINED_GRAPH_CI = SUCCESS.
UNIVERSAL_POLY_DECIDER_FOR_UNSPLITTABLE_CORES = NOT_CONSTRUCTED.
ALL_INPUT_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
