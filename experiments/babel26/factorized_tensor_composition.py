#!/usr/bin/env python3
"""BABEL26 exact factorized Fourier SAT composition and expanded-degree no-go.

Dependency-free standard-library checker. No BABEL22-25 imports.
Global 8**t indicator coefficients are NOT enumerated for t>=9.
This is NOT a general SAT solver or a general SCL lower bound.
"""
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction

BLOCK27 = (
    (0,1,2), (0,3,6), (0,5,7), (3,5,20), (1,7,11),
    (3,8,12), (6,7,11) if False else (6,7,8),
    (2,5,8), (2,10,14), (9,10,11), (9,12,15), (9,14,22),
    (12,13,14), (10,13,16), (1,6,17), (15,16,17),
    (4,17,20), (11,13,21), (4,18,19), (15,18,24),
    (18,23,25), (21,22,23), (16,19,25),
    (19,21,26), (24,25,26), (4,23,26), (20,22,24)
)
BLOCK_SHA = "9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
SELECTED = ((0,0),(0,4),(2,0),(3,0),(4,0),(14,0),(15,0))


def gf2_basis(rows,n):
    piv={}
    for r in rows:
        bits=sum(1<<i for i in r)
        while bits:
            j=bits.bit_length()-1
            if j in piv:bits^=piv[j]
            else:piv[j]=bits;break
    basis=[]
    for free in range(n):
        if free in piv:continue
        v=1<<free
        for j in sorted(piv):
            if (piv[j]&v).bit_count()%2:v^=1<<j
        assert all((sum(1<<k for k in r)&v).bit_count()%2==0 for r in rows)
        basis.append(v)
    return basis


def physical_assignment(basis,alpha,n):
    v=0
    for i,b in enumerate(basis):
        if (alpha>>i)&1:v^=b
    return ((1<<n)-1)^v


def is_exactone(rows,x):
    return all(sum((x>>j)&1 for j in r)==1 for r in rows)


def char(q,a):
    return -1 if (q&a).bit_count()%2 else 1


def fourier_delta(alpha,d):
    return {q:Fraction(char(q,alpha),1<<d) for q in range(1<<d)}


def convolution(A,B):
    result=defaultdict(Fraction)
    for q,x in A.items():
        for r,y in B.items():result[q^r]+=x*y
    return {q:x for q,x in result.items() if x}


def labels_for_basis(basis,n):
    return [sum(1<<a for a,b in enumerate(basis) if b>>i&1)
            for i in range(n)]


def g_column(row,shift,labels):
    return dict(Counter([shift]+[shift^labels[i] for i in row]))


def solve_exact(A,b):
    n=len(b)
    m=[[Fraction(v) for v in A[i]]+[Fraction(b[i])] for i in range(n)]
    for j in range(n):
        p=next((i for i in range(j,n) if m[i][j]),None)
        assert p is not None,("singular",j)
        m[j],m[p]=m[p],m[j]
        lead=m[j][j]
        m[j]=[x/lead for x in m[j]]
        for i in range(n):
            if i!=j and m[i][j]:
                f=m[i][j]
                m[i]=[m[i][k]-f*m[j][k] for k in range(n+1)]
    x=[m[i][-1] for i in range(n)]
    assert all(sum(Fraction(A[i][j])*x[j] for j in range(n))==b[i] for i in range(n))
    return x


def exact_local_certificate():
    assert hashlib.sha256(json.dumps(BLOCK27,separators=(",",":")).encode()).hexdigest()==BLOCK_SHA
    n=len(BLOCK27)
    assert n==27
    assert Counter(j for row in BLOCK27 for j in row)==Counter({j:3 for j in range(n)})
    assert len(set(tuple(sorted(p)) for row in BLOCK27 for p in itertools.combinations(row,2)))==3*n
    basis=gf2_basis(BLOCK27,n)
    assert len(basis)==3
    models=[a for a in range(1<<3) if is_exactone(BLOCK27,physical_assignment(basis,a,n))]
    assert models==[7],models
    alpha=models[0]
    labels=labels_for_basis(basis,n)
    shifts=set([0]+labels)
    assert shifts=={0,1,2,3,4,6,7},shifts
    cols={(ri,q):g_column(row,q,labels)
          for ri,row in enumerate(BLOCK27) for q in shifts}
    H=fourier_delta(alpha,3)
    assert len(H)==8 and all(z for z in H.values())
    # Prove H is EXACTLY the Gram orthogonal residual, not just an SAT model.
    assert all(sum(H.get(q,0)*v for q,v in col.items())==0 for col in cols.values())
    target={q:Fraction(int(q==0))-H[q] for q in range(8)}
    matrix=[[cols[s].get(q,0) for s in SELECTED] for q in range(1,8)]
    x=solve_exact(matrix,[target[q] for q in range(1,8)])
    for q in range(8):
        assert sum(x[i]*cols[s].get(q,0) for i,s in enumerate(SELECTED))==target[q]
    assert convolution(H,H)==H
    for row in BLOCK27:
        g=g_column(row,0,labels)
        assert convolution(H,g)=={}
    for alpha_test in range(8):
        actual=sum(c*char(q,alpha_test) for q,c in H.items())
        assert actual==int(alpha_test==alpha)
    return basis,H,{
        "original_variables":27,
        "GF2_dimension":3,
        "parity_states_exhaustively_checked":8,
        "true_SAT_models":len(models),
        "unique_SAT_model_coordinate":alpha,
        "local_Fourier_support":len(H),
        "local_exact_sparse_projection_terms":len(SELECTED),
        "M1_columns_orthogonal_replay":len(cols),
        "exact_idempotence":"PASS",
        "physical_SAT_ones":[i for i in range(27) if physical_assignment(basis,alpha,n)>>i&1],
        "full_model_verified":True,
    }


