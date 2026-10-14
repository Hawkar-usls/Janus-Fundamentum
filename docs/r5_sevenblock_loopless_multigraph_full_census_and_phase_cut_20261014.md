# R5 — Seven-fourpole loopless multigraph census and exact new 3-edge no-go

**Date:** 2026-10-14, Europe/Kyiv  
**Branch:** `research/r5-kempe-coupled-involutions-20261013`  
**Complete multigraph census:** [r5_exactone_sevenblock_loopless_full_multigraph_census.cpp](../experiments/r5_exactone_sevenblock_loopless_full_multigraph_census.cpp)  
**Full three-witness proof for new parallel, 3-edge-connected types:** [r5_exactone_sevenblock_parallel_3edge_exact_nogo.py](../experiments/r5_exactone_sevenblock_parallel_3edge_exact_nogo.py)  
**Previous four simple 3-edge-connected types:** [r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness.py](../experiments/r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness.py)  
**Previous exact all-size fourpole two-edge transfer taxonomy:** [r5_exactone_sevenblock_simple_twoedge_antiphase_gate.py](../experiments/r5_exactone_sevenblock_simple_twoedge_antiphase_gate.py)

## Scientific status

**New proved result:** NO assembly of seven arbitrary connected colourable cubic FOURPOLES, joined by eleven ordinary interblock edges forming a LOOPLESS **3-edge-connected MULTIGRAPH**, can realize a complete GOOD-only three-input Exact-One physical sixport relation. This includes all parallel connections between blocks allowed by 3-edge-connectivity. The constituent fourpoles may have arbitrary internal sizes.

**Open frontier:** connected sevenblock loopless multigraphs with 1-edge or 2-edge cuts, eight-plus block architectures, self-joins or indivisible cubic sixpole cores. The global existence/nonexistence of a physical all-108-state cubic Exact-One sixpole is still OPEN. No universal deterministic polynomial native `SolveLinearCubicXSAT` is constructed; `P` vs `NP` is OPEN.

## 1. Complete skeleton census without a fixed hub

Each of seven blocks is a cubic FOURPOLE, so it has exactly four physical semiedges available for either interblock links or one of the six final outer ports. Select eleven undirected pairs of DISTINCT block vertices from the 21 pairs of seven vertices, permitting repeated pairs but no self-loops, with degree of each block <=4. This automatically leaves exactly 7×4−2×11=6 exposed physical ports. Demand connectedness.

The independent, no-external-library C++ verifier generates each such labelled edge multiset ONCE by lexicographic multiplicity recursion and inspects every proper vertex-subset cut, counting boundary edges with MULTIPLICITY. For each cut it computes the number of exposed physical semiedges on that side as the sum of `4 − block degree` over constituent blocks.

| Exact labelled category | Number |
| --- | ---: |
| All degree-eligible edge multisets | 5,229,168 |
| Disconnected | 493,458 |
| **Connected** | **4,735,710** |
| Connected, minimum edge cut 1 | 2,532,390 |
| Connected, minimum edge cut 2 | 2,188,830 |
| Connected, minimum edge cut 3 | 14,490 |

Among the **2,532,390 connected bridged** labelled block multigraphs, **2,311,890** contain a 3+3 physical-port bridge, excluded as a full GOOD-only threebit assembly by the previously proven all-size fourpole bridge theorem. The other **220,500** have no 3+3 bridge; they may have 1+5 transfer bridges, or zero-port cut sides, so they are NOT all declared fully UNSAT solely from this count.

**Every single one** of the 2,188,830 connected labelled **2-edge-connected** skeletons admits at least one TWO-edge cut separating exactly 2+4 exposed physical ports. A subset of **289,590** also admits a cut splitting some OTHER port count. All counts are labelled edge-multiset counts, NOT numbers of graph isomorphism classes.

Breakdown of the 2-edge-connected category by number of degree-two constituent blocks (each has exactly two physical exposed semiedges):

| Degree-two constituent blocks | Labelled skeletons |
| --- | ---: |
| None | 54,810 |
| Exactly one | 740,670 |
| Two or more | 1,393,350 |
| **Total** | **2,188,830** |

Therefore **2,134,020** labelled skeletons in this category have at least one isolated two-outer-port constituent fourpole, where the exact cross-pair anti-phase reduction can be applied directly. The remaining 54,810 still have a 2+4 cut but its two-outer-port side must contain multiple blocks; as a combined connected two-cut component it still forms an actual cubic FOURPOLE and obeys the same full signature restriction, though an exact sixblock reduction may require extra reasoning.

**Important proof boundary:** this census proves the existence of those combinatorial cuts. It does NOT by itself show no full 108-state relation for any low-connectivity skeleton. In particular, some outer one-port transfer bridge can be eliminated by physical contraction only under its explicit colourability condition and without incorrectly inferring it was a minimal graph.

## 2. Complete 3-edge-connected multigraph classification

When the block skeleton's minimum edge-cut is three, every block degree is at least three. Eleven joining edges give total degree 22; with seven constituent FOURPOLES this forces exactly one degree-four hub and six degree-three terminal blocks. Fix the hub at vertex 0. Independently generate ALL loopless multigraph degree realizations with degrees `(4,3,3,3,3,3,3)`:

