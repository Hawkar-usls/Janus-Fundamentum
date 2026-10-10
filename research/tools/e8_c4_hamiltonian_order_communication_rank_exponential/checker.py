#!/usr/bin/env python3
"""Exact v8.5.9 checker: smooth-C4 Hamiltonian-cut exponential communication rank."""

from fractions import Fraction
from itertools import product

K = ((1, 1), (1, 0))
L_EVEN = ((0, 1), (0, 2))
L_ODD = ((1, 0), (2, 0))
R_EVEN = ((0, 1), (2, 1))
R_ODD = ((1, 0), (1, 2))


def rank_q(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    nr = len(a)
    nc = len(a[0]) if nr else 0
    r = 0
    for c in range(nc):
        pivot = next((i for i in range(r, nr) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [x / pv for x in a[r]]
        for i in range(nr):
            if i == r or a[i][c] == 0:
                continue
            q = a[i][c]
            a[i] = [a[i][j] - q * a[r][j] for j in range(nc)]
        r += 1
        if r == nr:
            break
    return r


def graph_edges(m):
    order = [(r, i) for r in range(4) for i in range(m)]
    H = set()
    for j in range(4 * m):
        u = order[j]
        v = order[(j + 1) % (4 * m)]
        H.add(frozenset((u, v)))
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
        assert len(e) == 2
        u, v = tuple(e)
        deg[u] += 1
        deg[v] += 1
    assert set(deg.values()) == {4}
    # Exact v7.6.1 smooth test: each component occurs in cyclic port order 0,1,2,3.
    for i in range(m):
        occurrences = [r for (r, j) in order if j == i]
        assert occurrences == [0, 1, 2, 3]
    return H, C


def choose_left(m, bits):
    assert len(bits) == m - 1
    pairs = []
    for i in range(m - 1):
        states = L_EVEN if i % 2 == 0 else L_ODD
        pairs.append(states[bits[i]])
    # m odd => m-1 is even. Freeze first even state.
    pairs.append(L_EVEN[0])
    return tuple(p[0] for p in pairs) + tuple(p[1] for p in pairs)


def choose_right(m, bits):
    assert len(bits) == m - 1
    pairs = []
    for i in range(m - 1):
        states = R_EVEN if i % 2 == 0 else R_ODD
        pairs.append(states[bits[i]])
    pairs.append(R_EVEN[0])
    return tuple(p[0] for p in pairs) + tuple(p[1] for p in pairs)


def side_is_proper(x, m):
    # Side order is one Hamiltonian path: first round followed by second round.
    if any(x[j] == x[j + 1] for j in range(2 * m - 1)):
        return False
    # Internal complement rung for every C4.
    if any(x[i] == x[m + i] for i in range(m)):
        return False
    return True


def compatible(x, y, m):
    # Complement crossing edges: (1,i)-(2,i) and (3,i)-(0,i).
    for i in range(m):
        if x[m + i] == y[i]:
            return False
        if x[i] == y[m + i]:
            return False
    # The two Hamiltonian edges crossing the cut.
    if x[2 * m - 1] == y[0]:
        return False
    if x[0] == y[2 * m - 1]:
        return False
    return True


def kron_power_K(k):
    mat = [[1]]
    for _ in range(k):
        nxt = []
        for row in mat:
            nxt.append([z for x in row for z in (x, x)])
            nxt.append([z for x in row for z in (x, 0)])
        mat = nxt
    return mat


def direct_selected_matrix(m):
    words = list(product((0, 1), repeat=m - 1))
    left = [choose_left(m, b) for b in words]
    right = [choose_right(m, b) for b in words]
    assert all(side_is_proper(x, m) for x in left)
    assert all(side_is_proper(y, m) for y in right)
    # Frozen endpoint states make both Hamiltonian crossing edges automatic.
    assert all(x[2 * m - 1] == 1 for x in left)
    assert all(y[0] in (0, 2) for y in right)
    assert all(x[0] == 0 for x in left)
    assert all(y[2 * m - 1] == 1 for y in right)
    return [[int(compatible(x, y, m)) for y in right] for x in left]


assert K[0][0] * K[1][1] - K[0][1] * K[1][0] == -1

# Check the claimed local 2x2 matrix independently for both parities.
def local_matrix(L, R):
    return tuple(tuple(int(lp[1] != rp[0] and lp[0] != rp[1]) for rp in R) for lp in L)

assert local_matrix(L_EVEN, R_EVEN) == K
assert local_matrix(L_ODD, R_ODD) == K

for m, expected_rank in ((3, 4), (5, 16), (7, 64)):
    verify_source(m)
    M = direct_selected_matrix(m)
    expected = kron_power_K(m - 1)
    assert M == expected
    assert rank_q(M) == expected_rank == 2 ** (m - 1)
    print(f"PASS: m={m}, n={4*m}, selected communication submatrix={len(M)}x{len(M)}, exact rank={expected_rank}")

print("PASS: family is simple 4-regular Hamiltonian with smooth complementary C4 occurrence order")
print("PASS: local crossing matrix K=[[1,1],[1,0]] has determinant -1 and field-independent rank 2")
print("PASS: selected cut matrix is exactly K^(tensor(m-1)); rank lower bound is 2^(m-1)=2^(n/4-1)")
print("VERDICT: ORDINARY_HAMILTONIAN_CUT_LINEAR_COMMUNICATION_STATE_HAS_EXPONENTIAL_RANK_ON_A_SMOOTH_C4_SOURCE_FAMILY")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
