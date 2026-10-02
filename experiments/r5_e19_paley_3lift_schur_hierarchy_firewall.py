#!/usr/bin/env python3
"""Exact controls for R5 E19.

Builds a deterministic connected 3-lift of the Paley tournament cyclic-triangle
source on 11 vertices and verifies:

  * base: 55 tournament arcs and 55 cyclic triangles, each arc in 3 triangles;
  * lift: 165x165 square/cubic/linear and connected;
  * a 10-dimensional A10 root space lies in the lift kernel;
  * rank mod 5 is 155, hence rank_Q=155 and nullity_Q=10 exactly;
  * therefore three copies of every base arc have identical kernel rows and must
    be equal in any Boolean witness;
  * quotienting those equal copies gives the 55-variable base source, which is
    UNSAT by 3|S|=55;
  * the Schur square of the root kernel already spans every function on the 55
    base arc types, so every diagonal Schur power r>=2 is the same 55-dimensional
    copy-constant space. Hence the diagonal Schur-power hierarchy cannot
    distinguish this UNSAT instance at any fixed or unbounded level.

P_VS_NP remains OPEN.
"""

from fractions import Fraction
from itertools import combinations


Q = 11


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


def rank_mod_p(M, p):
    A = [[x % p for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f*A[r][j]) % p for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def paley():
    residues = {a*a % Q for a in range(1, Q)}
    arcs = [
        (i,j)
        for i in range(Q)
        for j in range(Q)
        if i != j and ((j-i) % Q) in residues
    ]
    assert len(arcs) == 55
    ai = {a:i for i,a in enumerate(arcs)}

    triangles = []
    for a,b,c in combinations(range(Q),3):
        for cyc in ((a,b,c),(a,c,b)):
            T = ((cyc[0],cyc[1]),(cyc[1],cyc[2]),(cyc[2],cyc[0]))
            if all(e in ai for e in T):
                triangles.append(T)

    assert len(triangles) == 55
    deg = {e:0 for e in arcs}
    for T in triangles:
        for e in T:
            deg[e] += 1
    assert set(deg.values()) == {3}
    return arcs, ai, triangles


def build_base(arcs, ai, triangles):
    A = [[0]*55 for _ in range(55)]
    for r,T in enumerate(triangles):
        for e in T:
            A[r][ai[e]] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(55)) == 3 for j in range(55))
    supports = [{j for j,v in enumerate(row) if v} for row in A]
    assert all(
        len(supports[i] & supports[j]) <= 1
        for i in range(55) for j in range(i)
    )
    return A


def shift_perm(s):
    return tuple((c+s) % 3 for c in range(3))


def build_lift(ai, triangles):
    # Deterministic cyclic voltage rule:
    # triangle t uses copy maps
    #   first arc: c
    #   second:    c+t
    #   third:     c+(2t+1)      (all mod 3).
    A = [[0]*165 for _ in range(165)]
    for t,T in enumerate(triangles):
        p1 = shift_perm(t % 3)
        p2 = shift_perm((2*t + 1) % 3)
        ids = [ai[e] for e in T]
        for c in range(3):
            r = 3*t+c
            cols = (
                3*ids[0] + c,
                3*ids[1] + p1[c],
                3*ids[2] + p2[c],
            )
            for j in cols:
                A[r][j] = 1

    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(165)) == 3 for j in range(165))
    supports = [{j for j,v in enumerate(row) if v} for row in A]
    assert all(
        len(supports[i] & supports[j]) <= 1
        for i in range(165) for j in range(i)
    )
    return A


def levi_connected(A):
    m = len(A)
    n = len(A[0])
    adj = [[] for _ in range(m+n)]
    for i,row in enumerate(A):
        for j,v in enumerate(row):
            if v:
                adj[i].append(m+j)
                adj[m+j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == m+n


def root_vectors(arcs):
    # Eleven coordinate functions on the 55 Paley arc types.
    U = []
    for c in range(Q):
        U.append([
            (1 if i == c else 0) - (1 if j == c else 0)
            for i,j in arcs
        ])
    return U


def matvec(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def check_kernel_and_schur(arcs, A_lift):
    Ubase = root_vectors(arcs)

    # Repeat every base-arc value on its three lift copies.
    Ulift = []
    for u in Ubase:
        v = []
        for x in u:
            v.extend((x,x,x))
        Ulift.append(v)

    for u in Ulift:
        assert matvec(A_lift, u) == [0]*165

    # Root span dimension is 10.
    root_matrix = [[Ulift[c][j] for c in range(Q)] for j in range(165)]
    assert rank_q(root_matrix) == 10

    # Integer reduction mod 5 gives a lower bound on rational rank.
    # Together with the 10-dimensional rational kernel above:
    #   rank_Q <= 155 and rank_Q >= rank_F5 = 155.
    assert rank_mod_p(A_lift, 5) == 155

    # Therefore rank_Q=155 and K is exactly the copy-constant root space.
    # Three copies of each base arc have identical kernel coordinate rows.

    # Schur square on the 55 base arc types.
    products = []
    for a in range(Q):
        for b in range(a, Q):
            products.append([
                Ubase[a][j] * Ubase[b][j]
                for j in range(55)
            ])
    S2 = [[products[c][j] for c in range(len(products))] for j in range(55)]
    assert rank_mod_p(S2, 5) == 55

    # Hence K^(star 2) is the full 55-dimensional space W of functions
    # constant on the three copies of each base arc.
    #
    # There is a kernel vector nonzero on every base arc: use potentials t_i=i.
    nonzero = [i-j for i,j in arcs]
    assert all(x != 0 for x in nonzero)

    # Multiplication by that vector is an invertible diagonal map on W.
    # Therefore K^(star r)=W for every r>=2.

    return 155, 10, 55


def check_quotient_unsat(base):
    # KPROJ equality identifies the three lift copies of each base arc.
    # Every three lifted rows over one base triangle collapse to the same
    # base equation, so the quotient is exactly the 55x55 base source.
    assert len(base) == 55 and len(base[0]) == 55
    assert all(sum(row) == 3 for row in base)
    assert all(sum(base[i][j] for i in range(55)) == 3 for j in range(55))

    # If a Boolean exact cover S existed, summing all 55 equations gives
    # 3|S|=55, impossible.
    assert 55 % 3 != 0


def main():
    arcs, ai, triangles = paley()
    base = build_base(arcs, ai, triangles)
    lift = build_lift(ai, triangles)

    assert levi_connected(lift)
    rankQ, nullityQ, schur2dim = check_kernel_and_schur(arcs, lift)
    check_quotient_unsat(base)

    print("R5 E19 exact controls: PASS")
    print("base Paley source: n=55, cyclic triangles=55, col degree=3")
    print("lift: n=165, square/cubic/linear=True, Levi-connected=True")
    print(f"rank_Q(lift)={rankQ}, nullity_Q(lift)={nullityQ}")
    print(f"dim K^(star 2) on base arc types={schur2dim}=55")
    print("therefore K^(star r)=W for every r>=2")
    print("diagonal Schur-power hierarchy: PASS at every level")
    print("KPROJ quotient: 165 -> 55 variables -> cardinality UNSAT")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
