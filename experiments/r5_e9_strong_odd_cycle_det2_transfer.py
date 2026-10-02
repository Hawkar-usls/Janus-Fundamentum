#!/usr/bin/env python3
from fractions import Fraction
from itertools import product


def det_q(M):
    M = [[Fraction(x) for x in row] for row in M]
    n = len(M)
    det = Fraction(1)
    for c in range(n):
        p = next((r for r in range(c,n) if M[r][c] != 0), None)
        if p is None:
            return 0
        if p != c:
            M[c], M[p] = M[p], M[c]
            det = -det
        piv = M[c][c]
        det *= piv
        for j in range(c,n):
            M[c][j] /= piv
        for r in range(c+1,n):
            if M[r][c] != 0:
                f = M[r][c]
                for j in range(c,n):
                    M[r][j] -= f*M[c][j]
    assert det.denominator == 1
    return int(det)


def cycle_matrix(k):
    M = [[0]*k for _ in range(k)]
    for i in range(k):
        M[i][i] = 1
        M[i][(i+1)%k] = 1
    return M


def belt_direct(k):
    out = set()
    for v in product((0,1), repeat=k):
        if any(v[i] + v[(i+1)%k] > 1 for i in range(k)):
            continue
        w = tuple(1-v[i]-v[(i+1)%k] for i in range(k))
        out.add(w)
    return out


def belt_formula(k):
    out = set()
    for w in product((0,1), repeat=k):
        sig = []
        for i in range(k):
            s = sum(((-1)**t)*w[(i+t)%k] for t in range(k))
            sig.append(s)
        if all(s in (-1,1) for s in sig):
            # Reconstruction and local transfer must both hold.
            v = tuple((1-s)//2 for s in sig)
            assert all(v[i]+v[(i+1)%k]+w[i] == 1 for i in range(k))
            assert all(sig[(i+1)%k] == 2*w[i]-sig[i] for i in range(k))
            out.add(tuple(w))
    return out


def full_direct(k):
    out = set()
    for v in product((0,1), repeat=k):
        if any(v[i] + v[(i+1)%k] > 1 for i in range(k)):
            continue
        w = tuple(1-v[i]-v[(i+1)%k] for i in range(k))
        choices = []
        for i in range(k):
            choices.append(((0,0),) if v[i] else ((1,0),(0,1)))
        for pairs in product(*choices):
            a = tuple(p[0] for p in pairs)
            b = tuple(p[1] for p in pairs)
            out.add(w+a+b)
    return out


def full_transfer(k):
    out = set()
    for sigma in product((-1,1), repeat=k):
        # w is forced by t=2w-s, so require numerator 0 or 2.
        w = []
        ok = True
        for i in range(k):
            num = sigma[(i+1)%k] + sigma[i]
            if num not in (0,2):
                ok = False
                break
            w.append(num//2)
        if not ok:
            continue
        choices = []
        for s in sigma:
            choices.append(((0,0),) if s == -1 else ((1,0),(0,1)))
        for pairs in product(*choices):
            a = tuple(p[0] for p in pairs)
            b = tuple(p[1] for p in pairs)
            # Exact B_i identity.
            assert all(2*(a[i]+b[i]) == 1+sigma[i] for i in range(k))
            out.add(tuple(w)+a+b)
    return out


for k in (3,5,7,9):
    assert det_q(cycle_matrix(k)) == 2

for k in (3,5,7):
    bd = belt_direct(k)
    bf = belt_formula(k)
    assert bd == bf

    fd = full_direct(k)
    ft = full_transfer(k)
    assert fd == ft

    print(f"k={k} belt={len(bd)} full={len(fd)} PASS")

# Special k=3 collapse: belt feasibility is exactly odd parity.
b3 = belt_direct(3)
odd3 = {w for w in product((0,1), repeat=3) if sum(w)%2 == 1}
assert b3 == odd3

print("PASS strong odd-cycle det2/full-boundary transfer normal form")
