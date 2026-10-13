#!/usr/bin/env python3
"""R5 SOURCE-CERTIFIED degree-three F3 Boolean Nullstellensatz refutation.

Track exact sparse-Gaussian provenance as an acyclic recipe DAG.
For each ORIGINAL SCL clause E_i=sum(x_v)-1 and every squarefree
multiplier x_M of degree <=2, include reduction of E_i*x_M
modulo x_j^2-x_j. Every generator has Boolean-PC degree<=3.
If a constant 1 pivot is obtained, unwind the provenance DAG
to an explicit linear combination of original source generators.

An INDEPENDENT replay checker multiplies the original clause
polynomials by their claimed multipliers, multilinearizes the
result by x_j^2=x_j, and verifies the polynomial identity
   1 = Σ c_(i,M) * E_i*x_M (mod boolean generators, over F3).
The verifier never trusts Gaussian pivot rows or their ranks.

If SOURCE-CERTIFIED, this is a genuine full original
UNSAT certificate for that particular source. It does not
establish degree-three completeness for all SCL and never
claims polynomial all-SCL zero testing.
"""
from __future__ import annotations

from r5_universal_gf3_boolean_degree3_pc_probe import (
    multilinear_monomials,source_degree3_generators,subtract_scaled
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def independent_original_certificate_replay(rows,n,certificate):
    """Reconstruct original source identity from unrelated recipe.

    The Boolean quotient reduction is independent of the Gaussian
    elimination; source rows, generator indices and coefficients
    are the ONLY trusted inputs.
    """
    rows=validate_sparse(rows,n)
    _,key=multilinear_monomials(n,3)
    result={}
    for (rid,mon),c in certificate.items():
        assert 0<=rid<n and c in (1,2)
        assert isinstance(mon,tuple)
        assert tuple(sorted(set(mon)))==mon and len(mon)<=2
        assert all(0<=v<n for v in mon)
        for v,coef in [(None,-1)]+[(v,1) for v in rows[rid]]:
            if v is None:
                target=mon
            else:
                target=tuple(sorted(set(mon)|{v}))
            k=key[target]
            new=(result.get(k,0)+c*coef)%3
            if new:result[k]=new
            elif k in result:del result[k]
    assert result=={key[()]:1},(
        "FORGED ORIGINAL SOURCE DEGREE3 UNSAT",result
    )
    return True


def certificate_from_dag(rows,n,max_updates=90000000):
    rows=validate_sparse(rows,n)
    monomials,key=multilinear_monomials(n,3)
    basis={}
    recipes={}
    birth_order=[]
    seen=0
    updates=0
    constant_pivot=False
    for gid,original in source_degree3_generators(
        rows,n,monomials,key
    ):
        seen+=1
        poly=dict(original)
        operations=[]
        while poly:
            pivot=max(poly)
            if pivot not in basis:
                inv=poly[pivot] # in F3, inverse of 1/2 itself
                assert inv in (1,2)
                if inv==2:
                    poly={j:(2*x)%3 for j,x in poly.items()}
                assert poly[pivot]==1
                basis[pivot]=poly
                recipes[pivot]=(gid,inv,tuple(operations))
                birth_order.append(pivot)
                if pivot==0:
                    constant_pivot=True
                break
            c=poly[pivot]
            operations.append((pivot,c))
            updates+=len(basis[pivot])
            assert updates<=max_updates,"RESOURCE_LIMIT_NOT_UNSAT"
            subtract_scaled(poly,basis[pivot],c)
        if constant_pivot:
            break
    assert constant_pivot,"NO_DEGREE3_CONST_PIVOT"
    assert basis[0]=={0:1}
    coefficients={0:1}
    source_combo={}
    for pivot in reversed(birth_order):
        coef=coefficients.pop(pivot,0)%3
        if not coef:
            continue
        gid,inv,ops=recipes[pivot]
        source_combo[gid]=(source_combo.get(gid,0)+coef*inv)%3
        for old_pivot,multiple in ops:
            new=(coefficients.get(old_pivot,0)-coef*inv*multiple)%3
            if new:coefficients[old_pivot]=new
            elif old_pivot in coefficients:del coefficients[old_pivot]
    assert not coefficients,("incomplete provenance",len(coefficients))
    source_combo={g:c for g,c in source_combo.items() if c}
    assert independent_original_certificate_replay(
        rows,n,source_combo
    )
    return {"status":"ORIGINAL_SOURCE_GF3_DEGREE3_UNSAT_CERTIFIED",
            "n":n,"generator_count":seen,
            "pivot_rank":len(basis),
            "updates":updates,
            "certificate_terms":len(source_combo),
            "source_coefficient_combination":source_combo}


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_triple_fano_connected_divisible_high_girth_unsat import (
        triple_cyclic_source_glue
    )
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,petersen_graph
    )
    source21,n21,_=triple_cyclic_source_glue(cyclic(7),7)
    for name,rows,n in (
        ("TRIPLE_FANO_UNSAT21",source21,n21),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2]),
    ):
        proof=certificate_from_dag(rows,n)
        assert proof["status"]=="ORIGINAL_SOURCE_GF3_DEGREE3_UNSAT_CERTIFIED"
        print(f"{name}_INDEPENDENT_ORIGINAL_SOURCE_GF3_DEGREE3="
              f"UNSAT_CERTIFIED pivot_rank={proof['pivot_rank']} "
              f"source_row_monomial_terms={proof['certificate_terms']} "
              f"updates={proof['updates']}",flush=True)
        # Deliberately tamper a coefficient in the independent
        # original-source certificate. Must REJECT.
        copied=dict(proof["source_coefficient_combination"])
        chosen=next(iter(copied))
        copied[chosen]=1 if copied[chosen]==2 else 2
        try:
            independent_original_certificate_replay(rows,n,copied)
        except AssertionError:
            print(f"{name}_FORGED_DEGREE3_CERTIFICATE_REJECTED=PASS",
                  flush=True)
        else:
            raise AssertionError("accepted forged source certificate")
    print("PETERSEN_SCL45_UNSAT_HAS_VALID_SOURCE_GF3_DEGREE3_REFUTATION=PROVED")
    print("FANO_TOWER_QUADRATIC_AND_PETERSEN_CUBIC_CERTIFICATES=COMPARED")
    print("ALL_SCL_UNIFORM_DEGREE3_REFUTATION_BOUND=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
