#!/usr/bin/env python3
import itertools

MOD = 3


def norm_edge(u, v):
    return (u, v) if u < v else (v, u)


def connected(n, edges):
    if n == 0:
        return True
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    seen = {0}; stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u); stack.append(u)
    return len(seen) == n


def oriented_edges(edges):
    return sorted(norm_edge(u, v) for u, v in edges)


def tension_from_coloring(n, edges, coloring):
    return tuple((coloring[v] - coloring[u]) % MOD for u, v in oriented_edges(edges))


def proper(n, edges, coloring):
    return all(coloring[u] != coloring[v] for u, v in edges)


def all_rooted_colorings(n, edges):
    for tail in itertools.product(range(MOD), repeat=max(0, n - 1)):
        c = (0,) + tail if n else ()
        if proper(n, edges, c):
            yield c


def spanning_tree(n, edges):
    adj = {v: [] for v in range(n)}
    for e in oriented_edges(edges):
        u, v = e
        adj[u].append((v, e)); adj[v].append((u, e))
    parent = {0: None}; pedge = {}; stack = [0]
    while stack:
        v = stack.pop()
        for u, e in adj[v]:
            if u not in parent:
                parent[u] = v; pedge[u] = e; stack.append(u)
    assert len(parent) == n
    return {pedge[v] for v in range(1, n)}


def integrate_tension(n, edges, t):
    E = oriented_edges(edges)
    val = dict(zip(E, t))
    adj = {v: [] for v in range(n)}
    for u, v in E:
        adj[u].append((v, (u, v), +1))
        adj[v].append((u, (u, v), -1))
    c = {0: 0}; stack = [0]
    while stack:
        v = stack.pop()
        for u, e, direction in adj[v]:
            # Stored t_e = c_head-c_tail for tail=min endpoint, head=max endpoint.
            if u in c:
                continue
            if direction == +1:
                c[u] = (c[v] + val[e]) % MOD
            else:
                c[u] = (c[v] - val[e]) % MOD
            stack.append(u)
    if len(c) != n:
        return None
    candidate = tuple(c[i] for i in range(n))
    if tension_from_coloring(n, edges, candidate) != tuple(t):
        return None
    return candidate


def all_tensions_bruteforce(n, edges):
    E = oriented_edges(edges)
    out = set()
    for vals in itertools.product(range(MOD), repeat=len(E)):
        c = integrate_tension(n, edges, vals)
        if c is not None:
            out.add(vals)
    return out


def cycle_edges(cycle):
    return {norm_edge(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))}


def b_from_coloring(cycle, coloring):
    shift = coloring[cycle[0]]
    c = [(coloring[v] - shift) % MOD for v in cycle]
    b = []
    for i in range(len(cycle)):
        d = (c[(i + 1) % len(cycle)] - c[i]) % MOD
        assert d in (1, 2)
        b.append(d - 1)
    return tuple(b)


def interval_accepts(n, edges, cycle, b):
    pos = {v: i for i, v in enumerate(cycle)}
    if (n + sum(b)) % MOD != 0:
        return False
    H = cycle_edges(cycle)
    for e in edges - H:
        u, v = e
        i, j = sorted((pos[u], pos[v]))
        if ((j - i) + sum(b[k] for k in range(i, j))) % MOD == 0:
            return False
    return True


def verify_connected_graph(n, edges, cycle=None):
    edges = {norm_edge(*e) for e in edges}
    assert connected(n, edges)
    rooted = list(all_rooted_colorings(n, edges))
    nz_tensions_from_colors = {tension_from_coloring(n, edges, c) for c in rooted}
    assert all(all(x != 0 for x in t) for t in nz_tensions_from_colors)

    all_t = all_tensions_bruteforce(n, edges)
    nz_all = {t for t in all_t if all(x != 0 for x in t)}
    assert nz_all == nz_tensions_from_colors
    # Root normalization gives a one-to-one map; without root there are exactly 3 shifts.
    assert len(rooted) == len(nz_all)

    if cycle is not None:
        assert cycle_edges(cycle) <= edges
        bs_from_colors = {b_from_coloring(cycle, c) for c in rooted}
        bs_carrier = {
            b for b in itertools.product((0, 1), repeat=n)
            if interval_accepts(n, edges, cycle, b)
        }
        assert bs_from_colors == bs_carrier


def controls():
    # Connected small graphs; brute-force tension enumeration remains tiny.
    verify_connected_graph(3, {(0,1),(1,2),(0,2)}, [0,1,2])
    verify_connected_graph(4, set(itertools.combinations(range(4), 2)), [0,1,2,3])
    verify_connected_graph(4, {(0,1),(1,2),(2,3),(3,0)}, [0,1,2,3])
    # K5 has no nowhere-zero GF3 tension.
    K5 = set(itertools.combinations(range(5), 2))
    rooted = list(all_rooted_colorings(5, K5))
    assert rooted == []
    bs = [b for b in itertools.product((0,1), repeat=5) if interval_accepts(5, K5, list(range(5)), b)]
    assert bs == []


def main():
    controls()
    print("PASS rooted proper COLOR3 <-> nowhere-zero GF3 tension on exact small controls")
    print("PASS every nowhere-zero tension integrates uniquely after root color is fixed")
    print("PASS Hamiltonian interval-F3 coordinates equal the tension carrier")
    print("PASS K5 has neither a 3-coloring, nowhere-zero GF3 tension, nor interval witness")


if __name__ == '__main__':
    main()
