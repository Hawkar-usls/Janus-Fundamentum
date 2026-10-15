#!/usr/bin/env python3
"""Exact rational ANCHORED_MOMENT_LP with independent primal/dual witnesses.

Known exact masses w_t at select violation counts t are removed from
both raw moment RHS and primal support. Solve the resulting LP:
  max w_0,  sum_{t unanchored} binom(t,j)*w_t
     = N_j - sum_{a anchored} mass_a*binom(a,j), w_t>=0.
The dual polynomial must dominate 1[t=0] ONLY on unanchored t;
mass at anchored t is already known and is never relaxed.
Every certificate is checked without trusting optimizer output.

For legal SCL, anchors include w_n(C)=1 iff all-one state belongs
to C; w_(n-3)=0, w_(n-6)=A4(C), w_(n-9)=A6(C).
All exact rational arithmetic uses Python Fraction.
"""
from fractions import Fraction as Q
from math import comb
import argparse,json

from r5_optimal_moment_lp_20261015 import simplex


def anchored_optimal_lp(n,raw,k,anchors):
    if n%3 or not 0<=k<=5 or len(raw)<k+1:
        raise ValueError("invalid source dimensions or fixed degree")
    if any(t%3 or t<0 or t>n or int(m)!=m or m<0
           for t,m in anchors.items()):
        raise ValueError("anchors must be exact nonnegative integer masses")
    all_t=list(range(0,n+1,3))
    unanchored=[t for t in all_t if t not in anchors]
    m=k+1
    size=len(unanchored)
    if size<m:
        raise ValueError("too few unanchored support points for this rank")
    residual=[
        Q(raw[j])-sum(Q(count)*comb(t,j) for t,count in anchors.items())
        for j in range(m)
    ]
    if any(b<0 for b in residual):
        raise ValueError("anchors inconsistent with supplied moments")
    tab=[
        [Q(comb(t,j)) for t in unanchored] +
        [Q(int(i==j)) for i in range(m)] + [residual[j]]
        for j in range(m)
    ]
    basis=list(range(size,size+m))
    obj1,i1=simplex(tab,basis,[Q(0)]*size+[-Q(1)]*m)
    if obj1!=0:
        raise ValueError("anchors not consistent with any support distribution")
    # Remove zero artificial basic variables exactly as source LP.
    for i in range(m):
        if basis[i]<size:
            continue
        occupied=set(basis)
        incoming=next((j for j in range(size)
                       if j not in occupied and tab[i][j]!=0),None)
        if incoming is None or tab[i][-1]!=0:
            raise AssertionError("artificial basic cannot be eliminated")
        factor=tab[i][incoming]
        tab[i]=[v/factor for v in tab[i]]
        for a in range(m):
            if a!=i and tab[a][incoming]:
                mul=tab[a][incoming]
                tab[a]=[v-mul*w for v,w in zip(tab[a],tab[i])]
        basis[i]=incoming
    obj2,i2=simplex(tab,basis,
                    [Q(int(t==0)) for t in unanchored])
    primal=[Q(0)]*size
    for i,index in enumerate(basis):
        assert index<size
        primal[index]=tab[i][-1]
    cb=[Q(int(unanchored[index]==0)) for index in basis]
    lam=[sum(cb[i]*tab[i][size+j] for i in range(m))
         for j in range(m)]
    dual_poly=lambda t: sum(lam[j]*comb(t,j) for j in range(m))
    dual_obj=sum(lam[j]*residual[j] for j in range(m))
    assert obj2==dual_obj
    assert all(v>=0 for v in primal)
    assert all(dual_poly(t)>=int(t==0) for t in unanchored)
    assert all(sum(primal[i]*comb(t,j)
                   for i,t in enumerate(unanchored))==residual[j]
               for j in range(m))
    assert obj2==primal[unanchored.index(0)]
    assert all(primal[i]*(dual_poly(t)-int(t==0))==0
               for i,t in enumerate(unanchored))
    # Independently replay all ORIGINAL moments, including anchors.
    all_masses={t:Q(w) for t,w in anchors.items()}
    all_masses.update({t:primal[i] for i,t in enumerate(unanchored)})
    assert all(sum(w*comb(t,j) for t,w in all_masses.items())==raw[j]
               for j in range(m))
    return {
        "n":n,"degree":k,
        "anchors":{str(t):int(v) for t,v in sorted(anchors.items())},
        "residual_moments":[str(b) for b in residual],
        "exact_optimum":str(obj2),
        "integer_upper_bound":obj2.numerator//obj2.denominator,
        "dual_coefficients":[str(c) for c in lam],
        "primal_support":[{"t":t,"mass":str(w)}
                          for t,w in sorted(all_masses.items()) if w],
        "phase_iterations":[i1,i2],
        "primal_verified":True,"dual_verified":True,
        "equality_verified":True
    }


def exact_manual_anchored_q36():
    n=36
    # N0=128, N1=1152, N2=6624 in BINOMIAL basis.
    raw=(128,1152,6624)
    anchors={36:1,33:0}
    q=lambda t: (Q(1)-Q(t,9))*(Q(1)-Q(t,12))
    assert all(q(t)>=int(t==0)
               for t in range(0,n+1,3) if t not in anchors)
    residual=(127,1116,6624-comb(36,2))
    assert residual==(127,1116,5994)
    # q=1-7/36*t+1/108*t^2
    # q=1-(7/36-1/108)*t+(1/54)*binom(t,2)
    coeff=(Q(1), -Q(7,36)+Q(1,108), Q(1,54))
    assert all(sum(coeff[j]*comb(t,j) for j in range(3))==q(t)
               for t in range(0,n+1,3))
    value=sum(coeff[i]*residual[i] for i in range(3))
    assert value==Q(94,3)
    primal={0:Q(94,3),9:Q(32,3),12:Q(85),36:Q(1)}
    assert sum(primal.values())==128
    assert all(sum(w*comb(t,j) for t,w in primal.items())==raw[j]
               for j in range(3))
    lp=anchored_optimal_lp(36,raw,2,anchors)
    assert lp["exact_optimum"]==str(value)
    return {"manual_q_coefficients":[str(x) for x in coeff],
            "manual_exact_dual":str(value),
            "manual_primal":[{"t":t,"mass":str(x)} for t,x in primal.items()],
            "independent_lp":lp}


def self_test():
    exact=exact_manual_anchored_q36()
    assert exact["independent_lp"]["integer_upper_bound"]==31
    return {
        "status":"ANCHOR_ROOT_36_DEGREE2_PRIMAL_DUAL_CERTIFIED",
        "manual":exact,
        "universal_polynomial_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:
        p.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
