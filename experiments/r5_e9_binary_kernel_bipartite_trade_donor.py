#!/usr/bin/env python3
"""Binary-kernel -> bipartite signed-trade donor controls.

Finite controls only. The arbitrary-size theorem is proved in the companion
research note. Exhaustive sign enumeration here is OFFLINE_FALSIFIER_ONLY.
"""
from __future__ import annotations
from itertools import product
from collections import Counter, deque
import json

Hypergraph = tuple[tuple[int, int, int], ...]

FANO: Hypergraph = (
    (0, 1, 3),
    (0, 2, 5),
    (0, 4, 6),
    (1, 2, 6),
    (1, 4, 5),
    (2, 3, 4),
    (3, 5, 6),
)

AFFINE_3X3: Hypergraph = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (1, 5, 6), (2, 3, 7),
)


def kernel_words(H: Hypergraph, n: int):
    for c in product((0, 1), repeat=n):
        if all(sum(c[v] for v in e) % 2 == 0 for e in H):
            yield c


def support_multigraph(H: Hypergraph, c):
    selected = {i for i, b in enumerate(c) if b}
    adj = {v: [] for v in selected}
    edges = []
    for e in H:
        s = [v for v in e if c[v]]
        assert len(s) in (0, 2)
        if len(s) == 2:
            u, v = s
            edges.append((u, v))
            adj[u].append(v)
            adj[v].append(u)
    return adj, edges


def bipartition(adj):
    color = {}
    for root in adj:
        if root in color:
            continue
        color[root] = 0
        q = deque([root])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return None
    return color


def construct_signed_trade(H: Hypergraph, c):
    adj, _ = support_multigraph(H, c)
    col = bipartition(adj)
    if col is None:
        return None
    h = [0] * len(c)
    for v, side in col.items():
        h[v] = 1 if side == 0 else -1
    assert all(sum(h[v] for v in e) == 0 for e in H)
    assert tuple(int(v != 0) for v in h) == tuple(c)
    return tuple(h)


def brute_signed_lift_exists(H: Hypergraph, c):
    S = [i for i, b in enumerate(c) if b]
    for signs in product((-1, 1), repeat=len(S)):
        h = [0] * len(c)
        for v, s in zip(S, signs):
            h[v] = s
        if all(sum(h[v] for v in e) == 0 for e in H):
            return True
    return False


def exact_models(H: Hypergraph, n: int):
    out = []
    for x in product((0, 1), repeat=n):
        if all(sum(x[v] for v in e) == 1 for e in H):
            out.append(x)
    return out


def analyze(name, H, n):
    kws = list(kernel_words(H, n))
    profile = Counter()
    checked = 0
    for c in kws:
        if not any(c):
            continue
        adj, _ = support_multigraph(H, c)
        bp = bipartition(adj) is not None
        constructed = construct_signed_trade(H, c) is not None
        brute = brute_signed_lift_exists(H, c)
        assert bp == constructed == brute
        profile[(sum(c), bp)] += 1
        checked += 1
    return {
        "name": name,
        "kernel_size": len(kws),
        "nonzero_kernel_words_checked": checked,
        "profile": {f"weight={w},bipartite={b}": k for (w, b), k in sorted(profile.items())},
        "exact_one_models": len(exact_models(H, n)),
    }


fano = analyze("FANO", FANO, 7)
aff = analyze("AFFINE_3X3", AFFINE_3X3, 9)

assert fano["kernel_size"] == 8
assert fano["profile"] == {"weight=4,bipartite=False": 7}
assert fano["exact_one_models"] == 0

assert aff["kernel_size"] == 4
assert aff["profile"] == {"weight=6,bipartite=True": 3}
assert aff["exact_one_models"] == 3

# Difference of any two Exact-One models is automatically an integer signed
# trade; verify that its absolute support is one of the bipartite F2-kernel
# words and that adding it maps one model to the other.
ams = exact_models(AFFINE_3X3, 9)
for i in range(len(ams)):
    for j in range(i):
        x, y = ams[j], ams[i]
        h = tuple(y[k] - x[k] for k in range(9))
        c = tuple(int(v != 0) for v in h)
        assert any(c)
        assert all(sum(c[v] for v in e) % 2 == 0 for e in AFFINE_3X3)
        assert all(sum(h[v] for v in e) == 0 for e in AFFINE_3X3)
        adj, _ = support_multigraph(AFFINE_3X3, c)
        assert bipartition(adj) is not None
        assert tuple(x[k] + h[k] for k in range(9)) == y

print(json.dumps({
    "status": "PASS_BINARY_KERNEL_BIPARTITE_TRADE_DONOR_CONTROLS",
    "fano": fano,
    "affine_3x3": aff,
    "theorem_control": "BIPARTITE_SUPPORT_GRAPH_IFF_SIGNED_PM1_KERNEL_LIFT",
    "role": "OFFLINE_FINITE_CONTROL__NOT_D1_SOLVER",
    "D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
