from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

Q=2
BLOCK=30
SOURCE_ALLOWED={"01111","10000","10001","10010","10011","10111","11111"}
STAGE1_ALLOWED={"0111","1000","1001","1010","1011","1111"}
FINAL_ALLOWED={"011","100","101","110","111"}
HOLDOUT_G=(1,2,3,5)


def canon_clause(c):
    s=set(int(x) for x in c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda z:(abs(z),z<0)))


def minimize_formula(clauses):
    xs=[]
    for c in clauses:
        z=canon_clause(c)
        if z is not None: xs.append(z)
    xs=sorted(set(xs),key=lambda c:(len(c),c))
    out=[]
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out): continue
        out.append(c)
    return tuple(sorted(out))


def dp_step(formula,var):
    formula=minimize_formula(formula)
    pos=[c for c in formula if var in c]
    neg=[c for c in formula if -var in c]
    rest=[c for c in formula if var not in c and -var not in c]
    raw=[]; taut=0
    for a in pos:
        for b in neg:
            z=canon_clause((set(a)-{var}) | (set(b)-{-var}))
            if z is None: taut+=1
            else: raw.append(z)
    dup=len(raw)-len(set(raw))
    new=minimize_formula(rest+raw)
    retained=[c for c in new if c not in rest]
    return new,{"raw_pairs":len(pos)*len(neg),"tautological_pairs":taut,"non_tautological_pairs":len(raw),"duplicates":dup,"retained":len(retained)}


def source_ok(a,x,y,b1,b2):
    return (a or x) and ((not x) or y) and ((not y) or b1) and ((not y) or b2)


def stage1_ok(a,y,b1,b2):
    return (a or y) and ((not y) or b1) and ((not y) or b2)


def final_ok(a,b1,b2):
    return (a or b1) and (a or b2)


def exact_sets():
    src={"".join(map(str,z)) for z in product((0,1),repeat=5) if source_ok(*z)}
    s1={"".join(map(str,z)) for z in product((0,1),repeat=4) if stage1_ok(*z)}
    fin={"".join(map(str,z)) for z in product((0,1),repeat=3) if final_ok(*z)}
    direct=set(); staged=set()
    for a,b1,b2 in product((0,1),repeat=3):
        bits=f"{a}{b1}{b2}"
        if any(source_ok(a,x,y,b1,b2) for x,y in product((0,1),repeat=2)): direct.add(bits)
        if any(stage1_ok(a,y,b1,b2) for y in (0,1)): staged.add(bits)
    return src,s1,fin,direct,staged


def source_clauses(qs):
    a,x,y,b1,b2=map(int,qs)
    return [(a,x),(-x,y),(-y,b1),(-y,b2)]


def build(U,g):
    base,lane_vars,_=ba4.build_instance(U,g,5)
    qs=[Q+ba4.lane_off(g,i) for i in range(5)]
    cross=source_clauses(qs)
    return list(base)+cross,lane_vars,qs,cross


def clause_ok(a,c):
    return any((bool(a[abs(int(l))]) if int(l)>0 else not bool(a[abs(int(l))])) for l in c)


def replay_full_model(first,U,g,bits):
    assignment={}
    for lane,bit in enumerate(bits):
        proto=first[(int(bit),1-int(bit))]
        lo=ba4.lane_off(g,lane)
        for block in range(g):
            off=lo+BLOCK*block
            for v,val in proto.items(): assignment[int(v)+off]=bool(val)
    clauses,lane_vars,qs,cross=build(U,g)
    bad=[c for c in clauses if not clause_ok(assignment,c)]
    qvec=[]
    for lane,bit in enumerate(bits):
        lo=ba4.lane_off(g,lane)
        qvec.append([int(bool(assignment[Q+lo+BLOCK*j])) for j in range(g)])
    return not bad and all(qvec[i]==[int(bits[i])]*g for i in range(5))


def local_transport(U,orientation):
    g=2
    base,lane_vars,_=ba4.build_instance(U,g,2)
    qs=[Q+ba4.lane_off(g,i) for i in range(2)]
    source=(qs[1],qs[0]) if orientation=="positive" else (-qs[0],qs[1])
    target=(qs[1]+BLOCK,qs[0]+BLOCK) if orientation=="positive" else (-(qs[0]+BLOCK),qs[1]+BLOCK)
    cur=minimize_formula(list(base)+[source])
    totals={"raw_pairs":0,"tautological_pairs":0,"non_tautological_pairs":0,"duplicates":0,"retained":0}
    live=len(cur); neighpeak=0
    for lane in range(2):
        lo=ba4.lane_off(g,lane)
        for base_v in ba4.az.ORDER:
            var=int(base_v)+lo
            neigh=set()
            for c in cur:
                if var in c or -var in c:
                    neigh|={abs(int(l)) for l in c if abs(int(l))!=var}
            neighpeak=max(neighpeak,len(neigh))
            cur,m=dp_step(cur,var)
            for k in totals: totals[k]+=m[k]
            live=max(live,len(cur))
    membership={int(v):i for i,vs in enumerate(lane_vars) for v in vs}
    cross=[c for c in cur if len({membership[abs(int(l))] for l in c})>1]
    return totals,live,neighpeak,minimize_formula(cross)==minimize_formula([target])


