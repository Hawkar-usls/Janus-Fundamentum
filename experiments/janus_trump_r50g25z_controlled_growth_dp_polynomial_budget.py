from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25x_adversarial_stall_search as r50g25x
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as r50g25y

GATE = "JANUS_TRUMP_R50G25Z_CONTROLLED_GROWTH_DP_DOOR_OR_LOWER_BOUND_OBSTRUCTION"
Z_PREREG_COMMIT = "b8196dc3bd32415b962ea586d009d99fd05fd81b"
Y_RECEIPT_COMMIT = "3398edec2c648cc59f366b179a61a895829eacb2"
EXPECTED_X_RESIDUALS = 15


def size_sum(formula):
    c,l,_v = r33.measure(formula)
    return c+l


def controlled_run(initial, chain):
    initial = r33.canonical_formula(initial)
    c0,l0,v0 = r33.measure(initial)
    budget = (c0+l0) * (v0+1) * (v0+1)
    state = initial
    fallback = []
    total_pair_checks = 0
    total_subsumption_pair_upper = 0

    for outer in range(v0+1):
        w = r50g25y.policy_replay(state, chain)
        if w["kind"] in {"TERMINAL","AFFINE"}:
            return {
                "status":"TERMINAL",
                "terminal_kind":w["kind"],
                "terminal_label":w["route"][-1].get("R33_terminal") if w["kind"]=="TERMINAL" and w["route"] else None,
                "fallback_DP_count":len(fallback),
                "fallback_trace":fallback,
                "budget":budget,
                "max_controlled_state_size":max([c0+l0]+[x["after_size"] for x in fallback]),
                "total_pair_checks":total_pair_checks,
                "total_subsumption_pair_upper":total_subsumption_pair_upper,
            }
        if w["kind"] != "RESIDUAL":
            return {"status":"OBSTRUCTION","class":"UNEXPECTED_W_KIND","kind":w["kind"],"fallback_DP_count":len(fallback),"budget":budget}

        core = r33.canonical_formula(w["state"])
        before = r33.measure(core)
        if size_sum(core) > budget:
            return {"status":"OBSTRUCTION","class":"STATE_BUDGET_VIOLATION","residual_CLV":list(before),"budget":budget,"fallback_DP_count":len(fallback)}
        if len(fallback) >= v0:
            return {"status":"OBSTRUCTION","class":"CONTROLLED_SCHEDULER_RESIDUAL_AFTER_AT_MOST_V0_FALLBACK_DP_STEPS","residual_CLV":list(before),"budget":budget,"fallback_DP_count":len(fallback)}

        all_records = []
        for var in r33.variables(core):
            rec = r50g25y.exact_dp_record(core, var)
            if rec is not None:
                all_records.append(rec)
        if not all_records:
            return {"status":"OBSTRUCTION","class":"NO_EXACT_DP_PIVOT_AT_RESIDUAL","residual_CLV":list(before),"budget":budget,"fallback_DP_count":len(fallback)}
        if any(not r["replay_pass"] for r in all_records):
            return {"status":"OBSTRUCTION","class":"EXACT_DP_REPLAY_FAILURE","residual_CLV":list(before),"budget":budget,"fallback_DP_count":len(fallback)}

        admissible = []
        for rec in all_records:
            transformed = r33.canonical_formula(rec["transformed"])
            after = r33.measure(transformed)
            if after[2] >= before[2]:
                continue
            if size_sum(transformed) <= budget:
                admissible.append(rec)
        if not admissible:
            return {
                "status":"OBSTRUCTION","class":"ALL_EXACT_DP_PIVOTS_EXCEED_POLYNOMIAL_STATE_BUDGET",
                "residual_CLV":list(before),"budget":budget,"fallback_DP_count":len(fallback),
                "all_DP_after_CLV":[r["CLV_after"] for r in all_records],
            }

        chosen = min(admissible, key=lambda r:(r["CLV_after"][0],r["CLV_after"][1],r["var"]))
        transformed = r33.canonical_formula(chosen["transformed"])
        after = r33.measure(transformed)
        if after[2] >= before[2]:
            return {"status":"OBSTRUCTION","class":"VARIABLE_COUNT_NOT_STRICTLY_DECREASING","var":chosen["var"],"before":list(before),"after":list(after)}
        total_pair_checks += int(chosen["pair_checks"])
        pool_c = int(chosen["pool_clause_count_before_subsumption"])
        total_subsumption_pair_upper += pool_c*pool_c
        fallback.append({
            "outer_round":outer,"var":chosen["var"],"before_CLV":list(before),"after_CLV":list(after),
            "relation_under_old_CLV":chosen["relation"],"before_size":before[0]+before[1],"after_size":after[0]+after[1],
            "budget":budget,"pair_checks":chosen["pair_checks"],"pool_clause_count":pool_c,"replay_pass":chosen["replay_pass"],
        })
        state = transformed

    return {"status":"OBSTRUCTION","class":"CONTROLLED_SCHEDULER_RESIDUAL_AFTER_AT_MOST_V0_FALLBACK_DP_STEPS","budget":budget,"fallback_DP_count":len(fallback)}


