#!/usr/bin/env python3
"""R5 E4.1 — proof-carrying AFFINE MacWilliams for every Boolean SCL cube.

Given fixed x bits Z=0, O=1, set v=1+x, a=v_S=indicator(Z).
For free T, solve A_T v_T = A_S a; the affine code is v0+L,
L=ker A_T, |L|=2^d, rank(A_T)=r, m=|T|, r+d=m.

D_s=sum_{u in row(A_T), |u|=s} (-1)^(u.v0).
N_j=2^(-r) sum_s D_s K_j(s;m), exact affine identity.

***D_s CAN BE NEGATIVE.*** In the LP use P_s,M_s >=0 and
D_s=P_s-M_s, B_s=P_s+M_s. Homogeneous H_i and coset C_j
are separate nonnegative distributions, constrained by
2^d (P_s +/- M_s) = sum_i H_i K_s(i)
and sum_j C_j K_s(j) respectively.

Full origin spectrum constraints MUST NEVER be inherited directly
into an affine child. Each child rebuilds its restricted rowspace.
All k moment counts computed by O(m^k) GF2 rank queries for fixed k,
not by enumerating 2^d codewords. Exact simplex gives primal/dual
certificates but polynomial number of Fraction pivots is NOT proved.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import comb
import argparse, json

from r5_cooperative_scl_coverage_20261015 import (
    validate_scl, gf2_affine, valid_witness, fixtures
)
from r5_optimal_moment_lp_20261015 import simplex
from r5_bidirectional_macwilliams_lp_20261015 import krawtchouk
from r5_local_codeword_anchors_20261015 import linear_validate_and_incidence


def affine_data(rows,cube):
    rows,_=linear_validate_and_incidence(rows)
    n=len(rows)
    Z,O=cube
    if Z<0 or O<0 or (Z&O) or ((Z|O)>>n):
        raise ValueError("invalid Boolean cube")
    x_aff=gf2_affine(rows,Z,O)
    if x_aff is None:
        return None
    x0,basis,d=x_aff
    free=tuple(v for v in range(n) if not ((Z|O)>>v)&1)
    free_mask=sum(1<<v for v in free)
    m=len(free)
    v0=free_mask & ~x0
    assert all((b&~free_mask)==0 for b in basis)
    assert d+m*0==len(basis)
    assert m-d>=0
    a=Z
    homogeneous=all(sum((a>>v)&1 for v in row)%2==0
                    for row in rows)
    # Independent parity check in all original rows for x and v.
    for row in rows:
        assert sum((x0>>v)&1 for v in row)%2==1
        full_v=v0|a
        assert sum((full_v>>v)&1 for v in row)%2==0
    return {"rows":rows,"cube":cube,"n":n,"free":free,
            "free_mask":free_mask,"m":m,"d":d,"r":m-d,
            "particular_free":v0,"kernel_basis":basis,
            "fixed_v_weight":Z.bit_count(),
            "homogeneous_restricted_rhs":homogeneous,
            "parity":v0.bit_count()%2,
            "target_free_weight":2*n//3-Z.bit_count() if n%3==0 else None}


def gf2_linear_count_with_ones(basis,part,selected):
    """Count affine seeds making every selected source coordinate one."""
    d=len(basis)
    echelon={}
    for v in selected:
        mask=sum(1<<j for j,b in enumerate(basis) if (b>>v)&1)
        rhs=1^((part>>v)&1)
        while mask:
            p=mask.bit_length()-1
            if p in echelon:
                z,t=echelon[p]
                mask^=z
                rhs^=t
            else:
                echelon[p]=(mask,rhs)
                break
        else:
            if rhs:
                return 0
    return 1<<(d-len(echelon))


def coset_moments(data,k=3,homogeneous=False):
    """Sum binomial(weight,j) for j<=k; O(m^k) rank queries."""
    if k<0 or k>5:
        raise ValueError("fixed-degree k in 0..5")
    basis=data["kernel_basis"]
    part=0 if homogeneous else data["particular_free"]
    free=data["free"]
    totals=[]
    for j in range(k+1):
        total=0
        for subset in combinations(free,j):
            total+=gf2_linear_count_with_ones(basis,part,subset)
        totals.append(total)
    assert totals[0]==1<<data["d"]
    return tuple(totals)


def signed_low_rowspace(data,k=3):
    """Independent low-weight exact R_T membership and sign by x0."""
    if not 0<=k<=4:
        raise ValueError("fixed signed low-weight degree<=4")
    free=data["free"]
    basis=data["kernel_basis"]
    part=data["particular_free"]
    out={}
    for j in range(k+1):
        pos=neg=0
        for subset in combinations(free,j):
            u=sum(1<<v for v in subset)
            if any((u&b).bit_count()%2 for b in basis):
                continue
            if (u&part).bit_count()%2:
                neg+=1
            else:
                pos+=1
        out[j]=(pos,neg)
    assert out[0]==(1,0)
    return out


def enumerate_affine_oracle(data,cap=1<<13):
    """ONLY small finite regression oracle, intentionally exponential."""
    d=data["d"]
    if 1<<d>cap:
        raise ValueError("finite oracle budget exceeded")
    m=data["m"]
    hist=Counter()
    base=data["particular_free"]
    for seed in range(1<<d):
        v=base
        for j,b in enumerate(data["kernel_basis"]):
            if seed>>j&1:
                v^=b
        hist[v.bit_count()]+=1
    assert sum(hist.values())==1<<d
    return dict(hist)


def spectral_transform_from_oracle(data,hist):
    """Independent full D_s via inverse Krawtchouk transform.

    D_s=2^-d sum_j C_j K_s(j;m). This recomputes from an
    independently enumerated affine histogram, not the LP.
    """
    m,d=data["m"],data["d"]
    D={}
    for s in range(m+1):
        t=sum(Q(mass)*krawtchouk(m,s,j)
              for j,mass in hist.items())/Q(1<<d)
        assert t.denominator==1
        D[s]=int(t)
    assert all(D[m-s]==((-1)**data["parity"])*D[s]
               for s in range(m+1))
    return D


def check_exact_coset_identity(data,hist,D):
    m,r=data["m"],data["r"]
    for j in range(m+1):
        mass=sum(D[s]*krawtchouk(m,j,s)
                 for s in range(m+1))
        assert mass%(1<<r)==0,(j,mass,r)
        assert mass//(1<<r)==hist.get(j,0),(
            j,mass,r,hist.get(j,0))
    return True


def exact_affine_lp(data,k=2,known_signed_degree=3):
    """Certified compact LP over homogeneous/coset/positive/negative spectra."""
    m,d,r=data["m"],data["d"],data["r"]
    if not 0<=k<=3 or not 0<=known_signed_degree<=3:
        raise ValueError("fixed LP moments/low spectrum <=3")
    if not m or m<4:
        raise ValueError("finite LP requires >=4 free coordinates")
    N=1<<d
    parity=data["parity"]
    jtarget=data["target_free_weight"]
    C_indices=list(range(parity,m+1,2))
    H_indices=list(range(0,m+1,2))
    if jtarget is None or not 0<=jtarget<=m or jtarget%2!=parity:
        return {"verdict":"UNSAT","reason":"target free weight impossible"}
    # A zero-weight continuation consists only of v_T=0 and is
    # directly checkable without invoking any relaxation.
    if jtarget==0:
        cnt=int(data["homogeneous_restricted_rhs"])
        return {"verdict":"EXACT_DIRECT_ZERO_TARGET",
                "exact_rational_optimum":str(cnt),
                "integer_upper_bound":cnt,
                "primal_verified":True,"dual_verified":True,
                "known_signed_low":{},
                "target_free_weight":0}
    low=signed_low_rowspace(data,known_signed_degree)
    # Full rowspace 1_T always belongs to R_T, and has signed
    # character (-1)^|v0|. Thus fixed endpoint spectra.
    anchored_spec={0:(1,0),m:((1,0) if parity==0 else (0,1))}
    anchored_spec.update({s:counts for s,counts in low.items()
                          if 0<s<m})
    # H0 always 1; affine C0 is 1 iff RHS0 (particular v0 in L).
    # We detect if v0==0 (chosen Gaussian particular) and use
    # C0=1 when homogeneous; otherwise C0=0.
    Hanchors={0:1}
    Canchors={}
    if 0 in C_indices:
        Canchors[0]=int(data["homogeneous_restricted_rhs"])
    unknownH=[i for i in H_indices if i not in Hanchors]
    unknownC=[i for i in C_indices if i not in Canchors]
    spect=[s for s in range(1,m) if s not in anchored_spec]
    names=[("H",i) for i in unknownH]+[("C",i) for i in unknownC]
    names += [("P",s) for s in spect]+[("M",s) for s in spect]
    size=len(names)
    index={v:j for j,v in enumerate(names)}
    equations=[]

    def add_equation(label,coefs,rhs):
        equations.append((label,coefs,Q(rhs)))

    for kind in ("H","C"):
        unknown=unknownH if kind=="H" else unknownC
        anchors=Hanchors if kind=="H" else Canchors
        coefs=[Q(0)]*size
        for i in unknown:
            coefs[index[(kind,i)]]=Q(1)
        add_equation((kind,"COUNT"),coefs,N-sum(anchors.values()))

    Cmom=coset_moments(data,k)
    for ell in range(1,k+1):
        coefs=[Q(0)]*size
        for i in unknownC:
            coefs[index[("C",i)]]=Q(comb(i,ell))
        rhs=Cmom[ell]-sum(Q(v)*comb(j,ell)
                          for j,v in Canchors.items())
        add_equation(("C","MOM",ell),coefs,rhs)

    for s in range(1,m):
        # H Kraw spectrum: sum H_i K_s(i) = N (P_s+M_s).
        coefs=[Q(0)]*size
        for i in unknownH:
            coefs[index[("H",i)]]=Q(krawtchouk(m,s,i))
        rhs=-sum(Q(a)*krawtchouk(m,s,i)
                 for i,a in Hanchors.items())
        if s in anchored_spec:
            rhs+=N*sum(anchored_spec[s])
        else:
            coefs[index[("P",s)]]=-Q(N)
            coefs[index[("M",s)]]=-Q(N)
        add_equation(("H","MAC",s),coefs,rhs)

        # C signed spectrum: sum C_i K_s(i) = N (P_s-M_s).
        coefs=[Q(0)]*size
        for i in unknownC:
            coefs[index[("C",i)]]=Q(krawtchouk(m,s,i))
        rhs=-sum(Q(a)*krawtchouk(m,s,i)
                 for i,a in Canchors.items())
        if s in anchored_spec:
            rhs+=N*(anchored_spec[s][0]-anchored_spec[s][1])
        else:
            coefs[index[("P",s)]]=-Q(N)
            coefs[index[("M",s)]]=Q(N)
        add_equation(("C","MAC",s),coefs,rhs)

    # IMPORTANT verify equation sign carefully: all term equations
    # in generic form 'LHS unknown = required RHS'.
    # We wrote RHS=-known plus N*knownSpectrum for fixed spectra,
    # and -known for unknown spectra; this is correct because
    # unknown term sum + known term = N*spectrum.
    # With unknown spectrum coefs must be -N(P+M).
    # For fixed spectrum, RHS=N*given-known.

    signed=[]
    for label,coefs,rhs in equations:
        orientation=-1 if rhs<0 else 1
        signed.append((label,[Q(orientation)*v for v in coefs],
                       Q(orientation)*rhs,orientation))
    eqCount=len(signed)
    tab=[
        coef+[Q(int(i==j)) for j in range(eqCount)]+[rhs]
        for i,(_,coef,rhs,_) in enumerate(signed)
    ]
    basis=list(range(size,size+eqCount))
    p1,it1=simplex(tab,basis,[Q(0)]*size+[-Q(1)]*eqCount)
    if p1!=0:
        raise AssertionError("true affine moment/coset LP inexplicably infeasible")
    idx=0
    redundant=0
    while idx<len(basis):
        if basis[idx]<size:
            idx+=1;continue
        inbasis=set(basis)
        entering=next((j for j in range(size)
                       if j not in inbasis and tab[idx][j]!=0),None)
        if entering is None:
            assert tab[idx][-1]==0
            tab.pop(idx)
            basis.pop(idx)
            redundant+=1
            continue
        pivot=tab[idx][entering]
        tab[idx]=[v/pivot for v in tab[idx]]
        for ii in range(len(tab)):
            if ii!=idx and tab[ii][entering]:
                f=tab[ii][entering]
                tab[ii]=[a-f*b for a,b in zip(tab[ii],tab[idx])]
        basis[idx]=entering
        idx+=1
    objective=[Q(int(v==("C",jtarget))) for v in names]
    opt,it2=simplex(tab,basis,objective)
    masses=[Q(0)]*size
    for i,j in enumerate(basis):
        assert j<size
        masses[j]=tab[i][-1]
    multipliers=[
        sum(objective[basis[i]]*tab[i][size+e]
            for i in range(len(basis)))
        for e in range(eqCount)
    ]
    # Independent full primal + dual verifier (not just simplex status).
    assert all(v>=0 for v in masses)
    assert all(sum(signed[e][1][j]*masses[j]
                   for j in range(size))==signed[e][2]
               for e in range(eqCount))
    assert all(sum(multipliers[e]*signed[e][1][j]
                   for e in range(eqCount))>=objective[j]
               for j in range(size))
    dual_obj=sum(multipliers[e]*signed[e][2]
                 for e in range(eqCount))
    assert dual_obj==opt
    H=dict((i,Q(v)) for i,v in Hanchors.items())
    C=dict((i,Q(v)) for i,v in Canchors.items())
    for name,v in zip(names,masses):
        if name[0]=="H":H[name[1]]=v
        if name[0]=="C":C[name[1]]=v
    assert sum(H.values())==sum(C.values())==N
    assert H[0]==1
    assert all(sum(v*comb(j,ell) for j,v in C.items())==Cmom[ell]
               for ell in range(k+1))
    P=dict((s,Q(v[0])) for s,v in anchored_spec.items())
    M=dict((s,Q(v[1])) for s,v in anchored_spec.items())
    for (kind,s),v in zip(names,masses):
        if kind=="P":P[s]=v
        if kind=="M":M[s]=v
    for s in range(m+1):
        assert P[s]>=0 and M[s]>=0
        lhsH=sum(a*krawtchouk(m,s,i) for i,a in H.items())
        lhsC=sum(a*krawtchouk(m,s,i) for i,a in C.items())
        assert lhsH==N*(P[s]+M[s]),("homogeneous Mac",s)
        assert lhsC==N*(P[s]-M[s]),("signed Mac",s)
    assert opt==C.get(jtarget,0)
    return {
        "verdict":"BOUNDED","m":m,"d":d,"r":r,
        "fixed_kernel_v_weight":data["fixed_v_weight"],
        "target_free_weight":jtarget,
        "root_is_affine":data["cube"]!=(0,0),
        "exact_rational_optimum":str(opt),
        "integer_upper_bound":opt.numerator//opt.denominator,
        "known_signed_low":{str(s):list(v) for s,v in low.items()},
        "primal_C_weight":{str(j):str(v) for j,v in C.items() if v},
        "primal_H_weight":{str(j):str(v) for j,v in H.items() if v},
        "dual_multipliers":[str(v) for v in multipliers],
        "dual_verified":True,"primal_verified":True,
        "reduced_equalities":redundant,
        "phase_pivots":[it1,it2]
    }


def prove_finite_cube(rows,cube):
    d=affine_data(rows,cube)
    if d is None:
        return {"verdict":"GF2_INCONSISTENT"}
    hist=enumerate_affine_oracle(d)
    D=spectral_transform_from_oracle(d,hist)
    assert check_exact_coset_identity(d,hist,D)
    signed=signed_low_rowspace(d,3)
    assert all(D[s]==v[0]-v[1] for s,v in signed.items())
    target=d["target_free_weight"]
    exact=hist.get(target,0)
    lp=exact_affine_lp(d,k=2,known_signed_degree=3)
    assert lp["integer_upper_bound"]>=exact
    assert lp["primal_verified"] and lp["dual_verified"]
    return {
        "cube":cube, "m":d["m"],"rank":d["r"],
        "nullity":d["d"],"target":target,
        "exact_count":exact,
        "spectrum_has_negative":any(v<0 for v in D.values()),
        "D_m":D[d["m"]],
        "signed_low":{str(s):D[s] for s in range(min(4,d["m"]+1))},
        "LP2_optimum":lp["exact_rational_optimum"],
        "LP2_floor":lp["integer_upper_bound"],
        "LP2_proofs":True
    }


def self_test():
    cases={"AffinePlane9":fixtures()["AffinePlane9_SAT"],
           "HolyerK4":fixtures()["HolyerK4_SAT"]}
    out={}
    for name,rows in cases.items():
        n=len(rows)
        tests=[(0,0),(1<<0,0),(0,1<<0),
               ((1<<0)|(1<<2),0)]
        vals=[]
        for cube in tests:
            print("CHECK_AFFINE_CUBE",name,cube,flush=True)
            try:
                ret=prove_finite_cube(rows,cube)
            except ValueError as exc:
                # If d>13 the independent oracle cannot finish;
                # record it rather than promoting to a negative.
                ret={"cube":cube,"oracle":"UNKNOWN_RESOURCE_LIMIT",
                     "detail":str(exc)}
            vals.append(ret)
        assert any(x.get("spectrum_has_negative") and
                   x.get("D_m")==-1 for x in vals)
        out[name]=vals
    return {"status":"AFFINE_MACWILLIAMS_EXACT_SIGNED_COSERET_AND_LP",
            "checks":out,"global_polynomial_SCL":"NOT_CONSTRUCTED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:p.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
