from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r49k_safe_only_width4_chain_52roots as r49k
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a

GATE = "JANUS_TRUMP_R50B_MINIMAL_DEADCORE_STRUCTURAL_CLASSIFICATION"
WIDTH_CAP = 4
EXPECTED_ROOTS = 52


class IntegrityFailure(RuntimeError):
    pass


def canon(formula):
    return r33.canonical_formula(formula)


def fhash(formula):
    return r49i.fhash(canon(formula))


def clv(formula):
    return list(r49i.clv(canon(formula)))


def max_width(formula):
    return r49i.max_width(canon(formula))


def clause_key(clause):
    return ",".join(str(int(x)) for x in clause)


def _hist(counter):
    return {str(k): int(counter[k]) for k in sorted(counter)}


def cross_pair_profile(formula, var):
    """Enumerate exact cross-polarity DP parent geometry for one pivot.

    This is descriptive theorem-mining instrumentation only.  It neither ranks nor
    selects pivots.  A retained pair is exactly one whose resolvent is not a
    tautology.  A bad pair for persisted W4 is a retained residual union of size
    at least five.
    """
    f = canon(formula)
    var = int(var)
    pos = [tuple(c) for c in f if var in c]
    neg = [tuple(c) for c in f if -var in c]
    union_hist = Counter()
    bad_union_hist = Counter()
    overlap_hist = Counter()
    bad_overlap_hist = Counter()
    bad_parent_usage = Counter()
    retained = 0
    tautological = 0
    bad = 0
    first_bad = None

    for pc in pos:
        a = set(pc)
        a.discard(var)
        for nc in neg:
            b = set(nc)
            b.discard(-var)
            u = a | b
            if r49i.is_tautological_union(u):
                tautological += 1
                continue
            retained += 1
            uw = len(u)
            ov = len(a & b)
            union_hist[uw] += 1
            overlap_hist[ov] += 1
            if uw >= 5:
                bad += 1
                bad_union_hist[uw] += 1
                bad_overlap_hist[ov] += 1
                bad_parent_usage[clause_key(pc)] += 1
                bad_parent_usage[clause_key(nc)] += 1
                if first_bad is None:
                    first_bad = {
                        "positive_parent": list(pc),
                        "negative_parent": list(nc),
                        "positive_residual": sorted(a, key=lambda x: (abs(x), x < 0)),
                        "negative_residual": sorted(b, key=lambda x: (abs(x), x < 0)),
                        "retained_union": sorted(u, key=lambda x: (abs(x), x < 0)),
                        "union_size": int(uw),
                        "signed_residual_intersection_size": int(ov),
                    }

    usage_hist = Counter(bad_parent_usage.values())
    return {
        "var": var,
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "bipolar": bool(pos and neg),
        "retained_nontautological_pair_count": int(retained),
        "tautological_cross_pair_count": int(tautological),
        "retained_union_size_histogram": _hist(union_hist),
        "bad_pair_count_union_ge_5": int(bad),
        "bad_union_size_histogram": _hist(bad_union_hist),
        "signed_residual_intersection_histogram": _hist(overlap_hist),
        "bad_signed_residual_intersection_histogram": _hist(bad_overlap_hist),
        "distinct_bad_parent_clause_count": len(bad_parent_usage),
        "maximum_bad_parent_reuse": max(bad_parent_usage.values(), default=0),
        "bad_parent_reuse_histogram": _hist(usage_hist),
        "first_bad_witness": first_bad,
    }


def r33_status(formula):
    f = canon(formula)
    result = r33.simplify(f)
    after = canon(result["final_formula"])
    terminal = result["terminal"]
    if terminal != "STALLED_STACK_LEAN_CORE":
        kind = "TERMINAL"
    elif after != f:
        kind = "REDUCTION"
    else:
        kind = "STALL"
    return {
        "kind": kind,
        "terminal": terminal,
        "input_hash": fhash(f),
        "after_hash": fhash(after),
        "input_CLV": clv(f),
        "after_CLV": clv(after),
    }


