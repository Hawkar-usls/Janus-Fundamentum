from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48g_targeted_unit_weight_pressure_counterexample_hunt as r48g
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o
import janus_trump_r49b_support_first_sa_bve_wide_survivor_controller as r49b

GATE = "JANUS_TRUMP_R49C_SUPPORT_FIRST_52ROOT_TRAJECTORY_REGRESSION"
MAX_ORDINAL = 64
EXPECTED_ROOTS = 52
EXPECTED_LEGACY_PROBES = 3463
EXPECTED_LEGACY_STEPS = 177
WIDTH_CAP = 4


def canon(f): return r33.canonical_formula(f)
def clv(f): return r33.measure(canon(f))
def fhash(f): return r47f.formula_hash(canon(f))
def maxw(f): return max((len(c) for c in canon(f)), default=0)

def polarity(terminal, semantic_sat):
    if terminal is None: return None
    if semantic_sat is True: return "SAT"
    if semantic_sat is False: return "UNSAT"
    return "UNKNOWN"


def support_candidate(before_formula, var):
    before=canon(before_formula)
    dp=r48o.r47m.r45a.exact_dp_record(before,int(var))
    if dp is None: return None
    dpr=r48o.r47m.r45a.independent_dp_replay(before,dp)
    env=r48o.r47m.r45a.polynomial_envelope(before,dp)
    if not dpr["pass"] or not env["pass"]:
        raise AssertionError(("R49C_DP_OR_ENVELOPE_FAIL",var,dpr,env))
    norm=r49b.support_first_normalize(dp["transformed"])
    final=canon(norm["final_formula"])
    sat_recon=r48o.r47m.reconstruct_sat(before,dp,norm)
    if norm["semantic_sat"] is True and not sat_recon["pass"]:
        raise AssertionError(("R49C_LOCAL_SAT_RECON_FAIL",var,sat_recon))
    return {
        "var":int(var),"DP":dp,"DP_independent_replay_pass":True,
        "polynomial_intermediate_envelope_pass":True,"normalization":norm,
        "SAT_reconstruction":sat_recon,"final_CLV":list(clv(final)),
        "accepted":bool(norm["terminal"] is not None or clv(final)<clv(before)),
    }


def support_replay(before_formula,claimed):
    x=support_candidate(before_formula,int(claimed["var"]))
    fields={
        "exists":x is not None,
        "final_hash_ok":x is not None and x["normalization"]["final_formula_hash"]==claimed["normalization"]["final_formula_hash"],
        "final_CLV_ok":x is not None and x["final_CLV"]==claimed["final_CLV"],
        "terminal_ok":x is not None and x["normalization"]["terminal"]==claimed["normalization"]["terminal"],
        "polarity_ok":x is not None and polarity(x["normalization"]["terminal"],x["normalization"]["semantic_sat"])==polarity(claimed["normalization"]["terminal"],claimed["normalization"]["semantic_sat"]),
        "BVE_sequence_ok":x is not None and x["normalization"]["SA_BVE_sequence"]==claimed["normalization"]["SA_BVE_sequence"],
        "segments_ok":x is not None and x["normalization"]["segments"]==claimed["normalization"]["segments"],
    }
    return {"pass":all(fields.values()),**fields}


