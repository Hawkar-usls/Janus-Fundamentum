from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o
import janus_trump_r48v_r47j_width5_discharge_operator_forensics as r48v

GATE = "JANUS_TRUMP_R48W_PIVOT10_TERMINAL_PREEMPTION_DISRUPTION"
EXPECTED_ROOT = "3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
PREFIX = [2, 4, 5, 7, 9]
TARGET_PIVOT = 10
WIDTH_CAP = 4
MAX_MUTANTS = 48


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def fhash(f):
    return r47f.formula_hash(canon(f))


def maxw(f):
    x = canon(f)
    return max((len(c) for c in x), default=0)


def width5(f):
    return [tuple(c) for c in canon(f) if len(c) == 5]


def advance_prefix(root):
    current = canon(root)
    path = []
    for step, var in enumerate(PREFIX, 1):
        candidate = r48o.r47m.macro_candidate_full_closure(current, int(var))
        if candidate is None:
            return None, path, {"kind": "PREFIX_CANDIDATE_MISSING", "step": step, "var": var}
        replay = r48o.r47m.independent_replay(current, candidate)
        if not replay["pass"]:
            raise AssertionError(("R48W_PREFIX_REPLAY_FAIL", step, var, replay))
        row = r48o.candidate_row(current, candidate, True)
        final = canon(candidate["normalization"]["final_formula"])
        path.append({
            "step": step,
            "var": int(var),
            "state_hash": fhash(current),
            "state_CLV": list(clv(current)),
            "state_max_width": maxw(current),
            "final_hash": fhash(final),
            "final_CLV": list(clv(final)),
            "final_max_width": maxw(final),
            "terminal": row["terminal"],
            "eligible": row["eligible"],
            "full_independent_replay_pass": True,
        })
        if row["terminal"] is not None:
            return None, path, {"kind": "PREFIX_TERMINATED_EARLY", "step": step, "var": var, "terminal": row["terminal"]}
        if not row["eligible"]:
            return None, path, {"kind": "PREFIX_NOT_ELIGIBLE", "step": step, "var": var}
        if maxw(final) > WIDTH_CAP:
            return None, path, {"kind": "PREFIX_LEFT_WIDTH4", "step": step, "var": var, "final_max_width": maxw(final)}
        current = final
    return current, path, None


def baseline():
    meta, reached, root = r48o.reconstruct_root()
    root = canon(root)
    if fhash(root) != EXPECTED_ROOT or maxw(root) > WIDTH_CAP:
        raise AssertionError(("R48W_BASELINE_ROOT_DRIFT", fhash(root), maxw(root)))
    predecessor, path, err = advance_prefix(root)
    if predecessor is None or err is not None:
        raise AssertionError(("R48W_BASELINE_PREFIX_DRIFT", err))
    candidate = r48o.r47m.macro_candidate_full_closure(predecessor, TARGET_PIVOT)
    if candidate is None:
        raise AssertionError("R48W_BASELINE_PIVOT10_MISSING")
    replay = r48o.r47m.independent_replay(predecessor, candidate)
    if not replay["pass"]:
        raise AssertionError(("R48W_BASELINE_PIVOT10_REPLAY_FAIL", replay))
    forced = canon(candidate["DP"]["transformed"])
    trace = r48v.exact_r47j_trace(forced)
    r47j = r48v.r47j.normalize_to_certified_fixpoint(forced)
    r47j_final = canon(r47j["final_formula"])
    survivors = width5(r47j_final)
    full_final = canon(candidate["normalization"]["final_formula"])
    if maxw(predecessor) != 4 or maxw(forced) != 5 or maxw(r47j_final) != 5:
        raise AssertionError(("R48W_BASELINE_WIDTH_DRIFT", maxw(predecessor), maxw(forced), maxw(r47j_final)))
    if len(survivors) != 1:
        raise AssertionError(("R48W_BASELINE_SURVIVOR_COUNT_DRIFT", len(survivors), survivors))
    if candidate["normalization"]["terminal"] != "DIRECT_EMPTY_CNF":
        raise AssertionError(("R48W_BASELINE_TERMINAL_DRIFT", candidate["normalization"]["terminal"]))
    if int(candidate["normalization"]["SA_BVE_application_count"]) != 8:
        raise AssertionError(("R48W_BASELINE_SABVE_DRIFT", candidate["normalization"]["SA_BVE_application_count"]))
    survivor = survivors[0]
    target_vars = sorted({TARGET_PIVOT} | {abs(int(l)) for l in survivor})
    return {
        "meta": meta,
        "root": root,
        "predecessor": predecessor,
        "path": path,
        "candidate": candidate,
        "forced": forced,
        "trace": trace,
        "r47j_final": r47j_final,
        "full_final": full_final,
        "survivor": survivor,
        "target_vars": target_vars,
        "original": canon(meta["mutated_original"]),
        "reached": reached,
    }


