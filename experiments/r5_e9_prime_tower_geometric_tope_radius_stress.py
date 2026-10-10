#!/usr/bin/env python3
"""Exact chamber-graph stress test on the frozen singular prime tower.

This checker is deliberately finite: it exhausts the complete projective
rational-kernel arrangements for the n=30,d=2 and n=60,d=3 tower stages.
All arithmetic used to construct/project the arrangements is rational.
No random sampling and no floating-point LP is used.

Scientific ceiling: this is evidence against tiny geometric augmentation
radii, not a proof that the required radius is unbounded.
"""

from __future__ import annotations

from collections import defaultdict, deque
from fractions import Fraction
from itertools import combinations

ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]

G = [1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1]
Z = [-7,-4,3,1,-2,2,-1,-4,6,8,2,-3,-5,1,5]
SEED_SIGNING = ((0,12),(2,9))
RECURSIVE_PAIR = ((0,5),(1,1))


def matrix_from_rows(rows, n):
    A = [[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


def rank_q(M):
    A = [[Fraction(v) for v in row] for row in M]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r,m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        z = A[r][c]
        A[r] = [x/z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                z = A[i][c]
                A[i] = [A[i][j]-z*A[r][j] for j in range(n)]
        r += 1
    return r


def mv(A, x):
    return [sum(Fraction(a)*Fraction(b) for a,b in zip(row,x)) for row in A]


def signed(A, neg):
    S = [row[:] for row in A]
    for i,j in neg:
        assert S[i][j] == 1
        S[i][j] = -1
    return S


def lift(A, neg):
    n = len(A)
    neg = set(neg)
    H = [[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            if not A[i][j]:
                continue
            if (i,j) in neg:
                H[i][j+n] = 1
                H[i+n][j] = 1
            else:
                H[i][j] = 1
                H[i+n][j+n] = 1
    return H


def sym(v):
    return list(v)+list(v)


def asym(v):
    return list(v)+[-Fraction(x) for x in v]


def zero_eval_basis(W, j):
    vals = [Fraction(w[j]) for w in W]
    if all(v == 0 for v in vals):
        return [list(map(Fraction,w)) for w in W]
    p = next(i for i,v in enumerate(vals) if v)
    out = []
    for q in range(len(W)):
        if q == p:
            continue
        coeff = [Fraction(0)]*len(W)
        coeff[q] = 1
        coeff[p] = -vals[q]/vals[p]
        v = [sum(coeff[t]*Fraction(W[t][r]) for t in range(len(W)))
             for r in range(len(W[0]))]
        assert v[j] == 0
        out.append(v)
    return out


def canonical(v):
    v = tuple(Fraction(x) for x in v)
    j = next(i for i,x in enumerate(v) if x)
    z = v[j]
    return tuple(x/z for x in v)


def projective_classes(W):
    n = len(W[0])
    classes = defaultdict(list)
    for i in range(n):
        p = tuple(Fraction(W[k][i]) for k in range(len(W)))
        assert any(p)
        c = canonical(p)
        j = next(k for k,x in enumerate(c) if x)
        lam = p[j]
        classes[c].append((i, 1 if lam > 0 else -1))
    return dict(classes)


def raw_signs(class_signs, classes, cs):
    n = sum(len(classes[c]) for c in cs)
    out = [None]*n
    for s,c in zip(class_signs,cs):
        for i,eps in classes[c]:
            out[i] = eps*s
    assert all(x in (-1,1) for x in out)
    return tuple(out)


def class_signs_from_raw(raw, classes, cs):
    out = []
    for c in cs:
        i,eps = classes[c][0]
        s = raw[i]*eps
        assert all(raw[j] == e*s for j,e in classes[c])
        out.append(s)
    return tuple(out)


def positive_count(class_signs, classes, cs):
    return sum(
        1
        for s,c in zip(class_signs,cs)
        for _,eps in classes[c]
        if eps*s > 0
    )


def rank2_patterns(normals):
    """All topes of a central rank-2 arrangement, exact in two affine charts."""
    normals = [tuple(map(Fraction,v)) for v in normals]
    assert all(a or b for a,b in normals)
    pats = set()

    def chart(swap):
        roots = set()
        for a,b in normals:
            A,B = (b,a) if swap else (a,b)
            if B:
                roots.add(-A/B)
        roots = sorted(roots)
        if roots:
            samples = [roots[0]-1]
            samples += [(x+y)/2 for x,y in zip(roots,roots[1:])]
            samples += [roots[-1]+1]
        else:
            samples = [Fraction(0)]
        for t in samples:
            q = (t,1) if swap else (1,t)
            vals = [a*q[0]+b*q[1] for a,b in normals]
            if any(v == 0 for v in vals):
                continue
            s = tuple(1 if v > 0 else -1 for v in vals)
            pats.add(s)
            pats.add(tuple(-x for x in s))

    chart(False)
    chart(True)
    return pats


def enumerate_rank2(classes):
    cs = list(classes)
    assert all(len(c) == 2 for c in cs)
    topes = rank2_patterns(cs)
    assert topes
    return cs, topes


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def cross(a,b):
    return (
        a[1]*b[2]-a[2]*b[1],
        a[2]*b[0]-a[0]*b[2],
        a[0]*b[1]-a[1]*b[0],
    )


def enumerate_rank3(classes):
    """Exhaust all chambers of an essential central rank-3 arrangement.

    Every chamber closure has an extreme ray.  Such a ray is an intersection
    of at least two projective hyperplanes.  Around every pair-intersection
    ray we enumerate the exact rank-2 local sectors of all hyperplanes
    containing that ray.  Taking both orientations of the ray emits every
    full-dimensional chamber.
    """
    cs = list(classes)
    assert all(len(c) == 3 for c in cs)
    topes = set()

    for i,j in combinations(range(len(cs)),2):
        ray = cross(cs[i],cs[j])
        if not any(ray):
            continue
        zero = [k for k,c in enumerate(cs) if dot(c,ray) == 0]
        if len(zero) < 2:
            continue

        u = cs[zero[0]]
        v = next(cs[k] for k in zero[1:] if any(cross(u,cs[k])))
        coeff = [(dot(cs[k],u),dot(cs[k],v)) for k in zero]
        local = rank2_patterns(coeff)
        nonzero = [k for k in range(len(cs)) if k not in zero]
        fixed = {k:(1 if dot(cs[k],ray) > 0 else -1) for k in nonzero}

        for loc in local:
            for ray_sign in (1,-1):
                s = [None]*len(cs)
                for k,val in fixed.items():
                    s[k] = ray_sign*val
                for q,k in enumerate(zero):
                    s[k] = loc[q]
                topes.add(tuple(s))

    assert topes
    return cs, topes


def tope_graph(topes):
    T = set(topes)
    m = len(next(iter(T)))
    G = {}
    for s in T:
        nb = []
        for k in range(m):
            t = list(s)
            t[k] *= -1
            t = tuple(t)
            if t in T:
                nb.append(t)
        G[s] = nb
    # Exact tope graphs of real arrangements are connected; this also catches
    # an incomplete chamber enumeration.
    root = next(iter(T))
    seen = {root}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in G[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    assert seen == T
    return G


def escape_radius(s, p, G, pval):
    q = deque([(s,0)])
    seen = {s}
    while q:
        u,d = q.popleft()
        if d and pval[u] < p:
            return d
        for v in G[u]:
            if v not in seen:
                seen.add(v)
                q.append((v,d+1))
    return None


def strict_local_minima(G, pval):
    out = []
    for s,nb in G.items():
        p = pval[s]
        if all(p < pval[t] for t in nb):
            out.append((s,p,escape_radius(s,p,G,pval)))
    return out


def main():
    A0 = matrix_from_rows(ROWS,15)
    assert rank_q(A0) == 14
    assert mv(A0,G) == [0]*15

    S0 = signed(A0,SEED_SIGNING)
    assert rank_q(S0) == 14
    assert mv(S0,Z) == [0]*15

    # n=30, d=2 exact tower stage.
    A1 = lift(A0,SEED_SIGNING)
    assert rank_q(A1) == 28
    W1 = [list(map(Fraction,sym(G))), list(map(Fraction,asym(Z)))]
    assert all(mv(A1,w) == [0]*30 for w in W1)
    assert rank_q(list(map(list,zip(*W1)))) == 2

    C1 = projective_classes(W1)
    cs1,T1 = enumerate_rank2(C1)
    assert len(C1) == 12
    assert len(T1) == 24
    G1 = tope_graph(T1)
    p1 = {s:positive_count(s,C1,cs1) for s in T1}
    assert min(p1.values()) == 12
    L1 = strict_local_minima(G1,p1)
    finite1 = [r for _,p,r in L1 if p > min(p1.values())]
    assert max(finite1) == 5

    # n=60, d=3 exact tower stage.
    F = RECURSIVE_PAIR
    assert all(A1[i][j] == 1 for i,j in F)
    A2 = lift(A1,F)
    assert rank_q(A2) == 57
    W10 = zero_eval_basis(W1,F[0][1])
    assert len(W10) == 1
    W2 = [sym(w) for w in W1] + [asym(w) for w in W10]
    assert len(W2) == 3
    assert all(mv(A2,w) == [0]*60 for w in W2)
    assert rank_q(list(map(list,zip(*W2)))) == 3

    C2 = projective_classes(W2)
    cs2,T2 = enumerate_rank3(C2)
    assert len(C2) == 23
    assert len(T2) == 288
    G2 = tope_graph(T2)
    p2 = {s:positive_count(s,C2,cs2) for s in T2}
    assert min(p2.values()) == 24
    L2 = strict_local_minima(G2,p2)
    finite2 = [r for _,p,r in L2 if p > min(p2.values())]
    assert max(finite2) == 9

    # Bind the radius-9 trap directly to a duplicated radius-5 stage-1 trap.
    amplified = []
    for s,p,r in L1:
        if r != 5:
            continue
        raw1 = raw_signs(s,C1,cs1)
        raw2 = raw1 + raw1
        s2 = class_signs_from_raw(raw2,C2,cs2)
        if s2 in T2:
            r2 = escape_radius(s2,p2[s2],G2,p2)
            amplified.append((p,p2[s2],r2))
    assert (15,30,9) in amplified

    print({
        'status': 'PASS_PRIME_TOWER_GEOMETRIC_TOPE_RADIUS_STRESS',
        'stage_n30': {
            'kernel_dimension': 2,
            'projective_hyperplanes': len(C1),
            'chambers': len(T1),
            'source_depth_floor': 10,
            'exact_min_p': min(p1.values()),
            'max_nonglobal_local_escape_radius': max(finite1),
        },
        'stage_n60': {
            'kernel_dimension': 3,
            'projective_hyperplanes': len(C2),
            'chambers': len(T2),
            'source_depth_floor': 20,
            'exact_min_p': min(p2.values()),
            'max_nonglobal_local_escape_radius': max(finite2),
        },
        'amplified_control': 'radius 5 at n=30 -> radius 9 at n=60',
        'unbounded_geometric_radius': 'NOT_PROVED',
        'universal_polynomial_decider': 'OPEN',
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