def exact_r47j_row(formula, var, profile):
    f = canon(formula)
    row, candidate = r50a._fallback_candidate(f, int(var))
    out = dict(row)
    out["var"] = int(var)
    out["chi_star"] = int(profile["chi_star"])
    out["reason_codes"] = []

    if candidate is None:
        out["independent_replay_pass"] = None
        out["reason_codes"] = ["NO_R47J_CANDIDATE"]
        return out

    if not candidate["DP_independent_replay_pass"]:
        raise IntegrityFailure(("R50B_DP_REPLAY_FLAG_FAIL", int(var)))
    if not candidate["polynomial_intermediate_envelope_pass"]:
        raise IntegrityFailure(("R50B_DP_ENVELOPE_FLAG_FAIL", int(var)))
    replay = r47j.independent_fixpoint_macro_replay(f, candidate)
    if not replay["pass"]:
        raise IntegrityFailure(("R50B_R47J_INDEPENDENT_REPLAY_FAIL", int(var), replay))
    out["independent_replay_pass"] = True

    if not out["width4_safe"]:
        if not out.get("no_fresh_variables", False):
            out["reason_codes"].append("FRESH_VARIABLE")
        if not out.get("strict_variable_descent", False):
            out["reason_codes"].append("NO_STRICT_VARIABLE_DESCENT")
        if int(out.get("final_max_width", WIDTH_CAP + 1)) > WIDTH_CAP:
            out["reason_codes"].append("FINAL_WIDTH_GT_4")
        if not out["reason_codes"]:
            raise IntegrityFailure(("R50B_UNCLASSIFIED_CLOSED_R47J_DOOR", int(var), out))
    return out


def classify_state(formula, source=None):
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        raise IntegrityFailure(("R50B_NON_W4_INPUT", max_width(f), fhash(f)))
    vars_ = [int(v) for v in sorted(r33.variables(f))]
    status = r33_status(f)
    base = {
        "state_hash": fhash(f),
        "state_CLV": clv(f),
        "state_max_width": max_width(f),
        "variable_count": len(vars_),
        "clause_count": len(f),
        "literal_count": sum(len(c) for c in f),
        "sources": [] if source is None else [source],
        "r33_status": status,
        "covered_under_current_R50A_machine": False,
        "deadcore_under_current_R50A_machine": False,
    }
    if status["kind"] != "STALL":
        base.update({
            "door": "R33_" + status["kind"],
            "direct_authorized_pivots": [],
            "r47j_rows": [],
            "r47j_scanned_all_current_variables": False,
            "formula": None,
        })
        base["covered_under_current_R50A_machine"] = True
        return base

    profiles = [r49i.variable_profile(f, v) for v in vars_]
    geometry = [cross_pair_profile(f, v) for v in vars_]
    direct = [int(p["var"]) for p in profiles if p["bipolar"] and int(p["chi_star"]) <= WIDTH_CAP]
    total_bad = sum(int(g["bad_pair_count_union_ge_5"]) for g in geometry)
    every_bad = all(int(g["bad_pair_count_union_ge_5"]) >= 1 for g in geometry) if vars_ else False
    all_bipolar = all(bool(p["bipolar"]) for p in profiles) if vars_ else False
    all_chi_ge5 = all(int(p["chi_star"]) >= 5 for p in profiles) if vars_ else False
    if all_bipolar and all_chi_ge5 and not every_bad:
        raise IntegrityFailure(("R50B_CHI_BAD_PAIR_DEFINITION_MISMATCH", fhash(f)))

    base.update({
        "profiles": profiles,
        "cross_pair_geometry": geometry,
        "direct_authorized_pivots": direct,
        "all_current_variables_bipolar": bool(all_bipolar),
        "all_current_variables_chi_star_ge_5": bool(all_chi_ge5),
        "every_current_variable_has_bad_pair": bool(every_bad),
        "total_bad_pair_count": int(total_bad),
        "bad_pair_count_minus_variable_count": int(total_bad - len(vars_)),
    })

    if direct:
        base.update({
            "door": "R49H_DIRECT_EXACT_DP",
            "covered_under_current_R50A_machine": True,
            "r47j_rows": [],
            "r47j_scanned_all_current_variables": False,
            "formula": None,
        })
        return base

    rows = []
    profile_by_var = {int(p["var"]): p for p in profiles}
    for var in vars_:
        rows.append(exact_r47j_row(f, var, profile_by_var[var]))
    safe = [int(r["var"]) for r in rows if r.get("width4_safe", False)]
    reasons = Counter(code for row in rows for code in row["reason_codes"])
    deadcore = bool(vars_) and not safe

    base.update({
        "door": "R47J_EXACT_FALLBACK" if safe else "OPEN_OBSTRUCTION",
        "covered_under_current_R50A_machine": bool(safe),
        "deadcore_under_current_R50A_machine": bool(deadcore),
        "r47j_safe_pivots": safe,
        "r47j_first_safe_pivot_by_R50A_order": None if not safe else int(min(safe)),
        "r47j_rows": rows,
        "r47j_reason_code_histogram": _hist(reasons),
        "r47j_scanned_all_current_variables": True,
        "formula": [list(c) for c in f],
    })
    return base


def _merge_source(record, source):
    if source is None:
        return record
    if source not in record["sources"]:
        record["sources"].append(source)
    return record


def classify_cached(cache, formula, source=None):
    h = fhash(formula)
    if h not in cache:
        cache[h] = classify_state(formula, source)
    else:
        _merge_source(cache[h], source)
    return cache[h]


