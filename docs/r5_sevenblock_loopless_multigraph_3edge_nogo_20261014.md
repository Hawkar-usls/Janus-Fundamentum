# R5 — Complete 3-edge-connected sevenblock 11-join LOOPLESS multigraph exclusion

Date: 2026-10-14, Kyiv. Research branch: `research/r5-kempe-coupled-involutions-20261013`.

**Standalone executable certificate:** [r5_exactone_sevenblock_parallel_3edge_exact_nogo.py](../experiments/r5_exactone_sevenblock_parallel_3edge_exact_nogo.py). Requires the previously verified [sevenblock local phase record generator](../experiments/r5_exactone_seven_fourpole_synchronous_hub_frontier.py) and [three-witness search](../experiments/r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness.py).

## Theorem and its strict scope

Take SEVEN arbitrary connected colourable cubic FOURPOLES, each with one of the eleven proven physically possible ordered fourport colour signatures (unions of two, three or four of the four Klein-four parity orbits AAAA,AABB,ABAB,ABBA). Join them with exactly ELEVEN ordinary interblock edges. Allow PARALLEL edges between blocks, but no loops on the block skeleton. Require the 7-vertex block multigraph to have edge connectivity >=3. The remaining six physical outer semiedges are paired into any three logical equality pairs.

**THEOREM:** No assembly in this entire 3-edge-connected loopless seven-fourpole grammar has complete GOOD-only bit relation {100,010,001}; in particular none can realize the exact 108 physical port tuples of the sought full three-input Exact-One sixpole. All constituent fourpole sizes are arbitrary.

This DOES NOT exclude edge-connectivity-one or two block multigraphs, self-joins, eight or more fourpoles, arbitrary indecomposable sixpoles, or a general polynomial exact SAT algorithm.

## Independent complete multigraph skeleton census

A 3-edge-connected skeleton has every block degree >=3. With seven fourpoles and eleven connecting edges the total block degree is 22. Since degrees <=4, the only possibility is exactly ONE degree-four hub and six degree-three terminal blocks. Fix the unique hub label 0, thus the seven-vertex ordinary degree vector is (4,3,3,3,3,3,3).

Generate EVERY loopless UNDIRECTED multigraph with this exact degree vector by recursively choosing the multiplicities on edges from the least unprocessed vertex to higher vertices. Each graph is generated once; no degree configurations or parallel edges are omitted. Test connectivity and EVERY vertex-subset edge cut. Canonicalize all 3-edge-connected graphs under the full six-factorial permutations of the nonhub vertices, keeping the unique hub fixed.

| Category | Hub-fixed labelled multigraphs |
| --- | ---: |
| All ordinary degree realizations | 13,440 |
| Disconnected (edge cut zero) | 1,140 |
| Connected, cut one | 2,400 |
| Connected, cut two | 7,830 |
| **Connected, cut at least three** | **2,070** |

The 2,070 graphs have EXACTLY SEVEN unlabeled types under full 6! terminal-block relabeling, of which FOUR are SIMPLE and were previously covered by the sevenblock exact simple-skeleton theorem. The other THREE have one doubled interblock edge incident to the central degree-four hub.

The actual three new representatives (hub=0) are:

```
M0: (0,1),(0,1),(0,2),(0,3),(1,4),(2,3),(2,5),
    (3,6),(4,5),(4,6),(5,6)               orbit size 360
M1: (0,1),(0,1),(0,2),(0,3),(1,4),(2,4),(2,5),
    (3,5),(3,6),(4,6),(5,6)               orbit size 720
M2: (0,1),(0,1),(0,2),(0,3),(1,4),(2,5),(2,6),
    (3,5),(3,6),(4,5),(4,6)               orbit size 180
```

The four simple labelled orbits have sizes 360,90,180,180. Sum: 2070, with no overlap. Thus EVERY allowed 3-edge-connected sevenblock LOOPLESS multigraph is isomorphic to exactly one of the seven listed classes.

## Exact physical three-witness UNSAT certificate

For each of three new representatives enumerate all 3^11 assignments of the ELEVEN physical connector-edge colours (parallel edges carry SEPARATE physical colour variables). At each of seven fourpole blocks check the exact S3-invariant fourport colour orbit; for every valid local orbit seven-vector record its **complete 729-bit physical sixport outer-colour relation**. These records are exact existential joins over coloured edges, not linear approximations or probabilistic oscillator states.

Compute all TRUE automorphisms of the given multigraph as permutations of its block vertices preserving ALL edge multiplicities, and their induced orbits on the 15 logical pairings of the six terminal physical port indices. The three representatives require 9,15,6 complete pairing-orbit checks, respectively (30 total), covering all 45 labelled pairings.

Assume some choice of seven legal fourpole signature classes produced all GOOD bits and no forbidden ones. Pick a genuine full proper colouring witness for each of 100,010,001, yielding three individually GOOD-safe seven-vectors of local orbit IDs. Their per-block union must be contained in the chosen true signature class. Physical colour support is MONOTONE under expanding local orbit support; therefore the union cannot enable any forbidden local orbit vector. Enlarge each singleton union coordinate by ONE additional orbit type (at most three choices), as all physically colourable connected fourpoles have at least two orbit types. If any legal solution existed, some such minimal extension would still support all three witnesses with no forbidden colouring. The verifier tests ALL these possibilities. NONE survives.

| New parallel skeleton | Pairing-orbit checks | Complete GOOD witness triples | Minimal legal singleton extensions | Successful 108-state class assignments |
| --- | ---: | ---: | ---: | ---: |
| M0 | 9 | 9,897,799 | 4,308,735 | 0 |
| M1 | 15 | 17,394,573 | 7,356,171 | 0 |
| M2 | 6 | 8,703,917 | 3,004,170 | 0 |
| **Total** | **30** | **35,996,289** | **14,669,076** | **0** |

The exact proof script checks every counter and fails on disagreement. Its three physical orbit-support record counts are 1266,1288,1351; its numbers of allowed full physical connector-colour assignments are 10857,10791,10731. It reuses an independently positive-tested exhaustive three-witness SAT/UNSAT core from the earlier sevenblock proof.

Combined with the completed four SIMPLE 3-edge-connected classes, this constitutes a complete all-internal-sizes NO-GO for all **SEVEN** 3-edge-connected seven-fourpole 11-join LOOPLESS multigraph skeletons.

## What remains

The NEW verified finite frontier is sevenblock LOOPLESS multigraphs with minimum edge connectivity one or two. Unlike the 3-edge-connected subclass, their skeleton degree sequences need not be (4,3,3,3,3,3,3); their number and exact cut types must be enumerated independently. Earlier sixblock loopless multigraph and sevenblock SIMPLE no-go certificates remain applicable only under their stated promises.

No real full 108-state physical Exact-One sixpole has been constructed. The existing real bridgeless n28 two-bit (100,010) 72-tuple sixpole remains independently verified, missing bit 001. The universal deterministic polynomial native SolveLinearCubicXSAT is NOT CONSTRUCTED; P versus NP remains OPEN.

Provenance: exact enumeration and all 30 matching-orbit tests independently executed in this research turn; standalone reproducible code committed to GitHub and wired to CI. A completed successful GitHub Actions result is NOT yet observed.
