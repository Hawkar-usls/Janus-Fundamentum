from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47v_r47n_first_cap_preserving_projection_chain as r47v

GATE = "JANUS_TRUMP_R47X_CAP_PROJECTION_COVERAGE_ONE_SWAP_FALSIFIER"
R47K_RESULT = Path(__file__).resolve().parents[1] / "research" / "JANUS_TRUMP_R47K_EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_EXTENDED_NORMALIZATION_CLOSURE_RESULT_2026-09-03.json"
CENTER_ORIGINAL_HASH = "eb13be26c29c106cf172db0be435aaf852d1e1248fced151c5356791f70024da"
CENTER_FIXPOINT_HASH = "9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde"
MANDATORY_R47V_ROOT_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
MANDATORY_R47V_PIVOTS = [7, 11, 12]


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def formula_hash(formula):
    return r42.formula_hash(r33.canonical_formula(formula))


def validate_exact_3cnf(formula):
    f = r33.canonical_formula(formula)
    if not f:
        raise AssertionError("R47X_EMPTY_EXACT3_INPUT")
    for clause in f:
        if len(clause) != 3:
            raise AssertionError(("R47X_NOT_EXACT_3CNF", clause))
        if r33.is_tautology(clause):
            raise AssertionError(("R47X_TAUTOLOGY_IN_EXACT3_INPUT", clause))


def load_center_original():
    data = json.loads(R47K_RESULT.read_text())
    original = r33.canonical_formula(data["mutated_original"]["formula"])
    validate_exact_3cnf(original)
    if formula_hash(original) != CENTER_ORIGINAL_HASH:
        raise AssertionError(("R47X_CENTER_ORIGINAL_HASH_DRIFT", formula_hash(original)))
    reached = r47f.reachable_fixpoint(original)
    if reached is None:
        raise AssertionError("R47X_CENTER_REACHABILITY_DRIFT")
    fixpoint = r33.canonical_formula(reached["formula"])
    if formula_hash(fixpoint) != CENTER_FIXPOINT_HASH:
        raise AssertionError(("R47X_CENTER_FIXPOINT_HASH_DRIFT", formula_hash(fixpoint)))
    return original, reached, fixpoint


def frontier(center_original):
    p20 = [c for c in center_original if any(abs(l) == 20 for l in c)]
    p11 = [c for c in center_original if c not in p20 and any(abs(l) == 11 for l in c)]
    rest = [c for c in center_original if c not in p20 and c not in p11]
    for phase, sources in (
        ("CLAUSES_TOUCHING_RESCUE_ROOT_PIVOT_20", p20),
        ("CLAUSES_TOUCHING_EXPOSED_SA_BVE_PIVOT_11_NOT_ALREADY_IN_PHASE1", p11),
        ("REMAINING_CLAUSES", rest),
    ):
        for source in sources:
            for replacement in r47i.signed_same_support_variants(source):
                mutated = r47i.mutate_one_clause(center_original, source, replacement)
                yield phase, source, replacement, mutated


def lift_assignment(before_formula, candidate, assignment):
    assignment = dict(assignment)
    for event in reversed(candidate["normalization"]["reconstruction_events"]):
        if event["kind"] == "R33":
            assignment = r33.reconstruct_model(event["result"], assignment)
        elif event["kind"] == "SA_BVE":
            assignment = r42.reconstruct_sa_bve(event["record"], assignment)
        else:
            raise AssertionError(("R47X_UNKNOWN_RECONSTRUCTION_EVENT", event["kind"]))
    assignment = r42.reconstruct_sa_bve(candidate["DP"], assignment)
    for v in sorted(set(r33.variables(before_formula)) - set(assignment)):
        assignment[v] = False
    if not r33.eval_formula(r33.canonical_formula(before_formula), assignment):
        raise AssertionError(("R47X_STEP_MODEL_RECONSTRUCTION_FAIL", candidate["var"]))
    return assignment


def compact_candidate(current, candidate, C0, V0, cap_accepted, replay_pass=None):
    final_formula = r33.canonical_formula(candidate["normalization"]["final_formula"])
    fclv = clv(final_formula)
    root_literal_cap = C0 * V0
    return {
        "var": int(candidate["var"]),
        "input_CLV": list(clv(current)),
        "forced_DP_CLV": list(candidate["DP"]["measure_after_forced_DP"]),
        "final_hash": formula_hash(final_formula),
        "final_CLV": list(fclv),
        "terminal": candidate["normalization"]["terminal"],
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "cap_accepted": bool(cap_accepted),
        "clause_cap_pass": bool(fclv[0] <= C0),
        "literal_cap_pass": bool(fclv[1] <= root_literal_cap),
        "variable_rank_strict": bool(fclv[2] < clv(current)[2]),
        "selected_pivot_absent_after": bool(int(candidate["var"]) not in set(r33.variables(final_formula))),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "full_R47M_independent_replay_pass": replay_pass,
        "normalization_segment_count": int(candidate["normalization"]["segment_count"]),
        "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
        "producer_net_CLV_descent": bool(candidate["net_CLV_descent"]),
    }


