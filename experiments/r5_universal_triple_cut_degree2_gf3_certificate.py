#!/usr/bin/env python3
"""R5 proof audit: mod-3 relaxation fails on matched SAT21/UNSAT21,
yet a degree-2 F3 Nullstellensatz CERTIFICATE refutes ALL threefold
cyclic Fano-cover sources (including connected large girth, 3|n).

Scientific scope: This is a new original-source short algebraic proof
for one infinite family, NOT a polynomial all-SCL SAT solver.

Original row generators are E_i(x) = sum_{v in row_i} x_v - 1.
Boolean generators are G_v(x) = x_v^2 - x_v.

For 3 copies of any connected legal m-variable SCL with m%3=r!=0
cyclically reconnected through one original cut Tanner incidence,
put B_i = variable at original cut in copy i, indices mod 3.

SUM of E_i generators over original rows of COPY i, over F3:
  F_i = B_(i+1) - B_i - r.
This is checked entirely from original source row provenance and
the fact all other original columns are cubic inside their copy.

For any r in F3*, write c=2r and
  T_i = (G_(i+1)-G_i) - F_i*(B_(i+1)+B_i-1+r).
Then the following is a polynomial IDENTITY over F3, degree<=2:
  T_i = c*B_i + r*(r-1).
Therefore
  1 = r^-1 * (c^-1*(T_1-T_0) - F_0)
in the polynomial ring F3[B0,B1,B2].

Substitute the F_i definitions as SUMS of ORIGINAL Exact-One
row generators. This becomes an actual Nullstellensatz
refutation (1 in the ideal), degree at most 2, and the number
of source clauses used is at most 2m plus 3 Boolean generators,
i.e. O(n) certificate size. For EVERY base tower level m,
including m=1792 and higher, this remains a polynomial-size
independently verifiable source UNSAT certificate!

The simple *linear* relaxation Ax=1 over F3 is nevertheless
CONSISTENT for the explicit connected SCL21 UNSAT source:
the obstruction requires BOOLEAN equations G_v=0.
The corresponding connected SCL21 SAT comparator also has
GF3 solution. Hence GF3 linear feasibility is not a complete
universal SCL SAT test; the modular-cut example is easy at
QUADRATIC degree and cannot be advertised as a difficult
universal algebraic-proof benchmark.

No P=NP or P!=NP claimed.
"""
from __future__ import annotations
from collections import Counter

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
from r5_universal_triple_fano_connected_divisible_high_girth_unsat import (
    triple_cyclic_source_glue,
    independently_replay_source_glue,
    group_source_rows_by_original_block,
    two_gadget_sat21_comparison,
)
from r5_universal_loop_high_girth_fano_homology_cover_nogo import (
    binary_homology_cover
)


# A tiny sparse F3 polynomial ring in the THREE original boundary
# source variables B0,B1,B2; tuple monomial lengths <=2.
def P(terms):
    out={}
    for mon,coef in terms.items():
        mon=tuple(sorted(mon))
        coef=coef%3
        if coef:
            out[mon]=coef
    return out


def const(c):
    return P({():c})


def var(i):
    assert i in (0,1,2)
    return P({(i,):1})


def add(a,b):
    d=dict(a)
    for m,c in b.items():
        d[m]=(d.get(m,0)+c)%3
    return P(d)


def scale(a,c):
    return P({m:v*c for m,v in a.items()})


def sub(a,b):
    return add(a,scale(b,-1))


def mul(a,b):
    d={}
    for ma,ca in a.items():
        for mb,cb in b.items():
            mon=tuple(sorted(ma+mb))
            assert len(mon)<=2,"refutation degree >2"
            d[mon]=(d.get(mon,0)+ca*cb)%3
    return P(d)


def mod3_inverse(x):
    v=x%3
    assert v in (1,2)
    return v


def boundary_identity(r):
    """Verify a completely expanded source-constant polynomial ID.

    No appeal to a symbolic computer algebra backend.
    """
    assert r in (1,2)
    b=[var(i) for i in range(3)]
    f=[]
    t=[]
    c=2*r%3
    for i in (0,1):
        a=b[i+1]
        old=b[i]
        fi=sub(sub(a,old),const(r))
        f.append(fi)
        gi=sub(mul(a,a),a)
        hi=sub(mul(old,old),old)
        ti=sub(sub(gi,hi),mul(fi,add(add(a,old),const(r-1))))
        expected=add(scale(old,c),const(r*(r-1)))
        assert ti==expected,(r,i,ti,expected)
        t.append(ti)
    refutation=scale(
        sub(scale(sub(t[1],t[0]),mod3_inverse(c)),f[0]),
        mod3_inverse(r)
    )
    assert refutation==const(1),(r,refutation)
    return {
        "charge_residue":r,
        "boundary_constant_polynomial":refutation,
        "max_degree":2,
        "source_generators_used":"two_original_blocks_plus_three_boundary_boolean",
        "source_refutation":"NULLSTELLENSATZ_DEGREE_AT_MOST_TWO",
    }


def source_block_generator_check(base,m,joined,n,cert):
    """Independently prove sum of ACTUAL ORIGINAL row equations has
    the claimed coefficient vector over F3, for each block.

    Row IDs are canonically sorted by validator, so do not assume
    they stayed contiguous after 3-component gluing.
    """
    assert independently_replay_source_glue(base,m,joined,n,cert)
    v=cert["cut_original_variable"]
    block_rows=group_source_rows_by_original_block(joined,m)
    assert len(block_rows)==3 and n==3*m
    for i,part in enumerate(block_rows):
        incidence=Counter(x for row in part for x in row)
        assert len(part)==m
        expected={i*m+j:(2 if j==v else 3) for j in range(m)}
        expected[((i+1)%3)*m+v]=1
        assert dict(incidence)==expected,(i,incidence,expected)
        # Modulo 3 all 3-fold occurrences vanish, 2*B_i=-B_i.
        observed={j:c%3 for j,c in incidence.items() if c%3}
        wanted={i*m+v:2,((i+1)%3)*m+v:1}
        assert observed==wanted
        # Each exact source E_row=sum x_v-1, so the constant
        # term of the block sum is -m=-r mod3.
        assert (-len(part))%3==(-m)%3
    return True


