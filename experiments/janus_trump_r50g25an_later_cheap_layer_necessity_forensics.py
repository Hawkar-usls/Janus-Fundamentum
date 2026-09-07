from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad
import janus_trump_r50g25ai_symbolic_signed_incidence_residual_class as ai
import janus_trump_r50g25aj_signed_incidence_reachability_closure as aj
import janus_trump_r50g25ak_symbolic_self_preserving_pivot as ak
import janus_trump_r50g25am_post_dp_r33_contraction_certificate as am
import janus_trump_r50g25x_adversarial_stall_search as x

GATE = "JANUS_TRUMP_R50G25AN_LATER_CHEAP_LAYER_NECESSITY_FORENSICS"
PREREG_COMMIT = "0c3c92896de54b77ff23ddd84a85706dd37af0de"
AM_RECEIPT_COMMIT = "324528f23524c647071e9b823e15fe7d7ea24e9b"
PARENT_HASH = "a28b56a47bf70487dfde4616b120d8ed68c4719546ff3d2756d12cf9b77d51cc"
PARENT_CLV = [157, 708, 21]
BUDGET = 1981168
PIVOT = 9
RAW_CHILD_HASH = "978512434c9464304b5294048778cbbacc789e854c207449dde57aa1a0ed3e21"
RAW_CHILD_CLV = [182, 962, 20]
RECOVERY_HASH = "2e5b98ca649fbe9c9a90bca7fb620c1787467ee6a6cb2d3cdc89e729d93bb72e"
RECOVERY_CLV = [177, 852, 20]
RECOVERY_SLACK = 23002


def class_record(formula):
    f = r33.canonical_formula(formula)
    C, L, V = map(int, r33.measure(f))
    if V <= 1:
        return {"CLV": [C, L, V], "hash": y.canonical_hash(f), "AI_class_pass": None, "AI_class_slack": None}
    rec = ai.signed_incidence_record(f, BUDGET)
    return {
        "CLV": [C, L, V],
        "hash": y.canonical_hash(f),
        "AI_class_pass": bool(rec["symbolic_class_pass"]),
        "AI_class_slack": int(rec["symbolic_class_slack"]),
    }


def r33_replay(state):
    a = r33.simplify(state)
    b = r33.simplify(state)
    fa = r33.canonical_formula(a["final_formula"])
    fb = r33.canonical_formula(b["final_formula"])
    replay = bool(fa == fb and a["terminal"] == b["terminal"] and a["history"] == b["history"])
    return a, fa, replay


def reconstruct_am_parent(chain):
    _b, r50g23, _r35b, _r33m, _r47jm = chain
    r34 = r50g23.r34
    initial, _meta = ad.graph_php(24, "SEEDED_BALANCED")
    initial = r33.canonical_formula(initial)
    c0, l0, v0 = map(int, r33.measure(initial))
    budget = (c0 + l0) * ((v0 + 1) ** 2)
    if budget != BUDGET:
        raise AssertionError(("AN_BUDGET_DRIFT", budget, BUDGET))
    state = initial
    replay_events = []
    for outer in range(26):
        w = y.policy_replay(state, chain)
        if w["kind"] != "RESIDUAL":
            raise AssertionError(("AN_PARENT_ROUTE_TERMINATED_EARLY", outer, w["kind"], aj.terminal_label(w)))
        core = r33.canonical_formula(w["state"])
        h = y.canonical_hash(core)
        if outer == 25:
            if h != PARENT_HASH or list(r33.measure(core)) != PARENT_CLV:
                raise AssertionError(("FROZEN_PARENT_WITNESS_DRIFT", h, list(r33.measure(core))))
            return core, replay_events

        parent_si = ai.signed_incidence_record(core, budget)
        if not parent_si["symbolic_class_pass"]:
            raise AssertionError(("AN_RECONSTRUCT_PARENT_OUTSIDE_CLASS", outer, h))
        admissible = []
        for var in r33.variables(core):
            b = aj.local_signed_incidence_bound(core, budget, int(var))
            if b is not None and b["envelope_admissible"]:
                admissible.append(b)
        admissible.sort(key=lambda q: (q["RAW_S_UB"], q["var"]))
        chosen = None
        tested = 0
        for b in admissible:
            tested += 1
            cert = am.post_dp_r33_certificate(core, budget, int(b["var"]), r34)
            if not cert.get("ok"):
                raise AssertionError(("AN_PARENT_RECONSTRUCTION_CERT_FAILURE", outer, cert))
            if cert["certificate_pass"]:
                chosen = cert
                break
        if chosen is None:
            raise AssertionError(("AN_PARENT_RECONSTRUCTION_EARLY_AM_GAP", outer, h))
        full = ak.actual_landing(core, budget, int(chosen["var"]), chain)
        if not full.get("ok") or not full.get("self_preserving"):
            raise AssertionError(("AN_PARENT_RECONSTRUCTION_FULL_POLICY_DRIFT", outer, chosen["var"], full))
        replay_events.append({
            "outer_round": outer,
            "residual_hash": h,
            "chosen_var": int(chosen["var"]),
            "candidates_tested": tested,
            "post_R33_CLV": chosen["post_R33_CLV"],
            "post_R33_AI_class_slack": chosen["post_R33_AI_class_slack"],
        })
        state = r33.canonical_formula(chosen["transformed_exact_child"])
    raise AssertionError("AN_PARENT_ROUTE_EXHAUSTED")


