#!/usr/bin/env python3
"""E129 cover tower: uniformly UNSAT, ACTUAL visited ExactSupport-DAG stress.

For every rationally invertible square cubic base A and any r-sheet
incidence cover L, a Boolean Exact-One solution yields A*y=r*1,
where y_j is the integer count of selected variables in column fibre j.
As A*1=3*1, uniqueness gives y=(r/3)*1, impossible if 3 does not
divide r. All powers of 2 are therefore UNSAT.

This theorem is from E129, not rediscovered. Our NEW finite experiment:
build seeded iterated 2-lifts of its explicit det(A)=36 legal q12 base,
verify the complete fibre-cover map, and measure the actual UNIQUE
memoized residual states consumed by the exact frozen DAG algorithm.
Always distinguish a budget-limited UNKNOWN from proven UNSAT.

Scientific gate: no extrapolation from finite sizes to 2^Omega(n) or
to n^O(1). A proof-size transfer theorem would still be needed.
"""
from __future__ import annotations

from random import Random

from r5_e129_invertible_base_cover_unsat_gauge_clean_seed import (
    base_matrix, det_bareiss
)
from r5_universal_exact_support_2lift_visited_dag_frontier import two_lift
from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse, ExactSupportResidualDAG_sparse
)


def sparse_base():
    A=base_matrix()
    assert det_bareiss(A)==36
    n=len(A)
    rows=validate_sparse([
        tuple(j for j,x in enumerate(row) if x) for row in A
    ],n)
    return rows,n


