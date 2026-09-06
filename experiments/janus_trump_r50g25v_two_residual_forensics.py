from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25u_certificate_size_theorem_scale_ladder as r50g25u

GATE = "JANUS_TRUMP_R50G25V_MINIMAL_RESIDUAL_FIXPOINT_FORENSICS_AND_ALTERNATE_CERTIFIED_DOOR"
U_RUN = 34043807456
U_JOURNAL_COMMIT = "d56a5e78f693ce7e4a15158a4d32f52e8486710e"
V_PREREG_COMMIT = "695719e3937f89279cb077598707a9a569a0dc79"
EXPECTED_U_RESIDUALS = 2


def run_micro(formula, r50g23, r35b, r33, r47j):
    try:
        return r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j), None
    except AssertionError as exc:
        return None, repr(exc)


def is_residual(formula, r50g23, r35b, r33, r47j):
    micro, exc = run_micro(formula, r50g23, r35b, r33, r47j)
    return exc is None and micro is not None and micro.get("semantic_sat") is None, micro, exc


def replay_to_residual_state(initial, r50g23, r35b, r33, r47j):
    r34 = r50g23.r34
    state = r33.canonical_formula(initial)
    height_bound = r47j.restart_height_bound(state)
    trace = []
    for round_index in range(height_bound + 1):
        before = state
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        row = {
            "round": round_index,
            "before_CLV": list(r33.measure(before)),
            "after_R33_CLV": list(r33.measure(after_r33)),
            "R33_terminal": str(reduced["terminal"]),
            "R33_rule_applications": int(reduced["total_rule_applications"]),
        }
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            row["stop"] = "R33_TERMINAL"
            trace.append(row)
            return {"kind": "TERMINAL", "state": after_r33, "trace": trace, "terminal": str(reduced["terminal"])}
        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            row["stop"] = "AFFINE"
            trace.append(row)
            return {"kind": "AFFINE", "state": after_r33, "trace": trace}
        proposal, ledger = r35b.first_rup_strengthening(after_r33)
        row["single_literal_RUP_scan_ledger"] = ledger
        if proposal is None:
            row["stop"] = "NO_SINGLE_LITERAL_RUP"
            trace.append(row)
            return {"kind": "RESIDUAL", "state": after_r33, "trace": trace}
        if not r35b.independent_up_conflict_checker(after_r33, proposal["assumptions"]):
            raise AssertionError(("V_RUP_CERT_FAIL_DURING_REPLAY", round_index, proposal))
        state = r35b.replace_clause_with_subclause(after_r33, tuple(proposal["source_clause"]), tuple(proposal["strengthened_clause"]))
        row["RUP_source_clause"] = list(proposal["source_clause"])
        row["RUP_strengthened_clause"] = list(proposal["strengthened_clause"])
        row["after_RUP_CLV"] = list(r33.measure(state))
        trace.append(row)
    raise AssertionError("V_HEIGHT_BOUND_EXHAUSTED")


def greedy_truth_blind_residual_minimize(initial, r50g23, r35b, r33, r47j):
    state = r33.canonical_formula(initial)
    trace = []
    # One deterministic clause-deletion sweep. Accepted deletions change the state;
    # rejected clauses are not revisited. This is a reducer, not a minimum proof.
    for clause in list(state):
        if clause not in state:
            continue
        candidate = r33.canonical_formula(c for c in state if c != clause)
        if not candidate:
            continue
        ok, micro, _ = is_residual(candidate, r50g23, r35b, r33, r47j)
        if ok:
            trace.append({
                "op": "DELETE_CLAUSE",
                "removed": list(clause),
                "before_CLV": list(r33.measure(state)),
                "after_CLV": list(r33.measure(candidate)),
                "residual_rounds": int(micro.get("round_count", 0)),
                "residual_RUP": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
            })
            state = candidate

    # Then one literal-deletion sweep over the surviving snapshot.
    for source_clause in list(state):
        if source_clause not in state or len(source_clause) <= 1:
            continue
        current_clause = source_clause
        for lit in list(source_clause):
            if current_clause not in state or lit not in current_clause or len(current_clause) <= 1:
                continue
            shortened = tuple(x for x in current_clause if x != lit)
            candidate = r33.canonical_formula(shortened if c == current_clause else c for c in state)
            ok, micro, _ = is_residual(candidate, r50g23, r35b, r33, r47j)
            if ok:
                trace.append({
                    "op": "DELETE_LITERAL",
                    "source_clause": list(current_clause),
                    "removed_literal": int(lit),
                    "before_CLV": list(r33.measure(state)),
                    "after_CLV": list(r33.measure(candidate)),
                    "residual_rounds": int(micro.get("round_count", 0)),
                    "residual_RUP": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
                })
                state = candidate
                current_clause = shortened
    final_ok, final_micro, final_exc = is_residual(state, r50g23, r35b, r33, r47j)
    if not final_ok:
        raise AssertionError(("V_MINIMIZER_LOST_RESIDUAL", final_exc, final_micro))
    return state, final_micro, trace