def boundary_replay(g=2,boundary=1):
    qs=[Q+ba4.lane_off(g,i)+BLOCK*boundary for i in range(5)]
    a,x,y,b1,b2=qs
    F0=minimize_formula([(a,x),(-x,y),(-y,b1),(-y,b2)])
    G1,mx=dp_step(F0,x)
    E1=minimize_formula([(a,y),(-y,b1),(-y,b2)])
    G2,my=dp_step(G1,y)
    E2=minimize_formula([(a,b1),(a,b2)])
    return G1,E1,G2,E2,mx,my


def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text())
    errors=[]
    obligations={}

    src,s1,fin,direct,staged=exact_sets()
    obligations["FRONTIER_HARDENING_PASS"]=int(r["BA11_frontier_hardening"]["BA7_already_certified_mixed_second_pivot_1_to_1"] and r["BA11_frontier_hardening"]["generation_pattern"]=="1->2")
    obligations["STAGE1_ALGEBRA_PASS"]=int(r["BA11_2_3_4_5_symbolic"]["stage1"]["existential"]=="a OR y")
    obligations["STAGE1_EXACT_PROJECTION_PASS"]=int(s1==STAGE1_ALLOWED)
    obligations["GEN1_PROVENANCE_PASS"]=int(r["BA11_1_15_generation_DAG"]["nodes"]["D"]["generation"]==1 and r["BA11_1_15_generation_DAG"]["edges"][0]["parents"]==["S_1","S_2"])
    obligations["STAGE2_MIXED_POLARITY_PASS"]=int(r["BA11_2_3_4_5_symbolic"]["stage2"]["P_y"]==1 and r["BA11_2_3_4_5_symbolic"]["stage2"]["N_y"]==2)
    obligations["STAGE2_TWO_RESOLVENT_PASS"]=int(r["BA11_12_actual_boundary_cascade"]["GEN2_NEW_FILL"]==2)
    obligations["GEN2_PROVENANCE_PASS"]=int(r["BA11_1_15_generation_DAG"]["nodes"]["H_1"]["generation"]==2 and r["BA11_1_15_generation_DAG"]["nodes"]["H_2"]["generation"]==2)
    obligations["DIRECT_TWO_VARIABLE_PROJECTION_PASS"]=int(direct==staged==FINAL_ALLOWED)
    obligations["EXHAUSTIVE_5BIT_SOURCE_PASS"]=int(src==SOURCE_ALLOWED)
    obligations["STAGE1_FINITE_AUDIT_PASS"]=int(s1==STAGE1_ALLOWED)
    obligations["FINAL_FINITE_AUDIT_PASS"]=int(fin==FINAL_ALLOWED)

    U,first,gates,hard=ba4.source_hardening()
    parent_ok=all(bool(v) for v in gates.values())
    source_cases=0; recon_cases=0; full_ok=True; size_ok=True
    for g in HOLDOUT_G:
        clauses,lane_vars,qs,cross=build(U,g)
        C=len(clauses); L=sum(len(c) for c in clauses); V=len(set().union(*lane_vars)); ns=C+L+V
        size_ok=size_ok and (C,L,V,ns)==(335*g-6,815*g-12,100*g,1250*g-18)
        for s in sorted(SOURCE_ALLOWED):
            source_cases+=1
            full_ok=full_ok and replay_full_model(first,U,g,tuple(map(int,s)))
        for f in sorted(FINAL_ALLOWED):
            a,b1,b2=map(int,f); bits=(a,1-a,1-a,b1,b2)
            recon_cases+=1
            full_ok=full_ok and replay_full_model(first,U,g,bits)
    obligations["CNF_REALIZATION_PASS"]=int(parent_ok and full_ok and size_ok)

    pos,plive,pwidth,ppass=local_transport(U,"positive")
    neg,nlive,nwidth,npass=local_transport(U,"negative")
    expected_pos={"raw_pairs":2320,"tautological_pairs":782,"non_tautological_pairs":1538,"duplicates":78,"retained":414}
    expected_neg={"raw_pairs":2001,"tautological_pairs":658,"non_tautological_pairs":1343,"duplicates":57,"retained":383}
    agg={
      "raw_pairs_per_transition":pos["raw_pairs"]+3*neg["raw_pairs"],
      "tautological_pairs_per_transition":pos["tautological_pairs"]+3*neg["tautological_pairs"],
      "non_tautological_pairs_per_transition":pos["non_tautological_pairs"]+3*neg["non_tautological_pairs"],
      "duplicates_per_transition":pos["duplicates"]+3*neg["duplicates"],
      "retained_per_transition":pos["retained"]+3*neg["retained"],
    }
    expected_agg={"raw_pairs_per_transition":8323,"tautological_pairs_per_transition":2756,"non_tautological_pairs_per_transition":5567,"duplicates_per_transition":249,"retained_per_transition":1563}
    obligations["GENERIC_TRANSPORT_PASS"]=int(ppass and npass and pos==expected_pos and neg==expected_neg and agg==expected_agg)
    obligations["NO_MANUAL_INSERTION_PASS"]=int(r["BA11_11_13_source_transport"]["manual_future_boundary_source_insertion"]==0 and r["BA11_12_actual_boundary_cascade"]["manual_derived_insertion"]==0)

    recon_ok=True
    for bits in FINAL_ALLOWED:
        a,b1,b2=map(int,bits); x=y=1-a
        recon_ok=recon_ok and stage1_ok(a,y,b1,b2) and source_ok(a,x,y,b1,b2)
    obligations["RECONSTRUCTION_PASS"]=int(recon_ok)
    obligations["FULL_ORIGINAL_CNF_VALIDATION_PASS"]=int(full_ok)

    G1,E1,G2,E2,mx,my=boundary_replay()
    obligations["GRAPH_GENERATION_ACCOUNTING_PASS"]=int(G1==E1 and G2==E2 and mx["raw_pairs"]==1 and my["raw_pairs"]==2)
    obligations["WIDTH_PASS"]=int(r["BA11_9_width"]["quotient_tw_peak"]==2 and r["BA11_9_width"]["W_full_upper"]==13)
    obligations["ACTUAL_CARRIER_WORK_PASS"]=int(pos==expected_pos and neg==expected_neg and mx["raw_pairs"]==1 and my["raw_pairs"]==2)
    obligations["CASCADE_DAG_PASS"]=int(r["BA11_1_15_generation_DAG"]["generation1_parent_required_for_generation2"] is True and len(r["BA11_1_15_generation_DAG"]["edges"])==3)
    obligations["COMPLEXITY_PASS"]=int(r["BA11_16_complexity"]["source_transport_raw_pairs_exact"]=="8323(g-1)" and r["BA11_16_complexity"]["T_total"]=="O(n log n)")

    if r["preregistration_commit"]!="b9cfe692b9d7b1f7aa5d903f533991aa92673238": errors.append("prereg_commit")
    if r["parent_BA10_final_meta_commit"]!="66eb10d8850079b4648863d43d7271563699616a": errors.append("parent_meta")
    if r["outcome"]!="BA11-A_MINIMAL_SECOND_GENERATION_RESOLUTION_FANOUT_CASCADE_CERTIFIED": errors.append("outcome")
    if r["falsifiers"] or r["failure_count"]!=0: errors.append("falsifiers")
    if r["BA11_14_minimality"]["minimum_source_clauses"]!=4 or r["BA11_14_minimality"]["minimum_distinct_variables"]!=5: errors.append("minimality")
    if not all(v==1 for v in obligations.values()): errors.append("obligations")
    if r["generic_two_stage_p_by_n_started"] or r["next_gate_started"] or r["arbitrary_CNF_coverage_started"]: errors.append("scope")
    if r["P_VS_NP"]!="OPEN" or r["SAT_IN_P"]!="NOT_PROVED": errors.append("firewall")

    p=1
    for v in obligations.values(): p*=v
    x=int(not errors)
    out={
      "status":"PASS" if not errors else "FAIL",
      "error_count":len(errors),
      "errors":errors,
      "obligations":obligations,
      "v_independent_verifier":x,
      "P_BA11":p*x,
      "message_state":"VERIFIED" if not errors else "FALSIFIED",
      "independent_source_kernel_rows":32,
      "independent_stage1_rows":16,
      "independent_final_rows":8,
      "independent_source_full_CNF_cases":source_cases,
      "independent_reconstruction_full_CNF_cases":recon_cases,
      "independent_transport": {"positive":pos,"negative":neg,"aggregate":agg,"positive_live_peak":plive,"negative_live_peak":nlive,"positive_neighbor_width":pwidth,"negative_neighbor_width":nwidth},
      "independent_boundary_work":{"stage1":mx,"stage2":my}
    }
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errors: raise SystemExit("BA11 independent verifier errors: "+",".join(errors))


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--result",required=True); ap.add_argument("--out",required=True); a=ap.parse_args(); main(a.result,a.out)
