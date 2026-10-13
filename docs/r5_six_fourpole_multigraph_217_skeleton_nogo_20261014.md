# R5 checkpoint — six-fourpole EXACT-ONE obstruction INCLUDING parallel block joins

Date: 2026-10-14. Research branch: research/r5-kempe-coupled-involutions-20261013.

Verifiers: [all fourteen SIMPLE skeletons](../experiments/r5_exactone_six_fourpole_nineedge_simple_skeleton_gate.py) and [all 217 LOOPLESS MULTIGRAPH skeletons](../experiments/r5_exactone_six_fourpole_multigraph_all_skeletons_gate.py). Prior physical positive control: [bridgeless n28 GOOD-only 72-state two-bit graph](../experiments/r5_exactone_bridgeless_n28_twobit_constructive.py).

## Exact result and validity boundary

Build a cubic sixpole from exactly **six independently connected colourable cubic FOURPOLES**, with arbitrary internal sizes, by identifying pairs of semiedges to make exactly **nine ordinary interblock edges**, each joining two DIFFERENT constituent fourpole blocks. The loopless six-vertex block multigraph may have parallel edges. Six semiedges remain exposed and may be logically paired in ANY of the fifteen perfect matchings.

Assume the independently proved R5 all-size fourpole catalogue: every colourable connected cubic fourpole's full ordered physical boundary 3-edge-colour relation is a nonempty union of **two, three or four** of the four parity-compatible S3 orbit classes AAAA, AABB, ABAB, ABBA, and every one of the eleven such unions has a physical representative.

**Theorem:** NO assembly in this ENTIRE six-fourpole/nine-join LOOPLESS multigraph grammar can realize all three onehot Boolean bit values `100,010,001` while excluding all non-onehot bit values. Consequently NONE realizes the desired complete **108-state** physical Exact-One sixport relation.

This theorem is for **arbitrary numbers of internal vertices of its six fourpole constituents**, but NOT for a generic indecomposable cubic sixpole; it does not cover >=7 fourpole blocks, connections of two ports belonging to the SAME block (a loop on the skeleton), or arbitrary multipole architecture.

## Exhaustive loopless skeleton generation

Nine undirected edges among six distinguishable block vertices, with parallel edges allowed but NO self-loops, can be represented by multisets of size nine drawn from C(6,2)=15 possible edge types. The degree of each block is at most four because it originally has four semiedges; demand connectedness.

The standalone verifier enumerates ALL such degree-feasible connected labelled edge multisets, counting **110,170**. Under complete permutations of the six block vertices (restricted by degree for efficient canonicalization), the 110,170 choices collapse into exactly **217 nonisomorphic** block skeletons:

| Skeleton class | Nonisomorphic skeletons |
| --- | ---: |
| Simple | 14 |
| With parallel edges | 203 |
| **Total** | **217** |

By a direct small graph edge-cut computation, **122** skeletons have edge connectivity one, **93** have connectivity two, and **2** have connectivity three. Of the 122 bridge skeletons, **114** have an ordinary bridge with an exposed port split 3+3 (3 simple, 111 with parallel edges). The prior all-size R5 bridge theorem excludes two or three GOOD-only truth bits for ANY such physical cubic sixpole; hence these 114 skeletons are discarded using a proved universal result, not an unrecorded heuristic.

For the remaining 103 skeletons: 8 have a 1+5 bridge, 93 have edge connectivity two, and 2 have edge connectivity three. Every one undergoes the COMPLETE exact nonlinear orbit-witness compatibility test below.

## Exhaustive colour relation using compressed three-witness monotonicity

For each skeleton enumerate ALL 3^9 assignments of its nine interblock edges to the three proper edge colours. Each block has d incident interblock edges and exactly 4-d exposed physical semiedges. Enumerate the local exposed colours and select only the four allowed 4port parity-orbits. Group the resulting globally compatible configurations by the SIX local orbit IDs (one of four at each block). For every such orbit-vector the verifier records a **729-bit exact support set** of possible ordered six-port physical colour tuples.

