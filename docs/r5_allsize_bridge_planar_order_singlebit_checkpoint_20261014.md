# R5 — Universal bridge restriction, planar port-order obstruction and real n=14 single-bit sixpole

Date: 2026-10-14 (Kyiv). Research branch: research/r5-kempe-coupled-involutions-20261013.

Executable: [r5_kempe_allsize_bridge_planar_order_singlebit_gate.py](../experiments/r5_kempe_allsize_bridge_planar_order_singlebit_gate.py)

## Scope and status

A **full** Exact-One sixpole is a connected simple cubic graph with six distinctly rooted, ordered physical semiedges, paired (0,1),(2,3),(4,5), whose complete 3-edge-colouring boundary relation has Boolean equality bits *exactly* {100,010,001}. The previously proved forced-Kempe saturation lemma entails that such a graph necessarily realizes **all 108 even-parity physical boundary colour tuples** with those bits.

Results below are NECESSARY properties of any full gadget, plus a concrete honest single-bit witness. There is still no all-size proof that a full gadget is impossible and no general polynomial algorithm for native JANUS SCL.

## Theorem A — every minimum-size full Exact-One sixpole is bridgeless

Map the three proper 3-edge colours to the three nonzero elements 1,2,3 of the additive Klein four group F2^2. At each cubic vertex the three incident colours xor to zero. Suppose e is an ordinary bridge of a putative full Exact-One sixpole M. Removing e divides its vertices, and each side contains a subset K of the six labelled outer ports. Summing the Kirchhoff identities over one side yields

    colour(e) = xor_{i in K} colour(port_i).

Since colour(e) is never zero, every actual boundary tuple must have nonzero xor over K.

However the 108-state full Exact-One target has these **independently verifiable** properties:

- For every labelled subset K of size 2 there is an allowed state where its two colours are equal, so the xor is zero.
- For every labelled triple K there is an allowed state where its three colours are all distinct (1 xor 2 xor 3 =0).
- For every labelled 4-set K there is an allowed state with zero xor, because its complementary 2-set can be chosen equal and the xor over all 6 ports is always zero.
- For K=empty or all six, the xor is zero in all allowed states by parity/conservation.

Thus no bridge may have a component containing 0,2,3,4 or 6 of the six physical ports. A bridge must partition the six labelled physical ports **1+5**.

Let H be the one-port side. As a cubic two-pole (outer port plus cut edge), parity implies its two exposed colours are equal in every proper colouring. Since the full gadget has a colouring, H is colourable; global S3 recolouring implies it admits every common colour.

If the *other* endpoint of the bridge is also a vertex incident to a second external semiedge, the colour of that second physical port is always **different** from the bridge colour (proper trivalent vertex), and hence different from the original one-port H colour. But the required 108-state target admits a state where **any chosen two** physical ports have equal colours. Contradiction.

Otherwise the other bridge endpoint has no outer semiedge. Delete the whole one-port H side together with e and install the dangling outer semiedge of H at the other endpoint of the deleted bridge. The resulting sixpole has fewer vertices, remains simple and connected, remains cubic, has exactly six distinctly rooted outer semiedges and the *identical ordered full physical boundary relation*. The equality of the relation uses that H is a colourable 2-pole and every common colour extends to a colouring of H.

Therefore a **minimum-order** full Exact-One sixpole is **bridgeless**. This conclusion is universal in n and does not assume planarity or bounded search.

Important: an arbitrary (non-minimal) full gadget, if one exists, may be inflated by a pendant colourable 2-pole, so we do NOT claim every full Exact-One graph has no bridges.

## Theorem B — 52/60 outer-face port orders cannot support planar full Exact-One

Let M be embedded in a topological disk with all six physical dangling semiedges meeting the boundary in a cyclic order. In each properly 3-edge-coloured graph, the (a,b)-coloured alternating terminal paths are internally vertex-disjoint, so the matching of their endpoints on the boundary is **noncrossing**.

