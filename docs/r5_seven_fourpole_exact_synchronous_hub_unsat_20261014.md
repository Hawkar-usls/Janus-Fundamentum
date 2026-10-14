# R5 — Exact UNSAT theorem for seven-fourpole synchronous phase hubs

**Date:** 2026-10-14 (Europe/Kyiv)  
**Branch:** `research/r5-kempe-coupled-involutions-20261013`  
**Exact verifier:** [r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness.py](../experiments/r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness.py)  
**Independent source of skeletons and complete colour-orbit tables:** [r5_exactone_seven_fourpole_synchronous_hub_frontier.py](../experiments/r5_exactone_seven_fourpole_synchronous_hub_frontier.py)

## Definitive scientific status

**THEOREM — ALL INTERNAL SIZES, ONE SPECIFIED INTERFACE GRAMMAR.** Construct a sixpole by taking exactly seven *connected, colourable, cubic fourpoles*, whose full ordered physical 3-edge-colour relations are among the eleven possible 4-port S3-invariant union-of-2-to-4-orbit signatures. Join exactly eleven pairs of physical semiedges from **different** fourpole blocks into ordinary edges. Suppose the seven-block join skeleton is a **simple 3-edge-connected graph**. The six remaining physical semiedges belong to distinct degree-three blocks; pair them into any of 15 possible logical pairs.

**No such assembly can realize the GOOD-only three-input equality predicate `{100,010,001}` on its six physical semiedges.** In particular, no member of this entire grammar realizes precisely the required 108 full ordered physical six-port tuples of a full three-input Exact-One gadget.

This is not an unrestricted all-size no-go for arbitrary cubic sixpoles. The theorem does not cover lower-connectivity seven-block skeletons, parallel edges between blocks, other numbers of blocks, differently partitioned multipoles, or physically indecomposable cubic cores. It does not imply a polynomial `SolveLinearCubicXSAT` algorithm, nor `P=NP` or `P≠NP`.

## Completeness: four skeletons, 60 port matchings, 29 exact cases

With seven fourpoles and eleven joining edges, the skeleton has total degree 22. Simple 3-edge-connectivity forces all skeleton degrees to be at least three, so its degree multiset is precisely `(4,3,3,3,3,3,3)`. The sole degree-four block exposes no physical semiedge and plays the role of the four-wire synchronization hub; each of the six degree-three blocks exposes exactly one external semiedge.

The separately executable graph generator exhaustively enumerates all 5,670 simple labelled graphs with this degree sequence, proves every one is 3-edge-connected, and partitions them under all 7! label permutations into four disjoint full isomorphism orbits of sizes `2520,1260,1260,630`.

For every skeleton, compute all *actual* graph automorphisms, and their induced permutation action on the six exposed physical semiedges. This partitions the 15 labelled perfect matchings into `9,7,8,5` orbits, respectively. Relabeling whole constituent blocks and permuting their ordered four-port relation is permitted because each block may take any of the eleven signatures, and the catalogue is closed under semiedge permutations. The verifier explicitly proves the orbits' union equals all 15 pairings, so checking one representative of each is exact, not heuristic.

Thus the **29** complete pairing-orbit checks cover `4 × 15 × 11^7 = 1,169,230,260` signature/skeleton/port-pairing choices. This is a count of **logically covered choices**, not raw evaluations of a billion compositions.

## Exact physical join records

For each of four skeletons, enumerate all `3^11=177,147` assignments of the eleven interblock edge colours. For each degree-three constituent, Kirchhoff's nonzero Klein-four flow law uniquely fixes its outer semiedge colour (unless the three connector colours xor to zero, which makes the local colouring impossible). The degree-four central block's four nonzero connector colours must xor to zero.

Represent a compatible ordered four-semiedge colour tuple by one of the four exact local S3 orbit types `AAAA,AABB,ABAB,ABBA`. Group full interblock assignments by their seven-dimensional orbit vector, and compute the **exact** 729-bit support of the six physical external semiedges for each orbit vector. No floating-point synchronization, linear-envelope relaxation, or estimated probability is used.

The independently checked four orbit-record counts are `1328,1400,1379,1272`. These records are the exact semantic composition of constituent fourpole boundary relations.

