#!/usr/bin/env python3
"""Polynomial two-sided Gaussian probing closure for 2-XNF.

This is a branch-FREE closure layer, not a DPLL fallback.

For every distinct active affine normal a:
  * temporarily assume a.x=0 and run the already-sound UGIC closure;
  * temporarily assume a.x=1 and run UGIC;
  * if one side is UNSAT, learn the opposite affine equation globally;
  * if both sides survive, intersect the two affine consequence spaces and
    learn every equation derived on BOTH sides;
  * if either side reaches SAT_LINEAR, the original formula is SAT.

No probe recursively invokes probing.  It invokes UGIC only.
Every successful outer round raises the global affine rank, so there are at
most n such rounds.  At most O(m) normals are probed per round.  Therefore the
procedure is polynomial.

The common-consequence intersection is computed as an actual GF(2) subspace
intersection of augmented equation vectors (mask,rhs), never by comparing RREF
rows syntactically.

Prior-art ceiling:
This is a parity/Gaussian analogue of failed-literal / lookahead probing and
common consequence learning.  It is not claimed novel and is not assumed
complete.

Firewalls:
  * the frozen 3-variable UGIC obstruction is solved by two-sided probing;
  * scalable PHP and bit-PHP are tested to see whether they still survive;
  * an invertible affine scramble of bit-PHP checks representation invariance
    of the current macro portfolio.

GENERAL_SAT_IN_P is NOT proved.  P_VS_NP remains OPEN.
"""

from itertools import product

from uniform_gaussian_implication_audit import (
    obstruction_formula,
    rref_affine,
    satisfies,
    uniform_gaussian_implication_closure,
)
from php_scalable_open_firewall import php_cnf, xnf_to_2xnf
from bit_php_open_firewall import bphp_xnf, represented_matroid_components, line_points
from choice_resource_hall_terminal import hall_terminal
from binary_alldifferent_capacity_terminal import detect_complete_alldifferent


def homogeneous_rref(rows,width):
    rows=[x for x in rows if x]
    rank=0
    for col in range(width):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        pivot=rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=pivot
        rank+=1
    out=[x for x in rows if x]
    out.sort(key=lambda x:(x & -x).bit_length())
    return tuple(out)


def nullspace_basis(rows,width):
    """Basis of {x : row.x=0 for every row}, bit-vector coordinates."""
    R=list(homogeneous_rref(rows,width))
    piv=[]
    for row in R:
        piv.append((row & -row).bit_length()-1)
    pset=set(piv)
    free=[c for c in range(width) if c not in pset]

    basis=[]
    for f in free:
        x=1<<f
        # RREF rows have unique pivot columns.
        for row,p in zip(R,piv):
            if (row>>f)&1:
                x |= 1<<p
        basis.append(x)
    return homogeneous_rref(basis,width)


def subspace_intersection(U,V,width):
    """Canonical basis for span(U) intersection span(V)."""
    U=homogeneous_rref(U,width)
    V=homogeneous_rref(V,width)
    Uperp=nullspace_basis(U,width)
    Vperp=nullspace_basis(V,width)
    return nullspace_basis(Uperp+Vperp,width)


def eq_to_aug(eq,n):
    m,rhs=eq
    return m | ((rhs&1)<<n)


def aug_to_eq(v,n):
    mask=v & ((1<<n)-1)
    rhs=(v>>n)&1
    return mask,rhs


def common_affine_consequences(eqs0,eqs1,n):
    """All affine equations represented in both consequence row spaces."""
    U=tuple(eq_to_aug(e,n) for e in (eqs0 or ()))
    V=tuple(eq_to_aug(e,n) for e in (eqs1 or ()))
    I=subspace_intersection(U,V,n+1)
    out=[]
    for v in I:
        m,rhs=aug_to_eq(v,n)
        assert not (m==0 and rhs==1)
        if m:
            out.append((m,rhs))
    R=rref_affine(tuple(out),n)
    assert R is not None
    return R


