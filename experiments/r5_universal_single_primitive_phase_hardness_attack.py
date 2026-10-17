#!/usr/bin/env python3
"""Single primitive cyclotomic phase: exact equivalence, not a solver.

For any legal n=3m cubic square Exact-One A and partial Boolean pins,
H_pi(z)=sum_{k in ker_F2(A), compatible} z^(wt(k)/2)
has degree <=m. The smallest power Q=2^s with Q>2m has
D=Q/2>m and Phi_Q(z)=z^D+1, hence *one* exact canonical
cyclotomic value H_pi(zeta_Q) has integer coefficient at zeta_Q^m
equal to the exact number of Ext-One solutions with pins.

An all-input polynomial canonical-basis evaluator for this primitive
phase would solve NP-complete SCL Exact-One in polynomial bit time.
This checker enumerates only SMALL FROZEN FIXTURES; its enumeration
is intentionally exponential, NOT an implementation of that evaluator.

It also constructs exact 2-adic ANF for the phase exponent to show
why existing quadratic Gauss elimination does not extend automatically.
"""
from __future__ import annotations

from itertools import combinations
from math import comb

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis
from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT, Q_SAT, P_UNSAT, Q_UNSAT, build_A,
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, source_solutions, e118_target, verify_target,
)


def primitive_phase_parameters(n):
    assert n>0 and n%3==0
    m=n//3
    Q=1
    while Q<=2*m:
        Q*=2
    D=Q//2
    assert m<D<=2*m and Q<=4*m
    return m,Q,D


