#!/usr/bin/env python3
"""Exact controls for R5 E50.

Rebuilds the frozen q=6 E12/E17 hardness target and counts independent 3-subsets
of every conflict neighborhood. Verifies:
  * all 102 vertices are multiclaw (>=2 claw triples);
  * 72 internal z/Z vertices have exactly 4 claw triples;
  * 18 t vertices and 12 global x/x' boundary vertices have exactly 8.

The companion note proves the 4/8 pattern symbolically for every E12 reduction
target.

P_VS_NP remains OPEN.
"""

from itertools import combinations
from collections import Counter, defaultdict


def rx_fixture():
    q = 6
    source_sets = [tuple(sorted({i, (i + 1) % q, (i + 3) % q})) for i in range(q)]
    return q, source_sets


def transform_rx(q, source_sets):
    target = []
    x = [f"x:{i}" for i in range(q)]
    xp = [f"xp:{i}" for i in range(q)]
    for j, C in enumerate(source_sets):
        a, b, c = C
        bx = [x[a], x[b], x[c]]
        bxp = [xp[a], xp[b], xp[c]]
        z = [f"g{j}:z{i}" for i in range(1, 7)]
        zp = [f"g{j}:Z{i}" for i in range(1, 7)]
        t = [f"g{j}:t{i}" for i in range(1, 4)]
        target.extend([
            {bx[0], z[0], z[3]}, {bx[1], z[1], z[4]}, {bx[2], z[2], z[5]},
            {z[0], z[1], z[2]}, {z[3], z[4], z[5]},
            {bxp[0], zp[0], zp[3]}, {bxp[1], zp[1], zp[4]}, {bxp[2], zp[2], zp[5]},
            {zp[0], zp[1], zp[2]}, {zp[3], zp[4], zp[5]},
            {z[1], z[5], t[0]}, {z[2], z[3], t[1]}, {z[0], z[4], t[2]},
            {zp[1], zp[5], t[1]}, {zp[2], zp[3], t[2]}, {zp[0], zp[4], t[0]},
            {t[0], t[1], t[2]},
        ])
    return target


def conflict(target):
    elems = sorted(set().union(*target))
    idx = {e: i for i, e in enumerate(elems)}
    adj = [set() for _ in elems]
    for T in target:
        vs = [idx[e] for e in T]
        for u, v in combinations(vs, 2):
            adj[u].add(v)
            adj[v].add(u)
    return elems, adj


def claw_count(adj, v):
    out = 0
    for T in combinations(sorted(adj[v]), 3):
        if all(b not in adj[a] for a, b in combinations(T, 2)):
            out += 1
    return out


def kind(e):
    if e.startswith("x:"):
        return "x"
    if e.startswith("xp:"):
        return "xp"
    if ":z" in e:
        return "z"
    if ":Z" in e:
        return "Z"
    if ":t" in e:
        return "t"
    raise AssertionError(e)


def main():
    q, source_sets = rx_fixture()
    target = transform_rx(q, source_sets)
    elems, adj = conflict(target)
    assert len(target) == len(elems) == 102
    assert all(len(adj[v]) == 6 for v in range(102))

    counts = [claw_count(adj, v) for v in range(102)]
    assert Counter(counts) == Counter({4: 72, 8: 30})
    assert all(c >= 2 for c in counts)

    by_kind = defaultdict(list)
    for i, e in enumerate(elems):
        by_kind[kind(e)].append(counts[i])

    assert Counter(by_kind["z"]) == Counter({4: 36})
    assert Counter(by_kind["Z"]) == Counter({4: 36})
    assert Counter(by_kind["t"]) == Counter({8: 18})
    assert Counter(by_kind["x"]) == Counter({8: 6})
    assert Counter(by_kind["xp"]) == Counter({8: 6})

    print("R5 E50 E12 multiclaw firewall: PASS")
    print("q=6 target: n=102, claw-count distribution 4 x 72, 8 x 30")
    print("all vertices are multiclaw; E49 exceptional set has size t=n")


if __name__ == "__main__":
    main()
