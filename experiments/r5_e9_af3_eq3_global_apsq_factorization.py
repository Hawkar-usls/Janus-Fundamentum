#!/usr/bin/env python3
"""Exact F3 regression for global APSQ factorization of the EQ3 regularizer.

Uses PG15 source affine space and constructs the regularizer coordinate forms
symbolically in source parameters alpha plus private gadget parameters p_x.
"""

P = 3
SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]


def matrix_from_rows(rows, n):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def rref_mod(M, p=P):
    A = [[x % p for x in row] for row in M]
    m = len(A); n = len(A[0]) if m else 0
    piv = []; r = 0
    for c in range(n):
        k = next((i for i in range(r, m) if A[i][c]), None)
        if k is None: continue
        A[r], A[k] = A[k], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(x*inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j]-f*A[r][j]) % p for j in range(n)]
        piv.append(c); r += 1
        if r == m: break
    return A, piv


def rank_mod(M):
    return len(rref_mod(M)[1])


def kernel_basis(M):
    R, piv = rref_mod(M)
    n = len(M[0])
    free = [j for j in range(n) if j not in piv]
    out = []
    for f in free:
        x = [0]*n; x[f] = 1
        for i,c in enumerate(piv): x[c] = (-R[i][f]) % P
        out.append(x)
    return out


def affine_one(A):
    n = len(A[0]); m = len(A)
    M = [[x % P for x in A[i]] + [1] for i in range(m)]
    r = 0; piv = []
    for c in range(n):
        k = next((i for i in range(r,m) if M[i][c]), None)
        if k is None: continue
        M[r],M[k] = M[k],M[r]
        inv = pow(M[r][c],-1,P)
        M[r] = [(x*inv)%P for x in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                f=M[i][c]
                M[i]=[(M[i][j]-f*M[r][j])%P for j in range(n+1)]
        piv.append(c); r+=1
    assert not any(all(M[i][j]==0 for j in range(n)) and M[i][n]
                   for i in range(r,m))
    x=[0]*n
    for i,c in enumerate(piv): x[c]=M[i][n]
    return x


def canonical_hyperplane(const, normal):
    # const + normal.dot(alpha) != 0 forbids normal.dot(alpha)=-const.
    k = next((i for i,x in enumerate(normal) if x % P), None)
    assert k is not None
    inv = pow(normal[k] % P, -1, P)
    a = tuple((inv*x) % P for x in normal)
    forbidden = ((-const) * inv) % P
    return a, forbidden


def main():
    n=15
    A=matrix_from_rows(SAT_ROWS,n)
    c=affine_one(A)
    K=kernel_basis(A)
    d=len(K)
    assert d==4 and rank_mod(A)==11
    B=[[K[t][i] for t in range(d)] for i in range(n)]

    # Source APSQ classes.
    src={}
    for x in range(n):
        a,off=canonical_hyperplane(c[x], B[x])
        src.setdefault(a,set()).add(off)
    assert len(src)==11
    assert all(len(v)==1 for v in src.values())
    src_rank=rank_mod([list(a) for a in src])
    assert src_rank==4
    src_eps=len(src)-src_rank
    assert src_eps==7

    D=d+n
    forms=[]
    for x in range(n):
        bx=B[x]
        # Q_x = c_x + b_x alpha
        forms.append(('Q',x,c[x], bx+[0]*n))
        # P_x = beta_x
        ep=[0]*n; ep[x]=1
        forms.append(('P',x,0, [0]*d+ep))
        # T_x = 1-c_x-b_x alpha-beta_x
        forms.append(('T',x,(1-c[x])%P,
                      [(-z)%P for z in bx]+[(-z)%P for z in ep]))

    groups={}
    labels={}
    for typ,x,const,normal in forms:
        a,off=canonical_hyperplane(const,normal)
        groups.setdefault(a,set()).add(off)
        labels.setdefault(a,[]).append((typ,x,off))

    # No pin or UNSAT class at the PG15 fixed point.
    assert all(len(v)==1 for v in groups.values())
    assert len(groups)==41

    q_groups=[a for a,L in labels.items() if any(t=='Q' for t,_,_ in L)]
    p_groups=[a for a,L in labels.items() if any(t=='P' for t,_,_ in L)]
    t_groups=[a for a,L in labels.items() if any(t=='T' for t,_,_ in L)]
    assert len(q_groups)==11
    assert len(p_groups)==15
    assert len(t_groups)==15

    # Any class containing coordinates from more than one source gadget is Q-only.
    for a,L in labels.items():
        gadgets={x for _,x,_ in L}
        if len(gadgets)>1:
            assert {typ for typ,_,_ in L}=={'Q'}

    normals=[list(a) for a in groups]
    rr=rank_mod(normals)
    eps=len(groups)-rr
    assert rr==19
    assert eps==22
    assert eps==n+src_eps

    # Local fibers after a source q pin.
    allowed={}
    for q in (1,2):
        vals=[]
        for p in (0,1,2):
            if p!=0 and (1-p-q)%P!=0:
                vals.append(p)
        allowed[q]=vals
    assert allowed=={1:[1,2],2:[1]}

    print({
        'status':'PASS_AF3_EQ3_GLOBAL_APSQ_FACTORIZATION',
        'source':'PG15',
        'source_classes':11,
        'source_rank':4,
        'source_epsilon':7,
        'regularizer_Q_classes':11,
        'regularizer_P_classes':15,
        'regularizer_T_classes':15,
        'regularizer_total_classes':41,
        'regularizer_normal_rank':rr,
        'regularizer_epsilon':eps,
        'cross_gadget_classes_are_Q_only':True,
        'local_extensions':allowed,
        'E8_D1':'EMPTY',
        'P_VS_NP':'OPEN',
    })


if __name__=='__main__':
    main()
