#!/usr/bin/env python3
"""Gate E4: two-sided exact MacWilliams-Delsarte weight enumerator LP.

Primal variables: unknown nonnegative even kernel codeword weights A_i
(i=0,2,...,2n/3), plus nonnegative B_j weights of the dual row code.
Constraints:
  - exact low binomial t moments,
  - exact kernel weight anchors (A0,A2,A4,A6,A8,A10),
  - MacWilliams equality sum_i A_i K_j(i) = 2^d B_j,
  - optionally low j dual B_j known exactly from polynomial rowspace tests.
All j are included logically: because every kernel word has even
weight and n divisible 3, 1 lies in rowspace, forcing B_j=B_(n-j).
Thus suffice j=1,...,floor(n/2) plus B0=Bn=1 from sum A_i.

Exact two-phase Fraction simplex is used only as CERTIFICATE GENERATOR;
its number of pivots is NOT claimed polynomial. The LP MATHEMATICAL
size is O(n), with polynomial-bit Krawtchouk coefficients.
Independent dual and primal validity + objective equality are checked.
"""
from fractions import Fraction as Q
from math import comb
from itertools import combinations
import json,argparse,random

from r5_optimal_moment_lp_20261015 import simplex
from r5_cooperative_scl_coverage_20261015 import (
    gf2_affine,fixtures
)
from r5_component_factor_20261015 import k4_blocks
from r5_connected_coverage_breaker_20261015 import (
    make_connected,mutate_connected
)
from r5_optimal_moment_gates_20261015 import (
    affine_hist,component_hist
)
from r5_local_codeword_anchors_20261015 import (
    linear_validate_and_incidence,anchor_counts
)
from r5_local_codeword_anchors_8_10_20261015 import (
    anchor_8_10
)


def krawtchouk(n,j,i):
    return sum((-1)**s*comb(i,s)*comb(n-i,j-s)
               for s in range(max(0,j-n+i),min(j,i)+1))


def rowspace_low_counts(rows,k=3):
    """B_j via sparse fixed-j rowspace membership, no dual enumeration."""
    if not 0<=k<=3:
        raise ValueError("fixed k<=3 only")
    rows,_=linear_validate_and_incidence(rows)
    n=len(rows)
    # Rowspace = ker(A)^perp. Orthogonality to each kernel basis
    # vector is an exact polynomial GF2 membership test.
    affine=gf2_affine(rows,0,0)
    if affine is None:
        raise AssertionError("Ax=1 mod2 always consistent in cubic source")
    _,basis,d=affine
    b={}
    for w in range(k+1):
        tally=0
        for subset in combinations(range(n),w):
            mask=sum(1<<v for v in subset)
            if all((mask&kernel).bit_count()%2==0 for kernel in basis):
                tally+=1
        b[w]=tally
    assert b[0]==1
    return b


def signed_low_spectrum(rows,k=3):
    b=rowspace_low_counts(rows,k)
    return {j:(-1)**j*b[j] for j in b}


