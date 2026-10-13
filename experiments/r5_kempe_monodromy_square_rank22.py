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
from itertools import combinations

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


def voltage_cover_connected(vertices, base_edges, selected):
    """Check a nontrivial abstract 2-sheet cover with a single odd edge."""
    lifts = {(v, sheet) for v in vertices for sheet in (0, 1)}
    lifted_edges = set()
    for u, v in base_edges:
        parity = int((u, v) == selected)
        for sheet in (0, 1):
            lifted_edges.add(edge((u, sheet), (v, sheet ^ parity)))
    assert len(lifts) == 72 and len(lifted_edges) == 144
    return connected(lifts, lifted_edges)


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
        assert voltage_cover_connected(V, E, selected)
        print('MONODROMY_SQUARES', b, {
            'boundary_states':len(V), 'forced_edges':len(E),
            'square_faces':len(S), 'mixed_squares':types['mixed'],
            'balanced_squares':types['all_balanced'],
            'edge_disjoint_square_edges':len(appearances),
            'other_edges':len(untouched), 'square_f2_rank':rank_f2(masks),
            'pi1_before_rank':beta1, 'pi1_after_rank':free_rank,
            'nontrivial_two_sheet_square_flat_cover':True
        }, flush=True)

    print('ALL_3_EXACTONE_BITS: 45_EDGE_DISJOINT_COMMUTATION_SQUARES PASS')
    print('ALL_SIZE_CONDITIONAL_MONODROMY: F37 -> F22 PASS')
    print('NO_REAL_SIXPOLE_FROM_ABSTRACT_COVER; NO_EXACTONE_NO_GO')
    print('SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN')


if __name__ == '__main__':
    test()
