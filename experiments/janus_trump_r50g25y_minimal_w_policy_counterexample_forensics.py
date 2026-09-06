from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25x_adversarial_stall_search as r50g25x

GATE = "JANUS_TRUMP_R50G25Y_MINIMAL_W_POLICY_COUNTEREXAMPLE_FORENSICS"
Y_PREREG_COMMIT = "92b93a34cd582800fc925e961196607ff8d27ee0"
X_RECEIPT_COMMIT = "30cbe3f2fd3b07fbffb1210bcd5d00c232a2945c"
TARGET_HASH = "c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb"


def canonical_hash(formula):
    return r42.formula_hash(r33.canonical_formula(formula))


def policy_replay(formula, chain):
    _b, r50g23, r35b, r33m, r47jm = chain
    return r50g25x.replay_to_policy_fixpoint(formula, r50g23, r35b, r33m, r47jm)


def is_residual(formula, chain):
    return policy_replay(formula, chain)["kind"] == "RESIDUAL"


def truth_blind_minimize(formula, chain):
    state = r33.canonical_formula(formula)
    attempts = 0
    accepted = []
    passes = 0
    changed = True
    while changed:
        passes += 1
        changed = False

        # Deterministic clause deletion, canonical order. Restart after each accepted edit.
        i = 0
        while i < len(state):
            attempts += 1
            candidate = r33.canonical_formula(state[:i] + state[i+1:])
            if is_residual(candidate, chain):
                accepted.append({"kind":"DELETE_CLAUSE","clause":list(state[i]),"CLV_before":list(r33.measure(state)),"CLV_after":list(r33.measure(candidate))})
                state = candidate
                changed = True
                i = 0
                continue
            i += 1

        # Deterministic literal deletion. Unit clauses are not shortened to empty clauses.
        ci = 0
        while ci < len(state):
            clause = state[ci]
            if len(clause) <= 1:
                ci += 1
                continue
            li = 0
            accepted_here = False
            while li < len(clause):
                attempts += 1
                shortened = tuple(l for j,l in enumerate(clause) if j != li)
                candidate_clauses = list(state)
                candidate_clauses[ci] = shortened
                candidate = r33.canonical_formula(candidate_clauses)
                if is_residual(candidate, chain):
                    accepted.append({"kind":"DELETE_LITERAL","clause_before":list(clause),"deleted_literal":int(clause[li]),"CLV_before":list(r33.measure(state)),"CLV_after":list(r33.measure(candidate))})
                    state = candidate
                    changed = True
                    accepted_here = True
                    ci = 0
                    break
                li += 1
            if accepted_here:
                continue
            ci += 1
    return state, {"passes":passes,"attempts":attempts,"accepted_count":len(accepted),"accepted":accepted}


def exact_dp_record(formula, var):
    before = r33.canonical_formula(formula)
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(before, int(var))
    if not pos or not neg:
        return None
    base = tuple(c for c in before if var not in c and -var not in c)
    pool = r33.canonical_formula(list(base) + list(resolvents))
    transformed = r42.subsumption_minimize(pool)
    before_m = r33.measure(before)
    after_m = r33.measure(transformed)
    relation = "STRICT_DESCENT" if after_m < before_m else ("EQUAL_MEASURE" if after_m == before_m else "GROWTH")

    # Independent syntactic replay without requiring progress.
    pos2, neg2, resolvents2, _ = r42.all_dp_resolvents(before, int(var))
    base2 = tuple(c for c in before if var not in c and -var not in c)
    expected = r42.subsumption_minimize(list(base2) + list(resolvents2))
    replay_pass = (pos == pos2 and neg == neg2 and resolvents == resolvents2 and transformed == expected and var not in r33.variables(transformed))

    return {
        "var":int(var),
        "positive_parent_count":len(pos),
        "negative_parent_count":len(neg),
        "non_tautological_resolvent_count":len(resolvents),
        "pair_checks":pair_checks,
        "pool_clause_count_before_subsumption":len(pool),
        "pool_literal_count_before_subsumption":sum(len(c) for c in pool),
        "CLV_before":list(before_m),
        "CLV_after":list(after_m),
        "relation":relation,
        "replay_pass":bool(replay_pass),
        "transformed":transformed,
    }