def trace_r50a_root(root, provenance, root_index, cache):
    root = canon(root)
    current = root
    initial_v = len(r33.variables(root))
    cap = 2 * initial_v + 8
    events = []
    seen = set()

    for ordinal in range(cap):
        h = fhash(current)
        if h in seen:
            raise IntegrityFailure(("R50B_R50A_POLICY_TRACE_CYCLE", root_index, h))
        seen.add(h)
        source = {
            "kind": "R50A_POLICY_TRACE",
            "root_index": int(root_index),
            "trace_step": int(ordinal),
            "root_provenance": provenance,
        }
        classification = classify_cached(cache, current, source)
        step = r50a.exact_step(current)
        events.append({
            "trace_step": int(ordinal),
            "state_hash": h,
            "classification_door": classification["door"],
            "step_kind": step["kind"],
            "step_lane": step["lane"],
        })

        if classification["deadcore_under_current_R50A_machine"]:
            if step["kind"] != "OPEN_OBSTRUCTION" or not step.get("all_current_variables_checked", False):
                raise IntegrityFailure(("R50B_DEADCORE_R50A_DISAGREEMENT", root_index, h, step["kind"]))
            return {"terminal": False, "open_obstruction": True, "events": events, "final_hash": h}

        if step["kind"] == "OPEN_OBSTRUCTION":
            raise IntegrityFailure(("R50B_UNCLASSIFIED_R50A_OPEN", root_index, h))
        if step["kind"] == "TERMINAL":
            return {"terminal": True, "open_obstruction": False, "events": events, "final_hash": h}
        current = canon(step["successor"])
        if max_width(current) > WIDTH_CAP:
            raise IntegrityFailure(("R50B_POLICY_TRACE_WIDTH_DRIFT", root_index, max_width(current)))

    raise IntegrityFailure(("R50B_POLICY_TRACE_STEP_CAP", root_index, cap, fhash(current)))


def classify_safe_only_frontier(root, provenance, root_index, cache):
    rec = r49k.run_root(root, provenance, root_index)
    if rec["covered"]:
        return {"has_frontier_obstruction": False, "state_hash": None}
    core = canon(rec["obstruction"]["formula"])
    source = {
        "kind": "R49K_SAFE_ONLY_FRONTIER_OBSTRUCTION",
        "root_index": int(root_index),
        "safe_only_path": [int(s["pivot"]) for s in rec["steps"]],
        "root_provenance": provenance,
    }
    classification = classify_cached(cache, core, source)
    return {
        "has_frontier_obstruction": True,
        "state_hash": fhash(core),
        "classification_door": classification["door"],
        "deadcore": bool(classification["deadcore_under_current_R50A_machine"]),
    }


def greedy_clause_minimize_deadcore(formula):
    current = canon(formula)
    if not classify_state(current)["deadcore_under_current_R50A_machine"]:
        raise IntegrityFailure("R50B_MINIMIZER_INPUT_NOT_DEADCORE")
    deletion_log = []
    changed = True
    while changed:
        changed = False
        for clause in list(current):
            candidate = canon([c for c in current if c != clause])
            if candidate == current or max_width(candidate) > WIDTH_CAP:
                continue
            classification = classify_state(candidate)
            keep_deleted = bool(classification["deadcore_under_current_R50A_machine"])
            deletion_log.append({
                "removed_clause": list(clause),
                "candidate_hash": fhash(candidate),
                "remains_deadcore": keep_deleted,
            })
            if keep_deleted:
                current = candidate
                changed = True
                break
    final = classify_state(current)
    return {
        "locally_clause_minimal": True,
        "original_hash": fhash(formula),
        "final_hash": fhash(current),
        "final_CLV": clv(current),
        "deletion_attempts": len(deletion_log),
        "accepted_deletions": sum(int(x["remains_deadcore"]) for x in deletion_log),
        "deletion_log": deletion_log,
        "final_formula": [list(c) for c in current],
        "final_classification": final,
    }


