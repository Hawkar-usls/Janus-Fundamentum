#!/usr/bin/env python3
"""Exact regression for the parity-group exterior all-or-none projection."""
from itertools import product


def eval_formula(formula, assignment):
    return all(any((assignment[abs(l)] if l>0 else 1-assignment[abs(l)]) for l in C) for C in formula)


def brute_sat_count(formula):
    vs=sorted({abs(l) for C in formula for l in C})
    ans=0
    for bits in product((0,1), repeat=len(vs)):
        ans += int(eval_formula(formula,dict(zip(vs,bits))))
    return ans


def build_occurrence_rank1(formula):
    m=len(formula); q=3*m; dim=3*m
    M0=[[0]*dim for _ in range(dim)]
    U=[[0]*dim for _ in range(q)]
    V=[[0]*dim for _ in range(q)]
    groups={}; occ=0
    for cidx,clause in enumerate(formula):
        assert len(clause)==3
        base=3*cidx
        for d in range(3): M0[base+d][base+d]=1
        coords=[(base,base+1,+1),(base+1,base+2,+1),(base+2,base,-1)]
        for pos,lit in enumerate(clause):
            row,col,cs=coords[pos]; var=abs(lit)
            groups.setdefault(var,[]).append(occ)
            if lit>0:
                M0[row][col]+=cs; coeff=-cs
            else:
                coeff=cs
            U[occ][row]=coeff; V[occ][col]=1; occ+=1
    return M0,U,V,groups


def wedge_vec(form,vec):
    out={}
    for mask,c in form.items():
        for j,v in enumerate(vec):
            if not v or ((mask>>j)&1): continue
            inv=(mask>>(j+1)).bit_count()
            nm=mask|(1<<j)
            out[nm]=out.get(nm,0)+((-1 if inv&1 else 1)*c*v)
    return {k:v for k,v in out.items() if v}


def wedge_rows(rows):
    f={0:1}
    for r in rows: f=wedge_vec(f,r)
    return f


def wedge_forms(A,B):
    out={}
    for ma,ca in A.items():
        for mb,cb in B.items():
            if ma&mb: continue
            inv=0; x=mb
            while x:
                bit=x & -x; j=bit.bit_length()-1
                inv += (ma>>(j+1)).bit_count(); x-=bit
            nm=ma|mb
            out[nm]=out.get(nm,0)+((-1 if inv&1 else 1)*ca*cb)
    return {k:v for k,v in out.items() if v}


def add_forms(A,B):
    C=dict(A)
    for k,v in B.items(): C[k]=C.get(k,0)+v
    return {k:v for k,v in C.items() if v}


def perm_sign(seq):
    inv=sum(seq[i]>seq[j] for i in range(len(seq)) for j in range(i+1,len(seq)))
    return -1 if inv&1 else 1


def exterior_count(formula):
    M0,U,V,groups=build_occurrence_rank1(formula)
    m0=len(M0); q=len(U); N=m0+q
    # Ordered fixed rows of [M0 | U^T].
    fixed=[]
    for i in range(m0): fixed.append(M0[i][:]+[U[o][i] for o in range(q)])
    f=wedge_rows(fixed)
    grouped=[]
    for var in sorted(groups):
        occs=groups[var]; grouped.extend(occs)
        arows=[]; brows=[]
        for o in occs:
            a=[0]*N; a[m0+o]=1
            b=[0]*N
            for j in range(m0): b[j]=-V[o][j]
            b[m0+o]=1
            arows.append(a); brows.append(b)
        local=add_forms(wedge_rows(arows),wedge_rows(brows))
        f=wedge_forms(f,local)
    eps=perm_sign(grouped)
    top=f.get((1<<N)-1,0)
    return eps*top, top, eps


def local_character_check(d):
    # Work in formal subset basis: selecting b positions gives character prod t_j.
    coeff={S:0 for S in range(1<<d)}
    signs=[]
    for t in product((1,-1), repeat=d):
        if d>1 and __import__('math').prod(t)!=1: continue
        if d==1 and t!=(1,): continue
        signs.append(t)
        for S in range(1<<d):
            val=1
            for j in range(d):
                if (S>>j)&1: val*=t[j]
            coeff[S]+=val
    if d==1:
        assert coeff=={0:1,1:1}
    else:
        target=2**(d-1)
        for S,v in coeff.items():
            assert v==(target if S in (0,(1<<d)-1) else 0),(d,S,v)


def main():
    for d in (1,2,3): local_character_check(d)
    formulas=[
        [(1,2,3)],
        [(1,2,3),(-1,2,-3)],
        [(1,1,2),(-1,2,3)],
        [(1,-2,3),(1,2,4),(-2,3,4)],
    ]
    for F in formulas:
        got,raw,eps=exterior_count(F); expected=brute_sat_count(F)
        assert got==expected,(F,got,expected,raw,eps)
        print('formula_clauses=',len(F),'#SAT=',expected,'raw_top=',raw,'epsilon=',eps)
    print('PASS_PARITY_GROUP_EXTERIOR_ALL_OR_NONE_PROJECTION')
    print('LOCAL_EVEN_FOURIER_GROUPS_COLLAPSE_TO_TWO_WEDGE_STATES=True')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__=='__main__': main()
