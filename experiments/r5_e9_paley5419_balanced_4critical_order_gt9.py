#!/usr/bin/env python3
"""Exact q=5419 replay against the complete edge-4-critical catalogue through order 9."""

from itertools import combinations

Q = 5419
R = (-2) % Q

CATALOG7 = [
    "FEnbo",
    "FQjRo",
]
CATALOG8 = [
    "GCqjbc",
    "GCp`f{",
    "GCpdrk",
    "GCrbds",
    "GCRdrs",
]
CATALOG9 = [
    "H?otQvs",
    "HCrb`qi",
    "HCQ`fP]",
    "HCQf@p|",
    "HCQRDpm",
    "H?`vAqz",
    "HCQRDP}",
    "HCp`eqm",
    "H?q`v`]",
    "HCp`eg}",
    "HCQb`rm",
    "HCQe`rm",
    "HCQbQqu",
    "HCQbdp]",
    "H?otU`}",
    "HCQe`pl",
    "HCp`fQ]",
    "H?q`qjy",
    "HCQ`epm",
    "HCp`fP]",
    "HCp`fa]",
]


def is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


assert is_prime(Q)
assert Q % 8 == 3


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
assert len(O) == 21
assert len(O) % 3 == 0
IDX = {s: k for k, s in enumerate(O)}
S = tuple(sorted(set(O) | {(-s) % Q for s in O}))
assert len(S) == 42

# Exact translation-invariant particular solution recurrence.
for k, s in enumerate(O):
    rs = (R * s) % Q
    assert IDX[rs] == (k + 1) % len(O)
    assert (2 * (k % 3) + (IDX[rs] % 3)) % 3 == 1


def phi(c, d):
    d %= Q
    if d in IDX:
        return (-IDX[d] - c) % 3
    nd = (-d) % Q
    if nd in IDX:
        return (IDX[nd] + c) % 3
    return None


def decode_graph6(s):
    n = ord(s[0]) - 63
    assert 0 <= n <= 62
    bits = []
    for ch in s[1:]:
        z = ord(ch) - 63
        bits.extend((z >> j) & 1 for j in range(5, -1, -1))
    edges = []
    p = 0
    for j in range(1, n):
        for i in range(j):
            if bits[p]:
                edges.append((i, j))
            p += 1
    return n, edges


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


# Self-contained small controls: generate all labelled connected edge-4-critical graphs through order 6.
def labelled_small_critical_counts():
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


SMALL = labelled_small_critical_counts()
assert SMALL[4] == (1, {(3, 3, 3, 3): 1})
assert SMALL[5] == (0, {})
assert SMALL[6] == (72, {(3, 3, 3, 3, 3, 5): 72})

K4 = list(combinations(range(4), 2))
W5 = [(i, (i + 1) % 5) for i in range(5)] + [(5, i) for i in range(5)]
assert edge4critical(4, K4)
assert edge4critical(6, W5)


def checked_catalog(strings, expected_n):
    out = []
    for code in strings:
        n, edges = decode_graph6(code)
        assert n == expected_n
        assert edge4critical(n, edges)
        out.append((code, n, edges))
    return out


C7 = checked_catalog(CATALOG7, 7)
C8 = checked_catalog(CATALOG8, 8)
C9 = checked_catalog(CATALOG9, 9)
assert len(C7) == 2
assert len(C8) == 5
assert len(C9) == 21

CATALOG = [
    ("K4", 4, K4),
    ("W5", 6, W5),
] + C7 + C8 + C9
assert len(CATALOG) == 30


def balanced_embedding_exists(c, n, edges):
    """Complete translation/switching-normalized embedding search."""
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
    nodes = 0

    def rec(done):
        nonlocal nodes
        nodes += 1
        if done == n:
            return True

        candidates = []
        for v in range(n):
            if x[v] is not None:
                continue
            assigned = [u for u in adj[v] if x[u] is not None]
            if assigned:
                candidates.append((len(assigned), len(adj[v]), -v, v, assigned))
        _, _, _, v, assigned = max(candidates)
        anchor = assigned[0]

        for d in S:
            xv = (x[anchor] + d) % Q
            if xv in used:
                continue
            gv = (g[anchor] + phi(c, d)) % 3
            ok = True
            for u in assigned[1:]:
                ph = phi(c, (xv - x[u]) % Q)
                if ph is None or (g[u] + ph) % 3 != gv:
                    ok = False
                    break
            if not ok:
                continue
            x[v] = xv
            g[v] = gv
            used.add(xv)
            if rec(done + 1):
                return True
            used.remove(xv)
            x[v] = None
            g[v] = None
        return False

    found = rec(1)
    return found, nodes


totals = {}
maxima = {}
for c in range(3):
    total_nodes = 0
    max_pair = (0, None)
    for name, n, edges in CATALOG:
        found, nodes = balanced_embedding_exists(c, n, edges)
        assert not found, (c, name)
        total_nodes += nodes
        if nodes > max_pair[0]:
            max_pair = (nodes, name)
    totals[c] = total_nodes
    maxima[c] = max_pair

assert totals == {0: 369084, 1: 369084, 2: 369084}
assert all(v[0] == 187027 for v in maxima.values())

print("PASS_PALEY5419_BALANCED_4CRITICAL_ORDER_GT9")
print("q=5419 L=21 support_degree=42 AF3_consistent=True")
print("complete_catalog_counts: n4=1 n5=0 n6=1 n7=2 n8=5 n9=21")
print("decoded_and_rechecked_graph6_types=28 plus K4/W5 controls=30 total tested types")
for c in range(3):
    print(
        f"c={c}: balanced_embeddings_order_le_9=0 "
        f"search_states={totals[c]} largest_single={maxima[c][0]}"
    )
print("minimum_balanced_ordinary_4critical_order_Paley5419>9")
print("NONBALANCED_GAIN_OBSTRUCTIONS_NOT_EXCLUDED")
print("rho_min_Paley5419=OPEN")
print("E8_D1=EMPTY P_VS_NP=OPEN")
