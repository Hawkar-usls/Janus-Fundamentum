#!/usr/bin/env python3
"""v8.5.5: source-aware cohomology signature explosion + exact dual return.

This checker has two independent duties:
1. Verify an explicit closed ring family of canonical six-port smooth wires where
   every local {0,+,-} choice has a distinct exact row-space signature whenever
   m is not divisible by 3, while the Hamiltonian path system is one cycle.
2. Verify the MacWilliams/Fourier dual identity on every two-wire closure and
   show that summing the dualized characteristic terms returns exactly the
   already-known v8.5.2 current contraction rather than a new compression.
"""

from collections import Counter
from itertools import permutations, product

# Canonical six-port order: L0,L2,L3,R0,R2,R3.
VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)
INTERNAL_H_PATHS = ((0, 5), (1, 3), (2, 4))
# Ring splice from wire v left ports 0,1,2 to wire v+1 right ports 4,5,3.
EXT_Q = (4, 5, 3)


def gf3_rref(rows, ncols):
    a = [[x % 3 for x in row] for row in rows if any(x % 3 for x in row)]
    r = 0
    c = 0
    pivots = []
    while r < len(a) and c < ncols:
        pivot = next((i for i in range(r, len(a)) if a[i][c] % 3), None)
        if pivot is None:
            c += 1
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = 1 if a[r][c] == 1 else 2
        a[r] = [(inv * x) % 3 for x in a[r]]
        for i in range(len(a)):
            if i == r or a[i][c] == 0:
                continue
            f = a[i][c]
            a[i] = [(x - f * y) % 3 for x, y in zip(a[i], a[r])]
        pivots.append(c)
        r += 1
        c += 1
    return a[:r], pivots


def gf3_rank(rows, ncols):
    return len(gf3_rref(rows, ncols)[0])


def rowspace_signature(rows, ncols):
    rr, _ = gf3_rref(rows, ncols)
    return tuple(tuple(row) for row in rr)


def gf3_nullspace_basis(rows, ncols):
    rr, pivots = gf3_rref(rows, ncols)
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for f in free:
        x = [0] * ncols
        x[f] = 1
        for i in range(len(pivots) - 1, -1, -1):
            pc = pivots[i]
            x[pc] = (-sum(rr[i][j] * x[j] for j in free)) % 3
        basis.append(x)
    for x in basis:
        assert all(sum(row[j] * x[j] for j in range(ncols)) % 3 == 0 for row in rows)
    return basis


def enum_span(basis, ncols):
    for coeff in product(range(3), repeat=len(basis)):
        yield [
            sum(coeff[i] * basis[i][j] for i in range(len(basis))) % 3
            for j in range(ncols)
        ]


def matmul3(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) % 3 for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def matpow3(a, exponent):
    n = len(a)
    out = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    base = [row[:] for row in a]
    e = exponent
    while e:
        if e & 1:
            out = matmul3(base, out)
        base = matmul3(base, base)
        e >>= 1
    return out


def ring_family_rows(m):
    """Conservation rows B_v and local P_v/M_v rows for the explicit ring."""
    ecount = 3 * m
    b = [[0] * ecount for _ in range(m)]
    p = [[0] * ecount for _ in range(m)]
    q = [[0] * ecount for _ in range(m)]
    for v in range(m):
        w = (v + 1) % m
        for left_port, right_port in enumerate(EXT_Q):
            e = 3 * v + left_port
            b[v][e] = (b[v][e] + 1) % 3
            b[w][e] = (b[w][e] - 1) % 3
            p[v][e] = (p[v][e] + VP[left_port]) % 3
            p[w][e] = (p[w][e] - VP[right_port]) % 3
            q[v][e] = (q[v][e] + VM[left_port]) % 3
            q[w][e] = (q[w][e] - VM[right_port]) % 3
    return b, p, q


def ring_hamiltonian_component_count(m):
    """Count cycles in internal-H-path + physical-splice 2-regular graph."""
    n = 6 * m
    adj = [[] for _ in range(n)]

    def node(v, port):
        return 6 * v + port

    def add_edge(x, y):
        adj[x].append(y)
        adj[y].append(x)

    for v in range(m):
        for x, y in INTERNAL_H_PATHS:
            add_edge(node(v, x), node(v, y))
        w = (v + 1) % m
        for left_port, right_port in enumerate(EXT_Q):
            add_edge(node(v, left_port), node(w, right_port))

    assert all(len(nei) == 2 for nei in adj)
    seen = set()
    components = 0
    for start in range(n):
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return components


# The left-dependence recurrence derived from the three physical splice types is
# (a_{v+1}, b_{v+1}, g_{v+1}) = T (a_v,b_v,g_v), where coefficients multiply
# B_v, P_v, M_v respectively.
T = [
    [1, 0, 1],
    [0, 1, 0],
    [0, 1, 1],
]
I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
assert matpow3(T, 3) == I3
assert gf3_rank([[(T[i][j] - I3[i][j]) % 3 for j in range(3)] for i in range(3)], 3) == 2
assert gf3_rank([[(matpow3(T, 2)[i][j] - I3[i][j]) % 3 for j in range(3)] for i in range(3)], 3) == 2

# Source-aware infinite-family control.  For m mod 3 != 0, the H system is one
# cycle and the 2m local row classes are independent modulo conservation.
for m in range(3, 31):
    b, p, q = ring_family_rows(m)
    ecount = 3 * m
    assert gf3_rank(b, ecount) == m - 1
    if m % 3:
        assert ring_hamiltonian_component_count(m) == 1
        assert gf3_rank(b + p + q, ecount) == 3 * m - 1
    else:
        assert ring_hamiltonian_component_count(m) == 3
        assert gf3_rank(b + p + q, ecount) == 3 * m - 3