def downstream_summary(transformed, chain):
    out = policy_replay(transformed, chain)
    route = out["route"]
    return {
        "kind":out["kind"],
        "final_CLV":list(r33.measure(out["state"])),
        "route_length":len(route),
        "route_tail":route[-6:],
        "terminal_label":route[-1].get("R33_terminal") if out["kind"] == "TERMINAL" and route else None,
    }


def run():
    chain = r50g25g._chain()
    _sealed, target = r47j.load_counterexample()
    target = r33.canonical_formula(target)
    if canonical_hash(target) != TARGET_HASH:
        raise AssertionError(("Y_TARGET_HASH_DRIFT", canonical_hash(target)))
    initial_replay = policy_replay(target, chain)
    if initial_replay["kind"] != "RESIDUAL":
        raise AssertionError(("Y_TARGET_NOT_RESIDUAL", initial_replay["kind"]))

    minimized, min_ledger = truth_blind_minimize(target, chain)
    minimized_replay = policy_replay(minimized, chain)
    if minimized_replay["kind"] != "RESIDUAL":
        raise AssertionError(("Y_MINIMIZER_LOST_RESIDUAL", minimized_replay["kind"]))
    core = r33.canonical_formula(minimized_replay["state"])

    pivots = []
    for var in r33.variables(core):
        rec = exact_dp_record(core, var)
        if rec is None:
            continue
        down = downstream_summary(rec["transformed"], chain)
        rec["downstream_W_policy"] = down
        rec.pop("transformed")
        pivots.append(rec)

    if any(not p["replay_pass"] for p in pivots):
        raise AssertionError("Y_EXACT_DP_REPLAY_FAILURE")

    hist = Counter(p["relation"] for p in pivots)
    strict = [p for p in pivots if p["relation"] == "STRICT_DESCENT"]
    nonresidual = [p for p in pivots if p["downstream_W_policy"]["kind"] != "RESIDUAL"]
    if not pivots:
        verdict = "MINIMAL_STALL_HAS_NO_EXACT_DP_PIVOT"
        next_gate = "R50G25Z_NON_DP_COLLAPSE_DOOR_SEARCH"
    elif strict:
        verdict = "MINIMAL_STALL_HAS_DESCENDING_DP_DOOR_W_POLICY_MISSED"
        next_gate = "R50G25Z_W_POLICY_IMPLEMENTATION_GAP_REPAIR"
    else:
        verdict = "MINIMAL_STALL_HAS_ONLY_NONDESCENDING_DP_DOORS"
        next_gate = "R50G25Z_CONTROLLED_GROWTH_DP_DOOR_OR_LOWER_BOUND_OBSTRUCTION"

    best_door = None
    if nonresidual:
        best_door = min(nonresidual, key=lambda p:(tuple(p["CLV_after"]), p["var"]))

    return {
        "gate":GATE,
        "Y_preregistration_commit":Y_PREREG_COMMIT,
        "parent_X_receipt_commit":X_RECEIPT_COMMIT,
        "target":{"hash":TARGET_HASH,"CLV":list(r33.measure(target)),"initial_policy_kind":initial_replay["kind"]},
        "minimization_contract":{"truth_blind":True,"SAT_truth_used_for_selection":False,"deterministic":True},
        "minimization":{"source_hash":TARGET_HASH,"source_CLV":list(r33.measure(target)),"minimized_hash":canonical_hash(minimized),"minimized_CLV":list(r33.measure(minimized)),"residual_core_hash":canonical_hash(core),"residual_core_CLV":list(r33.measure(core)),**min_ledger},
        "exact_DP_pivot_count":len(pivots),
        "exact_DP_relation_histogram":dict(sorted(hist.items())),
        "pivots":pivots,
        "downstream_nonresidual_pivot_count":len(nonresidual),
        "minimum_nonresidual_DP_door":best_door,
        "verdict":verdict,
        "next_gate":next_gate,
        "interpretation":{"counterexample_is_to_current_W_policy_only":True,"non_descending_DP_is_not_automatically_algorithmically_safe":True,"bounded_forensics_is_not_universal_theorem":True},
        "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k:result[k] for k in ["gate","verdict","next_gate","exact_DP_pivot_count","exact_DP_relation_histogram","downstream_nonresidual_pivot_count"]}, indent=2, sort_keys=True))
    print("MINIMIZATION", json.dumps(result["minimization"], sort_keys=True))
    print("BEST_DOOR", json.dumps(result["minimum_nonresidual_DP_door"], sort_keys=True))


if __name__ == "__main__":
    main()