## Complete monotone three-witness SAT/UNSAT certificate

Fix a skeleton and a perfect logical pairing. Call an orbit vector BAD if its exact sixport relation permits any Boolean truth value other than `100,010,001`. An assembled fourpole-class choice with no forbidden states cannot admit any BAD orbit vector.

Assume that a valid complete three-bit assembly existed. Because its full relation realizes all three truth bits, take three *actual* full colourings that respectively witness `100`, `010`, `001`. Their local fourpole orbit vectors `p,q,r` are individually GOOD-safe. For each constituent block `v`, let `U_v` be the union of the at most three orbit types used by these witnesses. Every `U_v` is contained in the actual selected physical fourpole signature class `S_v`.

The exact composed colour relation is **monotone** in these local orbit sets: enlarging one `U_v` can only add possible physical colourings. Thus the union `U` may not include a BAD orbit vector. Because each actual connected, colourable cubic fourpole signature contains **at least two** local orbit types, at each singleton `U_v` we may add one of at most three other types drawn from `S_v`; at nonsingletons keep `U_v`. The resulting minimal allowed masks `T_v` are valid (each has 2,3, or 4 orbits), still support the three witnesses, and remain BAD-free.

**Therefore any real three-bit GOOD-only assembly gives a certificate consisting of three individually safe good orbit vectors and one of the listed singleton extensions.** Conversely if the verifier finds such a BAD-free choice `T`, its seven local signatures correspond to actually realizable cubic fourpoles under the established 11-class atlas, and therefore give a legitimate positive composite *boundary-relation* witness. Consequently exhaustive failure to find a triple plus singleton extension proves UNSAT **within this grammar**, not merely lack of discovery.

The verifier represents all BAD vectors using finite bitsets; it tests every pair, every third witness that survives, and every singleton extension. An all-good positive synthetic relation is deliberately included as a regression to ensure the procedure is able to return SAT.

## Observed exact computational certificate

| Skeleton | Pairing-orbit cases | GOOD witness triples actually tested | Singleton minimal extensions |
| ---: | ---: | ---: | ---: |
| 0 | 9 | 11,590,395 | 4,269,270 |
| 1 | 7 | 12,014,345 | 4,044,777 |
| 2 | 8 | 13,257,203 | 4,561,146 |
| 3 | 5 | 4,919,448 | 1,942,200 |
| **Total** | **29** | **41,781,391** | **14,817,393** |

Across these cases, exactly **170,704** two-witness pairs survive early BAD-pattern rejection and **1,181,873** three-witness triples avoid an immediate BAD-pattern conflict. Every one of the 14,817,393 required minimal extensions fails the exact BAD-vector test. Zero valid complete three-bit compositions survive.

The 29-case data were computed independently during this research iteration using complete orbit-vector relations and exact integer bitset checks. The new committed standalone verifier asserts these figures and includes a positive SAT-control; it is wired into GitHub Actions. An independently observed completed GitHub Actions **PASS remains UNVERIFIED** until a run is retrieved and checked.

## Implication for synchronous physics and next gate

The phase-synchronization analogy is useful for identifying nonlinear four-body correlations, but **one central four-wire hub embedded in any of the four simple 3-edge-connected seven-fourpole / eleven-join skeletons cannot implement the desired full three-bit Exact-One boundary relation**, even when the constituent blocks are arbitrary-sized and their full legal signatures can be chosen freely.

This excludes the specific seven-block construction as a route to adding bit `001` to the already **physically verified** 28-vertex bridgeless GOOD-only two-bit graph (`100,010`, 72 sixport tuples and 144 full colourings). The full 108-state physical three-bit cubic sixpole remains **OPEN**, as does a universal polynomial algorithm for native `SolveLinearCubicXSAT`; `P` versus `NP` remains **OPEN**.

**Next admissible research:** enumerate the seven-block lower-edge-connectivity or parallel-edge skeletons (with proper cut reduction), increase block count, or construct and analyse an irreducible cubic sixpole core. Require exact physical colourability certificates, correct completeness arguments and runnable regression tests; do not infer all-size gadget nonexistence from this limited grammar theorem.
