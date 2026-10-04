#!/usr/bin/env python3
"""R5 E66 exact controls: optimal-layer exchange mobility firewall.

This checker continues E65 on the genuine post-quotient Tutte 12-cage pair.
It asks whether the exchange graph of minimum parity representatives can
separate SAT from UNSAT.

Results replayed here:

* UNSAT orientation R:
    ker_F2(R) weight enumerator has maximum weight 40, so the minimum parity
    layer has weight 63-40=23 (defect m=1).  It contains 252 representatives.
    Under the smallest layer-preserving exchange (symmetric difference weight
    16), these 252 minima form one connected 18-regular graph.

* Every UNSAT minimum has a unique defect-center column.  There are four
  minima over each of the 63 centers.  Each four-vertex fiber induces C4.
  Cross-fiber minimum exchanges occur exactly when the two centers are at
  distance 3 in the column-conflict graph.  The center graph is connected
  strongly regular with parameters (63,32,16,16), and every adjacent pair of
  center fibers is joined by exactly two lifted exchange edges.

  Hence the defect can move globally through all 63 centers by neutral minimum
  exchanges while never annihilating.

* SAT orientation R^T:
    ker_F2(R^T) contains 36 words of weight 42=2n/3, exactly the 36 Exact-One
    solutions.  Their smallest layer-preserving exchange has weight 24.  The
    resulting 36-vertex graph is connected strongly regular with parameters
    (36,21,12,12).

Therefore connectivity, regularity, and global mobility of the optimal exchange
layer are not sufficient to decide Exact-One.  The surviving target is an
orientation-sensitive criterion for whether the top binary-kernel shell reaches
weight 2n/3, not merely whether that shell is well connected.

Scientific ceiling: this is a structural anti-loop theorem, not a universal
polynomial algorithm.  P_VS_NP remains OPEN.
"""

from collections import Counter, deque
import itertools

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import (
    transpose,
    gf2_rref_basis,
    row_sums,
    common_support_column,
)


EXPECTED_W_R = {
    0: 1,
    16: 126,
    24: 1596,
    28: 2880,
    32: 7497,
    36: 4032,
    40: 252,
}

EXPECTED_W_RT = {
    0: 1,
    14: 36,
    18: 56,
    20: 252,
    24: 378,
    26: 1764,
    28: 1800,
    30: 1764,
    32: 3591,
    34: 4032,
    36: 2044,
    38: 504,
    40: 126,
    42: 36,
}

EXPECTED_PAIR_R = {
    16: 2268,
    24: 8064,
    28: 4032,
    32: 11214,
    36: 4032,
    40: 2016,
}

EXPECTED_PAIR_RT = {
    24: 378,
    36: 252,
}


def kernel_words(M):
    _, free, basis = gf2_rref_basis(M)
    out = []
    for mask in range(1 << len(basis)):
        k = 0
        for j, b in enumerate(basis):
            if (mask >> j) & 1:
                k ^= b
        out.append(k)
    return len(free), out


def weight_enumerator(words):
    return dict(sorted(Counter(w.bit_count() for w in words).items()))


def pair_distance_distribution(words):
    C = Counter()
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            C[(words[i] ^ words[j]).bit_count()] += 1
    return dict(sorted(C.items()))


def graph_at_distance(words, d):
    adj = [set() for _ in words]
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            if (words[i] ^ words[j]).bit_count() == d:
                adj[i].add(j)
                adj[j].add(i)
    return adj


def connected(adj):
    if not adj:
        return True
    seen = {0}
    todo = [0]
    while todo:
        u = todo.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == len(adj)


def common_neighbor_parameters(adj):
    """Return (k, lambda, mu) if strongly regular; assert uniformity."""
    degrees = {len(N) for N in adj}
    assert len(degrees) == 1
    k = next(iter(degrees))
    lam = set()
    mu = set()
    for i in range(len(adj)):
        for j in range(i + 1, len(adj)):
            c = len(adj[i] & adj[j])
            if j in adj[i]:
                lam.add(c)
            else:
                mu.add(c)
    assert len(lam) == len(mu) == 1
    return k, next(iter(lam)), next(iter(mu))


def column_conflict_graph(M):
    n = len(M[0])
    adj = [set() for _ in range(n)]
    for row in M:
        S = [j for j, v in enumerate(row) if v]
        assert len(S) == 3
        for a, b in itertools.combinations(S, 2):
            adj[a].add(b)
            adj[b].add(a)
    assert {len(N) for N in adj} == {6}
    return adj


def all_pair_distances(adj):
    D = []
    for s in range(len(adj)):
        dist = [-1] * len(adj)
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    q.append(v)
        assert all(d >= 0 for d in dist)
        D.append(dist)
    return D


