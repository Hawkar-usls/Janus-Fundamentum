# R5 — Atomic-Core Global Coverage: 3-Edge-Connected Tanner SCL Is NP-Complete

Date: 2026-10-12 Europe/Kyiv. Frozen source:
Hawkar-usls/Janus-Fundamentum, research stacked DRAFT PR #516.
Authority: exact all-input mathematical reduction plus replayable
finite controls, NOT a universal polynomial algorithm.

## Scientific target

`SolveLinearCubicXSAT` must return SAT+ORIGINAL verified Boolean
witness or UNSAT for EVERY legal n-by-n square/cubic/C4-free
Positive Exact-One source in uniform deterministic n^O(1) BIT time.

**UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED; P_VS_NP=OPEN.**

The previous checkpoint built a complete (potentially exponential)
four-state 2-port signature algebra and proved that computing
arbitrary cut-open interior signatures is NP-hard. This checkpoint
directly targets the remaining connected *atomic* Tanner sources
that have NO 2-edge cut at all.

## 1. All-input atomic Tanner theorem for connected cubic graph images

Let G=(V,E) be ANY connected finite simple cubic graph (G itself
may contain a graph bridge). Define the exact original SCL Holyer
embedding A_G, as implemented and independently checked in
`experiments/r5_universal_cubic_edgecolor_direct_scl_bridge.py`:

  Boolean source variables X_(e,c) for e in E and c=0,1,2.
  For each original graph edge e:
       one source row R_e = EXACTONE(X_(e,0),X_(e,1),X_(e,2)).
  For each original graph vertex v and colour c:
       one source row R_(v,c) = EXACTONE(X_(e,c): e incident v).

Each SCL row and each SCL column has exactly three ones.
Every pair of SCL rows shares at most one column (simple
cubic graph), hence the source is legally C4-free/linear.
For |V|=N, |E|=3N/2=M, the square source has
n=3M=M+3N=9N/2 rows and columns. A satisfying original
Boolean source is in bijection with a properly labelled
three-edge-colouring of G.

### THEOREM

**For every CONNECTED simple cubic G, the original Tanner
bipartite incidence graph T(A_G) has edge connectivity EXACTLY 3.**

Formal proof independent of finite tests:

(a) For arbitrary two original graph edges e,f, since G is
connected, its line graph is connected. Choose a simple edge
adjacency walk e=e0,e1,...,ek=f. If e_i and e_(i+1) meet at
original vertex v_i, then for each fixed colour c,

  R_e, X_(e0,c), R_(v0,c), X_(e1,c), ...,
  R_(v_(k-1),c), X_(ek,c), R_f

is an actual Tanner path (alternating source rows/columns).
The three paths c=0,1,2 share NO Tanner edges, because
all colour-labelled X and R_(v,c) edges are distinct.

Therefore any Tanner edge cut separating R_e from R_f
contains at least three edges. For a hypothetical cut
of size <=2, ALL original graph-edge source-row nodes
R_e must lie on the SAME side.

(b) Every original vertex-colour row R_(v,c) has three
distinct incident Tanner variables X_(e,c), corresponding
to the THREE distinct original graph edges e touching v.
For each such e the length-two path

    R_(v,c) -- X_(e,c) -- R_e

joins R_(v,c) to the shared R_e side. These three paths
are edge-disjoint. Thus any Tanner edge cut of size <=2
must also place EVERY vertex-colour source row R_(v,c)
on the same side as all R_e.

(c) Finally each variable-column Tanner node X_(e,c) is
connected by THREE distinct Tanner edges to exactly
R_e, R_(u,c), R_(v,c) for e={u,v}. These three
source-row neighbours already lie on the same side.
If X_(e,c) were across the cut, at least three
boundary edges would be required, contradiction.

Consequently T(A_G) has no nontrivial cut of size 1 or
2; its min edge-cut is >=3. As every Tanner vertex
has degree three, min cut <=3 by isolating any
vertex. Hence

       lambda(T(A_G)) = 3.

This remains TRUE EVEN IF original cubic G HAS A BRIDGE:
the three colour layers protect the SCL Tanner structure.
It is misleading to transfer cuts of original G to
size-two Tanner cuts.

### Executable independent witnesses

Code:
`experiments/r5_universal_atomic_holyer_tanner_three_edge_npcomplete.py`

It explicitly constructs THREE original-source Tanner paths
for EVERY pair of original edge-row nodes on the finite
control families, independently checks that each path
uses only actual source matrix incidences and verifies
that all three are edge-disjoint. A completely separate
existing Tanner graph cut enumerator searches ALL
one-edge and two-edge deletions and certifies that
none disconnects the control source. The mathematical
proof above covers ALL connected simple cubic G,
not merely tested values.

## 2. Fully constructive connected-cubic hardness

Published starting theorem: Ian Holyer,
*The NP-Completeness of Edge-Coloring*,
SIAM Journal on Computing 10(4), 718-720 (1981),
DOI 10.1137/0210055.
It establishes NP-completeness of 3-edge-colorability
for cubic graphs.

To avoid assuming that Holyer's theorem already
restricts its source to connected cubic graphs,
construct a polynomial source-connectedization:

Given a disconnected simple cubic graph G with
components G_1,...,G_t, choose a NON-BRIDGE edge
(a,b) in G_1 and (c,d) in G_2. Every finite
connected cubic graph contains at least one cycle,
hence such edges can be found by polynomial
reachability. Delete these two edges, and add
crossing edges (a,c) and (b,d). The joined
graph remains simple cubic, is connected across
these two old components, and has unchanged
numbers of vertices/edges. Iterate at most t-1
times. Each output stays simple cubic.

