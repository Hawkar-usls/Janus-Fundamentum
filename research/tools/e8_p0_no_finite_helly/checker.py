#!/usr/bin/env python3
"""Exact finite regressions for the infinite no-Helly P0 coefficient family."""

from itertools import product, combinations


def family(n):
    a=n+1; b=n+2
    F=[(1,a),(1,-a)]
    F += [(-i,i+1) for i in range(1,n)]
    F += [(-n,b),(-n,-b)]
    return F


def satisfiable(F):
    vs=sorted({abs(l) for c in F for l in c})
    for bits in product((0,1), repeat=len(vs)):
        A=dict(zip(vs,bits))
        if all(any(A[abs(l)] if l>0 else 1-A[abs(l)] for l in c) for c in F):
            return True
    return False


def sign_consistent_transversal_count(F):
    # Exactly one witness occurrence per clause; selected signs of each variable must agree.
    total=0
    for choice in product(*[range(len(c)) for c in F]):
        signs={}
        ok=True
        for ci,pos in enumerate(choice):
            lit=F[ci][pos]; v=abs(lit); s=1 if lit>0 else -1
            if v in signs and signs[v]!=s:
                ok=False; break
            signs[v]=s
        total += int(ok)
    return total


def main():
    for n in range(2,8):
        F=family(n)
        assert not satisfiable(F)
        assert sign_consistent_transversal_count(F)==0
        # Minimal UNSAT: every single deletion is SAT and has positive target coefficient.
        for i in range(len(F)):
            G=F[:i]+F[i+1:]
            assert satisfiable(G)
            assert sign_consistent_transversal_count(G)>0
        # Stronger finite replay: every proper subset is SAT/positive for n<=5.
        if n<=5:
            m=len(F)
            for r in range(m):
                for I in combinations(range(m),r):
                    G=[F[i] for i in I]
                    assert satisfiable(G)
                    assert sign_consistent_transversal_count(G)>0
        print(f'n={n} clauses={len(F)} full_W=0 every_single_deletion_W>0 PASS')
    print('PASS_P0_NO_FINITE_HELLY_COEFFICIENT_POSITIVITY')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
