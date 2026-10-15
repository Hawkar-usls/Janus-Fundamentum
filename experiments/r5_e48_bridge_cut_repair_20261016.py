#!/usr/bin/env python3
"""R5 E4.8: independent exact 2-lift replay and bridge-cut removal scout.

CROSS-SWITCH A UNSAT + B SAT gives cheap 2-edge cut by design.
Try SECOND disjoint cross-component switch. To preserve all
two E4.8 ternary witnesses, require yA[a2]=yB[b2] for both,
and avoid original switched source rows. This ensures all
integer Ay=2 witnesses survive by direct row check, but
DOES NOT by itself preserve UNSAT. We independently enumerate
EVERY GF2 parity solution for each candidate and accept ONLY
an EXACT certified UNSAT legal connected C2 with no 1- or
2-edge cuts (computed by independent bridge search).

To certify no size-2 edge cut, for each original edge e,
remove it and independently run lowlink Tarjan; any bridge
f remaining gives separating pair {e,f}. Cubic regularity
ensures no original edge bridge, but the code rechecks.

If no candidates meet criteria in bounded search, status
NOT FOUND, never universal impossibility. If found, construct
one joint-voltage signed 2-lift realizing two distinct z
and independently enumerate full GF2 parity set when
dimension small enough (else honestly UNKNOWN).
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from r5_e48_connected_multi_z_bridge_20261016 import (
    bridge,joint_cover,exact_sat_words,incidence_component_sizes
)
from r5_cooperative_scl_coverage_20261015 import (
    fixtures,validate_scl,valid_witness,fingerprint
)


def no_small_edge_cut(rows):
    n=len(rows)
    E=[(i,j) for i,row in enumerate(rows) for j in row]
    num=2*n
    def components_and_bridges(excluded):
        graph=[[] for _ in range(num)]
        for index,(i,j) in enumerate(E):
            if index in excluded:continue
            graph[i].append((n+j,index))
            graph[n+j].append((i,index))
        order=[-1]*num
        low=[0]*num
        timer=0
        bridges=[]
        comps=0
        def dfs(u,parent_edge):
            nonlocal timer
            order[u]=low[u]=timer
            timer+=1
            for v,e in graph[u]:
                if e==parent_edge:continue
                if order[v]==-1:
                    dfs(v,e)
                    low[u]=min(low[u],low[v])
                    if low[v]>order[u]:bridges.append(e)
                else:
                    low[u]=min(low[u],order[v])
        for start in range(num):
            if order[start]==-1:
                comps+=1
                dfs(start,-1)
        return comps,bridges
    comps,bridges=components_and_bridges(set())
    assert comps==1
    if bridges:
        return {"at_least_three_edge_connected":False,
                "witness_edges":[E[bridges[0]]],
                "witness_size":1}
    for index,e in enumerate(E):
        c,bridge_after=components_and_bridges({index})
        if c!=1:
            return {"at_least_three_edge_connected":False,
                    "witness_edges":[e],"witness_size":1}
        if bridge_after:
            return {"at_least_three_edge_connected":False,
                    "witness_edges":[e,E[bridge_after[0]]],
                    "witness_size":2}
    return {"at_least_three_edge_connected":True,
            "witness_edges":None,"witness_size":None,
            "all_single_edge_deletions_and_bridges_checked":len(E)}


def controlled_second_switch(C,Y,nA,old_r,old_s):
    n=len(C)
    Aedges=[(i,j) for i,row in enumerate(C)
            if i<nA and i!=old_r for j in row if j<nA]
    Bedges=[(i,j) for i,row in enumerate(C)
            if i>=nA and i!=nA+old_s for j in row if j>=nA]
    for e1 in Aedges:
        i,a=e1
        for e2 in Bedges:
            k,b=e2
            if not all(item["y"][a]==item["y"][b]
                       for item in Y):
                continue
            V=[list(row) for row in C]
            V[i].remove(a);V[i].append(b)
            V[k].remove(b);V[k].append(a)
            try:
                validate_scl(V)
            except ValueError:
                continue
            yield e1,e2,tuple(tuple(sorted(row)) for row in V)


def independent_lift_count(rows,capacity=1<<15):
    oracle=exact_sat_words(rows,cap=capacity)
    return {"status":oracle["status"],
            "n":len(rows),"rank":oracle.get("rank"),
            "nullity":oracle["d"],
            "checked":oracle.get("checked"),
            "exact_SAT_count":oracle.get("count"),
            "first_SAT_witness_decimal":(
                str(oracle["witnesses"][0])
                if oracle["status"]=="EXACT" and oracle["count"]
                else None)}


def run(limit=400):
    fixture=json.loads(Path(__file__).with_name(
        "r5_e46_frozen_fixture_20261016.json").read_text())
    A=[tuple(row) for row in fixture["base_rows"]]
    B=fixtures()["AffinePlane9_SAT"]
    C,Y,proof=bridge(A,B,fixture["ternary_y"],2)
    joint,cover=joint_cover(C,Y)
    assert joint["status"]=="JOINT_SAT_2LIFT_WITNESSES_VERIFIED"
    initial=independent_lift_count(cover)
    assert initial["status"]=="EXACT" and initial["exact_SAT_count"]>=4
    assert initial["checked"]==(1<<initial["nullity"])
    old_cut=no_small_edge_cut(C)
    assert not old_cut["at_least_three_edge_connected"]
    counts=Counter()
    success=None
    for e1,e2,C2 in controlled_second_switch(
            C,Y,len(A),proof["switched_A_row"],proof["switched_B_row_local"]):
        if counts["processed"]>=limit:break
        counts["processed"]+=1
        assert len(incidence_component_sizes(C2))==1
        for item in Y:
            assert all(sum(item["y"][j] for j in row)==2 for row in C2)
        if not no_small_edge_cut(C2)["at_least_three_edge_connected"]:
            counts["reject_small_cut"]+=1
            continue
        counts["candidate_no_small_cut"]+=1
        oracle=exact_sat_words(C2,cap=1<<15)
        if oracle["status"]!="EXACT":
            counts["unknown_parity_cap"]+=1
            continue
        if oracle["count"]>0:
            counts["reject_SAT"]+=1
            continue
        counts["independent_UNSAT"]+=1
        combined,lifted=joint_cover(C2,Y)
        if combined["status"]!="JOINT_SAT_2LIFT_WITNESSES_VERIFIED":
            counts["joint_voltage_incompatible"]+=1
            continue
        exact=independent_lift_count(lifted)
        if exact["status"]=="EXACT":
            assert exact["exact_SAT_count"]>=4
        success={
            "second_switch_A_edge":[e1[0],e1[1]],
            "second_switch_B_edge":[e2[0],e2[1]],
            "base_45_rows":[list(row) for row in C2],
            "C2_sha256":fingerprint(validate_scl(C2)),
            "C2_exact_UNSAT_GF2_words":oracle["checked"],
            "C2_nullity":oracle["d"],
            "z_distinct":[str(y["z"]) for y in Y],
            "2lift_joint":combined,
            "2lift_exact_GF2_oracle":exact,
            "no_edge_cut_size_1_or_2":True,
            "original_A_B_partition_cross_edges":4,
            "proved_expander":False
        }
        break
    return {
        "gate":"E4_8_REMOVE_TWO_EDGE_BRIDGE_SCOUT",
        "baseline_SCL45_SAT_2lift_oracle":initial,
        "baseline_has_small_edge_cut":old_cut,
        "second_switch_candidates":dict(counts),
        "first_certified_separator_resistant_multi_z":success,
        "status":("FOUND_CONNECTED_UNSAT_MULTI_Z_WITH_NO_TWO_EDGE_CUT"
                  if success else "NOT_FOUND_WITHIN_BOUNDED_SECOND_SWITCH_SEARCH"),
        "proof_limit":"No cuts of size1 or2 in successful source, not high balanced expansion",
        "all_n_SCL_polynomial":"NOT_CONSTRUCTED","P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--limit",type=int,default=400)
    opt=p.parse_args()
    print(json.dumps(run(opt.limit),indent=2,sort_keys=True))
