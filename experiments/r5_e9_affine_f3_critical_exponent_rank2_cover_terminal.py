#!/usr/bin/env python3
"""Exact finite regression for CE3-1 and R2C-1/R2C-2.

No floating point arithmetic. The arbitrary-size critical-exponent and rank-2
projection theorems are proved in the companion markdown.
"""
from itertools import combinations, product

UNSAT_ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]


def mat_from_rows(rows, n):
    A = [[0]*n for _ in range(len(rows))]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


def rref_aug(A, b, p=3):
    m, n = len(A), len(A[0])
    M = [[x % p for x in A[i]] + [b[i] % p] for i in range(m)]
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r,m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c], -1, p)
        M[r] = [(x*inv) % p for x in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(M[i][j]-f*M[r][j]) % p for j in range(n+1)]
        pivots.append(c)
        r += 1
    for i in range(r,m):
        if all(M[i][c] == 0 for c in range(n)) and M[i][n] != 0:
            return None, None
    free = [c for c in range(n) if c not in pivots]
    x0 = [0]*n
    for i,c in enumerate(pivots):
        x0[c] = M[i][n]
    basis = []
    for f in free:
        v = [0]*n
        v[f] = 1
        for i,c in enumerate(pivots):
            v[c] = (-M[i][f]) % p
        basis.append(v)
    return x0, basis


def affine_solutions(A,b):
    x0,basis = rref_aug(A,b)
    if x0 is None:
        return []
    out=[]
    for coeff in product(range(3), repeat=len(basis)):
        x=x0[:]
        for a,v in zip(coeff,basis):
            for j in range(len(x)):
                x[j]=(x[j]+a*v[j])%3
        out.append(tuple(x))
    return out


def kernel_solutions(M):
    return affine_solutions(M,[0]*len(M))


def support(v):
    return {i for i,x in enumerate(v) if x != 0}


def critical_exponent_le2_control(A, expected_sat):
    n=len(A[0])
    aff=affine_solutions(A,[1]*len(A))
    assert aff, "control must be F3-consistent"
    aug=[row+[2] for row in A]  # -1 mod 3
    C=kernel_solutions(aug)
    full=[c for c in C if all(x != 0 for x in c)]
    if expected_sat:
        assert full
    else:
        assert not full
        c0=tuple([1]*n+[0])
        assert c0 in C
        c1=tuple(list(aff[0])+[1])
        assert c1 in C
        assert support(c0) | support(c1) == set(range(n+1))
    return len(aff),len(C),len(full)


def ag23_lines():
    points=list(product(range(3),repeat=2))
    dirs=((1,0),(0,1),(1,1),(1,2))
    lines=[]
    for a in dirs:
        for c in range(3):
            pts=frozenset(
                p for p in points
                if (a[0]*p[0]+a[1]*p[1])%3 == c
            )
            assert len(pts)==3
            lines.append((a,c,pts))
    return points,lines


def minimal_cover_census():
    points,lines=ag23_lines()
    universe=set(points)
    sizes=[]
    examples={}
    for mask in range(1,1<<len(lines)):
        inds=[i for i in range(len(lines)) if (mask>>i)&1]
        union=set().union(*(lines[i][2] for i in inds))
        if union != universe:
            continue
        minimal=True
        for i in inds:
            u=set()
            for j in inds:
                if j != i:
                    u.update(lines[j][2])
            if u == universe:
                minimal=False
                break
        if minimal:
            sizes.append(len(inds))
            examples.setdefault(len(inds),tuple(inds))
    assert set(sizes)=={3,4,5}
    assert max(sizes)==5
    assert len(sizes)==121
    return {s:sizes.count(s) for s in sorted(set(sizes))},examples


def rank_mod3(vectors):
    if not vectors:
        return 0
    _,kernel_basis = rref_aug([list(v) for v in vectors],[0]*len(vectors))
    return len(vectors[0]) - len(kernel_basis)


def covers_affine_space(forms, dim):
    for alpha in product(range(3), repeat=dim):
        if not any(sum(a*x for a,x in zip(n,alpha))%3 == c%3
                   for n,c in forms):
            return False
    return True


def detector(forms):
    N=len(forms)
    for r in range(1,min(5,N)+1):
        for I in combinations(range(N),r):
            chosen=[forms[i] for i in I]
            rank=rank_mod3([n for n,_ in chosen if any(n)])
            if rank > 2:
                continue
            dim=len(chosen[0][0])
            if covers_affine_space(chosen,dim):
                return I
    return None


def main():
    census,examples=minimal_cover_census()
    assert census == {3:4,4:9,5:108}, census

    _,lines=ag23_lines()
    I5=examples[5]
    forms5=[(lines[i][0],lines[i][1]) for i in I5]
    assert rank_mod3([n for n,_ in forms5]) == 2
    assert covers_affine_space(forms5,2)
    assert detector(forms5) is not None

    A_sat=[[1,1,1] for _ in range(3)]
    sat_stats=critical_exponent_le2_control(A_sat, True)

    A_unsat=mat_from_rows(UNSAT_ROWS,15)
    assert all(sum(row)==3 for row in A_unsat)
    assert all(sum(A_unsat[i][j] for i in range(15))==3 for j in range(15))
    unsat_stats=critical_exponent_le2_control(A_unsat, False)
    assert unsat_stats[0] == 3

    print("PASS CE3-1 / rank-2 AF3 cover terminal")
    print("AG(2,3) minimal-cover census", census)
    print("SAT J3 stats (affine,code,full)",sat_stats)
    print("UNSAT 15_3 stats (affine,code,full)",unsat_stats)
    print("RANK2_CERTIFICATE_MAX_SIZE=5")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__=="__main__":
    main()
