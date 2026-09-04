from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48d_minimum_local_amortized_pressure_controller as r48d
import janus_trump_r48g_targeted_unit_weight_pressure_counterexample_hunt as r48g

GATE = "JANUS_TRUMP_R48L_A_STAR_4_CONTINUATION_OR_TARGETED_ESCALATION"
TARGET_A_STAR = 4
R48G_SECOND_ORDINAL = 4
R48G_MUTATED_ORIGINAL_HASH = "720355b9542ddccc7bfe6ae1fcda35eb6879ad921aebb4a8b6f63998ecaadd0c"
R48G_ROOT_HASH = "3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
R48G_ROOT_CLV = (75, 199, 22)
R48G_ASTAR3_STATE_HASH = "9c06bfcfecbff7b79342a0c4113c77bba310e976ad1ac1b52120c887782d96ac"
R48G_ASTAR3_STATE_CLV = (78, 223, 18)
PRIMARY_VARS = frozenset((2, 7, 9, 11, 12, 16, 25, 26))
MAX_THIRD_MUTATED_ORIGINALS = 96


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def reconstruct_r48g_source():
    first = r48g.reconstruct_r47x_first_mutation()
    target = None
    for meta in r48g.targeted_second_mutations(first["mutated_original"]):
        if int(meta["targeted_ordinal"]) != R48G_SECOND_ORDINAL:
            continue
        if meta["mutated_original_hash"] != R48G_MUTATED_ORIGINAL_HASH:
            raise AssertionError(("R48L_MUTATED_ORIGINAL_HASH_DRIFT", meta["mutated_original_hash"]))
        reached = r47f.reachable_fixpoint(meta["mutated_original"])
        if reached is None:
            raise AssertionError("R48L_R48G_SOURCE_NO_REACHABLE_ROOT")
        root = canon(reached["formula"])
        if formula_hash(root) != R48G_ROOT_HASH or clv(root) != R48G_ROOT_CLV:
            raise AssertionError(("R48L_R48G_ROOT_DRIFT", formula_hash(root), clv(root)))
        target = {
            **meta,
            "reachable_root": root,
            "reachable_root_hash": formula_hash(root),
            "reachable_root_CLV": list(clv(root)),
            "reachability_trajectory": reached["trajectory"],
        }
        break
    if target is None:
        raise AssertionError("R48L_R48G_SECOND_ORDINAL_NOT_FOUND")
    return target


def compact_selected(current, chosen_row, candidate, state_a_star, step):
    return {
        "step": int(step),
        "state_hash": formula_hash(current),
        "state_CLV": list(clv(current)),
        "state_a_star": int(state_a_star),
        "var": int(chosen_row["var"]),
        "a_req": int(chosen_row.get("a_req") or 0),
        "forced_DP_CLV": chosen_row["forced_DP_CLV"],
        "final_CLV": chosen_row["final_CLV"],
        "terminal": chosen_row["terminal"],
        "semantic_sat": chosen_row["semantic_sat"],
        "full_R47M_independent_replay_pass": True,
    }


def replay_target_state(current, rows, candidates, expected_minimum):
    replayed = r48g.independently_replay_all(current, rows, candidates)
    eligible = [x for x in replayed if x.get("eligible", False)]
    terminals = [x for x in eligible if x.get("terminal") is not None]
    nonterm = [x for x in eligible if x.get("terminal") is None and x.get("a_req") is not None]
    if terminals:
        raise AssertionError("R48L_TARGET_REPLAY_FOUND_TERMINAL")
    if not nonterm:
        raise AssertionError("R48L_TARGET_REPLAY_LOST_NONTERMINAL_CANDIDATES")
    a_star = min(int(x["a_req"]) for x in nonterm)
    if a_star < int(expected_minimum):
        raise AssertionError(("R48L_TARGET_REPLAY_DROPPED", expected_minimum, a_star))
    return replayed, a_star


