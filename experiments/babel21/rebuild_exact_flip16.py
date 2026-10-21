#!/usr/bin/env python3
"""BABEL-21 independent, provenance-pinned BABEL8 source regeneration.

Recompute original flip16 degree2 Fourier-multiplier polynomial using 90
modular Lanczos primes with exact CRT coefficient bound, then verify ALL
32768 integer normal-operator coordinates and independently expand the
complete base source Fourier identity.

Lastly, verify both rank-quotient residuals against ALL original source
row/multiplier generators (including duplicate exact Fourier signatures).
It proves exact existence on two fixed covers conditioned only on earlier
independently certified ker(T) and syzygy rank, not generic P=NP.
"""
import argparse,gzip,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from janus_babel8_krylov_verify import input_data,normal
from janus_babel10_degree_scan import frozen_instances
from janus_babel6_transfer import xor_labels

EXPECTED_SHA="d9d3e3af51140222be83712fb0e9fe24d9c632fcd4198054d93684fc67a88a09"
P_DEGREE=245

def nextprime(x):
    candidate=x+1 if x%2==0 else x+2
    while True:
        prime=True
        for factor in range(3,int(candidate**.5)+1,2):
            if candidate%factor==0:
                prime=False;break
        if prime:return candidate
        candidate+=2

def modulo_lanczos(M,MT,p):
    old=np.zeros(32768,dtype=np.int64)
    current=old.copy();current[0]=1
    oldnorm=0;prev=[0];poly=[1]
    for step in range(700):
        norm=int(np.dot(current,current))%p
        if not norm:raise ArithmeticError(("isotropic",step,p))
        evaluated=M.dot(MT.dot(current))%p
        alpha=int(np.dot(current,evaluated))%p
        alpha=alpha*pow(norm,-1,p)%p
        beta=norm*pow(oldnorm,-1,p)%p if step else 0
        new=(evaluated-alpha*current-beta*old)%p
        out=[0]*(len(poly)+1)
        for k,c in enumerate(poly):
            out[k]=(out[k]-alpha*c)%p
            out[k+1]=(out[k+1]+c)%p
        for k,c in enumerate(prev):
            out[k]=(out[k]-beta*c)%p
        prev,poly=poly,out
        if not np.any(new):
            assert len(poly)==P_DEGREE+1,(p,step,len(poly))
            assert poly[0] and poly[-1]==1
            return poly
        old,current=current,new
        oldnorm=norm
    raise ArithmeticError(("Lanczos termination not reached",p))