def legacy_root(root, provenance):
    root=canon(root); current=root; V0=clv(root)[2]
    selected=[]; selected_full=[]; probes=0; max_persisted=maxw(root)
    for state_index in range(V0+1):
        if state_index>=V0: raise AssertionError(("R49C_LEGACY_STEP_CAP",fhash(root),clv(current)))
        rows,candidates=r48o.scan(current,False); probes+=len(rows)
        if probes>V0*V0: raise AssertionError(("R49C_LEGACY_PROBE_CAP",fhash(root),probes,V0*V0))
        safe=[r for r in rows if r.get("width4_safe",False)]
        if not safe: raise AssertionError(("R49C_LEGACY_FRONTIER_DRIFT_NO_SAFE",fhash(root),state_index))
        chosen_row=min(safe,key=lambda r:int(r["var"])); chosen=candidates[int(chosen_row["var"])]
        rep=r48o.r47m.independent_replay(current,chosen)
        if not rep["pass"]: raise AssertionError(("R49C_LEGACY_REPLAY_FAIL",fhash(root),chosen_row["var"],rep))
        row=r48o.candidate_row(current,chosen,True); final=canon(chosen["normalization"]["final_formula"])
        selected_full.append((current,chosen))
        selected.append({
            "step":len(selected)+1,"state_hash":fhash(current),"state_CLV":list(clv(current)),
            "var":int(row["var"]),"legacy_final_hash":fhash(final),"legacy_final_CLV":list(clv(final)),
            "legacy_final_width":maxw(final),"legacy_terminal":row["terminal"],"legacy_semantic_sat":row["semantic_sat"],
            "legacy_polarity":polarity(row["terminal"],row["semantic_sat"]),
            "legacy_SA_BVE_count":int(chosen["normalization"]["SA_BVE_application_count"]),
        })
        if row["terminal"] is not None:
            lift=r48g.lift_sat_root(root,selected_full,chosen)
            if not lift["pass"]: raise AssertionError(("R49C_LEGACY_ROOT_LIFT_FAIL",fhash(root)))
            return {
                "root_hash":fhash(root),"root_CLV":list(clv(root)),"provenance":provenance,
                "selected":selected,"selected_full":selected_full,"candidate_probe_count":probes,
                "max_persisted_width":max_persisted,
                "terminal":{"kind":row["terminal"],"semantic_sat":row["semantic_sat"],"polarity":polarity(row["terminal"],row["semantic_sat"]),"SAT_root_reconstruction_pass":True},
            }
        if maxw(final)>WIDTH_CAP: raise AssertionError(("R49C_LEGACY_WIDTH_DRIFT",fhash(root),row))
        max_persisted=max(max_persisted,maxw(final)); current=final
    raise AssertionError("R49C_LEGACY_UNREACHABLE")


def support_replay_trajectory(root, legacy):
    root=canon(root); current=root; selected_full=[]; rows=[]
    exact_matches=0; support_mode_steps=0; legacy_bve=0; support_bve=0
    legacy_polarity=legacy["terminal"]["polarity"]
    for step in legacy["selected"]:
        if fhash(current)!=step["state_hash"]:
            raise AssertionError(("R49C_INTERNAL_STATE_DRIFT",fhash(root),step["step"],fhash(current),step["state_hash"]))
        c=support_candidate(current,int(step["var"]))
        if c is None:
            return finish_replay(rows,"HARD_REGRESSION_CANDIDATE_MISSING",exact_matches,support_mode_steps,legacy_bve,support_bve)
        rep=support_replay(current,c)
        if not rep["pass"]:
            return finish_replay(rows,"HARD_REGRESSION_INDEPENDENT_REPLAY_FAIL",exact_matches,support_mode_steps,legacy_bve,support_bve)
        norm=c["normalization"]; final=canon(norm["final_formula"])
        before_vars=set(r33.variables(current)); after_vars=set(r33.variables(final))
        terminal=norm["terminal"]; pol=polarity(terminal,norm["semantic_sat"])
        eligible=bool(terminal is not None or (len(before_vars)-len(after_vars)>=1 and after_vars<=before_vars))
        width_safe=bool(terminal is not None or (eligible and maxw(final)<=WIDTH_CAP))
        modes=[seg.get("selection",{}).get("mode") for seg in norm["segments"]]
        used_support="SUPPORT_FIRST" in modes
        support_mode_steps += int(used_support)
        legacy_bve += int(step["legacy_SA_BVE_count"]); support_bve += int(norm["SA_BVE_application_count"])
        same_hash=fhash(final)==step["legacy_final_hash"]
        exact_matches += int(same_hash)
        row={
            "step":int(step["step"]),"state_hash":fhash(current),"var":int(step["var"]),
            "legacy_final_hash":step["legacy_final_hash"],"support_final_hash":fhash(final),"exact_hash_match":same_hash,
            "legacy_terminal":step["legacy_terminal"],"support_terminal":terminal,
            "legacy_polarity":step["legacy_polarity"],"support_polarity":pol,
            "support_final_CLV":list(clv(final)),"support_final_width":maxw(final),
            "eligible":eligible,"width4_safe":width_safe,"support_first_mode_used":used_support,
            "legacy_SA_BVE_count":int(step["legacy_SA_BVE_count"]),"support_SA_BVE_count":int(norm["SA_BVE_application_count"]),
            "support_SA_BVE_sequence":norm["SA_BVE_sequence"],"independent_replay_pass":True,
        }
        rows.append(row); selected_full.append((current,c))
        if terminal is not None:
            if pol!=legacy_polarity:
                return finish_replay(rows,"HARD_REGRESSION_TERMINAL_POLARITY_MISMATCH",exact_matches,support_mode_steps,legacy_bve,support_bve)
            if norm["semantic_sat"] is True:
                lift=r48g.lift_sat_root(root,selected_full,c)
                if not lift["pass"]:
                    return finish_replay(rows,"HARD_REGRESSION_SAT_ROOT_RECONSTRUCTION_FAIL",exact_matches,support_mode_steps,legacy_bve,support_bve)
            status="EXACT_TRAJECTORY" if same_hash and step["legacy_terminal"] is not None else "SAFE_TERMINAL_DIVERGENCE"
            return finish_replay(rows,status,exact_matches,support_mode_steps,legacy_bve,support_bve)
        if not width_safe:
            return finish_replay(rows,"HARD_REGRESSION_WIDTH4_SAFETY_LOST",exact_matches,support_mode_steps,legacy_bve,support_bve)
        if not same_hash:
            return finish_replay(rows,"SAFE_SYNTACTIC_DIVERGENCE",exact_matches,support_mode_steps,legacy_bve,support_bve)
        current=final
    return finish_replay(rows,"HARD_REGRESSION_LEGACY_PATH_EXHAUSTED_WITHOUT_TERMINAL",exact_matches,support_mode_steps,legacy_bve,support_bve)


