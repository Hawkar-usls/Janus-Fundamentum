# R5 — nonlinear fourpole synthesis beyond bridges: 3-block cycle vs 4-block K4-minus-edge

Date: 2026-10-14 (Kyiv).
Research branch: research/r5-kempe-coupled-involutions-20261013.

Executable 3-block cycle and n10 two-bit: [r5_exactone_bridge_grammar_two_bit_n10.py](../experiments/r5_exactone_bridge_grammar_two_bit_n10.py)
Executable K4-minus-edge 4-block grammar: [r5_exactone_fourpole_k4minus_grammar_n24.py](../experiments/r5_exactone_fourpole_k4minus_grammar_n24.py)
Prior n10 full proof: [r5_two_bit_n10_bridge_grammar_checkpoint_20261014.md](r5_two_bit_n10_bridge_grammar_checkpoint_20261014.md)

## Exact semantic tool

For arbitrary properly colourable connected cubic 4-pole B with ordered four semiedges, its entire properly 3-edge-colourable physical boundary relation is one of the eleven sets formed by choosing any 2,3,4 of four S3 orbits AAAA,AABB,ABAB,ABBA. The catalogue is ALL-SIZE and each class has a concrete physical simple connected cubic representative.

To glue interfaces between distinct multipoles, take natural join (existentially quantify the common edge colour and require the two connected semiedge colours to agree). The exact exposed physical relation of the assembled graph is exactly the resulting colour relation. This holds for arbitrary interior sizes, provided the physical graph is formed by distinct blocks and ordinary edges as specified.

We ALWAYS check all FIFTEEN perfect logical pairings of the exposed six semiedges, not merely a single convenient pairing. A relation is GOOD-only if all proper colourings have equality bits in {100,010,001}; an UNCOLOURABLE relation is not counted as a successful gadget.

## Theorem 1 — triangular cyclic assembly of three fourpoles never carries 2 or 3 GOOD bits

Take three independent connected colourable cubic 4poles A,B,C. Identify the interface colours through THREE ordinary edges:

    A[2]=B[3], B[2]=C[3], C[2]=A[3],

leaving A[0],A[1],B[0],B[1],C[0],C[1] as the six outer semiedges.

This block skeleton is a TRIANGLE, so there are no BRIDGES **between** its three blocks. (There may be bridges INSIDE individual blocks.)

The possible physical colour relations are fully described by all 11^3=1331 triples of fourpole signatures. Test each with 15 logical perfect port matchings, giving exactly 19,965 combinations:

    empty physical colour relation:      45
    GOOD-only and only bit 100:          39
    GOOD-only and only bit 010:          33
    GOOD-only and only bit 001:          45
    GOOD-only with TWO bits:              0
    GOOD-only with THREE bits:            0.

All 117 nonempty GOOD-only cases have exactly 36 physical six-port tuples. Every other nonempty combination admits at least one forbidden Boolean equality pattern. This finite abstract interface calculation proves the claim for arbitrarily large internal blocks, not merely n<=some bound.

## Theorem 2 — four fourpoles with K4-minus-edge interfaces CAN support TWO GOOD bits, but not all THREE

Take independent connected properly colourable cubic 4poles A,B,C,D. Join five ordinary interface edges with these equal-colour constraints:

    A[2]=C[1],  A[3]=D[1],
    B[2]=C[2],  B[3]=D[2],
    C[3]=D[3].

The remaining exposed ports in order are

    A[0],A[1],B[0],B[1],C[0],D[0].

The 4-block connectivity skeleton is K4 with one edge deleted: every block has internal degree 2 or 3 and the skeleton itself is bridgeless. The exact semantic relation is a five-variable, 3-colour existential join, with 3^5 possibilities for the interface colour assignments.

Exhaustively enumerate all 11^4=14,641 assignments of 4pole signature classes and all 15 perfect logical pairings of six remaining physical ports. This yields 219,615 class/pairing configurations; 70 of the 14,641 class assignments have EMPTY physical colour support, accounting for 1,050 empty pairings. The remaining 218,565 paired compositions have nonempty support.

Among ALL 219,615 exact tests, the complete GOOD-only distribution is:

    exactly one bit 100:     340
    exactly one bit 010:     274
    exactly one bit 001:     213
    exactly two bits 100/010:  2
    exactly two bits 001/010:  2
    exactly all three bits:    0.

All 827 one-bit cases have 36 physical outer states. All FOUR two-bit cases have exactly 72 physical outer states, thirty-six for each bit. Thus simple cyclic 3-block composition is insufficient, while the extra cross-link in the 4-block K4-e grammar enables genuine two-bit semantics.

A full three-bit 108-state gadget remains NOT CONSTRUCTED within this grammar. This is an ALL-SIZE result only for this specifically fixed 4-pole composition graph. It does not exclude more complex 4-pole compositions or an arbitrary indivisible cubic sixpole.

## Independent real physical 24-vertex witness for a K4-e two-bit composition

Use FOUR copies of the six-vertex, seven-internal-edge connected cubic HETERO_TWO fourpole:

    internal edges:
      (0,1),(0,2),(0,3),(1,2),(3,4),(3,5),(4,5)
    ordered original semiedge roots:
      (1,2,4,5).

Each block has precisely twelve 4-port physical colour states, each extending to exactly one internal colouring.

Offset the vertex indices of the A,B,C,D blocks by 0,6,12,18 respectively. Reorder each block's four semiedges before joining:

    A: permutation (0,2,1,3), signature class 4
    B: permutation (0,1,2,3), signature class 5
    C: permutation (0,2,3,1), signature class 3
    D: permutation (0,2,3,1), signature class 3,

where catalogue classes are ordered by all size-2 combinations of (AAAA,AABB,ABAB,ABBA).

Connect the same FIVE K4-e interfaces described above. The resulting graph has exactly 24 ordinary internal vertices, 33 distinct ordinary edges and SIX DISTINCT physical semiedge roots:

    (1,4,7,8,13,19).

Use logical PAIRS OF PHYSICAL PORT INDICES

    ((0,5),(1,4),(2,3)).

Independent full graph edge-colouring DFS (not only 4pole join) gives precisely 72 different full 3-edge-colourings, 72 different ordered outer port tuples, each with multiplicity 1, and Boolean counts

    100:36, 010:36, all other Boolean values:0.

**Critical firewall:** Although the connectivity of the four-block SKELETON is bridgeless, the constructed FULL 24-vertex graph has exactly ONE internal ordinary bridge, between vertices (6,9) INSIDE block B. Thus this is NOT a physically bridgeless two-bit gadget, nor a counterexample to the all-size bridge theorem. Replacing the internal HETERO_TWO block with a genuinely bridgeless same-signature fourpole (if possible) would be a meaningful next experiment; one must verify both the semantic signature and the absence of newly induced forbidden colour states.

## Context for the universal solver objective

These theorems constitute exact finite-interface semantic composition results for a bounded block grammar, not a polynomial method for discovering such a decomposition or computing an arbitrary large unknown block's signature. The earlier fixed-sixport NP-completeness reduction demonstrates the difficulty of the general nonlinear support problem.

No genuine 108-state cubic full Exact-One 6pole has been built or excluded for all n. No polynomial native SolveLinearCubicXSAT is built; P vs NP stays OPEN. No native PC-degree lower bound follows.

**CI provenance:** source tests and workflow changes committed; a new successful GitHub Actions run must be independently observed before labelling these automated regressions PASS.
