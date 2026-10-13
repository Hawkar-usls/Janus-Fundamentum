# R5 two-wire multipole gates and Kempe fan-out obstruction (2026-10-13)

Research PR #516. Original-source goal: a **uniform**, sound and complete,
bit-polynomial SolveLinearCubicXSAT for **every** legal square/cubic/linear
positive Exact-One instance. NOT CONSTRUCTED. P vs NP OPEN.

## Source context and honesty

Prior frozen results already give:
- J5/SCL90 UNSAT with an independently replayed original GF(3) Boolean
  polynomial-calculus degree-3 dual, hence native degree >=4;
- infinite native legal SCL90+9k families preserving that SAME bound >=4,
  not proving growth with k;
- exhaustive signed K4/SCL18 (216) and K3,3/SCL27 (1296), every UNSAT
  native degree <=2; unified successful CI #38386450371 on PR HEAD
  dca21e3afb38b2eac968ddb203594be615bc3409.
None of these supplies unbounded-degree hardness.

The external candidate is Conneryd–de Rezende–Nordström–Pang–Risse,
*Graph Colouring Is Hard on Average for Polynomial Calculus and
Nullstellensatz* (FOCS 2023, ECCC TR25-032, arXiv:2503.17022):
linear PC degree for suitable sparse random *vertex*-3-colouring systems.
A degree-preserving map from these exact polynomial systems to native
SCL is REQUIRED; an ordinary NP-hardness reduction is insufficient.
Field chosen for this experiment is GF(3), matching native J5 dual.

## Encoding

Identify 3 colours with the nonzero elements of H=GF(2)^2:
0 -> (1,0), 1 -> (0,1), 2 -> (1,1).
At any properly 3-edge-coloured cubic vertex, the three incident
colours are all distinct and their vector sum is zero.

For a 2-wire *ordered or unordered* pair (a,b) with a != b, encode
a 3-valued symbol as its MISSING colour
m(a,b)=a+b in GF(2)^2 (the unique third nonzero element).

For Boolean edge-colour indicators X_(port,c), the missing-colour
indicator has the exact **AFFINE** decoder

    P_c = 1 - X_(port1,c) - X_(port2,c).

Whenever the two ports meet at a cubic source vertex whose remaining
internal edge is t, the ORIGINAL Exact-One3 source row supplies
    P_c - X_(t,c) = -(X_(port1,c)+X_(port2,c)+X_(t,c)-1).
This is an exact degree-one polynomial identity, not merely a truth
table. Booleanity and one-hot for P follow from the corresponding
internal edge indicators and the literal old source generators.

## Universal F2^2 boundary conservation

THEOREM (classical colour parity): For any finite cubic multipole M
with 2k dangling semiedges, every proper 3-edge-colouring satisfies

    XOR_(all boundary semiedges s) colour(s) = 0 in H.

Proof: XOR all triples of incident colours at all internal vertices.
Each internal edge is counted twice and cancels, while each dangling
edge is counted once.

COROLLARY: If 2k ports are partitioned into k pairs, each pair of
distinct colours, and z_i is the missing colour of pair i, then

    XOR_i z_i = 0.

This is mandatory for EVERY cubic topology, regardless of its size,
internal cycles, or choice of gadget; it may not be sufficient for
realizability by a particular gadget.

Consequences:
* For k=2, missing colours z_1=z_2: a 4-pole with two distinct
  two-wire bundles CANNOT realize z_1 != z_2.
* For k=3, z_1,z_2,z_3 must be the three DISTINCT nonzero colours.
* For any odd k, it is impossible that all z_i are the same.

## Constructive gates, exact boundary relations

### Four poles: equality of two coded symbols

Remove two adjacent vertices from K4; remain two internal vertices
u,v connected by one edge, with two dangling semiedges at each.
At u and at v the dangling colours are distinct. Both pairs miss
exactly the colour of internal edge uv. Conversely, for each missing
colour and each independent orientation of the two remaining colours
on each side, the internal colouring is valid.

EXACT relation: z_left=z_right; precisely 3 * 2 * 2 = 12 ordered
boundary signatures. Exhaustive 3^5=243 tests return 12 valid.

### Six poles: all-different of three coded symbols

Remove two same-partition vertices from K3,3. The remaining graph is
a degree-3 centre c linked to leaves u,v,w, each leaf with two dangling
ports. Each leaf pair misses the colour of the corresponding centre
edge. The three centre edges are all different, and conversely every
permutation of three missing colours admits all 2^3 independent
port orientations.

