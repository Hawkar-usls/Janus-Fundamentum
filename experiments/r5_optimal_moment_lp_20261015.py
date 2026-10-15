#!/usr/bin/env python3
"""Exact rational LP optimum for polynomial binomial moment certificates.

Primal: maximize w_0 subject to sum_t binom(t,j) w_t = N_j,
w_t >= 0, t in 0,3,...,n, j=0..k.
Dual: minimize sum_j lambda_j N_j subject to
q(t)=sum_j lambda_j binom(t,j) >= indicator(t==0).

Two-phase Bland simplex using Fraction; primal/dual checked
independently, with exact objective equality. k<=5 is FIXED.
When moments are passed from a verified polynomial fixed-k rank oracle
or a sound component convolution, this LP has polynomial input size.

No claim that exact high-degree moments are easy or that this produces
a universal polynomial-time SAT/UNSAT solver.
"""
from fractions import Fraction as Q
from math import comb
import argparse, json


def simplex(tab, basis, costs):
    """Deterministic exact tableau simplex, Bland entering/leaving rule."""
    m=len(basis)
    nvars=len(costs)
    seen=0
    while True:
        cb=[costs[x] for x in basis]
        reduced=[
            costs[j]-sum(cb[i]*tab[i][j] for i in range(m))
            for j in range(nvars)
        ]
        occupying=set(basis)
        entering=next((j for j in range(nvars)
                       if j not in occupying and reduced[j]>0),None)
        if entering is None:
            objective=sum(cb[i]*tab[i][-1] for i in range(m))
            return objective,seen
        possible=[i for i in range(m) if tab[i][entering]>0]
        if not possible:
            raise AssertionError("unbounded LP (unexpected)")
        leaving=min(possible,key=lambda i:(
            tab[i][-1]/tab[i][entering],basis[i]))
        pivot=tab[leaving][entering]
        tab[leaving]=[x/pivot for x in tab[leaving]]
        for i in range(m):
            if i==leaving:
                continue
            factor=tab[i][entering]
            if factor:
                tab[i]=[x-factor*y for x,y in
                        zip(tab[i],tab[leaving])]
        basis[leaving]=entering
        seen+=1
        if seen>20000:
            raise AssertionError("rational simplex exceeded safety iteration cap")


def exact_optimal_lp(n, raw, k, check=True):
    if n%3 or not 0<=k<=5:
        raise ValueError("legal n divisible3, fixed 0<=k<=5")
    if len(raw)<k+1 or raw[0]<=0 or any(x<0 for x in raw[:k+1]):
        raise ValueError("exact moment vector required")
    ts=list(range(0,n+1,3))
    m=k+1
    size=len(ts)
    if size<m:
        raise ValueError("degree larger than n/3")
    # Added artificial variables produce an always feasible phase-I
    # starting basis: raw moments are nonnegative integers.
    tab=[
        [Q(comb(t,j)) for t in ts]+
        [Q(int(i==j)) for i in range(m)]+[Q(raw[j])]
        for j in range(m)
    ]
    basis=list(range(size,size+m))
    obj1,iterations1=simplex(tab,basis,[Q(0)]*size+[-Q(1)]*m)
    if obj1 !=0:
        raise ValueError("moment sequence incompatible with any support distribution")

    # The binomial moment matrix has full row rank for size>=m,
    # hence all 0-valued artificial basics can be pivoted away.
    for i in range(m):
        if basis[i]<size:
            continue
        occupied=set(basis)
        entering=next((j for j in range(size)
                       if j not in occupied and tab[i][j]!=0),None)
        if entering is None or tab[i][-1]!=0:
            raise AssertionError("unable to eliminate zero artificial")
        factor=tab[i][entering]
        tab[i]=[x/factor for x in tab[i]]
        for z in range(m):
            if z!=i and tab[z][entering]!=0:
                mul=tab[z][entering]
                tab[z]=[x-mul*y for x,y in zip(tab[z],tab[i])]
        basis[i]=entering

    obj2,iterations2=simplex(tab,basis,
                             [Q(int(t==0)) for t in ts]+[Q(0)]*m)
    primal=[Q(0)]*size
    for i,j in enumerate(basis):
        assert j<size
        primal[j]=tab[i][-1]
    # Tableau columns for artificials ARE B^{-1}, so objective
    # multipliers y=c_B B^{-1} give an exact dual LP certificate.
    costs_basic=[Q(int(ts[j]==0)) for j in basis]
    lam=[
        sum(costs_basic[i]*tab[i][size+j] for i in range(m))
        for j in range(m)
    ]
    dual=[sum(lam[j]*comb(t,j) for j in range(m)) for t in ts]
    dual_objective=sum(lam[j]*raw[j] for j in range(m))
    assert obj2==dual_objective
    assert all(primal[i]>=0 for i in range(size))
    assert all(dual[i]>=int(t==0) for i,t in enumerate(ts))
    assert all(sum(primal[i]*comb(ts[i],j)
                   for i in range(size))==raw[j]
               for j in range(m))
    assert obj2==primal[0]
    assert all(primal[i]*(dual[i]-int(t==0))==0
               for i,t in enumerate(ts)) # complementary slackness

    return {
        "degree":k,"n":n,
        "exact_optimum":str(obj2),
        "integer_upper_bound":obj2.numerator//obj2.denominator,
        "dual_coefficients":[str(x) for x in lam],
        "primal_support":[{"t":t,"mass":str(primal[i])}
                          for i,t in enumerate(ts) if primal[i]],
        "iterations":[iterations1,iterations2],
        "verified_primal":True,"verified_dual":True,
        "exact_primal_dual_equality":True,
    }


def solve_from_histogram(n,hist,k):
    """Finite OR component-factor histogram; not assumed available for all n."""
    raw=[sum(count*comb(t,j) for t,count in hist.items())
         for j in range(k+1)]
    return exact_optimal_lp(n,raw,k)


def self_test():
    # Independent LP oracle with exact distribution supported at 0 and 9.
    result=solve_from_histogram(9,{0:3,9:1},1)
    assert result["integer_upper_bound"]==3
    # Unit test of weak moments: k0 cannot distinguish t=0 from t>0.
    assert solve_from_histogram(9,{0:3,9:1},0)["integer_upper_bound"]==4
    # Single-support distribution at positive t gives degree1 optimum 0
    # ONLY if the moment lies at the maximal support boundary.
    assert solve_from_histogram(9,{9:4},1)["integer_upper_bound"]==0
    return {"status":"EXACT_PRIMAL_DUAL_RATIONAL_SIMPLEX_VALIDATED",
            "small_cases":"PASS","P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    opt=p.parse_args()
    if opt.self_test:
        print(json.dumps(self_test(),indent=2))
    else:
        p.error("--self-test; invoke exact_optimal_lp from analysis scripts")
