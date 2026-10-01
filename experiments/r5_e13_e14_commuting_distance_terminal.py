#!/usr/bin/env python3
"""Executable controls for R5 E13/E14.

Checks:
  * exact Z3 propagation on commuting I+P+Q toroidal controls;
  * SAT iff both rectangular periods are divisible by 3;
  * polynomial nearest-centralizer construction for a fixed P;
  * a 2-row noncommuting perturbation of a commuting 6x6 torus;
  * exact rational-nullity bound d <= 3t on that active core;
  * nearest-centralizer distance on the frozen PG15_UNSAT P,Q pair.

No external dependencies.
"""

from collections import defaultdict, deque
from fractions import Fraction


PG15_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PG15_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]


def compose(a, b):
    """Permutation composition a o b."""
    return [a[b[i]] for i in range(len(a))]


def commute(p, q):
    return compose(p, q) == compose(q, p)


def permutation_cycles(p):
    seen = [False] * len(p)
    out = []
    for s in range(len(p)):
        if seen[s]:
            continue
        cyc = []
        v = s
        while not seen[v]:
            seen[v] = True
            cyc.append(v)
            v = p[v]
        out.append(cyc)
    return out


def generated_orbits(p, q):
    n = len(p)
    pinv = [0] * n
    qinv = [0] * n
    for i, v in enumerate(p):
        pinv[v] = i
    for i, v in enumerate(q):
        qinv[v] = i

    seen = [False] * n
    out = []
    for root in range(n):
        if seen[root]:
            continue
        seen[root] = True
        dq = deque([root])
        orb = []
        while dq:
            v = dq.popleft()
            orb.append(v)
            for w in (p[v], q[v], pinv[v], qinv[v]):
                if not seen[w]:
                    seen[w] = True
                    dq.append(w)
        out.append(orb)
    return out


def try_z3_orientation(p, q, orbit, inc_p, inc_q):
    allowed = set(orbit)
    color = {}
    root = orbit[0]
    color[root] = 0
    dq = deque([root])

    pinv = [0] * len(p)
    qinv = [0] * len(q)
    for i, v in enumerate(p):
        pinv[v] = i
    for i, v in enumerate(q):
        qinv[v] = i

    transitions = (
        (p, inc_p),
        (q, inc_q),
        (pinv, -inc_p),
        (qinv, -inc_q),
    )

    while dq:
        v = dq.popleft()
        for perm, delta in transitions:
            w = perm[v]
            if w not in allowed:
                return None
            want = (color[v] + delta) % 3
            if w in color:
                if color[w] != want:
                    return None
            else:
                color[w] = want
                dq.append(w)

    if len(color) != len(orbit):
        return None
    return color


def commuting_exactone_solver(p, q):
    assert commute(p, q)
    global_x = [0] * len(p)

    for orbit in generated_orbits(p, q):
        coloring = try_z3_orientation(p, q, orbit, +1, -1)
        if coloring is None:
            coloring = try_z3_orientation(p, q, orbit, -1, +1)
        if coloring is None:
            return None
        for v in orbit:
            global_x[v] = int(coloring[v] == 0)

    assert all(global_x[i] + global_x[p[i]] + global_x[q[i]] == 1
               for i in range(len(p)))
    return global_x


def torus_perms(a, b):
    def vid(i, j):
        return (i % a) * b + (j % b)

    n = a * b
    p = [0] * n
    q = [0] * n
    for i in range(a):
        for j in range(b):
            v = vid(i, j)
            p[v] = vid(i + 1, j)
            q[v] = vid(i, j + 1)
    return p, q


def hungarian_min(cost):
    """O(n^3) Hungarian algorithm for a square integer cost matrix."""
    n = len(cost)
    if n == 0:
        return [], 0
    u = [0] * (n + 1)
    v = [0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)
    INF = 10**18

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = 0
            for j in range(1, n + 1):
                if used[j]:
                    continue
                cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    assignment = [-1] * n
    for j in range(1, n + 1):
        assignment[p[j] - 1] = j - 1
    value = sum(cost[i][assignment[i]] for i in range(n))
    return assignment, value


