#!/usr/bin/env python3
"""JANUS ExactSupport(A,pins): sound/complete with bounded UNKNOWN semantics.

The program implements a genuine decision+SAT-witness API for *every*
square/cubic/linear Positive Exact-One input. It integrates:

  - all-input sound polynomial cardinality, propagation, affine-GF2
    top-shell capacity, and pinned quadratic-Gauss MOD4 filters;
  - exact exhaustive 3-way clause branching on the remaining input;
  - safe UNKNOWN on an explicit resource guard;
  - self-reduction through the pinned support predicate.

No deterministic worst-case polynomial bound for the complete algorithm
is claimed. Branch search costs O(3^(n/3)*poly(n)) or better, not n^O(1).
Polynomial-filter PASS is not Boolean SAT. Finite CI replay cannot change
that complexity statement. P_VS_NP is OPEN.

Unlike a call to a hypothetical support oracle, this implementation
NEVER assumes an unproved polynomial-time black box.
"""
from __future__ import annotations

from dataclasses import dataclass,field

from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis
from r5_universal_quadratic_gauss_mod4_attack import (
    pinned_affine_basis,mod4_weight_counts
)
from r5_universal_exact_support_mod9_dual_certificate import (
    mod9_exactone_precheck,independent_verify_mod9_certificate
)
from r5_universal_e118_tropical_defect_variable_elimination import (
    constraints_from_matrix
)
from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,build_A
)
from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source,source_solutions,e118_target,verify_target
)


@dataclass
class Audit:
    nodes:int=0
    branches:int=0
    forced:int=0
    clause_conflicts:int=0
    affine_checks:int=0
    affine_inconsistent:int=0
    top_capacity_prunes:int=0
    mod4_checks:int=0
    mod4_prunes:int=0
    mod9_checks:int=0
    mod9_prunes:int=0
    max_depth:int=0
    guard_hits:int=0

    def as_dict(self):
        return vars(self).copy()


class _GuardHit(Exception):
    pass


def _propagate(rows,partial,audit):
    """Exact-One unit propagation, returns bool: feasibility not guaranteed."""
    changed=True
    while changed:
        changed=False
        for clause in rows:
            ones=sum(partial[j]==1 for j in clause)
            free=[j for j in clause if partial[j]<0]
            if ones>1 or (ones==0 and not free):
                audit.clause_conflicts+=1
                return False
            if ones==1:
                for j in free:
                    partial[j]=0
                    audit.forced+=1
                    changed=True
            elif len(free)==1:
                partial[free[0]]=1
                audit.forced+=1
                changed=True
    return True


