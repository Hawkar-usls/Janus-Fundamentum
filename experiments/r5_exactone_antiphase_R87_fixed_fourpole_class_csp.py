#!/usr/bin/env python3
"""Second-stage exact fixed-class anti-phase R87 CSP, with SAT control.

First-stage 217-skeleton SAFE envelope is NECESSARY, NOT SUFFICIENT.
Here, choose ONE legal physical fourpole orbit-class mask (one of 11
2/3/4-subsets of AAAA,AABB,ABAB,ABBA) per each of six component
blocks. Every complete colouring of the joined sixpole must lie
in its frozen required 87-state relation R87, AND all 87 states
must be obtained.

Proof procedure for an exact fixed instance (skeleton,2cut,outer
assignment):
- compute full external state set for EACH six-vector of local
  fourpole orbit IDs through all 3**9 interblock edge 3-colourings;
- split orbit vectors into SAFE (full support subset target R87)
  and BAD (support contains at least one outside);
- form 11 allowed masks per block, compute bitset of SAFE vectors
  and BAD vectors selected by each physical class mask;
- recursively select one mask from EACH of six blocks. Early prune
  if a required S3 external state orbit has no possible compatible
  SAFE local vector; this prune is monotone, future class choices
  cannot restore it.
- At the leaf check NO compatible BAD vector remains and at least
  ONE compatible SAFE orbit vector covers EACH of the 15 global
  physical S3 orbit classes of R87.

Since six physical classes are colour-name symmetric, supporting
one representative of each of the 15 S3 orbits is EXACTLY equivalent
to supporting all 87 required states. This is a complete SAT/UNSAT
test for the specified one-configuration input, NOT all 20616
first-stage surviving interface placements.

Independent EXACT regressions using the canonical catalogue:
  skeleton 51, cut (0,2), outer order 0123: UNSAT;
  skeleton 52, cut (0,2), outer order 0123: UNSAT;
  skeleton 100,cut (0,2), outer order 0123: UNSAT;
  skeleton 200,cut (0,2), outer order 0123: UNSAT.
Each of these passes the first-stage envelope but fails the true
fixed-physical-fourpole-signature consistency test.

A synthetic positive SAT fixture explicitly exercises the solver
to prevent trivial always-UNSAT regressions. DO NOT confuse that
fixture with a physically realized graph.

Full 217-skeleton final class compatibility remains OPEN.
Full 108-state physical Exact-One gadget NOT CONSTRUCTED;
polynomial native SolveLinearCubicXSAT NOT CONSTRUCTED; P vs NP OPEN.
"""
from collections import Counter
from itertools import combinations,product
import sys

from r5_exactone_six_fourpole_nineedge_simple_skeleton_gate import (
    local_orbit_physical_records
)
from r5_exactone_antiphase_mandatory_R87_217_envelope import (
    mandatory_right87,right_target_mask,load_catalogue,canonical_colours,
)

LEGAL=tuple(sum(1<<i for i in sub)
    for k in (2,3,4) for sub in combinations(range(4),k))
assert len(LEGAL)==11


def local_mask_exact_solver(records,target):
    safe=[(p,b) for p,b in records.items() if not(b&~target)]
    bad=[(p,b) for p,b in records.items() if b&~target]
    mask_safe=[[0]*16 for _ in range(6)]
    mask_bad=[[0]*16 for _ in range(6)]
    for is_safe,collection,table in (
        (True,safe,mask_safe),(False,bad,mask_bad)):
        for i,(p,bits) in enumerate(collection):
            flag=1<<i
            for v,colour_orbit in enumerate(p):
                for mask in LEGAL:
                    if mask&(1<<colour_orbit):
                        table[v][mask]|=flag
    needed={}
    for code in range(729):
        if not (target&(1<<code)):continue
        t=tuple((code//3**(5-j))%3 for j in range(6))
        key=canonical_colours(t)
        needed.setdefault(key,code)
    assert len(needed)==15,(len(needed),needed)
    orbit_witnesses=[]
    for rep in needed.values():
        bit=1<<rep
        orbit_witnesses.append(
            sum(1<<i for i,(_,out) in enumerate(safe) if out&bit))
    assert all(orbit_witnesses)
    counts=Counter()

    def recurse(depth,bad_allowed,safe_allowed,masks):
        if depth==6:
            counts["class_leaf_arrangements_after_safe_prune"]+=1
            if bad_allowed:return None
            counts["forbidden_free_class_arrangements"]+=1
            if all(safe_allowed&w for w in orbit_witnesses):
                return tuple(masks)
            return None
        for mask in LEGAL:
            B=mask_bad[depth][mask]
            S=mask_safe[depth][mask]
            if depth:
                B &= bad_allowed
                S &= safe_allowed
            if not all(S&w for w in orbit_witnesses):
                continue
            result=recurse(depth+1,B,S,masks+[mask])
            if result is not None:return result
        return None

    result=recurse(0,0,0,[])
    return result,dict(counts),len(safe),len(bad)


def positive_control(target):
    # Two ABSTRACT compatible local orbit vectors together realize
    # all desired targets; class {0,1} on every block MUST be SAT.
    codes=[i for i in range(729) if target&(1<<i)]
    assert len(codes)==87
    relation={
        (0,)*6:sum(1<<k for k in codes[:40]),
        (1,)*6:sum(1<<k for k in codes[40:]),
    }
    result,counts,_,_=local_mask_exact_solver(relation,target)
    assert result == (3,)*6,(result,counts)
    print("R87_FIXED_CLASS_EXACT_SOLVER_SYNTHETIC_SAT_CONTROL PASS",flush=True)


def run(catalogue):
    skeletons=load_catalogue(catalogue)
    required=mandatory_right87()
    fixed=((51,(0,2),(0,1,2,3),4140),
           (52,(0,2),(0,1,2,3),17424),
           (100,(0,2),(0,1,2,3),17409),
           (200,(0,2),(0,1,2,3),18339))
    positive_control(right_target_mask(required,(0,2),(0,1,2,3)))
    for idx,cut,order,expected_leaves in fixed:
        records,_=local_orbit_physical_records(skeletons[idx])
        mask=right_target_mask(required,cut,order)
        solution,stats,safe_count,bad_count=local_mask_exact_solver(
            records,mask)
        assert solution is None
        assert stats["class_leaf_arrangements_after_safe_prune"]==expected_leaves
        assert stats["forbidden_free_class_arrangements"]==0
        print("FIXED_6BLOCK_R87_11_CLASS_EXACT_UNSAT",{
            "skeleton_index":idx,
            "cut_port_positions":cut,
            "four_other_port_assignment":order,
            "good_safe_orbit_patterns":safe_count,
            "bad_orbit_patterns":bad_count,
            "traversed_leaf_class_assignments":expected_leaves,
            "fixed_instance_SAT":False
        },flush=True)
    print("REMAINING_R87_ENVELOPE_POSITIVES_NOT_ALL_EXACTLY_CLASS_TESTED")
    print("PHYSICAL_108_GOOD_ONLY_GRAPH_OPEN; P_VS_NP_OPEN")


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python verifier.py /tmp/sixblock217.txt")
    run(sys.argv[1])
