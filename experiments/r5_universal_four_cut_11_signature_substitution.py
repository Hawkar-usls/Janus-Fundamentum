#!/usr/bin/env python3
"""R5: universal *semantic* replacement of colourable port-free 4-cut blocks.

THEOREM. A properly 3-edge-colourable cubic four-pole B has a boundary
colour relation equal to that of one connected SIMPLE four-pole B* with
at most eight internal vertices, with four DISTINCT semiedge roots.

Proof:
  (1) Parity gives four S3-orbits of ordered boundary colours:
      1111, 1122, 1212, 1221.
  (2) A Kempe switch from a suitable terminal changes its orbit,
      hence any nonempty colour set contains >=2 orbits.
  (3) The 11 possible subsets of cardinality 2,3,4 are ALL realised
      by the five explicit templates below and port permutations.
  (4) A gluing across the four ports depends ONLY on the full ordered
      four-colour relation. Same relation => same six-port relation.
  (5) Using disjoint new vertices for B*, including distinct port
      roots, preserves simplicity, connectedness and cubic degrees
      in an ambient simple connected cubic six-pole.

Therefore any minimum-order open Exact-One gadget has no port-free
4-edge-cut component B with |B|>=10, since B* is strictly smaller.
For an n=18 candidate this also reduces to the independently excluded
n<=16 family; n=18 exclusion requires the source promise of an exact
colourable gadget. This is NOT a test of block colourability.

IMPORTANT: This theorem preserves boundary signatures, NOT PC degree;
there is no claimed uniform polynomial-time procedure to discover
the full colour relation of an arbitrary four-pole.

Finite regression checks:
* Construct each of the 11 signature templates by permuting 5 cores.
* Recolour the 11 outer-C6 substitution examples (6 physical ports).
* Inflate one 4-vertex template by TWO diamonds into an n=12 block,
  insert it into C6 -> n=18 6-pole, shrink exactly to the n=10 fixture.
* Exhaustively scan all 4-edge sets in an earlier constructed 18-vertex
  sixpole, finding 5 port-free 10-vertex blocks. Independently compare
  all six physical port colours before and after each replacement.
"""

from collections import Counter
from itertools import combinations, permutations

from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    assert_simple_cubic_multipole,
    colour_states, connected, component_cut, graph_cycle6,
    inflate_edge_diamond, inflate_trivalent_vertex_triangle, norm,
)
from r5_universal_n18_portfree_smallcut_structural_filter import components


def templates():
    return {
        "FOUR_CYCLE_THREE_WITH_1111": (
            ((0, 1), (0, 2), (1, 3), (2, 3)),
            (0, 1, 2, 3),
        ),
        "SIX_VERTEX_HETERO_TWO": (
            ((0, 1), (0, 2), (0, 3), (1, 2), (3, 4), (3, 5), (4, 5)),
            (1, 2, 4, 5),
        ),
        "SIX_VERTEX_THREE_WITHOUT_1111": (
            ((0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 5), (4, 5)),
            (1, 2, 3, 5),
        ),
        "PETERSEN_MINUS_ADJACENT_TWO_ISO": (
            ((0, 1), (0, 5), (1, 2), (1, 6), (2, 7),
             (3, 5), (3, 6), (4, 6), (4, 7), (5, 7)),
            (0, 2, 3, 4),
        ),
        "EIGHT_VERTEX_ALL_FOUR": (
            ((0, 4), (0, 6), (1, 3), (1, 5), (2, 4),
             (2, 7), (3, 7), (4, 5), (5, 6), (6, 7)),
            (0, 1, 2, 3),
        ),
    }


def orbit(ports):
    renaming = {}
    return tuple(renaming.setdefault(c, len(renaming)+1) for c in ports)


ALL_FOUR = {
    (1, 1, 1, 1), (1, 1, 2, 2), (1, 2, 1, 2), (1, 2, 2, 1)
}


def orbit_set(colours):
    return frozenset(orbit(s) for s in colours)


def build_catalogue():
    signatures = {}
    for name, (edges, roots) in templates().items():
        vertices = assert_simple_cubic_multipole(edges, roots)
        assert len(vertices) in (4, 6, 8)
        assert len(roots) == len(set(roots)) == 4
        assert connected(vertices, edges)
        colours, _ = colour_states(edges, roots)
        assert colours
        for permutation in permutations(range(4)):
            r = tuple(roots[i] for i in permutation)
            reordered = frozenset(tuple(s[i] for i in permutation)
                                   for s in colours)
            signature = orbit_set(reordered)
            assert 2 <= len(signature) <= 4 and signature <= ALL_FOUR
            signatures.setdefault(signature, (name, edges, r))
    assert len(signatures) == 11
    assert Counter(map(len, signatures)) == Counter({2: 6, 3: 4, 4: 1})
    for k in (2, 3, 4):
        assert all(sub in signatures
                   for sub in combinations(sorted(ALL_FOUR), k))
    print("FOUR_POLE_COMPLETE_SIGNATURE_CATALOGUE 11/11 PASS")
    print("FOUR_POLE_SIZES_MAX_8 TRUE")
    return signatures


def glue_to_cycle6(block_edges, block_roots):
    outer, ports = graph_cycle6()
    outside = set(outer) - {norm(0, 1), norm(3, 4)}
    assert len(outside) == 4
    outer_n = 6
    block_n = len(assert_simple_cubic_multipole(block_edges, block_roots))
    assert set(v for e in block_edges for v in e) == set(range(block_n))
    internal = {norm(a+outer_n, b+outer_n) for a,b in block_edges}
    cuts = {norm(v, r+outer_n) for v,r in zip((0, 1, 3, 4), block_roots)}
    full = frozenset(outside | internal | cuts)
    assert len(assert_simple_cubic_multipole(full, ports)) == block_n + 6
    assert connected(set(v for e in full for v in e), full)
    return full, ports


