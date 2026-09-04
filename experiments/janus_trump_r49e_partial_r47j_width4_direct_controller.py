from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o

GATE = "JANUS_TRUMP_R49E_PARTIAL_R47J_WIDTH4_DIRECT_CONTROLLER"
EXPECTED_HASH = "eb13be26c29c106cf172db0be435aaf852d1e1248fced151c5356791f70024da"
EXPECTED_CLV = (114, 342, 30)
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return tuple(r33.measure(canon(f)))


def fhash(f):
    return r42.formula_hash(canon(f))


def max_width(f):
    x = canon(f)
    return max((len(c) for c in x), default=0)


def width_histogram(f):
    out = {}
    for c in canon(f):
        k = str(len(c))
        out[k] = out.get(k, 0) + 1
    return out


def candidate_row(current, candidate, replay_pass=None):
    final = canon(candidate["normalization"]["final_formula"])
    before_vars = set(r33.variables(current))
    after_vars = set(r33.variables(final))
    terminal = candidate["normalization"]["terminal"]
    delta_v = len(before_vars) - len(after_vars)
    no_fresh = after_vars <= before_vars
    w = max_width(final)
    eligible = bool(terminal is not None or (delta_v >= 1 and no_fresh))
    safe = bool(terminal is not None or (eligible and w <= WIDTH_CAP))
    return {
        "var": int(candidate["var"]),
        "input_CLV": list(clv(current)),
        "forced_DP_CLV": list(candidate["DP"]["measure_after_forced_DP"]),
        "final_CLV": list(clv(final)),
        "terminal": terminal,
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "delta_V_eliminated": int(delta_v),
        "no_fresh_variables": bool(no_fresh),
        "eligible": bool(eligible),
        "final_max_width": int(w),
        "final_width_histogram": width_histogram(final),
        "width4_safe": bool(safe),
        "R47J_legacy_CLV_accepted_flag": bool(candidate["accepted"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "R47J_independent_replay_pass": replay_pass,
        "R47J_round_count": int(candidate["normalization"]["round_count"]),
        "R47J_restart_count": int(candidate["normalization"]["restart_count"]),
        "R47J_RUP_checks": int(candidate["normalization"]["ledger"]["RUP_checks"]),
        "SA_BVE_application_count": 0,
    }


def scan(current, replay_all=False):
    rows = []
    candidates = {}
    for v in r33.variables(current):
        c = r47j.macro_candidate_fixpoint(current, int(v))
        if c is None:
            rows.append({"var": int(v), "candidate": False, "eligible": False, "width4_safe": False})
            continue
        if not c["DP_independent_replay_pass"] or not c["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R49E_CANDIDATE_INTEGRITY_FAIL", v))
        replay_pass = None
        if replay_all:
            replay = r47j.independent_fixpoint_macro_replay(current, c)
            if not replay["pass"]:
                raise AssertionError(("R49E_REPLAY_FAIL", v, replay))
            replay_pass = True
        rows.append(candidate_row(current, c, replay_pass))
        candidates[int(v)] = c
    return rows, candidates


def lift_assignment_through_nonterminal(before_formula, candidate, assignment_after):
    before = canon(before_formula)
    final = canon(candidate["normalization"]["final_formula"])
    assignment = {int(k): bool(v) for k, v in dict(assignment_after).items()}

    final_vars = set(r33.variables(final))
    for v in final_vars:
        if v not in assignment:
            assignment[v] = False
    if not r33.eval_formula(final, assignment):
        raise AssertionError(("R49E_LIFT_INPUT_ASSIGNMENT_DOES_NOT_SATISFY_SUCCESSOR", candidate["var"]))

    for result in reversed(candidate["normalization"]["R33_reconstruction_results"]):
        assignment = r33.reconstruct_model(result, assignment)

    assignment = r42.reconstruct_sa_bve(candidate["DP"], assignment)
    for v in r33.variables(before):
        if v not in assignment:
            assignment[v] = False

    passed = r33.eval_formula(before, assignment)
    if not passed:
        raise AssertionError(("R49E_PREDECESSOR_RECONSTRUCTION_FAIL", candidate["var"], clv(before)))
    return assignment


def lift_root_sat(root, selected_nonterminal, terminal_candidate):
    terminal_sat = terminal_candidate["normalization"]["semantic_sat"]
    if terminal_sat is not True:
        return {"applicable": False, "pass": True, "semantic_sat": terminal_sat}

    terminal_reconstruction = terminal_candidate["SAT_reconstruction"]
    if not terminal_reconstruction.get("applicable") or not terminal_reconstruction.get("pass"):
        raise AssertionError(("R49E_TERMINAL_SAT_RECONSTRUCTION_MISSING", terminal_reconstruction))
    assignment = {int(k): bool(v) for k, v in terminal_reconstruction["assignment"].items()}

    for before, candidate in reversed(selected_nonterminal):
        assignment = lift_assignment_through_nonterminal(before, candidate, assignment)

    for v in r33.variables(root):
        if v not in assignment:
            assignment[v] = False
    passed = r33.eval_formula(canon(root), assignment)
    if not passed:
        raise AssertionError("R49E_ROOT_SAT_RECONSTRUCTION_FAIL")
    return {"applicable": True, "pass": True, "semantic_sat": True, "assignment": assignment}


def load_root():
    original, _, _ = r47x.load_center_original()
    root = canon(original)
    if fhash(root) != EXPECTED_HASH:
        raise AssertionError(("R49E_HASH_DRIFT", fhash(root)))
    if clv(root) != EXPECTED_CLV:
        raise AssertionError(("R49E_CLV_DRIFT", clv(root)))
    if max_width(root) != 3:
        raise AssertionError(("R49E_WIDTH_DRIFT", max_width(root)))
    r47x.validate_exact_3cnf(root)
    return root


def run():
    root = load_root()
    current = root
    V0 = clv(root)[2]
    selected_path = []
    selected_nonterminal = []
    total_probes = 0
    max_persisted_width = max_width(root)
    total_selected_RUP_checks = 0

    for state_index in range(V0 + 1):
        if state_index >= V0:
            raise AssertionError(("R49E_STEP_CAP_EXHAUSTED", clv(current)))
        if max_width(current) > WIDTH_CAP:
            raise AssertionError(("R49E_PERSISTED_WIDTH_DRIFT", state_index, max_width(current)))

        rows, candidates = scan(current, replay_all=False)
        total_probes += len(rows)
        if total_probes > V0 * V0:
            raise AssertionError(("R49E_PROBE_CAP_EXCEEDED", total_probes, V0 * V0))
        safe = [r for r in rows if r.get("width4_safe", False)]

        if not safe:
            replay_rows, _ = scan(current, replay_all=True)
            replay_safe = [r for r in replay_rows if r.get("width4_safe", False)]
            if replay_safe:
                raise AssertionError(("R49E_OBSTRUCTION_REPLAY_FOUND_SAFE", replay_safe))
            return {
                "gate": GATE,
                "verdict": "EXPLICIT_PARTIAL_R47J_WIDTH4_CONTROLLER_OBSTRUCTION_FOUND",
                "root": {"hash": fhash(root), "CLV": list(clv(root)), "max_width": max_width(root)},
                "selected_path": selected_path,
                "candidate_probe_count": total_probes,
                "max_persisted_width": max_persisted_width,
                "total_selected_RUP_checks": total_selected_RUP_checks,
                "obstruction": {
                    "state_index": int(state_index),
                    "state_hash": fhash(current),
                    "state_CLV": list(clv(current)),
                    "state_max_width": max_width(current),
                    "state_formula": [list(c) for c in current],
                    "candidate_rows": replay_rows,
                },
                "terminal": None,
                "firewall": firewall(),
            }

        chosen_row = min(safe, key=lambda r: int(r["var"]))
        chosen = candidates[int(chosen_row["var"])]
        replay = r47j.independent_fixpoint_macro_replay(current, chosen)
        if not replay["pass"]:
            raise AssertionError(("R49E_SELECTED_REPLAY_FAIL", chosen_row["var"], replay))
        chosen_row = candidate_row(current, chosen, True)
        final = canon(chosen["normalization"]["final_formula"])
        total_selected_RUP_checks += int(chosen_row["R47J_RUP_checks"])

        selected_path.append({
            "step": len(selected_path) + 1,
            "state_hash": fhash(current),
            "state_CLV": list(clv(current)),
            "state_max_width": max_width(current),
            **chosen_row,
        })

        if chosen_row["terminal"] is not None:
            sat_lift = lift_root_sat(root, selected_nonterminal, chosen)
            if chosen_row["semantic_sat"] is True and not sat_lift["pass"]:
                raise AssertionError("R49E_SAT_LIFT_FAIL")
            return {
                "gate": GATE,
                "verdict": "PARTIAL_R47J_DIRECT_WIDTH4_CONTROLLER_REACHES_CERTIFIED_TERMINAL__FINITE_ONLY",
                "root": {"hash": fhash(root), "CLV": list(clv(root)), "max_width": max_width(root)},
                "selected_path": selected_path,
                "candidate_probe_count": total_probes,
                "max_persisted_width": max(max_persisted_width, max_width(final)),
                "total_selected_RUP_checks": total_selected_RUP_checks,
                "obstruction": None,
                "terminal": {
                    "kind": chosen_row["terminal"],
                    "semantic_sat": chosen_row["semantic_sat"],
                    "final_hash": fhash(final),
                    "final_CLV": list(clv(final)),
                    "SAT_root_reconstruction": sat_lift,
                },
                "firewall": firewall(),
            }

        if chosen_row["final_max_width"] > WIDTH_CAP:
            raise AssertionError(("R49E_SELECTED_WIDTH_FAIL", chosen_row))
        if chosen_row["delta_V_eliminated"] < 1 or not chosen_row["no_fresh_variables"]:
            raise AssertionError(("R49E_SELECTED_PROGRESS_FAIL", chosen_row))

        selected_nonterminal.append((current, chosen))
        max_persisted_width = max(max_persisted_width, int(chosen_row["final_max_width"]))
        current = final

    raise AssertionError("R49E_UNREACHABLE_EXIT")


def firewall():
    return {
        "PARTIAL_R47J_WIDTH4_CONTROLLER_UNIVERSAL_COVERAGE": "NOT_PROVED_UNLESS_REFUTED_BY_THIS_GATE",
        "DIRECT_W4_STEP_COVERAGE": "OPEN",
        "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED",
        "O4_UNIVERSAL_COVERAGE": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    out = run()
    if a.output is not None:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "root": out["root"],
        "selected_pivots": [x["var"] for x in out["selected_path"]],
        "persisted_widths": [x["final_max_width"] for x in out["selected_path"]],
        "selected_R47J_legacy_CLV_flags": [x["R47J_legacy_CLV_accepted_flag"] for x in out["selected_path"]],
        "SA_BVE_counts": [x["SA_BVE_application_count"] for x in out["selected_path"]],
        "candidate_probe_count": out["candidate_probe_count"],
        "total_selected_RUP_checks": out["total_selected_RUP_checks"],
        "max_persisted_width": out["max_persisted_width"],
        "terminal": out["terminal"],
        "obstruction": None if out["obstruction"] is None else {
            "state_hash": out["obstruction"]["state_hash"],
            "state_CLV": out["obstruction"]["state_CLV"],
            "state_max_width": out["obstruction"]["state_max_width"],
        },
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