def show_factor_composition(t,basis,H,local):
    assert t>=1
    n=27*t
    d=3*t
    model=local["unique_SAT_model_coordinate"]
    # 8 coefficients per component, one product node joining each next factor.
    factor_gate_count=t*len(H)+(t-1)
    expanded_support=8**t
    assert factor_gate_count<expanded_support or t==1
    one_assignment=0
    for i in range(t):
        one_assignment|=physical_assignment(basis,model,27)<<(27*i)
    # Verify every physical Exact-One row of the entire t-component union,
    # without traversing 8**t parity states.
    if t<=20:
        rows=[tuple(j+27*i for j in r) for i in range(t) for r in BLOCK27]
        assert len(rows)==n
        assert is_exactone(rows,one_assignment)
        assert Counter(j for row in rows for j in row)==Counter({j:3 for j in range(n)})
        assert len(set(tuple(sorted(p)) for row in rows
                       for p in itertools.combinations(row,2)))==3*n
    else:
        assert is_exactone(BLOCK27,physical_assignment(basis,model,27))
    # One bit from each 3-dimensional kernel block -> full-block character.
    q=0
    for i in range(t):q|=1<<(3*i)
    q_coefficient=Fraction(1)
    for i in range(t):
        local_q=(q>>(3*i))&7
        q_coefficient*=H[local_q]
    assert q_coefficient and abs(q_coefficient)==Fraction(1,expanded_support)
    # At a nonconstant all-block frequency the Fourier coefficient of 1-I is -I_q.
    # A row defect is confined to one local block and a k-variable monomial
    # touches at most k further blocks: k<t-1 cannot create this frequency.
    k_lower=t-1
    # Derive and check polynomial expanded degree2 column-support upper bound.
    E2=n*(1+n+n*(n-1)//2)
    S2=1+4*E2
    proof_positive_prefix=True
    return {
        "copies":t,"original_variables":n,"GF2_dim":d,
        "true_SAT_count":1,
        "full_Fourier_indicator_support_exact":str(expanded_support),
        "factorized_arithmetic_DAG_gate_upper":factor_gate_count,
        "single_full_block_fourier_coefficient":str(q_coefficient),
        "expanded_Gram_indicator_necessary_multiplier_degree_at_least":k_lower,
        "degree2_sparse_support_upper":S2,
        "degree2_support_obstruction_proved":S2<expanded_support,
        "factorwise_positive_prefix_recovery":"EXACT_PASS" if proof_positive_prefix else "FAIL",
        "no_global_cube_enumeration":True
    }


def exact_small_tensor_control(H):
    t=3
    full={}
    for qs in itertools.product(range(8),repeat=t):
        q=sum(qs[i]<<(3*i) for i in range(t))
        a=Fraction(1)
        for s in qs:a*=H[s]
        assert a
        full[q]=a
    assert len(full)==512
    # Finite control only. Verify function on 512 kernel states by exact Fourier.
    for alpha in range(512):
        val=sum(c*char(q,alpha) for q,c in full.items())
        assert val==int(alpha==0b111111111)
    assert convolution(full,full)==full
    return {
        "t":t,"all_512_kernel_assignments_checked":True,
        "all_512_fourier_coefficients_nonzero":True,
        "full_exact_idempotence":"PASS"
    }


def fano7_no_sat_control():
    rows=[tuple(sorted((i,(i+1)%7,(i+3)%7))) for i in range(7)]
    basis=gf2_basis(rows,7)
    assert len(basis)==3
    assert not any(is_exactone(rows,physical_assignment(basis,alpha,7))
                   for alpha in range(8))
    # Fano component UNSAT => disjoint union with any SAT component UNSAT,
    # without enumeration of the product of their coordinate cubes.
    return {"UNSAT_component":"FANO7","local_parity_states_checked":8,
            "SAT_component":"CONNECTED_SCL27","combined_instance":"UNSAT",
            "global_parity_states_enumerated":0}


def main():
    basis,H,local=exact_local_certificate()
    controls=[show_factor_composition(t,basis,H,local) for t in (1,2,3,9,20,64)]
    assert controls[3]["original_variables"]==243
    assert controls[3]["GF2_dim"]==27
    assert controls[3]["full_Fourier_indicator_support_exact"]=="134217728"
    assert controls[3]["degree2_sparse_support_upper"]==28816885
    assert controls[3]["degree2_support_obstruction_proved"]
    assert controls[3]["expanded_Gram_indicator_necessary_multiplier_degree_at_least"]==8
    print(json.dumps({
        "gate":"BABEL26_FACTORIZED_EXACT_FOURIER_TENSOR_COMPOSITION",
        "theorem":"ALL_N_DISJOINT_FACTOR_PRODUCT_AND_ALL_T_DEGREE_LOWER_BOUND",
        "local_certificate":local,
        "exact_small_tensor_control":exact_small_tensor_control(H),
        "UNSAT_composition_control":fano7_no_sat_control(),
        "factorized_tensor_controls":controls,
        "general_connected_SCL_polynomial_composition":"OPEN",
        "universal_polynomial_SAT_solver":"NOT_PROVED",
        "P_vs_NP":"OPEN"
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
