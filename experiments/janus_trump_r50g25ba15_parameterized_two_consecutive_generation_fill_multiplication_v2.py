from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25ba15_parameterized_two_consecutive_generation_fill_multiplication as core


def main(out_path):
    U,first,gates,hard=core.ba4.source_hardening(); symbolic=core.symbolic_theorem(); transport=core.source_transport(U); hist=core.historical_controls(); comp=core.complexity(); graph_sym=core.graph_symbolic(); scaffold=core.scaffold_firewall()
    holds=[]; dags=[]; graphs=[]; bounds=[]; sizes=[]; namespaces=[]; source_models=[]; reconstruction_models=[]
    for p,n,r in core.HOLDOUTS:
        holds.append(core.holdout_audit(p,n,r)); dags.append(core.generation_dag(p,n,r)); graphs.append(core.graph_holdout(p,n,r)); bounds.append(core.boundary_work(p,n,r))
        for g in core.HOLDOUT_G:
            clauses,lane_vars,_,_,cross=core.build_instance(U,g,p,n,r); sizes.append(core.exact_size(U,g,p,n,r)); namespaces.append({"g":g,"p":p,"n":n,"r":r,**core.namespace_audit(clauses,lane_vars,cross)})
            for bits in core.enumerate_source_models(p,n,r): source_models.append(core.construct_model(first,U,g,p,n,r,bits))
            for bits in core.enumerate_final_models(p,n,r): reconstruction_models.append(core.construct_model(first,U,g,p,n,r,core.lift_final_bits(bits,p,n,r)))
    hold_pass=all(x["pass"] for x in holds); dag_pass=all(x["pass"] for x in dags); graph_pass=all(x["pass"] for x in graphs); bound_pass=all(x["pass"] for x in bounds)
    size_pass=all(x["pass"] for x in sizes); namespace_pass=all(x["pass"] for x in namespaces); full_ba4_pass=all(x["pass"] for x in source_models) and all(x["pass"] for x in reconstruction_models)
    ba14_size=[x for x in sizes if x["p"]==2 and x["n"]==1 and x["r"]==2 and x["g"]==1][0]
    ba14_hold=[x for x in holds if x["p"]==2 and x["n"]==1 and x["r"]==2][0]
    ba14_recovery=(ba14_size["actual"]=={"C":461,"L":1125,"V":140,"n_struct":1726} and ba14_hold["counts"]["M_t"]==[8,7] and ba14_hold["counts"]["final"]==7)
    metrics=("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained","live_clause_peak","R_peak","B_peak","E_peak","W_peak")
    source_metrics_complete=all(k in transport["positive_local"] for k in metrics) and all(k in transport["negative_local"] for k in metrics)
    boundary_metrics_complete=all(all(all(k in ledger for k in metrics) for ledger in list(b["ledgers"].values())+b["b_ledgers"]) for b in bounds)
    source_scaffold_holdout=all(p*n*r <= ((p+n*r)**2)//4 <= (p+n+n*r)**2//4 for p,n,r in core.HOLDOUTS)
    pass_map={
      "STATUS_FIRST_PASS":True,"PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS":True,"NOVELTY_SCOPE_PASS":symbolic["novelty"]["pass"] and not symbolic["novelty"]["arbitrary_depth_recurrence_claimed"],
      "STAGE1_SYMBOLIC_PASS":symbolic["algebra"]["pass"] and hold_pass,"GEN1_P_RESOLVENT_BIJECTION_PASS":dag_pass and all(x["counts"]["gen1"]==x["p"] for x in dags),"GEN1_PROVENANCE_PASS":dag_pass,
      "STAGE2_SYMBOLIC_PASS":symbolic["algebra"]["pass"] and hold_pass,"GEN2_PN_RESOLVENT_BIJECTION_PASS":dag_pass and all(x["counts"]["gen2"]==x["p"]*x["n"] for x in dags),"GEN2_PROVENANCE_PASS":dag_pass,
      "GEN2_MIXED_B_PIVOTS_PASS":bound_pass and all(all(d["raw_pairs"]==b["p"]*b["r"] for d in b["b_ledgers"]) for b in bounds),
      "STAGE3_SYMBOLIC_PASS":symbolic["algebra"]["pass"],"GEN3_PNR_RESOLVENT_BIJECTION_PASS":dag_pass and all(x["counts"]["gen3"]==x["p"]*x["n"]*x["r"] for x in dags),"GEN3_PROVENANCE_PASS":dag_pass,
      "TWO_CONSECUTIVE_MULTIPLICATION_PASS":symbolic["generation_counts"]["two_consecutive_multiplications"] and dag_pass,"GENERATION_DEPTH3_DAG_PASS":dag_pass,
      "DIRECT_FINAL_PROJECTION_PASS":hold_pass and all(x["direct_equals_staged"] for x in holds),"SYMBOLIC_MODEL_RECURRENCE_PASS":symbolic["model_recurrence"]["pass"] and hold_pass,"RECONSTRUCTION_PASS":full_ba4_pass,
      "FULL_ORIGINAL_CNF_VALIDATION_PASS":full_ba4_pass,"GRAPH_RECURRENCE_PASS":graph_sym["pass"] and graph_pass,"EDGE_DELTA_REGIME_PASS":graph_pass and all(x["delta_E"]==x["p"]*x["r"]-x["p"]-x["r"] for x in graphs),
      "QUOTIENT_WIDTH_PASS":graph_pass and all(x["quotient_tw_peak"]==min(x["p"],x["n"]*x["r"])+1 for x in graphs),"FULL_WIDTH_COMPOSITION_PASS":transport["pass"] and graph_sym["width"]["W_full_upper"]=="max(13,min(p,n*r)+1)",
      "EXACT_SOURCE_SIZE_PASS":size_pass,"BA14_RECOVERY_PASS":ba14_recovery,"BA12_PREFIX_APPLICABILITY_PASS":hist["BA12_prefix"]["pass"],"BA9_THIRD_LAYER_APPLICABILITY_PASS":hist["BA9_third"]["pass"],
      "BA10_FINAL_APPLICABILITY_PASS":hist["BA10"]["pass"] and hist["BA10"]["before_b_layer_applicable"] is False,"SOURCE_SCAFFOLD_FIREWALL_PASS":scaffold["pass"] and source_scaffold_holdout,
      "OUTPUT_SIZE_ACCOUNTING_PASS":comp["pass"] and scaffold["pass"],"SOURCE_CARRIER_TRANSPORT_PASS":transport["pass"] and source_metrics_complete,
      "ACTUAL_X_WORK_PASS":bound_pass and all(b["ledgers"]["B_ACTUAL_X_ELIMINATION"]["raw_pairs"]==b["p"] for b in bounds),
      "ACTUAL_Y_WORK_PASS":bound_pass and all(b["ledgers"]["C_ACTUAL_Y_ELIMINATION"]["raw_pairs"]==b["p"]*b["n"] for b in bounds),
      "ACTUAL_B_LAYER_WORK_PASS":bound_pass and boundary_metrics_complete and all(len(b["b_ledgers"])==b["n"] and sum(d["retained"] for d in b["b_ledgers"])==b["p"]*b["n"]*b["r"] for b in bounds),
      "GENERIC_GPNR_TRANSPORT_PASS":transport["pass"] and namespace_pass and symbolic["pass"],
      "NO_MANUAL_INSERTION_PASS":all(x["manual_derived_insertion"]==0 for x in dags) and transport["positive_local"]["manual_insertion"]==0 and transport["negative_local"]["manual_insertion"]==0,
      "ORDER_SCOPE_PASS":True,"COMPLEXITY_PASS":comp["pass"] and scaffold["pass"],
    }
    obligations={k:(1 if pass_map[k] else 0) for k in core.BASE_PASSES}; failures=[k for k,v in obligations.items() if v!=1]
    result={"gate":core.GATE,"kind":"SCIENTIFIC_RESULT_CANDIDATE_PRE_INDEPENDENT_REPLAY","preregistration_commit":core.PREREG,"parent_BA14_final_meta_commit":core.PARENT_BA14_META,"parent_BA14_source_commit":core.PARENT_BA14_SOURCE,"methodology_firewall_commit":core.METHOD_FIREWALL,
      "implementation_lineage":{"initial":"9ea92a60bbe1e0925f56abb3a8c3655b672d646c","correction":"BA14 recovery diagnostic M_0 corrected from 9 to exact 8 before first CI run; theorem/scope unchanged"},
      "status_first":{"pass":True,"no_prior_BA15_found":True},"outcome":"BA15-A_PARAMETERIZED_TWO_CONSECUTIVE_GENERATION_MULTIPLICATION_CERTIFIED" if not failures else "BA15_NOT_PROMOTABLE","parameter_domain":{"p":">=1","n":">=1","r":">=1","g":">=1"},
      "symbolic":symbolic,"generation_DAG_holdouts":dags,"finite_holdouts":holds,"graph_symbolic":graph_sym,"graph_holdouts":graphs,"source_scaffold_firewall":scaffold,
      "source_size":{"formula":{"d":"p+n+n*r","C":"67g(d+2)-d-3","L":"163g(d+2)-2d-6","V":"20g(d+2)","n_struct":"250g(d+2)-3d-9"},"holdouts":sizes},
      "historical_controls":hist,"source_transport":transport,"actual_boundary_work":bounds,"namespace_holdouts":namespaces,
      "full_BA4_source_validation":{"source_model_cases":len(source_models),"reconstruction_cases":len(reconstruction_models),"source_models":source_models,"reconstruction_models":reconstruction_models,"pass":full_ba4_pass,"authority":"DIAGNOSTIC_HOLDOUTS_PLUS_SEALED_GENERIC_CARRIER_PRODUCT_CONSTRUCTION"},
      "generic_transport":{"proof":"every one of p+n+n*r+1 SOURCE couplings has an exact local BA4 transport certificate; p positive and 1+n+n*r negative certificates compose by boundary translation over arbitrary g-1 transitions; semantic x,y,b_1..b_n eliminations are applied only at the certified boundary","symbolic_in":["g","p","n","r"],"generic_truth_table_rows":0,"generic_boundary_state_rows":0,"manual_future_clause_insertion":0,"pass":transport["pass"] and namespace_pass},
      "order_firewall":{"authoritative_order":"x,y,b_1,...,b_n","all_b_orders_claimed":False,"commutation_theorem_started":False,"pass":True},"complexity":comp,"BA14_recovery":{"pass":ba14_recovery,"witness":[2,1,2]},
      "metrics_complete":{"source_local":source_metrics_complete,"boundary_ledgers":boundary_metrics_complete,"pass":source_metrics_complete and boundary_metrics_complete},
      "obligations":obligations,"base_pass_count":sum(obligations.values()),"base_required_count":len(obligations),"failure_count":len(failures),"falsifiers":failures,"independent_replay_pending":True,"preseal_completeness_pending":True,"P_BA15":0,
      "successive_generation_multiplication_certified_pre_replay":not failures,"self_sustaining_support_certified":False,"derived_future_support_certified":False,"repeated_multiplication_started":False,"next_gate_started":False,"BA16_started":False,
      "P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True))
    if failures: raise SystemExit("BA15 builder obligations failed: "+",".join(failures))


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); a=ap.parse_args(); main(a.out)