def counterfactual_sa_bve(raw_child, r42m):
    candidate, ledger = r42m.best_sa_bve_candidate(raw_child)
    if candidate is None:
        return {"candidate_exists": False, "scan_ledger": ledger}
    replay = r42m.independent_sa_bve_replay(raw_child, candidate)
    transformed = r33.canonical_formula(candidate["transformed"])
    return {
        "candidate_exists": True,
        "var": int(candidate["var"]),
        "independent_replay_pass": bool(replay["pass"]),
        "after": class_record(transformed),
        "scan_ledger": ledger,
    }


def forensic_route(raw_child, chain):
    _b, r50g23, r35b, r33m, r47jm = chain
    r34 = r50g23.r34
    r42m = r50g23.r42
    state = r33.canonical_formula(raw_child)
    route = []
    rup_count = 0
    sa_count = 0
    classification = None
    reentry_stage = None

    height_bound = r47jm.restart_height_bound(state)
    for round_index in range(height_bound + 1):
        before = class_record(state)
        simp, after_r33, r33_ok = r33_replay(state)
        if not r33_ok:
            raise AssertionError(("R33_RESTART_REPLAY_FAILURE", round_index))
        r33_rec = class_record(after_r33)
        row = {
            "round": round_index,
            "before": before,
            "after_R33": r33_rec,
            "R33_terminal": str(simp["terminal"]),
            "R33_rule_counts": dict(simp.get("rule_counts", {})),
            "R33_rule_applications": int(simp.get("total_rule_applications", 0)),
            "R33_certificate_bytes": int(simp.get("total_certificate_bytes", 0)),
            "R33_check_operation_upper_ledger": int(simp.get("total_check_operation_count_upper_ledger", 0)),
            "R33_replay_pass": True,
        }
        if r33_rec["AI_class_pass"] is True:
            if rup_count == 1 and sa_count == 0:
                classification = "RUP_UNLOCKS_R33_REENTRY"
            elif rup_count > 1 and sa_count == 0:
                classification = "MULTI_RUP_RESTART_CHAIN"
            elif sa_count > 0:
                classification = "SA_BVE_THEN_R33_REENTRY"
            else:
                classification = "R33_REENTRY_WITHOUT_LATER_DOOR"
            reentry_stage = {"round": round_index, "stage": "AFTER_R33", "state": r33_rec}
            route.append(row)
            break
        if simp["terminal"] != "STALLED_STACK_LEAN_CORE":
            classification = "TERMINAL_BEFORE_AI_REENTRY"
            reentry_stage = {"round": round_index, "stage": "R33_TERMINAL", "terminal": simp["terminal"], "state": r33_rec}
            route.append(row)
            break
        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine.get("recognized"):
            classification = "AFFINE_BEFORE_AI_REENTRY"
            reentry_stage = {"round": round_index, "stage": "AFFINE", "state": r33_rec}
            route.append(row)
            break

        proposal, rup_ledger = r35b.first_rup_strengthening(after_r33)
        row["RUP_scan_ledger"] = rup_ledger
        if proposal is not None:
            replay_ok = bool(r35b.independent_up_conflict_checker(after_r33, proposal["assumptions"]))
            if not replay_ok:
                raise AssertionError(("RUP_REPLAY_FAILURE", round_index, proposal))
            after_rup = r35b.replace_clause_with_subclause(
                after_r33, tuple(proposal["source_clause"]), tuple(proposal["strengthened_clause"])
            )
            after_rup = r33.canonical_formula(after_rup)
            rup_count += 1
            rup_rec = class_record(after_rup)
            row.update({
                "door": "RUP",
                "RUP_source_clause": list(proposal["source_clause"]),
                "RUP_strengthened_clause": list(proposal["strengthened_clause"]),
                "RUP_assumptions": list(proposal["assumptions"]),
                "RUP_independent_replay_pass": True,
                "after_RUP": rup_rec,
            })
            route.append(row)
            if rup_rec["AI_class_pass"] is True:
                classification = "RUP_DIRECT_REENTRY" if rup_count == 1 else "MULTI_RUP_DIRECT_REENTRY"
                reentry_stage = {"round": round_index, "stage": "AFTER_RUP", "state": rup_rec}
                break
            state = after_rup
            continue

        candidate, bve_ledger = r42m.best_sa_bve_candidate(after_r33)
        row["SA_BVE_scan_ledger"] = bve_ledger
        if candidate is not None:
            replay = r42m.independent_sa_bve_replay(after_r33, candidate)
            if not replay["pass"]:
                raise AssertionError(("SA_BVE_REPLAY_FAILURE", round_index, replay))
            after_sa = r33.canonical_formula(candidate["transformed"])
            sa_count += 1
            sa_rec = class_record(after_sa)
            row.update({
                "door": "SA_BVE",
                "SA_BVE_var": int(candidate["var"]),
                "SA_BVE_independent_replay_pass": True,
                "after_SA_BVE": sa_rec,
            })
            route.append(row)
            if sa_rec["AI_class_pass"] is True:
                classification = "SA_BVE_DIRECT_REENTRY"
                reentry_stage = {"round": round_index, "stage": "AFTER_SA_BVE", "state": sa_rec}
                break
            state = after_sa
            continue

        row["stop"] = "NO_RUP_NO_SA_BVE"
        route.append(row)
        classification = "RECOVERY_NOT_REPRODUCED"
        break
    else:
        classification = "RESOURCE_LIMIT"

    return {
        "classification": classification,
        "reentry_stage": reentry_stage,
        "RUP_count_before_reentry": rup_count,
        "SA_BVE_count_before_reentry": sa_count,
        "route": route,
    }


