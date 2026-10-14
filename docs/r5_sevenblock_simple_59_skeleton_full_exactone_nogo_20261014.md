# R5 — Complete no-go for SIMPLE seven-fourpole / eleven-join Exact-One synthesis

**Date:** 2026-10-14 (Europe/Kyiv)  
**Branch:** `research/r5-kempe-coupled-involutions-20261013`  
**New complete verifier:** [r5_exactone_sevenblock_simple_all_59_exact_nogo.py](../experiments/r5_exactone_sevenblock_simple_all_59_exact_nogo.py)  
**Independent atlas and all-size two-edge transfer:** [r5_exactone_sevenblock_simple_twoedge_antiphase_gate.py](../experiments/r5_exactone_sevenblock_simple_twoedge_antiphase_gate.py)  
**Existing 3-edge-connected 7-block no-go:** [r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness.py](../experiments/r5_exactone_seven_fourpole_synchronous_hub_exact_three_witness.py)  
**Existing sixblock MULTIGRAPH no-go:** [r5_exactone_six_fourpole_multigraph_all_skeletons_gate.py](../experiments/r5_exactone_six_fourpole_multigraph_all_skeletons_gate.py)

## Theorem, scope and relation to the primary objective

Consider a connected cubic sixpole obtained from **seven independently connected and properly three-edge-colourable cubic FOURPOLES**. Each constituent can have an ARBITRARY number of internal vertices; its complete ordered four-semiedge physical colour relation is among the previously established **eleven** admissible S3-invariant fourpole signatures (unions of 2, 3 or 4 of the four allowed parity orbit classes `AAAA,AABB,ABAB,ABBA`). Connect exactly **eleven** pairs of semiedges from DIFFERENT blocks by ordinary edges, with the seven-block interface graph **SIMPLE and CONNECTED** (no parallel interblock edges or loops), leaving exactly six physical external semiedges. Assign these six semiedges to any three ordered logical equality pairs.

**THEOREM. No member of this entire seven-fourpole / eleven-SIMPLE-join grammar has full GOOD-only equality-bit support `{100,010,001}`.** Thus no such member realizes the 108 ordered physical port tuples required of a full three-input Exact-One sixpole gadget, regardless of internal constituent block sizes.

This remains a **bounded-grammar all-size theorem**, NOT a universal impossibility result for every cubic sixpole. Parallel-edge sevenblock networks, other numbers of fourpoles and irreducible cubic cores are NOT excluded. A universal polynomial `SolveLinearCubicXSAT` is NOT constructed and `P` vs `NP` is OPEN.

## 1. Exhaustive 59-skeleton classification with independent completeness proof

A connected simple seven-vertex eleven-edge block skeleton with maximum degree four represents a valid seven-fourpole interface topology. For independently reproducible completeness, enumerate all `C(21,11)=352,716` labelled eleven-edge selections of the 21 possible simple seven-vertex edges; retain maximum degree four and ordinary graph connectivity. This produces **145,110 labelled eligible skeletons**.

Independently obtain 59 candidate nonisomorphic seven-vertex skeletons from the NetworkX small graph atlas. For EACH candidate generate its complete orbit under all `7!=5040` vertex relabellings, representing each labelled graph by its exact 21-bit edge mask. Verify the 59 orbits are mutually disjoint and their union equals **exactly** the independently enumerated **145,110** graph edge masks. Thus the number **59 is an exhaustive verified census**, not an atlas completeness assumption.

Their minimum ordinary edge connectivity is:

| Edge connectivity of block skeleton | Nonisomorphic simple skeletons | Proof action |
| --- | ---: | --- |
| 1 | 15 | ALL have a bridge splitting outer six ports **3+3**; exclude by prior all-size 11x11x15 fourpole bridge theorem |
| 2 | 40 | NEW exact cut transfer + complete nonlinear sixblock witness search |
| 3 | 4 | Excluded by the previously completed 29-pairing-orbit sevenblock 3edge exact certificate |
| **Total** | **59** | **All 59 excluded** |

Every **2-edge-cut** in all 40 edge-connectivity-two schemes splits **exactly 2+4** of the six physical exposed ports. Each has at least one degree-two fourpole block H; because its two interblock connections form a two-edge cut, this fourpole exposes exactly TWO original physical ports `x,y` and TWO joining semiedges `a,b`. Removing H leaves a **CONNECTED** six-fourpole / nine-join graph, because the original skeleton was 2-edge-connected. Every cut-end physical semiedge root is distinct by the original constituent 4pole promises.