def continue_trajectory(root):
    root = canon(root)
    current = root
    V0 = clv(root)[2]
    selected_path = []
    total_probes = 0
    max_a_star = -1
    saw_r48g_astar3_state = False

    for state_index in range(V0 + 1):
        if state_index >= V0:
            raise AssertionError(("R48L_NONTERMINAL_STEP_CAP_EXHAUSTED", clv(current)))
        rows, candidates, eligible, terminals, nonterm, a_star = r48g.scan_state(current)
        total_probes += len(rows)
        if total_probes > V0 * V0:
            raise AssertionError(("R48L_PROBE_CAP_EXCEEDED", total_probes, V0 * V0))

        if formula_hash(current) == R48G_ASTAR3_STATE_HASH:
            if clv(current) != R48G_ASTAR3_STATE_CLV:
                raise AssertionError(("R48L_ASTAR3_STATE_CLV_DRIFT", clv(current)))
            saw_r48g_astar3_state = True

        if a_star is None:
            replayed = r48g.independently_replay_all(current, rows, candidates)
            replay_eligible = [x for x in replayed if x.get("eligible", False)]
            replay_terminals = [x for x in replay_eligible if x.get("terminal") is not None]
            if replay_terminals or replay_eligible:
                raise AssertionError("R48L_NO_CANDIDATE_REPLAY_DRIFT")
            return {
                "outcome": "NO_VARIABLE_DECREASING_CANDIDATE",
                "candidate_probe_count": total_probes,
                "max_a_star": max_a_star,
                "selected_path": selected_path,
                "saw_R48G_a_star_3_state": saw_r48g_astar3_state,
                "counterexample": {
                    "state_index": int(state_index),
                    "state_hash": formula_hash(current),
                    "state_CLV": list(clv(current)),
                    "state_formula": [list(c) for c in current],
                    "a_star": None,
                    "candidate_rows": replayed,
                },
            }

        max_a_star = max(max_a_star, int(a_star))
        if not terminals and int(a_star) >= TARGET_A_STAR:
            replayed, replay_a_star = replay_target_state(current, rows, candidates, TARGET_A_STAR)
            return {
                "outcome": "A_STAR_GE_4",
                "candidate_probe_count": total_probes,
                "max_a_star": max(max_a_star, replay_a_star),
                "selected_path": selected_path,
                "saw_R48G_a_star_3_state": saw_r48g_astar3_state,
                "counterexample": {
                    "state_index": int(state_index),
                    "state_hash": formula_hash(current),
                    "state_CLV": list(clv(current)),
                    "state_formula": [list(c) for c in current],
                    "a_star": int(replay_a_star),
                    "candidate_rows": replayed,
                },
            }

        if not eligible:
            raise AssertionError(("R48L_ASTAR_DEFINED_WITHOUT_ELIGIBLE", a_star))
        chosen_row = min(eligible, key=r48d.selection_key)
        chosen = candidates[int(chosen_row["var"])]
        replay = r48g.r47m.independent_replay(current, chosen)
        if not replay["pass"]:
            raise AssertionError(("R48L_SELECTED_REPLAY_FAIL", chosen_row["var"], replay))
        chosen_row = r48d.candidate_row(current, chosen, True)
        selected_path.append(compact_selected(current, chosen_row, chosen, a_star, len(selected_path) + 1))
        final_formula = canon(chosen["normalization"]["final_formula"])
        if chosen_row["terminal"] is not None:
            sat_reconstruction = r48g.lift_sat_root(root, [(root, chosen)] if len(selected_path) == 1 else [], chosen)
            # The full multi-step SAT lift is not needed for UNSAT/pressure claims here; candidate replay remains authoritative.
            return {
                "outcome": "TERMINAL_BEFORE_A_STAR_4",
                "candidate_probe_count": total_probes,
                "max_a_star": max_a_star,
                "selected_path": selected_path,
                "saw_R48G_a_star_3_state": saw_r48g_astar3_state,
                "terminal": {
                    "kind": chosen_row["terminal"],
                    "semantic_sat": chosen_row["semantic_sat"],
                    "final_hash": formula_hash(final_formula),
                    "final_CLV": list(clv(final_formula)),
                    "single_step_SAT_lift_if_applicable": sat_reconstruction if len(selected_path) == 1 else {"applicable": False, "pass": True},
                },
                "counterexample": None,
            }
        current = final_formula

    raise AssertionError("R48L_UNREACHABLE_CONTINUATION_EXIT")


def third_mutation_frontier(second_mutated_original):
    f = canon(second_mutated_original)
    primary = [c for c in f if any(abs(l) in PRIMARY_VARS for l in c)]
    remaining = [c for c in f if c not in primary]
    seen = set()
    ordinal = 0
    for phase, sources in (("PRESSURE_VARS", primary), ("REMAINING", remaining)):
        for source in sources:
            for replacement in r47i.signed_same_support_variants(source):
                mutated = r47i.mutate_one_clause(f, source, replacement)
                if mutated is None:
                    continue
                mutated = canon(mutated)
                r47x.validate_exact_3cnf(mutated)
                mh = formula_hash(mutated)
                if mh in seen:
                    continue
                seen.add(mh)
                ordinal += 1
                yield {
                    "targeted_ordinal": int(ordinal),
                    "phase": phase,
                    "source_clause": list(source),
                    "replacement_clause": list(replacement),
                    "mutated_original": mutated,
                    "mutated_original_hash": mh,
                }
                if ordinal >= MAX_THIRD_MUTATED_ORIGINALS:
                    return


def compact_root(meta, root, result):
    return {
        "targeted_ordinal": meta.get("targeted_ordinal"),
        "phase": meta.get("phase"),
        "source_clause": meta.get("source_clause"),
        "replacement_clause": meta.get("replacement_clause"),
        "mutated_original_hash": meta.get("mutated_original_hash"),
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "outcome": result["outcome"],
        "max_a_star": result["max_a_star"],
        "candidate_probe_count": result["candidate_probe_count"],
        "selected_pivots": [int(x["var"]) for x in result["selected_path"]],
        "selected_path": result["selected_path"],
        "saw_R48G_a_star_3_state": result["saw_R48G_a_star_3_state"],
        "terminal": result.get("terminal"),
    }


