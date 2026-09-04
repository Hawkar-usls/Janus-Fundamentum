from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48d_minimum_local_amortized_pressure_controller as r48d

GATE = "JANUS_TRUMP_R48G_TARGETED_UNIT_WEIGHT_PRESSURE_COUNTEREXAMPLE_HUNT"
R47X_ORDINAL = 22
R47X_ROOT_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
R47X_ROOT_CLV = (75, 199, 22)
R48D_EXPECTED_PIVOTS = [7, 2, 15, 5]
R48D_EXPECTED_MAX_A_STAR = 1
PRIMARY_VARS = frozenset((2, 7, 15, 5))
SECONDARY_VARS = frozenset((11, 20))
MAX_SECOND_MUTATED_ORIGINALS = 64


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def reconstruct_r47x_first_mutation():
    center_original, _, _ = r47x.load_center_original()
    target = None
    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if ordinal != R47X_ORDINAL:
            continue
        if mutated is None:
            raise AssertionError("R48G_R47X_ORDINAL22_MUTATION_MISSING")
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            raise AssertionError("R48G_R47X_ORDINAL22_NO_REACHABLE_FIXPOINT")
        root = canon(reached["formula"])
        target = {
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original": canon(mutated),
            "mutated_original_hash": formula_hash(mutated),
            "reachable_root": root,
            "reachable_root_hash": formula_hash(root),
            "reachable_root_CLV": list(clv(root)),
            "reachability_trajectory": reached["trajectory"],
        }
        break
    if target is None:
        raise AssertionError("R48G_R47X_ORDINAL22_NOT_FOUND")
    if target["reachable_root_hash"] != R47X_ROOT_HASH or tuple(target["reachable_root_CLV"]) != R47X_ROOT_CLV:
        raise AssertionError(("R48G_R47X_ROOT_DRIFT", target["reachable_root_hash"], target["reachable_root_CLV"]))
    return target


def source_phase(first_mutated_original):
    f = canon(first_mutated_original)
    primary = [c for c in f if any(abs(l) in PRIMARY_VARS for l in c)]
    secondary = [c for c in f if c not in primary and any(abs(l) in SECONDARY_VARS for l in c)]
    return primary, secondary


def targeted_second_mutations(first_mutated_original):
    primary, secondary = source_phase(first_mutated_original)
    seen_mutated = set()
    generated = 0
    for phase, sources in (
        ("R48D_TRAJECTORY_PIVOTS_2_7_15_5", primary),
        ("LEGACY_EXPOSURE_PIVOTS_11_20", secondary),
    ):
        for source in sources:
            for replacement in r47i.signed_same_support_variants(source):
                mutated = r47i.mutate_one_clause(first_mutated_original, source, replacement)
                if mutated is None:
                    continue
                mutated = canon(mutated)
                r47x.validate_exact_3cnf(mutated)
                mh = formula_hash(mutated)
                if mh in seen_mutated:
                    continue
                seen_mutated.add(mh)
                generated += 1
                yield {
                    "targeted_ordinal": generated,
                    "phase": phase,
                    "source_clause": list(source),
                    "replacement_clause": list(replacement),
                    "mutated_original": mutated,
                    "mutated_original_hash": mh,
                }
                if generated >= MAX_SECOND_MUTATED_ORIGINALS:
                    return


def scan_state(current):
    current = canon(current)
    rows = []
    candidates = {}
    for var in r33.variables(current):
        candidate = r47m.macro_candidate_full_closure(current, int(var))
        if candidate is None:
            rows.append({
                "var": int(var),
                "candidate": False,
                "eligible": False,
                "terminal": None,
                "a_req": None,
            })
            continue
        if not candidate["DP_independent_replay_pass"]:
            raise AssertionError(("R48G_DP_REPLAY_FAIL", var))
        if not candidate["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R48G_POLY_ENVELOPE_FAIL", var))
        row = r48d.candidate_row(current, candidate, None)
        rows.append(row)
        candidates[int(var)] = candidate
    eligible = [r for r in rows if r.get("eligible", False)]
    terminals = [r for r in eligible if r["terminal"] is not None]
    nonterm = [r for r in eligible if r["terminal"] is None and r["a_req"] is not None]
    if terminals:
        a_star = 0
    elif nonterm:
        a_star = min(int(r["a_req"]) for r in nonterm)
    else:
        a_star = None
    return rows, candidates, eligible, terminals, nonterm, a_star


