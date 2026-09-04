from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o

GATE = "JANUS_TRUMP_R48V_R47J_WIDTH5_DISCHARGE_OPERATOR_FORENSICS"
EXPECTED_ROOT = "3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
PATH = [2, 4, 5, 7, 9, 10]
DEEP_STEPS = {3, 4, 6}
RESET_STEPS = {3, 4}
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def maxw(f):
    x = canon(f)
    return max((len(c) for c in x), default=0)


def fhash(f):
    return r48o.formula_hash(canon(f))


def width5_clauses(f):
    return [list(c) for c in canon(f) if len(c) == 5]


def digest(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def state_metrics(f):
    w5 = width5_clauses(f)
    return {
        "hash": fhash(f),
        "CLV": list(clv(f)),
        "max_width": maxw(f),
        "width5_clause_count": len(w5),
        "width5_clauses_sha256": digest(w5),
    }


def exact_r47j_trace(forced):
    forced = canon(forced)
    state = forced
    bound = r47j.restart_height_bound(forced)
    rounds = []
    terminal = None
    first_discharge = None

    for round_index in range(bound + 1):
        before = state
        before_m = state_metrics(before)
        reduced = r33.simplify(before)
        after_r33 = canon(reduced["final_formula"])
        r33_m = state_metrics(after_r33)
        row = {
            "round": round_index,
            "before": before_m,
            "R33": {
                **r33_m,
                "application_count": int(reduced["total_rule_applications"]),
                "declared_terminal": reduced["terminal"],
                "removed_width5_clause_count": before_m["width5_clause_count"] - r33_m["width5_clause_count"],
            },
        }
        if first_discharge is None and before_m["max_width"] > WIDTH_CAP and r33_m["max_width"] <= WIDTH_CAP:
            first_discharge = {"operator": "R33", "round": round_index}

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = r47j.r42.solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("R48V_R33_TERMINAL_VERIFY_FAIL", round_index, solved))
            terminal = solved["kind"]
            row["stop"] = terminal
            rounds.append(row)
            state = after_r33
            break

        affine = r47j.r34.recognize_complete_affine_cnf(after_r33)
        row["affine_recognized"] = bool(affine["recognized"])
        if affine["recognized"]:
            solution = r47j.r34.solve_gf2_with_certificate(affine["equations"])
            verify = r47j.r34.verify_affine_certificate(after_r33, affine, solution)
            if not verify["pass"]:
                raise AssertionError(("R48V_AFFINE_VERIFY_FAIL", round_index, verify))
            terminal = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            row["stop"] = terminal
            rounds.append(row)
            state = after_r33
            break

        rup = r47j.r35b.run_candidate(after_r33)
        rup_replay = r47j.r35b.independent_certificate_replay(after_r33, rup)
        if not rup_replay["pass"]:
            raise AssertionError(("R48V_RUP_REPLAY_FAIL", round_index, rup_replay))
        after_rup = canon(rup["final_formula"])
        rup_m = state_metrics(after_rup)
        row["RUP"] = {
            **rup_m,
            "status": rup["status"],
            "history_count": len(rup.get("history", [])),
            "independent_replay_pass": True,
            "removed_width5_clause_count": r33_m["width5_clause_count"] - rup_m["width5_clause_count"],
        }
        if first_discharge is None and r33_m["max_width"] > WIDTH_CAP and rup_m["max_width"] <= WIDTH_CAP:
            first_discharge = {"operator": "RUP", "round": round_index}

        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            terminal = "RUP_UNSAT"
            row["stop"] = terminal
            rounds.append(row)
            state = after_rup
            break

        if after_rup != after_r33:
            if not clv(after_rup) < clv(after_r33):
                raise AssertionError(("R48V_RUP_NOT_DESCENT", round_index, clv(after_r33), clv(after_rup)))
            row["restart"] = True
            rounds.append(row)
            state = after_rup
            continue

        row["stop"] = "CERTIFIED_NORMALIZATION_FIXPOINT"
        rounds.append(row)
        state = after_rup
        break
    else:
        raise AssertionError(("R48V_HEIGHT_BOUND_EXHAUSTED", bound))

    frozen = r47j.normalize_to_certified_fixpoint(forced)
    frozen_final = canon(frozen["final_formula"])
    exact_match = {
        "final_hash": fhash(state) == fhash(frozen_final),
        "final_CLV": clv(state) == clv(frozen_final),
        "terminal": terminal == frozen["terminal"],
        "round_count": len(rounds) == int(frozen["round_count"]),
    }
    if not all(exact_match.values()):
        raise AssertionError(("R48V_TRACE_DRIFT_FROM_FROZEN_R47J", exact_match, terminal, frozen["terminal"]))
    return {
        "forced": state_metrics(forced),
        "rounds": rounds,
        "first_width_discharge": first_discharge,
        "final": state_metrics(state),
        "terminal": terminal,
        "exact_match_to_frozen_R47J": exact_match,
    }