def solve_exact_mac_lp(n,d,raw,k,anchors,known_dual=None):
    """Exact rational primal-dual LP with Krawtchouk constraints.

    Anchors are a map of kernel weights i -> exact A_i. The target
    i=2n/3 is NEVER supplied among anchors in the research fixtures.
    """
    if n%3 or not 0<=k<=5 or len(raw)<k+1:
        raise ValueError("invalid n or moment degree")
    if d<0 or any(i%2 or i<0 or i>2*n//3 or int(v)!=v or v<0
                  for i,v in anchors.items()):
        raise ValueError("invalid exact kernel anchors")
    target=2*n//3
    if target in anchors:
        raise ValueError("cannot anchor target: model expects unknown count")
    indices=list(range(0,target+1,2))
    if any(i not in indices for i in anchors):
        raise ValueError("invalid support index")
    known_dual={} if known_dual is None else dict(known_dual)
    if any(j<=0 or j>n//2 or int(v)!=v or v<0
           for j,v in known_dual.items()):
        raise ValueError("invalid low dual anchors")
    unknown=[i for i in indices if i not in anchors]
    # primal variables A_i followed by B_j slack for all unfixed j.
    slack=[j for j in range(1,n//2+1) if j not in known_dual]
    variable_names=[("A",i) for i in unknown]+[("B",j) for j in slack]
    Nv=len(variable_names)
    N=1<<d
    equations=[]
    for ell in range(k+1):
        coeff=[Q(comb(n-3*i//2,ell)) for i in unknown]
        coeff += [Q(0)]*len(slack)
        rhs=Q(raw[ell])-sum(Q(v)*comb(n-3*i//2,ell)
                             for i,v in anchors.items())
        equations.append(("M",ell,coeff,rhs))
    for j in range(1,n//2+1):
        coeff=[Q(krawtchouk(n,j,i)) for i in unknown]
        coeff += [Q(-N if j==q else 0) for q in slack]
        rhs=Q(N*known_dual[j] if j in known_dual else 0)
        rhs-=sum(Q(v)*krawtchouk(n,j,i)
                 for i,v in anchors.items())
        equations.append(("B",j,coeff,rhs))
    # Nonnegative artificial RHS for trivial phase I basis. Reversing
    # row orientation keeps equality constraints equivalent.
    signed=[]
    for kind,idx,coeff,rhs in equations:
        scale=-1 if rhs<0 else 1
        signed.append((kind,idx,[Q(scale)*v for v in coeff],Q(scale)*rhs,
                       scale))
    m=len(signed)
    tab=[
        row+[Q(int(i==j)) for j in range(m)]+[rhs]
        for i,(_,_,row,rhs,_) in enumerate(signed)
    ]
    basis=list(range(Nv,Nv+m))
    objective1,phase1=simplex(tab,basis,[Q(0)]*Nv+[-Q(1)]*m)
    if objective1:
        raise ValueError("MacWilliams+moment anchors are inconsistent")
    # All remaining artificial basic values are ZERO. Pivot out
    # when possible; otherwise remove redundant equality rows.
    i=0
    redundant=0
    while i<len(basis):
        if basis[i]<Nv:
            i+=1
            continue
        occupied=set(basis)
        incoming=next((j for j in range(Nv)
                       if j not in occupied and tab[i][j]!=0),None)
        if incoming is None:
            assert tab[i][-1]==0
            tab.pop(i)
            basis.pop(i)
            redundant+=1
            continue
        factor=tab[i][incoming]
        tab[i]=[v/factor for v in tab[i]]
        for z in range(len(tab)):
            if z!=i and tab[z][incoming]:
                mul=tab[z][incoming]
                tab[z]=[a-mul*b for a,b in zip(tab[z],tab[i])]
        basis[i]=incoming
        i+=1
    costs=[Q(int(v==("A",target))) for v in variable_names]
    optimum,pivots=simplex(tab,basis,costs)
    primal=[Q(0)]*Nv
    for i,j in enumerate(basis):
        assert j<Nv
        primal[j]=tab[i][-1]
    # Dual y from original artificial B^{-1} columns of this tableau.
    cb=[costs[j] for j in basis]
    multiplier=[
        sum(cb[i]*tab[i][Nv+j] for i in range(len(tab)))
        for j in range(m)
    ]
    independently_verified=True
    # primal: exact original moment and full MacWilliams constraints.
    masses={i:Q(v) for i,v in anchors.items()}
    masses.update({idx:primal[j] for j,(kind,idx)
                   in enumerate(variable_names) if kind=="A"})
    bvars={j:primal[z] for z,(kind,j) in enumerate(variable_names)
           if kind=="B"}
    assert all(v>=0 for v in primal)
    assert sum(masses.values())==N
    assert all(sum(a*comb(n-3*i//2,ell)
                   for i,a in masses.items())==raw[ell]
               for ell in range(k+1))
    spectrum={}
    for j in range(n+1):
        value=sum(a*krawtchouk(n,j,i) for i,a in masses.items())
        assert value>=0,("Mac negativity",j,value)
        spectrum[j]=value/Q(N)
        assert spectrum[j]>=0
        if 0<j<=n//2:
            if j in known_dual:
                assert spectrum[j]==known_dual[j]
            else:
                assert spectrum[j]==bvars[j]
    assert all(spectrum[j]==spectrum[n-j] for j in range(n+1))
    assert spectrum[0]==1 and spectrum[n]==1
    assert masses[target]==optimum
    # independent signed equality dual feasible check
    rhs=[eq[3] for eq in signed]
    dualobjective=sum(multiplier[r]*rhs[r] for r in range(m))
    assert dualobjective==optimum
    assert all(sum(multiplier[r]*signed[r][2][col]
                   for r in range(m))>=costs[col]
               for col in range(Nv))
    assert all(primal[col]*(
        sum(multiplier[r]*signed[r][2][col]
            for r in range(m))-costs[col])==0
        for col in range(Nv))
    return {
        "n":n,"degree":k,"nullity":d,
        "optimum":str(optimum),
        "integer_upper_bound":optimum.numerator//optimum.denominator,
        "primal_kernel_distribution":{
            str(i):str(v) for i,v in sorted(masses.items()) if v},
        "dual_row_distribution":{
            str(j):str(v) for j,v in sorted(spectrum.items()) if v},
        "dual_multipliers":[str(v) for v in multiplier],
        "primal_dual_verified":True,
        "all_krawtchouk_inequalities_verified":True,
        "phase_iterations":[phase1,pivots],
        "redundant_equalities":redundant,
        "constraints":m,"variables":Nv
    }


def moments_from_hist(n,hist,k):
    return [sum(cnt*comb(t,j) for t,cnt in hist.items())
            for j in range(k+1)]


def anchors_root(rows):
    n=len(rows)
    base=anchor_counts(rows)
    higher,_=anchor_8_10(rows)
    out={0:base[n],2:base[n-3],4:base[n-6],
         6:base[n-9],8:higher[8],10:higher[10]}
    return {i:v for i,v in out.items() if i<=2*n//3}


def connected_pair(seed):
    rows,witness,_=make_connected(2,seed)
    return mutate_connected(
        rows,witness,random.Random(seed*991+20261015),
        moves=4+(seed%13)
    )[0]


def self_test():
    # Fixed tiny legal SCL. (General n=9 LP source to verify.)
    controls=[
        ("Connected36_seed0",connected_pair(0),"finite"),
        ("Connected36_seed13",connected_pair(13),"finite"),
        ("Petersen45",fixtures()["HolyerPetersen_UNSAT"],"finite")
    ]
    result={}
    for label,rows,mode in controls:
        n=len(rows)
        affine=gf2_affine(rows,0,0)
        assert affine is not None
        d=affine[2]
        hist=affine_hist(rows,cap=n**3)
        anchors=anchors_root(rows)
        known=rowspace_low_counts(rows,3)
        assert known[0]==1
        graded={}
        for k in (2,3):
            data=solve_exact_mac_lp(
                n,d,moments_from_hist(n,hist,k),
                k,anchors,{j:v for j,v in known.items() if j>0}
            )
            assert data["integer_upper_bound"]>=hist[0]
            graded[str(k)]={"optimum":data["optimum"],
                            "floor":data["integer_upper_bound"],
                            "primal_dual_verified":True,
                            "iterations":data["phase_iterations"]}
        result[label]={"n":n,"nullity":d,
                       "true_SAT":hist[0],"anchors":anchors,
                       "row_dual_low":known,"optima":graded}
    return {
        "status":"EXACT_BIDIRECTIONAL_MACWILLIAMS_PRIMAL_DUAL_VERIFIED",
        "controls":result,
        "all_n_theory":"poly-size LP, exact-Fraction simplex NOT polynomial bounded",
        "uniform_SCL_polynomial_solver":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:
        p.error("--self-test")
    print(json.dumps(self_test(),sort_keys=True,indent=2))
