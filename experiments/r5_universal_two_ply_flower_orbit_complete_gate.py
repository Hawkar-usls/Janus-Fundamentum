#!/usr/bin/env python3
"""R5 complete two-ply Isaacs flower test by a PROVED edge-orbit covering.

For Isaacs flower J_k (odd k>=5) the explicit permutation T on the
4k original graph vertices is an automorphism:
  T(a_i)=a_(i+1); T(b_i)=b_(i+1)
  T(c_i)=c_(i+1), T(d_i)=d_(i+1) except at i=k-1
  where c_(k-1)->d_0 and d_(k-1)->c_0.
Its edge orbits are precisely four: (a,b), (a,c/d), (b,b),
(c/d,c/d). The Holyer SCL variable X_(edge,color) is equivariant
under graph automorphisms and the independent S3 permutation of
all colour names. Thus four orbit representatives cover ALL n
Boolean source variables in a constant number of checks.

The inner certified_failed_literal_closure saturates ALL pins,
ALL GF2 and Boolean unit implications, and ALL single-bit probes;
its final SAT/UNSAT/UNKNOWN STATUS is unchanged by source
renaming. Its row and variable scanning order may alter the
certificate event sequence, not its terminal status.

This is a finite barrier test for the EXACT FIXED two-ply expert.
It is NOT a lower bound against all fixed-depth procedures, nor
proof of P!=NP.
"""
from __future__ import annotations
import os
from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl
from r5_universal_certified_failed_literal_boolean_closure import (
    certified_failed_literal_closure, verify_probe_certificate,
    check_original_witness,
)

REP_EDGES=((0,1),(0,2),(1,5),(2,6))


def rotate_vertex(v,k):
    i,role=divmod(v,4)
    j=(i+1)%k
    if i==k-1 and role in (2,3):
        role=5-role
    return 4*j+role


def certify_four_edge_orbits(edges,k):
    edge_set=set(edges)
    assert len(edges)==6*k and len(edge_set)==len(edges)
    assert set(rotate_vertex(v,k) for v in range(4*k))==set(range(4*k))
    perm_edge=lambda e:tuple(sorted(rotate_vertex(v,k) for v in e))
    assert {perm_edge(e) for e in edges}==edge_set
    orbit_sets=[]
    covered=set()
    for rep in REP_EDGES:
        assert rep in edge_set
        orb=set()
        e=rep
        while e not in orb:
            orb.add(e)
            e=perm_edge(e)
        assert e==rep,("orbit did not return to representative",rep)
        assert not (covered & orb),("overlapping reps",rep)
        orbit_sets.append(orb)
        covered|=orb
    assert covered==edge_set,("orbit representatives incomplete",len(covered),len(edge_set))
    assert tuple(map(len,orbit_sets))==(k,2*k,k,2*k)
    return orbit_sets


def main():
    k=int(os.environ.get("FLOWER_K","5"))
    assert k in (5,7)
    rows,n,edges,idx=make_scl(flower(k))
    assert n==18*k
    orbit_sets=certify_four_edge_orbits(edges,k)
    assert {idx[(e,c)] for orb in orbit_sets for e in orb for c in range(3)}==set(range(n))
    assert tuple(idx[(e,0)] for e in REP_EDGES)==(0,3,9,15)
    print(f"FLOWER_J{k}_EXACT_ORBIT_COVERAGE=PROVED sizes="
          f"{tuple(3*len(o) for o in orbit_sets)} n={n}",flush=True)

    root=certified_failed_literal_closure(rows,n)
    assert verify_probe_certificate(rows,n,{},root)
    print(f"FLOWER_J{k}_ROOT={root['status']}",flush=True)
    if root["status"]=="SAT":
        assert check_original_witness(rows,n,{},root["witness"])
        print(f"FLOWER_J{k}_DEPTH2_STATUS=SAT_ORIGINAL_WITNESS")
        return
    if root["status"]=="UNSAT":
        print(f"FLOWER_J{k}_DEPTH2_STATUS=UNSAT_CERTIFIED_AT_ROOT")
        return
    assert root["status"]=="UNKNOWN"
    assert not root["certified_pins"],"unexpected root pin: inspect new symmetry claim"

    status_by_rep={}
    for rep in REP_EDGES:
        v=idx[(rep,0)]
        answers={}
        for bit in (0,1):
            cond={v:bit}
            proof=certified_failed_literal_closure(rows,n,cond)
            assert verify_probe_certificate(rows,n,cond,proof)
            answers[bit]=proof["status"]
            if proof["status"]=="SAT":
                assert check_original_witness(rows,n,cond,proof["witness"])
            print(f"FLOWER_J{k}_ORBIT_REP_X{v}_BIT{bit}="
                  f"{proof['status']} probes={proof['probes']} "
                  f"passes={proof['passes']}",flush=True)
        status_by_rep[v]=answers

    if all(answer[0]=="UNKNOWN" and answer[1]=="UNKNOWN"
           for answer in status_by_rep.values()):
        print(f"FLOWER_J{k}_EXACT_TWO_PLY_ALL_VARIABLES_UNKNOWN="
              "PROVED_BY_AUTOMORPHISM_AND_CERTIFIED_CLOSURE",flush=True)
        print("FIXED_TWO_PLY_GLOBAL_COMPLETENESS=REFUTED_BY_THIS_SOURCE",flush=True)
    else:
        for v,pair in status_by_rep.items():
            if pair[0]=="UNSAT" and pair[1]=="UNSAT":
                print(f"FLOWER_J{k}_DEPTH2_CERTIFIED_UNSAT_BY_X{v}",flush=True)
            elif "SAT" in pair.values():
                print(f"FLOWER_J{k}_DEPTH2_CERTIFIED_SAT_BY_X{v}",flush=True)
            elif "UNSAT" in pair.values():
                print(f"FLOWER_J{k}_ONE_REFUTED_BRANCH_NOT_FULL_TWO_PLY_CLOSURE"
                      f"_X{v}",flush=True)
        print("FIXED_TWO_PLY_GLOBAL_COMPLETENESS=UNDETERMINED_BY_THIS_TEST",flush=True)

    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED",flush=True)
    print("P_VS_NP=OPEN",flush=True)


if __name__=="__main__":
    main()