def run():
    source = reconstruct_r48g_source()
    baseline = continue_trajectory(source["reachable_root"])
    if baseline["outcome"] in ("A_STAR_GE_4", "NO_VARIABLE_DECREASING_CANDIDATE"):
        verdict = (
            "R48G_ROOT_CONTINUATION_REACHES_A_STAR_GE_4"
            if baseline["outcome"] == "A_STAR_GE_4"
            else "STRONGER_NO_VARIABLE_DECREASING_CANDIDATE_FOUND"
        )
        return {
            "gate": GATE,
            "verdict": verdict,
            "source": {k: v for k, v in source.items() if k not in ("mutated_original", "reachable_root")},
            "baseline_continuation": baseline,
            "targeted_metrics": None,
            "first_targeted_positive": None,
            "firewall": firewall(),
        }

    if baseline["outcome"] != "TERMINAL_BEFORE_A_STAR_4":
        raise AssertionError(("R48L_UNEXPECTED_BASELINE_OUTCOME", baseline["outcome"]))

    metrics = {
        "third_mutated_originals_generated": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "duplicate_reachable_fixpoints_skipped": 0,
        "unique_reachable_fixpoints_evaluated": 0,
        "total_candidate_probes": int(baseline["candidate_probe_count"]),
        "terminal_below_4": 0,
    }
    seen_roots = {R48G_ROOT_HASH}
    first_positive = None
    best_below4 = compact_root({"phase": "R48G_BASELINE"}, source["reachable_root"], baseline)

    for meta in third_mutation_frontier(source["mutated_original"]):
        metrics["third_mutated_originals_generated"] += 1
        reached = r47f.reachable_fixpoint(meta["mutated_original"])
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root = canon(reached["formula"])
        rh = formula_hash(root)
        if rh in seen_roots:
            metrics["duplicate_reachable_fixpoints_skipped"] += 1
            continue
        seen_roots.add(rh)
        metrics["unique_reachable_fixpoints_evaluated"] += 1
        result = continue_trajectory(root)
        metrics["total_candidate_probes"] += int(result["candidate_probe_count"])
        if result["outcome"] in ("A_STAR_GE_4", "NO_VARIABLE_DECREASING_CANDIDATE"):
            first_positive = {
                **compact_root(meta, root, result),
                "reachability_trajectory": reached["trajectory"],
                "mutated_original_formula": [list(c) for c in meta["mutated_original"]],
                "counterexample": result["counterexample"],
            }
            break
        metrics["terminal_below_4"] += 1
        record = compact_root(meta, root, result)
        if (int(record["max_a_star"]), int(record["candidate_probe_count"]), record["root_hash"]) > (
            int(best_below4["max_a_star"]), int(best_below4["candidate_probe_count"]), best_below4["root_hash"]
        ):
            best_below4 = record

    if first_positive is None:
        verdict = "NO_A_STAR_GE_4_WITHIN_FROZEN_SCOPE__FINITE_ONLY"
    elif first_positive["outcome"] == "NO_VARIABLE_DECREASING_CANDIDATE":
        verdict = "STRONGER_NO_VARIABLE_DECREASING_CANDIDATE_FOUND"
    else:
        verdict = "TARGETED_THIRD_MUTATION_REACHES_A_STAR_GE_4"

    return {
        "gate": GATE,
        "verdict": verdict,
        "source": {k: v for k, v in source.items() if k not in ("mutated_original", "reachable_root")},
        "baseline_continuation": baseline,
        "targeted_metrics": metrics,
        "first_targeted_positive": first_positive,
        "hardest_below_4_if_no_positive": best_below4,
        "firewall": firewall(),
    }


def firewall():
    return {
        "UNIVERSAL_FIXED_a_LE_2_COVERAGE": "REFUTED_BY_R48G",
        "UNIVERSAL_FIXED_a_LE_3_COVERAGE": "OPEN_UNLESS_R48L_FINDS_A_STAR_GE_4",
        "UNBOUNDED_PRESSURE": "NOT_PROVED",
        "UNIVERSAL_ROOT_POLYNOMIAL_PRESSURE_BOUND": "NOT_PROVED",
        "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
        "O4_UNIVERSAL_COVERAGE": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
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
    compact = {
        "gate": d["gate"],
        "verdict": d["verdict"],
        "baseline": {
            "outcome": d["baseline_continuation"]["outcome"],
            "max_a_star": d["baseline_continuation"]["max_a_star"],
            "selected_pivots": [x["var"] for x in d["baseline_continuation"]["selected_path"]],
            "counterexample": None if d["baseline_continuation"].get("counterexample") is None else {
                "state_hash": d["baseline_continuation"]["counterexample"]["state_hash"],
                "state_CLV": d["baseline_continuation"]["counterexample"]["state_CLV"],
                "a_star": d["baseline_continuation"]["counterexample"]["a_star"],
            },
        },
        "targeted_metrics": d.get("targeted_metrics"),
        "targeted_positive": None if d.get("first_targeted_positive") is None else {
            k: d["first_targeted_positive"].get(k)
            for k in ("targeted_ordinal", "phase", "source_clause", "replacement_clause", "mutated_original_hash", "root_hash", "root_CLV", "outcome", "max_a_star")
        },
        "firewall": d["firewall"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
