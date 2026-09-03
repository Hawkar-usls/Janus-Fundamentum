from __future__ import annotations

import itertools
import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f

BASE = {
    "n": 30,
    "ratio": 3.8,
    "attempt": 3,
    "seed": 473383,
    "original_hash": "31621a04517fa41a334187572001608dff9b338dc529d8a809b5ee95bccf9297",
    "original_CLV": [114, 342, 30],
    "fixpoint_hash": "3130377ee52a6d6abf01f44fdc5f1a96cf83d701e30f70debea26cd347b7a495",
    "fixpoint_CLV": [87, 233, 25],
    "selected_var": 7,
    "selected_final_CLV": [87, 233, 24],
}


def debt_row(before, candidate, replay_pass=None):
    input_clv = tuple(r33.measure(before))
    dp_clv = tuple(int(x) for x in candidate["DP"]["measure_after_forced_DP"])
    final_clv = tuple(int(x) for x in candidate["final_CLV"])
    d_c = dp_clv[0] - input_clv[0]
    d_l = dp_clv[1] - input_clv[1]
    r_c = dp_clv[0] - final_clv[0]
    r_l = dp_clv[1] - final_clv[1]
    if d_c > 0:
        debt_class = "CLAUSE_DEBT"
    elif d_c == 0 and d_l > 0:
        debt_class = "LITERAL_DEBT"
    else:
        debt_class = "DEBT_CONTRACT_VIOLATION"
    return {
        "var": int(candidate["var"]),
        "input_CLV": list(input_clv),
        "forced_DP_CLV": list(dp_clv),
        "debt_class": debt_class,
        "dC": d_c,
        "dL": d_l,
        "final_CLV": list(final_clv),
        "rC": r_c,
        "rL": r_l,
        "terminal": candidate["normalization"].get("terminal"),
        "accepted": bool(candidate["accepted"]),
        "net_CLV_descent": bool(candidate["net_CLV_descent"]),
        "temporary_internal_ascent": bool(candidate["temporary_internal_ascent"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay"]["pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope"]["pass"]),
        "independent_replay_pass": replay_pass,
    }


def first_accepted_with_debt(fixpoint):
    before = r33.canonical_formula(fixpoint)
    rows = []
    checked = 0
    for var in r33.variables(before):
        checked += 1
        candidate = r45a.macro_candidate_for_var(before, int(var))
        if candidate is None:
            rows.append({"var": int(var), "candidate": False, "accepted": False})
            continue
        if not candidate["DP_independent_replay"]["pass"]:
            raise AssertionError(("R47I_DP_REPLAY_FAIL", var))
        if not candidate["polynomial_intermediate_envelope"]["pass"]:
            raise AssertionError(("R47I_POLY_ENVELOPE_FAIL", var))
        if candidate["accepted"]:
            replay = r45a.independent_macro_replay(before, candidate)
            if not replay["pass"]:
                raise AssertionError(("R47I_MACRO_REPLAY_FAIL", var, replay))
            row = debt_row(before, candidate, True)
            if row["debt_class"] == "DEBT_CONTRACT_VIOLATION":
                raise AssertionError(("R47I_R47H_DEBT_CONTRACT_FAIL", row))
            rows.append(row)
            return {
                "selected": row,
                "variables_checked": checked,
                "total_variables": len(r33.variables(before)),
                "rows_prefix": rows,
            }
        row = debt_row(before, candidate, None)
        if row["debt_class"] == "DEBT_CONTRACT_VIOLATION":
            raise AssertionError(("R47I_R47H_DEBT_CONTRACT_FAIL", row))
        rows.append(row)
    return {
        "selected": None,
        "variables_checked": checked,
        "total_variables": len(r33.variables(before)),
        "rows_prefix": rows,
    }


def signed_same_support_variants(source):
    vs = tuple(sorted(abs(int(l)) for l in source))
    variants = set()
    for signs in itertools.product((-1, 1), repeat=len(vs)):
        variants.add(r33.canonical_clause(s * v for s, v in zip(signs, vs)))
    variants.discard(tuple(source))
    return tuple(sorted(variants))


def mutate_one_clause(original, source, replacement):
    before = r33.canonical_formula(original)
    if tuple(source) not in before:
        raise AssertionError("R47I_SOURCE_NOT_IN_ORIGINAL")
    remaining = [c for c in before if c != tuple(source)]
    if tuple(replacement) in remaining:
        return None
    mutated = r33.canonical_formula(remaining + [tuple(replacement)])
    if len(mutated) != len(before):
        raise AssertionError("R47I_CLAUSE_COUNT_DRIFT")
    if any(len(c) != 3 or r33.is_tautology(c) for c in mutated):
        raise AssertionError("R47I_EXACT_3CNF_DRIFT")
    return mutated


def compact_reachable_record(phase, source, replacement, mutated, reached, scan):
    fixpoint = r33.canonical_formula(reached["formula"])
    selected = scan["selected"]
    return {
        "phase": phase,
        "source_clause": list(source),
        "replacement_clause": list(replacement),
        "mutated_original_hash": r47f.formula_hash(mutated),
        "mutated_original_CLV": list(r33.measure(mutated)),
        "fixpoint_hash": r47f.formula_hash(fixpoint),
        "fixpoint_CLV": list(r33.measure(fixpoint)),
        "trajectory": reached["trajectory"],
        "variables_checked_to_first_accept": int(scan["variables_checked"]),
        "total_fixpoint_variables": int(scan["total_variables"]),
        "selected": selected,
        "rows_prefix": scan["rows_prefix"],
    }


def run():
    original = r33.deterministic_random_3cnf(BASE["seed"], n=BASE["n"], ratio=BASE["ratio"])
    if r47f.formula_hash(original) != BASE["original_hash"]:
        raise AssertionError("R47I_BASE_ORIGINAL_HASH_DRIFT")
    if list(r33.measure(original)) != BASE["original_CLV"]:
        raise AssertionError("R47I_BASE_ORIGINAL_CLV_DRIFT")
    baseline_reached = r47f.reachable_fixpoint(original)
    if baseline_reached is None:
        raise AssertionError("R47I_BASE_NO_LONGER_REACHES_FIXPOINT")
    baseline_fixpoint = r33.canonical_formula(baseline_reached["formula"])
    if r47f.formula_hash(baseline_fixpoint) != BASE["fixpoint_hash"]:
        raise AssertionError("R47I_BASE_FIXPOINT_HASH_DRIFT")
    if list(r33.measure(baseline_fixpoint)) != BASE["fixpoint_CLV"]:
        raise AssertionError("R47I_BASE_FIXPOINT_CLV_DRIFT")
    baseline_scan = first_accepted_with_debt(baseline_fixpoint)
    if baseline_scan["selected"] is None:
        raise AssertionError("R47I_BASE_MACRO_DISAPPEARED")
    if int(baseline_scan["selected"]["var"]) != BASE["selected_var"]:
        raise AssertionError(("R47I_BASE_SELECTED_VAR_DRIFT", baseline_scan["selected"]))
    if baseline_scan["selected"]["final_CLV"] != BASE["selected_final_CLV"]:
        raise AssertionError("R47I_BASE_SELECTED_FINAL_CLV_DRIFT")

    sources_v7 = [c for c in original if any(abs(l) == 7 for l in c)]
    sources_other = [c for c in original if c not in sources_v7]
    phases = (("PIVOT7_TOUCHING", sources_v7), ("REMAINING_SUPPORTS", sources_other))

    metrics = {
        "source_clause_count": len(original),
        "pivot7_touching_source_count": len(sources_v7),
        "mutants_generated": 0,
        "mutants_skipped_duplicate": 0,
        "reachable_fixpoints": 0,
        "unique_reachable_fixpoints": 0,
        "macro_covered_fixpoints": 0,
        "macro_dead_fixpoints": 0,
        "phase": {},
    }
    seen_fixpoints = set()
    first_counterexample = None
    hardest = None
    hardest_score = None

    for phase, sources in phases:
        pm = {"mutants_generated": 0, "reachable_fixpoints": 0, "unique_reachable_fixpoints": 0, "macro_covered": 0, "macro_dead": 0}
        metrics["phase"][phase] = pm
        for source in sources:
            for replacement in signed_same_support_variants(source):
                mutated = mutate_one_clause(original, source, replacement)
                if mutated is None:
                    metrics["mutants_skipped_duplicate"] += 1
                    continue
                metrics["mutants_generated"] += 1
                pm["mutants_generated"] += 1
                reached = r47f.reachable_fixpoint(mutated)
                if reached is None:
                    continue
                metrics["reachable_fixpoints"] += 1
                pm["reachable_fixpoints"] += 1
                fixpoint = r33.canonical_formula(reached["formula"])
                fh = r47f.formula_hash(fixpoint)
                if fh in seen_fixpoints:
                    continue
                seen_fixpoints.add(fh)
                metrics["unique_reachable_fixpoints"] += 1
                pm["unique_reachable_fixpoints"] += 1
                scan = first_accepted_with_debt(fixpoint)
                record = compact_reachable_record(phase, source, replacement, mutated, reached, scan)
                if scan["selected"] is None:
                    metrics["macro_dead_fixpoints"] += 1
                    pm["macro_dead"] += 1
                    record["mutated_original_formula"] = [list(c) for c in mutated]
                    record["fixpoint_formula"] = [list(c) for c in fixpoint]
                    first_counterexample = record
                    break
                metrics["macro_covered_fixpoints"] += 1
                pm["macro_covered"] += 1
                score = int(scan["variables_checked"])
                if hardest_score is None or score > hardest_score:
                    hardest_score = score
                    hardest = record
            if first_counterexample is not None:
                break
        if first_counterexample is not None:
            break

    verdict = (
        "EXPLICIT_REACHABLE_ONE_SWAP_MACRO_DEAD_COUNTEREXAMPLE_FOUND"
        if first_counterexample is not None
        else "NO_MACRO_DEAD_COUNTEREXAMPLE_IN_FROZEN_ONE_SWAP_FRONTIER__O4_OPEN"
    )
    out = {
        "gate": "JANUS_TRUMP_R47I_R47G_ONE_SWAP_MACRO_DEAD_COMPLEMENT_HUNT",
        "verdict": verdict,
        "baseline": {
            "source": BASE,
            "fixpoint_CLV": list(r33.measure(baseline_fixpoint)),
            "baseline_scan": baseline_scan,
        },
        "mutation_contract": "ONE_CLAUSE_SAME_SUPPORT_SIGN_PATTERN_REPLACEMENT",
        "metrics": metrics,
        "first_counterexample": first_counterexample,
        "hardest_covered": hardest,
        "interpretation": {
            "finite_frontier_only": True,
            "universal_theorem_elevation_allowed": False,
            "counterexample_if_found_refutes_current_frozen_macro_grammar_only": True,
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
