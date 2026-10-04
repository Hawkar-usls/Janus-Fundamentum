#!/usr/bin/env python3
"""R5 E68 exact controls: log-level complexity + SDP/lift-tower firewall.

This checker continues E67 without changing the scientific ceiling.

It verifies four points.

1. Complexity firewall.
   The E67 low-moment implementation costs n^{O(t)}.  Therefore t=O(log n)
   is quasi-polynomial, not polynomial, unless an additional compressed
   algorithm computes the required hierarchy data in poly(n) time.

2. Deterministic connected 2-lift tower diagnostic.
   Starting from the E64 Tutte-12 UNSAT orientation and applying deterministic
   two-lifts with seeds 1,2,3,4,5 gives orders

       63,126,252,504,1008,2016.

   Every checked carrier is connected and remains square/cubic/linear.  The
   complete binary-kernel enumerations have dimensions

       14,16,17,18,20,22,

   maximum weights

       40,80,160,320,640,1280,

   while the Exact-One top weights are

       42,84,168,336,672,1344.

   Hence every checked tower member is UNSAT and the top-shell gap doubles.

3. Canonical moment-only annihilator diagnostic.
   For each exact kernel weight support S, form

       F(w)=prod_{s in S\{0}} (w-s).

   On the allowed even grid [0,2n/3], add the minimum sign-correction factors
   used by this checker between consecutive non-root grid points where sign F
   changes.  This produces an explicit polynomial Q that is positive on every
   allowed non-support grid point and zero on every actual positive support
   weight.  Its degree is a sufficient moment-only certificate order.

   The checked degrees are

       12,28,44,74,120,186.

   Thus the initial +16-per-doubling pattern breaks.  These are constructive
   sufficient orders for this particular annihilator scheme; they are NOT
   proved minimal levels of the full Delsarte/SDP hierarchies.

4. Degree-2 incidence-aware SDP firewall.
   For the Tutte-12 transpose pair R / R^T, the orthogonal projector P onto the
   right real kernel has constant diagonal 2/9 in both orientations.  Therefore

       m = (1/3) 1,
       X = (1/9) J + P

   satisfies the degree-2 Exact-One moment equations:

       diag(X)=m,
       A m = 1,
       A X = (1/3) J,

   and the moment matrix [[1,m^T],[m,X]] is PSD because its Schur complement is
   P >= 0.  Yet E65 gives R UNSAT and R^T SAT.  Thus this natural first
   incidence-aware Lasserre/SoS level does not decide Exact-One.

This is a hierarchy diagnostic/firewall, not a universal polynomial algorithm.
P_VS_NP remains OPEN.
"""

from collections import Counter, deque
from fractions import Fraction

from r5_e64_connected_postquotient_nullity_firewall import (
    tutte12_incidence,
    two_level_kernel_count,
)
from r5_e67_dual_moment_delsarte_hierarchy import (
    gf2_kernel_basis,
    two_lift,
)


def transpose(M):
    return [list(col) for col in zip(*M)]


def connected_incidence(M):
    n = len(M)
    adj = [[] for _ in range(2 * n)]
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            if v:
                adj[i].append(n + j)
                adj[n + j].append(i)
    seen = {0}
    todo = [0]
    while todo:
        u = todo.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == 2 * n


def verify_square_cubic_linear_fast(M):
    n = len(M)
    assert n and all(len(row) == n for row in M)
    assert all(v in (0, 1) for row in M for v in row)
    assert all(sum(row) == 3 for row in M)
    colsum = [0] * n
    row_pairs = set()
    col_supports = [[] for _ in range(n)]
    for i, row in enumerate(M):
        supp = [j for j, v in enumerate(row) if v]
        assert len(supp) == 3
        for j in supp:
            colsum[j] += 1
            col_supports[j].append(i)
        for a in range(3):
            for b in range(a + 1, 3):
                p = (supp[a], supp[b])
                assert p not in row_pairs
                row_pairs.add(p)
    assert set(colsum) == {3}
    col_pairs = set()
    for supp in col_supports:
        assert len(supp) == 3
        supp = sorted(supp)
        for a in range(3):
            for b in range(a + 1, 3):
                p = (supp[a], supp[b])
                assert p not in col_pairs
                col_pairs.add(p)
    assert connected_incidence(M)


def kernel_weight_enumerator_gray(M):
    basis = gf2_kernel_basis(M)
    d = len(basis)
    W = Counter({0: 1})
    v = 0
    prev_gray = 0
    for m in range(1, 1 << d):
        gray = m ^ (m >> 1)
        diff = gray ^ prev_gray
        bit = diff.bit_length() - 1
        v ^= basis[bit]
        W[v.bit_count()] += 1
        prev_gray = gray
    return d, dict(sorted(W.items()))


def canonical_annihilator(M, W):
    """Return exact sign-corrected moment-only annihilator degree and checks."""
    n = len(M)
    top = 2 * n // 3
    support = sorted(w for w in W if w)
    assert support and max(support) < top
    assert all(w % 2 == 0 and 0 <= w <= top for w in W)

    grid = list(range(0, top + 1, 2))
    nonroots = [w for w in grid if w not in support]

    def F(w):
        z = 1
        for s in support:
            z *= w - s
        return z

    signs = [1 if F(w) > 0 else -1 for w in nonroots]
    correction_roots2 = []  # stores 2*r for exact half-integer roots r
    for a, b, sa, sb in zip(nonroots, nonroots[1:], signs, signs[1:]):
        if sa != sb:
            correction_roots2.append(a + b)

    def raw_Q(w):
        z = F(w)
        for r2 in correction_roots2:
            z *= 2 * w - r2
        return z

    orient = 1 if raw_Q(0) > 0 else -1

    def Q(w):
        if w in support:
            return 0
        return orient * raw_Q(w)

    assert Q(0) > 0
    assert all(Q(w) > 0 for w in nonroots)
    assert Q(top) > 0
    assert all(Q(s) == 0 for s in support)

    # The true code moment is exhausted by A_0=1, since all positive support
    # is annihilated.  Thus matching all polynomial moments through deg(Q)
    # forces zero pseudo-mass at every other positive allowed grid point.
    true_moment = sum(a * Q(w) for w, a in W.items())
    assert true_moment == Q(0)

    degree = len(support) + len(correction_roots2)
    return degree, len(support), len(correction_roots2)


