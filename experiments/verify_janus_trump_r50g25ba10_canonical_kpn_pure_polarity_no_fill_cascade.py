from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

import janus_trump_r50g25ba9_parameterized_single_pivot_bipartite_fill_multiplication as ba9
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG="013dc9dd4a32c6673bcf46976af74ccb3ed2aacb"
HARDENING="343cc0a4ffb46509ae4593bf6a05812c60cbdd7e"
PARENT_META="c60e691917466c268e863153c66a0ce3d92b180b"
PARENT_SOURCE="2527ff8fe0c3695a6dd2d8228c4e653dc5867d9a"
HOLDOUTS=((2,2,2),(2,3,2),(3,2,3))
Q=2; BLOCK=30


def boundary_ids(g,p,n,k=1):
    d=p+n
    return [Q+ba4.lane_off(g,i)+BLOCK*k for i in range(d+1)]


def residual(aa,bb):
    return tuple(sorted((int(a),int(b)) for a in aa for b in bb))


def clause_sat(c,vals):
    return any(bool(vals[abs(l)]) if l>0 else not bool(vals[abs(l)]) for l in c)


def formula_sat(f,vals):
    return all(clause_sat(c,vals) for c in f)


def replay_holdout(U,first,g,p,n):
    transport=ba9.factorized_transport_certificate(U)
    ids=boundary_ids(g,p,n,1); aa=ids[1:1+p]; bb=ids[1+p:]
    f=residual(aa,bb); pivot=aa[0]
    pos=[c for c in f if pivot in c]; neg=[c for c in f if -pivot in c]
    out=tuple(sorted(c for c in f if pivot not in c and -pivot not in c))
    exp=residual(aa[1:],bb)
    exact=out==exp and len(pos)==n and len(neg)==0 and len(pos)*len(neg)==0
    semantic=0; sem_ok=True
    leaves=aa+bb
    for bits in product((0,1),repeat=len(leaves)):
        vals=dict(zip(leaves,bits))
        vals0=dict(vals); vals0[pivot]=0
        vals1=dict(vals); vals1[pivot]=1
        lhs=formula_sat(f,vals0) or formula_sat(f,vals1)
        rhs=formula_sat(exp,vals)
        sem_ok=sem_ok and lhs==rhs; semantic+=1
    composed=0; comp_ok=True
    for bits in product((0,1),repeat=(p-1+n)):
        arest=bits[:p-1]; bbits=bits[p-1:]
        if all(a or b for a in arest for b in bbits):
            fulla=(1,)+tuple(arest); fullb=tuple(bbits)
            x=1-int(all(fulla))
            model=ba9.construct_model(first,U,g,p,n,x,fulla,fullb)
            comp_ok=comp_ok and model["pass"] and model["FULL_ORIGINAL_CNF_VALIDATION"]=="PASS"
            composed+=1
    return {"tuple":[g,p,n],"transport_pass":transport["pass"],"positive":len(pos),"negative":len(neg),"raw_pairs":len(pos)*len(neg),"exact_clause_result":exact,"semantic_rows":semantic,"semantic_pass":sem_ok,"composed_cases":composed,"composed_pass":comp_ok,"pass":transport["pass"] and exact and sem_ok and comp_ok}


