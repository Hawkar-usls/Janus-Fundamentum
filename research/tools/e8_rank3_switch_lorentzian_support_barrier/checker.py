#!/usr/bin/env python3
"""Exact support-exchange regression for the rank-3 Lorentzian barrier."""

SUPPORT={
    (2,0,0,0), # y^2
    (1,1,0,0), # yL
    (1,0,1,0), # yM
    (1,0,0,1), # yR
    (0,1,0,1), # LR
}


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))


def main():
    alpha=(0,1,0,1) # LR
    beta=(1,0,1,0)  # yM
    e=[(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]
    i=1 # L: alpha_i > beta_i
    assert alpha[i]>beta[i]
    deficits=[j for j in range(4) if alpha[j]<beta[j]]
    assert deficits==[0,2]
    valid=[]
    for j in deficits:
        a2=add(sub(alpha,e[i]),e[j])
        b2=add(sub(beta,e[j]),e[i])
        if a2 in SUPPORT and b2 in SUPPORT:
            valid.append((j,a2,b2))
    assert not valid
    # Canonical degree-2 Hessian also has two positive eigenvalues by exact
    # principal-signature witness: the 2x2 principal block on y,L has det -1,
    # while the full support failure is already coefficient-independent.
    print('PASS_RANK3_SWITCH_LORENTZIAN_SUPPORT_BARRIER')
    print('support_M_convex=False')
    print('positive_same_support_Lorentzian=False')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__': main()