def finish_replay(rows,status,exact_matches,support_mode_steps,legacy_bve,support_bve):
    return {
        "status":status,"rows":rows,"replayed_steps":len(rows),"exact_hash_matches":int(exact_matches),
        "support_first_mode_steps":int(support_mode_steps),"legacy_SA_BVE_count_on_replayed_steps":int(legacy_bve),
        "support_SA_BVE_count_on_replayed_steps":int(support_bve),
        "hard_regression":status.startswith("HARD_REGRESSION"),
        "safe_divergence":status in {"SAFE_SYNTACTIC_DIVERGENCE","SAFE_TERMINAL_DIVERGENCE"},
    }


def roots():
    center_original,_,center_fixpoint=r47x.load_center_original(); seen=set(); out=[]
    center=canon(center_fixpoint); seen.add(fhash(center)); out.append((center,{"kind":"CENTER_CONTROL","frontier_ordinal":0,"phase":"CENTER"}))
    for ordinal,(phase,source,replacement,mutated) in enumerate(r47x.frontier(center_original),1):
        if ordinal>MAX_ORDINAL: break
        if mutated is None: continue
        r47x.validate_exact_3cnf(mutated); reached=r47f.reachable_fixpoint(mutated)
        if reached is None: continue
        root=canon(reached["formula"]); h=fhash(root)
        if h in seen: continue
        seen.add(h); out.append((root,{"kind":"ONE_SWAP_REACHABLE_FIXPOINT","frontier_ordinal":int(ordinal),"phase":phase,"source_clause":list(source),"replacement_clause":list(replacement)}))
    if len(out)!=EXPECTED_ROOTS: raise AssertionError(("R49C_EXPECTED_52_ROOT_DRIFT",len(out)))
    return out