| Hub-fixed labelled category | Number |
| --- | ---: |
| All multigraph degree realizations | 13,440 |
| Disconnected | 1,140 |
| Connected with edge cut 1 | 2,400 |
| Connected with edge cut 2 | 7,830 |
| **3-edge-connected** | **2,070** |

Canonicalization of the final 2,070 under all `6!=720` permutations of terminal blocks gives precisely **SEVEN** unlabelled 3-edge-connected types. FOUR are simple and were already proven to exclude complete threebit GOOD-only under the prior exact sevenblock certificate. The remaining THREE are genuinely new, featuring doubled connections between hub and another block, and have hub-fixed labelled orbit sizes 360,720,180.

## 3. Exact nonlinear GOOD-only no-go for all three new parallel types

For each representative, use all `3^11=177,147` assignments of nonzero edge colours to ELEVEN distinct (possibly parallel) interface wires. Every constituent fourpole has one of the four exact parity-consistent ordered physical colour orbit types `AAAA,AABB,ABAB,ABBA`. Group all legal connector-colour choices into seven-component local orbit vectors; record the COMPLETE 729-bit physical sixport relation of each vector. The resulting orbit-vector counts are 1266,1288,1351 for the three representatives, with 10857,10791,10731 valid connector-colour assignments, respectively.

Compute ACTUAL multigraph skeleton automorphisms and their action on all 15 logical physical port-pairings. These reduce the three 15-pairing families to 9,15,6 checks while provably covering all 45 pairings.

Run the already proven exact MONOTONE THREE-WITNESS certificate: any good-only class assignment supporting all three bits yields three locally good-safe orbit vectors, whose coordinate unions must be free of every forbidden locally realizable vector; singleton orbit masks must be completed to real colourable fourpole 2-orbit-or-larger classes. All those minimal extensions are exhaustively tested. Any positive result would produce an exact symbolic physically realizable boundary-class candidate; the test returns **none**.

| New multigraph skeleton | Complete pairing orbit checks | Triples of GOOD witnesses | Minimal legal extensions | Valid full threebit classes |
| --- | ---: | ---: | ---: | ---: |
| M0 | 9 | 9,897,799 | 4,308,735 | 0 |
| M1 | 15 | 17,394,573 | 7,356,171 | 0 |
| M2 | 6 | 8,703,917 | 3,004,170 | 0 |
| **Total** | **30** | **35,996,289** | **14,669,076** | **0** |

The detailed exact edge multisets are frozen in the verifier. It independently reconstructs the full 13,440 labelled degree sequence census, the unique seven isomorphism classes and the three new representatives, then checks all 30 necessary and sufficient class compatibility searches. The previous simple-case verifier already covered the other four 3-connected types, completing the seven-type classification.

## 4. Why the two-cut frontier is physically interesting

For ANY cubic sixpole, not merely this grammar, if a two-edge cut separates a connected component with exactly TWO of the six outer physical semiedges, that component plus its two exposed cut-edge ends is a physical cubic FOURPOLE. Denote its two original exposed colours by `x,y` and its two cut colours by `a,b`; the Klein-four parity lemma gives the exact conservation law

    code(x) XOR code(y) = code(a) XOR code(b).

This transfers the equality bit `x=y` to `a=b` and is the rigorous interpretation of **two-channel synchronous phase compensation**.

If `x,y` are from TWO DIFFERENT logical pairs, the all-size fourpole atlas plus the exact 108-state target compatibility test restricts the possible fourpole's full signature to exactly four classes:

    {AAAA,ABAB}, {AAAA,ABBA},
    {AABB,ABAB}, {AABB,ABBA}.

The first two are direct or swapped transmission and hence reduce the question to a smaller remainder, where a prior no-go may apply. The final two are genuinely **anti-phase**, able to transmit equality with a change of common colour. This is a GLOBAL NECESSARY condition on every physically proper two-cut component of a hypothetical full Exact-One gadget, even when that component contains several original blocks. It is not by itself a universal no-go.

Therefore the next precise work is to classify which of the remaining 2,188,830 labelled 2-edge-connected multigraphs reduce to known excluded smaller-interface grammars and then perform the exact anti-phase three-witness check on the residual types. Bridge-connected 1+5 transfer inflations must also be treated without silently assuming that semantic shrinking preserves minimum size.

## Provenance and next admissible experiment

The table's 5,229,168-multiset exhaustive census was independently executed in optimized C++, and the 3-edge parallel cases were independently evaluated using exact physical-colour orbit records and 35,996,289 real three-witness tests. Reproducible C++/Python sources are committed to the research branch with GitHub Actions wiring; a completed successful GitHub Actions **PASS** has not yet been independently observed.

Our physical connected SIMPLE BRIDGELESS n28 two-bit gadget remains a verified 72-external-state, 144-internal-colouring `100/010` witness; the third 36-state branch `001` has NOT been constructed. Neither a polynomial native solver nor P=NP follows from these bounded-grammar tests.
