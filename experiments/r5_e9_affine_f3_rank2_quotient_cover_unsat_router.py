#!/usr/bin/env python3
"""Exact F3 regression for the rank-2 quotient-cover UNSAT router.

The symbolic theorem proves soundness for arbitrary row-weight-three sources.
This finite checker verifies strictness over the rank-1 terminal on the frozen
pair2 EQ3-regularized connected linear-cubic UNSAT control, and rejection on
three hostile SAT controls. No floating point or SAT/ILP library is used.
"""

from itertools import combinations, product

P = [7,6,4,2,0,1,8,5,3]
Q = [6,8,7,0,5,2,1,3,4]
GADGET = [
    (2,5,6),(1,4,7),(5,7,9),
    (0,3,7),(4,6,9),(2,4,8),
    (3,8,9),(0,5,8),(1,3,6),
]

PG15_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

SAT18_ROWS = [
    (0,15,17),(1,4,12),(2,10,14),(3,4,11),(4,8,9),(3,5,13),
    (1,6,10),(2,7,15),(1,8,14),(3,7,9),(9,10,16),(7,11,13),
    (5,12,17),(0,13,16),(0,12,14),(5,8,15),(2,6,16),(6,11,17),
]


def source9():
    rows=[]
    for i in range(9):
        row=tuple(sorted({i,P[i],Q[i]}))
        assert len(row)==3
        rows.append(row)
    return rows


def pair2_regularized_rows():
    src=source9()
    rows=[]
    for v in range(9):
        off=10*v
        for row in GADGET:
            rows.append(tuple(off+j for j in row))
    occ=[0]*9
    for row in src:
        out=[]
        for v in row:
            out.append(10*v+occ[v])
            occ[v]+=1
        rows.append(tuple(out))
    assert occ==[3]*9
    return rows


def matrix_from_rows(rows,n,one_based=False):
    A=[[0]*n for _ in rows]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j-1 if one_based else j]=1
    return A


