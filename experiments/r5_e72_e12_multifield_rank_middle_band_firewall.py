#!/usr/bin/env python3
"""R5 E72 exact controls: E12 hardness image sits deep in the multi-field middle band.

Let R be a q x q square-cubic-linear RXC3 source incidence matrix and B the
17q x 17q E12 target.  Write d_K(M)=nullity over field K and c(H) for the
number of connected components of the source hypergraph.

This checker freezes the exact quotient formulas

  over Q and F2:
      d(B) = 2q + 2 d(R),

  over F3:
      d_3(B) = 3q + c(H) + d_3(R).

Consequently

  d_Q(B) >= 2q,
  d_2(B) >= 2q,   r_2(B) >= 13q,
  d_3(B) >= 3q,   r_3(B) >= 13q,

for N=17q target columns.  Thus every E12 hardness target is linearly far from
all current E61/E70/E71 logarithmic rank/nullity edges.

The F3 formula comes from a different local quotient.  For the six port
coordinates (L1,L2,L3,P1,P2,P3), a one-gadget F3 kernel projects to the
3-dimensional space parameterized by

    L=(a,b,-a-b),
    P=(c,c+a-b,c-a+b).

For source triples ordered (u,v,w), put M1,M2,M3 for the three position
incidence matrices, U=M1-M3 and V=M2-M3.  In characteristic three,
R=M1+M2+M3=U+V.  Global boundary equations reduce to

    U a + V b = 0,
    R(c+a) = 0.

[U V] is an oriented incidence matrix of the graph obtained by replacing each
source triple (u,v,w) by the two edges w->u and w->v, so its rank is q-c(H).
Adding the 2q local zero-port gauge dimensions gives the F3 formula above.

Scientific ceiling: this is a firewall against rank-MAGNITUDE-only dichotomies,
not a polynomial solver.  A universal polynomial implication would have to act
inside the E12 NP-hard image itself.  P_VS_NP remains OPEN.
"""

from fractions import Fraction

from r5_e17_hardness_kernel_quotient import (
    gadget,
    incidence,
    rank_q,
    rx_fixture,
    source_matrix,
    transform_rx,
    natural_target_matrix,
)


def rref_mod(A, p):
    M = [[x % p for x in row] for row in A]
    m = len(M)
    n = len(M[0]) if m else 0
    pivots = []
    r = 0
    for col in range(n):
        pivot = next((i for i in range(r, m) if M[i][col] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][col], -1, p)
        M[r] = [(z * inv) % p for z in M[r]]
        for i in range(m):
            if i != r and M[i][col] % p:
                f = M[i][col] % p
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(n)]
        pivots.append(col)
        r += 1
        if r == m:
            break
    return M, pivots


def rank_mod(A, p):
    return len(rref_mod(A, p)[1])


def nullspace_mod(A, p):
    R, pivots = rref_mod(A, p)
    n = len(A[0]) if A else 0
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for rr, pc in enumerate(pivots):
            v[pc] = (-R[rr][f]) % p
        basis.append(v)
    return basis


def source_components(q, source_sets):
    adj = [set() for _ in range(q)]
    for C in source_sets:
        a, b, c = C
        for u, v in ((a, b), (a, c), (b, c)):
            adj[u].add(v)
            adj[v].add(u)
    seen = set()
    comps = 0
    for s in range(q):
        if s in seen:
            continue
        comps += 1
        seen.add(s)
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return comps


def check_source(q, source_sets):
    assert len(source_sets) == q
    assert len(set(source_sets)) == q
    counts = [0] * q
    for C in source_sets:
        assert len(C) == 3
        assert len(set(C)) == 3
        for v in C:
            assert 0 <= v < q
            counts[v] += 1
    assert counts == [3] * q
    # Linearity: no two source triples share two vertices.
    for i in range(q):
        for j in range(i):
            assert len(set(source_sets[i]) & set(source_sets[j])) <= 1