def run(output: Path | None = None):
    _, _, root = r48o.reconstruct_root()
    if fhash(root) != EXPECTED_ROOT:
        raise AssertionError("R48V_ROOT_DRIFT")
    current = canon(root)
    rows = []
    reset_ops = []

    for step, var in enumerate(PATH, 1):
        candidate = r48o.r47m.macro_candidate_full_closure(current, int(var))
        if candidate is None:
            raise AssertionError(("R48V_SELECTED_CANDIDATE_MISSING", step, var))
        replay = r48o.r47m.independent_replay(current, candidate)
        if not replay["pass"]:
            raise AssertionError(("R48V_FULL_REPLAY_FAIL", step, var, replay))
        forced = canon(candidate["DP"]["transformed"])
        full_final = canon(candidate["normalization"]["final_formula"])

        if step in DEEP_STEPS:
            trace = exact_r47j_trace(forced)
            if maxw(forced) != 5:
                raise AssertionError(("R48V_EXPECTED_WIDTH5_DRIFT", step, maxw(forced)))
            if step in RESET_STEPS:
                if trace["terminal"] is not None or trace["final"]["max_width"] > WIDTH_CAP:
                    raise AssertionError(("R48V_NONTERMINAL_RESET_DRIFT", step, trace))
                if trace["first_width_discharge"] is None:
                    raise AssertionError(("R48V_MISSING_DISCHARGE", step))
                reset_ops.append(trace["first_width_discharge"])
            else:
                if trace["final"]["max_width"] <= WIDTH_CAP:
                    raise AssertionError(("R48V_STEP6_R47J_UNEXPECTED_RESET", trace["final"]))
            rows.append({
                "step": step,
                "pivot": int(var),
                "current": state_metrics(current),
                "R47J_trace": trace,
                "full_R47M_final": state_metrics(full_final),
                "full_terminal": candidate["normalization"]["terminal"],
                "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
                "full_independent_replay_pass": True,
            })
        current = full_final

    if len(reset_ops) != 2:
        raise AssertionError(("R48V_RESET_OPERATOR_COUNT", reset_ops))
    operators = [x["operator"] for x in reset_ops]
    rounds = [int(x["round"]) for x in reset_ops]
    if operators == ["R33", "R33"] and rounds == [0, 0]:
        classification = "R33_DOMINANT_WIDTH5_DISCHARGE"
    elif operators == ["RUP", "RUP"] and rounds == [0, 0]:
        classification = "RUP_DOMINANT_WIDTH5_DISCHARGE"
    else:
        classification = "MIXED_R33_RUP_WIDTH5_DISCHARGE"

    out = {
        "gate": GATE,
        "parent_R48T_seal_commit": "34d13b4e62b1756a4c5e4c37071b4ef882990d07",
        "classification": classification,
        "sealed_path": PATH,
        "deep_trace_steps": sorted(DEEP_STEPS),
        "nonterminal_reset_steps": sorted(RESET_STEPS),
        "rows": rows,
        "reset_operators": reset_ops,
        "interpretation": {
            "finite_path_only": True,
            "smallest_observed_width5_discharge_operator_identified": True,
            "universal_width_reset_lemma_proved": False,
            "next_front_if_R33": "PROVE_OR_FALSIFY_R33_WIDTH5_TO_WIDTH4_DISCHARGE_ON_ALL_W4_PERSISTED_DP_SUCCESSORS",
            "next_front_if_RUP": "PROVE_OR_FALSIFY_RUP_WIDTH5_TO_WIDTH4_DISCHARGE_ON_ALL_W4_PERSISTED_DP_SUCCESSORS",
            "next_front_if_mixed": "SEARCH_EXPLICIT_W5_SURVIVOR_OF_JOINT_R33_RUP_FIXPOINT",
        },
        "firewall": {
            "UNIVERSAL_WIDTH_RESET_LEMMA": "NOT_PROVED",
            "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED",
            "UNIVERSAL_CONSTANT_WIDTH_COVERAGE": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "gate": GATE,
        "classification": classification,
        "reset_operators": reset_ops,
        "steps": [{
            "step": r["step"],
            "pivot": r["pivot"],
            "forced": r["R47J_trace"]["forced"],
            "first_discharge": r["R47J_trace"]["first_width_discharge"],
            "final": r["R47J_trace"]["final"],
            "terminal": r["R47J_trace"]["terminal"],
            "round_count": len(r["R47J_trace"]["rounds"]),
            "SA_BVE": r["SA_BVE_application_count"],
            "full_terminal": r["full_terminal"],
        } for r in rows],
        "firewall": out["firewall"],
    }, sort_keys=True))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    run(a.output)


if __name__ == "__main__":
    main()
