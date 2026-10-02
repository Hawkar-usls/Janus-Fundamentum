#!/usr/bin/env python3
"""Exact controls for corrected R5 E50.

IMPORTANT ORIENTATION:
  Exact-One variables are the E12 target triples (matrix columns), not the target
  hypergraph elements (matrix rows). Therefore the E45--E49 conflict graph has one
  vertex per target triple; two vertices are adjacent iff the two triples share a
  target element.

Rebuilds the frozen q=6 E12/E17 target and verifies on the correct column-conflict
graph:
  * all 102 variable-columns are multiclaw (>=2 claw triples);
  * 24 columns have c(v)=2;
  * 72 columns have c(v)=4;
  * 6 columns have c(v)=8.

Breakdown per gadget:
  L1-L3,P1-P3,D1-D6 -> c=4;
  L4-L5,P4-P5       -> c=2;
  D7                 -> c=8.

The companion note proves this local pattern for every E12 reduction target.
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
    names = []
    x = [f"x:{i}" for i in range(q)]
    xp = [f"xp:{i}" for i in range(q)]
    for j, C in enumerate(source_sets):
        a, b, c = C
        bx = [x[a], x[b], x[c]]
        bxp = [xp[a], xp[b], xp[c]]
        z = [f"g{j}:z{i}" for i in range(1, 7)]
        zp = [f"g{j}:Z{i}" for i in range(1, 7)]
        t = [f"g{j}:t{i}" for i in range(1, 4)]
        triples = [
            {bx[0], z[0], z[3]}, {bx[1], z[1], z[4]}, {bx[2], z[2], z[5]},
            {z[0], z[1], z[2]}, {z[3], z[4], z[5]},
            {bxp[0], zp[0], zp[3]}, {bxp[1], zp[1], zp[4]}, {bxp[2], zp[2], zp[5]},
            {zp[0], zp[1], zp[2]}, {zp[3], zp[4], zp[5]},
            {z[1], z[5], t[0]}, {z[2], z[3], t[1]}, {z[0], z[4], t[2]},
            {zp[1], zp[5], t[1]}, {zp[2], zp[3], t[2]}, {zp[0], zp[4], t[0]},
            {t[0], t[1], t[2]},
        ]
        labels = (
            [f"g{j}:L{i}" for i in range(1, 6)]
            + [f"g{j}:P{i}" for i in range(1, 6)]
            + [f"g{j}:D{i}" for i in range(1, 8)]
        )
        target.extend(triples)
        names.extend(labels)
    return names, target


def column_conflict(target):
    # Vertices are target triples / Exact-One columns.
    n = len(target)
    adj = [set() for _ in range(n)]
    for i, j in combinations(range(n), 2):
        if target[i] & target[j]:
            adj[i].add(j)
            adj[j].add(i)
    return adj


def claw_count(adj, v):
    out = 0
    for T in combinations(sorted(adj[v]), 3):
        if all(b not in adj[a] for a, b in combinations(T, 2)):
            out += 1
    return out


def local_tag(name):
    return name.split(":", 1)[1]


def main():
    q, source_sets = rx_fixture()
    names, target = transform_rx(q, source_sets)
    adj = column_conflict(target)

    assert len(target) == len(names) == 102
    assert all(len(adj[v]) == 6 for v in range(102))

    counts = [claw_count(adj, v) for v in range(102)]
    assert Counter(counts) == Counter({2: 24, 4: 72, 8: 6})
    assert all(c >= 2 for c in counts)

    by_tag = defaultdict(list)
    for i, name in enumerate(names):
        by_tag[local_tag(name)].append(counts[i])

    for tag in ("L1", "L2", "L3", "P1", "P2", "P3",
                "D1", "D2", "D3", "D4", "D5", "D6"):
        assert Counter(by_tag[tag]) == Counter({4: q})

    for tag in ("L4", "L5", "P4", "P5"):
        assert Counter(by_tag[tag]) == Counter({2: q})

    assert Counter(by_tag["D7"]) == Counter({8: q})

    print("R5 E50 corrected E12 multiclaw firewall: PASS")
    print("q=6 target column-conflict graph: n=102, distribution c=2 x24, c=4 x72, c=8 x6")
    print("all 102 Exact-One variable-columns are multiclaw; E49 exceptional set has size t=n")


if __name__ == "__main__":
    main()