def bit_kernel_basis(A):
    n=len(A)
    assert n>0 and all(len(row)==n and sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    _,_,basis=gf2_rref_basis(A)
    rows=[sum(int(v)<<j for j,v in enumerate(row)) for row in A]
    assert all(all((b&r).bit_count()%2==0 for r in rows) for b in basis)
    return basis


def exact_fixture_halfweight_coefficients(basis,n,pins=None):
    """Exponential finite-fixture oracle, never claimed polynomial."""
    pins=pins or {}
    m,Q,D=primitive_phase_parameters(n)
    count=[0]*(m+1)
    word=0
    last=0
    for i in range(1<<len(basis)):
        gray=i^(i>>1)
        change=gray^last
        if change:
            word^=basis[change.bit_length()-1]
        last=gray
        if any(((word>>j)&1)!=bit for j,bit in pins.items()):
            continue
        w=word.bit_count()
        assert w%2==0 and w<=2*m
        count[w//2]+=1
    assert sum(count)<=1<<len(basis)
    assert len(count)<=D
    return count


def source_to_target_matrix(a,b):
    source=cyclic_source(9,a,b)
    models=source_solutions(source)
    rows,ports,pos=e118_target(source)
    verify_target(rows)
    n=len(rows)
    assert n==90
    A=[[int(j in row) for j in range(n)] for row in rows]
    return A,models


def phase_anf_nonzero_counts(basis,Q):
    """Full high-degree intersection ANF on fixed witnesses only.

    For t_i in {0,1}, XOR inclusion-exclusion gives exactly
    wt(XOR_i t_i b_i)/2 =
      sum_nonempty_J (-1)^(|J|-1) 2^(|J|-2)
         wt(AND_{j in J} b_j) prod_{j in J} t_j.
    The |J|=1 term is wt(b_j)/2 (integer for this code).
    Reduction modulo Q=2^s kills all |J|>=s+2 terms.
    """
    s=Q.bit_length()-1
    d=len(basis)
    nonzero=[]
    examples=[]
    for degree in range(1,min(s+1,d)+1):
        count=0
        sample=None
        for inds in combinations(range(d),degree):
            mask=basis[inds[0]]
            for i in inds[1:]:
                mask &=basis[i]
            intersection=mask.bit_count()
            coeff=(
                intersection//2 if degree==1
                else ((-1)**(degree-1))*(1<<(degree-2))*intersection
            )%Q
            if coeff:
                count+=1
                if sample is None:
                    sample=(inds,coeff)
        nonzero.append(count)
        examples.append(sample)
    return nonzero,examples



def independent_finite_mobius_anf_counts(basis,Q):
    """Full independent ANF derivation for FIXED finite controls only.

    Exponent evaluations enumerate 2^d kernel words; a subset
    Mobius transform then recovers exact multilinear coefficients mod Q.
    It validates, but does NOT accelerate, the general phase formula.
    """
    d=len(basis)
    size=1<<d
    assert d<=18  # scientific fixture budget, not general complexity
    v=[0]*size
    last=0
    word=0
    for t in range(size):
        g=t^(t>>1)
        change=g^last
        if change:
            word^=basis[change.bit_length()-1]
        last=g
        assert word.bit_count()%2==0
        v[g]=word.bit_count()//2%Q

    for i in range(d):
        step=1<<i
        for mask in range(size):
            if mask&step:
                v[mask]=(v[mask]-v[mask^step])%Q

    s=Q.bit_length()-1
    counts=[0]*min(d,s+1)
    for mask,coeff in enumerate(v):
        degree=mask.bit_count()
        if degree>s+1:
            assert coeff==0, (mask,degree,coeff)
        elif degree and coeff:
            counts[degree-1]+=1
        elif degree==0:
            assert coeff==0
    return counts

def check(name,A,expected_top,expected_dim,expected_top_degree=None):
    n=len(A)
    m,Q,D=primitive_phase_parameters(n)
    basis=bit_kernel_basis(A)
    assert len(basis)==expected_dim
    c=exact_fixture_halfweight_coefficients(basis,n)
    assert c[m]==expected_top,(name,c[m],expected_top)
    assert sum(c)==1<<expected_dim
    # Representation of H(zeta_Q) in canonical integral Z-basis
    # 1,zeta,...,zeta^(D-1) is exactly c + trailing zeroes.
    canonical_coordinates=c+[0]*(D-len(c))
    assert len(canonical_coordinates)==D
    assert canonical_coordinates[m]==expected_top
    assert max(canonical_coordinates)<(1<<(expected_dim+1))
    counts,examples=phase_anf_nonzero_counts(basis,Q)
    independent=independent_finite_mobius_anf_counts(basis,Q)
    assert counts==independent, (name,counts,independent)
    if expected_top_degree is not None:
        assert max(i for i,v in enumerate(counts,1) if v)>=(expected_top_degree)
        assert counts[expected_top_degree-1]>0
    print(f"{name}: n={n} kernel_dim={expected_dim} Q={Q} D={D}")
    print(f"    primitive phase canonical coordinate at m={m}: {canonical_coordinates[m]}")
    print(f"    halfweight polynomial supports: {[(j,v) for j,v in enumerate(c) if v]}")
    print(f"    exact mod-Q phase ANF nonzero counts by degree: {counts}")
    return c


def main():
    c1=check("E61_SAT12",build_A(P_SAT,Q_SAT),1,2)
    c0=check("E61_UNSAT12",build_A(P_UNSAT,Q_UNSAT),0,1)
    assert c1==[1,0,0,2,1]
    assert c0==[1,0,1,0,0]

    R=tutte12_incidence()
    ct=check("E65_SAT_TRANSPOSE63",[list(x) for x in zip(*R)],36,14,7)
    cr=check("E123_UNSAT63",R,0,14,7)
    assert ct[21]==36 and cr[21]==0

    Aneg,modelneg=source_to_target_matrix(1,6)
    Apos,modelpos=source_to_target_matrix(1,2)
    assert not modelneg and len(modelpos)==3
    cn=check("E118_CONNECTED_UNSAT90",Aneg,0,18)
    cp=check("E118_CONNECTED_SAT90",Apos,192,18)
    assert cn[30]==0 and cp[30]==64*len(modelpos)
    assert sum(cn)==sum(cp)==1<<18

    # Demonstrate pin projection agrees with selecting real solutions:
    # x_0=1 iff k_0=0, preserving the same primitive phase identity.
    for name,M in (("SAT12",build_A(P_SAT,Q_SAT)),("UNSAT12",build_A(P_UNSAT,Q_UNSAT))):
        basis=bit_kernel_basis(M)
        full=exact_fixture_halfweight_coefficients(basis,12)
        p0=exact_fixture_halfweight_coefficients(basis,12,{0:0})
        p1=exact_fixture_halfweight_coefficients(basis,12,{0:1})
        assert [u+v for u,v in zip(p0,p1)]==full
        print(f"{name}: pinned split a4 = {p0[4]} + {p1[4]} = {full[4]}")

    print("ONE_PRIMITIVE_PHASE_CANONICAL_COORDINATE_RECOVERS_EXACT_COUNT=PROVED")
    print("Q=O(n), canonical output O(n^2) bits; but universal evaluator NOT FOUND")
    print("ANY_POLYNOMIAL_EXACT_PHASE_EVALUATOR_FOR_ALL_SCL => P=NP")
    print("UNIVERSAL_SOLVER=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
