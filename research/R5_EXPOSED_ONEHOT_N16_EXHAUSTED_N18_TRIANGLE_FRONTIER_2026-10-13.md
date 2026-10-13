# R5 — Complete exact connected simple ordinary 6-pole classification through n=16 and structural triangle-shrink filter

Scientific date: 2026-10-13 (Europe/Kyiv). Draft PR #516;
do not edit main. Earlier checkpoints n<=14 and original GF(3)
Boolean PC decoder remain authoritative.

## Critical scientific contract

Goal is STILL a total, sound, complete UNIFORM worst-case
BIT-polynomial solver `SolveLinearCubicXSAT` for ALL original
square/cubic/linear positive Exact-One source instances, returning
original SAT witness or genuine UNSAT. NOT CONSTRUCTED. P vs NP OPEN.
A finite exclusion of one semantic gadget does NOT establish
polynomial solvability, and does NOT establish native unbounded
Polynomial Calculus refutation degree.

## 1. Frozen original problem

An ordinary open cubic sixpole M has connected SIMPLE internal graph
G on n vertices (each degree 1..3) and six labelled semiedges
completing all vertices to degree3, without free semiedge-to-semiedge
edges; its n vertices and m original edges obey
    2m+6=3n.
Thus n is even. For one of the 15 partitions of the 6 boundary
semiedges into three pairs, each Boolean bit t_i is 1 iff the two
ACTUAL semiedge three-edge-colours agree. Exposed ExactOne means
the EXACT support of the three bits is
    {100,010,001}
with all three states realized and every other state forbidden.

## 2. NEW completed n16 FULL canonical isomorphism-free census

Stand-alone source:
`experiments/r5_universal_exposed_exactone_n16_anchored_rejection.py`.
Workflow:
`.github/workflows/r5-exposed-exactone-n16-anchored.yml`.