def nearest_commuting_q(p, q):
    """Return exact Hamming-nearest q0 in the centralizer C(p)."""
    by_len = defaultdict(list)
    for cyc in permutation_cycles(p):
        by_len[len(cyc)].append(cyc)

    q0 = [None] * len(p)
    matches = 0

    for ell, cycles in by_len.items():
        m = len(cycles)
        positions = [{v: r for r, v in enumerate(c)} for c in cycles]
        weight = [[0] * m for _ in range(m)]
        shift = [[0] * m for _ in range(m)]

        for a, src in enumerate(cycles):
            for b, dst in enumerate(cycles):
                dst_pos = positions[b]
                cnt = [0] * ell
                for r, x in enumerate(src):
                    y = q[x]
                    if y in dst_pos:
                        s = (dst_pos[y] - r) % ell
                        cnt[s] += 1
                best_s = max(range(ell), key=lambda s: cnt[s])
                weight[a][b] = cnt[best_s]
                shift[a][b] = best_s

        # Max weight = min cost for negative weights.
        assignment, neg_value = hungarian_min(
            [[-weight[i][j] for j in range(m)] for i in range(m)]
        )
        matches += -neg_value

        for a, b in enumerate(assignment):
            src = cycles[a]
            dst = cycles[b]
            s = shift[a][b]
            for r, x in enumerate(src):
                q0[x] = dst[(r + s) % ell]

    assert sorted(q0) == list(range(len(p)))
    assert commute(p, q0)
    t = len(p) - matches
    assert t == sum(q[i] != q0[i] for i in range(len(p)))
    return q0, t


def matrix_from_perms(p, q):
    n = len(p)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, p[i], q[i]):
            A[i][j] += 1
    return A


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def check_commuting_tori():
    cases = [
        (6, 6, True),
        (6, 7, False),
        (7, 6, False),
        (7, 7, False),
        (9, 6, True),
    ]
    for a, b, expected in cases:
        p, q = torus_perms(a, b)
        assert commute(p, q)
        x = commuting_exactone_solver(p, q)
        assert (x is not None) == expected
        if x is not None:
            assert sum(x) == (a * b) // 3
    return cases


def check_distance_terminal():
    p, q0_true = torus_perms(6, 6)
    q = q0_true[:]
    # Swap two images: a genuine permutation at Hamming distance two.
    q[0], q[2] = q[2], q[0]
    assert not commute(p, q)
    assert all(len({i, p[i], q[i]}) == 3 for i in range(len(p)))

    q0, t = nearest_commuting_q(p, q)
    assert t == 2
    assert q0 == q0_true

    A = matrix_from_perms(p, q)
    d = len(A) - rank_q(A)
    assert d <= 3 * t

    # Active-orbit theorem: here the commuting reference has one orbit,
    # so the active core is the full 36-vertex instance.
    assert len(generated_orbits(p, q0)) == 1
    return t, d


def check_pg15_distance():
    q0, t = nearest_commuting_q(PG15_P, PG15_Q)
    assert commute(PG15_P, q0)
    # Frozen value for this displayed normal form.
    assert t == 12
    return t


def main():
    torus = check_commuting_tori()
    t, d = check_distance_terminal()
    pg_t = check_pg15_distance()

    print("R5 E13/E14 controls: PASS")
    for a, b, sat in torus:
        print(f"  commuting torus {a}x{b}: {'SAT' if sat else 'UNSAT'}")
    print(f"  near-commuting 6x6 perturbation: t={t}, nullity_Q={d}, bound=3t={3*t}")
    print(f"  frozen PG15_UNSAT displayed normal form: nearest-centralizer t={pg_t}")


if __name__ == "__main__":
    main()