def one_affine_solution(equations,n):
    """One solution of a consistent RREF affine system (free vars = 0)."""
    E=rref_affine(tuple(equations or ()),n)
    if E is None:
        return None
    x=0
    # With free vars zero, each pivot is its row rhs.
    for m,rhs in reversed(E):
        p=(m & -m).bit_length()-1
        rest=m & ~(1<<p)
        val=rhs ^ ((rest & x).bit_count()&1)
        if val:
            x |= 1<<p
    return x


def active_probe_masks(active):
    return tuple(sorted({L[0] for C in active for L in C if L[0]}))


def bidirectional_gaussian_probe_closure(formula,n,initial_equations=tuple()):
    equations=rref_affine(tuple(initial_equations),n)
    if equations is None:
        return "UNSAT",None,tuple(),{"ugic_calls":0,"probes":0,"rank_rounds":0}

    stats={"ugic_calls":0,"probes":0,"rank_rounds":0}

    for _outer in range(n+2):
        st,equations,active=uniform_gaussian_implication_closure(
            formula,n,initial_equations=equations
        )
        stats["ugic_calls"]+=1

        if st!="OPEN":
            return st,equations,active,stats

        learned=[]
        found_sat=None

        for mask in active_probe_masks(active):
            branches=[]
            for rhs in (0,1):
                st_b,eq_b,act_b=uniform_gaussian_implication_closure(
                    formula,n,initial_equations=tuple(equations)+((mask,rhs),)
                )
                stats["ugic_calls"]+=1
                branches.append((st_b,eq_b,act_b))
            stats["probes"]+=1

            (s0,e0,a0),(s1,e1,a1)=branches

            if s0=="UNSAT" and s1=="UNSAT":
                return "UNSAT",equations,active,stats

            # A surviving SAT_LINEAR side is an explicit global SAT certificate.
            if s0=="SAT_LINEAR":
                found_sat=(e0,a0)
                break
            if s1=="SAT_LINEAR":
                found_sat=(e1,a1)
                break

            if s0=="UNSAT":
                learned.append((mask,1))
                continue
            if s1=="UNSAT":
                learned.append((mask,0))
                continue

            # Both sides survive: any affine equation derived on BOTH sides is
            # globally valid by exhaustive case split on mask.x.
            learned.extend(common_affine_consequences(e0,e1,n))

        if found_sat is not None:
            eq_sat,act_sat=found_sat
            x=one_affine_solution(eq_sat,n)
            assert x is not None
            assert satisfies(formula,x)
            return "SAT_LINEAR",eq_sat,tuple(),stats

        neweq=rref_affine(tuple(equations)+tuple(learned),n)
        if neweq is None:
            return "UNSAT",None,active,stats

        if neweq!=equations:
            assert len(neweq)>len(equations)
            equations=neweq
            stats["rank_rounds"]+=1
            continue

        return "OPEN",equations,active,stats

    raise AssertionError("probing closure exceeded affine-rank round bound")


def verify_subspace_intersection():
    # Branch 0: x=0, y=1. Branch 1: x=1, y=1.
    # Common affine consequence is exactly y=1.
    n=2
    E0=rref_affine(((1,0),(2,1)),n)
    E1=rref_affine(((1,1),(2,1)),n)
    C=common_affine_consequences(E0,E1,n)
    assert C==((2,1),)

    # Opposite x assumptions alone have no nontrivial common equation.
    A0=rref_affine(((1,0),),n)
    A1=rref_affine(((1,1),),n)
    assert common_affine_consequences(A0,A1,n)==tuple()


def prefix_transform_mask(mask,n):
    """Substitute x_i = y_0 xor ... xor y_i (invertible unit-lower-triangular)."""
    out=0
    for i in range(n):
        if (mask>>i)&1:
            out ^= (1<<(i+1))-1
    return out


def transform_source_xnf(source,n0):
    out=[]
    for C in source:
        CC=[]
        for mask,const in C:
            CC.append((prefix_transform_mask(mask,n0),const))
        out.append(tuple(CC))
    return tuple(out)