Run [#38408523974](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38408523974)
**SUCCESS**, EXACT commit
`c5821da3cdf09fb159eff7554461367d637028c4`.

Canonical generator:
    nauty-geng -c -q -d1 -D3 16 21
one representative of EVERY simple connected 16-vertex, 21-edge,
min-degree>=1 max-degree<=3 graph, i.e. six dangling semiedges
by deficit counting. Check ALL 15 physical port-pairing interfaces
of every such graph.

EXACT independent CI log:
    N16_SUMMARY {
      graphs: 965223,
      status_rejected: 952019,
      status_uncolourable: 13204,
      anchored_full_assignments_seen: 7885254,
      boundary_tuples_seen: 13047815
    }
    N16_GRAPH6_SHA256 =
      60593e0507b676aab66c906c49edaabfd4ab0b90ac22999e03930cdf7b6e9be4
    N16_CANDIDATE_COUNT = 0
    NO_OPEN_EXACTONE_N16_EXHAUSTIVE_FINITE_CENSUS

Meaning of `status_rejected`: these 952019 interiors admitted
proper internal 3-edge-colourings but EACH of their 15 potential
pairings failed to realize exactly target support.
The other 13204 interiors were internally UNCOLOURABLE and
cannot yield any required target state.

### Exhaustiveness despite exact early rejection

Global S3 permutation of physical 3-edge colours preserves
all pair-equality bit predicates. Every proper colouring can be
permuted to make the FIRST internal edge colour0. Therefore
enumerating FIRST-edge-colour-zero representatives is COMPLETE
for every Boolean interface projection.

For each chosen port-pairing, the checker stores an actual
physical boundary state with a forbidden bit tuple, permanently
disqualifying that pairing. It halts graph DFS early only if ALL
15 pairings have individual genuine forbidden state witnesses.
If any pairing never acquires such a witness, all remaining
normalized proper physical colourings are enumerated to
completion and the nonrealization of at least one of the
three necessary singleton states is established. Therefore
NO exact-one candidate can be pruned by the optimization.

Counts `7885254` and `13047815` describe assignments/states
ACTUALLY VISITED across the bounded early-stop checks, NOT the
total number of all possible full colourings of all graphs and
NOT a number of globally distinct abstract boundary states.
Keep the provenance of those counters precise.

## 3. Combined complete exact finite theorem n<=16

Older full physical signature/port pairing runs:
- n=4: 2 nonisomorphic interiors; 30 pairings; zero exactone;
- n=6: 9 / 135 / zero;
- n=8: 63 / 945 / zero;
- n=10: 551 / 8175 / zero; 6 noncolourable;
- n=12: 5741 / 84780 / zero; 89 noncolourable;
  combined CI #38402140506 SUCCESS;
- n=14: 69602 / 1,027,845 colourable-interface pairings /
  zero; 1079 noncolourable; CI #38405242305 SUCCESS;
- n=16: 965223 / 14,280,285 colourable-interface pairings /
  zero; 13204 noncolourable; CI #38408523974 SUCCESS.

TOTAL n=4 through16:
 1,041,191 nonisomorphic simple connected interior graphs;
 1,026,813 colourable graphs;
 14,378 uncolourable interior graphs;
 15,402,195 EXACT physical-pair logical interface checks;
 ZERO exactone candidate.

n=2 connected sixpole impossible: by counting m=0 and n=2,
so interior would be disconnected. Odd n impossible by parity.

**PROVEN FINITE THEOREM**:
No simple connected ordinary 6-pole with n<=16 internal vertices,
no free semiedge-to-semiedge segment, and 3 disjoint colour-equality
port pairs realizes the exact relation {100,010,001}.

COROLLARY:
If an exposed exactone sixpole exists within this EXACT
structural class, it has at least 18 internal vertices.

This statement DOES NOT exclude other semantics, disconnected
gadgets, multigraph interiors, extra ports, graph size>=18,
or global polynomial-degree reductions that do not use one
constant-size standalone exact-one sixpole.
It is NOT a general P vs NP or all-instance SCL statement.

## 4. Reuse existing triangle expansion / retraction theorem

Already proven in this PR:
`research/R5_INFINITE_3EDGE_CONNECTED_NATIVE_SCL_NO_GF3_DEGREE3_TRIANGLE_RETRACTION_2026-10-13.md`,
authenticated CI #38384437400 SUCCESS. The local Delta-Y
triangle expansion and inverse contraction preserve proper
3-edge colourability by cubic odd 3-edge cut parity.
At the ORIGINAL native SCL polynomial level, the existing
degree-one literal variable substitution maps every inflated
source row and Boolean generator to original source generators.
This does NOT cause degree to grow, nor prove any unbounded degree
lower bound.

NEW APPLICATION TO OPEN SIXPOLES:
Suppose an internal triangle T of an open simple connected sixpole
has three outward (ordinary or dangling) incidences and contracting
T to a single trivalent vertex yields a SIMPLE connected smaller
sixpole. Then any proper original colouring has pairwise distinct
colours on those three incidences (cubic odd parity).
Conversely every permutation of 3 DISTINCT outgoing colours has a
UNIQUE proper colouring of the three internal triangle edges:
each interior edge receives the colour of the OPPOSITE outward
incidence. Thus contraction preserves the EXACT set of SIX
PHYSICAL boundary colour tuples, with port labels mapped to the
new vertex slots. In particular ALL 15 encoded Boolean pair
relations are exactly preserved.

This is a universal exact-source proposition for every valid
simple contraction, not a mere numerical observation. It
isomorphically identifies full proper physical source colourings
across triangle contraction, and in closed graphs it reuses the
existing degree-one GF(3) source PC retraction.

Consequently a hypothetical **n=18** exposed ExactOne gadget
CANNOT have ANY *internally* contractible triangle whose contraction
remains simple/connected: it would yield an exactone n=16 sixpole,
contradicting the proven finite theorem above.
A triangle whose contraction creates PARALLEL edges (e.g. a
diamond topology) is not excluded by this corollary;
neither are triangles involving a newly attached STAR6 completion
rather than being wholly inside the original sixpole.

Independent source physical signature regression:
`experiments/r5_universal_sixpole_internal_triangle_shrink_exact_port.py`.
CI [#38415793609](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38415793609)
SUCCESS before small source message refinement:
- n=6: 9 interiors / 4 eligible triangles;
- n=8: 63 interiors / 36 eligible triangles;
- n=10: 551 interiors / 388 eligible triangles;
  **428** fully physically checked simple contractible
  triangles across 623 graphs, all full boundary colour tuple
  sets matched after precise port remapping.

## 5. Complementary six published nontrivial 20vertex snarks

A. D. Forbes, *Snark Designs*, arXiv:1207.3032, Section 4
(source PDF https://oro.open.ac.uk/56584/1/1207.3032.pdf)
gives the **six nontrivial** 20-vertex snarks S1..S6.
See paired memo
`research/R5_ALL_SIX_20_SNARKS_INDUCED_CLAWS_EXACTONE_AUDIT_2026-10-13.md`.
Original full source audit #38414354891 SUCCESS, unified independent
J5 + S1..S6 + original GF3 decoder #38415286627 SUCCESS:
6 x 20 induced-claw deletions x15 port-pairings=1800,
ZERO exactone. This supports a targeted independent check,
not the complete n16 census (which is much stronger and
also covers all relevant reducible/star-completion scenarios).

## 6. New frontier and strict statuses

The full-size structural question for the *specified* local gadget
moves to n>=18. A source-minimal such candidate must additionally
be irreducible under every SIMPLE internal triangle contraction.
Useful next exact targeted strategy: source-specific full-colour
search over triangle-contraction-irreducible n18 interiors,
or a new all-size same-interior Kempe path-groupoid invariant,
or a different multiport/mixed-code architecture bypassing
the excluded pure two-wire sixpole interface.

But this is STILL only a reduction strategy. To import a published
unbounded polynomial-calculus lower bound from graph vertex
3-colouring / hard Tseitin, a complete Boolean source-variable
substitution of constant degree and a polynomial-calculus
back-simulation of EVERY original base constraint into EVERY
native target source constraint with UNIFORM k,C is indispensable.

GATES:
- NAUTY_EXPOSED_EQUALITY_ONEHOT_N<=16 = REFUTED_FINITE_CI_SUCCESS
- MIN_INTERNAL_VERTICES_IF_EXISTS = >=18_WITHIN_THIS_CLASS
- 20VERTEX_FORBES_NONTRIVIAL_SIX_SOURCES = REFUTED_FINITE_CI_SUCCESS
- ALL_SIZE_CONTRACTIBLE_TRIANGLE_SOURCE_RETRACTION = PROVED_CONDITIONAL
- 428_SMALL_CONTRACTIBLE_TRIANGLES_FULL_PHYSICAL_REPLAY = CI_SUCCESS
- ALL_SIZE_EXPOSED_ONEHOT_NONEXISTENCE = OPEN
- ACTUAL_EXPOSED_ONEHOT_GADGET = NOT_CONSTRUCTED
- ALL_BASE_CONSTRAINT_GF3_PC_BACKSIM = NOT_CONSTRUCTED
- UNBOUNDED_NATIVE_GF3_PC_REFUTATION_DEGREE = OPEN
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
