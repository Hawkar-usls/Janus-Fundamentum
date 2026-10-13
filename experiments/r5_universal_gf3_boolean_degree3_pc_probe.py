#!/usr/bin/env python3
"""R5 exact ORIGINAL-source degree-3 Boolean PC probe over F3.

Frozen multilinear proof system:
- source generators E_i(x)=x_a+x_b+x_c-1 for every ORIGINAL ExactOne
  row (with Boolean idempotency x_i^2=x_i);
- all degree<=3 generators E_i * x_S for |S|<=2;
- exact GF3 linear span in multilinear monomials |S|<=3.

If 1 absent from span, construct and INDEPENDENTLY source-replay
a dual linear functional y with y(1)=1 and y(E_i*x_S)=0 for
ALL original source clauses and allowed multipliers. This is a
finite exact certificate of NO refutation IN THIS FROZEN
degree-3 polynomial calculus, not a SAT certificate.

If 1 appears in span, do NOT claim a certified UNSAT result
until a source-original coefficient combination is separately
reconstructed and verified. Resource guards produce UNKNOWN.

This directly tests Petersen SCL45 vs the deliberately easy
connected triple-Fano21 source. No general PC lower bound or
P!=NP/P=NP result follows from any one finite instance.
"""
from __future__ import annotations
from itertools import combinations
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def multilinear_monomials(n,limit_degree):
    monomials=[()]
    for degree in range(1,limit_degree+1):
        monomials.extend(combinations(range(n),degree))
    keys={m:i for i,m in enumerate(monomials)}
    assert len(keys)==len(monomials)
    return monomials,keys


def source_degree3_generators(rows,n,monomials,ids):
    choices=monomials[:1+n+n*(n-1)//2]
    for rid,row in enumerate(rows):
        for multiplier in choices:
            poly={}
            def add(mon,c):
                key=ids[mon]
                val=(poly.get(key,0)+c)%3
                if val:poly[key]=val
                elif key in poly:del poly[key]
            add(multiplier,-1)
            for v in row:
                if v in multiplier:
                    # Boolean quotient x_v^2=x_v.
                    out=multiplier
                else:
                    out=tuple(sorted(multiplier+(v,)))
                add(out,1)
            yield (rid,multiplier),poly


def subtract_scaled(poly,basis,coef):
    for j,v in basis.items():
        res=(poly.get(j,0)-coef*v)%3
        if res:poly[j]=res
        elif j in poly:del poly[j]


def verify_dual_source(rows,n,dual,monos,ids):
    rows=validate_sparse(rows,n)
    assert dual.get(0,0)==1
    assert all(0<=j<len(monos) and c in (1,2)
               for j,c in dual.items())
    number=0
    for _gid,g in source_degree3_generators(rows,n,monos,ids):
        assert sum(dual.get(j,0)*c for j,c in g.items())%3==0
        number+=1
    assert number==n*(1+n+n*(n-1)//2)
    return number


def degree3_source_span(rows,n,max_updates=45000000):
    rows=validate_sparse(rows,n)
    monomials,ids=multilinear_monomials(n,3)
    basis={}
    visited=0
    updates=0
    for gid,gen in source_degree3_generators(rows,n,monomials,ids):
        visited+=1
        poly=dict(gen)
        while poly:
            pivot=max(poly)
            if pivot not in basis:
                coef=poly[pivot]
                if coef==2:
                    poly={k:(2*v)%3 for k,v in poly.items()}
                assert poly[pivot]==1
                basis[pivot]=poly
                if pivot==0:
                    return {"status":"DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED",
                            "n":n,"rank":len(basis),
                            "generators":visited,"updates":updates}
                break
            coef=poly[pivot]
            updates+=len(basis[pivot])
            if updates>max_updates:
                return {"status":"UNKNOWN_RESOURCE_LIMIT",
                        "n":n,"rank":len(basis),
                        "generators":visited,"updates":updates}
            subtract_scaled(poly,basis[pivot],coef)
    assert 0 not in basis
    # Construct exact dual as in degree-2 method. Rows have unit
    # HIGHEST pivot. Assign y(1)=1, other free coords0.
    values={0:1}
    for pivot in sorted(basis):
        row=basis[pivot]
        assert row[pivot]==1 and all(k<=pivot for k in row)
        values[pivot]=(-sum(c*values.get(j,0)
                             for j,c in row.items() if j!=pivot))%3
    dual={j:c for j,c in values.items() if c}
    verify_dual_source(rows,n,dual,monomials,ids)
    return {"status":"DEGREE3_NO_REFUTATION_DUAL_CERTIFIED",
            "n":n,"rank":len(basis),
            "ambient_dim":len(monomials),
            "generators":visited,"updates":updates,
            "dual_support":len(dual),
            "dual":dual}


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_triple_fano_connected_divisible_high_girth_unsat import (
        triple_cyclic_source_glue,two_gadget_sat21_comparison
    )
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,petersen_graph
    )

    U,n,_=triple_cyclic_source_glue(cyclic(7),7)
    S,source_witnesses=two_gadget_sat21_comparison()
    assert len(source_witnesses)==2
    P,m,_,_=make_scl(petersen_graph())
    for name,rows,size in (
        ("TRIPLE_FANO_UNSAT21",U,n),
        ("TWO_GADGET_SAT21",S,21),
        ("PETERSEN_SCL45",P,m)
    ):
        limit=45000000 if size<=21 else 60000000
        result=degree3_source_span(rows,size,max_updates=limit)
        print(f"ORIGINAL_{name}_GF3_BOOLEAN_PC_DEGREE3="
              f"{result['status']} n={size} "
              f"rank={result['rank']} "
              f"generators={result['generators']} "
              f"updates={result['updates']} "
              f"dual_support={result.get('dual_support','NA')}",
              flush=True)
        if name=="TWO_GADGET_SAT21":
            assert result["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED"
        if name=="TRIPLE_FANO_UNSAT21":
            assert result["status"] in (
                "DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED",
                "UNKNOWN_RESOURCE_LIMIT"
            )
        if name=="PETERSEN_SCL45":
            # All claims below conditioned on an independently
            # verified dual; timeouts remain explicitly UNKNOWN.
            if result["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
                print("PETERSEN_SCL45_EXACT_SOURCE_DEGREE3_DUAL="
                      "PROVED",flush=True)
            elif result["status"]=="DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED":
                print("PETERSEN_SCL45_DEGREE3_REFUTATION_CANDIDATE="
                      "REQUIRES_INDEPENDENT_CERTIFICATE",flush=True)
            else:
                print("PETERSEN_SCL45_DEGREE3_RESULT="
                      "UNKNOWN_RESOURCE_LIMIT",flush=True)

    print("DEGREE3_GF3_BOOLEAN_SOURCE_SPAN=EXACT_WHEN_COMPLETED")
    print("GENERAL_UNIFORM_POLY_DEGREE_BOOLEAN_PC=NOT_PROVED")
    print("UNIVERSAL_POLY_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