def independently_replay_all(current, rows, candidates):
    replayed = []
    for row in rows:
        var = int(row["var"])
        if var not in candidates:
            replayed.append(row)
            continue
        candidate = candidates[var]
        replay = r47m.independent_replay(current, candidate)
        if not replay["pass"]:
            raise AssertionError(("R48G_COUNTEREXAMPLE_CANDIDATE_FULL_REPLAY_FAIL", var, replay))
        replayed.append(r48d.candidate_row(current, candidate, True))
    return replayed


def lift_sat_root(root, selected_full, terminal_candidate):
    if terminal_candidate["normalization"]["semantic_sat"] is not True:
        return {"applicable": False, "pass": True}
    assignment = dict(terminal_candidate["normalization"]["terminal_assignment"] or {})
    for before_formula, candidate in reversed(selected_full):
        assignment = r47x.lift_assignment(before_formula, candidate, assignment)
    for v in sorted(set(r33.variables(root)) - set(assignment)):
        assignment[v] = False
    passed = bool(r33.eval_formula(root, assignment))
    if not passed:
        raise AssertionError("R48G_SAT_ROOT_RECONSTRUCTION_FAIL")
    return {
        "applicable": True,
        "pass": True,
        "assignment": {str(k): bool(v) for k, v in sorted(assignment.items())},
    }


def hunt_trajectory(root):
    root = canon(root)
    V0 = clv(root)[2]
    max_probes = V0 * V0
    current = root
    selected_path = []
    selected_full = []
    total_probes = 0
    max_a_star = -1
    hardest_state = None

    for state_index in range(V0 + 1):
        if state_index >= V0:
            raise AssertionError(("R48G_NONTERMINAL_STEP_CAP_EXHAUSTED", clv(current)))
        rows, candidates, eligible, terminals, nonterm, a_star = scan_state(current)
        total_probes += len(rows)
        if total_probes > max_probes:
            raise AssertionError(("R48G_PROBE_CAP_EXCEEDED", total_probes, max_probes))

        if a_star is None:
            replayed = independently_replay_all(current, rows, candidates)
            if any(r.get("terminal") is not None for r in replayed if r.get("candidate", True)):
                raise AssertionError("R48G_NO_CANDIDATE_REPLAY_FOUND_TERMINAL")
            if any(r.get("eligible", False) for r in replayed):
                raise AssertionError("R48G_NO_CANDIDATE_REPLAY_FOUND_ELIGIBLE")
            return {
                "outcome": "NO_VARIABLE_DECREASING_CANDIDATE",
                "max_a_star_before_stop": max_a_star,
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "counterexample": {
                    "state_index": state_index,
                    "state_hash": formula_hash(current),
                    "state_CLV": list(clv(current)),
                    "state_formula": [list(c) for c in current],
                    "a_star": None,
                    "candidate_rows": replayed,
                },
            }

        if int(a_star) > max_a_star:
            max_a_star = int(a_star)
            hardest_state = {
                "state_index": state_index,
                "state_hash": formula_hash(current),
                "state_CLV": list(clv(current)),
                "a_star": int(a_star),
            }

        if not terminals and int(a_star) >= 2:
            replayed = independently_replay_all(current, rows, candidates)
            replay_eligible = [r for r in replayed if r.get("eligible", False)]
            replay_terminals = [r for r in replay_eligible if r["terminal"] is not None]
            replay_nonterm = [r for r in replay_eligible if r["terminal"] is None and r["a_req"] is not None]
            if replay_terminals:
                raise AssertionError("R48G_ASTAR_COUNTEREXAMPLE_REPLAY_FOUND_TERMINAL")
            if not replay_nonterm:
                raise AssertionError("R48G_ASTAR_COUNTEREXAMPLE_REPLAY_LOST_NONTERMINAL_CANDIDATES")
            replay_a_star = min(int(r["a_req"]) for r in replay_nonterm)
            if replay_a_star < 2:
                raise AssertionError(("R48G_ASTAR_COUNTEREXAMPLE_REPLAY_DROPPED", replay_a_star))
            return {
                "outcome": "A_STAR_GE_2",
                "max_a_star_before_stop": max(max_a_star, replay_a_star),
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "counterexample": {
                    "state_index": state_index,
                    "state_hash": formula_hash(current),
                    "state_CLV": list(clv(current)),
                    "state_formula": [list(c) for c in current],
                    "a_star": int(replay_a_star),
                    "candidate_rows": replayed,
                },
            }

        chosen_row = min(eligible, key=r48d.selection_key)
        chosen = candidates[int(chosen_row["var"])]
        replay = r47m.independent_replay(current, chosen)
        if not replay["pass"]:
            raise AssertionError(("R48G_SELECTED_FULL_REPLAY_FAIL", chosen_row["var"], replay))
        chosen_row = r48d.candidate_row(current, chosen, True)
        final_formula = canon(chosen["normalization"]["final_formula"])
        selected_path.append({
            "step": len(selected_path) + 1,
            "state_a_star": int(a_star),
            "var": int(chosen_row["var"]),
            "input_CLV": chosen_row["input_CLV"],
            "forced_DP_CLV": chosen_row["forced_DP_CLV"],
            "final_CLV": chosen_row["final_CLV"],
            "a_req": int(chosen_row["a_req"] or 0),
            "terminal": chosen_row["terminal"],
            "semantic_sat": chosen_row["semantic_sat"],
            "full_R47M_independent_replay_pass": True,
        })
        selected_full.append((current, chosen))

        if chosen_row["terminal"] is not None:
            sat_reconstruction = lift_sat_root(root, selected_full, chosen)
            return {
                "outcome": "TERMINAL_WITHOUT_UNIT_WEIGHT_COUNTEREXAMPLE",
                "max_a_star_before_stop": max_a_star,
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "hardest_state": hardest_state,
                "terminal": {
                    "kind": chosen_row["terminal"],
                    "semantic_sat": chosen_row["semantic_sat"],
                    "final_hash": formula_hash(final_formula),
                    "final_CLV": list(clv(final_formula)),
                    "SAT_root_reconstruction": sat_reconstruction,
                },
                "counterexample": None,
            }
        current = final_formula

    raise AssertionError("R48G_UNREACHABLE_TRAJECTORY_EXIT")


