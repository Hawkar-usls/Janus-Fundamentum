#!/usr/bin/env python3
"""Exact regression for the rank-3 switch real-stability barrier."""

from fractions import Fraction


def rayleigh_delta_lr(a,b,c,d,e,M):
    # f=a+bL+cM+dR+eLR
    # Delta_LR=(d_L f)(d_R f)-f(d_LR f)=bd-ea-ec M
    return b*d - e*a - e*c*M


def canonical_p(L,M,R):
    return 1 + L + M + R + L*R


def main():
    # Symbolic coefficient check via several exact rational samples.
    a,b,c,d,e = map(Fraction, (2,3,5,7,11))
    vals = [rayleigh_delta_lr(a,b,c,d,e,Fraction(t)) for t in (-100,0,100)]
    assert vals[0] > 0 and vals[-1] < 0
    assert vals[1] == b*d-e*a

    # Canonical explicit upper-half-plane zero: L=R=-2+i, M=2i.
    L = complex(-2,1)
    R = complex(-2,1)
    M = complex(0,2)
    z = canonical_p(L,M,R)
    assert L.imag > 0 and R.imag > 0 and M.imag > 0
    assert abs(z) < 1e-12

    # Frozen five-state support is the known non-delta relation.
    F = {frozenset(), frozenset({'L'}), frozenset({'M'}), frozenset({'R'}), frozenset({'L','R'})}
    X=frozenset({'L','R'}); Y=frozenset({'M'}); u='M'
    sym = X ^ Y
    candidates=[]
    for v in sym:
        T=set(X)
        T.symmetric_difference_update({u} if v==u else {u,v})
        candidates.append(frozenset(T))
    assert all(T not in F for T in candidates)

    print('PASS_RANK3_SWITCH_REAL_STABILITY_BARRIER')
    print('Delta_LR=bd-ea-ec*M has nonzero M slope when c,e!=0')
    print('canonical_upper_half_plane_zero=True')
    print('five_state_support_delta_matroid=False')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
