from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x

GATE = "JANUS_TRUMP_R48A_FIXED_POLYNOMIAL_ENVELOPE_PRESSURE_FRONTIER"
MANDATORY_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
MANDATORY_DELTA = 4
MANDATORY_B = 79
MANDATORY_PIVOTS = [2, 7, 9, 5]


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def h(formula):
    return r47f.formula_hash(canon(formula))


def run_chain(root_formula, B):
    root = canon(root_formula)
    C0, _, V0 = clv(root)
    root_vars = set(r33.variables(root))
    literal_envelope = B * max(1, V0)
    current = root
    selected_full = []
    selected_rows = []
    probes = 0
    rejected = 0
    max_persisted_clause_debt = 0
    max_forced_clause_count = C0

    while True:
        cur = clv(current)
        if cur[0] > B or cur[1] > literal_envelope:
            raise AssertionError(("R48A_PERSISTED_ENVELOPE_ESCAPE", h(root), B, cur))
        if not set(r33.variables(current)).issubset(root_vars):
            raise AssertionError(("R48A_FRESH_VARIABLE", h(root), h(current)))
        max_persisted_clause_debt = max(max_persisted_clause_debt, cur[0] - C0)

        selected = None
        selected_replay = None
        rejected_here = []
        for var in r33.variables(current):
            probes += 1
            if probes > V0 * V0:
                raise AssertionError(("R48A_PROBE_CAP_EXCEEDED", h(root), probes, V0 * V0))
            cand = r47m.macro_candidate_full_closure(current, int(var))
            if cand is None:
                rejected += 1
                rejected_here.append({"var": int(var), "candidate": False})
                continue
            if not cand["DP_independent_replay_pass"]:
                raise AssertionError(("R48A_DP_REPLAY_FAIL", h(root), var))
            if not cand["polynomial_intermediate_envelope_pass"]:
                raise AssertionError(("R48A_POLYNOMIAL_INTERMEDIATE_FAIL", h(root), var))

            forced_clv = tuple(cand["DP"]["measure_after_forced_DP"])
            max_forced_clause_count = max(max_forced_clause_count, forced_clv[0])
            final_formula = canon(cand["normalization"]["final_formula"])
            final_clv = clv(final_formula)
            final_vars = set(r33.variables(final_formula))
            terminal = cand["normalization"]["terminal"] is not None
            accepted = terminal or (
                final_clv[0] <= B
                and final_clv[1] <= literal_envelope
                and final_clv[2] < cur[2]
                and final_vars.issubset(root_vars)
            )
            if not accepted:
                rejected += 1
                rejected_here.append({
                    "var": int(var),
                    "candidate": True,
                    "forced_DP_CLV": list(forced_clv),
                    "final_CLV": list(final_clv),
                    "final_clause_overflow": max(0, final_clv[0] - B),
                })
                continue

            replay = r47m.independent_replay(current, cand)
            if not replay["pass"]:
                raise AssertionError(("R48A_SELECTED_FULL_REPLAY_FAIL", h(root), var, replay))
            selected = cand
            selected_replay = replay
            selected_rows.append({
                "step": len(selected_rows) + 1,
                "var": int(var),
                "input_CLV": list(cur),
                "forced_DP_CLV": list(forced_clv),
                "final_CLV": list(final_clv),
                "terminal": cand["normalization"]["terminal"],
                "semantic_sat": cand["normalization"]["semantic_sat"],
                "rejected_before_selection": len(rejected_here),
                "transient_clause_over_B": max(0, forced_clv[0] - B),
                "persisted_clause_debt_over_C0": max(0, final_clv[0] - C0),
                "SA_BVE_application_count": int(cand["normalization"]["SA_BVE_application_count"]),
                "full_R47M_independent_replay_pass": True,
            })
            selected_full.append((current, cand, selected_replay))
            current = final_formula
            break

        if selected is None:
            rich = [r for r in rejected_here if r.get("candidate")]
            best = None if not rich else min(
                rich,
                key=lambda r: (r["final_clause_overflow"], r["final_CLV"][0], r["final_CLV"][1], r["var"]),
            )
            return {
                "covered": False,
                "root_hash": h(root),
                "root_CLV": list(clv(root)),
                "B": int(B),
                "delta": int(B - C0),
                "selected_steps": selected_rows,
                "candidate_probe_count": probes,
                "rejected_probe_count": rejected,
                "maximum_persisted_clause_debt_over_C0": max_persisted_clause_debt,
                "maximum_forced_clause_count": max_forced_clause_count,
                "obstruction": {
                    "state_hash": h(current),
                    "state_CLV": list(clv(current)),
                    "candidate_count": len(rejected_here),
                    "best_rejected": best,
                },
            }

        terminal = selected["normalization"]["terminal"]
        if terminal is not None:
            semantic_sat = selected["normalization"]["semantic_sat"]
            sat_reconstruction = {"applicable": False, "pass": True}
            if semantic_sat is True:
                assignment = dict(selected["normalization"]["terminal_assignment"] or {})
                for before_formula, cand, _ in reversed(selected_full):
                    assignment = r47x.lift_assignment(before_formula, cand, assignment)
                for v in sorted(root_vars - set(assignment)):
                    assignment[v] = False
                if not r33.eval_formula(root, assignment):
                    raise AssertionError(("R48A_ROOT_MODEL_RECONSTRUCTION_FAIL", h(root)))
                sat_reconstruction = {"applicable": True, "pass": True}
            return {
                "covered": True,
                "root_hash": h(root),
                "root_CLV": list(clv(root)),
                "B": int(B),
                "delta": int(B - C0),
                "selected_steps": selected_rows,
                "candidate_probe_count": probes,
                "rejected_probe_count": rejected,
                "maximum_persisted_clause_debt_over_C0": max(
                    max_persisted_clause_debt,
                    max((r["persisted_clause_debt_over_C0"] for r in selected_rows), default=0),
                ),
                "maximum_forced_clause_count": max_forced_clause_count,
                "terminal": {
                    "kind": terminal,
                    "semantic_sat": semantic_sat,
                    "final_hash": h(current),
                    "final_CLV": list(clv(current)),
                },
                "SAT_root_reconstruction": sat_reconstruction,
                "obstruction": None,
            }

        if len(selected_rows) > V0:
            raise AssertionError(("R48A_STEP_CAP_EXCEEDED", h(root), len(selected_rows), V0))