def lift(A,pair):
    n=len(A)
    E=[[0]*n for _ in range(n)]
    for i,j in pair:
        assert A[i][j]==1
        E[i][j]=1
    R=[[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    return [R[i]+E[i] for i in range(n)] + [E[i]+R[i] for i in range(n)]


def check_cubic_linear_connected(rows,n):
    assert len(rows)==n
    assert all(len(r)==3 and len(set(r))==3 for r in rows)
    degree=[0]*n
    for row in rows:
        for j in row: degree[j]+=1
    assert degree==[3]*n
    sets=[set(r) for r in rows]
    assert all(len(sets[i]&sets[j])<=1 for i in range(n) for j in range(i))
    adj=[[] for _ in range(2*n)]
    for i,row in enumerate(rows):
        for j in row:
            adj[i].append(n+j); adj[n+j].append(i)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    assert len(seen)==2*n


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
        return None,None
    free=[j for j in range(n) if j not in piv]
    r0=[0]*n
    for i,c in enumerate(piv): r0[c]=M[i][n]
    basis=[]
    for f in free:
        v=[0]*n; v[f]=1
        for i,c in enumerate(piv): v[c]=(-M[i][f])%p
        basis.append(v)
    B=[[basis[t][i] for t in range(len(basis))] for i in range(n)]
    return r0,B


def normalize(row,r0i):
    first=next((x%3 for x in row if x%3),None)
    if first is None: return None
    inv=pow(first,-1,3)
    return tuple((inv*x)%3 for x in row),(-inv*r0i)%3


def coeff_in_span(c,u,v):
    for a in range(3):
        for b in range(3):
            if all((a*u[j]+b*v[j]-c[j])%3==0 for j in range(len(c))):
                return a,b
    return None


def analyze(A):
    r0,B=affine_parameterization(A)
    if r0 is None:
        return {'inconsistent':True,'router':'rank0-inconsistent'}
    d=len(B[0]) if B and B[0] else 0
    unique={}
    for i,row in enumerate(B):
        z=normalize(row,r0[i])
        if z is None:
            if r0[i]==0:
                return {'inconsistent':False,'d':d,'router':'rank0-identically-zero'}
            continue
        c,t=z
        unique.setdefault((c,t),[]).append(i)
    classes={}
    for (c,t),ids in unique.items():
        classes.setdefault(c,set()).add(t)
    rank1=[c for c,off in classes.items() if off=={0,1,2}]
    if rank1:
        return {'inconsistent':False,'d':d,'router':'rank1','classes':classes,'unique':unique}

    normals=sorted(classes)
    for u,v in combinations(normals,2):
        lines=[]
        for (c,t),ids in unique.items():
            ab=coeff_in_span(c,u,v)
            if ab is not None:
                lines.append((ab,t,(c,t),ids))
        if all(any((ab[0]*x+ab[1]*y-t)%3==0 for ab,t,_,_ in lines)
               for x,y in product(range(3),repeat=2)):
            return {
                'inconsistent':False,'d':d,'router':'rank2',
                'classes':classes,'unique':unique,
                'u':u,'v':v,'lines':lines,
            }
    return {'inconsistent':False,'d':d,'router':'none','classes':classes,'unique':unique}


def exactone_source9_unsat():
    rows=source9()
    for bits in product((0,1),repeat=9):
        if all(sum(bits[j] for j in row)==1 for row in rows):
            return False
    return True


def gadget_terminal_states():
    states=set()
    count=0
    for bits in product((0,1),repeat=10):
        if all(sum(bits[j] for j in row)==1 for row in GADGET):
            count+=1
            states.add(bits[:3])
    return count,states


def minimum_induced_cover_size(lines):
    # Deduplicate quotient equations only.
    eq=sorted(set((ab,t) for ab,t,_,_ in lines))
    pts=list(product(range(3),repeat=2))
    def covers(sel):
        return all(any((eq[i][0][0]*x+eq[i][0][1]*y-eq[i][1])%3==0 for i in sel)
                   for x,y in pts)
    for k in range(1,len(eq)+1):
        for C in combinations(range(len(eq)),k):
            if covers(C): return k,C,eq
    return None,None,eq


def main():
    # Strict connected linear-cubic UNSAT control from the frozen pair2 regularizer.
    rows90=pair2_regularized_rows()
    check_cubic_linear_connected(rows90,90)
    assert exactone_source9_unsat()
    count,states=gadget_terminal_states()
    assert count==3
    assert states=={(0,0,0),(1,1,1)}
    # Therefore any Boolean witness of the 90-carrier would collapse to a witness
    # of the n=9 source; exact local terminal equality proves UNSAT.

    A90=matrix_from_rows(rows90,90)
    info=analyze(A90)
    assert info['d']==11
    assert info['router']=='rank2'
    assert len(info['classes'])==21
    assert max(len(x) for x in info['classes'].values())==2
    assert all(x!={0,1,2} for x in info['classes'].values())
    assert len(info['unique'])==24

    k,C,eq=minimum_induced_cover_size(info['lines'])
    assert k==5
    assert len(set((ab,t) for ab,t,_,_ in info['lines']))==6

    # SAT hostile controls must reject the UNSAT router.
    pg15=matrix_from_rows(PG15_ROWS,15,one_based=True)
    sat18=matrix_from_rows(SAT18_ROWS,18)
    sat36=lift(sat18,((0,15),(1,1)))
    for name,A,expected_d in (
        ('PG15',pg15,4),('UNIQUE18',sat18,2),('UNIQUE36',sat36,3)
    ):
        out=analyze(A)
        assert out['d']==expected_d
        assert out['router']=='none', (name,out['router'])

    print('PASS_AFFINE_F3_RANK2_QUOTIENT_COVER_UNSAT_ROUTER')
    print('pair2_regularized: n=90 d3=11 unique_hyperplanes=24 projective_classes=21')
    print('rank1_full_parallel_classes=0')
    print('rank2_induced_lines=6 minimum_cover_size=5')
    print('SAT controls rejected: PG15, UNIQUE18, UNIQUE36')
    print('rank1 completeness: FALSIFIED')
    print('rank<=2 completeness: OPEN')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
