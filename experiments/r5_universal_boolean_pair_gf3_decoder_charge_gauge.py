#!/usr/bin/env python3
"""Exact GF3 native source-PC equality decoder and signed-charge no-go.

Two distinct source edge indicator triples p=(p0,p1,p2), q=(q0,q1,q2)
each satisfy E_p=sum p-1, E_q=sum q-1 and original Boolean B_z=z^2-z.
T=sum_c p_c q_c is the Boolean predicate [edge colours equal].
We verify a LITERAL polynomial identity proving T^2-T in the ideal
at total degree <=4, with no truth-table-only inference.

A global equality-bit wire between two C6 gate incidences cannot be
one-sided 'inverted' by semantic relabelling: edge signs must match
both endpoints, making total Tseitin charge parity 0 for any cubic H.
"""
from itertools import combinations
from collections import Counter

MOD=3
ZERO=(0,)*6


def normalize(poly):
    return {m:c%MOD for m,c in poly.items() if c%MOD}


def const(x):
    return normalize({ZERO:x})


def variable(i):
    m=[0]*6
    m[i]=1
    return {tuple(m):1}


def add(*polys):
    out={}
    for p in polys:
        for m,c in p.items():
            out[m]=(out.get(m,0)+c)%MOD
    return normalize(out)


def neg(p):
    return scale(p,-1)


def scale(p,k):
    return normalize({m:c*k for m,c in p.items()})


def sub(p,q):
    return add(p,neg(q))


def mul(p,q):
    out={}
    for a,x in p.items():
        for b,y in q.items():
            m=tuple(z+w for z,w in zip(a,b))
            out[m]=(out.get(m,0)+x*y)%MOD
    return normalize(out)


def degree(p):
    return max((sum(m) for m in p),default=-1)


def verify_decoder_identity():
    p=[variable(i) for i in range(3)]
    q=[variable(3+i) for i in range(3)]
    Bp=[sub(mul(x,x),x) for x in p]
    Bq=[sub(mul(x,x),x) for x in q]
    Ep=sub(add(*p),const(1))
    T=add(*(mul(p[i],q[i]) for i in range(3)))
    assert degree(T)==2
    lhs=sub(mul(T,T),T)
    rhs=const(0)
    for i in range(3):
        rhs=add(rhs,mul(Bp[i],mul(q[i],q[i])),mul(p[i],Bq[i]))
    for i,j in combinations(range(3),2):
        k=next(c for c in range(3) if c!=i and c!=j)
        R=add(mul(sub(add(p[i],p[j]),p[k]),Ep),
              neg(Bp[i]),neg(Bp[j]),Bp[k])
        # R=2*p_i*p_j, exact polynomial identity.
        assert sub(R,scale(mul(p[i],p[j]),2))=={}
        rhs=add(rhs,mul(R,mul(q[i],q[j])))
    assert lhs==rhs,sub(lhs,rhs)
    assert degree(rhs)==4
    for i,j in combinations(range(3),2):
        k=next(c for c in range(3) if c!=i and c!=j)
        assert scale(mul(p[i],p[j]),2)==add(
            mul(sub(add(p[i],p[j]),p[k]),Ep),
            neg(Bp[i]),neg(Bp[j]),Bp[k])
    print("GF3_BIT_DECODER: T=sum_c p_c q_c has degree 2;")
    print("  T^2-T exact original edge-row/Boolean identity degree <=4 PASS")
    print("  pairwise one-hot exclusivity exact source degree <=2 PASS")


def test_charge_gauge(name,n,edges):
    edges=tuple(tuple(sorted(e)) for e in edges)
    assert len(edges)==3*n//2 and len(edges)==len(set(edges))
    inc=[tuple(i for i,e in enumerate(edges) if v in e) for v in range(n)]
    assert all(len(v)==3 for v in inc)
    for mask in range(1<<len(edges)):
        s=tuple((mask>>i)&1 for i in range(len(edges)))
        effective_charge=tuple(1^s[a]^s[b]^s[c] for a,b,c in inc)
        assert sum(effective_charge)%2==n%2
        # The physical all-equal T=1 state is always a satisfying bit
        # assignment for every native odd-C6 gate (1 xor1 xor1=1).
        assert all((1^s[a])^(1^s[b])^(1^s[c])==effective_charge[v]
                   for v,(a,b,c) in enumerate(inc))
    print(f"GAUGE_{name}: all {1<<len(edges)} coherent edge signs checked;")
    print("  global XOR charge EVEN and universal bit witness PASS")


def main():
    verify_decoder_identity()
    k4=[(i,j) for i in range(4) for j in range(i+1,4)]
    k33=[(i,j) for i in range(3) for j in range(3,6)]
    p=[]
    for i in range(5):
        p += [(i,(i+1)%5),(i,5+i),(5+i,5+(i+2)%5)]
    test_charge_gauge("K4",4,k4)
    test_charge_gauge("K33",6,k33)
    test_charge_gauge("PETERSEN",10,p)
    print("SIGNED_LOCAL_RELABEL_ONLY: does not implement physical one-end inversion")
    print("HARD_TSEITIN_IMPORT=OPEN; UNBOUNDED_NATIVE_PC_DEGREE=OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