def assert_exact_cover_map(rows,n,degree,base_rows,base_n):
    """Every lift check fibre projects bijectively to all source incidences."""
    assert n==degree*base_n
    names={row:i for i,row in enumerate(base_rows)}
    origin_counts=[0]*base_n
    for row in rows:
        roots=tuple(sorted(j//degree for j in row))
        assert roots in names
        origin_counts[names[roots]]+=1
    assert all(num==degree for num in origin_counts)
    for ri,base_row in enumerate(base_rows):
        lifted_rows=[
            row for row in rows
            if tuple(sorted(j//degree for j in row))==base_row
        ]
        assert len(lifted_rows)==degree
        for v in base_row:
            fibres=[next(j for j in row if j//degree==v)%degree
                    for row in lifted_rows]
            assert sorted(fibres)==list(range(degree))
    return True


def hierarchy(seed,levels=6):
    base,n=sparse_base()
    rng=Random(seed)
    rows=base
    degree=1
    for k in range(levels):
        assert_exact_cover_map(rows,n,degree,base,12)
        yield k,n,degree,rows
        rows=two_lift(rows,n,rng)
        degree*=2
        n*=2



def base_integer_fibre_separator():
    """Construct integral u with u^T A=36*e_0, sum(u)=12.

    Fractions are used in a 12x12 exact Gauss-Jordan solve to build an
    integer vector; verification uses ONLY integer arithmetic.
    """
    from fractions import Fraction
    A=base_matrix()
    n=len(A)
    assert n==12
    assert det_bareiss(A)==36
    # Solve A^T*u = 36*e0 exactly.
    aug=[
        [Fraction(A[j][i]) for j in range(n)]
        +[Fraction(36 if i==0 else 0)]
        for i in range(n)
    ]
    for k in range(n):
        pivot=next(i for i in range(k,n) if aug[i][k])
        aug[k],aug[pivot]=aug[pivot],aug[k]
        q=aug[k][k]
        aug[k]=[v/q for v in aug[k]]
        for i in range(n):
            if i!=k and aug[i][k]:
                q=aug[i][k]
                aug[i]=[v-q*w for v,w in zip(aug[i],aug[k])]
    assert all(aug[i][j]==int(i==j) for i in range(n) for j in range(n))
    u=[row[-1] for row in aug]
    assert all(z.denominator==1 for z in u)
    z=[int(t) for t in u]
    assert sum(z)==12
    assert [
        sum(z[i]*A[i][j] for i in range(n)) for j in range(n)
    ]==[36]+[0]*11
    return tuple(z)


def validate_integer_cover_refutation(rows,n,r,base_rows,u):
    """Independent O(n) exact linear certificate; no Boolean search.

    Lifted check copies get coefficient u_i. Sum their equations:
       36 * (number of selected copies of base variable 0) = 12*r.
    Since 3 does not divide r this is impossible for INTEGER x.
    """
    nbase=12
    assert n==12*r and len(base_rows)==nbase and len(u)==nbase
    # u's indices refer to the ORIGINAL base_matrix row order.
    # validate_sparse sorts rows lexicographically, so enumerate(base_rows)
    # would silently permute u and INVALIDATE the certificate!
    B=base_matrix()
    labels={
        tuple(j for j,value in enumerate(row) if value): i
        for i,row in enumerate(B)
    }
    assert len(labels)==12 and set(labels)==set(base_rows)
    left=[0]*n
    sum_coeff=0
    for row in rows:
        key=tuple(sorted(v//r for v in row))
        i=labels[key]
        w=u[i]
        sum_coeff+=w
        for j in row:
            left[j]+=w
    expected=[36 if j//r==0 else 0 for j in range(n)]
    assert left==expected,(n,left[:20],expected[:20])
    assert sum_coeff==12*r
    assert r%3!=0
    return True

def main():
    base,_=sparse_base()
    results=[]
    u=base_integer_fibre_separator()
    print("FIBRE_LINEAR_UNSAT_CERTIFICATE_INTEGER_U12=",u)
    # Complete q12/q24/q48/q96 where affordable; guarded at larger n.
    caps={12:2500,24:4500,48:6000,96:6000,192:1800,384:1000}
    for seed in (129,132,9421):
        for k,n,r,rows in hierarchy(seed,levels=6):
            assert validate_integer_cover_refutation(rows,n,r,base,u)
            result=ExactSupportResidualDAG_sparse(
                rows,n,max_states=caps[n]
            )
            status=result["status"]
            stats=result["stats"]
            # ALL members are mathematically UNSAT by the E129 theorem,
            # including those for which the solver returns UNKNOWN.
            assert r&(r-1)==0 and r%3!=0
            assert status in ("UNSAT","UNKNOWN"),(seed,k,n,status)
            if status=="UNKNOWN":
                assert stats["distinct_states"]==caps[n]
                assert stats["guard_hits"]>=1
            else:
                assert result["witness"] is None
            results.append((seed,n,status,stats["distinct_states"]))
            print(
                f"E129_COVER2 seed={seed}, n={n}, r={r}, "
                f"math=UNSAT, solver={status}, "
                f"ACTUAL_VISITED_S={stats['distinct_states']}, "
                f"cap={caps[n]}, component_splits={stats['component_splits']}, "
                f"cache_hits={stats['cache_hits']}"
            )
    assert all(s in ("UNSAT","UNKNOWN") for _,_,s,_ in results)
    assert len(results)==18
    print("E129_INVERTIBLE_BASE_DET36 = PREDECESSOR_REPLAY")
    print("EXPLICIT_O(N)_VERIFY_INTEGER_UNSAT_CERTIFICATE = PROVED_FOR_ALL_COVERS")
    print("THIS_FAMILY_HAS_SHORT_ARITHMETIC_PROOFS; NOT_A_UNIVERSAL_LOWER_BOUND")
    print("ALL_POWERS_OF_TWO_LEVI_COVERS_UNSAT = E129_GENERAL_THEOREM")
    print("EXACT_FIBRE_COVER_MAP = INDEPENDENTLY_VERIFIED")
    print("ACTUAL_MEMO_STATES = FINITE_OBSERVATION_WITH_GUARD")
    print("EXPONENTIAL_ACTUAL_SEARCH_PROOF_SIZE_LOWER_BOUND = OPEN")
    print("GLOBAL_POLYNOMIAL_ExactSupport = NOT_CONSTRUCTED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
