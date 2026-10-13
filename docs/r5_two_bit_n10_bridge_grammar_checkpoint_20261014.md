# R5 — TWO-BIT physical cubic sixpole on 10 vertices, and complete bridge 2+4 / 3+3 theorem

Date: 2026-10-14 (Kyiv). Branch: research/r5-kempe-coupled-involutions-20261013.
Executable: [r5_exactone_bridge_grammar_two_bit_n10.py](../experiments/r5_exactone_bridge_grammar_two_bit_n10.py).
Reference: Fiol and Vilaltella (2015), *Some Results on the Structure of Multipoles in the Study of Snarks*, EJC 22(1), #P1.45, DOI 10.37236/3629.

## Main result — genuinely physical GOOD-only TWO-BIT sixpole

There exists a connected SIMPLE cubic multipole on exactly TEN internal vertices 0,...,9, with twelve ordinary edges and SIX DISTINCT physical semiedge roots, whose full proper 3-edge-colouring equality-bit set is precisely TWO allowed Exact-One values:

    Bits(M)={100,010}, excluding 001,000,111 and all other non-onehot values.

This is not the full three-input Exact-One gadget, which requires three nonempty 36-state components, total 108 physical states. It is a strictly stronger intermediate construction than the previous real n=14 ONE-BIT example.

### Complete replayable physical graph

Internal ordinary edges (listed sorted, each distinct):

    (0,1) (0,6) (1,5) (2,4) (2,5) (3,5)
    (3,6) (3,9) (4,6) (7,8) (7,9) (8,9).

The six ordered physical semiedges are rooted at

    port_roots=(0,1,2,4,7,8).

Every root has ordinary degree 2 and exactly one dangling semiedge; each nonroot (3,5,6,9) has ordinary degree 3. The ordinary graph is connected and has no loops or multiple edges. The logical pairs use PORT INDICES (not graph vertex labels):

    ((0,2),(1,3),(4,5)),

so they correspond to physical root pairs ((0,2),(1,4),(7,8)).

Exhaustive and independent proper 3-edge-colouring DFS gives:

    physical 6-semiedge tuples:                 72
    full proper assignments on twelve edges:  72
    bit 100:                                  36
    bit 010:                                  36
    bit 001:                                   0
    forbidden bit 000:                         0
    forbidden bit 111:                         0
    each physical tuple's internal fibre:     exactly one.

This saturates BOTH realised onehot bits and has NO forbidden or extra Boolean states.

### Two literal full-colouring certificates

The following tuples order the 12 ordinary edges EXACTLY as listed in the complete physical graph above. Each tuple is a proper edge-colouring of the SAME graph; the six outer physical port colours are uniquely determined by the missing colour at each of the six distinct roots:

    bit 100
    ports:         (2,2,2,0,2,0)
    ordinary edges:(0,1,1,1,0,2,0,1,2,1,0,2)

    bit 010
    ports:         (2,2,0,2,2,0)
    ordinary edges:(0,1,1,1,2,0,2,1,0,1,0,2)

These are independently reproducible SAT witnesses of both realised truth values, not a substitute for checking the full 72-state relation.

### Two actual graph components

The 7-vertex 5-pole uses vertices 0,...,6, five semiedges at roots (0,1,2,3,4) and eight ordinary edges:

    (0,1) (0,6) (1,5) (2,4) (2,5) (3,5) (3,6) (4,6).

It has exactly 36 full proper edge-colourings, 36 distinct physical five-port states, and six colour-permutation orbits of six physical states each. The six orbit representatives, using first-appearance colour normalization, are:

    00012, 00120, 01002, 01020, 01121, 01211.

Attach a 3-pole TRIANGLE on vertices 7,8,9 with edges (7,8),(7,9),(8,9). Convert the 5-pole's semiedge at old root vertex 3 and the triangle's semiedge at vertex 9 into the ordinary edge (3,9). The remaining two external semiedges of the triangle are at **distinct** vertices 7 and 8; the other four at old roots 0,1,2,4. The connecting edge (3,9) is an actual graph BRIDGE partitioning the six physical ports into sets of sizes 4+2.

The triangle 3-pole admits precisely the six orderings of the three distinct semiedge colours. Thus for each of the 36 five-port colour states z, the cut-edge colour is z[3] and the two triangle exposed port colours must be the other two colours, in either order. This gluing independently generates all and only 36*2=72 physical outer tuples. The executable compares the entire set computed this way to a SECOND, independent 12-edge full graph colouring DFS.

## Theorem A (all sizes) — any GOOD-only 3+3 bridge supports AT MOST ONE bit

Let M be any connected cubic sixpole with six labelled external semiedges, three ordered physical equality pairs and NONEMPTY total proper-colouring relation. Assume all its Boolean boundary states belong to GOOD={100,010,001}.

