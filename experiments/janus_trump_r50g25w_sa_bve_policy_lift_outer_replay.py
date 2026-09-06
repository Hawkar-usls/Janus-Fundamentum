from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25t_resource_growth_ladder as r50g25t
import janus_trump_r50g25u_certificate_size_theorem_scale_ladder as r50g25u
import janus_trump_r50g25v_two_residual_forensics as r50g25v

GATE = "JANUS_TRUMP_R50G25W_R42_SA_BVE_POLICY_LIFT_OR_COUNTEREXAMPLE"
V_RUN = 34044114670
V_RECEIPT_COMMIT = "0bd1a4b1d3aba9b4f5dd6f55dd831438dfa8e31b"
W_PREREG_COMMIT = "b10247ac6b86480de67ffac8194dfab416988d91"
EXPECTED_V_RESIDUALS = 2


def sa_bve_call_envelope(measure):
    c, _l, v = (int(x) for x in measure)
    # For each variable, a first pos*neg scan and at most one repeated scan inside
    # sa_bve_candidate_for_var. pos*neg <= C^2/4, so V*C^2 is a simple safe bound.
    pair_checks_bound = v * c * c
    pool_clause_bound = c + (c * c) // 4 + 1
    subsumption_checks_bound = v * pool_clause_bound * pool_clause_bound
    return {
        "C": c,
        "V": v,
        "resolution_pair_checks_conservative_bound": pair_checks_bound,
        "pool_clause_bound": pool_clause_bound,
        "subsumption_pair_checks_conservative_bound": subsumption_checks_bound,
    }


