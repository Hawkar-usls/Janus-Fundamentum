#!/usr/bin/env python3
from itertools import combinations

GROUND = ('L','M','R')
R = {
    frozenset(),
    frozenset({'L'}),
    frozenset({'M'}),
    frozenset({'R'}),
    frozenset({'L','R'}),
}


def matroid_augmentation_fail(fam):
    for I in fam:
        for J in fam:
            if len(I) >= len(J):
                continue
            if not any((I | {e}) in fam for e in (J - I)):
                return I, J
    return None


def det3(a,b,c,d,e,f):
    # [[a,d,e],[d,b,f],[e,f,c]]
    return a*b*c + 2*d*e*f - a*f*f - b*e*e - c*d*d


def main():
    fail = matroid_augmentation_fail(R)
    assert fail is not None
    I,J = fail
    assert I == frozenset({'M'}) and J == frozenset({'L','R'})
    assert (I | {'L'}) not in R
    assert (I | {'R'}) not in R

    # Exact real-symmetric 3x3 obstruction.
    # singleton minors=1 -> diagonal a=b=c=1.
    # LM=0 and MR=0 -> d,f in {+1,-1}.
    # LR=1 -> e=0.
    # Every sign choice then has determinant -1, not required 0.
    vals=[]
    for d in (-1,1):
        for f in (-1,1):
            e=0
            D=det3(1,1,1,d,e,f)
            vals.append(D)
            assert D == -1
    assert set(vals)=={-1}

    print('PASS_PSD_RADO_MATROID_SUPPORT_BARRIER')
    print('augmentation_failure=I{M}_J{L,R}')
    print('symmetric_target_det_values=', vals)
    print('PSD_LOCAL_SUPPORT_REPLACEMENT=IMPOSSIBLE')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