def run():
    records=[]; total_probes=0; total_steps=0; exact_roots=0; safe_div=0; hard=0; mismatches=0
    total_replays=0; exact_step_hashes=0; support_mode_steps=0; legacy_bve=0; support_bve=0
    first_hard=None; first_div=None
    for root,prov in roots():
        legacy=legacy_root(root,prov); total_probes+=legacy["candidate_probe_count"]; total_steps+=len(legacy["selected"])
        replay=support_replay_trajectory(root,legacy); total_replays+=replay["replayed_steps"]
        exact_step_hashes+=replay["exact_hash_matches"]; support_mode_steps+=replay["support_first_mode_steps"]
        legacy_bve+=replay["legacy_SA_BVE_count_on_replayed_steps"]; support_bve+=replay["support_SA_BVE_count_on_replayed_steps"]
        if replay["status"]=="EXACT_TRAJECTORY": exact_roots+=1
        if replay["safe_divergence"]:
            safe_div+=1
            if first_div is None: first_div={"root_hash":legacy["root_hash"],"provenance":prov,"replay":replay}
        if replay["hard_regression"]:
            hard+=1
            if "POLARITY_MISMATCH" in replay["status"]: mismatches+=1
            if first_hard is None: first_hard={"root_hash":legacy["root_hash"],"provenance":prov,"legacy":legacy,"replay":replay}
        records.append({"root_hash":legacy["root_hash"],"root_CLV":legacy["root_CLV"],"provenance":prov,"legacy_selected_pivots":[x["var"] for x in legacy["selected"]],"legacy_terminal":legacy["terminal"],"legacy_candidate_probe_count":legacy["candidate_probe_count"],"support_first_replay":replay})
        if first_hard is not None: break
    if total_probes!=EXPECTED_LEGACY_PROBES and first_hard is None: raise AssertionError(("R49C_LEGACY_PROBE_COUNT_DRIFT",total_probes))
    if total_steps!=EXPECTED_LEGACY_STEPS and first_hard is None: raise AssertionError(("R49C_LEGACY_STEP_COUNT_DRIFT",total_steps))
    if hard:
        verdict="SUPPORT_FIRST_52ROOT_HARD_REGRESSION_FOUND"
    elif safe_div:
        verdict="SUPPORT_FIRST_52ROOT_REGRESSION_HAS_ONLY_CERTIFIED_SAFE_DIVERGENCES__FINITE_ONLY"
    else:
        verdict="SUPPORT_FIRST_PRESERVES_ALL_52_LEGACY_WIDTH4_TRAJECTORIES_EXACTLY__FINITE_ONLY"
    return {
        "gate":GATE,"verdict":verdict,
        "metrics":{
            "roots_evaluated":len(records),"legacy_candidate_probes":int(total_probes),"legacy_selected_steps":int(total_steps),
            "support_first_selected_pivot_replays":int(total_replays),"exact_step_final_hash_matches":int(exact_step_hashes),
            "exact_trajectory_roots":int(exact_roots),"safe_divergence_roots":int(safe_div),"hard_regression_roots":int(hard),
            "terminal_polarity_mismatches":int(mismatches),"support_first_mode_steps":int(support_mode_steps),
            "legacy_SA_BVE_count_on_replayed_steps":int(legacy_bve),"support_SA_BVE_count_on_replayed_steps":int(support_bve),
        },
        "first_safe_divergence":first_div,"first_hard_regression":first_hard,"roots":records,
        "interpretation":{"finite_52root_frontier_only":True,"new_inference_rule_added":False,"universal_support_first_safety_proved":False,"universal_width4_coverage_proved":False},
        "firewall":{"UNIVERSAL_SUPPORT_FIRST_SA_BVE_SAFETY":"NOT_PROVED","UNIVERSAL_SURVIVOR_SUPPORT_SA_BVE_LAW":"NOT_PROVED","UNIVERSAL_WIDTH_RESET_LEMMA":"NOT_PROVED","UNIVERSAL_WIDTH_4_COVERAGE":"NOT_PROVED","UNIVERSAL_CONSTANT_WIDTH_COVERAGE":"NOT_PROVED","O4_UNIVERSAL_COVERAGE":"OPEN","SAT_IN_P":"NOT_PROVED","P_EQ_NP":"NOT_PROVED","P_NE_NP":"NOT_PROVED","P_VS_NP":"OPEN","TRUMP_finished":False},
    }


def main():
    p=argparse.ArgumentParser();p.add_argument("--output");a=p.parse_args();d=run()
    if a.output:
        path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"gate":d["gate"],"verdict":d["verdict"],"metrics":d["metrics"],"first_safe_divergence":d["first_safe_divergence"],"first_hard_regression":None if d["first_hard_regression"] is None else {"root_hash":d["first_hard_regression"]["root_hash"],"provenance":d["first_hard_regression"]["provenance"],"status":d["first_hard_regression"]["replay"]["status"]},"firewall":d["firewall"]},sort_keys=True))
if __name__=="__main__":main()