def micro_with_sa_bve(initial, r50g23, r35b, r33, r47j):
    r34 = r50g23.r34
    r42 = r50g23.r42
    original = r33.canonical_formula(initial)
    state = original
    height_bound = r47j.restart_height_bound(original)
    reconstruction_events = []
    rounds = []
    terminal = None
    semantic_sat = None
    terminal_assignment = None
    terminal_verification = None
    ledger = {
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "RUP_successful_strengthenings": 0,
        "SA_BVE_calls": 0,
        "SA_BVE_applications": 0,
        "SA_BVE_reported_variables_checked": 0,
        "SA_BVE_reported_resolution_pair_checks": 0,
        "SA_BVE_reported_subsumption_pair_upper_ledger": 0,
        "SA_BVE_resolution_pair_checks_symbolic_bound": 0,
        "SA_BVE_subsumption_pair_checks_symbolic_bound": 0,
        "GF2_estimated_bit_ops": 0,
        "restart_count": 0,
    }
    sa_bve_events = []

    for round_index in range(height_bound + 1):
        before = state
        before_clv = tuple(r33.measure(before))
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        after_r33_clv = tuple(r33.measure(after_r33))
        if after_r33 != before and not after_r33_clv < before_clv:
            raise AssertionError(("W_R33_NO_STRICT_DESCENT", round_index, before_clv, after_r33_clv))
        if reduced["history"]:
            reconstruction_events.append({"kind": "R33", "result": reduced})
        ledger["R33_check_operation_upper_ledger"] += int(reduced["total_check_operation_count_upper_ledger"])
        ledger["R33_certificate_bytes"] += int(reduced["total_certificate_bytes"])
        row = {
            "round": round_index,
            "before_CLV": list(before_clv),
            "after_R33_CLV": list(after_r33_clv),
            "R33_terminal": str(reduced["terminal"]),
        }

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = r42.solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("W_DECLARED_TERMINAL_VERIFY_FAIL", round_index, solved))
            terminal = str(solved["kind"])
            semantic_sat = bool(solved["sat"])
            terminal_assignment = solved.get("assignment")
            terminal_verification = solved
            state = after_r33
            row["stop"] = terminal
            rounds.append(row)
            break

        affine = r34.recognize_complete_affine_cnf(after_r33)
        row["affine_recognized"] = bool(affine["recognized"])
        if affine["recognized"]:
            solution = r34.solve_gf2_with_certificate(affine["equations"])
            verify = r34.verify_affine_certificate(after_r33, affine, solution)
            if not verify["pass"]:
                raise AssertionError(("W_AFFINE_VERIFY_FAIL", round_index, verify))
            terminal = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            semantic_sat = bool(solution["sat"])
            terminal_assignment = solution.get("assignment")
            terminal_verification = verify
            ledger["GF2_estimated_bit_ops"] += int(solution["estimated_bit_ops"])
            state = after_r33
            row["stop"] = terminal
            rounds.append(row)
            break

        proposal, proposal_ledger = r35b.first_rup_strengthening(after_r33)
        ledger["RUP_checks"] += int(proposal_ledger["rup_checks"])
        ledger["RUP_UP_clause_scans"] += int(proposal_ledger["up_clause_scans"])
        ledger["RUP_UP_literal_inspections"] += int(proposal_ledger["up_literal_inspections"])
        if proposal is not None:
            if not r35b.independent_up_conflict_checker(after_r33, proposal["assumptions"]):
                raise AssertionError(("W_RUP_CERT_FAIL", round_index, proposal))
            after_rup = r35b.replace_clause_with_subclause(
                after_r33, tuple(proposal["source_clause"]), tuple(proposal["strengthened_clause"])
            )
            after_rup_clv = tuple(r33.measure(after_rup))
            if not after_rup_clv < after_r33_clv or not after_rup_clv < before_clv:
                raise AssertionError(("W_RUP_NO_STRICT_DESCENT", round_index, before_clv, after_r33_clv, after_rup_clv))
            ledger["RUP_successful_strengthenings"] += 1
            ledger["restart_count"] += 1
            row.update({
                "RUP": True,
                "RUP_source_clause": list(proposal["source_clause"]),
                "RUP_strengthened_clause": list(proposal["strengthened_clause"]),
                "after_RUP_CLV": list(after_rup_clv),
                "restart": True,
            })
            rounds.append(row)
            state = after_rup
            continue

        # New placement only here: old micro would stop residual at this point.
        ledger["SA_BVE_calls"] += 1
        env = sa_bve_call_envelope(after_r33_clv)
        ledger["SA_BVE_resolution_pair_checks_symbolic_bound"] += int(env["resolution_pair_checks_conservative_bound"])
        ledger["SA_BVE_subsumption_pair_checks_symbolic_bound"] += int(env["subsumption_pair_checks_conservative_bound"])
        candidate, bve_ledger = r42.best_sa_bve_candidate(after_r33)
        ledger["SA_BVE_reported_variables_checked"] += int(bve_ledger["variables_checked"])
        ledger["SA_BVE_reported_resolution_pair_checks"] += int(bve_ledger["resolution_pair_checks"])
        ledger["SA_BVE_reported_subsumption_pair_upper_ledger"] += int(bve_ledger["subsumption_pair_upper_ledger"])
        row["SA_BVE_scan_envelope"] = env
        row["SA_BVE_reported_ledger"] = bve_ledger

        if candidate is None:
            terminal = None
            semantic_sat = None
            state = after_r33
            row["stop"] = "CERTIFIED_RUP_PLUS_SA_BVE_FIXPOINT"
            rounds.append(row)
            break

        replay = r42.independent_sa_bve_replay(after_r33, candidate)
        if not replay["pass"]:
            raise AssertionError(("W_SA_BVE_REPLAY_FAIL", round_index, replay, candidate))
        after_bve = r33.canonical_formula(candidate["transformed"])
        after_bve_clv = tuple(r33.measure(after_bve))
        if not after_bve_clv < after_r33_clv or not after_bve_clv < before_clv:
            raise AssertionError(("W_SA_BVE_NO_STRICT_DESCENT", round_index, before_clv, after_r33_clv, after_bve_clv))
        reconstruction_events.append({"kind": "SA_BVE", "record": candidate})
        ledger["SA_BVE_applications"] += 1
        ledger["restart_count"] += 1
        sa_bve_events.append({
            "round": round_index,
            "var": int(candidate["var"]),
            "measure_before": list(after_r33_clv),
            "measure_after": list(after_bve_clv),
            "full_non_tautological_resolvent_count": len(candidate["full_non_tautological_resolvents"]),
            "replay_pass": True,
        })
        row.update({"RUP": False, "SA_BVE": sa_bve_events[-1], "restart": True})
        rounds.append(row)
        state = after_bve
    else:
        raise AssertionError(("W_HEIGHT_BOUND_EXHAUSTED", height_bound))

    reconstruction = {"applicable": False, "pass": True, "assignment": None}
    if semantic_sat is True:
        assignment = dict(terminal_assignment or {})
        reconstructed = r42.reconstruct_full_model(reconstruction_events, assignment, original)
        reconstruction = {
            "applicable": True,
            "pass": bool(reconstructed["pass"]),
            "assignment": {str(k): bool(v) for k, v in sorted(reconstructed["assignment"].items())},
        }
        if not reconstruction["pass"]:
            raise AssertionError("W_FINAL_MODEL_RECONSTRUCTION_FAIL")

    return {
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_verification": terminal_verification,
        "final_CLV": list(r33.measure(state)),
        "round_count": len(rounds),
        "restart_count": int(ledger["restart_count"]),
        "rounds": rounds,
        "ledger": ledger,
        "SA_BVE_events": sa_bve_events,
        "SAT_reconstruction": reconstruction,
    }


