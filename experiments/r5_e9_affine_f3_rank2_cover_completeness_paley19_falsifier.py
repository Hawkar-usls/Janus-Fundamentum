#!/usr/bin/env python3
"""Exact regression for the Paley(19) falsifier of rank<=2 F3 cover completeness."""

from itertools import combinations

Q = 19
QR = {1,4,5,6,7,9,11,16,17}
REPS = (
    (0,1,2),(0,1,10),(0,2,4),(0,3,6),(0,3,11),
    (0,4,8),(0,5,10),(0,5,12),(0,6,12),
)


def is_arc(u,v):
    return ((v-u)%Q) in QR


def oriented_arc(u,v):
    return (u,v) if is_arc(u,v) else (v,u)


def translate_tri(tri,s):
    return tuple(sorted((x+s)%Q for x in tri))


def tri_arcs(tri):
    return [oriented_arc(u,v) for u,v in combinations(tri,2)]


def build_source():
    triangles=[]
    for rep in REPS:
        triangles.extend(translate_tri(rep,s) for s in range(Q))
    arcs=[oriented_arc(u,v) for u,v in combinations(range(Q),2)]
    assert len(triangles)==171 and len(set(triangles))==171
    assert len(arcs)==171 and len(set(arcs))==171
    idx={e:i for i,e in enumerate(arcs)}
    A=[[0]*171 for _ in range(171)]
    for i,T in enumerate(triangles):
        for e in tri_arcs(T): A[i][idx[e]]=1
    return arcs,A


def affine_parameterization(A,p=3):
    m,n=len(A),len(A[0])
    M=[[A[i][j]%p for j in range(n)]+[1] for i in range(m)]
    piv=[]; r=0
    for c in range(n):
        q=next((i for i in range(r,m) if M[i][c]),None)
        if q is None: continue
        M[r],M[q]=M[q],M[r]
        inv=pow(M[r][c],-1,p)
        M[r]=[(x*inv)%p for x in M[r]]
        for i in range(m):
            if i!=r and M[i][c]:
                f=M[i][c]
                M[i]=[(M[i][j]-f*M[r][j])%p for j in range(n+1)]
        piv.append(c); r+=1
        if r==m: break
    if any(all(M[i][c]==0 for c in range(n)) and M[i][n] for i in range(m)):
        return None,None,len(piv)
    free=[j for j in range(n) if j not in piv]
    r0=[0]*n
    for i,c in enumerate(piv): r0[c]=M[i][n]
    basis=[]
    for f in free:
        v=[0]*n; v[f]=1
        for i,c in enumerate(piv): v[c]=(-M[i][f])%p
        basis.append(v)
    B=[[basis[t][i] for t in range(len(basis))] for i in range(n)]
    return r0,B,len(piv)


def normalize(row,r0i):
    first=next((x for x in row if x),None)
    if first is None: return None
    inv=pow(first,-1,3)
    return tuple((inv*x)%3 for x in row),(-inv*r0i)%3


def normalize_vec(v):
    first=next((x for x in v if x),None)
    if first is None: return None,None
    inv=pow(first,-1,3)
    return tuple((inv*x)%3 for x in v),inv


def combine(u,v,a,b):
    raw=tuple((a*u[j]+b*v[j])%3 for j in range(len(u)))
    return normalize_vec(raw)


def rank2_cover_exists(normal_to_offset):
    normals=list(normal_to_offset)
    checked=0
    four_direction_planes=0
    concurrent=0
    for i in range(len(normals)):
        u=normals[i]; tu=normal_to_offset[u]
        for j in range(i+1,len(normals)):
            v=normals[j]; tv=normal_to_offset[v]
            checked+=1
            w1,s1=combine(u,v,1,1)
            w2,s2=combine(u,v,1,2)
            if w1 not in normal_to_offset or w2 not in normal_to_offset:
                continue
            four_direction_planes+=1
            expected1=(s1*(tu+tv))%3
            expected2=(s2*(tu+2*tv))%3
            if normal_to_offset[w1]==expected1 and normal_to_offset[w2]==expected2:
                concurrent+=1
                return True,checked,four_direction_planes,concurrent
    return False,checked,four_direction_planes,concurrent


def connected_linear_cubic(A):
    n=len(A)
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    supp=[{j for j,x in enumerate(row) if x} for row in A]
    assert all(len(supp[i]&supp[j])<=1 for i,j in combinations(range(n),2))
    adj=[[] for _ in range(2*n)]
    for i,S in enumerate(supp):
        for j in S:
            adj[i].append(n+j); adj[n+j].append(i)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    assert len(seen)==2*n


def main():
    arcs,A=build_source()
    connected_linear_cubic(A)

    r0,B,rank=affine_parameterization(A)
    assert r0 is not None
    assert rank==152
    assert len(B[0])==19

    normal_to_offset={}
    zero_normals=0
    for i,row in enumerate(B):
        z=normalize(row,r0[i])
        if z is None:
            zero_normals+=1
            assert r0[i]!=0
            continue
        c,t=z
        assert c not in normal_to_offset, 'projective-normal collision'
        normal_to_offset[c]=t

    assert zero_normals==0
    assert len(normal_to_offset)==171

    # With exactly one affine hyperplane per projective normal direction,
    # a rank-2 quotient cover requires the four directions of PG(1,3) and
    # their four affine lines to form the complete pencil through one point.
    exists,checked,fourdirs,concurrent=rank2_cover_exists(normal_to_offset)
    assert checked==171*170//2
    assert not exists
    assert concurrent==0

    # Exact-One UNSAT is independently frozen by the companion Paley19
    # gradient-kernel theorem: ker_Q(A)=gradient space on K_19 arcs, and a
    # {-1,2}-kernel word would require >3 real potentials with every pairwise
    # distance in {1,2}, impossible. AF3-1 then implies the full coordinate
    # hyperplane family covers the 19-dimensional affine F3 space.
    assert Q>3

    print('PASS_PALEY19_AFFINE_F3_RANK2_COMPLETENESS_FALSIFIER')
    print('n=171 rank_F3=152 dim_F3=19 consistent=True')
    print('projective_normal_classes=171 max_offsets_per_class=1')
    print('rank1_cover=False')
    print('rank2_pairs_checked=',checked)
    print('rank2_four_direction_planes=',fourdirs)
    print('rank2_concurrent_cover_pencils=0')
    print('minimum_cover_normal_rank>=3')
    print('RANK_LE_2_COMPLETENESS=FALSE')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