def targeted_third_mutations(original, target_vars):
    target = set(int(v) for v in target_vars)
    sources = [c for c in canon(original) if {abs(int(l)) for l in c} & target]
    seen = set()
    ordinal = 0
    for source in sources:
        for replacement in r47i.signed_same_support_variants(source):
            mutated = r47i.mutate_one_clause(original, source, replacement)
            if mutated is None:
                continue
            mutated = canon(mutated)
            r47x.validate_exact_3cnf(mutated)
            h = fhash(mutated)
            if h in seen:
                continue
            seen.add(h)
            ordinal += 1
            yield {
                "ordinal": ordinal,
                "source_clause": list(source),
                "replacement_clause": list(replacement),
                "mutated_original": mutated,
                "mutated_original_hash": h,
            }
            if ordinal >= MAX_MUTANTS:
                return


def analyze_target(predecessor):
    candidate = r48o.r47m.macro_candidate_full_closure(predecessor, TARGET_PIVOT)
    if candidate is None:
        return {"kind": "PIVOT10_CANDIDATE_MISSING", "dangerous": False}
    replay = r48o.r47m.independent_replay(predecessor, candidate)
    if not replay["pass"]:
        raise AssertionError(("R48W_TARGET_REPLAY_FAIL", replay))
    row = r48o.candidate_row(predecessor, candidate, True)
    forced = canon(candidate["DP"]["transformed"])
    full_final = canon(candidate["normalization"]["final_formula"])
    forced_w = maxw(forced)
    if forced_w > WIDTH_CAP:
        trace = r48v.exact_r47j_trace(forced)
        r47j_final = canon(r48v.r47j.normalize_to_certified_fixpoint(forced)["final_formula"])
        r47j_w = maxw(r47j_final)
        r47j_w5 = len(width5(r47j_final))
    else:
        trace = None
        r47j_final = None
        r47j_w = forced_w
        r47j_w5 = 0
    terminal = candidate["normalization"]["terminal"]
    dangerous = bool(
        forced_w > WIDTH_CAP
        and r47j_w > WIDTH_CAP
        and terminal is None
        and maxw(full_final) > WIDTH_CAP
        and row["eligible"]
        and row["no_fresh_variables"]
        and int(row["delta_V_eliminated"]) >= 1
    )
    return {
        "kind": "PIVOT10_ANALYZED",
        "dangerous": dangerous,
        "eligible": bool(row["eligible"]),
        "delta_V_eliminated": int(row["delta_V_eliminated"]),
        "no_fresh_variables": bool(row["no_fresh_variables"]),
        "predecessor_hash": fhash(predecessor),
        "predecessor_CLV": list(clv(predecessor)),
        "predecessor_max_width": maxw(predecessor),
        "forced_DP_hash": fhash(forced),
        "forced_DP_CLV": list(clv(forced)),
        "forced_DP_max_width": forced_w,
        "R47J_final_hash": None if r47j_final is None else fhash(r47j_final),
        "R47J_final_CLV": None if r47j_final is None else list(clv(r47j_final)),
        "R47J_final_max_width": int(r47j_w),
        "R47J_width5_clause_count": int(r47j_w5),
        "R47J_first_width_discharge": None if trace is None else trace["first_width_discharge"],
        "full_final_hash": fhash(full_final),
        "full_final_CLV": list(clv(full_final)),
        "full_final_max_width": maxw(full_final),
        "full_terminal": terminal,
        "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
        "full_independent_replay_pass": True,
    }


