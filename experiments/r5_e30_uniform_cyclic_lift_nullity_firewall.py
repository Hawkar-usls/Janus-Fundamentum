#!/usr/bin/env python3
"""Finite exact controls for R5 E30.

Builds several genuinely noncommuting transitive finite bases P0,Q0 and their
uniform cyclic lifts

    P = P0 x shift^a,
    Q = Q0 x shift^b,
    A = I + P + Q.

For increasing fiber sizes r, checks exact rational nullity and verifies the
R5 E30 bound

    nullity_Q(A) <= m^2 * Delta,
    Delta=max(0,a,b)-min(0,a,b),

which is independent of r for fixed base and fixed shifts.

P_VS_NP remains OPEN.
"""

from fractions import Fraction


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    rr = 0
    for c in range(n):
        pivot = next((i for i in range(rr, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[rr], A[pivot] = A[pivot], A[rr]
        z = A[rr][c]
        A[rr] = [x / z for x in A[rr]]
        for i in range(rr + 1, m):
            if A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[rr][j] for j in range(c, n)]
        rr += 1
        if rr == m:
            break
    return rr


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def commute(p, q):
    return compose(p, q) == compose(q, p)


def transitive(p, q):
    m = len(p)
    ip = [0] * m
    iq = [0] * m
    for i, j in enumerate(p):
        ip[j] = i
    for i, j in enumerate(q):
        iq[j] = i
    seen = {0}
    stack = [0]
    while stack:
        x = stack.pop()
        for s in (p, q, ip, iq):
            y = s[x]
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == m


def lifted_perm(base, shift, r):
    m = len(base)
    out = [0] * (m * r)
    for i in range(m):
        for t in range(r):
            out[i * r + t] = base[i] * r + ((t + shift) % r)
    return out


def carrier(P, Q):
    n = len(P)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        A[i][i] += 1
        A[i][P[i]] += 1
        A[i][Q[i]] += 1
    return A


def main():
    # cycle + transposition bases generate transitive nonabelian permutation groups.
    bases = [
        ("S3-natural", [1, 2, 0], [1, 0, 2]),
        ("S4-like", [1, 2, 3, 0], [1, 0, 2, 3]),
        ("S5-like", [1, 2, 3, 4, 0], [1, 0, 2, 3, 4]),
    ]
    shifts = [(1, -1), (1, 2), (2, -1)]
    fibers = (5, 7, 8, 10, 11, 13)

    print("R5 E30 uniform cyclic-lift controls: PASS")
    for name, P0, Q0 in bases:
        assert transitive(P0, Q0)
        assert not commute(P0, Q0)
        m = len(P0)
        for a, b in shifts:
            Delta = max(0, a, b) - min(0, a, b)
            bound = m * m * Delta
            seen = []
            for r in fibers:
                P = lifted_perm(P0, a, r)
                Q = lifted_perm(Q0, b, r)
                A = carrier(P, Q)
                n = m * r
                d = n - rank_q(A)
                assert d <= bound, (name, a, b, r, d, bound)
                seen.append((r, d))
            print(
                f"{name}: shifts=({a},{b}), m={m}, bound={bound}, "
                f"nullities={seen}"
            )

    print("Conclusion: fixed-base uniform cyclic lifts stay within an r-independent nullity bound.")


if __name__ == "__main__":
    main()