On the 108-state full Exact-One target and each of the 3 unordered colour pairs there are 324 state/colour decisions. A matching of the exposed endpoints is GOOD-safe when switching ANY subset of its disjoint paths preserves a one-hot bit. Exhaustive finite classification yields exactly 252 decisions with one UNIQUE GOOD-safe matching and 72 with five possible GOOD-safe matchings. The unique choices are therefore FORCED in every real global-GOOD-only full colouring.

There are only (6-1)!/2=60 distinct unoriented cyclic orders of six labelled ports. Evaluate whether any of the 252 uniquely forced GOOD-safe Kempe matchings has a crossing pair of chords. The result is:

    number of forced crossing decisions : cyclic port orders
    0                                   : 8
    48                                  : 12
    60                                  : 24
    96                                  : 12
    108                                 : 4

Exactly the 8 surviving orders have the original paired port labels (0,1), (2,3), (4,5) **each adjacent around the circular boundary**. In every one of the remaining 52 orders, the 108-state saturation promise forces an unrealizable crossing of two vertex-disjoint alternating Kempe paths.

Hence for EVERY n:

    Planar-disk full Exact-One sixpole =>
    all three logical port pairs consecutive on the outer boundary.

This is a NECESSARY topological condition, **not** a proof that any one of the 8 surviving orders is realizable.

## Constructive positive control — honest n14 GOOD-only single-bit sixpole

The 11-class connected cubic 4-pole atlas contains:

- SIX_VERTEX_HETERO_TWO, on vertices 0..5, ordered semiedge roots (1,2,4,5);
- PETERSEN_MINUS_ADJACENT_TWO_ISO, on vertices 0..7, ordered semiedge roots (0,2,3,4).

Shift the second block's internal vertex indices by +6 and connect its semiedge root 0+6=6 to the first block's root 2 by an ordinary edge (2,6), eliminating those two semiedges. The resulting connected simple cubic sixpole has n=14 internal vertices, m=18 ordinary edges and six DISTINCT ordered external roots

    ports = (1,4,5,8,9,10).

Take the ordered logical pairings

    ((0,5),(1,2),(3,4)).

Independent full 3-edge-colouring DFS over the entire 18-edge graph gives precisely **36 distinct physical sixport colour tuples**, and for every one of them the logical truth bit is exactly

    001.

This is an ACTUAL colourable cubic sixpole with GOOD-only support, but it realizes **only one** of the three required truth bits. Hence the stronger conjecture "every nonempty globally GOOD-only sixpole must realize all three one-hot bits" is FALSE. It does not contradict the bridge theorem: its one bridge separates 3+3 physical ports, and it is not a full Exact-One gadget.

It is important that all six semiedge roots are DISTINCT and the ordinary graph is simple and connected; no illicit port identification or abstract boundary-only matching is used.

## Physical 1+5 bridge regression

Begin with bare C6 and attach the colourable four-vertex Diamond K4-minus-edge two-pole between the old physical port 0 and the C6 vertex 0, transporting that outer port to one fresh internal vertex. The new graph has n=10, one 1+5 bridge, and EXACTLY the same 63 ordered physical outer-port tuples as C6. This concretely demonstrates that arbitrary nonminimal colourable sixpoles may have pendant bridges; the correct theorem concerns MINIMAL full Exact-One gadgets only.

## Scientific consequence and next universal barrier

The three all-size conclusions are independent of how many internal vertices a sixpole has:

1. A minimum-order *full* Exact-One gadget has no bridges (simple all-size physical condition).
2. A planar *disk* full gadget can expose logical paired ports only as three adjacent boundary pairs (52/60 cyclic orders excluded).
3. A good-only **single-bit** physical sixpole DOES exist (n14), so saturation *within* one bit does NOT imply the appearance of the other two bits.

The full three-bit 108-state physical gadget remains OPEN, and there is no proof that every bridge-free or admissibly embedded core has a forbidden state. The results do not construct native PC-degree lower bounds or polynomial SolveLinearCubicXSAT. P versus NP remains OPEN.

Verification: exact 108-state finite classification, 60 outer orders, full physical colour DFS on n14 and pendant n10. CI run conclusion UNVERIFIED until a completed GitHub Actions job can be read.
