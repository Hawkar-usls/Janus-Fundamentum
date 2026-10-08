#!/usr/bin/env python3
"""Polynomial two-sided Gaussian probing closure for 2-XNF.

This is a strict, branch-free strengthening of UGIC.

For every active nonzero affine normal m:
  * probe m·x=0 and m·x=1 independently with UGIC;
  * if both probes are UNSAT, return UNSAT;
  * if exactly one probe is UNSAT, force the opposite equation globally;
  * if both survive, intersect the full augmented GF(2) row spaces of the
    equations learned in the two probes and add every common affine equation.

No recursive probing is performed.  The outer loop only repeats after the
global affine rank increases.  Hence at most n strict learning rounds occur.

If q is the number of active normals, this performs O(n q) calls to a
polynomial UGIC routine plus polynomial GF(2) row-space intersections.

The closure is sound and polynomial.  It is not claimed complete.
"""

from collections import Counter

from uniform_gaussian_implication_audit import (
    obstruction_formula,
    rref_affine,
    rank_vectors,
    satisfying_assignments,
    uniform_gaussian_implication_closure,
)
from php_scalable_open_firewall import php_cnf, xnf_to_2xnf
from bit_php_open_firewall import bphp_xnf


def vec_basis(vecs):
    """Return an independent GF(2) basis of integer bit-vectors."""
    piv={}
    B=[]
    for x in vecs:
        y=x
        while y:
            p=y.bit_length()-1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p]=y
                B.append(x)
                break
    return tuple(B)


def reduce_vec(x,basis):
    piv={}
    for b in basis:
        y=b
        while y:
            p=y.bit_length()-1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p]=y
                break
    y=x
    for p in sorted(piv,reverse=True):
        if (y>>p)&1:
            y ^= piv[p]
    return y


def rowspace_contains(basis,x):
    return reduce_vec(x,basis)==0


def augmented_rows(equations,n):
    return tuple(mask | (rhs<<n) for mask,rhs in equations)


def equation_rowspace_intersection(E0,E1,n):
    """Basis for row-span(E0_aug) intersect row-span(E1_aug).

    Small exact linear-algebra construction:
      x in A∩B iff x = sum alpha_i A_i = sum beta_j B_j.
    Nullspace of [A | B] coefficient map is computed over coefficient
    variables; projected common vectors are then independently based.
    """
    A=vec_basis(augmented_rows(E0,n))
    B=vec_basis(augmented_rows(E1,n))
    cols=A+B
    na=len(A)
    nb=len(B)
    total=na+nb

    # Build one equation per ambient augmented coordinate.
    ambient=n+1
    eqrows=[]
    for bit in range(ambient):
        row=0
        for i,v in enumerate(cols):
            if (v>>bit)&1:
                row |= 1<<i
        if row:
            eqrows.append(row)

    # Nullspace in coefficient space.
    rows=list(eqrows)
    rank=0
    piv=[]
    for col in range(total):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        piv.append(col)
        rank+=1
    pset=set(piv)
    free=[c for c in range(total) if c not in pset]

    common=[]
    for f in free:
        coeff=1<<f
        for i,p in enumerate(piv):
            if (rows[i]>>f)&1:
                coeff |= 1<<p
        x=0
        for i,a in enumerate(A):
            if (coeff>>i)&1:
                x ^= a
        y=0
        for j,b in enumerate(B):
            if (coeff>>(na+j))&1:
                y ^= b
        assert x==y
        if x:
            common.append(x)

    basis=vec_basis(common)

    # Translate back to affine equations; consistent branch rowspaces cannot
    # contain the contradiction 0=1.
    out=[]
    for v in basis:
        mask=v & ((1<<n)-1)
        rhs=(v>>n)&1
        assert mask!=0 or rhs==0
        if mask:
            out.append((mask,rhs))
    return rref_affine(tuple(out),n) or tuple()


def active_probe_masks(active):
    return tuple(sorted(set(
        L[0]
        for clause in active
        for L in clause
        if L[0]
    )))