def run_cap_chain(root_formula):
    root = r33.canonical_formula(root_formula)
    C0, _, V0 = clv(root)
    root_vars = set(r33.variables(root))
    literal_cap = C0 * max(1, V0)
    max_steps = V0
    max_probes = V0 * V0
    current = root
    selected_full = []
    selected_rows = []
    probes = 0
    rejected = 0
    max_forced = [0, 0, 0]
    max_normalized = list(clv(root))

    while True:
        current_clv = clv(current)
        if current_clv[0] > C0:
            raise AssertionError(("R47X_CHAIN_ESCAPED_CLAUSE_CAP", current_clv, C0))
        if current_clv[1] > literal_cap:
            raise AssertionError(("R47X_CHAIN_ESCAPED_LITERAL_CAP", current_clv, literal_cap))
        if not set(r33.variables(current)).issubset(root_vars):
            raise AssertionError("R47X_CHAIN_FRESH_VARIABLE")

        selected = None
        selected_replay = None
        selected_row = None
        rejected_here = []
        for var in r33.variables(current):
            probes += 1
            if probes > max_probes:
                raise AssertionError(("R47X_PER_ROOT_PROBE_BOUND_EXCEEDED", probes, max_probes))
            candidate = r47m.macro_candidate_full_closure(current, int(var))
            if candidate is None:
                rejected += 1
                rejected_here.append({"var": int(var), "candidate": False, "cap_accepted": False})
                continue
            if not candidate["DP_independent_replay_pass"] or not candidate["polynomial_intermediate_envelope_pass"]:
                raise AssertionError(("R47X_CANDIDATE_CERTIFICATION_FAIL", var))

            forced = list(candidate["DP"]["measure_after_forced_DP"])
            max_forced = [max(max_forced[i], int(forced[i])) for i in range(3)]
            final_formula = r33.canonical_formula(candidate["normalization"]["final_formula"])
            final_clv = clv(final_formula)
            final_vars = set(r33.variables(final_formula))
            terminal = candidate["normalization"]["terminal"] is not None
            cap_accepted = terminal or (
                final_clv[0] <= C0
                and final_clv[2] < current_clv[2]
                and final_vars.issubset(root_vars)
            )
            if cap_accepted:
                replay = r47m.independent_replay(current, candidate)
                if not replay["pass"]:
                    raise AssertionError(("R47X_SELECTED_FULL_REPLAY_FAIL", var, replay))
                row = compact_candidate(current, candidate, C0, V0, True, True)
                if not terminal:
                    if not row["clause_cap_pass"] or not row["literal_cap_pass"]:
                        raise AssertionError(("R47X_SELECTED_CAP_INTEGRITY_FAIL", row))
                    if not row["variable_rank_strict"] or not row["selected_pivot_absent_after"]:
                        raise AssertionError(("R47X_SELECTED_RANK_INTEGRITY_FAIL", row))
                selected = candidate
                selected_replay = replay
                selected_row = row
                break
            rejected += 1
            rejected_here.append(compact_candidate(current, candidate, C0, V0, False, None))

        if selected is None:
            return {
                "covered": False,
                "root_hash": formula_hash(root),
                "root_CLV": list(clv(root)),
                "C0": C0,
                "V0": V0,
                "literal_cap": literal_cap,
                "selected_steps": selected_rows,
                "candidate_probe_count": probes,
                "rejected_probe_count": rejected,
                "max_forced_DP_CLV_coordinatewise": max_forced,
                "max_normalized_CLV_coordinatewise": max_normalized,
                "obstruction": {
                    "state_hash": formula_hash(current),
                    "state_CLV": list(clv(current)),
                    "state_formula": [list(c) for c in current],
                    "candidate_receipts": rejected_here,
                },
            }

        final_formula = r33.canonical_formula(selected["normalization"]["final_formula"])
        final_clv = clv(final_formula)
        max_normalized = [max(max_normalized[i], int(final_clv[i])) for i in range(3)]
        selected_rows.append({
            "step": len(selected_rows) + 1,
            "rejected_before_selection": len(rejected_here),
            **selected_row,
        })
        selected_full.append((current, selected, selected_replay))

        terminal_kind = selected["normalization"]["terminal"]
        semantic_sat = selected["normalization"]["semantic_sat"]
        if terminal_kind is not None:
            sat_reconstruction = {"applicable": False, "pass": True}
            if semantic_sat is True:
                assignment = dict(selected["normalization"]["terminal_assignment"] or {})
                for before_formula, cand, _ in reversed(selected_full):
                    assignment = lift_assignment(before_formula, cand, assignment)
                for v in sorted(root_vars - set(assignment)):
                    assignment[v] = False
                if not r33.eval_formula(root, assignment):
                    raise AssertionError("R47X_ROOT_MODEL_RECONSTRUCTION_FAIL")
                sat_reconstruction = {
                    "applicable": True,
                    "pass": True,
                    "assignment": {str(k): bool(v) for k, v in sorted(assignment.items())},
                }
            return {
                "covered": True,
                "root_hash": formula_hash(root),
                "root_CLV": list(clv(root)),
                "C0": C0,
                "V0": V0,
                "literal_cap": literal_cap,
                "selected_steps": selected_rows,
                "candidate_probe_count": probes,
                "rejected_probe_count": rejected,
                "max_forced_DP_CLV_coordinatewise": max_forced,
                "max_normalized_CLV_coordinatewise": max_normalized,
                "terminal": {
                    "kind": terminal_kind,
                    "semantic_sat": semantic_sat,
                    "final_hash": formula_hash(final_formula),
                    "final_CLV": list(final_clv),
                },
                "SAT_root_reconstruction": sat_reconstruction,
                "obstruction": None,
            }

        if len(selected_rows) > max_steps:
            raise AssertionError(("R47X_PER_ROOT_STEP_BOUND_EXCEEDED", len(selected_rows), max_steps))
        current = final_formula


