#!/usr/bin/env python3
"""Exact v8.6.1 checker: alternate constant-width path decomposition of the v8.6 witness family."""


def graph_edges(m):
    assert m >= 3
    order = [(r, i) for r in range(4) for i in range(m)]
    H = set()
    for j in range(4 * m):
        H.add(frozenset((order[j], order[(j + 1) % (4 * m)])))
    C = set()
    for i in range(m):
        cyc = [(0, i), (1, i), (2, i), (3, i)]
        for j in range(4):
            C.add(frozenset((cyc[j], cyc[(j + 1) % 4])))
    assert H.isdisjoint(C)
    return order, H | C


def columns(m):
    return [{(r, i) for r in range(4)} for i in range(m)]


def path_bags(m):
    cols = columns(m)
    return [cols[0] | cols[i] | cols[i + 1] for i in range(m - 1)]


def verify(m):
    vertices, edges = graph_edges(m)
    V = set(vertices)
    bags = path_bags(m)

    # Graph control: simple 4-regular graph with 4m vertices and 8m edges.
    assert len(V) == 4 * m
    assert len(edges) == 8 * m
    deg = {v: 0 for v in V}
    for e in edges:
        assert len(e) == 2
        u, v = tuple(e)
        assert u != v
        deg[u] += 1
        deg[v] += 1
    assert set(deg.values()) == {4}

    # Path-decomposition axiom 1: all vertices are covered.
    covered = set().union(*bags)
    assert covered == V

    # Axiom 2: every edge is contained in at least one bag.
    uncovered = []
    for e in edges:
        if not any(e <= bag for bag in bags):
            uncovered.append(e)
    assert not uncovered

    # Axiom 3: bags containing any fixed vertex form a contiguous interval.
    for v in V:
        idx = [i for i, bag in enumerate(bags) if v in bag]
        assert idx
        assert idx == list(range(idx[0], idx[-1] + 1))

    max_bag = max(len(bag) for bag in bags)
    assert max_bag <= 12
    width = max_bag - 1
    assert width <= 11

    # Strong structural shape controls from the closed form B_i=C_0 U C_i U C_{i+1}.
    cols = columns(m)
    assert bags[0] == cols[0] | cols[1]
    assert len(bags[0]) == 8
    if m >= 3:
        for i in range(1, m - 1):
            assert bags[i] == cols[0] | cols[i] | cols[i + 1]
            assert len(bags[i]) == 12

    # The four long Hamiltonian connector/wrap edges all lie between C_{m-1} and C_0
    # and must therefore be covered by the final bag.
    long_edges = {
        frozenset(((0, m - 1), (1, 0))),
        frozenset(((1, m - 1), (2, 0))),
        frozenset(((2, m - 1), (3, 0))),
        frozenset(((3, m - 1), (0, 0))),
    }
    assert long_edges <= edges
    assert all(e <= bags[-1] for e in long_edges)

    return len(V), len(edges), len(bags), max_bag, width


for m in (3, 5, 7, 11, 25):
    n, e, nb, max_bag, width = verify(m)
    print(
        f"PASS: m={m}, n={n}, edges={e}, bags={nb}, "
        f"max_bag_size={max_bag}, pathwidth_upper_bound={width}"
    )

print("PASS: every vertex is covered, every edge is covered, and every vertex has contiguous bag support")
print("PASS: explicit bags B_i=C_0 union C_i union C_{i+1} give pathwidth(G_m)<=11 for every m>=3")
print("PASS: v8.6 exponential supplied-Hamiltonian prefix state count is therefore order-specific, not a global width lower bound")
print("VERDICT: EXPLICIT_V8_6_WITNESS_FAMILY_HAS_PATHWIDTH_AT_MOST_11")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