def run(shard_index=0, shard_count=4):
    shard_index = int(shard_index)
    shard_count = int(shard_count)
    if shard_count < 1 or not (0 <= shard_index < shard_count):
        raise ValueError(("R50B_BAD_SHARD", shard_index, shard_count))
    roots = r49i.collect_roots()
    if len(roots) != EXPECTED_ROOTS:
        raise IntegrityFailure(("R50B_ROOT_CORPUS_DRIFT", len(roots), EXPECTED_ROOTS))
    assigned = [
        (idx, root, provenance)
        for idx, (root, provenance) in enumerate(roots, 1)
        if (idx - 1) % shard_count == shard_index
    ]

    cache = {}
    traces = []
    frontiers = []
    for idx, root, provenance in assigned:
        traces.append({
            "root_index": int(idx),
            "root_hash": fhash(root),
            "trace": trace_r50a_root(root, provenance, idx, cache),
        })
        frontiers.append({
            "root_index": int(idx),
            "root_hash": fhash(root),
            "frontier": classify_safe_only_frontier(root, provenance, idx, cache),
        })

    states = list(cache.values())
    hard = [
        s for s in states
        if s["r33_status"]["kind"] == "STALL" and not s.get("direct_authorized_pivots", [])
    ]
    deadcores = [s for s in hard if s["deadcore_under_current_R50A_machine"]]
    minimization = None
    if deadcores:
        minimization = greedy_clause_minimize_deadcore(deadcores[0]["formula"])

    reason_total = Counter(
        code
        for s in hard
        for row in s.get("r47j_rows", [])
        for code in row.get("reason_codes", [])
    )
    bad_margins = [int(s["bad_pair_count_minus_variable_count"]) for s in hard if s["variable_count"]]
    verdict = (
        "REPLAYABLE_R50A_DEADCORE_FOUND"
        if deadcores
        else "FINITE_ASSIGNED_CORPUS_COVERED__STRUCTURAL_THEOREM_OPEN"
    )
    out = {
        "gate": GATE,
        "verdict": verdict,
        "shard": {"index": shard_index, "count": shard_count},
        "parent_R50A_commit": "8c46d99415bc68291bb3253ca36b10a3c4202b17",
        "corpus": {
            "expected_total_roots": EXPECTED_ROOTS,
            "assigned_root_indices": [int(x[0]) for x in assigned],
            "assigned_root_count": len(assigned),
            "policy": "R50A_EXACT_POLICY_TRACE_PLUS_R49K_SAFE_ONLY_FIRST_HARD_FRONTIER",
        },
        "metrics": {
            "unique_states_classified": len(states),
            "hard_states_R33_stall_and_no_R49H_direct": len(hard),
            "deadcores": len(deadcores),
            "policy_traces_terminal": sum(int(x["trace"]["terminal"]) for x in traces),
            "policy_traces_open_obstruction": sum(int(x["trace"]["open_obstruction"]) for x in traces),
            "safe_only_frontier_obstructions": sum(int(x["frontier"]["has_frontier_obstruction"]) for x in frontiers),
            "hard_states_every_var_has_bad_pair": sum(int(s["every_current_variable_has_bad_pair"]) for s in hard),
            "hard_states_all_bipolar_and_chi_ge5": sum(int(s["all_current_variables_bipolar"] and s["all_current_variables_chi_star_ge_5"]) for s in hard),
            "total_bad_pairs_across_hard_states": sum(int(s["total_bad_pair_count"]) for s in hard),
            "minimum_bad_pair_count_minus_V": min(bad_margins, default=None),
            "maximum_bad_pair_count_minus_V": max(bad_margins, default=None),
            "closed_R47J_reason_code_histogram": _hist(reason_total),
        },
        "finite_conjecture_seed": {
            "all_observed_hard_states_every_var_has_bad_pair": bool(hard) and all(s["every_current_variable_has_bad_pair"] for s in hard),
            "all_observed_hard_states_have_bad_pair_count_at_least_V": bool(hard) and all(int(s["total_bad_pair_count"]) >= int(s["variable_count"]) for s in hard),
            "role": "OBSERVATION_ONLY__SEEK_SYMBOLIC_REACHABLE_STATE_UPPER_BOUND_OR_TRANSFER_LEMMA",
            "proof_authority": False,
        },
        "policy_traces": traces,
        "safe_only_frontiers": frontiers,
        "hard_state_classifications": hard,
        "first_deadcore": None if not deadcores else deadcores[0],
        "first_deadcore_local_clause_minimization": minimization,
        "firewall": {
            "HEURISTIC_AUTHORITY": False,
            "ML_AUTHORITY": False,
            "RANDOM_AUTHORITY": False,
            "FINITE_GREEN_IS_UNIVERSAL_COVERAGE": False,
            "UNIVERSAL_R50A_PROGRESS": "OPEN",
            "UNIVERSAL_W4_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=4)
    args = parser.parse_args()
    out = run(args.shard_index, args.shard_count)
    path = Path(f"artifacts/JANUS_TRUMP_R50B_MINIMAL_DEADCORE_STRUCTURAL_CLASSIFICATION_SHARD_{args.shard_index}_OF_{args.shard_count}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "shard": out["shard"],
        "metrics": out["metrics"],
        "finite_conjecture_seed": out["finite_conjecture_seed"],
        "first_deadcore_hash": None if out["first_deadcore"] is None else out["first_deadcore"]["state_hash"],
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