At each join the 2-crossing-edge cut between the
two previous components has even vertex count
on one side, since 3|S|=2|E(S)|+2. In any proper
3-edge-colouring, each colour occupies a perfect
matching and the number of edges of that colour
crossing any cut has parity |S|. Hence for this
two-edge cut the TWO crossing edges share the
SAME colour.

Replacing the two crossings by the old internal
edges with that same colour recovers valid
independent 3-edge-colourings of the old
components. Conversely independently permute
the three colour NAMES in one component to
make the two chosen old edges have the same
colour; replace them by crossing edges with
that colour, giving a valid colouring of
the joined graph.

Both directions are constructive and
witness preserving; repeated joins are
polynomial-time and size preserving.
Actual executable regression independently
checks colour class legality at EVERY
original cubic graph vertex in forward and
reverse transitions.

Thus 3-edge-colourability of connected
simple cubic graphs remains NP-complete
under polynomial many-one reductions.

## 3. Main theorem: the atomic SCL decision class is NP-complete

Compose:

  general cubic 3-edge-colouring
       -> connected cubic 3-edge-colouring
       -> legal Holyer SCL A_G
       -> Tanner graph edge connectivity 3.

The first arrow is exact polynomial connectedization;
the second is the source witness-bijective positive
Exact-One Holyer embedding; the final arrow is the
all-input 3-edge-connectivity theorem, with no
additional computation required.

This proves that the **promised problem** of deciding
SAT on legal square/cubic/linear SCL inputs whose
bipartite Tanner graph is 3-edge-connected is
NP-hard. It belongs to NP because every Boolean
SAT witness is polynomial-size and verifiable against
the original source. Hence it is NP-complete.

No simple two-port or connected-component
preprocessing can eliminate this hardness.
A globally polynomial solver for these atomic
sources would imply P=NP, exactly like a general
unrestricted SCL polynomial solver.

THIS IS A HARDNESS-PRESERVATION / COVERAGE NO-SHORTCUT
THEOREM, NOT A PROOF THAT P!=NP.

The HOLYER image witnesses show NP-completeness for
3-EDGE-CONNECTED Tanner sources; this does NOT show
NP-completeness under the STRONGER exclusion of
nontrivial three-edge cuts. Do not silently elevate
the edge-connectivity-3 theorem to cyclically
four-edge connectivity or irreducibility under
every possible 3-port algebra.

## 4. CI evidence and frozen cross-family tests

CI final with path construction, min-cut
enumeration, graph component connectedization,
independent SAT witnesses and noncolourability:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38259919419
SUCCESS.

Connected cubic source graphs all producing
exact atomic Tanner SCL:

| Graph G | SCL n | True decision | Tanner 1/2 cuts |
|---|---:|---|---|
| K4 | 18 | SAT | 0 |
| K3,3 | 27 | SAT | 0 |
| Cube graph | 36 | SAT | 0 |
| Petersen | 45 | UNSAT | 0 |
| Connected cubic G with bridge | 45 | UNSAT | 0 |

Connectedized pairs tested:

| Components before switch | New SCL n | Source status | Tanner 1/2 cuts |
|---|---:|---|---|
| K4 + K4 | 36 | SAT | 0 |
| K4 + Petersen | 63 | UNSAT | 0 |
| K3,3 + K4 | 45 | SAT | 0 |

For each positive switch source the test
constructs source-correct edge-colouring
both FORWARD (local independent colour
renaming followed by two-edge switch) and
BACKWARD (two-cross-edge colour parity and
restoration of the original local edges).
A verified SCL witness is equally available
by the already checked colour→Exact-One
source translation.

Separate source alignment control is
the prior basic Holyer original/SCL witness
bijection and full Tanner 1/2-cut recognizer;
not a guess based on benchmark filenames.

## 5. Next admissible atomic algorithm target

We need a single source-preserving all-input
mechanism beyond merely splitting small cuts:
for any connected simple cubic G, the exact
direct SCL A_G of size n must receive either

   (i) SAT + original 0/1 witness, or
   (ii) UNSAT with a source-correct proof,

within a UNIFORM n^C worst-case bit budget
for fixed C independent of input/family.

Via the graph embedding, this amounts to
solving full cubic three-edge-colourability;
a new polynomial-time proof would suffice
for P=NP, but no such proof is known.

Candidate proof routes to attack, with
NO authority until a theorem:

- deterministic algebraic circuit compression
  for two binary cycle-space vectors with
  full edge support (nowhere-zero F2^2 flow);
- universal source-independent reduction
  of exact support to a polynomial bit-length
  certificate of SAT/UNSAT with computable
  polynomial normal form;
- source-complete polynomial time witness
  extraction following the shared no-good
  and algebraic expert closure.

Testing families, symmetry, modular moments,
perfect matching subsets and finite CI
runs cannot establish worst-case polynomiality.
Existing failed Pfaffian and fixed modular
count filters MUST remain negative controls.

An NP-hard subclass does not imply no
polynomial algorithm; it states exactly
the required global mathematical breakthrough.

## Gate ledger

CONNECTED_CUBIC_SOURCE_CONNECTEDIZATION = PROVED.
CONNECTED_CUBIC_SOURCE_SAT_WITNESS_TRANSPORT = VERIFIED_CI.
HOLYER_SOURCE_SCL_BIJECTION = PREDECESSOR_PROVED.
ALL_CONNECTED_HOLYER_TANNER_EDGE_CONNECTIVITY_3 = PROVED.
THREE_INDEPENDENT_LAYER_PATH_CONSTRUCTION = VERIFIED_CI.
ATOMIC_TANNER_3_EDGE_CONNECTED_SCL_SAT = NP_COMPLETE.
ATOMIC_TANNER_POLY_TIME_SAT_AND_UNSAT_COVERAGE = OPEN.
UNIFORM_ALL_INPUT_POLY_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
