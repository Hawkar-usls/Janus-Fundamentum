#!/usr/bin/env python3
"""R5: mandatory Kempe commutation squares, F37 -> F22 monodromy quotient.

This script constructs the full 108-boundary-state forced single-path
Kempe graph from the earlier certified finite matching rule (252 forced
state/pair choices, 432 directed edges) and computes its 2-complex.

For EACH of b=100,010,001:
* forced boundary component: |V|=36, |E|=72, beta1=37;
* same-colour-pair independent-path commutation squares: 15, each
  involving exactly four distinct states;
* 12 mixed (two 222 and two 42) and 3 all-balanced (four 222);
* square 1-chains are edge-disjoint => their F2 rank =15;
* their union uses 60 edges; 12 edges are unused;
* attaching the 15 square 2-cells gives pi1=F_22, by elementary
  collapse of one unique edge and its 2-cell for each square.
* a connected 2-sheet VOLTAGE GRAPH cover satisfying all 15 square
  relations can be built by assigning odd voltage to one non-bridge
  edge outside all squares.

ALL-SIZE CONDITIONAL CONSEQUENCE:
For any genuine cubic sixpole whose *entire* three-edge-colouring
boundary bit signature is subset of {100,010,001}, every forced
boundary edge lifts to an involution between full-colouring fibres
and each of the 15 (a,b)-same-pair squares has TRIVIAL monodromy:
the two actual bicolour paths are disjoint and their flips commute.
Therefore monodromy factors through F_22, not only F_37.

LIMIT:
This is a necessary covering-space property, NOT a sixpole gadget
and NOT an obstruction to the existence of an Exact-One gadget.
The explicit two-sheet abstract cover is NOT asserted realizable
as proper edge-colourings of any physical cubic graph.
PC-degree lower bounds and SolveLinearCubicXSAT remain OPEN.

Run:
python -u experiments/r5_kempe_monodromy_square_rank22.py
"""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product

from r5_kempe_sixpole_saturation_or_forbidden_gate import (
    GOOD, bits, parity_states, forced_transition_graph, toggled_boundary
)


def edge(a, b):
    assert a != b
    return tuple(sorted((a, b)))


def connected(vertices, edges):
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    start = min(vertices)
    seen = {start}
    queue = [start]
    while queue:
        for v in adj[queue.pop()]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return len(seen) == len(vertices)