Suppose an ordinary bridge partitions the six outer ports 3+3. Delete the bridge: the two resulting sides are connected colourable cubic FOURPOLES with four ordered physical semiedges each, including the removed cut edge's exposed end.

The Parity Lemma and real Kempe switches prove that the four physical port-colour relation of a colourable cubic fourpole is an S3-invariant union of at least two of the FOUR four-port colour orbits AAAA, AABB, ABAB and ABBA. All 11 nonempty possible unions of size 2,3,4 are realizable as proper cubic fourpoles and exhaust this ALL-N signature class.

Join any two 4pole relations A and B by equality of the colour on one bridge port. This yields the EXACT full physical six-port relation:

    R(A,B)={a[:3] concatenated with b[:3]:
                 a in A, b in B, a[3]=b[3]}.

The global assignment of the six remaining boundary ports to three logical pairs is an arbitrary perfect matching of six positions: 15 possibilities. Exhaustively verify the finite set of 11*11*15=1815 possible (A,B,pairing) configurations:

    GOOD-only, only bit 100: 6 configurations;
    GOOD-only, only bit 010: 3 configurations;
    GOOD-only, only bit 001: 9 configurations;
    GOOD-only, two bits:    0;
    GOOD-only, three bits:  0.

All 18 GOOD-only cases have exactly 36 physical port states. The other 1797 cases exhibit at least one disallowed Boolean bit. This is an exact finite algebra proof over an ALL-SIZE proven classification, NOT a search restricted by graph order.

Therefore a bridge split 3+3 cannot synthesize even the newly constructed two-bit gadget. It is not a claim that ALL bridges are forbidden in two-bit graphs: the n10 example itself has a legal 2+4 bridge.

## Theorem B (all sizes) — a GOOD-only 2+4 bridge has at most two truth bits, and the bound is SHARP

If bridge e partitions the six physical semiedges into 2+4, the side carrying two physical external semiedges becomes a cubic THREEPOLE after e is cut. By the Parity Lemma, each proper 3-edge-colouring of any cubic 3pole has ALL THREE exposed semiedge colours distinct. In particular the two original exposed physical colours are ALWAYS unequal.

For each realized onehot bit b, the separately proved forced-Kempe 36-state saturation theorem ensures EVERY parity-compatible physical boundary tuple of bit b occurs. Among those 36 tuples, any prescribed physical port pair from TWO DIFFERENT logical pairs is equal in SOME tuple. Thus the two physical ports on the 2-port side of a bridge must be the TWO ports of ONE logical equality pair, or else no GOOD-only colouring is possible. That pair's truth bit is permanently 0; of the three onehot Boolean values only the other TWO may occur.

The explicit n10 simple connected sixpole above realizes precisely BOTH remaining onehot truth bits, showing the all-n 2+4 bound is SHARP. In contrast, the 3+3 bound is also SHARP via the earlier genuine n14 GOOD-only onebit multipole.

### Compositional implications

Gluing two physically realizable FOURPOLES through one edge cannot produce a two- or three-bit GOOD-only gadget (3+3 split).

Gluing a suitable genuine FIVEPOLE to a genuine THREEPOLE through one edge CAN yield two allowed truth bits, but cannot yield the third. This establishes which kind of connector is required for the next stage: a full 108-state gadget, if realizable, must avoid any 2+4 or 3+3 bridge; 1+5 transfer bridges may be removed from a minimal candidate by the prior theorem. Consequently a minimum-order full Exact-One sixpole remains BRIDGELESS.

These are strict boundaries on the studied construction grammar. No published global no-go for bridgeless sixpoles is claimed, and the new graph is NOT a universal SCL solver.

## Extra exploratory negative control (NOT a proof)

A fixed-seed 120,000-step degree-preserving random simple-graph edge-switch walk starting from the n10 two-bit graph, keeping six distinct roots and testing real colourability, did not produce a *bridgeless* GOOD-only two-bit graph. It encountered 17 two-bit GOOD-only configurations, all retaining bridges. This is an observational, highly non-exhaustive control, not a theorem about n10 or any larger n.

## Next decisive gate

1. Construct a BRIDGELESS connected simple cubic sixpole whose full physical 6-port relation contains precisely two onehot bits (72 tuples), without forbidden states, or prove a universal obstruction to such a core.
2. Attempt to realize the third 36-state bit through a physical higher-width interface, checking all 108 physical tuples in the SAME graph.
3. Only after a legal full 108-state construction (if it exists), consider polynomial-calculus back-simulation or an actual native SCL algorithm. Neither follows from the current two-bit gadget.

**Science checkpoint:** physical TWO-BIT sixpole CONSTRUCTED (n10); all-n 3+3 bridge at-most-one and 2+4 bridge at-most-two PROVED; physical three-bit 108 gadget OPEN; polynomial native SolveLinearCubicXSAT NOT CONSTRUCTED; P vs NP OPEN. New GitHub Actions job conclusion must remain UNVERIFIED until explicitly inspected.