def all_proper_nonempty_subclauses(clause):
    clause = tuple(clause)
    for r in range(1, len(clause)):
        for idxs in itertools.combinations(range(len(clause)), r):
            yield tuple(clause[i] for i in idxs)


def all_wider_rup_subclauses(formula, r35b):
    formula = tuple(formula)
    found = []
    checked = 0
    for source in formula:
        if len(source) <= 1:
            continue
        for sub in all_proper_nonempty_subclauses(source):
            # Skip the already exhausted single-literal-removal class. A proper
            # subclause with len(source)-1 literals is exactly R35B's search space.
            if len(sub) == len(source) - 1:
                continue
            checked += 1
            assumptions = tuple(-l for l in sorted(sub, key=r35b.lit_key))
            if r35b.independent_up_conflict_checker(formula, assumptions):
                found.append({
                    "source_clause": list(source),
                    "derived_subclause": list(sub),
                    "removed_literals": [int(l) for l in source if l not in sub],
                    "assumptions": list(assumptions),
                })
    return found, checked


def dp_forensics(formula, r33, r47j):
    before = tuple(r33.measure(formula))
    rows = []
    for var in r33.variables(formula):
        record = r47j.r45a.exact_dp_record(formula, int(var))
        if record is None:
            rows.append({"var": int(var), "record": None})
            continue
        replay = r47j.r45a.independent_dp_replay(formula, record)
        transformed = r33.canonical_formula(record["transformed"])
        after = tuple(r33.measure(transformed))
        pos = sum(1 for c in formula if int(var) in c)
        neg = sum(1 for c in formula if -int(var) in c)
        rows.append({
            "var": int(var),
            "positive_parent_count": pos,
            "negative_parent_count": neg,
            "raw_parent_pair_upper": pos * neg,
            "replay_pass": bool(replay.get("pass")),
            "CLV_before": list(before),
            "CLV_after": list(after),
            "strict_CLV_descent": after < before,
            "clause_growth": int(after[0] - before[0]),
            "literal_growth": int(after[1] - before[1]),
            "transformed_hash": None,
        })
    rows.sort(key=lambda x: (
        x.get("record") is None,
        x.get("clause_growth", 10**9),
        x.get("literal_growth", 10**9),
        x["var"],
    ))
    return rows


