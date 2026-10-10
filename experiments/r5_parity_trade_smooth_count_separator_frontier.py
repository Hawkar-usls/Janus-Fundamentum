#!/usr/bin/env python3
"""
Parity/isolation trade frontier control.

Verifies on an 18x18 square-cubic-linear Exact-One carrier that:
  * three explicit perfect matchings exist;
  * a prescribed connected cubic bipartite graph is realized exactly as
    the trade graph between two of them;
  * exhaustive local-trade supports coincide with connected induced
    cubic bipartite subgraphs of the conflict graph on this control.

No third-party dependencies.
"""

from collections import Counter, deque
from itertools import combinations


def connected(adj, nodes):
    nodes = set(nodes)
    if not nodes:
        return False
    root = next(iter(nodes))
    seen = {root}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v in nodes and v not in seen:
                seen.add(v)
                q.append(v)
    return seen == nodes


def bipartition(adj, nodes):
    nodes = set(nodes)
    color = {}
    for root in nodes:
        if root in color:
            continue
        color[root] = 0
        q = deque([root])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in nodes:
                    continue
                if v not in color:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return None
    return color


def build_cubic_bipartite(r=6):
    assert r % 3 == 0
    # Three disjoint perfect matchings of the bipartite graph.
    offsets = (0, 1, 3)
    edges = set()
    classes = []
    for off in offsets:
        factor = []
        for i in range(r):
            e = (i, (i + off) % r)
            assert e not in edges
            edges.add(e)
            factor.append(e)
        classes.append(factor)

    adj_l = {i: set() for i in range(r)}
    adj_r = {j: set() for j in range(r)}
    for i, j in edges:
        adj_l[i].add(j)
        adj_r[j].add(i)

    assert all(len(x) == 3 for x in adj_l.values())
    assert all(len(x) == 3 for x in adj_r.values())

    # Connectedness.
    seen = {("L", 0)}
    q = deque([("L", 0)])
    while q:
        side, u = q.popleft()
        nxt = (
            [("R", v) for v in adj_l[u]]
            if side == "L"
            else [("L", v) for v in adj_r[u]]
        )
        for z in nxt:
            if z not in seen:
                seen.add(z)
                q.append(z)
    assert len(seen) == 2 * r
    return sorted(edges), classes, adj_l, adj_r


def build_hypergraph(r=6):
    b_edges, classes, adj_l, adj_r = build_cubic_bipartite(r)
    edge_id = {e: k for k, e in enumerate(b_edges)}

    h = []
    labels = []

    # M: left stars.
    for i in range(r):
        h.append(tuple(sorted(edge_id[(i, j)] for j in adj_l[i])))
        labels.append(("M", i))

    # N: right stars.
    for j in range(r):
        h.append(tuple(sorted(edge_id[(i, j)] for i in adj_r[j])))
        labels.append(("N", j))

    # P: split each 1-factor into triples.  Every triple is a matching in B.
    for ci, factor in enumerate(classes):
        factor = sorted(factor)
        for a in range(0, r, 3):
            h.append(tuple(sorted(edge_id[e] for e in factor[a : a + 3])))
            labels.append(("P", ci, a // 3))

    return b_edges, h, labels


def validate_target(b_edges, h):
    vertices = set(range(len(b_edges)))

    assert len(h) == len(vertices)  # square
    assert all(len(set(e)) == 3 for e in h)  # 3-uniform

    degree = Counter(v for e in h for v in e)
    assert set(degree) == vertices
    assert set(degree.values()) == {3}  # 3-regular

    for a, b in combinations(range(len(h)), 2):
        assert len(set(h[a]) & set(h[b])) <= 1  # linear

    r = len(vertices) // 3
    families = [
        list(range(0, r)),
        list(range(r, 2 * r)),
        list(range(2 * r, 3 * r)),
    ]

    for fam in families:
        covered = Counter(v for i in fam for v in h[i])
        assert set(covered) == vertices
        assert set(covered.values()) == {1}

    return families


def conflict_graph(h):
    adj = [set() for _ in h]
    for i, j in combinations(range(len(h)), 2):
        if set(h[i]) & set(h[j]):
            adj[i].add(j)
            adj[j].add(i)

    assert all(len(x) == 6 for x in adj)
    return adj


def local_trade_from_bipartition(h, color):
    side_a = [u for u, c in color.items() if c == 0]
    side_b = [u for u, c in color.items() if c == 1]

    cover_a = Counter(v for u in side_a for v in h[u])
    cover_b = Counter(v for u in side_b for v in h[u])

    return (
        cover_a == cover_b
        and all(x == 1 for x in cover_a.values())
        and all(x == 1 for x in cover_b.values())
    )


def enumerate_trade_supports(h, adj):
    n = len(h)
    out = []

    for mask in range(1, 1 << n):
        k = mask.bit_count()
        if k < 6 or k % 2:
            continue

        support = [i for i in range(n) if (mask >> i) & 1]
        support_set = set(support)

        if not connected(adj, support):
            continue

        if any(
            sum(v in support_set for v in adj[u]) != 3
            for u in support
        ):
            continue

        color = bipartition(adj, support)
        if color is None:
            continue

        assert local_trade_from_bipartition(h, color)
        out.append(tuple(support))

    return out


def verify_embedded_trade(b_edges, h, adj, families):
    m_family, n_family, _ = families
    support = m_family + n_family
    support_set = set(support)

    assert connected(adj, support)
    color = bipartition(adj, support)
    assert color is not None
    assert all(
        sum(v in support_set for v in adj[u]) == 3
        for u in support
    )
    assert local_trade_from_bipartition(h, color)

    # M_i -- N_j in the conflict graph iff (i,j) is an edge of B.
    b_set = set(b_edges)
    r = len(m_family)
    for i in range(r):
        for j in range(r):
            got = (r + j) in adj[i]
            want = (i, j) in b_set
            assert got == want


def main():
    b_edges, h, labels = build_hypergraph(6)
    families = validate_target(b_edges, h)
    adj = conflict_graph(h)

    verify_embedded_trade(b_edges, h, adj, families)

    trades = enumerate_trade_supports(h, adj)
    volumes = Counter(len(support) // 2 for support in trades)

    assert len(trades) == 6
    assert volumes == Counter({6: 4, 3: 2})

    print("TARGET_VERTICES =", len(b_edges))
    print("TARGET_HYPEREDGES =", len(h))
    print("SQUARE_3UNIFORM_3REGULAR_LINEAR = PASS")
    print("THREE_EXPLICIT_PERFECT_MATCHINGS = PASS")
    print("EMBEDDED_CUBIC_BIPARTITE_TRADE = PASS")
    print("CONNECTED_CUBIC_BIPARTITE_SUPPORT_LOCAL_TRADE_CONTROL = PASS")
    print("EXHAUSTIVE_CONTROL_TRADE_SUPPORTS =", len(trades))
    print("EXHAUSTIVE_CONTROL_TRADE_VOLUMES =", dict(sorted(volumes.items())))
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
