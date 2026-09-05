from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g23_direct5_skeleton_r47j_collapse_cascade_anti_collapse_debt as r50g23

GATE = "JANUS_TRUMP_R50G24_PAIRWISE_COUNTERPOLARITY_CLOSURE_REPLAY"
EXPECTED_FROZEN_SKELETONS = 30
EXPECTED_FIRST_CLAUSE_CANDIDATES = 360
EXPECTED_FIRST_BREAKS = 122
EXPECTED_PAIR_TRIALS = 1774
EXPECTED_FIRST_REPLACEMENTS = {
    "R33:BOUNDED_VARIABLE_ELIMINATION": 34,
    "R33:BLOCKED_CLAUSE_ELIMINATION": 88,
}
EXPECTED_FINAL_FIRST = {
    "R33:BOUNDED_VARIABLE_ELIMINATION": 786,
    "R33:BLOCKED_CLAUSE_ELIMINATION": 887,
    "R33:PURE_LITERAL_AUTARKY": 94,
    "R33:UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE": 7,
}


def canon(formula):
    return r50g23.canon(formula)


def formula_variables(formula):
    return sorted({abs(int(lit)) for clause in formula for lit in clause})


def is_bipolar(formula):
    signs = {}
    for clause in formula:
        for raw in clause:
            lit = int(raw)
            signs.setdefault(abs(lit), set()).add(1 if lit > 0 else -1)
    return bool(signs) and all(v == {-1, 1} for v in signs.values())


def first_label(reduced):
    history = reduced.get("history", [])
    if history:
        return "R33:" + str(history[0]["rule"])
    return "R33_TERMINAL:" + str(reduced.get("terminal"))


def first_debt(reduced):
    history = reduced.get("history", [])
    if not history:
        return None
    compact = r50g23.compact_r33_record(history[0])
    try:
        return r50g23.direct_blocking_debt({"phase": "R33", "record": compact})
    except Exception:
        return None


def required_literals(debt):
    if not debt:
        return []
    if debt.get("required_literal") is not None:
        return [int(debt["required_literal"])]
    vals = debt.get("allowed_required_literals")
    if isinstance(vals, list):
        return [int(x) for x in vals]
    return []


def binary_clauses(req_lits, variables):
    out = set()
    for req in req_lits:
        for var in variables:
            if var == abs(req):
                continue
            for partner in (var, -var):
                if partner == -req:
                    continue
                clause = tuple(sorted((int(req), int(partner))))
                if clause[0] == -clause[1]:
                    continue
                out.add(clause)
    return sorted(out)


def replay_state(source, additions):
    r33 = r50g23.r33
    r47j = r50g23.r47j
    pivot = int(r50g23.PIVOT)
    mutated = canon(list(source) + list(additions))
    candidate = r47j.macro_candidate_fixpoint(mutated, pivot)
    if candidate is None:
        return {"ok": False, "reason": "R47J_CANDIDATE_MISSING"}
    replay = r47j.independent_fixpoint_macro_replay(mutated, candidate)
    if not replay.get("pass"):
        return {"ok": False, "reason": "R47J_REPLAY_FAIL", "replay": replay}
    forced = canon(candidate["DP"]["transformed"])
    reduced = r33.simplify(forced)
    final_formula = canon(reduced["final_formula"])
    return {
        "ok": True,
        "mutated": mutated,
        "candidate": candidate,
        "forced": forced,
        "reduced": reduced,
        "final": final_formula,
        "first_label": first_label(reduced),
        "debt": first_debt(reduced),
    }


