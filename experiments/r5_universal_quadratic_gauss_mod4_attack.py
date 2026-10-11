#!/usr/bin/env python3
"""Universal all-input GF(2) quadratic-Gauss parity-weight certificate.

Unlike enumeration of 2^d kernel words, quadratic Gauss sums on ANY
(possibly pinned/affine) binary kernel are computable in polynomial time.

This is a SOUND necessary arithmetic-constraint UNSAT test, not a
complete SAT decision for all square-cubic-linear inputs.
On the q63 E123 UNSAT orientation it rejects ALL 189 one-check pins
without enumerating the kernel; the SAT transpose survives.
"""
from __future__ import annotations

from itertools import combinations

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis
from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT, Q_SAT, P_UNSAT, Q_UNSAT, build_A,
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, source_solutions, e118_target, verify_target,
)


def kernel_basis(A):
    _, _, b = gf2_rref_basis(A)
    assert all(sum((v & sum(1 << j for j,c in enumerate(row) if c)).bit_count() % 2
                   for row in A)==0 for v in b)
    return b


def affine_word_map(basis, coeff):
    word=0
    for i,v in enumerate(basis):
        if coeff >> i & 1:
            word ^= v
    return word


def pinned_affine_basis(basis, n, pins=None):
    """Solve linear constraints k_i=pins[i] in coefficient space.

    Returns (one_k_word, independent_translation_basis) or None.
    Gaussian elimination works in O(poly(n,d)) bit operations.
    """
    pins=pins or {}
    d=len(basis)
    pivot={}
    input_rows=[]
    for j,rhs in sorted(pins.items()):
        assert 0<=j<n and rhs in (0,1)
        c=sum(((basis[t]>>j)&1)<<t for t in range(d))
        input_rows.append((c,rhs))
        while c:
            p=c.bit_length()-1
            if p not in pivot:
                pivot[p]=(c,rhs)
                break
            row,previous=pivot[p]
            c ^= row
            rhs ^= previous
        if not c and rhs:
            return None
    pkeys=sorted(pivot)
    free=[t for t in range(d) if t not in pivot]

    def solve(free_vector, particular):
        v=free_vector
        for p in pkeys:
            row,rhs=pivot[p]
            s=((v & row).bit_count() & 1) ^ (rhs if particular else 0)
            if s:
                v ^= 1<<p
        assert all(((v & row).bit_count() & 1)==(rhs if particular else 0)
                   for row,rhs in input_rows)
        return affine_word_map(basis,v)

    word0=solve(0,True)
    translations=[solve(1<<f,False) for f in free]
    assert all((word0>>j)&1==rhs for j,rhs in pins.items())
    assert all(all(((v>>j)&1)==0 for j in pins) for v in translations)
    return word0,translations