def transformed_formula(formula,nbase,ntotal):
    """Apply prefix transform to original coordinates; keep auxiliaries fixed."""
    lowmask=(1<<nbase)-1
    out=[]
    for a,b in formula:
        CC=[]
        for mask,const in (a,b):
            low=mask & lowmask
            high=mask & ~lowmask
            CC.append((prefix_transform_mask(low,nbase)^high,const))
        out.append(tuple(CC))
    return tuple(out)


def verify_frozen_obstruction():
    F=obstruction_formula()
    st,eqs,active,stats=bidirectional_gaussian_probe_closure(F,3)
    assert st=="UNSAT"
    return stats


def verify_php_probe(k):
    cnf,n0,_=php_cnf(k)
    formula,n=xnf_to_2xnf(cnf,n0)
    st,eqs,active,stats=bidirectional_gaussian_probe_closure(formula,n)
    hall=hall_terminal(cnf)
    assert hall["status"]=="UNSAT"
    return {
        "k":k,
        "probe_status":st,
        "learned_rank":0 if eqs is None else len(eqs),
        "active":len(active),
        "probes":stats["probes"],
        "hall":"UNSAT",
    }


def verify_bit_php_probe(ell):
    source,n0,_,p,h=bphp_xnf(ell)
    formula,n=xnf_to_2xnf(source,n0)

    st,eqs,active,stats=bidirectional_gaussian_probe_closure(formula,n)
    macro=detect_complete_alldifferent(source)
    assert macro["status"]=="UNSAT"

    # Affine-scramble only original/source coordinates. Semantics and all
    # linear-algebra invariants are preserved, but the syntax recognizer should
    # no longer see weight-two XOR edges.
    scrambled_source=transform_source_xnf(source,n0)
    scrambled_formula=transformed_formula(formula,n0,n)

    st_s,eqs_s,active_s,stats_s=bidirectional_gaussian_probe_closure(
        scrambled_formula,n
    )
    macro_s=detect_complete_alldifferent(scrambled_source)
    assert macro_s["status"]=="OPEN"

    # Normal rank / represented-matroid connectivity are invariant under the
    # invertible change on source coordinates.
    lines=line_points(active)
    lines_s=line_points(active_s)
    normals=[g for L in lines for g in L]
    normals_s=[g for L in lines_s for g in L]
    comps,ranks=represented_matroid_components(normals)
    comps_s,ranks_s=represented_matroid_components(normals_s)
    assert len(comps)==len(comps_s)==1
    assert ranks==ranks_s

    return {
        "ell":ell,
        "pigeons":p,
        "domain":h,
        "plain_probe":st,
        "plain_rank":0 if eqs is None else len(eqs),
        "plain_alldifferent":"UNSAT",
        "scrambled_probe":st_s,
        "scrambled_rank":0 if eqs_s is None else len(eqs_s),
        "scrambled_alldifferent":macro_s["status"],
        "normal_component_count":1,
        "normal_rank":ranks[0],
        "plain_probes":stats["probes"],
        "scrambled_probes":stats_s["probes"],
    }


def main():
    verify_subspace_intersection()

    frozen=verify_frozen_obstruction()
    php=[verify_php_probe(k) for k in range(3,6)]
    bphp=[verify_bit_php_probe(ell) for ell in range(2,5)]

    print("BIDIRECTIONAL GAUSSIAN PROBE CLOSURE: PASS")
    print("frozen 3-variable UGIC obstruction -> UNSAT without recursive branching",frozen)
    print("PHP probe receipts:")
    for r in php:
        print(r)
    print("bit-PHP / affine-scrambled bit-PHP receipts:")
    for r in bphp:
        print(r)
    print("resource bound: <= n strict rank rounds, O(m) two-sided UGIC probes per round")
    print("this is a polynomial closure layer, not a DPLL search tree")
    print("prior-art ceiling: failed-literal/lookahead/common-consequence style; no novelty claim")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