def compact_chain(row):
    return {
        "covered": row["covered"],
        "B": row["B"],
        "delta": row["delta"],
        "selected_pivots": [int(s["var"]) for s in row["selected_steps"]],
        "selected_step_count": len(row["selected_steps"]),
        "candidate_probe_count": row["candidate_probe_count"],
        "rejected_probe_count": row["rejected_probe_count"],
        "maximum_persisted_clause_debt_over_C0": row["maximum_persisted_clause_debt_over_C0"],
        "maximum_forced_clause_count": row["maximum_forced_clause_count"],
        "terminal": row.get("terminal"),
        "obstruction": row.get("obstruction"),
    }


def characterize_root(root_formula):
    root = canon(root_formula)
    C0, _, V0 = clv(root)
    minimum = None
    minimum_full = None
    ladder = []
    for delta in range(V0 + 1):
        row = run_chain(root, C0 + delta)
        ladder.append(compact_chain(row))
        if row["covered"]:
            minimum = delta
            minimum_full = row
            break

    B_star = C0 + V0
    if minimum == V0:
        star = minimum_full
    else:
        star = run_chain(root, B_star)

    return {
        "root_hash": h(root),
        "root_CLV": list(clv(root)),
        "C0": C0,
        "V0": V0,
        "minimum_delta": minimum,
        "minimum_B": None if minimum is None else C0 + minimum,
        "minimum_delta_over_V0": None if minimum is None or V0 == 0 else minimum / V0,
        "minimum_chain": None if minimum_full is None else compact_chain(minimum_full),
        "delta_ladder": ladder,
        "B_star": B_star,
        "B_star_chain": compact_chain(star),
    }


