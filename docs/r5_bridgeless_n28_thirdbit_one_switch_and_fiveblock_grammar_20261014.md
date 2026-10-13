# R5 checkpoint — third-bit attempts from the bridgeless 28-vertex seed

Date: 2026-10-14. Research branch: research/r5-kempe-coupled-involutions-20261013.

Source: [all n28 double-edge neighbours](../experiments/r5_exactone_n28_direct_thirdbit_switch_gate.py). Independent physical construction: [bridgeless n28 two-bit sixpole](../experiments/r5_exactone_bridgeless_n28_twobit_constructive.py). Exact bounded-interface grammar: [five fourpole skeleton C++](../experiments/r5_exactone_five_fourpole_all_simple_skeletons.cpp).

## First requested goal — accomplished

A genuinely BRIDGELESS connected simple cubic sixpole on n=28 with six distinct physical roots and 39 ordinary edges has exact physical GOOD-only bits 100 and 010, 36 externally distinct colour tuples each, 72 total, with 144 complete proper interior colourings and precisely two complete extensions per physical tuple. The full graph and proof are in the n28 checkpoint. The third bit 001 is absent.

## Second requested goal — attempted, not solved

### All 1,224 single double-edge endpoint interchanges of fixed n28

Take ANY pair of vertex-disjoint internal ordinary edges and reconnect their four endpoints in either of the two alternate pairings, keeping the graph simple and the physical root set unchanged. After canonical deduplication this produces exactly 1,224 labelled graph edge sets, 1,221 connected and three disconnected.

Exhaustive actual proper edge-colouring checks, with the full colour name symmetry used ONLY for safe existence-of-forbidden detection, and a second unpinned full-census check on every surviving GOOD-only graph, yield:

| Real graph state | Physical outcome | Count |
| --- | --- | ---: |
| Bridgeless | Has a forbidden full proper colouring | 1144 |
| Bridged | Has a forbidden full proper colouring | 48 |
| Bridgeless | Exact physical two-bit 100/010 relation (72 states) | 20 |
| Bridged | Exact physical two-bit 100/010 relation (72 states) | 4 |
| Bridgeless | No complete proper 3-edge-colouring | 5 |
| Disconnected | Outside input promise | 3 |
| **Total** | | **1224** |

Thus precisely twenty distinct *labelled* single-switch neighbours are still physical bridgeless exact two-bit gadgets, proving the n28 construction lies in a nontrivial local family. **Zero** one-switch neighbours add the third bit 001 without forbidden states. This is an EXACT finite local result, not a universal obstruction and not proof that several switches cannot succeed.

### All connected simple 5-block / 7-join skeletons composed from fourpoles

For five connected colourable cubic fourpoles joined by seven ordinary edges with a SIMPLE connected graph of five blocks, the exposed number of physical semiedges is six. There are exactly **four** unlabelled connected simple five-vertex skeletons with seven edges. For each skeleton, assign the arbitrary internal-size fourpole to one of its **11 exact possible physical signature classes** (11^5=161051 assignments), then inspect every one of 15 perfect matchings of the six exposed physical port indices. In total there are 4 * 161051 * 15 = **9,663,060** class-and-pairing compositions. The entire existential colour join is evaluated exactly, retaining the nonlinear proper 3-edge-colour boundary relation, not just Klein-four linear rank.

Per-skeleton results, indexed by the four explicit skeletons in the executable:

| Skeleton | Empty block-signature assignments | GOOD-only 1-bit pairings | GOOD-only 2-bit pairings | GOOD-only 3-bit pairings |
| --- | ---: | ---: | ---: | ---: |
| 0 | 1545 | 9870 | 36 | **0** |
| 1 | 1584 | 7641 | 0 | **0** |
| 2 | 1213 | 7187 | 42 | **0** |
| 3 | 868 | 5019 | 34 | **0** |
| **Total** | **5210** | **29717** | **112** | **0** |

The GOOD-only count includes multiplicity across distinct assignments of signature classes, port labellings and/or pairings; NOT counts of nonisomorphic physical graphs. The four skeletons may have bridges at block level or individual fourpoles may have internal bridges. Each fourpole class is physically realizable by a connected simple cubic block; hence the finite relation algebra applies to all sizes of the corresponding constituent blocks. It DOES NOT cover multiedge block skeletons, six-plus block skeletons, arbitrary decompositions or genuinely indivisible sixpole cores.

This is a bounded **all-size within the grammar** proof that these simplest new higher-width fourpole compositions still cannot realize the full 108 physical tuple Exact-One signature. It is not a global gadget impossibility theorem.

## Reproducibility and scientific gates

The Python n28 neighbour verifier enumerates every full graph option and independently checks each GOOD-only survivor with an unpinned exhaustive proper-colouring DFS. The C++ five-block verifier expands every one of eleven S3-symmetric fourpole signature classes and existentially composes seven three-colour join wires, then tests all fifteen labelled physical pairings. The numbers above are finite exact computations; their correctness needs a completed CI run for external automation provenance, which is currently UNVERIFIED.

The next viable constructive direction is a genuinely higher-width shared-interface assembly not expressible by these four simple five-fourpole skeletons, or an irreducible bridgefree core with nonlinear cross-colour compatibility. A potential candidate needs one real physical graph with all **108** even-parity GOOD physical tuples and no forbidden state.

Full Exact-One three-bit sixpole: OPEN. General deterministic polynomial SolveLinearCubicXSAT: NOT CONSTRUCTED. P versus NP: OPEN.