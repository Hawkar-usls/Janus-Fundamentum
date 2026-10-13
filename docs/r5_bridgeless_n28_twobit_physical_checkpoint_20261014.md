# R5 checkpoint: bridge-free two-bit cubic sixpole (2026-10-14)

Executable: [full physical verifier](../experiments/r5_exactone_bridgeless_n28_twobit_constructive.py). Independent n10 controls: [exhaustive C++ census](../experiments/r5_exactone_n10_exhaustive_goodonly_census.cpp) and [independent enumeration and bridge-healing script](../experiments/r5_exactone_n10_independent_degree_orbit_bridge_healing.py).

## Real physical result

A connected simple cubic sixpole with **n=28**, 39 ordinary edges, six DISTINCT semiedge roots **(1,4,6,9,17,23)**, and logical pairs of PORT INDICES **((0,5),(1,4),(2,3))** has zero ordinary bridges. Independent exhaustive edge-3-colouring DFS gives **144 complete proper colourings**, precisely **72 distinct ordered physical sixport colour tuples**, **2 completions per tuple**. Truth bits: **100:36**, **010:36**, all others including **001,000,111:0**. First requested goal, remove every bridge without losing the 72-state GOOD-only relation, is CONSTRUCTED.

### Exact 39 ordinary edges

(0,1),(0,2),(0,3),(1,2),(2,20),(3,4),(3,5),(4,5),(5,26),(6,7),(6,10),(7,11),(7,21),(8,12),(8,13),(8,27),(9,12),(9,14),(10,13),(10,15),(11,14),(11,15),(12,15),(13,14),(16,17),(16,18),(16,19),(17,18),(18,24),(19,20),(19,21),(20,21),(22,23),(22,24),(22,25),(23,24),(25,26),(25,27),(26,27).

## Mechanism: replace exactly one internal fourpole

Original real n24 K4-minus-edge four-block assembly had only bridge (6,9), INSIDE its B fourpole. The old B: six vertices; internal edges (0,1),(0,2),(0,3),(1,2),(3,4),(3,5),(4,5), ordered semiedge roots (1,2,4,5). Its exact physical fourport relation contains 12 tuples.

New B*: TEN vertices; internal edges (0,1),(0,4),(1,5),(2,6),(2,7),(3,6),(3,8),(4,7),(4,9),(5,8),(5,9),(6,9),(7,8); ordered semiedge roots (0,3,1,2). It is SIMPLE CONNECTED AND BRIDGELESS and has **EXACTLY the same 12 ordered fourport physical tuples** as old B, with two internal continuations per tuple instead of one.

Replacing old B by B* in the n24 fourblock assembly produces the above n28 graph, with block vertex ranges A:0–5, B*:6–15, C:16–21, D:22–27. Semantic equality of full fourport relations proves the whole sixport relation is preserved. Direct full n28 DFS independently checks the 72/144 counts and explicit one-edge-deletion connectivity checks verify the absence of physical bridges.

Complete independent small-fourpole enumeration of ALL simple labelled connected cubic fourpoles with four distinct semiedge roots on n=4,6,8 examines respectively **3,54,6057** degree-sequence graphs and excludes any bridgefree realization of the old HETERO_TWO two-orbit signature (including all port permutations). The new n10 B* is therefore a smallest possible **bridgeless replacement of this interface type**, not a minimum full sixpole.

## Independent n10 sixpole census

Separate from fourpole replacement, an exact C++ exhaustive generator of ALL labelled simple n10 cubic SIXPOLES with six distinct semiedge roots finds **888292 total**, **866520 connected**, **657720 connected bridgeless**, **208800 connected bridged**. There are exactly **144 nonempty GOOD-only sixpoles**, all **BRIDGED** and all with exactly two allowed bits (48 for each two-bit choice); no connected n10 bridgeless GOOD-only instance and no n10 full three-bit gadget. A separate memoized combinatorial degree recurrence independently obtains the total 888292; the 144 relabelings of the old two-bit n10 source under logical pair and internal-vertex symmetries account for all 144 outcomes.

Local bridge-healing negative controls: 72 immediate edge switches of the original n10 seed, 1060 n14 and 9908 n18 single cross-shore switches after 1/2 Diamond inflations, and 278 n12 / 2388 n14 / 25728 n16 single cross-shore switches after 1/2/3 triangle vertex inflations. All specified bridgeless candidates have a forbidden fully proper colouring. These are restricted grammar attempts, NOT full n>=12 enumeration or universal no-go.

## Open research gate

The **third bit 001 remains absent**. A full three-input Exact-One sixpole would require **all 108 physical tuples** on ONE legitimate simple connected cubic graph, and none of the forbidden bits. That gadget remains OPEN. General polynomial SolveLinearCubicXSAT is NOT CONSTRUCTED; P versus NP remains OPEN. GitHub Actions SUCCESS has not been independently observed; new source-level checks are to be verified in CI.