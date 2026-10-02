#!/usr/bin/env python3
"""Regression checks for R5 E9 exact Levi small-separator composition.

1. Exhaustively verifies CUT-COMP-1 on K_{3,3} with
   K(row)={1}, K(column)={0,3}, using a nontrivial 4-edge cut.
2. Verifies the three-state transfer law for the stitched TD(3,3) family,
   including Fibonacci witness counts.

This is a theorem regression, not a universal solver.
"""

from itertools import product


def k33():
    # vertices 0,1,2 = rows; 3,4,5 = columns
    edges = [(r, c) for r in range(3) for c in range(3, 6)]
    return list(range(6)), edges


def K(v):
    return {1} if v < 3 else {0, 3}


def degree_ok(vertices, chosen_edges):
    deg = {v: 0 for v in vertices}
    for u, v in chosen_edges:
        deg[u] += 1
        deg[v] += 1
    return all(deg[v] in K(v) for v in vertices)


def all_global_factors(vertices, edges):
    ans = set()
    for bits in product((0, 1), repeat=len(edges)):
        chosen = frozenset(e for e, b in zip(edges, bits) if b)
        if degree_ok(vertices, chosen):
            ans.add(chosen)
    return ans


def local_feasible(side, internal_edges, cut_edges, y):
    crossing_degree = {v: 0 for v in side}
    for e, bit in zip(cut_edges, y):
        if not bit:
            continue
        u, v = e
        if u in crossing_degree:
            crossing_degree[u] += 1
        if v in crossing_degree:
            crossing_degree[v] += 1

    witnesses = []
    for bits in product((0, 1), repeat=len(internal_edges)):
        chosen = frozenset(e for e, b in zip(internal_edges, bits) if b)
        internal_degree = {v: 0 for v in side}
        for u, v in chosen:
            internal_degree[u] += 1
            internal_degree[v] += 1
        good = True
        for v in side:
            total = internal_degree[v] + crossing_degree[v]
            if total not in K(v):
                good = False
                break
        if good:
            witnesses.append(chosen)
    return witnesses


def verify_cut_comp():
    vertices, edges = k33()
    S = {0, 3}
    T = set(vertices) - S
    internal_S = [e for e in edges if e[0] in S and e[1] in S]
    internal_T = [e for e in edges if e[0] in T and e[1] in T]
    cut = [e for e in edges if (e[0] in S) ^ (e[1] in S)]
    assert len(cut) == 4

    reconstructed = set()
    accepted_states = []
    for y in product((0, 1), repeat=len(cut)):
        ws = local_feasible(S, internal_S, cut, y)
        wt = local_feasible(T, internal_T, cut, y)
        if ws and wt:
            accepted_states.append(y)
        selected_cut = frozenset(e for e, b in zip(cut, y) if b)
        for fs in ws:
            for ft in wt:
                reconstructed.add(fs | ft | selected_cut)

    global_factors = all_global_factors(vertices, edges)
    assert reconstructed == global_factors
    # K3,3 factors are exactly the three full stars at the column vertices.
    assert len(global_factors) == 3
    assert accepted_states


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def verify_td33_transfer():
    # State values are the block-constant kernel values (a,b,c).
    states = {
        "X": (2, -1, -1),
        "Y": (-1, 2, -1),
        "Z": (-1, -1, 2),
    }
    transitions = {}
    for s, (_, b, _) in states.items():
        transitions[s] = []
        for t, (a2, _, _) in states.items():
            if b == a2:
                transitions[s].append(t)

    assert transitions == {
        "X": ["Y", "Z"],
        "Y": ["X"],
        "Z": ["Y", "Z"],
    }

    counts = {s: 1 for s in states}
    totals = [sum(counts.values())]
    for m in range(2, 11):
        new = {t: 0 for t in states}
        for s, count in counts.items():
            for t in transitions[s]:
                new[t] += count
        counts = new
        totals.append(sum(counts.values()))

    for m, total in enumerate(totals, start=1):
        assert total == fib(m + 3), (m, total, fib(m + 3))


def main():
    verify_cut_comp()
    verify_td33_transfer()
    print("R5_E9_LEVI_SMALL_SEPARATOR_EXACT_COMPOSITION = PASS")
    print("CUT-COMP-1 exhaustive K3,3 replay = PASS")
    print("TD33 transfer counts F_(m+3), m=1..10 = PASS")
    print("E8_D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