def linear_mod3_solve(rows,n):
    """Exact Gaussian elimination in F3; finite small controls only.

    A source-level solution to Ax=1 over F3 is NOT necessarily
    an original BOOLEAN Exact-One witness.
    """
    rows=validate_sparse(rows,n)
    assert n<=45
    A=[[int(j in row) for j in range(n)]+[1] for row in rows]
    pivots=[]
    k=0
    for j in range(n):
        p=next((i for i in range(k,n) if A[i][j]),None)
        if p is None:
            continue
        A[k],A[p]=A[p],A[k]
        inv=mod3_inverse(A[k][j])
        A[k]=[(x*inv)%3 for x in A[k]]
        for i in range(n):
            if i!=k and A[i][j]:
                coef=A[i][j]
                A[i]=[(x-coef*y)%3 for x,y in zip(A[i],A[k])]
        pivots.append(j)
        k+=1
    inconsistent=any(not any(r[:-1]) and r[-1] for r in A)
    if inconsistent:
        return {"status":"INCONSISTENT_GF3","rank":k,
                "kernel_dim":n-k,"solution":None}
    x=[0]*n
    for i,j in enumerate(pivots):
        x[j]=A[i][-1]
    assert all(sum(x[v] for v in row)%3==1 for row in rows)
    return {"status":"CONSISTENT_GF3","rank":k,
            "kernel_dim":n-k,"solution":tuple(x)}


def prove_original_quadratic_unsat(base,m,joined,n,cert):
    base=validate_sparse(base,m)
    joined=validate_sparse(joined,n)
    assert m%3 in (1,2)
    assert source_block_generator_check(base,m,joined,n,cert)
    witness=boundary_identity(m%3)
    assert witness["max_degree"]==2
    # The certificate identity only uses F0 and F1,
    # each a sum of m original row generators and the
    # Boolean equations of the 3 cut original variables.
    witness["base_source_n"]=m
    witness["joined_source_n"]=n
    witness["source_clause_bound"]=2*m
    witness["source_variable_boolean_bound"]=3
    return witness


def main():
    for residue in (1,2):
        b=boundary_identity(residue)
        print(f"CYCLIC_SOURCE_BOUNDARY_CHARGE_{residue}_"
              f"F3_NULLSTELLENSATZ_DEGREE2=PROVED",flush=True)

    base=cyclic(7)
    assert linear_mod3_solve(base,7)["status"]=="INCONSISTENT_GF3"

    U,n,cert=triple_cyclic_source_glue(base,7)
    proof=prove_original_quadratic_unsat(base,7,U,n,cert)
    unsat_field=linear_mod3_solve(U,n)
    assert unsat_field["status"]=="CONSISTENT_GF3"
    assert any(x==2 for x in unsat_field["solution"])
    print(f"CONNECTED_UNSAT_SCL21_GF3_LINEAR_RELAXATION="
          f"CONSISTENT rank={unsat_field['rank']} "
          f"BOOLEANS_REQUIRE_QUADRATIC_REFUTATION",flush=True)

    S,w=two_gadget_sat21_comparison()
    assert len(w)==2
    sat_field=linear_mod3_solve(S,21)
    assert sat_field["status"]=="CONSISTENT_GF3"
    assert all(sum(x[v] for v in row)==1 for x in w for row in S)
    print(f"CONNECTED_SAT_SCL21_GF3_LINEAR_RELAXATION="
          f"CONSISTENT rank={sat_field['rank']}",flush=True)
    print("SAME_SIZE_CONNECTED_GF3_CONSISTENT_SAT2_VS_UNSAT0=PROVED",
          flush=True)

    lifted,m,meta=binary_homology_cover(base,7)
    assert m==1792 and meta["sheets"]==256
    large,n,cert=triple_cyclic_source_glue(lifted,m)
    assert n==5376 and n%3==0
    source_proof=prove_original_quadratic_unsat(
        lifted,m,large,n,cert
    )
    assert source_proof["source_clause_bound"]==3584
    print("HIGH_GIRTH_CONNECTED_SCL5376_SOURCE_F3_QUADRATIC_UNSAT="
          "PROOF_VERIFIED_USING_3584_ROW_GENERATORS_AND_3_BOOL_GENERATORS",
          flush=True)

    # Tamper with block composition while keeping certificate metadata.
    forged=list(large)
    forged[0]=large[1]
    try:
        prove_original_quadratic_unsat(
            lifted,m,tuple(forged),n,cert
        )
    except (AssertionError,ValueError):
        print("FORGED_QUADRATIC_SOURCE_CERTIFICATE_REJECTED=PASS",
              flush=True)
    else:
        raise AssertionError("forged source accepted")

    print("ALL_TRIPLE_FANO_HOMOLOGY_TOWER_QUADRATIC_F3_UNSAT=PROVED")
    print("TRIPLE_FANO_FAMILY_NOT_A_HARD_ALGEBRAIC_ZERO_TEST_BENCHMARK")
    print("GENERAL_ALL_SCL_DEGREE2_OR_POLY_DEGREE_NULLSTELLENSATZ=NOT_PROVED")
    print("UNIFORM_POLY_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
