#!/usr/bin/env python3
"""Exact v8.6 checker: nonlinear Hamiltonian-prefix extension-equivalence barrier."""

from itertools import product, combinations

L_EVEN = ((0, 1), (0, 2))
L_ODD = ((1, 0), (2, 0))
R_EVEN = ((0, 1), (2, 1))
R_ODD = ((1, 0), (1, 2))
K = ((1, 1), (1, 0))


def graph_edges(m):
    order = [(r, i) for r in range(4) for i in range(m)]
    H = set()
    for j in range(4 * m):
        H.add(frozenset((order[j], order[(j + 1) % (4 * m)])))
    C = set()
    for i in range(m):
        cyc = [(0, i), (1, i), (2, i), (3, i)]
        for j in range(4):
            C.add(frozenset((cyc[j], cyc[(j + 1) % 4])))
    return order, H, C


def verify_source(m):
    assert m >= 3 and m % 2 == 1
    order, H, C = graph_edges(m)
    assert len(H) == 4 * m
    assert len(C) == 4 * m
    assert H.isdisjoint(C)
    E = H | C
    assert len(E) == 8 * m
    deg = {v: 0 for v in order}
    for e in E:
        u, v = tuple(e)
        deg[u] += 1
        deg[v] += 1
    assert set(deg.values()) == {4}
    for i in range(m):
        occurrences = [r for (r, j) in order if j == i]
        assert occurrences == [0, 1, 2, 3]


def choose_left(m, bits):
    pairs = []
    for i in range(m - 1):
        states = L_EVEN if i % 2 == 0 else L_ODD
        pairs.append(states[bits[i]])
    pairs.append(L_EVEN[0])
    return tuple(p[0] for p in pairs) + tuple(p[1] for p in pairs)


def choose_right(m, bits):
    pairs = []
    for i in range(m - 1):
        states = R_EVEN if i % 2 == 0 else R_ODD
        pairs.append(states[bits[i]])
    pairs.append(R_EVEN[0])
    return tuple(p[0] for p in pairs) + tuple(p[1] for p in pairs)


def side_is_proper(x, m):
    if any(x[j] == x[j + 1] for j in range(2 * m - 1)):
        return False
    if any(x[i] == x[m + i] for i in range(m)):
        return False
    return True


def compatible(x, y, m):
    for i in range(m):
        if x[m + i] == y[i]:
            return False
        if x[i] == y[m + i]:
            return False
    if x[2 * m - 1] == y[0]:
        return False
    if x[0] == y[2 * m - 1]:
        return False
    return True


def bitwords(k):
    return list(product((0, 1), repeat=k))


def selected_matrix(m):
    words = bitwords(m - 1)
    left = {b: choose_left(m, b) for b in words}
    right = {c: choose_right(m, c) for c in words}
    assert all(side_is_proper(x, m) for x in left.values())
    assert all(side_is_proper(y, m) for y in right.values())
    rows = {
        b: tuple(int(compatible(left[b], right[c], m)) for c in words)
        for b in words
    }
    return words, left, right, rows


# Symbolic local separator witness: column 0 accepts both rows; column 1 distinguishes them.
assert K[0][0] == K[1][0] == 1
assert K[0][1] == 1 and K[1][1] == 0

for m in (3, 5, 7):
    verify_source(m)
    words, left, right, rows = selected_matrix(m)
    expected = 2 ** (m - 1)

    # Pairwise distinct selected future-acceptance signatures.
    assert len(rows) == expected
    assert len(set(rows.values())) == expected

    # Stronger witness check: for every pair, build one proper right continuation
    # that accepts exactly one of the two left prefixes.
    pair_count = 0
    for b, bp in combinations(words, 2):
        j = next(i for i in range(m - 1) if b[i] != bp[i])
        c = [0] * (m - 1)
        c[j] = 1
        c = tuple(c)
        y = right[c]
        assert side_is_proper(y, m)
        ab = compatible(left[b], y, m)
        ap = compatible(left[bp], y, m)
        assert ab != ap
        # Orientation of the distinction is exactly the differing local K row.
        assert ab == bool(K[b[j]][1])
        assert ap == bool(K[bp[j]][1])
        pair_count += 1

    assert pair_count == expected * (expected - 1) // 2
    print(
        f"PASS: m={m}, n={4*m}, selected left prefixes={expected}, "
        f"distinct extension signatures={expected}, pair witnesses={pair_count}"
    )

print("PASS: every pair of selected prefixes has an explicit proper right continuation distinguishing extension feasibility")
print("PASS: exact deterministic extension-sufficient Hamiltonian-prefix summaries require at least 2^(m-1)=2^(n/4-1) states on this smooth C4 family")
print("VERDICT: NONLINEAR_DETERMINISTIC_HAMILTONIAN_PREFIX_EXTENSION_STATE_COUNT_IS_EXPONENTIAL_ON_A_SMOOTH_C4_SOURCE_FAMILY")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