def scan_existential_width4(predecessor):
    rows, _ = r48o.scan(predecessor, True)
    eligible = [r for r in rows if r.get("eligible", False)]
    terminal = [r for r in eligible if r.get("terminal") is not None]
    safe = [r for r in eligible if r.get("terminal") is None and int(r.get("final_max_width", 999)) <= WIDTH_CAP]
    return {
        "candidate_count": len(rows),
        "eligible_count": len(eligible),
        "terminal_count": len(terminal),
        "width4_safe_nonterminal_count": len(safe),
        "has_existential_width4_successor": bool(terminal or safe),
        "safe_vars": sorted(int(r["var"]) for r in terminal + safe),
        "rows": rows,
    }


def compact_record(meta, root, path, target):
    return {
        "ordinal": int(meta["ordinal"]),
        "source_clause": meta["source_clause"],
        "replacement_clause": meta["replacement_clause"],
        "mutated_original_hash": meta["mutated_original_hash"],
        "root_hash": fhash(root),
        "root_CLV": list(clv(root)),
        "root_max_width": maxw(root),
        "selected_prefix": [int(x["var"]) for x in path],
        "predecessor_hash": target.get("predecessor_hash"),
        "target": target,
    }


def run():
    b = baseline()
    target_vars = b["target_vars"]
    metrics = {
        "mutated_originals_generated": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "root_width_gt4": 0,
        "duplicate_reachable_roots": 0,
        "unique_reachable_roots": 0,
        "prefix_preserving_roots": 0,
        "pivot10_forced_width_gt4": 0,
        "pivot10_R47J_width_gt4": 0,
        "pivot10_R47J_survivor_full_handled": 0,
        "dangerous_percandidate_counterexamples": 0,
        "strong_existential_width4_obstructions": 0,
    }
    seen_roots = set()
    records = []
    prefix_divergences = []
    first_percandidate = None
    first_strong = None
    first_r47j_survivor_handled = None

    for meta in targeted_third_mutations(b["original"], target_vars):
        metrics["mutated_originals_generated"] += 1
        reached = r47f.reachable_fixpoint(meta["mutated_original"])
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root = canon(reached["formula"])
        if maxw(root) > WIDTH_CAP:
            metrics["root_width_gt4"] += 1
            continue
        rh = fhash(root)
        if rh in seen_roots:
            metrics["duplicate_reachable_roots"] += 1
            continue
        seen_roots.add(rh)
        metrics["unique_reachable_roots"] += 1

        predecessor, path, err = advance_prefix(root)
        if predecessor is None:
            prefix_divergences.append({
                "ordinal": int(meta["ordinal"]),
                "mutated_original_hash": meta["mutated_original_hash"],
                "root_hash": rh,
                "root_CLV": list(clv(root)),
                "error": err,
            })
            continue
        metrics["prefix_preserving_roots"] += 1
        target = analyze_target(predecessor)
        if target.get("forced_DP_max_width", 0) > WIDTH_CAP:
            metrics["pivot10_forced_width_gt4"] += 1
        if target.get("R47J_final_max_width", 0) > WIDTH_CAP:
            metrics["pivot10_R47J_width_gt4"] += 1
        record = compact_record(meta, root, path, target)
        records.append(record)

        if target.get("R47J_final_max_width", 0) > WIDTH_CAP and not target.get("dangerous", False):
            if target.get("full_terminal") is not None or target.get("full_final_max_width", 999) <= WIDTH_CAP:
                metrics["pivot10_R47J_survivor_full_handled"] += 1
                if first_r47j_survivor_handled is None:
                    first_r47j_survivor_handled = record

        if not target.get("dangerous", False):
            continue
        metrics["dangerous_percandidate_counterexamples"] += 1
        existential = scan_existential_width4(predecessor)
        record["existential_width4_scan"] = existential
        if not existential["has_existential_width4_successor"]:
            metrics["strong_existential_width4_obstructions"] += 1
            if first_strong is None:
                first_strong = record
            break
        if first_percandidate is None:
            first_percandidate = record

    if first_strong is not None:
        verdict = "EXPLICIT_REACHABLE_EXISTENTIAL_WIDTH4_COVERAGE_OBSTRUCTION_FOUND"
        witness = first_strong
    elif first_percandidate is not None:
        verdict = "EXPLICIT_REACHABLE_PERCANDIDATE_WIDTH_RESET_COUNTEREXAMPLE_BUT_SAFE_ALTERNATIVE_EXISTS"
        witness = first_percandidate
    elif first_r47j_survivor_handled is not None:
        verdict = "R47J_WIDTH5_SURVIVOR_FOUND_BUT_FULL_CLOSURE_RESETS_OR_TERMINATES__FINITE_ONLY"
        witness = first_r47j_survivor_handled
    elif metrics["prefix_preserving_roots"] > 0:
        verdict = "PIVOT10_NEAR_MISS_NOT_REPRODUCED_IN_TARGETED_THIRD_SWAP_PANEL__FINITE_ONLY"
        witness = None
    else:
        verdict = "NO_PREFIX_PRESERVING_REACHABLE_ROOTS_IN_TARGETED_PANEL__FINITE_ONLY"
        witness = None

    return {
        "gate": GATE,
        "verdict": verdict,
        "baseline": {
            "root_hash": fhash(b["root"]),
            "certified_prefix": PREFIX,
            "predecessor_hash": fhash(b["predecessor"]),
            "predecessor_CLV": list(clv(b["predecessor"])),
            "predecessor_max_width": maxw(b["predecessor"]),
            "pivot": TARGET_PIVOT,
            "surviving_width5_clause": list(b["survivor"]),
            "target_vars": target_vars,
            "full_terminal": b["candidate"]["normalization"]["terminal"],
            "SA_BVE_application_count": int(b["candidate"]["normalization"]["SA_BVE_application_count"]),
        },
        "metrics": metrics,
        "first_witness": witness,
        "records": records,
        "prefix_divergences": prefix_divergences,
        "interpretation": {
            "finite_targeted_panel_only": True,
            "percandidate_counterexample_refutes_reset_for_every_DP_successor": first_percandidate is not None or first_strong is not None,
            "percandidate_counterexample_alone_refutes_existential_W4_coverage": False,
            "strong_obstruction_refutes_universal_W4_for_frozen_grammar": first_strong is not None,
            "finite_success_proves_universal_W4": False,
        },
        "firewall": {
            "UNIVERSAL_WIDTH_RESET_FOR_EVERY_DP_SUCCESSOR": "REFUTED_FOR_FROZEN_GRAMMAR" if (first_percandidate is not None or first_strong is not None) else "NOT_PROVED",
            "UNIVERSAL_WIDTH_4_COVERAGE": "REFUTED_FOR_FROZEN_GRAMMAR" if first_strong is not None else "NOT_PROVED",
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    d = run()
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    w = d["first_witness"]
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "baseline": d["baseline"],
        "metrics": d["metrics"],
        "first_witness": None if w is None else {
            "ordinal": w["ordinal"],
            "root_hash": w["root_hash"],
            "root_CLV": w["root_CLV"],
            "target": w["target"],
            "existential_width4_scan": w.get("existential_width4_scan"),
        },
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