def check_local_field_quotients():
    elements, triples = gadget()
    J = incidence(elements, triples)
    Jint = J[6:]
    ports = [0, 1, 2, 5, 6, 7]

    assert rank_q(Jint) == 13

    for p, expected_rank, expected_nullity, expected_proj in (
        (2, 13, 4, 2),
        (3, 12, 5, 3),
        (5, 13, 4, 2),
    ):
        basis = nullspace_mod(Jint, p)
        assert rank_mod(Jint, p) == expected_rank
        assert len(basis) == expected_nullity
        projection = [[v[j] for v in basis] for j in ports]
        assert rank_mod(projection, p) == expected_proj

        # Pin all six ports to zero: the invisible local gauge is always 2D.
        aug = [row[:] for row in Jint]
        for j in ports:
            row = [0] * 17
            row[j] = 1
            aug.append(row)
        assert 17 - rank_mod(aug, p) == 2

        for v in basis:
            L = [v[j] % p for j in ports[:3]]
            P = [v[j] % p for j in ports[3:]]
            if p == 3:
                # Equivalent defining equations for
                # L=(a,b,-a-b), P=(c,c+a-b,c-a+b).
                assert sum(L) % 3 == 0
                assert sum(P) % 3 == 0
                assert (P[1] - P[0] - (L[0] - L[1])) % 3 == 0
            else:
                assert L[0] == L[1] == L[2]
                assert P[0] == P[1] == P[2]

    print("local gadget: Q/F2 port_dim=2, F3 port_dim=3, zero-port gauge_dim=2: PASS")


def check_global_fixture(name, q, source_sets, check_q_target=True):
    check_source(q, source_sets)
    c = source_components(q, source_sets)
    R = source_matrix(q, source_sets)
    B = natural_target_matrix(transform_rx(q, source_sets))
    N = 17 * q
    assert len(B) == N and len(B[0]) == N

    rQ_R = rank_q(R)
    dQ_R = q - rQ_R
    r2_R = rank_mod(R, 2)
    d2_R = q - r2_R
    r3_R = rank_mod(R, 3)
    d3_R = q - r3_R

    r2_B = rank_mod(B, 2)
    d2_B = N - r2_B
    r3_B = rank_mod(B, 3)
    d3_B = N - r3_B

    assert d2_B == 2 * q + 2 * d2_R
    assert d3_B == 3 * q + c + d3_R
    assert r2_B == 13 * q + 2 * r2_R
    assert r3_B == 13 * q + r3_R - c

    # Every nonempty source component contributes rank at least one.
    assert r3_R >= c

    if check_q_target:
        rQ_B = rank_q(B)
        dQ_B = N - rQ_B
        assert dQ_B == 2 * q + 2 * dQ_R
    else:
        dQ_B = 2 * q + 2 * dQ_R

    # Linear-depth middle-band lower bounds for the E12 image.
    assert dQ_B >= 2 * q
    assert d2_B >= 2 * q
    assert r2_B >= 13 * q
    assert d3_B >= 3 * q
    assert r3_B >= 13 * q
    assert min(r2_B, d2_B) >= 2 * q
    assert min(r3_B, d3_B) >= 3 * q

    print(
        f"{name}: q={q} N={N} components={c} "
        f"source(dQ,d2,d3)=({dQ_R},{d2_R},{d3_R}) "
        f"target(dQ,d2,d3)=({dQ_B},{d2_B},{d3_B}) "
        f"target(r2,r3)=({r2_B},{r3_B})"
    )


def main():
    check_local_field_quotients()

    # Frozen E17/E12 q=6 fixture: connected, Q/F2 full rank, F3 nullity one.
    q6, s6 = rx_fixture()
    check_global_fixture("E12_FROZEN_Q6", q6, s6, check_q_target=True)

    # Connected genuine square-cubic-linear fixture with nontrivial nullity in
    # all three fields; this exercises the +d_K(R) terms.
    s9 = [
        (0, 5, 8),
        (0, 1, 4),
        (1, 2, 3),
        (0, 3, 7),
        (4, 7, 8),
        (1, 5, 6),
        (2, 4, 6),
        (2, 5, 7),
        (3, 6, 8),
    ]
    check_global_fixture("CONNECTED_Q9", 9, s9, check_q_target=True)

    # Disjoint union of two frozen q=6 sources.  This freezes the c(H) term in
    # the ternary quotient: c=2, d3(R)=2, so d3(B)=36+2+2=40.
    s12 = list(s6) + [tuple(v + 6 for v in C) for C in s6]
    check_global_fixture("DISCONNECTED_2XQ6", 12, s12, check_q_target=False)

    print("R5 E72 E12 multi-field rank middle-band firewall: PASS")
    print("Q/F2 formula: d_target = 2q + 2 d_source")
    print("F3 formula: d3_target = 3q + components(H) + d3_source")
    print("for N=17q: dQ>=2N/17, min(r2,d2)>=2N/17, min(r3,d3)>=3N/17")
    print("rank/nullity magnitudes alone do not separate the current polynomial edges from the E12 hardness image")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