def run():
    r33 = r50g23.r33
    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    if len(skeletons) != EXPECTED_FROZEN_SKELETONS:
        raise AssertionError(("R50G24_FROZEN_30_DRIFT", len(skeletons)))

    first_clause_candidates = 0
    first_breaks = 0
    second_debt_available = 0
    pair_trials = 0
    first_replacement = Counter()
    second_debt_partition = Counter()
    final_first = Counter()
    failed_replay = Counter()
    terminal_partition = Counter()
    strong = []
    near = []

    for item in skeletons:
        source = canon(item["source"])
        vars_ = formula_variables(source)
        base = r50g23.audit_one_skeleton(item)
        base_label = str(base["transition_labels"][0])
        base_debt = base["first_transition_direct_blocking_debt"]

        for c1 in binary_clauses(required_literals(base_debt), vars_):
            if c1 in source:
                continue
            first_clause_candidates += 1
            s1 = replay_state(source, [c1])
            if not s1["ok"]:
                failed_replay[str(s1["reason"])] += 1
                continue
            if s1["first_label"] == base_label:
                continue

            first_breaks += 1
            first_replacement[s1["first_label"]] += 1
            debt2 = s1.get("debt")
            req2 = required_literals(debt2)
            if not req2:
                second_debt_partition["NO_DIRECT_ADDITIVE_DEBT"] += 1
                continue
            second_debt_available += 1
            second_debt_partition[str(debt2.get("debt_class", "UNKNOWN"))] += 1

            for c2 in binary_clauses(req2, vars_):
                if c2 == c1 or c2 in source:
                    continue
                pair_trials += 1
                s2 = replay_state(source, [c1, c2])
                if not s2["ok"]:
                    failed_replay[str(s2["reason"])] += 1
                    continue

                reduced = s2["reduced"]
                final_formula = s2["final"]
                final_first[s2["first_label"]] += 1
                terminal_partition[str(reduced.get("terminal"))] += 1
                stalled = reduced.get("terminal") == "STALLED_STACK_LEAN_CORE" and bool(final_formula)
                bipolar = is_bipolar(final_formula) if final_formula else False
                row = {
                    "spec": item["spec"],
                    "source_hash": item["source_hash"],
                    "base_first_transition": base_label,
                    "first_clause": list(c1),
                    "first_clause_replacement_transition": s1["first_label"],
                    "first_clause_replacement_debt": debt2,
                    "second_clause": list(c2),
                    "pair_first_transition": s2["first_label"],
                    "mutated_source_CLV": list(r33.measure(s2["mutated"])),
                    "forced_DP_CLV": list(r33.measure(s2["forced"])),
                    "R33_terminal": reduced.get("terminal"),
                    "R33_transition_labels": ["R33:" + str(x["rule"]) for x in reduced.get("history", [])],
                    "R33_final_CLV": list(r33.measure(final_formula)),
                    "R33_final_formula": [list(c) for c in final_formula],
                    "nonempty_stalled_residual": stalled,
                    "bipolar_residual": bipolar,
                    "R47J_independent_replay_pass": True,
                    "full_R47J_terminal": s2["candidate"]["normalization"].get("terminal"),
                    "full_R47J_round_count": int(s2["candidate"]["normalization"].get("round_count", 0)),
                    "full_R47J_restart_count": int(s2["candidate"]["normalization"].get("restart_count", 0)),
                }
                if stalled and bipolar:
                    strong.append(row)
                elif len(near) < 20 and s2["first_label"] != s1["first_label"]:
                    near.append(row)

    observed_first_replacement = dict(sorted(first_replacement.items()))
    observed_final_first = dict(sorted(final_first.items()))

    if first_clause_candidates != EXPECTED_FIRST_CLAUSE_CANDIDATES:
        raise AssertionError(("R50G24_FIRST_CLAUSE_COUNT_DRIFT", first_clause_candidates))
    if first_breaks != EXPECTED_FIRST_BREAKS:
        raise AssertionError(("R50G24_FIRST_BREAK_COUNT_DRIFT", first_breaks))
    if pair_trials != EXPECTED_PAIR_TRIALS:
        raise AssertionError(("R50G24_PAIR_TRIAL_COUNT_DRIFT", pair_trials))
    if observed_first_replacement != dict(sorted(EXPECTED_FIRST_REPLACEMENTS.items())):
        raise AssertionError(("R50G24_FIRST_REPLACEMENT_PARTITION_DRIFT", observed_first_replacement))
    if observed_final_first != dict(sorted(EXPECTED_FINAL_FIRST.items())):
        raise AssertionError(("R50G24_FINAL_FIRST_PARTITION_DRIFT", observed_final_first))
    if failed_replay:
        raise AssertionError(("R50G24_REPLAY_FAILURE_DRIFT", dict(failed_replay)))
    if strong:
        raise AssertionError(("R50G24_UNEXPECTED_STRONG_SURVIVOR", strong[:2]))

    dominant_two = final_first["R33:BLOCKED_CLAUSE_ELIMINATION"] + final_first["R33:BOUNDED_VARIABLE_ELIMINATION"]
    verdict = "PAIRWISE_BINARY_COUNTERPOLARITY_FINITE_NEGATIVE__BCE_BVE_REPLACEMENT_CYCLE_DOMINATES__R50G25_STRUCTURAL_DEBT_OPEN"

    return {
        "gate": GATE,
        "source_gate": r50g23.GATE,
        "frozen_skeleton_count": len(skeletons),
        "no_source_family_expansion": True,
        "same_pivot_R47J": int(r50g23.PIVOT),
        "new_variables_added": False,
        "mutation_grammar": "TWO_ADDITIVE_BINARY_CLAUSES_OVER_EXISTING_VARIABLES_ONLY",
        "first_clause_candidate_count": first_clause_candidates,
        "first_transition_break_count": first_breaks,
        "second_direct_debt_available_count": second_debt_available,
        "pair_trial_count": pair_trials,
        "first_replacement_partition": observed_first_replacement,
        "second_debt_partition": dict(sorted(second_debt_partition.items())),
        "final_first_transition_partition": observed_final_first,
        "R47J_replay_failure_partition": dict(sorted(failed_replay.items())),
        "R33_terminal_partition": dict(sorted(terminal_partition.items())),
        "strong_candidate_count": len(strong),
        "strong_candidates": strong,
        "near_misses": near,
        "BCE_plus_BVE_final_first_count": dominant_two,
        "BCE_plus_BVE_final_first_fraction": dominant_two / pair_trials,
        "next_gate": "R50G25_BCE_BVE_REPLACEMENT_CYCLE_STRUCTURAL_DEBT",
        "verdict": verdict,
        "firewall": {
            "FINITE_PAIRWISE_NEGATIVE_IMPLIES_ALL_PAIRWISE_MUTATIONS_FAIL": False,
            "FINITE_PAIRWISE_NEGATIVE_IMPLIES_UNIVERSAL_ALL_DIRECT5": False,
            "BCE_BVE_DOMINANCE_IS_A_THEOREM_OUTSIDE_THIS_REPLAY": False,
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