def rref_fraction(M):
    A = [[Fraction(v) for v in row] for row in M]
    m = len(A)
    n = len(A[0])
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def rational_nullspace(M):
    R, pivots = rref_fraction(M)
    n = len(M[0])
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0)] * n
        v[f] = Fraction(1)
        for rr, p in enumerate(pivots):
            v[p] = -R[rr][f]
        basis.append(v)
    return basis


def inverse_fraction(M):
    n = len(M)
    A = [
        [Fraction(x) for x in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(M)
    ]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c])
        A[c], A[p] = A[p], A[c]
        z = A[c][c]
        A[c] = [x / z for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    return [row[n:] for row in A]


def projector_onto_right_kernel(M):
    basis = rational_nullspace(M)
    n = len(M[0])
    d = len(basis)
    assert d > 0
    # B is n x d, stored by coordinate rows.
    Brows = [[basis[j][i] for j in range(d)] for i in range(n)]
    G = [[sum(Brows[i][a] * Brows[i][b] for i in range(n)) for b in range(d)] for a in range(d)]
    Gi = inverse_fraction(G)

    def bilinear(u, v):
        return sum(u[a] * Gi[a][b] * v[b] for a in range(d) for b in range(d))

    P = [[bilinear(Brows[i], Brows[j]) for j in range(n)] for i in range(n)]
    assert all(P[i][j] == P[j][i] for i in range(n) for j in range(n))
    return P, d


def degree2_sdp_firewall(A, expected_sat):
    n = len(A)
    P, d = projector_onto_right_kernel(A)
    diag = {P[i][i] for i in range(n)}
    assert diag == {Fraction(2, 9)}
    assert d == 14

    # P is B(B^T B)^(-1)B^T, hence PSD by construction and projects onto ker A.
    for i in range(n):
        for k in range(n):
            assert sum(Fraction(A[i][j]) * P[j][k] for j in range(n)) == 0

    one_third = Fraction(1, 3)
    one_ninth = Fraction(1, 9)
    X = [[one_ninth + P[i][j] for j in range(n)] for i in range(n)]
    assert all(X[i][i] == one_third for i in range(n))
    assert all(sum(Fraction(A[i][j], 3) for j in range(n)) == 1 for i in range(n))
    for i in range(n):
        for k in range(n):
            assert sum(Fraction(A[i][j]) * X[j][k] for j in range(n)) == one_third

    # Independent exact SAT status via the E61 two-level-kernel equivalence.
    dd, count = two_level_kernel_count(A)
    assert dd == 14
    assert bool(count) is expected_sat
    return count


def main():
    R = tutte12_incidence()
    RT = transpose(R)

    # Degree-2 SDP is feasible in both orientations despite opposite SAT status.
    count_R = degree2_sdp_firewall(R, expected_sat=False)
    count_RT = degree2_sdp_firewall(RT, expected_sat=True)
    assert count_R == 0
    assert count_RT == 36

    # Deterministic connected lift tower.
    tower = [R]
    for seed in range(1, 6):
        tower.append(two_lift(tower[-1], seed=seed))

    expected = [
        (63, 14, 40, 42, 6, 12),
        (126, 16, 80, 84, 14, 28),
        (252, 17, 160, 168, 32, 44),
        (504, 18, 320, 336, 55, 74),
        (1008, 20, 640, 672, 93, 120),
        (2016, 22, 1280, 1344, 144, 186),
    ]

    rows = []
    for level, (M, exp) in enumerate(zip(tower, expected)):
        n, ed, emax, etop, esupp, eann = exp
        assert len(M) == n
        verify_square_cubic_linear_fast(M)
        d, W = kernel_weight_enumerator_gray(M)
        top = 2 * n // 3
        degree, support_count, sign_changes = canonical_annihilator(M, W)
        assert d == ed
        assert max(W) == emax
        assert top == etop
        assert support_count == esupp
        assert degree == eann
        assert top - max(W) == 2 ** (level + 1)
        rows.append((level, n, d, max(W), top, support_count, sign_changes, degree))

    # On the checked finite tower, direct kernel enumeration is itself at most
    # a small quadratic multiple.  This prevents misusing this tower as a hard
    # asymptotic family for the universal P=NP goal.
    assert all((1 << d) <= 5 * n * n for _, n, d, *_ in rows)

    print("R5 E68 log-level / SDP lift-tower firewall: PASS")
    print("degree-2 SDP transpose firewall: R UNSAT with 0 exact solutions; R^T SAT with 36; same feasible pseudo-moment construction")
    for level, n, d, mx, top, supp, changes, degree in rows:
        print(
            f"lift level={level} n={n} dim={d} max_kernel_weight={mx} "
            f"target={top} support={supp} sign_changes={changes} "
            f"moment_annihilator_degree={degree} code_size={1<<d}"
        )
    print("observed moment-only orders = [12, 28, 44, 74, 120, 186]; early +16 pattern is false")
    print("current E67 n^{O(t)} implementation: t=O(log n) is quasi-polynomial, not polynomial")
    print("checked tower is diagnostic, not hard: 2^d <= 5 n^2 on all six checked levels")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
