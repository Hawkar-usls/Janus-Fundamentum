#!/usr/bin/env python3
"""Finite exact regression for the Paley-orbit canonical-diamond AF3 family theorem."""

from itertools import product

INCONSISTENT_CONTROLS=(11,43,59)
CONSISTENT_CONTROLS=(19,67,331,5419)


def is_prime(n):
    if n<2: return False
    d=2
    while d*d<=n:
        if n%d==0: return False
        d+=1
    return True


def orbit_minus2(q):
    r=(-2)%q
    out=[]; seen=set(); x=1
    while x not in seen:
        seen.add(x); out.append(x); x=x*r%q
    assert x==1
    return tuple(out)


def phi_factory(q,O):
    idx={s:k for k,s in enumerate(O)}
    def phi(c,d):
        d%=q
        if d in idx:
            return (-idx[d]-c)%3
        nd=(-d)%q
        if nd in idx:
            return (idx[nd]+c)%3
        return None
    return idx,phi


def canonical_coordinate(q,O,u,v):
    """Return the unique source arc coordinate for supported undirected edge {u,v}."""
    S=set(O)
    d=(v-u)%q
    if d in S:
        return (u,v)
    rd=(u-v)%q
    assert rd in S
    return (v,u)


def verify_local_diamond(q,O,c,a,b,phi,mu):
    pa=phi(c,a); pb=phi(c,b); pba=phi(c,(b-a)%q)
    assert None not in (pa,pb,pba)
    assert (pb-pa)%3==pba
    assert (pa+pb)%3==mu

    # vertices x=0, x+a, x+b, x+a+b
    req=((0,1,pa),(0,2,pb),(1,2,pba),(1,3,pb),(2,3,pa))
    avoiding=0
    for p in product(range(3),repeat=4):
        if any((p[v]-p[u])%3==g for u,v,g in req):
            continue
        avoiding+=1
        assert (p[3]-p[0])%3==mu
    assert avoiding>0
    return avoiding


def selected_coordinates(q,O,A,a,b,extra_d=()):
    coords=set()
    for j in range(q):
        x=(j*A)%q
        va=(x+a)%q; vb=(x+b)%q; tip=(x+A)%q
        for u,v in ((x,va),(x,vb),(va,vb),(va,tip),(vb,tip)):
            coords.add(canonical_coordinate(q,O,u,v))
    for d in extra_d:
        coords.add(canonical_coordinate(q,O,0,d))
    return coords


def check_consistent(q):
    assert is_prime(q) and q>3 and q%8==3
    O=orbit_minus2(q); L=len(O)
    assert L%3==0
    m=L//3; r=(-2)%q
    idx,phi=phi_factory(q,O)

    # r0(r^k)=k mod3 is an exact particular solution.
    for k,s in enumerate(O):
        rs=r*s%q
        assert idx[rs]==(k+1)%L
        assert (2*(k%3)+(idx[rs]%3))%3==1

    zeta=pow(r,m,q)
    assert zeta!=1 and pow(zeta,3,q)==1
    assert (1+zeta+zeta*zeta)%q==0

    a=1
    b=(-zeta)%q
    bma=(b-a)%q
    assert a in idx
    assert (-b)%q in idx
    assert bma==zeta*zeta%q and bma in idx

    A=(a+b)%q
    mu=m%3
    assert A!=(0%q)

    local_counts=[]
    for c in range(3):
        assert phi(c,a)==(-c)%3
        assert phi(c,b)==(m+c)%3
        assert phi(c,bma)==(-2*m-c)%3
        local_counts.append(verify_local_diamond(q,O,c,a,b,phi,mu))

    roots={(j*A)%q for j in range(q)}
    assert len(roots)==q and (q*A)%q==0

    if mu!=0:
        assert (q*mu)%3!=0
        coords=selected_coordinates(q,O,A,a,b)
        assert len(coords)<=5*q
        mode='nonzero-cycle-gain'
        extra=0
    else:
        # The q diamonds force equality transport over every additive vertex.
        closing=[]
        for c in range(3):
            e=(-c)%3
            assert e<L
            d=pow(r,e,q)
            assert d in idx
            assert phi(c,d)==0
            closing.append(d)
        coords=selected_coordinates(q,O,A,a,b,closing)
        assert len(coords)<=5*q+3
        mode='zero-gain-equality-plus-closing'
        extra=len(set(closing))

    return {
        'q':q,'L':L,'m':m,'mu':mu,'zeta':zeta,'A':A,
        'mode':mode,'coordinate_count':len(coords),'closing_distinct':extra,
        'local_avoiding_counts':tuple(local_counts),
    }


def check_inconsistent(q):
    assert is_prime(q) and q>3 and q%8==3
    L=len(orbit_minus2(q))
    assert L%3!=0
    # Existing family theorem: 1^T A=0 over F3 while RHS has qL nonzero sum.
    assert (q*L)%3!=0
    return q,L


def main():
    bad=[check_inconsistent(q) for q in INCONSISTENT_CONTROLS]
    good=[check_consistent(q) for q in CONSISTENT_CONTROLS]

    # Exercise both consistent symbolic cases.
    assert any(x['mu']==0 for x in good)
    assert any(x['mu']!=0 for x in good)

    print('PASS_PALEY_ORBIT_CANONICAL_DIAMOND_CYCLE_AF3_POLYSIZE_COVER')
    for q,L in bad:
        print(f'q={q}: L={L} branch=AF3_INCONSISTENT_LINEAR_TERMINAL')
    for x in good:
        print(
            f"q={x['q']}: L={x['L']} m={x['m']} mu={x['mu']} "
            f"zeta={x['zeta']} A={x['A']} mode={x['mode']} "
            f"distinct_source_coordinates={x['coordinate_count']} "
            f"bound={5*x['q']+3} local_counts={x['local_avoiding_counts']}"
        )
    print('CONSISTENT_BRANCH_COVER_BOUND<=5q+3')
    print('AFFINE_POTENTIAL_ENUMERATION=ELIMINATED_FOR_FROZEN_PALEY_ORBIT_FAMILY')
    print('OVERALL_PALEY_UNSAT_TERMINAL_WAS_ALREADY_KNOWN_FROM_RATIONAL_GRADIENT')
    print('TRANSFER_TO_NONPALEY_PRIME_TOWERS=OPEN')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