For any logical pairing P, a local orbit-vector is BAD if it admits any physical tuple whose equality bits are not one of {100,010,001}. A GOOD-only assembled graph may only use orbit-vectors that are individually safe.

If any 11-class assignment realized all three onehot bits without bad ones, choose ONE actual physical state for each of 100,010,001. These three complete colourings define three individually safe local orbit-vectors p,q,r. At each block, the union of their local orbit ID bits must lie in its selected 11-class mask.

Because physical relation composition is MONOTONE under adding local orbit support, the componentwise orbit union may not admit a BAD local orbit-vector. Each block signature must contain at least two orbits. If a union is a singleton at any block, extend it by ONE orbit from the actual block signature. There are at most three choices per singleton. Thus EVERY hypothetical legal full threebit assembly has a certificate consisting of three safe good-orbit vectors and <=3 choices per singleton block, with NO BAD orbit-vector covered by the selected orbit masks.

The verifier enumerates all such necessary certificates and finds NONE. This is complete without naively iterating billions of 11-class assignments.

### Sound symmetry reduction for the 15 logical pairings

Permuting any exposed physical semiedges belonging to the SAME fourpole block reorders that block's fourport coordinates. Because the allowed catalogue contains EVERY possible 2-,3-,4-orbit signature and is closed under permutations of fourport coordinates, the property of existence of a GOOD-only three-bit class assignment is INVARIANT under this external-port reordering. The verifier independently computes the orbit partition of all 15 perfect logical matchings under these within-block permutations and tests one representative of each orbit, checking that all 15 matchings are covered.

There are **716** logically complete representative (skeleton, pairing) checks across the 103 nonpruned skeletons, and an independent research replay inspected **27,988,176** candidate triples of safe local orbit-pattern witnesses (after the sound early rejection of pairs already allowing a forbidden configuration). Every completed check is negative.

| Stage | Count |
| --- | ---: |
| All canonical loopless six-block/nine-join skeletons | 217 |
| Bridge-3+3 skeletons excluded by prior theorem | 114 |
| Other skeletons given direct exact nonlinear check | 103 |
| Pairing-orbit representatives tested | 716 |
| Actual compressed good-witness triple checks (independent replay) | 27,988,176 |
| **Full three-bit GOOD-only compositions** | **0** |

This exact exhaustion logically covers

    217 × 15 × 11^6 = 5,766,431,055

possible skeleton/class/pairing selections without individually iterating every selection. Repeatedly count this as **covered possibilities**, NOT raw executed candidate tests.

## Strong structural corollary: 3-edge-connected skeletons

If six fourpole blocks have nine interblock joins and the loopless block multigraph is 3-edge-connected, all six vertices have degree at least three; total degree is eighteen, so EVERY vertex has degree exactly three. Were there a parallel pair between blocks u and v, the set {u,v} would be attached to the other four blocks by at most two edges, contradicting 3-edge-connectivity. Therefore such a block skeleton is necessarily SIMPLE, hence one of the triangular prism or K3,3. Both already fail the exact three-bit witness test.

This says NOTHING about arbitrary 3-edge-connected physical sixpoles without this six-fourpole decomposition.

## Relation to user objective

The **first construction goal** is already met by the REAL connected simple bridgeless n28 72-state two-bit sixpole (100/010, each 36 physical tuples, no forbidden tuples). A single actual graph supporting the **third missing bit 001**, preserving the other 72 states, and excluding forbidden physical colourings remains **NOT CONSTRUCTED**.

We have now excluded full 108-state assembly for this considerably larger SIX-fourpole/nine-join grammar, including all parallel-edge block joins. This frontier result prevents repeating invalid assembly attempts; it does **not** exclude larger fourpole networks, unreduced cubic cores, or arbitrary gadgets. The general P vs NP objective is untouched by a finite grammar result.

Provenance: source scripts and GitHub Actions workflow entries committed in research branch; **CI success remains UNVERIFIED** until an actual completed successful job is observed. General full Exact-One sixpole no-go OPEN; universal polynomial SolveLinearCubicXSAT NOT CONSTRUCTED; P vs NP OPEN.
