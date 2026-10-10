#!/usr/bin/env python3
"""Exact degree-2 moment-SDP attack on the universal SCL Exact-One solver.

Build a *rational* level-1 Boolean/Exact-One pseudo-moment matrix on
the known E123/GH(2,2) UNSAT carrier; the matrix is proven PSD via an
INTEGER projector H satisfying H^2 = 36 H and A H = 0.

This demonstrates that ordinary quadratic moment consistency is NOT
a universal SAT/UNSAT discriminator. It is not an algorithm proving P=NP.
No SDP package, floating point, randomness, or optimizer is used.
"""
from __future__ import annotations
from collections import Counter, deque

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis


def levi_graph(A):
    n=len(A)
    g=[[] for _ in range(2*n)]
    for i,row in enumerate(A):
        assert len(row)==n and sum(row)==3
        for j,v in enumerate(row):
            assert v in (0,1)
            if v:
                g[i].append(n+j)
                g[n+j].append(i)
    assert all(len(xs)==3 for xs in g)
    return g


def distances(graph, source):
    d=[-1]*len(graph)
    d[source]=0
    q=deque([source])
    while q:
        v=q.popleft()
        for w in graph[v]:
            if d[w]==-1:
                d[w]=d[v]+1
                q.append(w)
    assert all(x>=0 for x in d)
    return d


def exact_unsat_from_f2_kernel(A):
    n=len(A)
    _,_,basis=gf2_rref_basis(A)
    assert n==63 and len(basis)==14
    max_weight=0
    for selection in range(1<<len(basis)):
        k=0
        for i,b in enumerate(basis):
            if (selection>>i)&1:
                k ^= b
        max_weight=max(max_weight,k.bit_count())
        assert k.bit_count() != 2*n//3
    assert max_weight==40 < 42
    return max_weight


def verify_transpose_true_moments(A):
    """The SAT transpose realizes the SAME shell moment formula honestly."""
    n=len(A)
    AT=[list(row) for row in zip(*A)]
    graph=levi_graph(AT)
    D=[distances(graph,n+i)[n:] for i in range(n)]
    scale={0:8,2:-4,4:2,6:-1}
    H=[[scale[d] for d in row] for row in D]
    assert all(
        sum(AT[i][k]*H[k][j] for k in range(n))==0
        for i in range(n) for j in range(n)
    )
    assert all(
        sum(H[i][k]*H[k][j] for k in range(n))==36*H[i][j]
        for i in range(n) for j in range(n)
    )
    _,_,basis=gf2_rref_basis(AT)
    assert len(basis)==14
    models=[]
    ones=(1<<n)-1
    rowbits=[sum(1<<j for j,v in enumerate(row) if v) for row in AT]
    for mask in range(1<<len(basis)):
        k=0
        for i,word in enumerate(basis):
            if (mask>>i)&1:
                k ^= word
        x=ones^k
        if x.bit_count()==n//3:
            assert all((rb&x).bit_count()==1 for rb in rowbits)
            models.append(x)
    assert len(models)==36
    expected={0:12,2:0,4:6,6:3}
    for i in range(n):
        for j in range(n):
            real_count=sum(((w>>i)&1) and ((w>>j)&1) for w in models)
            assert real_count==expected[D[i][j]], (i,j,D[i][j],real_count)
            assert real_count==4+H[i][j]
    print("Transpose SAT: all 36 Boolean witnesses realize the SAME shell moment profile")
    print("Real pair counts among 36 witnesses: d=0:12 d=2:0 d=4:6 d=6:3")


def main():
    A=tutte12_incidence()
    n=len(A)
    assert n==63
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    bad_top_weight=exact_unsat_from_f2_kernel(A)

    graph=levi_graph(A)
    D=[
        distances(graph,n+i)[n:]
        for i in range(n)
    ]
    expected=Counter({0:1,2:6,4:24,6:32})
    assert all(Counter(row)==expected for row in D)
    assert all(D[i][j]==D[j][i] for i in range(n) for j in range(n))

    # Let H=36 C be an integer rescaling of the covariance matrix.
    # For variable-to-variable Levi distances 0,2,4,6:
    # H(d)=8,-4,2,-1.
    scale={0:8,2:-4,4:2,6:-1}
    H=[[scale[D[i][j]] for j in range(n)] for i in range(n)]
    assert sum(H[i][i] for i in range(n))==504

    # AH=0 and H 1=0 => C has support entirely inside ker(A).
    assert all(sum(row)==0 for row in H)
    assert all(
        sum(A[i][k]*H[k][j] for k in range(n))==0
        for i in range(n) for j in range(n)
    )
    # EXACT PSD certificate: symmetry and H^2=36H force
    # eigenvalues(H) in {0,36}. Its rank is trace(H)/36=14.
    assert all(
        sum(H[i][k]*H[k][j] for k in range(n))==36*H[i][j]
        for i in range(n) for j in range(n)
    )

    # Mu_i=1/3, M_ij=(4+H_ij)/36.
    # The block moment matrix [[1,mu'],[mu,M]] has covariance
    # C=M-mu mu'=H/36 >= 0, hence the full block matrix is PSD.
    M36=[[4+H[i][j] for j in range(n)] for i in range(n)]
    assert all(M36[i][i]==12 for i in range(n))
    assert all(M36[i][j]==0 for i in range(n) for j in range(n)
               if D[i][j]==2)
    # Every check is true as a linear identity in the moment functional:
    # E[sum_{v in check} x_v]=1 and
    # E[x_i (sum_{v in check} x_v-1)]=0 for every i.
    assert all(
        sum(A[c][k]*M36[k][i] for k in range(n))==12
        for c in range(n) for i in range(n)
    )
    # E[(sum x_in_check-1)^2]=0 follows from the Boolean
    # diagonal and zero offdiagonals for two variables in a check.
    assert all(
        sum(M36[u][v] for u in range(n) for v in range(n)
            if A[c][u] and A[c][v]) ==36
        for c in range(n)
    )

    # Conditioning the pseudo *first* moments at one chosen variable:
    # E[x_i x_j]/E[x_j]=3*M_ij in {1,0,1/2,1/4}.
    # These recover precisely the previous Levi-shell LP vectors.
    pin_count=0
    for j in range(n):
        values4=[M36[i][j]//3 for i in range(n)]
        assert all(M36[i][j]%3==0 for i in range(n))
        assert Counter(values4)==Counter({4:1,0:6,2:24,1:32})
        assert values4[j]==4
        assert all(
            sum(A[c][i]*values4[i] for i in range(n))==4
            for c in range(n)
        )
        for c in range(n):
            if A[c][j]:
                assert sorted(values4[i] for i in range(n) if A[c][i])==[0,0,4]
                pin_count+=1
    assert pin_count==189

    print("GLOBAL DEGREE-2 MOMENT ATTACK / E123: EXACT CHECK PASS")
    print("H symmetric, H^2=36 H, A H=0, H 1=0, trace H=504")
    print("C=H/36 is PSD orthogonal projector, rank=14")
    print("M=J/9+C has diag=1/3, local pair moments=0, A M=1 mu'")
    print("Unpinned Boolean/ExactOne degree-2 moment SDP = FEASIBLE")
    print("189 conditional first moments yield the exact earlier pinned LP vectors")
    print(f"E123 Boolean UNSAT independently: max F2 kernel weight {bad_top_weight}<42")
    verify_transpose_true_moments(A)
    print("Level-1 moment feasibility => Boolean SAT is FALSE")
    print("UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
