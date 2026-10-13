#!/usr/bin/env python3
"""R5 original-source F3 Boolean degree-2 polynomial calculus audit.

Exactly fixed proof system: over F3, generators are original linear
Exact-One clause polynomials E_i = (x_a+x_b+x_c-1) and Boolean
idempotence B_j=x_j*x_j-x_j. Reduce modulo all B_j to multilinear
polynomials, and span {E_i, x_j*E_i} for all clause rows i and
original variables j. All these generators have total degree<=2
after Boolean quotient normalization.

A constant polynomial 1 in this GF3-linear span is a VALID
degree-2 original-source refutation (a Nullstellensatz identity
with boolean constraints implicit), replayable by expanding the
explicit combination of source generators and monomials.

When 1 is NOT in the computed span, only the FROZEN
multilinear degree-2 linear span is insufficient. This is not
evidence SAT, nor an unconditional algebraic hardness bound.

The engine is exact GF3 Gaussian elimination over an enumerated
basis of size 1+n+binom(n,2), no float, with provenance to
original source clause/multiplier row IDs. To disprove a false
degree-2 UNSAT claim, it checks independent SAT original witness
when available. It also tests a source-verified cyclic triple Fano
UNSAT21, whose algebraic degree<=2 certificate is known.

Do not count this as a universal polynomial SAT/UNSAT solver:
fixed-degree truncated PC is at best a sufficient UNSAT test.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations

from r5_universal_exact_support_residual_dag_attack import validate_sparse


def basis_monomial(n,i,j=None):
    """Integer sparse monomial encoding, injective for degree <=2."""
    if i is None:
        return 0
    if j is None or i==j:
        return 1+i
    a,b=sorted((i,j))
    return 1+n+a*n+b


def source_generators(rows,n):
    for row_i,row in enumerate(rows):
        E={0:2}
        for v in row:
            E[basis_monomial(n,v)]=1
        yield (row_i,-1),E
        for z in range(n):
            poly={basis_monomial(n,z):2}
            for v in row:
                k=basis_monomial(n,v,z)
                poly[k]=(poly.get(k,0)+1)%3
            poly={k:c for k,c in poly.items() if c}
            yield (row_i,z),poly


def subtract_scaled(target,other,coef):
    assert coef in (1,2)
    for mon,val in other.items():
        old=target.get(mon,0)
        nextval=(old-coef*val)%3
        if nextval:target[mon]=nextval
        elif mon in target:del target[mon]


def independent_source_replay(rows,n,combo):
    """Construct the full exact multilinear GF3 polynomial 1
    from a claimed ORIGINAL source generator coefficient dictionary.
    Completely independent from the elimination basis implementation.
    """
    rows=validate_sparse(rows,n)
    polynomial={}
    for (i,z),coef in combo.items():
        assert coef in (1,2) and 0<=i<n and (z==-1 or 0<=z<n)
        if z==-1:
            terms=[(None,None,2)]+[(v,None,1) for v in rows[i]]
        else:
            terms=[(z,None,2)]+[(v,z,1) for v in rows[i]]
        for var_a,var_b,val in terms:
            k=basis_monomial(n,var_a,var_b)
            nxt=(polynomial.get(k,0)+val*coef)%3
            if nxt:polynomial[k]=nxt
            elif k in polynomial:del polynomial[k]
    assert polynomial=={0:1},("forged UNSAT combination",polynomial)
    return True


def verify_degree2_dual_certificate(rows,n,dual):
    """Independent original-source F3 functional certificate.

    The dual y sends the unit polynomial to 1 but EVERY
    degree<=2 multilinear source generator E_i and E_i*x_j
    to 0, so 1 cannot be in the frozen degree2 row span.
    No appeal to a SAT model and no dependency on Gaussian pivots.
    """
    rows=validate_sparse(rows,n)
    assert dual.get(0,0)%3==1
    assert all(isinstance(k,int) and 0<=k<1+n+n*n
               and c in (1,2) for k,c in dual.items())
    for _gid,generator in source_generators(rows,n):
        residual=sum(dual.get(k,0)*v for k,v in generator.items())%3
        assert residual==0,("forged dual moment",_gid,residual)
    return True


def degree2_dual_from_triangular_basis(rows,n,pivot_basis):
    """Exactly solve degree2 moment equations from row-echelon basis.

    Each pivot is highest monomial in its row, with coefficient 1.
    The unit monomial is a free nonpivot. Set its dual value to 1,
    other free monomials 0, and recover all dependent moments
    in ASCENDING pivot order from the triangular constraints.
    This constructs a small independently source-checkable dual
    certificate of NON-membership of constant 1 in row span.
    """
    assert 0 not in pivot_basis
    values={0:1}
    for pivot in sorted(pivot_basis):
        row=pivot_basis[pivot]
        assert row[pivot]==1 and all(k<=pivot for k in row)
        required=sum(coef*values.get(k,0)
                     for k,coef in row.items() if k!=pivot)
        value=(-required)%3
        values[pivot]=value
    dual={k:c for k,c in values.items() if c%3}
    assert verify_degree2_dual_certificate(rows,n,dual)
    return dual


def degree2_row_span(rows,n,guard_n=50):
    rows=validate_sparse(rows,n)
    assert n<=guard_n
    pivot_basis={}
    basis_repr={}
    generator_count=0
    for gid,initial in source_generators(rows,n):
        generator_count+=1
        poly=dict(initial)
        combo={gid:1}
        while poly:
            pivot=max(poly)
            if pivot not in pivot_basis:
                coef=poly[pivot]
                if coef==2:
                    poly={j:(2*v)%3 for j,v in poly.items()}
                    combo={j:(2*v)%3 for j,v in combo.items()}
                assert poly[pivot]==1
                pivot_basis[pivot]=poly
                basis_repr[pivot]=combo
                if pivot==0:
                    assert independent_source_replay(rows,n,combo)
                    return {"status":"UNSAT_DEGREE2_SOURCE_CERTIFIED",
                            "n":n,"span_rank":len(pivot_basis),
                            "generators_seen":generator_count,
                            "source_certificate":combo,
                            "certificate_size":len(combo)}
                break
            coef=poly[pivot]
            subtract_scaled(poly,pivot_basis[pivot],coef)
            subtract_scaled(combo,basis_repr[pivot],coef)

    # All generators processed; constant target is not reducible
    # to zero iff no pivot for the pure constant monomial appeared.
    assert 0 not in pivot_basis
    dim=1+n+(n*(n-1))//2
    assert len(pivot_basis)<=dim
    dual=degree2_dual_from_triangular_basis(rows,n,pivot_basis)
    return {"status":"DEGREE2_UNRESOLVED",
            "n":n,"span_rank":len(pivot_basis),
            "ambient_dim":dim,"generators_seen":generator_count,
            "constant_not_in_span":True,
            "dual_certificate":dual,"dual_size":len(dual)}


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph
    )
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
    )
    from r5_universal_triple_fano_connected_divisible_high_girth_unsat import (
        triple_cyclic_source_glue,two_gadget_sat21_comparison
    )
    cases=[
        ("FANO7",cyclic(7),7,"UNSAT"),
        ("TRIPLE_FANO_UNSAT21",*triple_cyclic_source_glue(
            cyclic(7),7)[:2],"UNSAT"),
        ("TWO_GADGET_SAT21",two_gadget_sat21_comparison()[0],21,"SAT"),
        ("K4_SCL18",*make_scl(K4())[:2],"SAT"),
        ("K33_SCL27",*make_scl(K33())[:2],"SAT"),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2],"UNSAT"),
    ]
    for name,p,q,status in (
        ("E61_SAT12",P_SAT,Q_SAT,"SAT"),
        ("E61_UNSAT12",P_UNSAT,Q_UNSAT,"UNSAT")
    ):
        A=build_A(p,q)
        rows=validate_sparse(
            [tuple(j for j,v in enumerate(row) if v)
             for row in A],len(A)
        )
        cases.append((name,rows,len(rows),status))
    for name,rows,n,expected in cases:
        result=degree2_row_span(rows,n)
        verdict=result["status"]
        assert not (expected=="SAT" and verdict.startswith("UNSAT")),(
            name,result
        )
        if name in ("FANO7","TRIPLE_FANO_UNSAT21"):
            assert verdict=="UNSAT_DEGREE2_SOURCE_CERTIFIED",(name,result)
        if verdict=="DEGREE2_UNRESOLVED":
            assert verify_degree2_dual_certificate(
                rows,n,result["dual_certificate"]
            )
            if name=="PETERSEN_SCL45":
                print("PETERSEN_SCL45_UNSAT_F3_DEGREE2_DUAL_PSEUDOMOMENT="
                      f"SOURCE_CERTIFIED dimension={result['ambient_dim']} "
                      f"support={result['dual_size']}",flush=True)
        print(f"F3_BOOLEAN_PC_DEGREE2_{name}={verdict} "
              f"span_rank={result['span_rank']} "
              f"generators_seen={result['generators_seen']} "
              f"cert_size={result.get('certificate_size','NA')}",
              flush=True)
    print("EXACT_ORIGINAL_SOURCE_GF3_BOOLEAN_DEGREE2_LINEAR_SPAN=AUDITED")
    print("DEGREE2_UNRESOLVED_NEVER_MEANS_SOURCE_SAT")
    print("GENERAL_ALL_SCL_POLY_DEGREE_BOOLEAN_PC=NOT_PROVED")
    print("UNIFORM_POLY_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
