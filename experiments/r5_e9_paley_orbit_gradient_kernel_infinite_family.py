#!/usr/bin/env python3
"""Exact finite regression for the infinite Paley-orbit gradient-kernel family."""

from collections import deque
from fractions import Fraction


def is_prime(q):
    if q < 2:
        return False
    d = 2
    while d*d <= q:
        if q % d == 0:
            return False
        d += 1
    return True


def qr_set(q):
    return {pow(x,2,q) for x in range(1,q)}


def minus_two_orbit(q, s0=1):
    r = (-2) % q
    out = []
    seen = set()
    s = s0 % q
    while s not in seen:
        seen.add(s)
        out.append(s)
        s = (r*s) % q
    assert s == s0 % q
    return out


def build(q):
    assert is_prime(q) and q > 3 and q % 8 == 3
    QR = qr_set(q)
    r = (-2) % q
    assert r in QR
    O = minus_two_orbit(q, 1)
    assert set(O) <= QR

    variables = [(t,s) for s in O for t in range(q)]
    idx = {v:i for i,v in enumerate(variables)}
    rows = []
    for s in O:
        rs = (r*s) % q
        for t in range(q):
            rows.append((
                idx[(t,s)],
                idx[((t+s)%q,s)],
                idx[((t+2*s)%q,rs)],
            ))
    return O, variables, rows


def rank_mod2_rows(rows, n):
    basis = {}
    rank = 0
    for inds in rows:
        x = 0
        for j in inds:
            x ^= 1 << j
        while x:
            p = x.bit_length()-1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                rank += 1
                break
    return rank


def gauge_gradient_row(q, u, v):
    row = [0]*(q-1)
    if u != 0:
        row[u-1] -= 1
    if v != 0:
        row[v-1] += 1
    return tuple(row)


def rank_q(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r,m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        z = a[r][c]
        a[r] = [x/z for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                z = a[i][c]
                a[i] = [a[i][j]-z*a[r][j] for j in range(n)]
        r += 1
        if r == n:
            break
    return r


def levi_connected(n, rows):
    adj = [[] for _ in range(2*n)]
    for i, inds in enumerate(rows):
        for j in inds:
            adj[i].append(n+j)
            adj[n+j].append(i)
    seen={0}
    dq=deque([0])
    while dq:
        u=dq.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return len(seen)==2*n


def canonical_projective(row):
    first=next(x for x in row if x)
    return tuple(row if first>0 else tuple(-x for x in row))


def check(q):
    O, variables, rows = build(q)
    n=len(variables)
    L=len(O)
    assert n==q*L and len(rows)==n

    coldeg=[0]*n
    for row in rows:
        assert len(set(row))==3
        for j in row:
            coldeg[j]+=1
    assert set(coldeg)=={3}

    supports=[set(r) for r in rows]
    assert all(len(supports[i]&supports[j])<=1
               for i in range(n) for j in range(i+1,n))
    assert levi_connected(n, rows)

    D=[]
    for u,s in variables:
        v=(u+s)%q
        D.append(gauge_gradient_row(q,u,v))
    assert rank_q(D)==q-1
    for inds in rows:
        summed=[sum(D[j][c] for j in inds) for c in range(q-1)]
        assert not any(summed)

    # For these finite controls, mod-2 rank reaches the rational upper bound
    # implied by the (q-1)-dimensional gradient kernel.
    r2=rank_mod2_rows(rows,n)
    assert r2==n-(q-1), (q,L,n,r2,n-(q-1))

    assert all(any(row) for row in D)
    keys=[canonical_projective(row) for row in D]
    assert len(set(keys))==len(keys)

    assert q % 3 != 0
    assert all(3*k-q != 0 for k in range(q+1))

    print(f"q={q} L={L} n={n} rank_Q={n-(q-1)} nullity_Q={q-1} "
          f"mod2_rank={r2} RKPR=clean UNSAT=cycle")


def main():
    for q in (11,19,43):
        check(q)
    print("PALEY_ORBIT_GRADIENT_KERNEL_INFINITE_FAMILY finite regression: PASS")


if __name__=="__main__":
    main()
