#!/usr/bin/env python3
"""Exact q=331 replay: balanced 4-critical gain obstructions and rank-13 Moser cover."""

from itertools import combinations, product

Q = 331
R = (-2) % Q


def orbit_minus2(q):
    out = []
    seen = set()
    x = 1
    r = (-2) % q
    while x not in seen:
        seen.add(x)
        out.append(x)
        x = (x * r) % q
    assert x == 1
    return out


O = orbit_minus2(Q)
assert len(O) == 15
IDX = {s: k for k, s in enumerate(O)}
S = tuple(sorted(set(O) | {(-s) % Q for s in O}))
assert len(S) == 30


def phi(c, d):
    d %= Q
    if d in IDX:
        return (-IDX[d] - c) % 3
    nd = (-d) % Q
    if nd in IDX:
        return (IDX[nd] + c) % 3
    return None


def connected(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return len(seen) == n


def is_3colorable(n, edges):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    color = [-1] * n

    def rec(i):
        if i == n:
            return True
        v = order[i]
        used = {color[u] for u in adj[v] if color[u] >= 0}
        for z in range(3):
            if z in used:
                continue
            color[v] = z
            if rec(i + 1):
                return True
            color[v] = -1
        return False

    return rec(0)


def edge4critical(n, edges):
    if not connected(n, edges):
        return False
    if is_3colorable(n, edges):
        return False
    for i in range(len(edges)):
        if not is_3colorable(n, edges[:i] + edges[i + 1:]):
            return False
    return True


def catalogue_counts_through_six():
    out = {}
    for n in (4, 5, 6):
        universe = list(combinations(range(n), 2))
        count = 0
        degree_profiles = {}
        for mask in range(1 << len(universe)):
            edges = [universe[i] for i in range(len(universe)) if (mask >> i) & 1]
            if not edge4critical(n, edges):
                continue
            count += 1
            deg = [0] * n
            for a, b in edges:
                deg[a] += 1
                deg[b] += 1
            prof = tuple(sorted(deg))
            degree_profiles[prof] = degree_profiles.get(prof, 0) + 1
        out[n] = (count, degree_profiles)
    return out


K4 = list(combinations(range(4), 2))
W5 = [(i, (i + 1) % 5) for i in range(5)] + [(5, i) for i in range(5)]
MOSER = [
    (0, 1), (0, 2), (1, 2), (1, 3), (2, 3),
    (0, 4), (0, 5), (4, 5), (4, 6), (5, 6),
    (3, 6),
]

assert edge4critical(4, K4)
assert edge4critical(6, W5)
assert edge4critical(7, MOSER)


def balanced_embeddings(c, n, edges):
    """All translation/gauge-normalized injective embeddings with vertex 0 -> 0, gauge 0 -> 0."""
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    assert connected(n, edges)

    x = [None] * n
    g = [None] * n
    x[0] = 0
    g[0] = 0
    used = {0}
    out = []
    nodes = 0

    def rec(done):
        nonlocal nodes
        nodes += 1
        if done == n:
            edge_set = frozenset(tuple(sorted((x[a], x[b]))) for a, b in edges)
            out.append((tuple(x), tuple(g), edge_set))
            return

        candidates = []
        for v in range(n):
            if x[v] is not None:
                continue
            assigned = [u for u in adj[v] if x[u] is not None]
            if assigned:
                candidates.append((len(assigned), -v, v, assigned))
        _, _, v, assigned = max(candidates)
        anchor = assigned[0]

        for d in S:
            xv = (x[anchor] + d) % Q
            if xv in used:
                continue
            gv = (g[anchor] + phi(c, d)) % 3
            ok = True
            for u in assigned[1:]:
                du = (xv - x[u]) % Q
                ph = phi(c, du)
                if ph is None or (g[u] + ph) % 3 != gv:
                    ok = False
                    break
            if not ok:
                continue
            x[v] = xv
            g[v] = gv
            used.add(xv)
            rec(done + 1)
            used.remove(xv)
            x[v] = None
            g[v] = None

    rec(1)
    return out, nodes


def moser_edges(root, a, b, tip1, c, d, tip2):
    raw = {
        (root, a), (root, b), (a, b), (a, tip1), (b, tip1),
        (root, c), (root, d), (c, d), (c, tip2), (d, tip2),
        (tip1, tip2),
    }
    return frozenset(tuple(sorted(e)) for e in raw)


EXPLICIT = {
    0: (
        {0: 0, 1: 0, 32: 2, 33: 2, 203: 2, 327: 2, 199: 1},
        moser_edges(0, 1, 32, 33, 203, 327, 199),
    ),
    1: (
        {0: 0, 16: 1, 181: 1, 197: 2, 203: 1, 327: 0, 199: 1},
        moser_edges(0, 16, 181, 197, 203, 327, 199),
    ),
    2: (
        {0: 0, 1: 1, 32: 1, 33: 2, 323: 1, 248: 0, 240: 1},
        moser_edges(0, 1, 32, 33, 323, 248, 240),
    ),
}


def verify_gain_edge(c, gauge, edge):
    a, b = edge
    ph = phi(c, (b - a) % Q)
    assert ph is not None
    assert (gauge[b] - gauge[a]) % 3 == ph


for c, (gauge, edges) in EXPLICIT.items():
    assert len(gauge) == 7 and len(edges) == 11
    for e in edges:
        verify_gain_edge(c, gauge, e)

# Independent complete small critical catalogue.
CAT = catalogue_counts_through_six()
assert CAT[4] == (1, {(3, 3, 3, 3): 1})
assert CAT[5] == (0, {})
assert CAT[6] == (72, {(3, 3, 3, 3, 3, 5): 72})

# Exact gain embeddings of the only connected edge-4-critical types through six vertices.
embedding_stats = {}
moser_unique = {}
for c in range(3):
    k4, k4_nodes = balanced_embeddings(c, 4, K4)
    w5, w5_nodes = balanced_embeddings(c, 6, W5)
    moser, moser_nodes = balanced_embeddings(c, 7, MOSER)
    assert len(k4) == 0
    assert len(w5) == 0
    assert len(moser) == 80
    unique = {}
    for x, g, es in moser:
        unique.setdefault(es, (x, g))
    assert len(unique) == 10
    assert EXPLICIT[c][1] in unique
    moser_unique[c] = unique
    embedding_stats[c] = (k4_nodes, w5_nodes, moser_nodes)

# Among the exact normalized Moser edge sets, find the minimum three-slice union.
best = None
best_edges = None
for e0, e1, e2 in product(moser_unique[0], moser_unique[1], moser_unique[2]):
    union = set(e0) | set(e1) | set(e2)
    verts = set()
    for a, b in union:
        verts.add(a)
        verts.add(b)
    key = (len(verts), len(union))
    if best is None or key < best:
        best = key
        best_edges = union
assert best == (13, 23)

explicit_union = set(EXPLICIT[0][1]) | set(EXPLICIT[1][1]) | set(EXPLICIT[2][1])
explicit_vertices = sorted({v for e in explicit_union for v in e})
assert len(explicit_vertices) == 13
assert len(explicit_union) == 23


def rank_mod3(mat):
    a = [[x % 3 for x in row] for row in mat]
    r = 0
    nr = len(a)
    nc = len(a[0]) if nr else 0
    for c in range(nc):
        p = next((i for i in range(r, nr) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        inv = 1 if a[r][c] == 1 else 2
        a[r] = [(x * inv) % 3 for x in a[r]]
        for i in range(nr):
            if i == r or not a[i][c]:
                continue
            f = a[i][c]
            a[i] = [(a[i][j] - f * a[r][j]) % 3 for j in range(nc)]
        r += 1
        if r == nr:
            break
    return r


def canonical_arc(a, b):
    d = (b - a) % Q
    if d in IDX:
        return a, b
    assert (-d) % Q in IDX
    return b, a


pos = {v: i for i, v in enumerate(explicit_vertices)}
D = []
N = []
for a, b in sorted(explicit_union):
    u, v = canonical_arc(a, b)
    row = [0] * len(explicit_vertices)
    row[pos[u]] = 2
    row[pos[v]] = 1
    D.append(row)
    N.append([1] + row)

assert rank_mod3(D) == 12
assert rank_mod3(N) == 13

print("PASS_PALEY331_CHARACTER_MOSER_BALANCED_4CRITICAL_COVER")
print("q=331 L=15 support_degree=30")
print("critical_catalog_connected_edge4critical: n4=1 n5=0 n6=72")
print("n6_degree_profile=(3,3,3,3,3,5) x72")
for c in range(3):
    k4_nodes, w5_nodes, moser_nodes = embedding_stats[c]
    print(
        f"c={c}: K4_embeddings=0 W5_embeddings=0 "
        f"Moser_labelled_embeddings=80 Moser_unique_edge_sets=10 "
        f"search_nodes={k4_nodes}/{w5_nodes}/{moser_nodes}"
    )
print("minimum_balanced_ordinary_4critical_order=7 for each slice")
print("three_slice_Moser_min_union_vertices=13 edges=23")
print("explicit_union_rankD=12 rankN=13")
print("rho_min_Paley331<=13; equality_NOT_claimed")
print("E8_D1=EMPTY P_VS_NP=OPEN")
