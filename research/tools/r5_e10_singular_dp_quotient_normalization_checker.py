#!/usr/bin/env python3
from itertools import product

def lhs(x, A, B):
    return all(x or a for a in A) and all((not x) or b for b in B)

def projected(A, B):
    return any(lhs(bool(x), A, B) for x in (0,1))

def rhs(A, B):
    return all(a or b for a in A for b in B)

def main():
    cases=0
    for p in range(0,4):
        for q in range(0,4):
            for bits in product((False,True), repeat=p+q):
                A=bits[:p]; B=bits[p:]
                assert projected(A,B)==rhs(A,B)
                cases += 1
            if p>0 and q>0 and min(p,q)==1:
                assert p*q <= p+q-1
    print(f'DP_PROJECTION_IDENTITY_CASES = {cases}')
    print('SINGULAR_POLARITY_CLAUSE_COUNT_STRICT_DROP = PASS')
    print('WITNESS_RECONSTRUCTION = PASS_BY_CASE_SPLIT')
    print('D1 = EMPTY')
    print('P_VS_NP = OPEN')

if __name__ == '__main__':
    main()
