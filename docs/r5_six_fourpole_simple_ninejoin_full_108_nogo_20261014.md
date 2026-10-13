# R5 checkpoint — no complete Exact-One in any simple six-fourpole nine-interface grammar

Date: 2026-10-14. Script: [complete compressed witness certificate](../experiments/r5_exactone_six_fourpole_nineedge_simple_skeleton_gate.py).

## Theorem and exact scope

Take **SIX connected colourable cubic FOURPOLES**, with any numbers of internal vertices. Their complete physical ordered four-semiedge colour relations belong to the **eleven** S3-symmetric signature classes (every union of two, three or four of the four parity-compatible local colour orbits AAAA, AABB, ABAB, ABBA), as established by the earlier R5 full-size fourpole atlas.

Join exactly **NINE pairs of semiedges between DISTINCT blocks**, one ordinary connecting edge per pair, and require the BLOCK skeleton to be a connected SIMPLE six-vertex graph. This leaves exactly six physical semiedges. Pair those six in any of the 15 possible logical matchings.

Then **NO SUCH ASSEMBLY** supports all three Boolean pair-equality patterns 100/010/001 without a forbidden pattern. In particular, none has the full required **108 ordered physical 6-port states**.

This is an **ALL-INTERNAL-SIZE** theorem for a specifically bounded block-assembly grammar. It is NOT a theorem for arbitrary indivisible cubic sixpoles, parallel interblock edges, seven-plus components or every cubic graph.

## Exhaustive skeleton classification

There are C(15,9)=5005 simple labelled choices of nine edges on six block vertices. Retain those with every block vertex of degree at most four (necessary for 4pole attachment) and whose skeleton is connected: **3700 labelled graphs**. Canonicalize under all permutations of six block labels, preserving degree classes: **14 unlabelled skeletons**. Their minimum edge-cut cardinalities split **3 with a bridge, 9 with edge connectivity two and 2 with edge connectivity three**. The two 3-edge-connected cubic skeletons are the triangular prism and K3,3.

For each of these 14 representatives test all **15 distinct perfect logical matchings** of the exposed six semiedges. Every block has **11** possible exact 4pole signatures; the entire naive signature-choice space is therefore

    14 × 15 × 11^6 = 372,027,810 compositions.

We do NOT claim to naively loop 372 million assignments. The verifier uses a logically complete compressed monotone certificate described below.

## Compressed exact certificate — completeness proof

For each skeleton enumerate all 3^9 assignments of the colours of its ordinary INTERBLOCK join edges. At a block of skeleton degree d, its number of exposed physical semiedges is 4-d. Enumerate the remaining physical colours and retain exactly the S3-compatible four-colour vectors whose parity permits one of AAAA, AABB, ABAB, ABBA. The local 4-tuple order is all exposed ports first, followed by its connector ports in increasing skeleton-edge index. This deterministic ordering realizes arbitrary block-port relabellings, since every one of the 11 signature classes is included.

For each *six-vector of local orbit IDs*, precompute the full 729-bit set of realizable ordered physical six-port colour tuples, aggregating over every compatible assignment of connector colours. This exact relation-level join is the same as colourability of independently specified fourpoles glued with equality on each interface edge. It is NOT an overapproximation or an abstract physical 6pole cover.

For any fixed choice of six exposed logical pairs (one of 15), classify an orbit six-vector BAD if it admits at least one forbidden external colour tuple. Any GOOD-only assembly may select only orbit vectors that are individually non-BAD.

Assume for contradiction that a choice of 11-class masks on the six blocks yields all three permitted truth bits and no forbidden ones. Select one actual full colouring witness of each truth bit. Each witness selects an individually GOOD-only six-vector of local orbits p, q, r. At block v the union U_v of the three orbit IDs is a SUBSET of the actual selected signature class S_v.

The admissible state relation is MONOTONE in the selected orbit classes: enlarging a class can only add physically possible states. Therefore the componentwise union U=(U_v) must itself admit NO bad orbit-pattern witness. Every actual block signature has at least two orbits. If U_v already contains >=2, retain it; if U_v is a singleton, choose ONE additional orbit from S_v, at most 3 choices. The resulting minimal two-orbit-or-larger class vector still lies within S and remains BAD-free, and still realizes p,q,r.

Hence **a full legal three-bit composition exists IF AND ONLY IF** some triple of individually safe good orbit-vectors, after the described at-most-three-per-singleton extensions, yields a BAD-free class vector. The executable enumerates ALL such triples and extensions for EVERY one of 14 × 15 cases, finding NONE. This proves the theorem; no untested 11-class assignment remains.

The proof uses monotonicity, not a heuristic sample of block choices.

## Additional all-size 3-edge-connectivity corollary, even with parallel join edges

Allow the nine interblock joining edges to form a connected MULTIGRAPH with no loop edges but possible parallel edges, still with six fourpole blocks and six external semiedges. If the block skeleton is 3-edge-connected, every vertex has degree >=3. The total skeleton degree is 2×9=18, hence all six degrees are EXACTLY 3.

A cubic multigraph on >=3 vertices with two parallel edges between u and v has a cut of size <=2 separating {u,v} from the rest: at u and v the parallel edges consume at least two of their three incident edges each, leaving <=2 outward edges total. Thus every connected 3-edge-connected cubic skeleton of six vertices is SIMPLE. It is therefore isomorphic to one of the same two 3-connected simple skeletons already excluded above.

Consequently **even allowing parallel join edges**, NO 3-edge-connected six-block/nine-join fourpole assembly can realize the complete physical 108-state Exact-One relation. This does NOT extend the exclusion to MULTIGRAPH block skeletons of edge connectivity one or two.

## Validated scope and further research

The direct physical 28-vertex, 39-edge bridgeless GOOD-only two-bit graph remains a valid positive witness for exactly 72 external states (100 and 010, 36 each). It does not support 001. The new theorem independently excludes the next simple six-fourpole / nine-join route to supplying the third bit.

To try to create all 108 states, study seven-plus constituent fourpoles, MULTIEDGE six-block skeletons with two-edge cuts, genuinely irreducible sixpoles, or other physically connected cubic multipole architectures. Full signature verification must always check ALL external colour tuples, not just one SAT witness.

CI: script committed and added to branch workflow; GitHub Actions PASS is not confirmed until a completed successful job is observed. Universal full 108-state sixpole OPEN; polynomial SolveLinearCubicXSAT NOT CONSTRUCTED; P versus NP OPEN.
