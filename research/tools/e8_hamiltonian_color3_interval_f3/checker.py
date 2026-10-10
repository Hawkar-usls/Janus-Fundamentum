#!/usr/bin/env python3
import itertools
import random


def norm_edge(u, v):
    assert u != v
    return (u, v) if u < v else (v, u)


def normalize_graph(n, edges):
    E = {norm_edge(u, v) for u, v in edges}
    assert all(0 <= u < n and 0 <= v < n for u, v in E)
    return E


def cycle_edges(cycle):
    n = len(cycle)
    return {norm_edge(cycle[i], cycle[(i + 1) % n]) for i in range(n)}


def check_hamiltonian(n, edges, cycle):
    assert len(cycle) == n
    assert set(cycle) == set(range(n))
    H = cycle_edges(cycle)
    assert H <= edges
    return H


def remap_to_cycle_positions(n, edges, cycle):
    pos = {v: i for i, v in enumerate(cycle)}
    return {norm_edge(pos[u], pos[v]) for u, v in edges}


def brute_3color(n, edges):
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    col = {}

    def rec(i):
        if i == n:
            return dict(col)
        v = order[i]
        used = {col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c
                ans = rec(i + 1)
                if ans is not None:
                    return ans
                del col[v]
        return None

    return rec(0)


def carrier_constraints(n, pos_edges):
    H = cycle_edges(list(range(n)))
    chords = sorted(pos_edges - H)
    return chords


def carrier_accepts(n, pos_edges, b):
    assert len(b) == n and all(x in (0, 1) for x in b)
    if (n + sum(b)) % 3 != 0:
        return False
    for i, j in carrier_constraints(n, pos_edges):
        s = sum(b[k] for k in range(i, j)) % 3
        forbidden = (-(j - i)) % 3
        if s == forbidden:
            return False
    return True


def colors_from_b(n, cycle, b):
    color_pos = [0] * n
    for i in range(n - 1):
        color_pos[i + 1] = (color_pos[i] + 1 + b[i]) % 3
    # b[n-1] participates only in the wrap closure; verify it closes to c_0.
    assert (color_pos[n - 1] + 1 + b[n - 1]) % 3 == 0
    return {cycle[i]: color_pos[i] for i in range(n)}


def b_from_colors(n, cycle, coloring):
    # Normalize the global color shift so c(v_0)=0.
    shift = coloring[cycle[0]]
    c = [(coloring[cycle[i]] - shift) % 3 for i in range(n)]
    b = []
    for i in range(n):
        d = (c[(i + 1) % n] - c[i]) % 3
        assert d in (1, 2)
        b.append(d - 1)
    return tuple(b)


def valid_coloring(n, edges, coloring):
    return set(coloring) == set(range(n)) and all(coloring[u] != coloring[v] for u, v in edges)


def brute_carrier(n, pos_edges):
    for b in itertools.product((0, 1), repeat=n):
        if carrier_accepts(n, pos_edges, b):
            return b
    return None


def verify_instance(n, edges, cycle, expect_4regular=None):
    edges = normalize_graph(n, edges)
    H = check_hamiltonian(n, edges, cycle)
    pos_edges = remap_to_cycle_positions(n, edges, cycle)

    graph_col = brute_3color(n, edges)
    b = brute_carrier(n, pos_edges)
    assert (graph_col is not None) == (b is not None), (n, edges, cycle, graph_col, b)

    if graph_col is not None:
        b2 = b_from_colors(n, cycle, graph_col)
        assert carrier_accepts(n, pos_edges, b2)
        reconstructed = colors_from_b(n, cycle, b2)
        assert valid_coloring(n, edges, reconstructed)

    if b is not None:
        reconstructed = colors_from_b(n, cycle, b)
        assert valid_coloring(n, edges, reconstructed)
        b3 = b_from_colors(n, cycle, reconstructed)
        assert b3 == tuple(b)

    if expect_4regular is not None:
        deg = [0] * n
        for u, v in edges:
            deg[u] += 1
            deg[v] += 1
        assert all(d == 4 for d in deg) == expect_4regular
        if expect_4regular:
            complement = edges - H
            cdeg = [0] * n
            for u, v in complement:
                cdeg[u] += 1
                cdeg[v] += 1
            assert all(d == 2 for d in cdeg)


def fixed_controls():
    # Bare Hamiltonian cycles C_n are always 3-colourable for n>=3.
    for n in range(3, 9):
        cyc = list(range(n))
        verify_instance(n, cycle_edges(cyc), cyc)

    # K4: Hamiltonian and 4-chromatic.
    n = 4
    K4 = set(itertools.combinations(range(n), 2))
    verify_instance(n, K4, list(range(n)))

    # K5: 4-regular Hamiltonian and not 3-colourable. Its complement to H is C5.
    n = 5
    K5 = set(itertools.combinations(range(n), 2))
    verify_instance(n, K5, list(range(n)), expect_4regular=True)

    # Octahedral graph K_{2,2,2}: 4-regular, Hamiltonian and 3-colourable.
    parts = [{0, 1}, {2, 3}, {4, 5}]
    E = set()
    for i in range(3):
        for j in range(i + 1, 3):
            for u in parts[i]:
                for v in parts[j]:
                    E.add(norm_edge(u, v))
    cycle = [0, 2, 4, 1, 3, 5]
    verify_instance(6, E, cycle, expect_4regular=True)


def random_hamiltonian_controls(seed=20260930):
    rng = random.Random(seed)
    checked = 0
    for n in range(4, 8):
        H = cycle_edges(list(range(n)))
        possible = sorted(set(itertools.combinations(range(n), 2)) - H)
        for _ in range(30):
            E = set(H)
            for e in possible:
                if rng.random() < 0.45:
                    E.add(e)
            verify_instance(n, E, list(range(n)))
            checked += 1
    return checked


def main():
    fixed_controls()
    checked = random_hamiltonian_controls()
    print("PASS Hamiltonian COLOR3 iff Boolean interval-F3 avoidance on fixed controls")
    print(f"PASS {checked} random Hamiltonian graph/carrier brute-force equivalence controls")
    print("PASS graph->b and b->graph witness reconstruction")
    print("PASS K5 and octahedral 4-regular complement-to-H 2-factor controls")


if __name__ == '__main__':
    main()