## 2. All-size two-cut transfer theorem and 11-class filter

For any proper three-edge-colouring of the connected fourpole H, the Klein-four parity equation gives

    code(x) XOR code(y) = code(a) XOR code(b).

Therefore `x=y` **if and only if** `a=b`.

**Case I: `x,y` are the SAME logical pair.** In a hypothetical full 108-state gadget, all three logical one-hot truth states appear. Therefore both `a=b` and `a≠b` must be physically extendable through H. Colour-label S3 symmetry then implies EVERY one of the 3 equal and 6 distinct ordered cut-colour pairs extends to at least one H proper full colouring. Thus EVERY right-sixpole complete proper colouring can be joined to H and the truth bits after join are IDENTICAL to the right-sixpole truth bits when its cut pair `(a,b)` replaces the original logical pair `(x,y)`. A hypothetical full threebit GOOD-only sevenblock gadget would force the remaining connected SIX-fourpole right side to be itself full threebit GOOD-only. The established **all-size SIX-fourpole / nine-join loopless multigraph no-go** contradicts this. Hence no degree-two block's two outer ports can belong to one logical pair.

**Case II: `x,y` are from DIFFERENT logical pairs.** Enumerate the **complete 11 physical fourpole signatures** H and all **81** assignments to the other four physical outer colours. For each such right four-tuple, compute the target set of admissible `(x,y)` values in the complete 108-state physical Exact-One relation. A cut pair `(a,b)` is SAFE only if ALL physically allowed H extensions for those cut colours stay in that target set. Define the maximal right relation as the union of all SAFE cut-colour choices, imposing the exact right-sixpole parity equation. If this maximal relation cannot reproduce all 108 target tuples, NO actual right-sixpole relation can.

The independently executable 11-class exhaustive compatibility check leaves EXACTLY FOUR possible H orbit sets:

    {AAAA,ABAB}, {AAAA,ABBA}, {AABB,ABAB}, {AABB,ABBA}.

In the first two classes, the physical colour values of `(x,y)` are EXACTLY `(a,b)` or `(b,a)` for every proper H state. The left block is a two-wire identity/swap. A full Good sevenblock would again require its RIGHT-sixblock relation to be full Good under a corresponding permutation of physical port indices; the preceding proven sixblock no-go excludes both.

**Only two anti-phase classes remain:**

    {AABB,ABAB} or {AABB,ABBA}.

For equal cut colours `a=b`, these classes force `x=y` but also `x≠a`, with TWO possible values of `x`; for unequal cut colours they transmit the two distinct colours either in order or swapped. Their maximal safe RIGHT-sixport relation contains precisely **87** distinct states for a cross-logical-pair split; they are not merely identity connections. This is the only remaining obstruction to the previously attempted direct reduction.

Swapping the two physical outer port indices `x,y` exchanges these two anti-phase classes. Since all **15** labelled logical perfect matchings are in scope and all **12** matchings placing `x,y` into DIFFERENT logical pairs are tested, it is COMPLETE to fix just the first class `{AABB,ABAB}` when doing the final exact search.

## 3. Count and completeness of surviving pairings

Among the 40 two-edge-connected skeletons:

| Number of degree-two blocks per skeleton | Skeletons | Logically possible pairings per skeleton |
| ---: | ---: | ---: |
| 1 | 18 | 12 |
| 2 | 19 | 10 |
| 3 | 3 | 8 |
| **Total** | **40** | **430 of 600 candidate skeleton/pairings** |

All other 170 cases are excluded immediately because at least one isolated two-port block would contain a complete logical pair. The two possible remaining anti-phase classes at each degree-two block leave `18×12×2 +19×10×4 +3×8×8 = 1,384` not-yet-checked simultaneous anti-phase assignments, prior to selecting classes of other blocks. This is a **necessary-condition count**, not a positive existence claim.

For a complete no-go it is enough to designate ONE degree-two block per skeleton, fix its `{AABB,ABAB}` class and test all 12 cross-pair perfect matchings. This covers both possible anti-phase choices by the outer-port-swap argument, and deliberately **does not restrict** any of the other six blocks to anti-phase: they retain all eleven legal classes. Therefore this test is logically more permissive than imposing all 1,384 local necessities and cannot accidentally exclude a real solution.