def rank_f2(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            bit = vector.bit_length() - 1
            if bit in pivots:
                vector ^= pivots[bit]
            else:
                pivots[bit] = vector
                break
    return len(pivots)


def forced_squares(graph):
    """Find canonical squares of two disjoint (a,b) terminal paths."""
    squares = {}
    for s in graph:
        for ab in combinations(range(3), 2):
            outgoing = [(t, ends) for t, pair, ends in graph[s]
                        if pair == ab]
            if len(outgoing) != 2:
                continue
            (t1, end1), (t2, end2) = outgoing
            assert set(end1).isdisjoint(end2)
            u = toggled_boundary(s, ab, (end1, end2), 3)
            cycle = (s, t1, u, t2)
            assert len(set(cycle)) == 4, (s, ab, cycle)
            assert (u, ab, end2) in graph[t1], (s, ab, cycle)
            assert (u, ab, end1) in graph[t2], (s, ab, cycle)
            assert (s, ab, end1) in graph[t1]
            assert (s, ab, end2) in graph[t2]
            key = frozenset(cycle)
            if key in squares:
                assert squares[key][0] == ab
            else:
                squares[key] = (ab, cycle)
    assert len(squares) == 45, len(squares)
    return list(squares.values())


def voltage_cover_connected(vertices, base_edges, odd_edges):
    """Check a nontrivial abstract 2-sheet cover with a single odd edge."""
    lifts = {(v, sheet) for v in vertices for sheet in (0, 1)}
    lifted_edges = set()
    for u, v in base_edges:
        parity = int((u, v) in odd_edges)
        for sheet in (0, 1):
            lifted_edges.add(edge((u, sheet), (v, sheet ^ parity)))
    assert len(lifts) == 72 and len(lifted_edges) == 144
    return connected(lifts, lifted_edges)


def bit_preserving_symmetry_orbits(vertices, base_edges, untouched):
    """Full S3 colours x (C2^3 semiport flips ⋊ S2 unequal-pair swap)."""
    pair_slots = ((0, 1), (2, 3), (4, 5))
    actions = []
    for swapflags in product((0, 1), repeat=3):
        for last_two in (0, 1):
            ps = [list(x) for x in pair_slots]
            if last_two:
                ps[1], ps[2] = ps[2], ps[1]
            ps = [tuple(reversed(x)) if swapflags[i] else tuple(x)
                  for i, x in enumerate(ps)]
            perm = tuple(i for pair in ps for i in pair)
            for ren in permutations(range(3)):
                actions.append((perm, ren))
    assert len(actions) == 96
    def transform(s, action):
        pp, ren = action
        return tuple(ren[s[i]] for i in pp)
    for action in actions:
        assert {transform(s, action) for s in vertices} == vertices
        assert {edge(transform(u, action), transform(v, action))
                for u, v in base_edges} == base_edges
        assert {edge(transform(u, action), transform(v, action))
                for u, v in untouched} == untouched
    remain = set(base_edges)
    orbit_lengths = []
    while remain:
        root = min(remain)
        orbit = {edge(transform(root[0], action),
                      transform(root[1], action))
                 for action in actions}
        assert orbit <= remain
        orbit_lengths.append((len(orbit), len(orbit & untouched)))
        remain -= orbit
    assert sorted(orbit_lengths) == [
        (12, 0), (12, 12), (24, 0), (24, 0)
    ] or sorted(orbit_lengths) == [
        (12, 0), (12, 12), (24, 24), (24, 24)
    ]
    # All three types of square edges are a union of non-odd orbits.
    assert sorted(len_o for len_o, _ in orbit_lengths) == [12, 12, 24, 24]
    assert sum(odd for _, odd in orbit_lengths) == 12
    return orbit_lengths


def shortest_odd_voltage_loop(vertices, base_edges, odd_edges):
    """Shortest closed boundary walk changing Z2 sheet of the cover."""
    start = min(vertices)
    adj = defaultdict(list)
    for u, v in base_edges:
        p = int((u, v) in odd_edges)
        adj[u].append((v, p))
        adj[v].append((u, p))
    queue = [(start, 0)]
    seen = {(start, 0): 0}
    for v, sheet in queue:
        if (v, sheet) == (start, 1):
            return seen[(v, sheet)]
        for w, p in adj[v]:
            nxt = (w, sheet ^ p)
            if nxt not in seen:
                seen[nxt] = seen[(v, sheet)] + 1
                queue.append(nxt)
    raise AssertionError("voltage cover disconnected")


def test():
    graph = forced_transition_graph()
    states = parity_states()
    squares = forced_squares(graph)
    assert len(states) == 108
    all_edges = {edge(s, t) for s, moves in graph.items()
                 for t, _, _ in moves}
    assert len(all_edges) == 216

    for b in sorted(GOOD):
        V = {s for s in states if bits(s) == b}
        E = {e for e in all_edges if bits(e[0]) == b}
        assert len(V) == 36 and len(E) == 72 and connected(V, E)
        S = [(ab, cyc) for ab, cyc in squares if bits(cyc[0]) == b]
        assert len(S) == 15
        appearances = Counter()
        types = Counter()
        masks = []
        edge_ids = {e: idx for idx, e in enumerate(sorted(E))}
        for ab, (a, x, c, y) in S:
            cls = ['222' if sorted(Counter(v).values()) == [2, 2, 2]
                   else '42' for v in (a, x, c, y)]
            types['all_balanced' if all(z == '222' for z in cls)
                  else 'mixed'] += 1
            mask = 0
            for u, v in ((a, x), (x, c), (c, y), (y, a)):
                e = edge(u, v)
                assert e in E
                appearances[e] += 1
                mask |= (1 << edge_ids[e])
            assert mask.bit_count() == 4
            masks.append(mask)
        assert types == Counter({'mixed': 12, 'all_balanced': 3}), types
        assert len(appearances) == 60
        assert set(appearances.values()) == {1}
        assert rank_f2(masks) == 15

        untouched = E - set(appearances)
        assert len(untouched) == 12
        assert all(sorted(Counter(u).values()) == [2, 4] and
                   sorted(Counter(v).values()) == [2, 4]
                   for u, v in untouched)
        beta1 = len(E) - len(V) + 1
        assert beta1 == 37
        # Every square has a unique edge, so collapse each 2-cell with
        # one of its edges. No other 2-cell is incident to that edge.
        # The resulting connected 1-complex has E-15 edges, V vertices.
        free_rank = (len(E) - len(S)) - len(V) + 1
        assert free_rank == 22
        # One uncovered edge can have odd Z2-voltage and all squares
        # remain at zero voltage. Nonbridge => connected 2-sheet cover.
        selected = min(untouched)
        assert connected(V, E - {selected})
        assert voltage_cover_connected(V, E, {selected})
        orbits = bit_preserving_symmetry_orbits(V, E, untouched)
        # Assign odd voltage to ALL 12 non-square edges; invariant under
        # the full 96-element colour+port boundary stabilizer.
        assert voltage_cover_connected(V, E, untouched)
        assert shortest_odd_voltage_loop(V, E, untouched) == 5
        print('MONODROMY_SQUARES', b, {
            'boundary_states':len(V), 'forced_edges':len(E),
            'square_faces':len(S), 'mixed_squares':types['mixed'],
            'balanced_squares':types['all_balanced'],
            'edge_disjoint_square_edges':len(appearances),
            'other_edges':len(untouched), 'square_f2_rank':rank_f2(masks),
            'pi1_before_rank':beta1, 'pi1_after_rank':free_rank,
            'nontrivial_two_sheet_square_flat_cover':True,
            'colour_port_symmetry_group_size':96,
            'symmetry_edge_orbits':sorted(orbits),
            'symmetric_two_sheet_odd_loop_length':5
        }, flush=True)

    print('ALL_3_EXACTONE_BITS: 45_EDGE_DISJOINT_COMMUTATION_SQUARES PASS')
    print('ALL_SIZE_CONDITIONAL_MONODROMY: F37 -> F22 PASS')
    print('S3_x_16_PORT_SYMMETRY_INVARIANT_NONTRIVIAL_TWO_SHEET_COVER PASS')
    print('NO_REAL_SIXPOLE_FROM_ABSTRACT_COVER; NO_EXACTONE_NO_GO')
    print('SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN')


if __name__ == '__main__':
    test()