def run():
    chain = r50g25g._chain()

    # Reproduce X exactly; truth is not used by X generation or selection.
    x = r50g25x.run()
    if x["residual_fixpoint_count"] != EXPECTED_X_RESIDUALS:
        raise AssertionError(("Z_X_RESIDUAL_COUNT_DRIFT",x["residual_fixpoint_count"]))

    cases = []
    for i,res in enumerate(x["residuals"]):
        f = r33.canonical_formula(res["residual_formula"])
        cases.append({"name":f"X_RESIDUAL_{i:02d}","family":res["family"],"hash":res["residual_hash"],"formula":f})

    # Independently reconstruct Y's truth-blind minimized residual core.
    _sealed, target = r47j.load_counterexample()
    minimized, min_ledger = r50g25y.truth_blind_minimize(target, chain)
    yrep = r50g25y.policy_replay(minimized, chain)
    if yrep["kind"] != "RESIDUAL":
        raise AssertionError(("Z_Y_RESIDUAL_REPRO_FAIL",yrep["kind"]))
    ycore = r33.canonical_formula(yrep["state"])
    if r50g25y.canonical_hash(ycore) != "98d929c32c0f838a920888ca10c4a2f2eb9afe5ad58ac471d8854851e5bb7532":
        raise AssertionError(("Z_Y_CORE_HASH_DRIFT",r50g25y.canonical_hash(ycore)))
    cases.append({"name":"Y_MINIMIZED_RESIDUAL_CORE","family":"Y_MINIMIZED_R47","hash":r50g25y.canonical_hash(ycore),"formula":ycore})

    rows = []
    obstruction_hist = Counter()
    terminal_hist = Counter()
    max_fallback = None
    max_budget_ratio = None
    for case in cases:
        out = controlled_run(case["formula"], chain)
        row = {"name":case["name"],"family":case["family"],"hash":case["hash"],"initial_CLV":list(r33.measure(case["formula"])),**out}
        rows.append(row)
        if out["status"] == "OBSTRUCTION":
            obstruction_hist[out["class"]] += 1
        else:
            terminal_hist[str(out.get("terminal_label") or out.get("terminal_kind"))] += 1
            key=(out["fallback_DP_count"], case["hash"])
            if max_fallback is None or key > (max_fallback["fallback_DP_count"],max_fallback["hash"]):
                max_fallback=row
            ratio = out["max_controlled_state_size"] / out["budget"] if out["budget"] else 0.0
            if max_budget_ratio is None or ratio > max_budget_ratio[0]:
                max_budget_ratio=(ratio,row)

    obstruction_count=sum(obstruction_hist.values())
    verdict = "CONTROLLED_GROWTH_DP_OBSTRUCTION_FOUND" if obstruction_count else "CONTROLLED_GROWTH_POLICY_TERMINATES_ON_PREREGISTERED_DOMAIN_WITHIN_POLYNOMIAL_STATE_BUDGET"
    next_gate = "R50G25AA_MINIMAL_CONTROLLED_GROWTH_OBSTRUCTION_FORENSICS" if obstruction_count else "R50G25AA_UNIVERSAL_CONTROLLED_DP_DOOR_EXISTENCE_OR_SYMBOLIC_COUNTEREXAMPLE"
    return {
        "gate":GATE,"Z_preregistration_commit":Z_PREREG_COMMIT,"parent_Y_receipt_commit":Y_RECEIPT_COMMIT,
        "domain":{"X_residual_occurrences":EXPECTED_X_RESIDUALS,"Y_minimized_core":1,"total":len(cases),"truth_used_for_door_selection":False,"exact_truth_authority":False},
        "budget_contract":{"B":"(C0+L0)*(V0+1)^2","fallback_DP_strictly_reduces_variable_count":True,"transformed_state_must_remain_within_B":True},
        "verdict":verdict,"obstruction_count":obstruction_count,"obstruction_histogram":dict(sorted(obstruction_hist.items())),
        "terminal_histogram":dict(sorted(terminal_hist.items())),"rows":rows,
        "max_fallback_case":max_fallback,
        "max_budget_ratio_case":None if max_budget_ratio is None else {"ratio":max_budget_ratio[0],"row":max_budget_ratio[1]},
        "Y_reproduction":{"minimized_CLV":list(r33.measure(minimized)),"core_CLV":list(r33.measure(ycore)),"minimization_accepted":min_ledger["accepted_count"]},
        "conditional_complexity_contract":{"DP_fallback_count_per_case_at_most_V0":True,"each_DP_scan_is_polynomial_in_current_bounded_state":True,"global_state_budget_is_polynomial_in_initial_C_L_V":True,"universal_admissible_door_existence_not_proved":True},
        "next_gate":next_gate,
        "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False,"finite_domain_pass_is_not_universal_coverage":True},
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); args=ap.parse_args()
    result=run(); p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ['gate','verdict','obstruction_count','obstruction_histogram','terminal_histogram','next_gate']},indent=2,sort_keys=True))
    print('MAX_FALLBACK',json.dumps(result['max_fallback_case'],sort_keys=True))
    print('MAX_BUDGET_RATIO',json.dumps(result['max_budget_ratio_case'],sort_keys=True))

if __name__=='__main__':
    main()