## 4. Exact nonlinear right-sixblock SAT/UNSAT verifier

Remove the designated two-outer-port degree-two H block. The six remaining fourpoles are connected by NINE ordinary edges and expose SIX physical semiedges: four originally outer ports and the two cut semiedges `a,b`.

Independently enumerate ALL `3^9=19,683` colour assignments to those nine interblock wires. For every right block enumerate each locally consistent four-semiedge colour orbit from `AAAA,AABB,ABAB,ABBA`. Group them into an ordered six-vector `p` of local orbit types, recording the EXACT `729`-bit physical support of its right six outer colours. This is a physically sound existential composition, not a Klein-four linear envelope approximation.

For a right-state `R=(r_0,r_1,r_2,r_3,a,b)`, join it with **all** colour-compatible H states from its specified anti-phase signature. This produces a set of Boolean outcomes under a chosen one of the 12 cross-logical pairings on the final six external ports. The outcome is BAD if ANY proper joined colouring gives a forbidden equality bit. A full Good sevenblock cannot select any BAD six-orbit vector.

If an assembly supported `100,010,001`, choose one actual full colouring witness for each bit, inducing three individually SAFE right-six-orbit vectors. Let their per-block orbit-type unions be `U_v`. Each is contained in the selected true (2-,3-,or4-orbit) physical fourpole class. The exact support relation is monotone when orbit types are added, so no BAD six-vector is enabled by `U`. At each singleton `U_v` extend by ONE of at most three other orbit types contained in the hypothetical actual class. The result is a legal minimal 11-class signature assignment with all three witnesses and no forbidden colouring. Conversely any such assignment gives a positive physical boundary composition because all 11 classes are physically realizable. Therefore testing ALL three-witness tuples and singleton extensions is a **sound and complete SAT/UNSAT test** for each designated skeleton/pairing/anti-phase case.

The standalone verifier also contains a positive synthetic triple-witness SAT regression; it is not hard-coded to return UNSAT.

## 5. Exhaustive computed certificate

The 40 skeletons ×12 pairings = **480** exact negative checks each preserve six completely unrestricted right constituent fourpole signatures. This is the independent finite census (small enough to be repeated from source):

| Check category | Exact count |
| --- | ---: |
| Surviving first-two GOOD witness pairs | 315,782 |
| Third GOOD witness triples tested | **22,063,552** |
| Triple unions passing immediate BAD check | 414,690 |
| Required minimal singleton orbit extensions checked | **3,812,910** |
| Full GOOD-only threebit class assignments | **0** |

The script checks the exact counter vector and fails if it changes unexpectedly. The actual search was independently executed in two 20-skeleton batches during this iteration; the first took 17.99 seconds, the second 19.56 seconds, and both returned zero SAT witnesses.

Combining this exhaustive finite result with the existing all-size 3+3 bridge obstruction (15 skeletons) and previously proven exact sevenblock 3-edge-connected no-go (4 skeletons) establishes the main theorem for **all 59 simple connected** sevenblock elevenjoin skeletons.

The raw number of class+pairing combinations logically covered is

    59 × 15 × 11^7 = 17,246,146,335.

This is a number of options excluded by exact proof and symbolic compression, **NOT** a count of directly executed assignments.

## Scientific firewall and follow-up

This DOES NOT settle the existence of a full 108-state cubic sixpole with arbitrary topology: parallel edges between fourpole blocks, self-joins requiring changed decomposition, >=8 constituent fourpoles and fully indecomposable cubic cores remain outside this grammar.

The previously independently verified physically connected simple BRIDGELESS n28 two-bit sixpole (100/010, 72 physical tuples, 144 complete colourings) remains valid and unchanged; bit 001 is still absent.

The NEXT mathematically legitimate direction is the sevenblock **MULTIGRAPH** skeleton grammar with parallel joins, or irreducible cores that resist fourpole signature decomposition. In every case a full physical gadget must show all 108 ordered boundary colour tuples and zero forbidden states. Neither a universal polynomial native `SolveLinearCubicXSAT` algorithm nor a P vs NP solution follows from this exact finite-grammar negative result.

**Provenance:** new scripts and GitHub workflow committed on the research branch. Independently observed completed GitHub Actions **SUCCESS is NOT yet available** and must not be claimed.