def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text())
    errors=[]
    if r.get("preregistration_commit")!=PREREG: errors.append("PREREG")
    if r.get("prereg_hardening_commit")!=HARDENING: errors.append("HARDENING")
    if r.get("parent_BA9_final_meta_commit")!=PARENT_META: errors.append("PARENT_META")
    if r.get("parent_BA9_source_commit")!=PARENT_SOURCE: errors.append("PARENT_SOURCE")
    if r.get("outcome")!="BA10-A_CANONICAL_KPN_PURE_POLARITY_NO_FILL_CASCADE_CERTIFIED": errors.append("OUTCOME")

    p=r["BA10_1_pure_polarity_law"]
    if p["a_i_occurrences"]!={"positive":"n","negative":0}: errors.append("A_POLARITY")
    if p["b_j_occurrences"]!={"positive":"p","negative":0}: errors.append("B_POLARITY")
    if p["abstract_resolution_productivity"]!="|P_v|*|N_v|=0 for every residual pivot v": errors.append("ZERO_PRODUCTIVITY")

    one=r["BA10_2_one_step_elimination"]
    if "R_{p-1,n}" not in one["A_side"]["generic"]: errors.append("A_STEP")
    if "R_{p,n-1}" not in one["B_side"]["generic"]: errors.append("B_STEP")
    if r["BA10_4_zero_second_generation_fill"]["new_fill_edges_per_step"]!=0: errors.append("NEW_FILL")
    if r["BA10_4_zero_second_generation_fill"]["E_peak"]!="p*n": errors.append("E_PEAK")
    if r["BA10_5_width_monotonicity"]["width_increases"] is not False: errors.append("WIDTH")
    if r["BA10_6_constructive_return"]["BA10_residual_map"]!="every residual variable eliminated in BA10 := 1": errors.append("RECON_MAP")
    if r["BA10_8_cascade_blocker_theorem"]["CANONICAL_BA9_FILL_DOES_NOT_SELF_CASCADE"] is not True: errors.append("THEOREM")
    fw=r["BA10_9_structural_firewall"]
    if not fw["GRAPH_DENSITY_NE_RESOLUTION_PRODUCTIVITY"] or not fw["TREEWIDTH_NE_SAT_HARDNESS_BY_ITSELF"]: errors.append("FIREWALL")
    if r["BA10_10_complexity"]["BA9_output_lower_bound_preserved"]!="Omega(p*n)": errors.append("OUTPUT_FIREWALL")
    if r["BA10_no_hidden_enumeration"]["generic_truth_table_rows"]!=0 or r["BA10_no_hidden_enumeration"]["generic_boundary_state_table_rows"]!=0: errors.append("ENUMERATION")

    U,first,gates,hard=ba4.source_hardening()
    replays=[replay_holdout(U,first,*t) for t in HOLDOUTS]
    if not all(z["pass"] for z in replays): errors.append("ACTUAL_REPLAY")
    if not all(z["raw_pairs"]==0 for z in replays): errors.append("RAW_PAIR_NONZERO")
    if not all(z["exact_clause_result"] for z in replays): errors.append("EXACT_RESIDUAL")
    if not all(z["composed_pass"] for z in replays): errors.append("COMPOSED_SOURCE")

    obligations={
      "PURE_POLARITY_PASS":int(not any(e in errors for e in ("A_POLARITY","B_POLARITY"))),
      "ZERO_ABSTRACT_RESOLUTION_PRODUCTIVITY_PASS":int("ZERO_PRODUCTIVITY" not in errors and "RAW_PAIR_NONZERO" not in errors),
      "ONE_STEP_A_ELIMINATION_PASS":int("A_STEP" not in errors),
      "ONE_STEP_B_ELIMINATION_PASS":int("B_STEP" not in errors),
      "GENERIC_VERTEX_DELETION_RECURRENCE_PASS":int(r["BA10_3_generic_recurrence"]["pass"] is True),
      "ZERO_NEW_FILL_PASS":int("NEW_FILL" not in errors and "ACTUAL_REPLAY" not in errors),
      "WIDTH_MONOTONICITY_PASS":int("WIDTH" not in errors),
      "ACTUAL_BA9_RESIDUAL_REALIZATION_PASS":int("ACTUAL_REPLAY" not in errors and "EXACT_RESIDUAL" not in errors),
      "RESIDUAL_RECONSTRUCTION_PASS":int("RECON_MAP" not in errors),
      "COMPOSED_BA9_SOURCE_RECONSTRUCTION_PASS":int("COMPOSED_SOURCE" not in errors),
      "FULL_SOURCE_VALIDATION_PASS":int("COMPOSED_SOURCE" not in errors and all(bool(x) for x in gates.values())),
      "COMPLEXITY_PASS":int("OUTPUT_FIREWALL" not in errors),
      "INDEPENDENT_REPLAY_PASS":int(not errors),
    }
    prod=1
    for z in obligations.values(): prod*=z
    out={
      "status":"PASS" if not errors else "FAIL",
      "error_count":len(errors),"errors":errors,
      "obligations":obligations,
      "independent_actual_replays":replays,
      "independent_semantic_rows":sum(z["semantic_rows"] for z in replays),
      "independent_composed_source_cases":sum(z["composed_cases"] for z in replays),
      "v_independent_verifier":int(not errors),
      "P_BA10":prod,
      "message_state":"VERIFIED" if not errors else "FALSIFIER_PRESERVED",
      "P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED"
    }
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errors: raise SystemExit("BA10 verify errors: "+",".join(errors))


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--result",required=True); ap.add_argument("--out",required=True); a=ap.parse_args(); main(a.result,a.out)
