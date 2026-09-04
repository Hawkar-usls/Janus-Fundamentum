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
import janus_trump_r48g_targeted_unit_weight_pressure_counterexample_hunt as r48g

GATE = "JANUS_TRUMP_R48I_TARGETED_PRESSURE_ESCALATION_A4_OR_BOUND"
TARGET_A = 4
R48G_SECOND_ORDINAL = 4
EXPECTED_SECOND_MUTATED_HASH = "720355b9542ddccc7bfe6ae1fcda35eb6879ad921aebb4a8b6f63998ecaadd0c"
EXPECTED_ROOT_HASH = "3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
EXPECTED_ROOT_CLV = (75, 199, 22)
EXPECTED_A3_STATE_HASH = "9c06bfcfecbff7b79342a0c4113c77bba310e976ad1ac1b52120c887782d96ac"
EXPECTED_A3_STATE_CLV = (78, 223, 18)
PRIMARY_VARS = frozenset((9, 11, 12, 16, 25))
SECONDARY_VARS = frozenset((26, 7, 2))
MAX_THIRD_MUTATIONS = 64


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def reconstruct_r48g_second_mutation():
    first = r48g.reconstruct_r47x_first_mutation()
    selected = None
    for meta in r48g.targeted_second_mutations(first["mutated_original"]):
        if int(meta["targeted_ordinal"]) == R48G_SECOND_ORDINAL:
            selected = meta
            break
    if selected is None:
        raise AssertionError("R48I_R48G_SECOND_MUTATION_NOT_FOUND")
    if selected["mutated_original_hash"] != EXPECTED_SECOND_MUTATED_HASH:
        raise AssertionError(("R48I_SECOND_MUTATED_HASH_DRIFT", selected["mutated_original_hash"]))
    reached = r47f.reachable_fixpoint(selected["mutated_original"])
    if reached is None:
        raise AssertionError("R48I_SECOND_MUTATION_NO_REACHABLE_ROOT")
    root = canon(reached["formula"])
    if formula_hash(root) != EXPECTED_ROOT_HASH or clv(root) != EXPECTED_ROOT_CLV:
        raise AssertionError(("R48I_ROOT_DRIFT", formula_hash(root), clv(root)))
    return first, selected, reached, root


def source_phases(formula):
    f = canon(formula)
    phase1 = [c for c in f if any(abs(l) in PRIMARY_VARS for l in c)]
    phase2 = [c for c in f if c not in phase1 and any(abs(l) in SECONDARY_VARS for l in c)]
    return phase1, phase2


def third_mutations(second_mutated_original):
    phase1, phase2 = source_phases(second_mutated_original)
    seen = set()
    ordinal = 0
    for phase, sources in (
        ("R48G_MIN_PRESSURE_PIVOTS_9_11_12_16_25", phase1),
        ("R48G_PREDECESSOR_PATH_PIVOTS_26_7_2", phase2),
    ):
        for source in sources:
            for replacement in r47i.signed_same_support_variants(source):
                mutated = r47i.mutate_one_clause(second_mutated_original, source, replacement)
                if mutated is None:
                    continue
                mutated = canon(mutated)
                r47x.validate_exact_3cnf(mutated)
                h = formula_hash(mutated)
                if h in seen:
                    continue
                seen.add(h)
                ordinal += 1
                yield {
                    "third_ordinal": ordinal,
                    "phase": phase,
                    "source_clause": list(source),
                    "replacement_clause": list(replacement),
                    "mutated_original": mutated,
                    "mutated_original_hash": h,
                }
                if ordinal >= MAX_THIRD_MUTATIONS:
                    return


def full_replay_threshold_state(state, rows, candidates, minimum_required):
    replayed = r48g.independently_replay_all(state, rows, candidates)
    eligible = [r for r in replayed if r.get("eligible", False)]
    terminals = [r for r in eligible if r.get("terminal") is not None]
    nonterminal = [r for r in eligible if r.get("terminal") is None and r.get("a_req") is not None]
    if terminals:
        raise AssertionError("R48I_THRESHOLD_REPLAY_FOUND_TERMINAL")
    if not nonterminal:
        return replayed, None
    a_star = min(int(r["a_req"]) for r in nonterminal)
    if a_star < minimum_required:
        raise AssertionError(("R48I_THRESHOLD_REPLAY_DROPPED", a_star, minimum_required))
    return replayed, a_star