def regenerate(max_primes=110):
    rows,labels,basis,eq,origins=input_data(16)
    frozen=frozen_instances()["SCL126_flip16"]
    assert [tuple(x) for x in rows]==[tuple(x) for x in frozen], "frozen rows differ from original proof"
    independent_labels,independent_Q,d=xor_labels(frozen)
    assert labels==independent_labels and set(basis)==set(independent_Q) and d==15
    assert len(eq)==128013 and len(basis)==2147
    E=np.asarray(eq,dtype=np.int64)
    n=len(eq)
    M=coo_matrix((np.ones(4*n,dtype=np.int64),(E.ravel(),np.repeat(np.arange(n),4))),
                 shape=(32768,n)).tocsr()
    MT=M.T.tocsr()
    bound=int(np.max(4*np.bincount(E.ravel(),minlength=32768)))
    assert bound==348
    threshold=2*pow(bound+1,P_DEGREE)
    modulus=1;crt=None;prime=10000019;count=0
    for trial in range(max_primes):
        prime=int(nextprime(prime))
        residue=modulo_lanczos(M,MT,prime)
        if crt is None:crt=[0]*len(residue)
        inv=pow(modulus%prime,-1,prime)
        for j,value in enumerate(residue):
            t=((value-crt[j])%prime)*inv%prime
            crt[j]+=t*modulus
        modulus*=prime
        count+=1
        if count%10==0:
            print("BABEL21_SOURCE_CRT_PROGRESS",count,"bits",modulus.bit_length(),"need",threshold.bit_length(),flush=True)
        if modulus>threshold:break
    assert modulus>threshold and count==90,("proven coefficient bound not reached",count)
    polynomial=[int(a if a<=modulus//2 else a-modulus) for a in crt]
    assert polynomial[-1]==1 and polynomial[0]!=0
    document={"format":"BABEL8_INTEGER_KRYLOV_DEGREE4_CERTIFICATE_V1",
        "degree_of_recurrence":len(polynomial)-1,
        "normal_operator_row_sum_bound":bound,
        "theoretical_CRT_coefficient_bound_expression":
              f"({bound}+1)^{P_DEGREE}",
        "CRT_modulus_exceeds_twice_coefficient_bound":True,
        "CRT_modulus_digits":len(str(modulus)),
        "prime_count":count,
        "modular_exceptions":0,
        "number_of_distinct_row_products":n,
        "degree2_fourier_basis_size":len(basis),
        "polynomial_coefficients_low_to_high":polynomial}
    out=Path("babel8_DEGREE4_KRYLOV_RATIONAL_DUAL.json")
    out.write_text(json.dumps(document,separators=(",",":"),sort_keys=True)+"\n")
    digest=hashlib.sha256(out.read_bytes()).hexdigest()
    assert digest==EXPECTED_SHA,("reconstructed proof differs from archived exact proof",digest)
    print("BABEL21_REGENERATED_FROZEN_BABEL8_BYTE_SHA_PASS",digest,flush=True)
    vec=[0]*32768
    for step,c in enumerate(reversed(polynomial[1:])):
        vec=normal(vec,eq);vec[0]+=c
        if (step+1)%50==0:
            print("BABEL21_SOURCE_EXACT_INTEGER_HORNER",step+1,flush=True)
    check=normal(vec,eq)
    assert check[0]==-polynomial[0] and not any(check[1:]),"entire 32768-frequency Krylov identity failed"
    sign=-1 if polynomial[0]>0 else 1
    D=abs(polynomial[0])
    source_coeff={}
    direct=defaultdict(int)
    for a,b,c,d4 in eq:
        y=sign*(vec[a]+vec[b]+vec[c]+vec[d4])
        if y:
            rp=origins[(a,b,c,d4)]
            source_coeff[rp]=y
            for q in (a,b,c,d4):direct[q]+=y
    assert {q:v for q,v in direct.items() if v}=={0:D}
    print("BABEL21_SOURCE_ALL_FOURIER_PASS",len(source_coeff),len(str(D)),flush=True)
    return rows,labels,basis,source_coeff,digest,len(str(D))

def verify_seed(seed,rows,labels,basis,source_coeff):
    path=Path(f"babel21_SCL126_flip16_seed{seed}_source_phi.json.gz")
    with gzip.open(path,"rt") as f:doc=json.load(f)
    assert doc["base"]=="SCL126_flip16" and doc["seed"]==seed
    outcomes=[]
    for item in doc["annihilator_representatives"]:
        phi={(r,u):int(v) for r,u,v in item["source_phi_response"]}
        assert len(phi)==18
        reps={};count=0;dup=0
        for r,row in enumerate(rows):
            a,b,c=[labels[j] for j in row]
            for u in basis:
                signature=tuple(sorted((u,u^a,u^b,u^c)))
                value=phi.get((r,u),0)
                if signature in reps:
                    assert reps[signature]==value
                    dup+=1
                else:reps[signature]=value
                count+=1
        assert count==270522 and len(reps)==128013 and dup==142509
        pairing=sum(coeff*phi.get(rp,0) for rp,coeff in source_coeff.items())
        assert pairing==0,("target projection outside correction span",seed,item["component"],pairing)
        outcomes.append({"component":item["component"],
             "source_columns_checked":count,"distinct_signatures":len(reps),
             "equal_source_columns_checked":dup,
             "pairing":str(pairing),
             "anti_functional_support":len(item["cover_anti_left_functional"])})
        print("BABEL21_INDEPENDENT_RATIONAL_TARGET_PASS",seed,item["component"],flush=True)
    return {"seed":seed,"remaining_exact_rational_components":len(outcomes),
       "all_source_pairings_zero":True,"results":outcomes,
       "source_phi_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
       "complete_cover_correction_existence_given_previous_rank_witnesses":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--max-primes",type=int,default=110)
    args=p.parse_args()
    rows,labels,basis,x,digest,digits=regenerate(args.max_primes)
    seeds=[verify_seed(seed,rows,labels,basis,x) for seed in (20,37)]
    report={"format":"BABEL21_CLOUD_INDEPENDENT_SOURCE_AND_RESIDUAL_EXACT_V1",
       "base":"SCL126_flip16",
       "base_proof_sha256":digest,
       "source_positive_constant_digits":digits,
       "source_exact_all_frequency_integer_replay":"PASS",
       "remaining_components_total":sum(z["remaining_exact_rational_components"] for z in seeds),
       "source_target_compatibility_seed20_seed37":"PASS",
       "seed_results":seeds,
       "cover_explicit_coefficients_generated":False,
       "full_source_kerA_basis_enumerated":False,
       "universal_polynomial_degree_bound_proved":False,
       "P_equals_NP_proved":False}
    Path("babel21_INDEPENDENT_EXACT_FINAL.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("BABEL21_CLOUD_EXACT_FINAL",json.dumps({k:v for k,v in report.items() if k!="seed_results"},sort_keys=True),flush=True)
if __name__=="__main__":main()