def run():
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    items, generation = r50g25u.generate_scale_ladder(r33)
    residual_sources = []
    for item in items:
        formula = r33.canonical_formula(item["formula"])
        micro, exc = run_micro(formula, r50g23, r35b, r33, r47j)
        if exc is not None:
            continue
        if micro is not None and micro.get("semantic_sat") is None:
            replay = replay_to_residual_state(formula, r50g23, r35b, r33, r47j)
            if replay["kind"] != "RESIDUAL":
                raise AssertionError(("V_RESIDUAL_REPLAY_DISAGREEMENT", item, micro, replay))
            residual_sources.append({
                "family": item["family"],
                "size": int(item["size"]),
                "meta": item["meta"],
                "source_formula": formula,
                "source_hash": r50g23.r50g4.fhash(formula),
                "source_CLV": list(r33.measure(formula)),
                "source_micro_rounds": int(micro.get("round_count", 0)),
                "source_micro_RUP": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
                "source_final_CLV": list(micro.get("final_CLV", [])),
                "source_residual_state": replay["state"],
                "source_residual_state_hash": r50g23.r50g4.fhash(replay["state"]),
                "source_residual_state_CLV": list(r33.measure(replay["state"])),
                "source_route_trace": replay["trace"],
            })

    if len(residual_sources) != EXPECTED_U_RESIDUALS:
        raise AssertionError(("V_PARENT_RESIDUAL_COUNT_DRIFT", len(residual_sources), [x["source_hash"] for x in residual_sources]))

    results = []
    for src in residual_sources:
        minimized, min_micro, min_trace = greedy_truth_blind_residual_minimize(
            src["source_formula"], r50g23, r35b, r33, r47j
        )
        min_replay = replay_to_residual_state(minimized, r50g23, r35b, r33, r47j)
        if min_replay["kind"] != "RESIDUAL":
            raise AssertionError("V_MINIMIZED_REPLAY_NOT_RESIDUAL")
        core = r33.canonical_formula(min_replay["state"])

        single, single_ledger = r35b.first_rup_strengthening(core)
        if single is not None:
            raise AssertionError(("V_EXPECTED_EXHAUSTED_SINGLE_LITERAL_RUP", single))

        wider, wider_checked = all_wider_rup_subclauses(core, r35b)
        wider_downstream = []
        for cand in wider[:20]:
            source = tuple(cand["source_clause"])
            derived = tuple(cand["derived_subclause"])
            transformed = r35b.replace_clause_with_subclause(core, source, derived)
            downstream, downstream_exc = run_micro(transformed, r50g23, r35b, r33, r47j)
            wider_downstream.append({
                "candidate": cand,
                "after_CLV": list(r33.measure(transformed)),
                "downstream_exception": downstream_exc,
                "downstream_terminal": None if downstream is None else downstream.get("terminal"),
                "downstream_semantic_sat_known": None if downstream is None else downstream.get("semantic_sat"),
                "downstream_residual": None if downstream is None else downstream.get("semantic_sat") is None,
                "downstream_RUP": None if downstream is None else int(downstream.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
            })

        dp_rows = dp_forensics(core, r33, r47j)
        best_dp = next((r for r in dp_rows if r.get("record") is not None), None)
        # dp_forensics stores no transformed formula to keep output compact; rerun best variable for downstream audit.
        best_dp_downstream = None
        if best_dp is not None:
            rec = r47j.r45a.exact_dp_record(core, int(best_dp["var"]))
            if rec is not None:
                transformed = r33.canonical_formula(rec["transformed"])
                downstream, downstream_exc = run_micro(transformed, r50g23, r35b, r33, r47j)
                best_dp_downstream = {
                    "var": int(best_dp["var"]),
                    "after_CLV": list(r33.measure(transformed)),
                    "transformed_hash": r50g23.r50g4.fhash(transformed),
                    "exception": downstream_exc,
                    "terminal": None if downstream is None else downstream.get("terminal"),
                    "semantic_sat_known": None if downstream is None else downstream.get("semantic_sat"),
                    "residual": None if downstream is None else downstream.get("semantic_sat") is None,
                    "RUP": None if downstream is None else int(downstream.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
                }

        results.append({
            "source": {
                k: v for k, v in src.items()
                if k not in {"source_formula", "source_residual_state", "source_route_trace"}
            },
            "source_formula": [list(c) for c in src["source_formula"]],
            "source_route_trace": src["source_route_trace"],
            "minimization": {
                "truth_used": False,
                "operation_count": len(min_trace),
                "trace": min_trace,
                "minimized_formula": [list(c) for c in minimized],
                "minimized_hash": r50g23.r50g4.fhash(minimized),
                "minimized_CLV": list(r33.measure(minimized)),
                "minimized_micro_rounds": int(min_micro.get("round_count", 0)),
                "minimized_micro_RUP": int(min_micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
                "minimized_final_CLV": list(min_micro.get("final_CLV", [])),
                "residual_core_hash": r50g23.r50g4.fhash(core),
                "residual_core_CLV": list(r33.measure(core)),
                "residual_core_formula": [list(c) for c in core],
            },
            "single_literal_RUP_exhaustive": {
                "proposal": None,
                "ledger": single_ledger,
                "no_single_literal_RUP": True,
            },
            "multi_literal_RUP": {
                "checked_candidate_count": wider_checked,
                "certified_candidate_count": len(wider),
                "candidate_examples": wider[:20],
                "downstream_examples": wider_downstream,
            },
            "unrestricted_DP_forensics": {
                "rows": dp_rows,
                "best_by_clause_then_literal_growth": best_dp,
                "best_downstream": best_dp_downstream,
            },
        })

    any_wider = any(r["multi_literal_RUP"]["certified_candidate_count"] > 0 for r in results)
    any_wider_terminal = any(
        any(x.get("downstream_semantic_sat_known") is not None for x in r["multi_literal_RUP"]["downstream_examples"])
        for r in results
    )
    any_descending_dp = any(
        any(bool(x.get("strict_CLV_descent")) for x in r["unrestricted_DP_forensics"]["rows"] if x.get("record") is not None)
        for r in results
    )
    if any_wider and any_wider_terminal:
        verdict = "RESIDUAL_ELIMINATED_BY_CERTIFIED_MULTI_LITERAL_RUP"
        next_gate = "R50G25W_LIFT_CERTIFIED_MULTI_LITERAL_RUP_TO_BOTH_RESIDUALS_AND_OUTER_REPLAY"
    elif any_descending_dp:
        verdict = "RESIDUAL_HAS_DESCENDING_EXACT_DP_DOOR_OUTSIDE_CURRENT_R33_POLICY"
        next_gate = "R50G25W_DP_POLICY_LIFT_OR_COUNTEREXAMPLE"
    else:
        verdict = "RESIDUAL_REQUIRES_NON_DESCENDING_DP_OR_NEW_DOOR"
        next_gate = "R50G25W_NON_DESCENDING_DP_GROWTH_OR_EXTENSION_DOOR"

    return {
        "gate": GATE,
        "parent_U_run": U_RUN,
        "parent_U_journal_commit": U_JOURNAL_COMMIT,
        "V_preregistration_commit": V_PREREG_COMMIT,
        "reproduced_U_generator_contract": generation,
        "reproduced_residual_fixpoint_count": len(residual_sources),
        "results": results,
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "R35B_none_means_all_single_literal_removals_exhausted": True,
            "multi_literal_RUP_is_certified_by_independent_UP_conflict": True,
            "unrestricted_DP_is_forensic_only_unless_strict_descent_and_policy_are_proved": True,
            "truth_not_used_for_minimization": True,
            "residual_is_counterexample_to_current_micro_scheduler_not_to_P_equals_NP": True,
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
    summary = {
        "verdict": out["verdict"],
        "reproduced_residual_fixpoint_count": out["reproduced_residual_fixpoint_count"],
        "residuals": [
            {
                "source": r["source"],
                "minimized_hash": r["minimization"]["minimized_hash"],
                "minimized_CLV": r["minimization"]["minimized_CLV"],
                "residual_core_hash": r["minimization"]["residual_core_hash"],
                "residual_core_CLV": r["minimization"]["residual_core_CLV"],
                "multi_literal_RUP_checked": r["multi_literal_RUP"]["checked_candidate_count"],
                "multi_literal_RUP_found": r["multi_literal_RUP"]["certified_candidate_count"],
                "best_DP": r["unrestricted_DP_forensics"]["best_by_clause_then_literal_growth"],
                "best_DP_downstream": r["unrestricted_DP_forensics"]["best_downstream"],
            }
            for r in out["results"]
        ],
        "next_gate": out["next_gate"],
        "firewall": out["firewall"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
