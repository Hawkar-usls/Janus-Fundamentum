#!/usr/bin/env python3
"""Exact controls for R5 E20 kernel-local projection terminal."""

from fractions import Fraction
from itertools import combinations, product

Q = 11
ALPHABET = (-1, 2)

def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m, n = len(A), (len(A[0]) if A else 0)
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
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r

def rank_mod_p(M, p):
    A = [[x % p for x in row] for row in M]
    m, n = len(A), (len(A[0]) if A else 0)
    r = 0
    for c in range(n):
        q = next((i for i in range(r, m) if A[i][c]), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
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
    arcs = [(i,j) for i in range(Q) for j in range(Q)
            if i != j and ((j-i) % Q) in residues]
    ai = {a:i for i,a in enumerate(arcs)}
    triangles = []
    for a,b,c in combinations(range(Q), 3):
        for cyc in ((a,b,c),(a,c,b)):
            T = ((cyc[0],cyc[1]), (cyc[1],cyc[2]), (cyc[2],cyc[0]))
            if all(e in ai for e in T):
                triangles.append(T)
    assert len(arcs) == len(triangles) == 55
    return arcs, ai, triangles

def build_base(arcs, ai, triangles):
    A = [[0]*55 for _ in range(55)]
    for r,T in enumerate(triangles):
        for e in T:
            A[r][ai[e]] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(55)) == 3 for j in range(55))
    supp = [{j for j,v in enumerate(row) if v} for row in A]
    assert all(len(supp[i] & supp[j]) <= 1
               for i in range(55) for j in range(i))
    return A

def root_basis(arcs):
    B = [[(1 if i == c else 0) - (1 if j == c else 0)
          for c in range(10)] for i,j in arcs]
    assert rank_q(B) == 10
    return B

def proportional(u, v):
    lam = None
    for a,b in zip(u,v):
        if a:
            q = Fraction(b, a)
            if lam is None:
                lam = q
            elif lam != q:
                return None
        elif b:
            return None
    return lam

def local_patterns(B, S):
    M = [B[i] for i in S]
    r = rank_q(M)
    out = []
    for sig in product(ALPHABET, repeat=len(S)):
        aug = [M[i] + [sig[i]] for i in range(len(S))]
        if rank_q(aug) == r:
            out.append(sig)
    return out

def check():
    arcs, ai, triangles = paley()
    A = build_base(arcs, ai, triangles)
    B = root_basis(arcs)

    # B spans a 10D kernel and rank_F5(A)=45, so rank_Q(A)=45 exactly.
    for row in A:
        for c in range(10):
            assert sum(row[j]*B[j][c] for j in range(55)) == 0
    assert rank_mod_p(A, 5) == 45

    # KLOC-2/KPROJ is clean.
    assert all(any(x for x in row) for row in B)
    for i,j in combinations(range(55), 2):
        assert proportional(B[i], B[j]) is None

    rank2 = compatible = incompatible = 0
    for S in combinations(range(55), 3):
        if rank_q([B[i] for i in S]) != 2:
            continue
        rank2 += 1
        if local_patterns(B, S):
            compatible += 1
        else:
            incompatible += 1

    assert (rank2, compatible, incompatible) == (165, 55, 110)

    S = (ai[(0,1)], ai[(0,3)], ai[(3,1)])
    assert S == (0, 1, 15)
    assert local_patterns(B, S) == []
    assert all(-B[S[0]][c] + B[S[1]][c] + B[S[2]][c] == 0
               for c in range(10))
    assert all(-a+b+c != 0 for a,b,c in product(ALPHABET, repeat=3))

    print("R5 E20 exact controls: PASS")
    print("Paley-11: n=55, rank_Q=45, nullity_Q=10")
    print("KLOC-2/KPROJ: clean (0 proportional pairs)")
    print("KLOC-3 rank-2 triples: 55 compatible, 110 incompatible")
    print("explicit bad triple: 0->1, 0->3, 3->1")

if __name__ == "__main__":
    check()