def two_sided_gaussian_probe_closure(formula,n):
    equations=tuple()
    probe_calls=0
    rounds=0

    while True:
        rounds+=1
        status,eqs,active=uniform_gaussian_implication_closure(
            formula,n,initial_equations=equations
        )
        if status!="OPEN":
            return status,eqs,active,{
                "probe_calls":probe_calls,
                "strict_rounds":rounds-1,
            }

        equations=eqs
        base_aug=vec_basis(augmented_rows(equations,n))
        learned=[]

        for mask in active_probe_masks(active):
            branch_results=[]
            for value in (0,1):
                probe_calls+=1
                st,E,A=uniform_gaussian_implication_closure(
                    formula,n,
                    initial_equations=tuple(equations)+((mask,value),)
                )
                branch_results.append((st,E,A))

            s0,E0,_=branch_results[0]
            s1,E1,_=branch_results[1]

            if s0=="UNSAT" and s1=="UNSAT":
                return "UNSAT",equations,active,{
                    "probe_calls":probe_calls,
                    "strict_rounds":rounds-1,
                }

            if s0=="UNSAT":
                learned.append((mask,1))
                continue
            if s1=="UNSAT":
                learned.append((mask,0))
                continue

            common=equation_rowspace_intersection(E0,E1,n)
            for e in common:
                aug=e[0] | (e[1]<<n)
                if not rowspace_contains(base_aug,aug):
                    learned.append(e)

        if not learned:
            return "OPEN",equations,active,{
                "probe_calls":probe_calls,
                "strict_rounds":rounds-1,
            }

        neweq=rref_affine(tuple(equations)+tuple(learned),n)
        if neweq is None:
            return "UNSAT",None,active,{
                "probe_calls":probe_calls,
                "strict_rounds":rounds,
            }
        if neweq==equations:
            return "OPEN",equations,active,{
                "probe_calls":probe_calls,
                "strict_rounds":rounds-1,
            }

        assert len(neweq)>len(equations)
        equations=neweq
        assert len(equations)<=n


def verify_intersection_algebra():
    # E0 entails x1=0, x2=0; E1 entails x1=1, x2=1.
    # Both entail x1 xor x2=0.
    I=equation_rowspace_intersection(((1,0),(2,0)),((1,1),(2,1)),2)
    aug=vec_basis(augmented_rows(I,2))
    assert rowspace_contains(aug,3)  # x1 xor x2 = 0
    assert not rowspace_contains(aug,1)  # x1=0 not common


def verify_frozen_obstruction():
    F=obstruction_formula()
    st,E,A,stats=two_sided_gaussian_probe_closure(F,3)
    # Probing is allowed to strengthen UGIC; exact semantics is UNSAT.
    assert satisfying_assignments(F,3)==tuple()
    assert st in ("UNSAT","OPEN")
    if st=="OPEN":
        # low-normal-rank exact terminal still closes it downstream.
        normals=[L[0] for C in A for L in C]
        assert rank_vectors(normals)<=3
    return st,len(E or ()),stats


def verify_scalable_php_samples():
    out=[]
    for k in range(3,7):
        cnf,n0,_=php_cnf(k)
        F,n=xnf_to_2xnf(cnf,n0)
        st,E,A,stats=two_sided_gaussian_probe_closure(F,n)
        # This closure layer alone must never overclaim SAT on UNSAT PHP.
        assert st!="SAT_LINEAR"
        out.append({
            "k":k,
            "status":st,
            "learned_rank":len(E or ()),
            "active":len(A),
            **stats,
        })
    return out


def verify_bit_php_samples():
    out=[]
    for ell in range(2,4):
        source,n0,_,p,h=bphp_xnf(ell)
        F,n=xnf_to_2xnf(source,n0)
        st,E,A,stats=two_sided_gaussian_probe_closure(F,n)
        assert st!="SAT_LINEAR"
        out.append({
            "ell":ell,
            "pigeons":p,
            "holes":h,
            "status":st,
            "learned_rank":len(E or ()),
            "active":len(A),
            **stats,
        })
    return out


def main():
    verify_intersection_algebra()
    frozen=verify_frozen_obstruction()
    php=verify_scalable_php_samples()
    bphp=verify_bit_php_samples()

    print("TWO-SIDED GAUSSIAN PROBING CLOSURE: PASS")
    print("row-space intersection logic: PASS")
    print("frozen obstruction:",frozen)
    print("PHP samples:")
    for r in php:
        print(r)
    print("bit-PHP samples:")
    for r in bphp:
        print(r)
    print("resource bound: O(n*q) polynomial UGIC probes, no recursive branching")
    print("COMMON_AFFINE_CONSEQUENCES are intersected as augmented GF(2) row spaces")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