def hunt_threshold(root, threshold=TARGET_A):
    root = canon(root)
    V0 = clv(root)[2]
    max_probes = V0 * V0
    current = root
    selected_path = []
    selected_full = []
    pressure_records = []
    total_probes = 0
    max_a_star = -1

    for state_index in range(V0 + 1):
        if state_index >= V0:
            raise AssertionError(("R48I_STEP_CAP_EXHAUSTED", clv(current)))
        rows, candidates, eligible, terminals, nonterm, a_star = r48g.scan_state(current)
        total_probes += len(rows)
        if total_probes > max_probes:
            raise AssertionError(("R48I_PROBE_CAP_EXCEEDED", total_probes, max_probes))

        if a_star is None:
            replayed = r48g.independently_replay_all(current, rows, candidates)
            if any(r.get("eligible", False) for r in replayed):
                raise AssertionError("R48I_NO_CANDIDATE_REPLAY_FOUND_ELIGIBLE")
            return {
                "outcome": "NO_VARIABLE_DECREASING_CANDIDATE",
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "pressure_records": pressure_records,
                "max_a_star": max_a_star,
                "threshold_state": {
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
            pressure_records.append({
                "state_index": state_index,
                "state_hash": formula_hash(current),
                "state_CLV": list(clv(current)),
                "a_star": int(a_star),
                "selected_prefix": [int(s["var"]) for s in selected_path],
            })

        if not terminals and int(a_star) >= threshold:
            replayed, replay_a = full_replay_threshold_state(current, rows, candidates, threshold)
            if replay_a is None:
                raise AssertionError("R48I_A_THRESHOLD_REPLAY_LOST_ALL_NONTERMINAL_CANDIDATES")
            return {
                "outcome": "A_STAR_THRESHOLD_REACHED",
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "pressure_records": pressure_records,
                "max_a_star": max(max_a_star, int(replay_a)),
                "threshold_state": {
                    "state_index": state_index,
                    "state_hash": formula_hash(current),
                    "state_CLV": list(clv(current)),
                    "state_formula": [list(c) for c in current],
                    "a_star": int(replay_a),
                    "candidate_rows": replayed,
                },
            }

        chosen_row = min(eligible, key=r48d.selection_key)
        chosen = candidates[int(chosen_row["var"])]
        replay = r47m.independent_replay(current, chosen)
        if not replay["pass"]:
            raise AssertionError(("R48I_SELECTED_FULL_REPLAY_FAIL", chosen_row["var"], replay))
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
            sat_reconstruction = r48g.lift_sat_root(root, selected_full, chosen)
            return {
                "outcome": "TERMINAL_BEFORE_THRESHOLD",
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "pressure_records": pressure_records,
                "max_a_star": max_a_star,
                "threshold_state": None,
                "terminal": {
                    "kind": chosen_row["terminal"],
                    "semantic_sat": chosen_row["semantic_sat"],
                    "final_hash": formula_hash(final_formula),
                    "final_CLV": list(clv(final_formula)),
                    "SAT_root_reconstruction": sat_reconstruction,
                },
            }
        current = final_formula

    raise AssertionError("R48I_UNREACHABLE_HUNT_EXIT")


def compact_completed(meta, root, result):
    return {
        "third_ordinal": int(meta["third_ordinal"]),
        "phase": meta["phase"],
        "source_clause": meta["source_clause"],
        "replacement_clause": meta["replacement_clause"],
        "mutated_original_hash": meta["mutated_original_hash"],
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "outcome": result["outcome"],
        "max_a_star": int(result["max_a_star"]),
        "candidate_probe_count": int(result["candidate_probe_count"]),
        "selected_pivots": [int(s["var"]) for s in result["selected_path"]],
        "pressure_records": result["pressure_records"],
        "terminal": result.get("terminal"),
    }


def run():
    first, second, second_reached, root = reconstruct_r48g_second_mutation()
    baseline = hunt_threshold(root, TARGET_A)
    baseline_a3 = next((r for r in baseline["pressure_records"] if r["state_hash"] == EXPECTED_A3_STATE_HASH), None)
    if baseline_a3 is None or baseline_a3["a_star"] != 3 or tuple(baseline_a3["state_CLV"]) != EXPECTED_A3_STATE_CLV:
        raise AssertionError(("R48I_BASELINE_A3_REGRESSION_FAIL", baseline["pressure_records"]))

    if baseline["outcome"] in ("A_STAR_THRESHOLD_REACHED", "NO_VARIABLE_DECREASING_CANDIDATE"):
        sealed = {
            "source": "BASELINE_CONTINUATION_NO_THIRD_MUTATION",
            "mutation": None,
            "reachable_root": {"hash": formula_hash(root), "CLV": list(clv(root))},
            "result": baseline,
        }
        verdict = (
            "STRONGER_EXPLICIT_REACHABLE_NO_VARIABLE_DECREASING_R47M_CANDIDATE_FOUND"
            if baseline["outcome"] == "NO_VARIABLE_DECREASING_CANDIDATE"
            else "EXPLICIT_REACHABLE_PRESSURE_COUNTEREXAMPLE_a_star_GE_4_FOUND"
        )
        return make_output(first, second, baseline, {}, [], sealed, verdict)

    metrics = {
        "third_mutated_originals_generated": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_roots": 0,
        "duplicate_reachable_roots_skipped": 0,
        "unique_reachable_roots_evaluated": 0,
        "total_candidate_probes": int(baseline["candidate_probe_count"]),
    }
    seen_roots = {formula_hash(root)}
    completed = []
    best = {
        "max_a_star": int(baseline["max_a_star"]),
        "source": "R48G_BASELINE_CONTINUATION",
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "pressure_records": baseline["pressure_records"],
        "selected_pivots": [int(s["var"]) for s in baseline["selected_path"]],
    }
    sealed = None

    for meta in third_mutations(second["mutated_original"]):
        metrics["third_mutated_originals_generated"] += 1
        reached = r47f.reachable_fixpoint(meta["mutated_original"])
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_roots"] += 1
        candidate_root = canon(reached["formula"])
        rh = formula_hash(candidate_root)
        if rh in seen_roots:
            metrics["duplicate_reachable_roots_skipped"] += 1
            continue
        seen_roots.add(rh)
        metrics["unique_reachable_roots_evaluated"] += 1
        result = hunt_threshold(candidate_root, TARGET_A)
        metrics["total_candidate_probes"] += int(result["candidate_probe_count"])

        if result["outcome"] in ("A_STAR_THRESHOLD_REACHED", "NO_VARIABLE_DECREASING_CANDIDATE"):
            sealed = {
                "source": "THIRD_TARGETED_MUTATION",
                "mutation": {
                    "third_ordinal": int(meta["third_ordinal"]),
                    "phase": meta["phase"],
                    "source_clause": meta["source_clause"],
                    "replacement_clause": meta["replacement_clause"],
                    "mutated_original_hash": meta["mutated_original_hash"],
                    "mutated_original_formula": [list(c) for c in meta["mutated_original"]],
                    "reachability_trajectory": reached["trajectory"],
                },
                "reachable_root": {"hash": rh, "CLV": list(clv(candidate_root)), "formula": [list(c) for c in candidate_root]},
                "result": result,
            }
            break

        record = compact_completed(meta, candidate_root, result)
        completed.append(record)
        key = (int(record["max_a_star"]), int(record["candidate_probe_count"]), tuple(record["root_CLV"]), record["root_hash"])
        old = (int(best["max_a_star"]), 0, tuple(best["root_CLV"]), best["root_hash"])
        if key > old:
            best = {
                "max_a_star": int(record["max_a_star"]),
                "source": "THIRD_TARGETED_MUTATION",
                "root_hash": record["root_hash"],
                "root_CLV": record["root_CLV"],
                "mutation": {
                    "third_ordinal": record["third_ordinal"],
                    "phase": record["phase"],
                    "source_clause": record["source_clause"],
                    "replacement_clause": record["replacement_clause"],
                    "mutated_original_hash": record["mutated_original_hash"],
                },
                "pressure_records": record["pressure_records"],
                "selected_pivots": record["selected_pivots"],
            }

    if sealed is None:
        verdict = "NO_a_star_GE_4_WITHIN_FROZEN_TARGETED_BUDGET__MAX_PRESSURE_SEALED_FINITE_ONLY"
    elif sealed["result"]["outcome"] == "NO_VARIABLE_DECREASING_CANDIDATE":
        verdict = "STRONGER_EXPLICIT_REACHABLE_NO_VARIABLE_DECREASING_R47M_CANDIDATE_FOUND"
    else:
        verdict = "EXPLICIT_REACHABLE_PRESSURE_COUNTEREXAMPLE_a_star_GE_4_FOUND"
    return make_output(first, second, baseline, metrics, completed, sealed, verdict, best)


def make_output(first, second, baseline, metrics, completed, sealed, verdict, best=None):
    if best is None:
        best = {
            "max_a_star": int(baseline["max_a_star"]),
            "source": "R48G_BASELINE_CONTINUATION",
            "root_hash": EXPECTED_ROOT_HASH,
            "root_CLV": list(EXPECTED_ROOT_CLV),
            "pressure_records": baseline["pressure_records"],
            "selected_pivots": [int(s["var"]) for s in baseline["selected_path"]],
        }
    return {
        "gate": GATE,
        "verdict": verdict,
        "sealed_R48G_lineage": {
            "first_mutation_ordinal": 22,
            "first_mutated_original_hash": first["mutated_original_hash"],
            "second_mutation_targeted_ordinal": R48G_SECOND_ORDINAL,
            "second_mutated_original_hash": second["mutated_original_hash"],
            "reachable_root_hash": EXPECTED_ROOT_HASH,
            "reachable_root_CLV": list(EXPECTED_ROOT_CLV),
            "known_a3_state_hash": EXPECTED_A3_STATE_HASH,
            "known_a3_state_CLV": list(EXPECTED_A3_STATE_CLV),
        },
        "baseline_continuation": baseline,
        "metrics": metrics,
        "best_finite_pressure_if_no_threshold": best,
        "completed_third_mutation_roots_before_threshold": completed,
        "sealed_threshold_or_stronger_counterexample": sealed,
        "interpretation": {
            "explicit_a4_refutes_universal_constant_a_le_3": True,
            "explicit_a4_refutes_general_polynomial_a_route": False,
            "no_a4_within_budget_proves_constant_a3": False,
            "finite_pressure_growth_proves_unbounded_family": False,
            "no_sequence_enumeration": True,
            "no_predeclared_persistent_clause_cap": True,
        },
        "firewall": {
            "UNIVERSAL_CONSTANT_a_LE_3": "NOT_PROVED",
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
    s = d["sealed_threshold_or_stronger_counterexample"]
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "baseline": {
            "outcome": d["baseline_continuation"]["outcome"],
            "max_a_star": d["baseline_continuation"]["max_a_star"],
            "selected_pivots": [int(x["var"]) for x in d["baseline_continuation"]["selected_path"]],
            "pressure_records": d["baseline_continuation"]["pressure_records"],
            "terminal": d["baseline_continuation"].get("terminal"),
        },
        "metrics": d["metrics"],
        "best": d["best_finite_pressure_if_no_threshold"],
        "sealed": None if s is None else {
            "source": s["source"],
            "mutation": s["mutation"],
            "reachable_root": {"hash":s["reachable_root"]["hash"],"CLV":s["reachable_root"]["CLV"]},
            "outcome": s["result"]["outcome"],
            "max_a_star": s["result"]["max_a_star"],
            "selected_pivots": [int(x["var"]) for x in s["result"]["selected_path"]],
            "threshold_state": s["result"]["threshold_state"],
        },
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