# Finite exact signature controls.  The general 3^m theorem follows from the
# analytic independence proof; m=4,5 are exhaustively canonicalized here.
for m in (4, 5):
    b, p, q = ring_family_rows(m)
    signatures = set()
    for tau in product(range(3), repeat=m):
        rows = [row[:] for row in b]
        for v, t in enumerate(tau):
            if t == 1:
                rows.append(p[v])
            elif t == 2:
                rows.append(q[v])
        signatures.add(rowspace_signature(rows, 3 * m))
    assert len(signatures) == 3 ** m


def wire_state(c, s, qbit):
    return (
        (c + s) % 3,
        (c + s * qbit) % 3,
        c % 3,
        (c + s * qbit) % 3,
        (c - s * (1 + qbit)) % 3,
        (c + s * (qbit - 1)) % 3,
    )


WIRE6 = sorted(
    {
        wire_state(c, s, qbit)
        for c in range(3)
        for s in (1, 2)
        for qbit in (1, 2)
    }
)
assert len(WIRE6) == 12


def direct_two_wire_count(pi):
    return sum(
        all(x[j] != y[pi[j]] for j in range(6))
        for x in WIRE6
        for y in WIRE6
    )


def two_wire_rows(pi, t1, t2):
    b = [[1] * 6, [2] * 6]
    p1 = list(VP)
    q1 = list(VM)
    p2 = [(-VP[pi[j]]) % 3 for j in range(6)]
    q2 = [(-VM[pi[j]]) % 3 for j in range(6)]
    rows = [row[:] for row in b]
    if t1 == 1:
        rows.append(p1)
    elif t1 == 2:
        rows.append(q1)
    if t2 == 1:
        rows.append(p2)
    elif t2 == 2:
        rows.append(q2)
    return rows


def full_support_rowspace_count(rows, ncols):
    basis, _ = gf3_rref(rows, ncols)
    return sum(all(word) for word in enum_span(basis, ncols))


def dual_h_weight_sum(rows, ncols):
    null_basis = gf3_nullspace_basis(rows, ncols)
    total = 0
    for z in enum_span(null_basis, ncols):
        nonzero = sum(x != 0 for x in z)
        total += ((-1) ** nonzero) * (2 ** (ncols - nonzero))
    return total


def two_wire_current_count(pi):
    b = [[1] * 6, [2] * 6]
    p1 = list(VP)
    q1 = list(VM)
    p2 = [(-VP[pi[j]]) % 3 for j in range(6)]
    q2 = [(-VM[pi[j]]) % 3 for j in range(6)]
    total = 0
    for z in enum_span(gf3_nullspace_basis(b, 6), 6):
        edge_weight = 1
        for x in z:
            edge_weight *= 2 if x == 0 else -1
        a1 = -2
        a1 += 3 * (sum(p1[j] * z[j] for j in range(6)) % 3 == 0)
        a1 += 3 * (sum(q1[j] * z[j] for j in range(6)) % 3 == 0)
        a2 = -2
        a2 += 3 * (sum(p2[j] * z[j] for j in range(6)) % 3 == 0)
        a2 += 3 * (sum(q2[j] * z[j] for j in range(6)) % 3 == 0)
        total += edge_weight * a1 * a2
    assert total % (3 ** 4) == 0
    return total // (3 ** 4)


profile = Counter()
dual_tau_checks = 0
for pi in permutations(range(6)):
    direct = direct_two_wire_count(pi)
    assert two_wire_current_count(pi) == direct

    for t1, t2 in product(range(3), repeat=2):
        rows = two_wire_rows(pi, t1, t2)
        r = gf3_rank(rows, 6)
        # MacWilliams/Fourier identity:
        # 3^(E-r) * |Row(A) intersect (F3*)^E|
        #   = sum_{z in Row(A)^perp} prod_e h(z_e), h(0)=2,h(nonzero)=-1.
        lhs = (3 ** (6 - r)) * full_support_rowspace_count(rows, 6)
        rhs = dual_h_weight_sum(rows, 6)
        assert lhs == rhs
        dual_tau_checks += 1

    profile[direct] += 1

expected_profile = Counter({0: 96, 6: 180, 12: 168, 18: 168, 24: 80, 30: 20, 36: 8})
assert profile == expected_profile
assert dual_tau_checks == 720 * 9 == 6480

print("PASS: explicit ring uses canonical v8.3 internal H paths and physical exposed-port splices")
print("PASS: for m=3..30, H component count is 1 iff m mod 3 != 0 and 3 otherwise")
print("PASS: left-dependence transfer T has T^3=I; local VP/VM classes are independent modulo conservation when m mod 3 != 0")
print("PASS: exact row-space signatures are 3^m on exhaustive m=4 and m=5 controls")
print("PASS: MacWilliams/Fourier dual identity verified for all 6480 two-wire (closure,tau) states")
print("PASS: summing the dualized terms returns the exact v8.5.2 current contraction on all 720 closures")
print("DIRECT_COUNT_PROFILE=0:96,6:180,12:168,18:168,24:80,30:20,36:8")
print("VERDICT: EXACT_COHOMOLOGY_SIGNATURE_EXPLOSION_AND_DUAL_RETURN_BARRIER_ESTABLISHED")
print("FRONTIER: FIND_A_NONTRIVIAL_GRAPH_STRUCTURAL_CONTRACTION_OF_THE_V8_5_2_CURRENT_SUM; DO_NOT_MEMOIZE_EXACT_ROWSPACES_OR_REBRAND_MACWILLIAMS_DUALITY_AS_COMPRESSION")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