def replace_4block(E, ports, B, catalogue):
    V = assert_simple_cubic_multipole(E, ports)
    assert B and not (set(B) & set(ports))
    cut, inside, outside, inside_roots, outside_roots = component_cut(E, B)
    assert len(cut) == 4 and connected(B, inside)
    inside_states, _ = colour_states(inside, inside_roots)
    assert inside_states, "block colouring is a required precondition"
    sig = orbit_set(inside_states)
    assert sig in catalogue, ("signature not in universal catalogue", sig)
    label, edges, roots = catalogue[sig]
    new_start = max(V) + 1
    shifted = tuple(norm(a+new_start, b+new_start) for a,b in edges)
    ports4 = tuple(norm(w, r+new_start) for w,r in zip(outside_roots, roots))
    Q = frozenset(outside + shifted + ports4)
    newV = assert_simple_cubic_multipole(Q, ports)
    assert connected(newV, Q)
    assert len(newV) == len(V) - len(B) + len(set(x for e in edges for x in e))
    return Q, label, sig


def find_portfree_4cut_large_blocks(E, ports, min_block=10):
    """O(m^4(n+m)) graph-only detection; no colouring oracle."""
    V = assert_simple_cubic_multipole(E, ports)
    assert connected(V, E)
    E = tuple(sorted(E))
    port_set = set(ports)
    found = {}
    for chosen in combinations(E, 4):
        after = set(E) - set(chosen)
        for B in components(V, after):
            if B in found or len(B) < min_block or B & port_set:
                continue
            if len(B) >= len(V):
                continue
            # After removing chosen edges, no other edge crosses B.
            if all((a in B) != (b in B) for a,b in chosen):
                found[B] = chosen
    return found


def check():
    catalogue = build_catalogue()

    # All 11 signature classes are represented by legal open sixpoles.
    signature_counts = Counter()
    for sig, (label, edges, roots) in catalogue.items():
        fixture, ports = glue_to_cycle6(edges, roots)
        physical, _ = colour_states(fixture, ports)
        assert physical
        signature_counts[len(sig)] += 1
    assert signature_counts == Counter({2:6, 3:4, 4:1})
    print("ALL_11_SIMPLE_CONNECTED_SIXPOLE_FIXTURES PASS")

    # 4 -> 8 -> 12 internal vertices, preserving exact 4-pole relation.
    base_edges, base_roots = templates()["FOUR_CYCLE_THREE_WITH_1111"]
    expanded, _ = inflate_edge_diamond(
        frozenset(base_edges), norm(0, 1), first_new=4)
    expanded, _ = inflate_edge_diamond(
        expanded, norm(6, 7), first_new=8)
    assert len(assert_simple_cubic_multipole(expanded, base_roots)) == 12
    base_4, _ = colour_states(base_edges, base_roots)
    large_4, _ = colour_states(expanded, base_roots)
    assert base_4 == large_4
    base6, ports = glue_to_cycle6(base_edges, base_roots)
    large6, _ = glue_to_cycle6(expanded, base_roots)
    state_base, _ = colour_states(base6, ports)
    state_large, _ = colour_states(large6, ports)
    assert len(state_base) == 87
    assert state_base == state_large
    Q, label, sig = replace_4block(large6, ports, frozenset(range(6, 18)), catalogue)
    qcol, _ = colour_states(Q, ports)
    assert qcol == state_base and len(Q) < len(large6)
    print("EXPLICIT_N18_TO_N10_FOURCUT_COLOUR_SIGNATURE_87 PASS")

    # Previously checked nested-diamond + triangle n18 sample.
    C6, ports = graph_cycle6()
    a, _ = inflate_edge_diamond(C6, norm(0, 1), first_new=6)
    b, _ = inflate_edge_diamond(a, norm(8, 9), first_new=10)
    c, _ = inflate_trivalent_vertex_triangle(b, 10, first_new=14)
    E18, _ = inflate_trivalent_vertex_triangle(c, 14, first_new=17)
    V18 = assert_simple_cubic_multipole(E18, ports)
    assert len(V18) == 18
    cuts = find_portfree_4cut_large_blocks(E18, ports)
    assert len(cuts) == 5 and all(len(B) == 10 for B in cuts)
    before, _ = colour_states(E18, ports)
    assert before
    result_sizes = []
    for B in cuts:
        quotient, label, sig = replace_4block(E18, ports, B, catalogue)
        after, _ = colour_states(quotient, ports)
        assert after == before
        result_sizes.append(len(assert_simple_cubic_multipole(quotient, ports)))
    assert all(12 <= n <= 16 for n in result_sizes), result_sizes
    print("N18_GRAPH_ONLY_PORTFREE_K4_CUTS", len(cuts), "PASS")
    print("N18_K4_FIVE_EXACT_SIXPORT_RETRACTIONS",
          dict(Counter(result_sizes)), "PASS")
    print("THEOREM: ANY_COLOURABLE_PORTFREE_K4_BLOCK_EQUIV_TO_AT_MOST_8")
    print("NOT_PC_DEGREE_ONE; NOT_POLYNOMIAL_BLOCK_COLOUR_ORACLE")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    check()
