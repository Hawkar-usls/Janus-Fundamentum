from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47n_r47m_joint_stack_closure_one_swap_falsifier as r47n

EXPECTED_HASH="eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
EXPECTED_CLV=(76,203,22)
SOURCE_CLAUSE=(-17,20,26)
REPLACEMENT_CLAUSE=(-17,-20,-26)
EXPECTED_ORIGINAL_HASH="6592d016738439574c3cb19a8fc63a4e06e121b7249a9adc7257962bf21e78e9"


def clv(f): return tuple(int(x) for x in r33.measure(r33.canonical_formula(f)))


def reconstruct_r47n():
    _, center=r47n.load_center_original()
    mutated=r47i.mutate_one_clause(center,SOURCE_CLAUSE,REPLACEMENT_CLAUSE)
    if mutated is None: raise AssertionError("R47P2_MUTATION_INVALID")
    mutated=r33.canonical_formula(mutated)
    if r47f.formula_hash(mutated)!=EXPECTED_ORIGINAL_HASH: raise AssertionError("R47P2_ORIGINAL_HASH_DRIFT")
    reached=r47f.reachable_fixpoint(mutated)
    if reached is None: raise AssertionError("R47P2_NO_REACHABLE_FIXPOINT")
    root=r33.canonical_formula(reached["formula"])
    if r47f.formula_hash(root)!=EXPECTED_HASH or clv(root)!=EXPECTED_CLV: raise AssertionError(("R47P2_FIXPOINT_DRIFT",r47f.formula_hash(root),clv(root)))
    return mutated,reached,root


def compact_layer(inp,c,replay):
    seq=[int(s["SA_BVE_var"]) for s in c["normalization"]["segments"] if s.get("SA_BVE_applied")]
    return {"var":int(c["var"]),"input_CLV":list(clv(inp)),"forced_DP_CLV":c["DP"]["measure_after_forced_DP"],"final_CLV":c["final_CLV"],"terminal":c["normalization"]["terminal"],"segment_count":int(c["normalization"]["segment_count"]),"SA_BVE_sequence":seq,"SA_BVE_application_count":int(c["normalization"]["SA_BVE_application_count"]),"accepted_relative_to_layer_input":bool(c["accepted"]),"DP_independent_replay_pass":bool(c["DP_independent_replay_pass"]),"polynomial_intermediate_envelope_pass":bool(c["polynomial_intermediate_envelope_pass"]),"independent_full_replay_pass":bool(replay["pass"])}


def reconstruct_pair_sat(root,first,second):
    if second["normalization"]["semantic_sat"] is not True: return {"applicable":False,"pass":True}
    sr=second["SAT_reconstruction"]
    if not sr["applicable"] or not sr["pass"]: raise AssertionError("R47P2_SECOND_SAT_RECON_FAIL")
    a={int(v):bool(b) for v,b in sr["assignment"].items()}
    for event in reversed(first["normalization"]["reconstruction_events"]):
        if event["kind"]=="R33": a=r33.reconstruct_model(event["result"],a)
        elif event["kind"]=="SA_BVE": a=r42.reconstruct_sa_bve(event["record"],a)
        else: raise AssertionError(event["kind"])
    a=r42.reconstruct_sa_bve(first["DP"],a)
    for v in r33.variables(root): a.setdefault(int(v),False)
    return {"applicable":True,"pass":bool(r33.eval_formula(root,a)),"assignment":a}


def pair(root,v1,v2):
    root=r33.canonical_formula(root)
    first=r47m.macro_candidate_full_closure(root,int(v1))
    if first is None: return None
    rep1=r47m.independent_replay(root,first)
    if not rep1["pass"]: raise AssertionError(("R47P2_FIRST_REPLAY_FAIL",v1,rep1))
    if first["normalization"]["terminal"] is not None or tuple(first["final_CLV"])<clv(root): raise AssertionError(("R47P2_DEPTH1_DRIFT",v1,first["final_CLV"]))
    g1=r33.canonical_formula(first["normalization"]["final_formula"])
    if int(v2)==int(v1) or int(v2) not in r33.variables(g1): return None
    second=r47m.macro_candidate_full_closure(g1,int(v2))
    if second is None: return None
    rep2=r47m.independent_replay(g1,second)
    if not rep2["pass"]: raise AssertionError(("R47P2_SECOND_REPLAY_FAIL",v1,v2,rep2))
    g2=r33.canonical_formula(second["normalization"]["final_formula"])
    terminal=second["normalization"]["terminal"] is not None
    descent=clv(g2)<clv(root)
    sr=reconstruct_pair_sat(root,first,second)
    if not sr["pass"]: raise AssertionError(("R47P2_COMPOSED_SAT_RECON_FAIL",v1,v2))
    return {"first_var":int(v1),"second_var":int(v2),"first":compact_layer(root,first,rep1),"second":compact_layer(g1,second,rep2),"final_CLV":list(clv(g2)),"pair_terminal":bool(terminal),"pair_terminal_kind":second["normalization"]["terminal"],"pair_descent":bool(descent),"accepted":bool(terminal or descent),"SAT_reconstruction_pass":bool(sr["pass"])}


