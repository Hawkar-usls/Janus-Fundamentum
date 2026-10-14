#!/usr/bin/env python3
"""R5 Tutte-deficit local-trap certificate; Python standard library only.

This program EXHAUSTIVELY checks finite graphs. Its running time is
exponential in the number of vertices; it is NOT a polynomial SAT solver.
For a labeling s, same-colored edges must form a matching. Remove all
endpoints of those edges and let R_s be the graph induced on the remainder.
Define Delta(s)=|V(R_s)|-2*nu(R_s), where nu is maximum matching size.
"""

from collections import Counter
from functools import lru_cache
import json

# Connected, bridgeless, SIMPLE cubic graph on 12 vertices.
N12_EDGES = (
    (0, 2), (0, 6), (0, 7), (1, 5), (1, 10), (1, 11),
    (2, 4), (2, 9), (3, 6), (3, 8), (3, 11), (4, 8),
    (4, 11), (5, 7), (5, 10), (6, 9), (7, 8), (9, 10),
)


def verify_cubic(n, edges):
    assert n % 2 == 0 and n >= 4
    assert len(edges) == 3 * n // 2
    assert len(edges) == len(set(edges))
    assert all(0 <= u < v < n for u, v in edges)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    assert all(len(x) == 3 for x in adj)

    def connected(skip=None):
        seen = {0}
        stack = [0]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if skip in ((u, v), (v, u)):
                    continue
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        return len(seen) == n

    assert connected(), "graph disconnected"
    assert all(connected(skip=e) for e in edges), "bridge found"


def matching_size(remaining, edges):
    """Exact subset dynamic programming; small-fixture verifier ONLY."""
    vertices = tuple(sorted(remaining))
    index = {v: i for i, v in enumerate(vertices)}
    adjmask = [0] * len(vertices)
    for u, v in edges:
        if u in index and v in index:
            a, b = index[u], index[v]
            adjmask[a] |= 1 << b
            adjmask[b] |= 1 << a

    @lru_cache(maxsize=None)
    def solve(mask):
        if not mask:
            return 0
        bit = mask & -mask
        i = bit.bit_length() - 1
        rest = mask ^ bit
        best = solve(rest)  # i unmatched
        choices = adjmask[i] & rest
        while choices:
            partner = choices & -choices
            best = max(best, 1 + solve(rest ^ partner))
            choices ^= partner
        return best

    return solve((1 << len(vertices)) - 1)


def signature(n, edges, mask):
    same = tuple((u, v) for u, v in edges
                 if ((mask >> u) & 1) == ((mask >> v) & 1))
    endpoints = [w for e in same for w in e]
    if len(endpoints) != len(set(endpoints)):
        return None  # E_same is NOT a matching
    remaining = tuple(v for v in range(n) if v not in set(endpoints))
    nu = matching_size(remaining, edges)
    return {"delta": len(remaining) - 2 * nu,
            "same": same, "remaining": remaining, "nu": nu}


def all_signatures(n, edges):
    return {mask: value for mask in range(1 << n)
            if (value := signature(n, edges, mask)) is not None}


def controls():
    k4 = tuple((u, v) for u in range(4) for v in range(u + 1, 4))
    k33 = tuple((u, v) for u in range(3) for v in range(3, 6))
    outer = {(min(i, (i + 1) % 5), max(i, (i + 1) % 5))
             for i in range(5)}
    spokes = {(i, i + 5) for i in range(5)}
    inner = {(min(5 + i, 5 + (i + 2) % 5),
              max(5 + i, 5 + (i + 2) % 5)) for i in range(5)}
    petersen = tuple(sorted(outer | spokes | inner))
    return ((4, k4, {0: 6}), (6, k33, {0: 2}),
            (10, petersen, {4: 10}))


def run():
    verify_cubic(12, N12_EDGES)
    observed = all_signatures(12, N12_EDGES)
    histogram = dict(sorted(Counter(x["delta"] for x in observed.values()).items()))
    assert histogram == {0: 8, 4: 2}, histogram
    assert set(k for k, x in observed.items() if x["delta"] > 0) == {1246, 2849}
    assert observed[1246]["same"] == ((1, 10), (2, 4), (3, 6))
    assert observed[1246]["remaining"] == (0, 5, 7, 8, 9, 11)
    assert observed[1246]["nu"] == 1
    assert observed[1295]["delta"] == 0
    assert len(observed[1295]["same"]) == 6  # explicit SAT witness

    # The Tutte-Berge obstacle W={7}: five isolated odd components remain.
    R = set(observed[1246]["remaining"])
    w = {7}
    leftover = R - w
    adj = {v: set() for v in leftover}
    for u, v in N12_EDGES:
        if u in leftover and v in leftover:
            adj[u].add(v)
            adj[v].add(u)
    assert len(leftover) == 5 and all(not x for x in adj.values())
    assert len(leftover) - len(w) == 4

    # Every valid labeling other than trap differs on at least 5 vertices.
    distances = {mask: (1246 ^ mask).bit_count()
                 for mask in observed if mask != 1246}
    assert min(distances.values()) == 5
    assert min(dist for mask, dist in distances.items()
               if observed[mask]["delta"] == 0) == 5
    assert all(signature(12, N12_EDGES, 1246 ^ bits) is None
               for bits in range(1 << 12)
               if 1 <= bits.bit_count() <= 4)

    control_report = {}
    for n, edges, expected in controls():
        verify_cubic(n, edges)
        hist = dict(sorted(Counter(x["delta"] for x in
                                   all_signatures(n, edges).values()).items()))
        assert hist == expected, (n, hist)
        control_report[str(n)] = hist

    report = {
        "status": "FINITE_CERTIFICATE_NOT_UNIVERSAL_SOLVER",
        "fixture": "connected_bridgeless_simple_cubic_12",
        "vertices": 12, "edges": list(N12_EDGES),
        "enumerated_labelings": 4096,
        "admissible_labelings": len(observed),
        "delta_histogram": histogram,
        "positive_delta_masks": [1246, 2849],
        "trap_mask": 1246, "trap_delta": 4,
        "tutte_barrier_W": [7], "tutte_odd_components_after_W": 5,
        "nearest_different_admissible_hamming_distance": 5,
        "sat_witness_mask": 1295,
        "sat_witness_matching": list(observed[1295]["same"]),
        "control_histograms_by_n": control_report,
        "universal_polynomial_scl": "NOT_CONSTRUCTED", "P_vs_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    run()
