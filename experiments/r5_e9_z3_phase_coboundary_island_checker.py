#!/usr/bin/env python3
from fractions import Fraction
from itertools import product

def invert_perm(P):
    inv=[0]*len(P)
    for i,j in enumerate(P): inv[j]=i
    return inv

def phase_potential(P,Q):
    n=len(P)
    invP,invQ=invert_perm(P),invert_perm(Q)
    phi=[None]*n
    for root in range(n):
        if phi[root] is not None: continue
        phi[root]=0
        stack=[root]
        while stack:
            i=stack.pop()
            for j,inc in ((P[i],1),(Q[i],-1),(invP[i],-1),(invQ[i],1)):
                want=(phi[i]+inc)%3
                if phi[j] is None:
                    phi[j]=want
                    stack.append(j)
                elif phi[j]!=want:
                    return None
    return tuple(phi)

def connected(P,Q):
    return phase_orbit(P,Q)==set(range(len(P)))

def phase_orbit(P,Q):
    invP,invQ=invert_perm(P),invert_perm(Q)
    seen={0}; stack=[0]
    while stack:
        i=stack.pop()
        for R in (P,Q,invP,invQ):
            j=R[i]
            if j not in seen:
                seen.add(j); stack.append(j)
    return seen

def rank_q(A):
    M=[[Fraction(x) for x in row] for row in A]
    m=len(M); n=len(M[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        q=M[r][c]
        M[r]=[x/q for x in M[r]]
        for i in range(m):
            if i==r: continue
            q=M[i][c]
            if q:
                M[i]=[x-q*y for x,y in zip(M[i],M[r])]
        r+=1
        if r==m: break
    return r

def matrix(P,Q):
    n=len(P)
    A=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i,P[i],Q[i]):
            A[i][j]+=1
    return A

def matvec(A,z):
    return tuple(sum(a*b for a,b in zip(row,z)) for row in A)

def canonical_phase_words(phi):
    out=[]
    for r in range(3):
        x=tuple(1 if p==r else 0 for p in phi)
        z=tuple(3*b-1 for b in x)
        out.append(z)
    return out

def special_family(m):
    pts=[(r,a) for r in range(3) for a in range(m)]
    idx={p:i for i,p in enumerate(pts)}
    P=[]; Q=[]
    for r,a in pts:
        P.append(idx[((r+1)%3,a)])
        if r==0: q=(2,(a+1)%m)
        elif r==1: q=(0,a)
        else: q=(1,a)
        Q.append(idx[q])
    return pts,tuple(P),tuple(Q)

def main():
    # Infinite noncommuting, phase-consistent, large-nullity family.
    for m in range(2,8):
        pts,P,Q=special_family(m)
        n=3*m
        assert connected(P,Q)
        assert any(P[Q[i]]!=Q[P[i]] for i in range(n))
        phi=phase_potential(P,Q)
        assert phi is not None
        assert all(phi[i]==pts[i][0] for i in range(n))

        A=matrix(P,Q)
        d=n-rank_q(A)
        assert d==m+1

        for z in canonical_phase_words(phi):
            assert matvec(A,z)==(0,)*n

        # Exact word count from the closed form:
        # z_{2,a}=c globally; if c=2 => one word, if c=-1 => 2^m.
        count=1+(1<<m)
        if m<=5:
            brute=0
            for z in product((-1,2), repeat=n):
                if matvec(A,z)==(0,)*n:
                    brute+=1
            assert brute==count

    # Phase-inconsistent does NOT imply UNSAT.
    P=(0,2,1,4,5,3)
    Q=(1,0,3,5,2,4)
    assert connected(P,Q)
    assert phase_potential(P,Q) is None
    A=matrix(P,Q)
    assert 6-rank_q(A)==2
    words=[
        z for z in product((-1,2), repeat=6)
        if matvec(A,z)==(0,)*6
    ]
    assert words==[
        (-1,2,-1,-1,-1,2),
        (-1,2,-1,-1,2,-1),
    ]

    # Alphabet does not factor across a trivial + sign decomposition.
    w=(2,-1)
    trivial=((Fraction(1,2),Fraction(1,2)))
    sign=((Fraction(3,2),Fraction(-3,2)))
    assert tuple(trivial[i]+sign[i] for i in range(2))==w
    assert any(v not in (-1,2) for v in trivial)
    assert any(v not in (-1,2) for v in sign)

    print("Z3_PHASE_BFS = PASS")
    print("PHASE_IMPLIES_THREE_CANONICAL_EXACT_WORDS = PASS")
    print("NONCOMMUTING_LARGE_NULLITY_PHASE_FAMILY_d=m+1 = PASS")
    print("SPECIAL_FAMILY_EXACT_WORD_COUNT = 2^m+1")
    print("PHASE_FAIL_DOES_NOT_IMPLY_UNSAT = PASS")
    print("IRREP_PROJECTION_ALPHABET_FACTORING = FALSE_IN_GENERAL")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