def failure_key(r): return (tuple(r["final_CLV"]),int(r["first_var"]),int(r["second_var"]))


def run():
    original,reached,root=reconstruct_r47n()
    depth1=[]
    for v in r33.variables(root):
        c=r47m.macro_candidate_full_closure(root,int(v))
        if c is None: continue
        rep=r47m.independent_replay(root,c)
        if not rep["pass"]: raise AssertionError(("R47P2_DEPTH1_REPLAY_FAIL",v))
        depth1.append({"var":int(v),"accepted":bool(c["accepted"]),"final_CLV":c["final_CLV"],"terminal":c["normalization"]["terminal"]})
    accepted1=[r["var"] for r in depth1 if r["accepted"]]
    if accepted1: raise AssertionError(("R47P2_R47N_NOT_JOINT_DEPTH1_DEAD",accepted1))
    tested=0; skipped=0; first_accept=None; best_fail=None
    for v1 in r33.variables(root):
        c1=r47m.macro_candidate_full_closure(root,int(v1))
        if c1 is None: continue
        g1=r33.canonical_formula(c1["normalization"]["final_formula"])
        for v2 in r33.variables(g1):
            if int(v2)==int(v1): continue
            p=pair(root,int(v1),int(v2))
            if p is None: skipped+=1; continue
            tested+=1
            if p["accepted"]: first_accept=p; break
            if best_fail is None or failure_key(p)<failure_key(best_fail): best_fail=p
        if first_accept is not None: break
    if first_accept is not None:
        verdict="R47N_RESCUED_BY_CERTIFIED_DEPTH2_JOINT_EXISTING_STACK_COMPOSITION"; stmt="joint d(F)=2 for this frozen witness/grammar"
    else:
        verdict="R47N_SURVIVES_ALL_CERTIFIED_DEPTH2_JOINT_EXISTING_STACK_COMPOSITIONS__JOINT_D_F_GT_2"; stmt="joint d(F)>2 for this frozen witness/grammar"
    return {"schema":"JANUS_TRUMP_R47P2_R47N_DEPTH2_JOINT_STACK_COMPOSITION_RESULT","version":"1.0","date":"2026-09-03","source_git_commit":os.environ.get("GITHUB_SHA","LOCAL_UNCOMMITTED"),"gate":"JANUS_TRUMP_R47P2_R47N_DEPTH2_JOINT_STACK_COMPOSITION","verdict":verdict,"R47N":{"mutated_original_hash":r47f.formula_hash(original),"fixpoint_hash":r47f.formula_hash(root),"fixpoint_CLV":list(clv(root)),"trajectory":reached["trajectory"],"joint_depth1_accepted_pivots":accepted1},"tested_ordered_pairs_until_stop":tested,"skipped_nonapplicable_pairs":skipped,"first_accepted_pair":first_accept,"best_failure_if_none":best_fail,"certified_depth_statement":stmt,"resource_envelope":{"fixed_depth":2,"ordered_pairs":"O(V0^2)","per_layer":"polynomial R47M joint closure","coarse_two_DP_growth":"O(C0^4)","polynomial":True},"interpretation":{"new_inference_rule_added":False,"new_proof_authority_added":False,"fixed_witness_result_does_not_prove_universal_K2":True,"unbounded_depth_not_authorized":True},"epistemic_firewall":{"UNIVERSAL_CONSTANT_K_EXISTS":"NOT_PROVED","K_EQUALS_2_FOR_JOINT_STACK_GRAMMAR":"NOT_PROVED","O4_UNIVERSAL_COVERAGE":"OPEN","SAT_IN_P":"NOT_PROVED","P_EQ_NP":"NOT_PROVED","P_NE_NP":"NOT_PROVED","P_VS_NP":"OPEN","TRUMP_finished":False}}


def main():
    p=argparse.ArgumentParser(); p.add_argument("--output"); a=p.parse_args(); d=run()
    if a.output:
        path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"gate":d["gate"],"verdict":d["verdict"],"tested_ordered_pairs_until_stop":d["tested_ordered_pairs_until_stop"],"first_accepted_pair":d["first_accepted_pair"],"best_failure_if_none":d["best_failure_if_none"],"certified_depth_statement":d["certified_depth_statement"],"firewall":d["epistemic_firewall"]},sort_keys=True))

if __name__=="__main__": main()