def compact_completed_root(meta, root, result):
    return {
        "targeted_ordinal": int(meta["targeted_ordinal"]),
        "phase": meta["phase"],
        "source_clause": meta["source_clause"],
        "replacement_clause": meta["replacement_clause"],
        "mutated_original_hash": meta["mutated_original_hash"],
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "outcome": result["outcome"],
        "max_a_star": result["max_a_star_before_stop"],
        "candidate_probe_count": int(result["candidate_probe_count"]),
        "selected_pivots": [int(s["var"]) for s in result["selected_path"]],
        "selected_path": result["selected_path"],
        "hardest_state": result.get("hardest_state"),
        "terminal": result.get("terminal"),
    }


def run():
    first = reconstruct_r47x_first_mutation()
    baseline = hunt_trajectory(first["reachable_root"])
    if baseline["outcome"] != "TERMINAL_WITHOUT_UNIT_WEIGHT_COUNTEREXAMPLE":
        raise AssertionError(("R48G_BASELINE_UNEXPECTED_COUNTEREXAMPLE", baseline["outcome"]))
    if baseline["max_a_star_before_stop"] != R48D_EXPECTED_MAX_A_STAR:
        raise AssertionError(("R48G_BASELINE_ASTAR_DRIFT", baseline["max_a_star_before_stop"]))
    if [int(s["var"]) for s in baseline["selected_path"]] != R48D_EXPECTED_PIVOTS:
        raise AssertionError(("R48G_BASELINE_PIVOT_DRIFT", [s["var"] for s in baseline["selected_path"]]))

    metrics = {
        "second_mutated_originals_generated": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "duplicate_reachable_fixpoints_skipped": 0,
        "unique_reachable_fixpoints_evaluated": 0,
        "total_candidate_probes": int(baseline["candidate_probe_count"]),
    }
    seen_fixpoints = {R47X_ROOT_HASH}
    completed = []
    best = {
        "max_a_star": int(baseline["max_a_star_before_stop"]),
        "root_hash": R47X_ROOT_HASH,
        "root_CLV": list(R47X_ROOT_CLV),
        "source": "R47X_BASELINE",
        "hardest_state": baseline.get("hardest_state"),
    }
    sealed_counterexample = None

    for meta in targeted_second_mutations(first["mutated_original"]):
        metrics["second_mutated_originals_generated"] += 1
        reached = r47f.reachable_fixpoint(meta["mutated_original"])
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root = canon(reached["formula"])
        fh = formula_hash(root)
        if fh in seen_fixpoints:
            metrics["duplicate_reachable_fixpoints_skipped"] += 1
            continue
        seen_fixpoints.add(fh)
        metrics["unique_reachable_fixpoints_evaluated"] += 1

        result = hunt_trajectory(root)
        metrics["total_candidate_probes"] += int(result["candidate_probe_count"])
        if result["outcome"] in ("A_STAR_GE_2", "NO_VARIABLE_DECREASING_CANDIDATE"):
            sealed_counterexample = {
                "mutation": {
                    "targeted_ordinal": int(meta["targeted_ordinal"]),
                    "phase": meta["phase"],
                    "source_clause": meta["source_clause"],
                    "replacement_clause": meta["replacement_clause"],
                    "mutated_original_hash": meta["mutated_original_hash"],
                    "mutated_original_formula": [list(c) for c in meta["mutated_original"]],
                    "reachability_trajectory": reached["trajectory"],
                },
                "reachable_root": {
                    "hash": fh,
                    "CLV": list(clv(root)),
                    "formula": [list(c) for c in root],
                },
                "trajectory_before_counterexample": result["selected_path"],
                "counterexample": result["counterexample"],
                "candidate_probe_count": int(result["candidate_probe_count"]),
            }
            break

        record = compact_completed_root(meta, root, result)
        completed.append(record)
        current_max = int(record["max_a_star"])
        best_key = (current_max, int(record["candidate_probe_count"]), tuple(record["root_CLV"]), record["root_hash"])
        old_key = (int(best["max_a_star"]), 0, tuple(best["root_CLV"]), best["root_hash"])
        if best_key > old_key:
            best = {
                "max_a_star": current_max,
                "root_hash": record["root_hash"],
                "root_CLV": record["root_CLV"],
                "source": "SECOND_MUTATION",
                "mutation": {
                    "targeted_ordinal": record["targeted_ordinal"],
                    "phase": record["phase"],
                    "source_clause": record["source_clause"],
                    "replacement_clause": record["replacement_clause"],
                    "mutated_original_hash": record["mutated_original_hash"],
                },
                "hardest_state": record["hardest_state"],
            }

    if sealed_counterexample is not None:
        if sealed_counterexample["counterexample"]["a_star"] is None:
            verdict = "STRONGER_EXPLICIT_REACHABLE_NO_VARIABLE_DECREASING_R47M_CANDIDATE_FOUND"
        else:
            verdict = "EXPLICIT_REACHABLE_UNIT_WEIGHT_COUNTEREXAMPLE_a_star_GE_2_FOUND"
    else:
        verdict = "NO_UNIT_WEIGHT_COUNTEREXAMPLE_WITHIN_FROZEN_TARGETED_BUDGET__FINITE_ONLY"

    return {
        "gate": GATE,
        "verdict": verdict,
        "sealed_first_mutation": {
            "frontier_ordinal": R47X_ORDINAL,
            "phase": first["phase"],
            "source_clause": first["source_clause"],
            "replacement_clause": first["replacement_clause"],
            "mutated_original_hash": first["mutated_original_hash"],
            "reachable_root_hash": first["reachable_root_hash"],
            "reachable_root_CLV": first["reachable_root_CLV"],
        },
        "baseline_R48D_regression": {
            "max_a_star": int(baseline["max_a_star_before_stop"]),
            "selected_pivots": [int(s["var"]) for s in baseline["selected_path"]],
            "pass": True,
        },
        "metrics": metrics,
        "best_finite_pressure_if_no_counterexample": best,
        "completed_roots_before_counterexample": completed,
        "sealed_counterexample": sealed_counterexample,
        "interpretation": {
            "targeted_two_swap_search_only": True,
            "no_counterexample_within_budget_proves_unit_weight_coverage": False,
            "explicit_a_star_ge_2_refutes_only_unit_weight_special_case": True,
            "explicit_a_star_ge_2_does_not_refute_general_polynomial_a_route": True,
            "no_sequence_enumeration": True,
            "no_predeclared_persistent_clause_cap": True,
        },
        "firewall": {
            "UNIVERSAL_UNIT_WEIGHT_COVERAGE": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_a_EXISTS": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    d = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    c = d["sealed_counterexample"]
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "baseline_R48D_regression": d["baseline_R48D_regression"],
        "metrics": d["metrics"],
        "best_finite_pressure_if_no_counterexample": d["best_finite_pressure_if_no_counterexample"],
        "sealed_counterexample": None if c is None else {
            "mutation": c["mutation"],
            "reachable_root": {"hash":c["reachable_root"]["hash"],"CLV":c["reachable_root"]["CLV"]},
            "trajectory_before_counterexample": c["trajectory_before_counterexample"],
            "counterexample": c["counterexample"],
            "candidate_probe_count": c["candidate_probe_count"],
        },
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