def defect_center(M, x):
    sums = row_sums(M, x)
    bad = tuple(i for i, s in enumerate(sums) if s == 3)
    assert len(bad) == 3
    c = common_support_column(M, bad)
    assert (x >> c) & 1
    return c


def main():
    R = tutte12_incidence()
    RT = transpose(R)
    n = len(R)
    assert n == 63
    ones = (1 << n) - 1

    # Exact binary-kernel shells.
    dR, KR = kernel_words(R)
    dT, KT = kernel_words(RT)
    assert dR == dT == 14
    assert len(KR) == len(KT) == 1 << 14

    WR = weight_enumerator(KR)
    WT = weight_enumerator(KT)
    assert WR == EXPECTED_W_R
    assert WT == EXPECTED_W_RT

    maxR = max(WR)
    maxT = max(WT)
    assert maxR == 40
    assert maxT == 42 == 2 * n // 3

    topR = [k for k in KR if k.bit_count() == maxR]
    topT = [k for k in KT if k.bit_count() == maxT]
    assert len(topR) == 252
    assert len(topT) == 36

    # x = 1 + k over F2, so top kernel shell = minimum parity shell.
    minXR = [ones ^ k for k in topR]
    exactXT = [ones ^ k for k in topT]
    assert {x.bit_count() for x in minXR} == {23}
    assert {x.bit_count() for x in exactXT} == {21}

    # All top-shell pair distances.
    pairR = pair_distance_distribution(topR)
    pairT = pair_distance_distribution(topT)
    assert pairR == EXPECTED_PAIR_R
    assert pairT == EXPECTED_PAIR_RT

    # Minimum layer-preserving exchange graphs.
    GR = graph_at_distance(topR, 16)
    GT = graph_at_distance(topT, 24)
    assert connected(GR)
    assert connected(GT)
    assert {len(N) for N in GR} == {18}
    assert {len(N) for N in GT} == {21}
    assert sum(map(len, GR)) // 2 == 2268
    assert sum(map(len, GT)) // 2 == 378

    # SAT exact exchange graph is strongly regular (36,21,12,12).
    kT, lamT, muT = common_neighbor_parameters(GT)
    assert (len(GT), kT, lamT, muT) == (36, 21, 12, 12)

    # Classify every UNSAT minimum by its unique defect-center column.
    centers = [defect_center(R, x) for x in minXR]
    C = Counter(centers)
    assert len(C) == 63
    assert set(C.values()) == {4}

    conflict = column_conflict_graph(R)
    D = all_pair_distances(conflict)

    # The center-level distance-3 graph is itself SRG(63,32,16,16).
    center_adj = [
        {j for j in range(n) if D[i][j] == 3}
        for i in range(n)
    ]
    assert connected(center_adj)
    kC, lamC, muC = common_neighbor_parameters(center_adj)
    assert (n, kC, lamC, muC) == (63, 32, 16, 16)

    # Fibers over one defect center contain four minima and induce C4.
    for c in range(n):
        I = [i for i, cc in enumerate(centers) if cc == c]
        assert len(I) == 4
        induced_degrees = [sum(j in GR[i] for j in I) for i in I]
        assert induced_degrees == [2, 2, 2, 2]

    # Cross-fiber minimum exchanges occur exactly between centers at distance 3.
    # Every such center pair carries exactly two lifted edges.
    cross = Counter()
    same_center_edges = 0
    center_distance_counter = Counter()
    for i in range(len(GR)):
        for j in GR[i]:
            if i >= j:
                continue
            a, b = centers[i], centers[j]
            if a == b:
                same_center_edges += 1
                center_distance_counter[0] += 1
            else:
                center_distance_counter[D[a][b]] += 1
                cross[tuple(sorted((a, b)))] += 1

    assert same_center_edges == 252
    assert center_distance_counter == {0: 252, 3: 2016}

    expected_center_pairs = {
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if D[i][j] == 3
    }
    assert set(cross) == expected_center_pairs
    assert len(cross) == 1008
    assert set(cross.values()) == {2}

    print("R5 E66 optimal-layer exchange mobility firewall: PASS")
    print(f"UNSAT kernel enumerator={WR}")
    print(f"SAT-transpose kernel enumerator={WT}")
    print(
        "UNSAT optimal exchange: vertices=252 edges=2268 degree=18 "
        "connected=True min_exchange_weight=16"
    )
    print(
        "UNSAT defect fibers: 63 fibers x 4 minima; each fiber=C4; "
        "cross-fiber exchanges iff center distance=3"
    )
    print(
        "center mobility graph: SRG(63,32,16,16), connected; "
        "2 lifted exchange edges per adjacent center pair"
    )
    print(
        "SAT exact exchange: SRG(36,21,12,12), connected, "
        "min_exchange_weight=24"
    )
    print("exchange connectivity/global defect mobility do not decide Exact-One")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
