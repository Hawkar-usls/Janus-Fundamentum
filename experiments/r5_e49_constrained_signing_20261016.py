#!/usr/bin/env python3
"""E4.9 CONSTRAINED_SIGNING: optimize NEW signed 2lift eigenvalues.

The source Γ's adjacency spectrum consists of eigenvalues ±svd(B),
where B is its 45×45 source incidence matrix. For edge signing
sigma, NEW 2lift eigenvalues are ±svd(B_sigma) and OLD eigenvalues
remain those of source B. Searching only the 27-dimensional affine
family preserving both SAT-compatible z cannot repair poor OLD
spectrum. We enumerate a deterministic finite RANDOM SAMPLE plus
one-bit quotient hill-climb (OBSERVATION, NOT GLOBAL OPTIMUM).
Every tested voltage lies in independently certified 27-dim affine
family and preserves two exact-one lifted SAT mechanisms.

Numerical numpy SVD is used ONLY to PROPOSE candidates. For source
lambda2 and winner rho_signed, build 45×45 integral Gram matrices
BB^T and Bsigma Bsigma^T. INDEPENDENT exact rational symmetric
LDL^T inertia tests at rational squared endpoints produce a short
strict certificate lambda2 ∈ (2.9049, 2.9050) and
rho_new ∈ (floor(rho*1000)/1000, ceil(...)/1000), no floats
used to ACCEPT spectral inequalities. Since signed incidence
is bipartite, |lambda| max = sqrt(max eigenvalue Gram).

The result does not show existence of Ramanujan signing constrained
for ALL SCL, nor polynomial minimization over 2^27 instances.
"""
import argparse,json,random
from fractions import Fraction
from math import floor,ceil
from pathlib import Path

import numpy as np

from r5_e49_joint_cyclespace_20261016 import (
    run as cyclespace_run,witness_for_z
)


def signed_incidence(rows,mask):
    n=len(rows)
    A=np.zeros((n,n),dtype=float)
    e=0
    for i,row in enumerate(rows):
        for j in row:
            A[i,j]=-1.0 if (mask>>e)&1 else 1.0
            e+=1
    assert e==3*n
    return A


def new_radius(rows,mask):
    # 45x45 SVD, maximum signed-adjacency absolute eigenvalue.
    return float(np.linalg.svd(signed_incidence(rows,mask),
                               compute_uv=False)[0])


def signed_gram_int(rows,sign):
    n=len(rows)
    M=[[0]*n for _ in range(n)]
    signs={}
    bit=0
    for i,row in enumerate(rows):
        for j in row:
            signs[(i,j)]=-1 if (sign>>bit)&1 else 1
            bit+=1
    for i in range(n):
        for j in range(i,n):
            shared=set(rows[i])&set(rows[j])
            value=sum(signs[(i,c)]*signs[(j,c)] for c in shared)
            M[i][j]=M[j][i]=value
    assert all(M[i][i]==3 for i in range(n))
    return M


def rational_inertia_q2_minus_gram(G,num,den):
    """Fraction LDL inertia, no floating spectral assertions."""
    n=len(G)
    scale=Fraction(num*num,den*den)
    # Store lower triangle only. Symmetric Schur complement
    # update M[j][i]-=M[i][k]*M[j][k]/pivot.
    M=[[scale-G[i][i] if j==i else Fraction(-G[i][j])
        for j in range(i+1)] for i in range(n)]
    negative=0
    for k in range(n):
        pivot=M[k][k]
        assert pivot!=0,("zero LDL pivot",k,num,den)
        if pivot<0:negative+=1
        col=[M[i][k] for i in range(k+1,n)]
        for ii,i in enumerate(range(k+1,n)):
            c=col[ii]/pivot
            if c==0:continue
            for jj,j in enumerate(range(i,n)):
                M[j][i]-=c*col[ii+jj]
        for i in range(k+1,n):
            M[i][k]=0
    return negative


def count_at(G,lo,hi,den):
    below=rational_inertia_q2_minus_gram(G,lo,den)
    above=rational_inertia_q2_minus_gram(G,hi,den)
    assert above<=below
    return {"lower_rational":f"{lo}/{den}",
            "upper_rational":f"{hi}/{den}",
            "count_singular_values_greater_than_lower":below,
            "count_singular_values_greater_than_upper":above,
            "strict_endpoints_no_zero_pivots":True,
            "exact_rational_inertia":True}