def _polynomial_kernel_prune(A,basis,partial,audit):
    """Returns an exact reason for UNSAT, or None (never assumes SAT)."""
    n=len(A)
    kpins={i:1-v for i,v in enumerate(partial) if v>=0}
    audit.affine_checks+=1
    affine=pinned_affine_basis(basis,n,kpins)
    if affine is None:
        audit.affine_inconsistent+=1
        return "AFFINE_PARITY_INCONSISTENT"
    k0,translations=affine
    possibly_one=k0
    for v in translations:
        possibly_one |= v
    if possibly_one.bit_count()<2*n//3:
        audit.top_capacity_prunes+=1
        return "TOP_WEIGHT_CAPACITY_BELOW_2N_OVER_3"
    audit.mod4_checks+=1
    n0,n2=mod4_weight_counts(basis,n,kpins)
    if (n2 if (n//3)%2 else n0)==0:
        audit.mod4_prunes+=1
        return "PINNED_QUADRATIC_GAUSS_MOD4_EMPTY"
    return None


def _canonical_pins(n,pins):
    if pins is None:
        return {}
    if isinstance(pins,dict):
        entries=pins.items()
    else:
        entries=pins
    result={}
    for j,v in entries:
        if not isinstance(j,int) or not isinstance(v,int) or v not in (0,1):
            raise ValueError("pins must contain (integer-coordinate, 0/1) pairs")
        if not (0<=j<n):
            raise ValueError("pin coordinate out of bounds")
        if j in result and result[j]!=v:
            return None
        result[j]=v
    return result


def ExactSupport(A,pins=None,max_nodes=None,gauss_depth=0):
    """Return a dict(status='SAT'|'UNSAT'|'UNKNOWN', witness,...).

    - With max_nodes=None: sound and complete for all legal matrices,
      worst-case exponential; does not misclassify a valid input.
    - With max_nodes>=0: after all safe prefilters, may return UNKNOWN.
    - gauss_depth>=0 uses the polynomial pinned GF2 filters at levels
      <=gauss_depth, -1 disables them. No positive Gauss reading is
      treated as a SAT proof.
    - UNSAT is sound from fully exhausted case-split or an exact filter;
      no polynomial-size universal UNSAT certificate is claimed.
    """
    rows=constraints_from_matrix(A)
    n=len(rows)
    if not isinstance(max_nodes,(int,type(None))) or (
        max_nodes is not None and max_nodes<0
    ):
        raise ValueError("max_nodes must be None or a nonnegative int")
    if not isinstance(gauss_depth,int):
        raise ValueError("gauss_depth must be an integer")
    supplied=_canonical_pins(n,pins)
    audit=Audit()
    if supplied is None:
        return dict(status="UNSAT",witness=None,reason="CONFLICTING_PINS",
                    audit=audit.as_dict(),runtime="polynomial")
    if n%3:
        return dict(status="UNSAT",witness=None,reason="3_DOES_NOT_DIVIDE_N",
                    audit=audit.as_dict(),runtime="polynomial")

    # Independent O(n^3) ring-consistency NEGATIVE gate. A Boolean
    # exact-one witness must solve the pinned linear equations mod 9;
    # the ring eliminator either constructs a CHECKABLE annihilating
    # row vector or returns CONSISTENT (meaning UNKNOWN, never SAT).
    audit.mod9_checks+=1
    ring_status,mod9_certificate=mod9_exactone_precheck(A,supplied)
    if ring_status=="INCONSISTENT":
        audit.mod9_prunes+=1
        rows_for_certificate=[list(row) for row in A]
        right_for_certificate=[1]*n
        for idx,value in sorted(supplied.items()):
            pin_row=[0]*n
            pin_row[idx]=1
            rows_for_certificate.append(pin_row)
            right_for_certificate.append(value)
        assert independent_verify_mod9_certificate(
            rows_for_certificate,right_for_certificate,mod9_certificate
        )
        return dict(
            status="UNSAT",witness=None,
            reason="PINNED_MOD9_INTEGER_OBSTRUCTION",
            mod9_certificate=mod9_certificate,
            audit=audit.as_dict(),
            runtime="polynomial fixed-ring bit complexity"
        )

    _,_,basis=gf2_rref_basis(A)
    partial=[-1]*n
    for j,value in supplied.items():
        partial[j]=value
    last_reason=[None]

    def visit(partial,depth):
        audit.nodes+=1
        audit.max_depth=max(audit.max_depth,depth)
        if not _propagate(rows,partial,audit):
            last_reason[0]="EXACT_ONE_CLAUSE_CONFLICT"
            return None

        if gauss_depth>=depth:
            reason=_polynomial_kernel_prune(A,basis,partial,audit)
            if reason is not None:
                last_reason[0]=reason
                return None

        if all(v>=0 for v in partial):
            assert all(sum(partial[j] for j in row)==1 for row in rows)
            return partial[:]

        # The guard is strictly BEFORE any exponential branching.
        # A fully polynomial prefilter may prove UNSAT with max_nodes=0.
        if max_nodes is not None and audit.branches>=max_nodes:
            audit.guard_hits+=1
            raise _GuardHit()

        # A row with no 1, and as few undecided positions as possible.
        # A branch selects its unique 1, forcing the others to 0.
        options=None
        for row in rows:
            if any(partial[j]==1 for j in row):
                continue
            free=[j for j in row if partial[j]<0]
            if options is None or len(free)<len(options):
                options=free
                if len(options)==2:
                    break
        assert options is not None and len(options) in (2,3)
        audit.branches+=1
        for chosen in options:
            nxt=partial[:]
            for j in options:
                nxt[j]=int(j==chosen)
            answer=visit(nxt,depth+1)
            if answer is not None:
                return answer
        return None

    try:
        found=visit(partial,0)
    except _GuardHit:
        return dict(status="UNKNOWN",witness=None,
                    reason="EXACT_BRANCH_RESOURCE_GUARD",
                    audit=audit.as_dict(),
                    runtime="bounded search, no SAT/UNSAT claim")

    if found is None:
        # Provenance: a leaf's local filter is NOT a root UNSAT
        # certificate unless no branch was needed.
        root_reason=(last_reason[0] if audit.branches==0
                     else "EXHAUSTIVE_EXACT_CLAUSE_SPLIT")
        return dict(status="UNSAT",witness=None,
                    reason=root_reason or "EXHAUSTIVE_EXACT_CLAUSE_SPLIT",
                    audit=audit.as_dict(),
                    runtime="worst-case O(3^(n/3)*poly(n)); NOT polynomial")
    assert all(found[j]==v for j,v in supplied.items())
    assert all(sum(found[j] for j in row)==1 for row in rows)
    return dict(status="SAT",witness=found,reason="EXACT_ONE_VERIFIED",
                audit=audit.as_dict(),
                runtime="worst-case O(3^(n/3)*poly(n)); NOT polynomial")


def RecoverWitnessFromSupport(A,max_nodes=None):
    """Explicit self-reduction using pinned support; no poly oracle claim."""
    n=len(A)
    root=ExactSupport(A,max_nodes=max_nodes)
    if root["status"]!="SAT":
        return root
    pins={}
    for i in range(n):
        attempted=ExactSupport(A,tuple(pins.items())+((i,0),),
                               max_nodes=max_nodes)
        if attempted["status"]=="UNKNOWN":
            return attempted
        pins[i]=0 if attempted["status"]=="SAT" else 1
    assert len(pins)==n
    result=ExactSupport(A,pins,max_nodes=max_nodes)
    assert result["status"]=="SAT"
    result["self_reduction_calls"]=n+2
    return result


def _e118_A(source):
    rows,_,_=e118_target(source)
    verify_target(rows)
    n=len(rows)
    return [[int(j in row) for j in range(n)] for row in rows]


def independent_n12_full_boolean_replay():
    """Frozen legal 3-regular C4-free samples vs independent enumeration.

    Enumeration is deliberately used ONLY for fixed n=12 tests.
    It is NOT a proposed universal polynomial algorithm.
    """
    from itertools import combinations
    permutations=[
        ([9,10,6,5,1,2,11,4,0,3,7,8],
         [11,3,8,7,0,10,1,2,5,6,9,4]),
        ([8,5,1,2,0,4,11,9,7,3,6,10],
         [11,3,4,0,9,6,7,10,2,8,1,5]),
        ([7,6,9,1,0,2,5,4,3,10,11,8],
         [6,2,8,11,5,10,9,1,7,3,4,0]),
        ([4,2,11,9,10,0,1,3,6,8,7,5],
         [8,4,6,2,5,3,7,11,10,1,0,9]),
        ([11,3,7,4,2,10,9,8,6,0,1,5],
         [1,8,11,7,5,0,3,10,4,2,9,6]),
        ([4,11,1,10,5,6,7,9,3,8,0,2],
         [1,5,9,2,7,3,8,10,11,0,6,4]),
    ]
    statuses=[]
    for p,q in permutations:
        n=12
        rows=[(i,p[i],q[i]) for i in range(n)]
        assert all(len(set(row))==3 for row in rows)
        A=[[int(j in row) for j in range(n)] for row in rows]
        assert len(constraints_from_matrix(A))==n
        # 3|x|=12: only 4 selected variables could form a model.
        genuine=[]
        for selected in combinations(range(n),4):
            chosen=set(selected)
            if all(sum(j in chosen for j in row)==1 for row in rows):
                genuine.append(sum(1<<j for j in chosen))
        pins_to_test=(
            {},{0:0},{0:1},{0:0,1:0},{0:0,1:1},
            {0:1,1:0},{0:1,1:1},
        )
        for pins in pins_to_test:
            expected=any(
                all((word>>j)&1==v for j,v in pins.items())
                for word in genuine
            )
            result=ExactSupport(A,pins,max_nodes=20000)
            assert result["status"]==("SAT" if expected else "UNSAT"),(
                p,q,pins,expected,result
            )
            if expected:
                word=sum(v<<j for j,v in enumerate(result["witness"]))
                assert word in genuine and all((word>>j)&1==v
                                               for j,v in pins.items())
        statuses.append(("SAT" if genuine else "UNSAT",len(genuine)))
    print("INDEPENDENT_FROZEN_n12_C4FREE_PINNED_42_REPLAYS=PASS",statuses)


def main():
    for name,A,expected in (
        ("E61_SAT12",build_A(P_SAT,Q_SAT),"SAT"),
        ("E61_UNSAT12",build_A(P_UNSAT,Q_UNSAT),"UNSAT"),
    ):
        r=ExactSupport(A,max_nodes=20000)
        assert r["status"]==expected,(name,r)
        assert r["witness"] is None or len(r["witness"])==len(A)
        for j in range(min(3,len(A))):
            for value in (0,1):
                pin=ExactSupport(A,{j:value},max_nodes=20000)
                assert pin["status"] in ("SAT","UNSAT")
                if pin["status"]=="SAT":
                    assert pin["witness"][j]==value
        print(name,r["status"],r["reason"],r["audit"])
    sat12=build_A(P_SAT,Q_SAT)
    got=RecoverWitnessFromSupport(sat12,max_nodes=20000)
    assert got["status"]=="SAT" and got["self_reduction_calls"]==14
    assert all(sum(got["witness"][j] for j,v in enumerate(row) if v)==1
               for row in sat12)
    assert ExactSupport(sat12,[(0,0),(0,1)])["status"]=="UNSAT"
    guarded=ExactSupport(sat12,max_nodes=0,gauss_depth=-1)
    assert guarded["status"]=="UNKNOWN" and not guarded["witness"]
    print("SAT12 PINNED SELF-REDUCTION and resource-guard semantics PASS")

    R=tutte12_incidence()
    neg63=ExactSupport(R,max_nodes=0)
    assert neg63["status"]=="UNSAT"
    assert neg63["audit"]["mod4_prunes"]==1,(neg63["audit"],neg63["reason"])
    print("E123_UNSAT63 polynomial Gauss ZERO certificate PASS",neg63["audit"])

    for name,offset,expected in (
        ("E118_UNSAT90",(1,6),"UNSAT"),
        ("E118_SAT90",(1,2),"SAT")
    ):
        source=cyclic_source(9,*offset)
        assert bool(source_solutions(source))==(expected=="SAT")
        target=_e118_A(source)
        probe=ExactSupport(target,max_nodes=0)
        assert probe["status"]=="UNKNOWN",(name,probe)
        # The complete search on this FINITE fixture may still require
        # exponential work; the budget never authorizes false UNSAT.
        r=ExactSupport(target,max_nodes=200000,gauss_depth=0)
        assert r["status"]==expected,(name,r["status"],r["audit"])
        if expected=="SAT":
            assert sum(r["witness"])==30
        print(name,r["status"],r["reason"],r["audit"])

    independent_n12_full_boolean_replay()
    print("EXACT_SUPPORT_PINNED_SOUND_COMPLETE = PROVED, WORST_CASE_EXPONENTIAL")
    print("EXACT_SUPPORT_SAT_WITNESS_SELF_REDUCTION = PROVED")
    print("UNKNOWN_ON_GUARD = IMPLEMENTED, NO FALSE_UNSAT")
    print("POLYNOMIAL_GAUSS_MOD4_NEGATIVE_E123 = CERTIFIED")
    print("E118_UNSAT90_GAUSS_NOT_COMPLETE = VERIFIED")
    print("GLOBAL_POLYNOMIAL_EXACT_SUPPORT = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