def run():
    center_original, _, center_fixpoint = r47x.load_center_original()
    roots = [{
        "kind": "CENTER_CONTROL",
        "frontier_ordinal": 0,
        "phase": "CENTER_CONTROL",
        "source_clause": None,
        "replacement_clause": None,
        "formula": center_fixpoint,
    }]
    seen = {h(center_fixpoint)}
    generated = 0
    reachable = 0

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if mutated is None:
            continue
        generated += 1
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            continue
        reachable += 1
        root = canon(reached["formula"])
        rh = h(root)
        if rh in seen:
            continue
        seen.add(rh)
        roots.append({
            "kind": "ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": ordinal,
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original_hash": h(mutated),
            "formula": root,
        })

    results = []
    mandatory = None
    for meta in roots:
        char = characterize_root(meta["formula"])
        record = {k: v for k, v in meta.items() if k != "formula"}
        record.update(char)
        results.append(record)
        if char["root_hash"] == MANDATORY_HASH:
            mandatory = record

    if mandatory is None:
        raise AssertionError("R48A_MANDATORY_R47X_ROOT_NOT_FOUND")
    if mandatory["minimum_delta"] != MANDATORY_DELTA:
        raise AssertionError(("R48A_MANDATORY_MIN_DELTA_DRIFT", mandatory["minimum_delta"]))
    if mandatory["minimum_B"] != MANDATORY_B:
        raise AssertionError(("R48A_MANDATORY_MIN_B_DRIFT", mandatory["minimum_B"]))
    if mandatory["minimum_chain"]["selected_pivots"] != MANDATORY_PIVOTS:
        raise AssertionError(("R48A_MANDATORY_PIVOTS_DRIFT", mandatory["minimum_chain"]["selected_pivots"]))

    star_failures = [r for r in results if not r["B_star_chain"]["covered"]]
    no_min = [r for r in results if r["minimum_delta"] is None]
    finite_minima = [r["minimum_delta"] for r in results if r["minimum_delta"] is not None]
    hardest = None
    if finite_minima:
        hardest = max(
            (r for r in results if r["minimum_delta"] is not None),
            key=lambda r: (r["minimum_delta"], r["minimum_delta_over_V0"], r["minimum_chain"]["candidate_probe_count"], r["root_hash"]),
        )

    verdict = (
        "ALL_FROZEN_FRONTIER_ROOTS_COVERED_BY_B_C0_PLUS_V0__FINITE_ONLY"
        if not star_failures
        else "EXPLICIT_FRONTIER_ROOT_NOT_COVERED_BY_B_C0_PLUS_V0"
    )

    return {
        "gate": GATE,
        "verdict": verdict,
        "frontier_metrics": {
            "mutants_generated": generated,
            "reachable_mutants": reachable,
            "unique_roots_including_center": len(results),
            "roots_with_minimum_delta_le_V0": len(results) - len(no_min),
            "roots_without_rescue_delta_le_V0": len(no_min),
            "B_star_failures": len(star_failures),
            "maximum_minimum_delta": None if not finite_minima else max(finite_minima),
            "maximum_minimum_delta_over_V0": None if not finite_minima else max(r["minimum_delta_over_V0"] for r in results if r["minimum_delta_over_V0"] is not None),
        },
        "mandatory_R47Z_regression": {
            "root_hash": mandatory["root_hash"],
            "minimum_delta": mandatory["minimum_delta"],
            "minimum_B": mandatory["minimum_B"],
            "selected_pivots": mandatory["minimum_chain"]["selected_pivots"],
        },
        "hardest_finite_root": None if hardest is None else {
            "root_hash": hardest["root_hash"],
            "root_CLV": hardest["root_CLV"],
            "frontier_ordinal": hardest["frontier_ordinal"],
            "phase": hardest["phase"],
            "source_clause": hardest["source_clause"],
            "replacement_clause": hardest["replacement_clause"],
            "minimum_delta": hardest["minimum_delta"],
            "minimum_B": hardest["minimum_B"],
            "minimum_delta_over_V0": hardest["minimum_delta_over_V0"],
            "minimum_chain": hardest["minimum_chain"],
        },
        "B_star_failure_summaries": [{
            "root_hash": r["root_hash"],
            "root_CLV": r["root_CLV"],
            "frontier_ordinal": r["frontier_ordinal"],
            "phase": r["phase"],
            "source_clause": r["source_clause"],
            "replacement_clause": r["replacement_clause"],
            "B_star": r["B_star"],
            "obstruction": r["B_star_chain"]["obstruction"],
        } for r in star_failures],
        "roots": results,
        "interpretation": {
            "finite_frontier_only": True,
            "all_roots_covered_proves_universal_B_C0_plus_V0": False,
            "explicit_B_star_failure_refutes_candidate_for_frozen_controller": bool(star_failures),
            "sequence_enumeration_used": False,
        },
        "firewall": {
            "B_C0_PLUS_V0_UNIVERSAL_COVERAGE": "OPEN",
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
    p = argparse.ArgumentParser()
    p.add_argument("--output")
    args = p.parse_args()
    d = run()
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact_roots = [{
        "root_hash": r["root_hash"],
        "root_CLV": r["root_CLV"],
        "frontier_ordinal": r["frontier_ordinal"],
        "minimum_delta": r["minimum_delta"],
        "minimum_B": r["minimum_B"],
        "B_star": r["B_star"],
        "B_star_covered": r["B_star_chain"]["covered"],
        "minimum_selected_pivots": None if r["minimum_chain"] is None else r["minimum_chain"]["selected_pivots"],
    } for r in d["roots"]]
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "frontier_metrics": d["frontier_metrics"],
        "mandatory_R47Z_regression": d["mandatory_R47Z_regression"],
        "hardest_finite_root": d["hardest_finite_root"],
        "B_star_failure_summaries": d["B_star_failure_summaries"],
        "roots": compact_roots,
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