def run():
    chain = r50g25g._chain()
    _b, r50g23, _r35b, _r33m, _r47jm = chain
    r42m = r50g23.r42

    parent, parent_replay_events = reconstruct_am_parent(chain)
    if y.canonical_hash(parent) != PARENT_HASH or list(r33.measure(parent)) != PARENT_CLV:
        return {"gate": GATE, "verdict": "FROZEN_PARENT_WITNESS_DRIFT"}

    exact = y.exact_dp_record(parent, PIVOT)
    if exact is None or not exact.get("replay_pass"):
        return {"gate": GATE, "verdict": "EXACT_DP_REPLAY_FAILURE"}
    raw_child = r33.canonical_formula(exact["transformed"])
    raw_rec = class_record(raw_child)
    if raw_rec["hash"] != RAW_CHILD_HASH or raw_rec["CLV"] != RAW_CHILD_CLV:
        return {"gate": GATE, "verdict": "RAW_CHILD_HASH_OR_CLV_DRIFT", "observed": raw_rec}

    initial_simp, initial_after, initial_ok = r33_replay(raw_child)
    initial_rec = class_record(initial_after)
    inertness = bool(
        initial_ok
        and initial_simp["terminal"] == "STALLED_STACK_LEAN_CORE"
        and int(initial_simp.get("total_rule_applications", 0)) == 0
        and initial_rec["hash"] == RAW_CHILD_HASH
        and initial_rec["CLV"] == RAW_CHILD_CLV
    )
    if not inertness:
        return {
            "gate": GATE, "verdict": "AM_R33_INERTNESS_NOT_REPRODUCED",
            "initial_R33": {"result": initial_simp, "state": initial_rec, "replay_pass": initial_ok},
        }

    cf = counterfactual_sa_bve(raw_child, r42m)
    main = forensic_route(raw_child, chain)

    # Independent full frozen-policy consistency replay.
    full = x.replay_to_policy_fixpoint(raw_child, r50g23, chain[2], chain[3], chain[4])
    full_state = r33.canonical_formula(full["state"])
    full_rec = class_record(full_state)
    recovery_ok = bool(
        full["kind"] == "RESIDUAL"
        and full_rec["hash"] == RECOVERY_HASH
        and full_rec["CLV"] == RECOVERY_CLV
        and full_rec["AI_class_pass"] is True
        and full_rec["AI_class_slack"] == RECOVERY_SLACK
    )
    if not recovery_ok:
        verdict = "FULL_POLICY_RECOVERY_NOT_REPRODUCED"
    elif main["classification"] in {"RECOVERY_NOT_REPRODUCED", "RESOURCE_LIMIT"}:
        verdict = "FULL_POLICY_RECOVERY_NOT_REPRODUCED" if main["classification"] == "RECOVERY_NOT_REPRODUCED" else "RESOURCE_LIMIT"
    else:
        verdict = main["classification"]

    return {
        "gate": GATE,
        "AN_preregistration_commit": PREREG_COMMIT,
        "parent_AM_receipt_commit": AM_RECEIPT_COMMIT,
        "verdict": verdict,
        "frozen_parent": class_record(parent),
        "parent_reconstruction_event_count": len(parent_replay_events),
        "exact_DP": {
            "pivot": PIVOT,
            "CLV_after": list(exact["CLV_after"]),
            "replay_pass": bool(exact["replay_pass"]),
            "raw_child": raw_rec,
        },
        "initial_R33": {
            "terminal": str(initial_simp["terminal"]),
            "rule_counts": dict(initial_simp.get("rule_counts", {})),
            "rule_applications": int(initial_simp.get("total_rule_applications", 0)),
            "replay_pass": bool(initial_ok),
            "state": initial_rec,
        },
        "counterfactual_raw_child_SA_BVE": cf,
        "main_route": main,
        "full_policy_consistency": {
            "recovery_pass": recovery_ok,
            "kind": full["kind"],
            "final": full_rec,
            "route": full["route"],
        },
        "recommended_next_gate": (
            "R50G25AO_RUP_UNLOCK_CONTRACTION_CERTIFICATE_OR_COUNTEREXAMPLE"
            if verdict in {"RUP_DIRECT_REENTRY", "RUP_UNLOCKS_R33_REENTRY", "MULTI_RUP_RESTART_CHAIN", "MULTI_RUP_DIRECT_REENTRY"}
            else "R50G25AO_SA_BVE_OR_LATER_LAYER_CERTIFICATE_OR_COUNTEREXAMPLE"
        ),
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "single_witness_route_necessity_is_not_universal_necessity": True,
            "counterfactual_SA_BVE_is_diagnostic_only": True,
            "local_proof_carrying_recovery_is_not_global_runtime_bound": True,
            "state_envelope_is_not_runtime_bound": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    keys = ["gate", "verdict", "parent_reconstruction_event_count", "recommended_next_gate"]
    print(json.dumps({k: result.get(k) for k in keys}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