EXACT relation: AllDifferent(z_u,z_v,z_w); 3! * 2^3 = 48
proper boundary colourings; 3^9=19683 exhaustively checked.

A ternary all-different gate is NOT the missing six-way copier and
does NOT yet provide a graph-vertex-3-colouring-to-native-SCL reduction.
Closing two arbitrary distinct 2-wire ports with a standalone
2-pole is impossible: colour parity for k=1 demands its two port
colours equal.

### Pure two-wire fan-out obstruction (all k>=3)

THEOREM: No **colourable** finite cubic multipole can require that k>=3
designated disjoint two-port bundles each consist of distinct colours
and ALL k bundles encode the SAME missing colour in EVERY proper
edge-colouring.

PROOF: Fix any proper colouring satisfying the alleged relation.
By global permutation of colours, each pair is (A,B) in some order,
and missing colour is C.
If k is odd, XOR_i C = C != 0, contradicting parity.
If k is even >=4, consider the A/C-coloured subgraph. Each internal
degree-3 vertex has one A edge and one C edge; it is a union of
alternating cycles and paths whose dangling endpoints are exactly
the k A-coloured ports (there are no C ports). Choose one path;
swap A<->C along that path. This is still a proper 3-edge-colouring
of the SAME multipole. Exactly two A-coloured boundary ports become C.
They belong to distinct bundles (each bundle initially had only one
A port). Those two bundles now miss A, and the remaining k-2 bundles
still miss C. Since k-2>0, the same-colour requirement is violated.
Contradiction.

This strengthens the earlier one-wire fan-out obstruction. It rules
out exactly **pure independent two-wire missing-colour copies**. It
does NOT disprove all mixed-state multiwire codes, overlapping port
schemes, charged/anchored constraints, nonlocal constructions, or
arbitrary algebraic low-degree reductions.

## Native SCL closure sanity test

Take TWO copies of the six-pole star and glue their six dangling
edges to form an alternating 6-cycle between the three leaves of
each star. The closed graph has 8 vertices, 12 edges and is simple,
cubic, and 3-edge-colourable (the cube graph).

Apply the ORIGINAL Holyer translation:
- one variable x_(e,c) for each edge e and colour c;
- one Exact-One3 row over the three colours of each edge;
- one Exact-One3 row over three incident edges for every (v,c).

The resulting 36x36 ORIGINAL source has row size 3, column degree 3,
all distinct row pair intersections <=1, and 24 proper graph edge
colourings, each independently checked as a native exact-one witness.
This demonstrates valid closed, unpinned native sources; the isolated
open multipoles are **not themselves closed SCL instances**.

## Explicit next gates A-D

A. Match the precise base polynomial encoding and lower-bound
   conditions from the published graph-vertex colouring PC paper.
   SOURCE-CODING REVIEW REQUIRED.
B. A general cubic-graph reduction from that bounded-degree
   vertex colouring problem must bypass *both* one-wire and
   two-wire pure fan-out. NOT CONSTRUCTED.
C. The local affine missing-colour decoder P_c has substitution degree
   1 and literal source identities at gate vertices. **PROVED LOCAL**.
   An all-gadget low-degree back-simulation with uniform constants
   k,C for the BASE vertex colouring equations is OPEN.
D. Native UNBOUNDED GF(3) PC DEGREE via D(N)/k-C is UNPROVED.

Reproduce:
    python3 experiments/r5_universal_two_wire_multipole_parity_gates.py

Independent status:
- Structural parity and Kempe theorems: proofs above (symbolic).
- Finite k=2/k=3 exact gate enumeration: executable assertions.
- K4/K33 old finite exhaustive classifications: separate CI records.
- No new global proof or polynomial solver claimed.

GATES:
  FOUR_POLE_TWO_WIRE_EQUALITY = PROVED
  SIX_POLE_TWO_WIRE_ALLDIFFERENT = PROVED
  GENERAL_MULTIPOLE_GF2X2_COLOR_CONSERVATION = PROVED
  PURE_TWO_WIRE_K_GE_3_MISSING_COLOR_FANOUT = REFUTED
  TWO_WIRE_DECODER_GF3_DEGREE1_LOCAL = PROVED
  GLUED_CLOSED_CUBE_NATIVE_SCL36 = TESTED
  GLOBAL_VERTEX_3COLOUR_TO_SCL_PC_TRANSFER = OPEN
  UNBOUNDED_NATIVE_GF3_PC_DEGREE = OPEN
  SolveLinearCubicXSAT = NOT_CONSTRUCTED
  P_VS_NP = OPEN
