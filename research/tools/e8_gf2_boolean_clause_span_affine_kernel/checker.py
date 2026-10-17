#!/usr/bin/env python3
from itertools import combinations, product


def monomials_le3(n):
    mons=[()]
    for d in (1,2,3):
        mons.extend(combinations(range(1,n+1),d))
    return mons


def clause_poly(C):
    # Polynomial as set of squarefree monomials with coefficient 1 over GF(2).
    poly={()}
    for lit in C:
        v=abs(lit)
        factor={(v,)} if lit<0 else {(),(v,)}
        new=set()
        for a in poly:
            for b in factor:
                m=tuple(sorted(set(a)|set(b)))
                if m in new:
                    new.remove(m)
                else:
                    new.add(m)
        poly=new
    return poly


def row_bits(poly,index):
    x=0
    for m in poly:
        x ^= 1<<index[m]
    return x


def span_basis(rows):
    piv={}
    combo={}
    for i,r0 in enumerate(rows):
        r=r0
        mask=1<<i
        while r:
            p=r.bit_length()-1
            if p not in piv:
                piv[p]=r
                combo[p]=mask
                break
            r ^= piv[p]
            mask ^= combo[p]
    return piv,combo


def express(target,piv,combo):
    r=target
    mask=0
    while r:
        p=r.bit_length()-1
        if p not in piv:
            return None
        r ^= piv[p]
        mask ^= combo[p]
    return mask


def xor3_clauses(vars_, rhs):
    out=[]
    for vals in product((0,1),repeat=3):
        if (sum(vals)&1)==rhs:
            continue
        C=[]
        for v,a in zip(vars_,vals):
            C.append(v if a==0 else -v)
        out.append(tuple(C))
    return out


def k4_tseitin():
    inc={0:(1,2,3),1:(1,4,5),2:(2,4,6),3:(3,5,6)}
    charge={0:1,1:0,2:0,3:0}
    F=[]; blocks=[]
    for v in range(4):
        block=xor3_clauses(inc[v],charge[v])
        blocks.append(block)
        F.extend(block)
    return F,blocks


def eval_formula(F,bits):
    return all(any(bits[abs(l)-1]==(l>0) for l in C) for C in F)


def main():
    n=6
    mons=monomials_le3(n)
    idx={m:i for i,m in enumerate(mons)}
    assert len(mons)==1+6+15+20

    T,blocks=k4_tseitin()
    rows=[row_bits(clause_poly(C),idx) for C in T]
    piv,comb=span_basis(rows)
    one=1<<idx[()]
    witness=express(one,piv,comb)
    assert witness is not None
    # For this control, XOR of all 16 clause rows is exactly 1.
    allmask=(1<<16)-1
    x=0
    for r in rows:
        x ^= r
    assert x==one

    # Each four-clause vertex block collapses to its affine parity equation.
    expected=[
        {():1,(1,):1,(2,):1,(3,):1},
        {(1,):1,(4,):1,(5,):1},
        {(2,):1,(4,):1,(6,):1},
        {(3,):1,(5,):1,(6,):1},
    ]
    for block,exp in zip(blocks,expected):
        z=0
        for C in block:
            z ^= row_bits(clause_poly(C),idx)
        assert z==row_bits(set(exp),idx)

    # Direct semantic UNSAT control.
    assert not any(eval_formula(T,bits) for bits in product((False,True),repeat=6))

    # SAT control: soundness forbids 1 in its span.
    S=[(1,2,5),(3,-4,-2),(3,-4,-5),(3,-4,-1)]
    rowsS=[row_bits(clause_poly(C),idx) for C in S]
    pivS,combS=span_basis(rowsS)
    assert express(one,pivS,combS) is None
    assert any(eval_formula(S,bits[:5]) for bits in product((False,True),repeat=6))

    print('PASS_GF2_BOOLEAN_CLAUSE_SPAN_AFFINE_KERNEL')
    print('ambient_degree_le3_dimension=',len(mons))
    print('K4_Tseitin_clause_rows=16 constant_one_in_span=True')
    print('K4_Tseitin_all16_xor_equals_one=True')
    print('SAT_control_constant_one_in_span=False')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