def quadratic_form_monomials(word0, basis):
    """Polynomial over F2 for q(t)=|word0+sum(t_i*b_i)|/2 mod 2.

    The domain is an even-weight binary code, so its polarization is
    the standard binary dot product.
    """
    assert word0.bit_count()%2==0
    assert all(v.bit_count()%2==0 for v in basis)
    mons=set()
    if (word0.bit_count()//2)&1:
        mons.add(frozenset())
    for i,v in enumerate(basis):
        if ((v.bit_count()//2)+(word0&v).bit_count())&1:
            mons.add(frozenset((i,)))
        for j in range(i):
            if (v&basis[j]).bit_count()&1:
                mons.add(frozenset((i,j)))
    return mons


def gauss_sum_of_quadratic(mons,dimension):
    """Exact polynomial-time GF2 quadratic exponential sum.

    Eliminate every uv interaction. If q=uv+a(r)u+b(r)v+c(r), then
    sum_{u,v}(-1)^q=2*(-1)^(c(r)+a(r)b(r)).
    Polynomial remains quadratic, no branching.
    """
    active=set(range(dimension))
    q=set(mons)
    factor=1
    while True:
        e=next((term for term in q if len(term)==2),None)
        if e is None:
            if any(len(term)==1 for term in q):
                return 0
            return factor * (1 if frozenset() not in q else -1) * (1<<len(active))
        i,j=sorted(e)
        a=set()
        b=set()
        c=set()
        for term in q:
            if term == e:
                continue
            if i in term:
                a.add(term-{i})
            elif j in term:
                b.add(term-{j})
            else:
                c.add(term)
        for u in a:
            for v in b:
                new=u|v
                if new in c:
                    c.remove(new)
                else:
                    c.add(new)
        q=c
        assert all(len(term)<=2 for term in q)
        active.remove(i)
        active.remove(j)
        factor*=2


def mod4_weight_counts(basis,n,pins=None):
    """Exact #(k mod4=0), #(k mod4=2) among pinned kernel words."""
    aff=pinned_affine_basis(basis,n,pins)
    if aff is None:
        return (0,0)
    word0,trans=aff
    d=len(trans)
    gauss=gauss_sum_of_quadratic(
        quadratic_form_monomials(word0,trans),d
    )
    size=1<<d
    assert abs(gauss)<=size
    assert (size+gauss)%2==0
    return ((size+gauss)//2,(size-gauss)//2)


def enumerate_small_independently(basis,n,pins=None):
    counts=[0,0]
    pins=pins or {}
    for t in range(1<<len(basis)):
        w=affine_word_map(basis,t)
        if any(((w>>j)&1)!=v for j,v in pins.items()):
            continue
        assert w.bit_count()%2==0
        counts[(w.bit_count()//2)&1]+=1
    return tuple(counts)


def exact_one_pins(A,selected,check):
    n=len(A)
    js=[j for j,v in enumerate(A[check]) if v]
    assert len(js)==3 and selected in js
    # x_selected=1 => k_selected=0; x_other=0 => k_other=1.
    return {j: int(j!=selected) for j in js}


def main():
    # All computations below are exact. Brute-force is used only as
    # INDEPENDENT small finite replay, never inside the general algorithm.
    for label,A in [
        ("SAT12",build_A(P_SAT,Q_SAT)),
        ("UNSAT12",build_A(P_UNSAT,Q_UNSAT)),
    ]:
        n=len(A)
        b=kernel_basis(A)
        for pins in (
            {},{0:0},{0:1},{0:1,1:0},{0:0,1:1}
        ):
            assert mod4_weight_counts(b,n,pins)==enumerate_small_independently(b,n,pins)
        print(f"{label}: exact affine quadratic-Gauss replay PASS")

    R=tutte12_incidence()
    RT=[list(col) for col in zip(*R)]
    for label,M,expected in [
        ("E123_UNSAT",R,(16384,0)),
        ("E65_TRANSPOSE_SAT",RT,(8192,8192)),
    ]:
        n=len(M)
        basis=kernel_basis(M)
        assert len(basis)==14
        got=mod4_weight_counts(basis,n)
        assert got==expected,(label,got)
        accepted=0
        for check in range(n):
            for selected in [j for j,c in enumerate(M[check]) if c]:
                pins=exact_one_pins(M,selected,check)
                c0,c2=mod4_weight_counts(basis,n,pins)
                if label=="E123_UNSAT":
                    assert c2==0
                else:
                    assert c2>0
                accepted+=1
        assert accepted==189
        print(f"{label}: mod4 (weight=0,2) counts={got}; 189 quadratic pin checks PASS")

    # E118 direct hard negative: no universal inference from nonzero
    # candidate target-residue mass is allowed.
    neg=cyclic_source(9,1,6)
    pos=cyclic_source(9,1,2)
    assert source_solutions(neg)==[]
    assert source_solutions(pos)
    for label,source,expect_sat in [
        ("E118_CONNECTED_UNSAT90",neg,False),
        ("E118_CONNECTED_SAT90",pos,True),
    ]:
        rows,_,_=e118_target(source)
        verify_target(rows)
        n=len(rows)
        M=[[int(j in row) for j in range(n)] for row in rows]
        basis=kernel_basis(M)
        counts=mod4_weight_counts(basis,n)
        assert n==90
        assert sum(counts)==1<<len(basis)
        # Target size n=90, |k| target=60, so mod4 class is 0.
        if expect_sat:
            assert counts[0]>0
        print(f"{label}: n=90 d={len(basis)}, mod4 counts={counts}")
    print("QUADRATIC_GAUSS_FOR_EVERY_AFFINE_GF2_KERNEL = POLYNOMIAL AND EXACT")
    print("MOD4_EXCLUSION = SOUND UNSAT TEST; COMPLETENESS NOT CLAIMED")
    print("UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED; P_VS_NP = OPEN")


if __name__=="__main__":
    main()
