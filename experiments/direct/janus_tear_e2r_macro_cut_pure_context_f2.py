#!/usr/bin/env python3
"""Pure-Resolution overlap replay for C025-E2R-L1G-F2 v1.1."""
Clause=frozenset[int]

def resolve(a:Clause,b:Clause,p:int):
    if p in a and -p in b:
        r=frozenset((a-{p})|(b-{-p}))
    elif -p in a and p in b:
        r=frozenset((a-{-p})|(b-{p}))
    else:
        return None
    return None if any(-x in r for x in r) else r

def restrict_clause(c:Clause,rho:dict[int,bool]):
    out=set()
    for lit in c:
        v=abs(lit)
        if v not in rho:
            out.add(lit); continue
        if (rho[v] if lit>0 else not rho[v]):
            return None
    return frozenset(out)

def main():
    # Context C={2,3} overlaps proof variable 2.
    gamma_c=frozenset({1,2,3})
    d1=frozenset({-1,2})
    d2=frozenset({-2})

    r1=resolve(d1,d2,2)
    assert r1==frozenset({-1})
    r2=resolve(gamma_c,r1,1)
    assert r2==frozenset({2,3})
    r3=resolve(r2,d2,2)
    assert r3==frozenset({3})
    assert r3 <= frozenset({2,3})

    # Restrict by assignment falsifying C: 2=False, 3=False.
    rho={2:False,3:False}
    assert restrict_clause(gamma_c,rho)==frozenset({1})
    assert restrict_clause(d1,rho)==frozenset({-1})
    assert restrict_clause(d2,rho) is None
    assert resolve(frozenset({1}),frozenset({-1}),1)==frozenset()

    print('C025_E2R_L1G_F2_PURE_RESTRICTION_CONTEXT_OVERLAP = PASS')
    print('C025_E2R_L1G_F2_PURE_CONTEXT_SUBCLAUSE_DERIVATION = PASS')
    print('claim_boundary = finite pure-Resolution context-lift mechanics only')

if __name__=='__main__':
    main()