def combined_domain(r33):
    t_items, t_generation = r50g25t.generate_ladder(r33)
    u_items, u_generation = r50g25u.generate_scale_ladder(r33)
    merged = {}
    for origin, items in (("T", t_items), ("U", u_items)):
        for item in items:
            f = r33.canonical_formula(item["formula"])
            key = tuple(f)
            if key not in merged:
                merged[key] = {"formula": f, "origins": []}
            merged[key]["origins"].append({
                "gate": origin,
                "family": item["family"],
                "size": int(item["size"]),
                "meta": item["meta"],
            })
    return list(merged.values()), {"T": t_generation, "U": u_generation, "deduplicated_count": len(merged)}


def reproduce_v_residual_sources(r50g23, r35b, r33, r47j):
    items, _ = r50g25u.generate_scale_ladder(r33)
    sources = []
    for item in items:
        f = r33.canonical_formula(item["formula"])
        old = r50g25g.micro_normalize(f, r50g23, r35b, r33, r47j)
        if old.get("semantic_sat") is None:
            sources.append({"item": item, "formula": f, "old": old})
    if len(sources) != 2:
        raise AssertionError(("W_V_RESIDUAL_COUNT_DRIFT", len(sources)))
    return sources


def run():
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    v_sources = reproduce_v_residual_sources(r50g23, r35b, r33, r47j)
    v_checks = []
    dedicated = []
    expected_core_vars = {
        "5e8b0e020f94c302c118aeeac791c133430d5c006fb199d3a2fe4cab79f91113": 15,
        "52b06824542e3cc29f39d1cd3188946971b27e889e5eeebee379751ae4955811": 22,
    }
    for src in v_sources:
        f = src["formula"]
        source_hash = r50g23.r50g4.fhash(f)
        lifted = micro_with_sa_bve(f, r50g23, r35b, r33, r47j)
        minimized, _min_micro, _trace = r50g25v.greedy_truth_blind_residual_minimize(f, r50g23, r35b, r33, r47j)
        replay = r50g25v.replay_to_residual_state(minimized, r50g23, r35b, r33, r47j)
        if replay["kind"] != "RESIDUAL":
            raise AssertionError(("W_MINIMIZED_CORE_DRIFT", source_hash, replay["kind"]))
        core = r33.canonical_formula(replay["state"])
        core_lifted = micro_with_sa_bve(core, r50g23, r35b, r33, r47j)
        expected_var = expected_core_vars[source_hash]
        first_core_sa_var = core_lifted["SA_BVE_events"][0]["var"] if core_lifted["SA_BVE_events"] else None
        if first_core_sa_var != expected_var:
            raise AssertionError(("W_EXPECTED_V_CORE_SA_BVE_PIVOT_DRIFT", source_hash, expected_var, first_core_sa_var))
        v_checks.append({
            "source_hash": source_hash,
            "source_CLV": list(r33.measure(f)),
            "source_old_residual": src["old"].get("semantic_sat") is None,
            "source_lifted_terminal": lifted["terminal"],
            "source_lifted_semantic_sat": lifted["semantic_sat"],
            "source_lifted_reconstruction_pass": lifted["SAT_reconstruction"]["pass"],
            "source_SA_BVE_events": lifted["SA_BVE_events"],
            "minimized_hash": r50g23.r50g4.fhash(minimized),
            "minimized_CLV": list(r33.measure(minimized)),
            "core_hash": r50g23.r50g4.fhash(core),
            "core_CLV": list(r33.measure(core)),
            "expected_core_SA_BVE_var": expected_var,
            "actual_core_first_SA_BVE_var": first_core_sa_var,
            "core_terminal": core_lifted["terminal"],
            "core_semantic_sat": core_lifted["semantic_sat"],
            "core_reconstruction_pass": core_lifted["SAT_reconstruction"]["pass"],
            "core_SA_BVE_events": core_lifted["SA_BVE_events"],
        })
        dedicated.extend([
            {"label": "V_PARENT_SOURCE", "formula": f},
            {"label": "V_MINIMIZED_RESIDUAL_CORE", "formula": core},
        ])

    domain, generation = combined_domain(r33)
    # Dedicated cores may not occur in T/U generation; include them once.
    seen = {tuple(x["formula"]) for x in domain}
    for d in dedicated:
        key = tuple(r33.canonical_formula(d["formula"]))
        if key not in seen:
            domain.append({"formula": r33.canonical_formula(d["formula"]), "origins": [{"gate": "V", "family": d["label"], "size": len(r33.variables(d["formula"])), "meta": {}}]})
            seen.add(key)

    terminal_hist = Counter()
    old_terminal_hist = Counter()
    old_residual = 0
    lifted_residual = 0
    semantic_disagreement = 0
    reconstruction_failure = 0
    sa_bve_usage_hist = Counter()
    sa_bve_total = 0
    max_sa_bve = None
    examples = []

    for index, item in enumerate(domain):
        f = r33.canonical_formula(item["formula"])
        old = r50g25g.micro_normalize(f, r50g23, r35b, r33, r47j)
        lifted = micro_with_sa_bve(f, r50g23, r35b, r33, r47j)
        old_term = str(old.get("terminal")) if old.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        new_term = str(lifted.get("terminal")) if lifted.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        old_terminal_hist[old_term] += 1
        terminal_hist[new_term] += 1
        if old.get("semantic_sat") is None:
            old_residual += 1
        if lifted.get("semantic_sat") is None:
            lifted_residual += 1
        if old.get("semantic_sat") is not None and lifted.get("semantic_sat") is not None and bool(old["semantic_sat"]) != bool(lifted["semantic_sat"]):
            semantic_disagreement += 1
        if lifted.get("semantic_sat") is True and not lifted["SAT_reconstruction"].get("pass", False):
            reconstruction_failure += 1
        n_sa = int(lifted["ledger"]["SA_BVE_applications"])
        sa_bve_usage_hist[n_sa] += 1
        sa_bve_total += n_sa
        row = {
            "index": index,
            "state_hash": r50g23.r50g4.fhash(f),
            "CLV": list(r33.measure(f)),
            "origins": item["origins"],
            "old_terminal": old_term,
            "old_semantic_sat": old.get("semantic_sat"),
            "new_terminal": new_term,
            "new_semantic_sat": lifted.get("semantic_sat"),
            "new_RUP": int(lifted["ledger"]["RUP_successful_strengthenings"]),
            "new_SA_BVE": n_sa,
            "new_rounds": int(lifted["round_count"]),
            "SA_BVE_events": lifted["SA_BVE_events"],
            "SAT_reconstruction_pass": lifted["SAT_reconstruction"].get("pass", True),
            "SA_BVE_symbolic_pair_bound": int(lifted["ledger"]["SA_BVE_resolution_pair_checks_symbolic_bound"]),
            "SA_BVE_symbolic_subsumption_bound": int(lifted["ledger"]["SA_BVE_subsumption_pair_checks_symbolic_bound"]),
        }
        if max_sa_bve is None or (n_sa, row["new_rounds"], tuple(row["CLV"]), row["state_hash"]) > (
            max_sa_bve["new_SA_BVE"], max_sa_bve["new_rounds"], tuple(max_sa_bve["CLV"]), max_sa_bve["state_hash"]
        ):
            max_sa_bve = row
        if (n_sa > 0 or old.get("semantic_sat") is None) and len(examples) < 30:
            examples.append(row)

    all_v_repaired = all(
        x["source_lifted_semantic_sat"] is not None
        and x["core_semantic_sat"] is not None
        and x["source_lifted_reconstruction_pass"]
        and x["core_reconstruction_pass"]
        for x in v_checks
    )
    if not all_v_repaired or lifted_residual or semantic_disagreement or reconstruction_failure:
        verdict = "SA_BVE_POLICY_LIFT_COUNTEREXAMPLE_OR_REGRESSION_FOUND"
        next_gate = "R50G25X_MINIMAL_W_POLICY_COUNTEREXAMPLE_FORENSICS"
    else:
        verdict = "SA_BVE_POLICY_LIFT_REPAIRS_V_RESIDUALS_AND_COMBINED_OUTER_REPLAY"
        next_gate = "R50G25X_UNIVERSAL_COMPLETENESS_OBLIGATION_AND_ADVERSARIAL_STALL_SEARCH"

    return {
        "gate": GATE,
        "parent_V_run": V_RUN,
        "parent_V_result_receipt_commit": V_RECEIPT_COMMIT,
        "W_preregistration_commit": W_PREREG_COMMIT,
        "operator_order": ["R33", "DECLARED_TERMINAL", "AFFINE", "ONE_RUP_OR_IF_NONE_SA_BVE", "RESTART"],
        "V_residual_repair_checks": v_checks,
        "combined_domain_generation": generation,
        "combined_deduplicated_plus_V_core_count": len(domain),
        "old_terminal_partition": dict(sorted(old_terminal_hist.items())),
        "new_terminal_partition": dict(sorted(terminal_hist.items())),
        "old_residual_count": old_residual,
        "new_residual_count": lifted_residual,
        "semantic_disagreement_on_previously_decided_count": semantic_disagreement,
        "SAT_reconstruction_failure_count": reconstruction_failure,
        "SA_BVE_application_histogram": {str(k): int(v) for k, v in sorted(sa_bve_usage_hist.items())},
        "SA_BVE_total_applications": sa_bve_total,
        "max_SA_BVE_usage_case": max_sa_bve,
        "examples": examples,
        "verdict": verdict,
        "next_gate": next_gate,
        "proof_contract": {
            "existing_R42_operator_only": True,
            "independent_SA_BVE_replay_required_each_application": True,
            "strict_CLV_descent_required_each_application": True,
            "SAT_model_reconstruction_through_R33_and_SA_BVE": True,
            "SA_BVE_per_call_symbolic_runtime_envelope_polynomial": True,
            "finite_replay_does_not_prove_completeness": True,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": out["verdict"],
        "count": out["combined_deduplicated_plus_V_core_count"],
        "V_residual_repair_checks": out["V_residual_repair_checks"],
        "old_terminal_partition": out["old_terminal_partition"],
        "new_terminal_partition": out["new_terminal_partition"],
        "old_residual_count": out["old_residual_count"],
        "new_residual_count": out["new_residual_count"],
        "semantic_disagreement": out["semantic_disagreement_on_previously_decided_count"],
        "reconstruction_failures": out["SAT_reconstruction_failure_count"],
        "SA_BVE_hist": out["SA_BVE_application_histogram"],
        "SA_BVE_total": out["SA_BVE_total_applications"],
        "max_SA_BVE_usage_case": out["max_SA_BVE_usage_case"],
        "next_gate": out["next_gate"],
        "firewall": out["firewall"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