def run(path,samples=400,seed=20261016):
    F=json.loads(Path(path).read_text())
    rows=F["base_45_rows"]
    C=cyclespace_run(path)
    gens=[int(v) for v in C["non_gauge_compatible_voltage_generators_decimal"]]
    assert len(gens)==27
    original=int(F["sat_lift_voltage_bits_decimal"])
    original_rho=new_radius(rows,original)
    rng=random.Random(seed)
    best=original;best_rho=original_rho;best_code=0
    unique={0}
    for index in range(samples):
        code=rng.getrandbits(len(gens))
        if code in unique:continue
        unique.add(code)
        delta=0
        for i,g in enumerate(gens):
            if (code>>i)&1:delta^=g
        sigma=original^delta
        rho=new_radius(rows,sigma)
        if rho+1e-11<best_rho:
            best,best_rho,best_code=sigma,rho,code
    rounds=0
    while rounds<5:
        rounds+=1; changed=False
        for i,g in enumerate(gens):
            candidate=best^g
            rho=new_radius(rows,candidate)
            if rho+1e-11<best_rho:
                best=candidate;best_rho=rho;best_code^=1<<i
                changed=True
        if not changed:break
    assert best_rho<=original_rho+1e-10
    # Strictly verify that the chosen sigma is within affine basis.
    derived=original
    for j,g in enumerate(gens):
        if (best_code>>j)&1:derived^=g
    assert derived==best
    E=[(i,j) for i,row in enumerate(rows) for j in row]
    lookup={edge:k for k,edge in enumerate(E)}
    zlist=[int(z) for z in F["distinct_z_decimal"]]
    found_witnesses=[witness_for_z(rows,z,best,lookup) for z in zlist]
    assert all(w is not None for w in found_witnesses)
    assert len(set(found_witnesses))==len(zlist)
    # Explicit source-edge cycle equations are checked again for
    # the FINAL combined perturbation, not only its basis vectors.
    for Z in C["G_z"]:
        for eq in Z["fundamental_cycle_constraints"]:
            mask=int(eq["incidence_mask_decimal"])
            assert ((mask&best).bit_count()&1)==eq["rhs"]
    # Numerical brackets are GUESSES. Exact rational LDL
    # counts constitute the actual acceptance certificate.
    low=max(0,int(floor(best_rho*1000))-1)
    high=int(ceil(best_rho*1000))+1
    Gsource=signed_gram_int(rows,0)
    Gbest=signed_gram_int(rows,best)
    source_spec=count_at(Gsource,29049,29050,10000)
    assert source_spec["count_singular_values_greater_than_lower"]==2
    assert source_spec["count_singular_values_greater_than_upper"]==1
    best_spec=count_at(Gbest,low,high,1000)
    assert best_spec["count_singular_values_greater_than_lower"]>=1
    assert best_spec["count_singular_values_greater_than_upper"]==0
    assert high*high<8*(1000**2), "new-spectrum bound not certified"
    assert 29049**2>8*(10000**2), "old-spectrum obstruction not certified"
    # We can assert observable best signed radius above/below
    # Ramanujan bound 2 sqrt2 using rational 8 threshold
    # without irrational arithmetic: q²=8.
    # This is Gram8-I inertia; use pivot-safe close rational
    # bracket instead of q=2sqrt2 as eigenvalue condition.
    return {
        "gate":"E4_9_CONSTRAINED_SIGNING",
        "source_sha256":F["base_canonical_sha256"],
        "numpy_only_for_heuristic_candidate_generation":True,
        "sample_seed":seed,"random_quotient_samples":samples,
        "distinct_random_samples_tried":len(unique),
        "greedy_local_improvement_rounds":rounds,
        "compatible_quotient_dimension":len(gens),
        "baseline_signed_voltage_decimal":str(original),
        "baseline_new_signed_rho_numeric":original_rho,
        "best_observed_new_signed_rho_numeric":best_rho,
        "best_quotient_code_decimal":str(best_code),
        "best_voltage_mask_decimal":str(best),
        "best_compatible_exact_GF2":True,
        "best_witnesses_for_both_z_decimal":[str(w) for w in found_witnesses],
        "best_witnesses_exact_row_sum_verified":True,
        "certified_new_spectrum_strictly_inside_2sqrt2":True,
        "certified_source_lambda2_strictly_above_2sqrt2":True,
        "source_lambda2_numerical":sorted(
            np.linalg.svd(signed_incidence(rows,0),compute_uv=False),
            reverse=True)[1],
        "source_lambda2_exact_rational_interval":source_spec,
        "new_signed_radius_exact_rational_interval":best_spec,
        "old_eigenvalues_inherited_by_every_2lift":"PROVED",
        "best_global_optimum_over_2_power_27":"NOT_CLAIMED",
        "constrained_Ramanujan_theorem":"NOT_ESTABLISHED",
        "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    p.add_argument("--samples",type=int,default=400)
    opt=p.parse_args()
    print(json.dumps(run(opt.fixture,opt.samples),indent=2,sort_keys=True))
