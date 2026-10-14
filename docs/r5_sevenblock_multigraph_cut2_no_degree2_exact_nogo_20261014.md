# R5 — Complete no-go for 19 multigraph 2-edge-connected sevenblock cores WITHOUT degree-two blocks

**Date:** 2026-10-14 (Kyiv)  
**Executable:** [r5_exactone_sevenblock_multigraph_cut2_no_degree2_exact_nogo.py](../experiments/r5_exactone_sevenblock_multigraph_cut2_no_degree2_exact_nogo.py).  
**Related complete skeleton census:** [r5_exactone_sevenblock_loopless_full_multigraph_census.cpp](../experiments/r5_exactone_sevenblock_loopless_full_multigraph_census.cpp).  
**Earlier 3-edge-connected multigraph no-go:** [r5_exactone_sevenblock_parallel_3edge_exact_nogo.py](../experiments/r5_exactone_sevenblock_parallel_3edge_exact_nogo.py).

## Main theorem (precise scope)

Let a sixpole consist of SEVEN connected colourable cubic FOURPOLES of arbitrary internal sizes, joined by eleven ordinary edges between different blocks, allowing PARALLEL edges between blocks but no self-loops. Require its seven-block LOOPLESS multigraph to be **2-edge-connected with minimum edge cut EXACTLY TWO**, and require EVERY constituent block to have at least three joining edges (so no block exposes two or more physical external ports).

Then NO such physically legitimate assembly realizes the complete GOOD-only `{100,010,001}` equality-bit boundary relation; in particular it cannot realize all 108 required physical sixport colour tuples without forbidden states.

This is another ALL-INTERNAL-SIZES **bounded-grammar theorem**, NOT a full all-size cubic sixpole impossibility result. The two-edge-connected multigraph cases WITH a degree-two block are still OPEN; see below.

## Why the entire case is small enough to verify exactly

A connected 7-block skeleton with eleven edges has total block degree 22. If every block has ordinary joining degree >=3, each must have degree <=4 as each constituent is a fourpole. Therefore its degrees are exactly `(4,3,3,3,3,3,3)`: one four-wire internal synchronization hub and six terminal blocks with one exposed physical port each.

Fix the unique degree-four hub at block vertex 0. Enumerate every loopless undirected MULTIGRAPH of exact block degrees `(4,3,3,3,3,3,3)`, allowing repeated edges and recording multiplicities. A recursion assigns each ordered smaller endpoint to larger endpoints, producing each labelled edge multiset exactly once. Evaluate all vertex-subset edge cuts:

| Hub-fixed labelled category | Count |
| --- | ---: |
| Complete degree realizations | 13,440 |
| Disconnected | 1,140 |
| Edge cut 1 | 2,400 |
| **Edge cut exactly 2** | **7,830** |
| Edge cut 3 | 2,070 |

Canonicalize ALL 7,830 hub-fixed two-edge-connected labelled multigraphs under the `6!=720` permutations of six terminal blocks. They form exactly **19 isomorphism classes**. Every class has parallel edges; there are NO simple edgecut2 graphs with this degree vector. Their labelled orbit sizes sum to 7,830.

Since the unique hub could be any of seven labels in the full fixed-label universe, this represents exactly **7×7,830 = 54,810 labelled** two-edge-connected skeletons without any degree-two constituent. Those are ALL the 54,810 such examples independently found by the prior 5,229,168-multiset all-degree census.

## Nonlinear proper-colouring compatibility test

For each of the 19 nonisomorphic representatives enumerate all `3^11=177,147` three-colour assignments of its eleven physical interblock edges. Parallel connector edges are counted as **different wires** and can have independently assigned colours subject to the fourpole interface relation.

At each block, its ordered physical semiedge colours must belong to exactly one of the four parity-consistent local S3 types `AAAA,AABB,ABAB,ABBA`. Record each seven-vector of orbit IDs along with the **EXACT** 729-bit support of the six ordered physical outer-port colour tuples accessible through that vector. This is a complete existential join over proper physical edge-colouring relations, not merely the linear Klein-four parity envelope.