def compact_chain(chain):
    return {
        "covered": bool(chain["covered"]),
        "root_hash": chain["root_hash"],
        "root_CLV": chain["root_CLV"],
        "C0": int(chain["C0"]),
        "V0": int(chain["V0"]),
        "selected_step_count": len(chain["selected_steps"]),
        "candidate_probe_count": int(chain["candidate_probe_count"]),
        "rejected_probe_count": int(chain["rejected_probe_count"]),
        "selected_pivots": [int(r["var"]) for r in chain["selected_steps"]],
        "terminal": chain.get("terminal"),
        "obstruction_summary": None if chain.get("obstruction") is None else {
            "state_hash": chain["obstruction"]["state_hash"],
            "state_CLV": chain["obstruction"]["state_CLV"],
            "candidate_count": len(chain["obstruction"]["candidate_receipts"]),
        },
    }


def run():
    mandatory = r47v.run()
    mandatory_pivots = [int(r["var"]) for r in mandatory["selected_steps"]]
    if mandatory["sealed_root"]["hash"] != MANDATORY_R47V_ROOT_HASH:
        raise AssertionError("R47X_MANDATORY_ROOT_DRIFT")
    if mandatory["verdict"] != "R47N_REACHES_CERTIFIED_TERMINAL_UNDER_FIRST_CAP_PRESERVING_PROJECTION_CHAIN__FINITE_ONLY":
        raise AssertionError(("R47X_MANDATORY_VERDICT_DRIFT", mandatory["verdict"]))
    if mandatory_pivots != MANDATORY_R47V_PIVOTS:
        raise AssertionError(("R47X_MANDATORY_PIVOT_DRIFT", mandatory_pivots))

    center_original, center_reached, center_fixpoint = load_center_original()
    center_chain = run_cap_chain(center_fixpoint)
    if not center_chain["covered"]:
        raise AssertionError("R47X_CENTER_REGRESSION_BECAME_CAP_OBSTRUCTION")

    metrics = {
        "frontier_positions": 0,
        "mutants_generated": 0,
        "duplicate_mutations_skipped": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "unique_fixpoints": 0,
        "cap_chain_covered": 0,
        "cap_chain_obstructions": 0,
        "total_chain_selected_steps": 0,
        "total_chain_candidate_probes": 0,
        "phase": {},
    }
    seen_fixpoints = {formula_hash(center_fixpoint)}
    first_counterexample = None
    hardest_covered = None

    for ordinal, (phase, source, replacement, mutated) in enumerate(frontier(center_original), 1):
        metrics["frontier_positions"] += 1
        pm = metrics["phase"].setdefault(phase, {
            "frontier_positions": 0,
            "mutants_generated": 0,
            "reachable_fixpoints": 0,
            "unique_fixpoints": 0,
            "cap_chain_covered": 0,
            "cap_chain_obstructions": 0,
        })
        pm["frontier_positions"] += 1
        if mutated is None:
            metrics["duplicate_mutations_skipped"] += 1
            continue
        validate_exact_3cnf(mutated)
        metrics["mutants_generated"] += 1
        pm["mutants_generated"] += 1

        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        pm["reachable_fixpoints"] += 1
        fixpoint = r33.canonical_formula(reached["formula"])
        fh = formula_hash(fixpoint)
        if fh in seen_fixpoints:
            continue
        seen_fixpoints.add(fh)
        metrics["unique_fixpoints"] += 1
        pm["unique_fixpoints"] += 1

        chain = run_cap_chain(fixpoint)
        metrics["total_chain_selected_steps"] += len(chain["selected_steps"])
        metrics["total_chain_candidate_probes"] += int(chain["candidate_probe_count"])
        record = {
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original_hash": formula_hash(mutated),
            "mutated_original_CLV": list(clv(mutated)),
            "fixpoint_hash": fh,
            "fixpoint_CLV": list(clv(fixpoint)),
            "chain": compact_chain(chain),
        }

        if not chain["covered"]:
            metrics["cap_chain_obstructions"] += 1
            pm["cap_chain_obstructions"] += 1
            record["mutated_original_formula"] = [list(c) for c in mutated]
            record["reachability_trajectory"] = reached["trajectory"]
            record["fixpoint_formula"] = [list(c) for c in fixpoint]
            record["full_chain"] = chain
            first_counterexample = record
            break

        metrics["cap_chain_covered"] += 1
        pm["cap_chain_covered"] += 1
        hardness = (
            int(chain["candidate_probe_count"]),
            len(chain["selected_steps"]),
            int(chain["V0"]),
            fh,
        )
        if hardest_covered is None or hardness > hardest_covered[0]:
            hardest_covered = (hardness, record)

    verdict = (
        "EXPLICIT_REACHABLE_CAP_PROJECTION_COVERAGE_COUNTEREXAMPLE_FOUND"
        if first_counterexample is not None
        else "NO_CAP_PROJECTION_COUNTEREXAMPLE_IN_FROZEN_ONE_SWAP_FRONTIER__UNIVERSAL_COVERAGE_STILL_OPEN"
    )

    return {
        "gate": GATE,
        "verdict": verdict,
        "mandatory_R47V_regression": {
            "root_hash": MANDATORY_R47V_ROOT_HASH,
            "selected_pivots": mandatory_pivots,
            "selected_step_count": len(mandatory["selected_steps"]),
            "candidate_probe_count": mandatory["metrics"]["candidate_probe_count"],
            "SAT_root_reconstruction_pass": mandatory["SAT_root_reconstruction"]["pass"],
        },
        "center_regression": compact_chain(center_chain),
        "metrics": metrics,
        "first_counterexample": first_counterexample,
        "hardest_covered": None if hardest_covered is None else hardest_covered[1],
        "interpretation": {
            "finite_falsification_frontier_only": True,
            "finite_no_counterexample_is_universal_theorem": False,
            "counterexample_if_found_refutes_cap_projection_coverage_for_frozen_grammar": True,
            "sequence_enumeration_used": False,
        },
        "firewall": {
            "CAP_PROJECTION_COVERAGE": "OPEN",
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
    result = run()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact = {
        "gate": result["gate"],
        "verdict": result["verdict"],
        "mandatory_R47V_regression": result["mandatory_R47V_regression"],
        "center_regression": result["center_regression"],
        "metrics": result["metrics"],
        "counterexample_summary": None if result["first_counterexample"] is None else {
            "frontier_ordinal": result["first_counterexample"]["frontier_ordinal"],
            "phase": result["first_counterexample"]["phase"],
            "source_clause": result["first_counterexample"]["source_clause"],
            "replacement_clause": result["first_counterexample"]["replacement_clause"],
            "mutated_original_hash": result["first_counterexample"]["mutated_original_hash"],
            "fixpoint_hash": result["first_counterexample"]["fixpoint_hash"],
            "fixpoint_CLV": result["first_counterexample"]["fixpoint_CLV"],
            "chain": result["first_counterexample"]["chain"],
        },
        "hardest_covered": result["hardest_covered"],
        "firewall": result["firewall"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