For each representative, compute its true multigraph automorphism action on the 15 logical perfect matchings of six physical external semiedges, without assuming any additional symmetry. Exactly **199** pairing-orbit checks cover every one of the **19×15 = 285** labelled pairing cases. No matching is omitted.

As in the preceding verified sevenblock theorem, a hypothetical full GOOD-only threebit assembly must have one GOOD-safe orbit vector per truth bit 100,010,001. The componentwise union of three witness vectors must be free of BAD orbit patterns because allowing additional constituent fourpole orbit types can only EXPAND the external relation. Each selected constituent must have at least TWO allowed local orbit types, so any singleton coordinate must be minimally extended by one additional orbit included in the true constituent signature. Enumerating ALL these extensions is mathematically COMPLETE; if even one BAD-free selection survives, the verifier reports a real candidate signature assignment. None survives. A separate synthetic SAT-positive regression in the reused verifier checks against systematic false UNSAT.

## Full finite check and counters

| Count | Exact |
| --- | ---: |
| Nonisomorphic skeletons | **19** |
| Automorphism-orbit pairing checks | **199** |
| Actual labelled pairing cases covered | **285** |
| Two-good witness pairs surviving first BAD check | 470,992 |
| Three-good witness triples examined | **82,606,770** |
| Three-witness unions surviving immediate BAD screening | 4,824,222 |
| Minimal physically legal orbit-class extensions examined | **49,606,866** |
| Exact full threebit GOOD-only class assignments | **0** |

The standalone Python verifier reconstructs the 7,830 complete two-edge-connected hub-fixed labelled census, certifies 19 complete disjoint orbit classes, checks per-class physical connector-colour record counts, and replays all 199 exact compatibility tests. It asserts complete per-class expected counters plus the totals, so any mismatch is a failed regression rather than an unreported reinterpretation.

The 19 cases were independently checked in three batches in this research iteration; all are negative. These exact negative results do not depend on a bounded number of internal constituent vertices.

## What is now proved for the SEVEN-block loopless grammar

- **3-edge-connected:** SEVEN isomorphism classes, including THREE parallel-edge multigraphs. ALL excluded by exact GOOD three-witness certificates.
- **2-edge-connected, NO degree-two constituent:** NINETEEN additional multigraph isomorphism classes, ALL excluded by this new certificate.
- **2-edge-connected, with at least one degree-two constituent:** 2,134,020 labelled skeletons in the independent full census, NOT YET declared UNSAT. Each has a genuine two-outer-port fourpole whose two connecting edges implement a two-channel phase transfer. Its signature must satisfy the exact fourpole compatibility restriction for a putative full GOOD gadget; some anti-phase classes survive that necessary restriction.
- **1-edge-connected:** 2,532,390 labelled skeletons; 2,311,890 with a 3+3 physical-port bridge are excluded by prior full-GOOD bridge theorem. The other 220,500 have 1+5 transfer bridges only; such side components are removable in a minimal graph under the explicit colourability premise, but we do not automatically classify every labelled nonminimal assembly as UNSAT without a correct semantic reduction.

The remaining general mathematical target is to deal with the two-outer-port **anti-phase transfer component** without allowing forbidden 000/111 colourings. A physical full 108-state threebit Exact-One cubic sixpole is still NOT CONSTRUCTED and its universal impossibility remains OPEN.

The previously verified physical simple connected BRIDGELESS n28 two-bit sixpole has exact 72 allowed outer states, 144 full internal colourings and only 100/010; bit 001 is still missing. General deterministic polynomial native `SolveLinearCubicXSAT` is NOT CONSTRUCTED and `P` versus `NP` remains OPEN.

Provenance: independent Python integer-bitset computations and standalone exact code, stored in research branch; completed successful GitHub Actions CI remains UNVERIFIED pending job evidence.
