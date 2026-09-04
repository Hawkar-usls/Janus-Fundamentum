from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50a_exact_operational_token_tranception_controller as r50a
import janus_trump_r50b_minimal_deadcore_structural_classification as r50b

GATE = "JANUS_TRUMP_R50C_TOP2_MIN_TAUTO_PROSPECTIVE_FALSIFIER"
WIDTH_CAP = 4
DISCOVERY_MAX_ORDINAL = 64
PROSPECTIVE_START_ORDINAL = 65
PROSPECTIVE_END_ORDINAL = 256
TARGET_PROSPECTIVE_ROOTS = 52
SELECTOR_K = 2


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


def discovery_root_hashes():
    roots = r49i.collect_roots()
    return {fhash(root) for root, _ in roots}


def collect_prospective_roots():
    center_original, _, _ = r47x.load_center_original()
    discovery = discovery_root_hashes()
    seen = set(discovery)
    roots = []
    scanned = 0

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if ordinal < PROSPECTIVE_START_ORDINAL:
            continue
        if ordinal > PROSPECTIVE_END_ORDINAL:
            break
        scanned += 1
        if mutated is None:
            continue
        r47x.validate_exact_3cnf(mutated)
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            continue
        root = canon(reached["formula"])
        rh = fhash(root)
        if rh in seen:
            continue
        seen.add(rh)
        roots.append((
            root,
            {
                "kind": "PROSPECTIVE_ONE_SWAP_REACHABLE_FIXPOINT",
                "frontier_ordinal": int(ordinal),
                "phase": phase,
                "source_clause": list(source),
                "replacement_clause": list(replacement),
            },
        ))
        if len(roots) == TARGET_PROSPECTIVE_ROOTS:
            break

    if len(roots) != TARGET_PROSPECTIVE_ROOTS:
        raise IntegrityFailure((
            "R50C_PROSPECTIVE_CORPUS_INSUFFICIENT",
            len(roots),
            TARGET_PROSPECTIVE_ROOTS,
            PROSPECTIVE_START_ORDINAL,
            PROSPECTIVE_END_ORDINAL,
            scanned,
        ))
    return roots


def rank_top2_geometry_rows(geometry):
    ordered = sorted(
        geometry,
        key=lambda g: (int(g["tautological_cross_pair_count"]), int(g["var"])),
    )
    return ordered[: min(SELECTOR_K, len(ordered))], ordered


def top2_min_taut_geometry(formula):
    f = canon(formula)
    vars_ = [int(v) for v in sorted(r33.variables(f))]
    geometry = [r50b.cross_pair_profile(f, v) for v in vars_]
    return rank_top2_geometry_rows(geometry)


def hard_state_probe(formula):
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        raise IntegrityFailure(("R50C_NON_W4_HARD_PROBE", max_width(f), fhash(f)))

    status = r50b.r33_status(f)
    if status["kind"] != "STALL":
        return {
            "applicable": False,
            "reason": "R33_OPEN",
            "state_hash": fhash(f),
            "state_CLV": clv(f),
        }

    vars_ = [int(v) for v in sorted(r33.variables(f))]
    profiles = [r49i.variable_profile(f, v) for v in vars_]
    direct = [
        int(p["var"])
        for p in profiles
        if p["bipolar"] and int(p["chi_star"]) <= WIDTH_CAP
    ]
    if direct:
        return {
            "applicable": False,
            "reason": "R49H_DIRECT_OPEN",
            "state_hash": fhash(f),
            "state_CLV": clv(f),
            "direct_authorized_pivots": direct,
        }

    selected_geometry, all_geometry = top2_min_taut_geometry(f)
    profile_by_var = {int(p["var"]): p for p in profiles}
    selected_rows = []
    first_safe_rank = None

    for rank, g in enumerate(selected_geometry, 1):
        var = int(g["var"])
        row = r50b.exact_r47j_row(f, var, profile_by_var[var])
        selected_rows.append({
            "rank": int(rank),
            "var": var,
            "tautological_cross_pair_count": int(g["tautological_cross_pair_count"]),
            "retained_nontautological_pair_count": int(g["retained_nontautological_pair_count"]),
            "bad_pair_count_union_ge_5": int(g["bad_pair_count_union_ge_5"]),
            "chi_star": int(profile_by_var[var]["chi_star"]),
            "width4_safe": bool(row.get("width4_safe", False)),
            "final_max_width": row.get("final_max_width"),
            "reason_codes": list(row.get("reason_codes", [])),
            "independent_replay_pass": row.get("independent_replay_pass"),
        })
        if row.get("width4_safe", False) and first_safe_rank is None:
            first_safe_rank = int(rank)

    covered = first_safe_rank is not None
    return {
        "applicable": True,
        "state_hash": fhash(f),
        "state_CLV": clv(f),
        "state_max_width": max_width(f),
        "variable_count": len(vars_),
        "selector": "TOP2_MIN_TAUTOLOGICAL_CROSS_PAIR_COUNT_THEN_VARIABLE_ID",
        "selector_is_truth_blind": True,
        "selector_k": SELECTOR_K,
        "selected_rows": selected_rows,
        "first_safe_rank": first_safe_rank,
        "covered": bool(covered),
        "all_geometry_summary": [
            {
                "var": int(g["var"]),
                "tautological_cross_pair_count": int(g["tautological_cross_pair_count"]),
                "retained_nontautological_pair_count": int(g["retained_nontautological_pair_count"]),
                "bad_pair_count_union_ge_5": int(g["bad_pair_count_union_ge_5"]),
            }
            for g in all_geometry
        ],
        "formula": None if covered else [list(c) for c in f],
    }


def trace_root(root, provenance, root_index):
    root = canon(root)
    root_vars = set(r33.variables(root))
    current = root
    seen = set()
    cap = 2 * max(1, len(root_vars)) + 8
    events = []
    hard_probes = []
    total_token_verifier_calls = 0

    for step_index in range(cap):
        ch = fhash(current)
        if ch in seen:
            raise IntegrityFailure(("R50C_TRACE_CYCLE", root_index, ch))
        seen.add(ch)
        if max_width(current) > WIDTH_CAP:
            raise IntegrityFailure(("R50C_TRACE_WIDTH_DRIFT", root_index, max_width(current)))
        if not set(r33.variables(current)).issubset(root_vars):
            raise IntegrityFailure(("R50C_TRACE_FRESH_VARIABLE", root_index, ch))

        probe = hard_state_probe(current)
        if probe["applicable"]:
            hard_probes.append(probe)
            total_token_verifier_calls += len(probe["selected_rows"])
            if not probe["covered"]:
                step = r50a.exact_step(current)
                return {
                    "covered": False,
                    "root_index": int(root_index),
                    "root_hash": fhash(root),
                    "root_CLV": clv(root),
                    "provenance": provenance,
                    "events": events,
                    "hard_probes": hard_probes,
                    "counterexample": {
                        "state_hash": probe["state_hash"],
                        "state_CLV": probe["state_CLV"],
                        "state_formula": probe["formula"],
                        "selected_rows": probe["selected_rows"],
                        "all_geometry_summary": probe["all_geometry_summary"],
                        "current_R50A_step_kind": step["kind"],
                        "current_R50A_step_lane": step["lane"],
                    },
                    "total_token_verifier_calls": int(total_token_verifier_calls),
                }

        step = r50a.exact_step(current)
        events.append({
            "step": int(step_index),
            "state_hash": ch,
            "state_CLV": clv(current),
            "hard_probe_applicable": bool(probe["applicable"]),
            "hard_probe_covered": None if not probe["applicable"] else bool(probe["covered"]),
            "hard_probe_first_safe_rank": None if not probe["applicable"] else probe["first_safe_rank"],
            "R50A_step_kind": step["kind"],
            "R50A_step_lane": step["lane"],
        })

        if step["kind"] == "OPEN_OBSTRUCTION":
            raise IntegrityFailure(("R50C_R50A_OPEN_WITHOUT_TOP2_COUNTEREXAMPLE", root_index, ch))
        if step["kind"] == "TERMINAL":
            return {
                "covered": True,
                "root_index": int(root_index),
                "root_hash": fhash(root),
                "root_CLV": clv(root),
                "provenance": provenance,
                "events": events,
                "hard_probes": hard_probes,
                "terminal": step.get("terminal"),
                "total_token_verifier_calls": int(total_token_verifier_calls),
            }

        current = canon(step["successor"])

    raise IntegrityFailure(("R50C_TRACE_STEP_CAP", root_index, cap, fhash(current)))


def compact_root(record):
    return {
        "covered": bool(record["covered"]),
        "root_index": int(record["root_index"]),
        "root_hash": record["root_hash"],
        "root_CLV": record["root_CLV"],
        "provenance": record["provenance"],
        "event_count": len(record["events"]),
        "hard_state_count": len(record["hard_probes"]),
        "hard_first_safe_rank_histogram": {
            "1": sum(1 for p in record["hard_probes"] if p["first_safe_rank"] == 1),
            "2": sum(1 for p in record["hard_probes"] if p["first_safe_rank"] == 2),
            "MISS": sum(1 for p in record["hard_probes"] if p["first_safe_rank"] is None),
        },
        "total_token_verifier_calls": int(record["total_token_verifier_calls"]),
        "counterexample_state_hash": None if record["covered"] else record["counterexample"]["state_hash"],
    }


def run(shard_index=0, shard_count=4):
    shard_index = int(shard_index)
    shard_count = int(shard_count)
    if shard_count < 1 or not (0 <= shard_index < shard_count):
        raise ValueError(("R50C_BAD_SHARD", shard_index, shard_count))

    roots = collect_prospective_roots()
    assigned = [
        (idx, root, provenance)
        for idx, (root, provenance) in enumerate(roots, 1)
        if (idx - 1) % shard_count == shard_index
    ]
    if not assigned:
        raise IntegrityFailure(("R50C_EMPTY_ASSIGNED_SHARD", shard_index, shard_count))

    records = []
    first_counterexample = None
    for idx, root, provenance in assigned:
        rec = trace_root(root, provenance, idx)
        records.append(rec)
        if not rec["covered"]:
            first_counterexample = rec
            break

    hard_probes = [p for rec in records for p in rec["hard_probes"]]
    first_rank = sum(1 for p in hard_probes if p["first_safe_rank"] == 1)
    second_rank = sum(1 for p in hard_probes if p["first_safe_rank"] == 2)
    misses = sum(1 for p in hard_probes if p["first_safe_rank"] is None)

    verdict = (
        "EXPLICIT_PROSPECTIVE_COUNTEREXAMPLE_TO_TOP2_MIN_TAUTO_SELECTOR_FOUND"
        if first_counterexample is not None
        else "FINITE_PROSPECTIVE_TOP2_MIN_TAUTO_COVERAGE__THEOREM_OPEN"
    )

    return {
        "gate": GATE,
        "verdict": verdict,
        "shard": {"index": shard_index, "count": shard_count},
        "parent_R50B_commit": "cb63d9db25a06780d897d5bd8107efeab4c1e026",
        "discovery": {
            "R50B_run_id": 33897153507,
            "discovery_frontier_ordinal_max": DISCOVERY_MAX_ORDINAL,
            "dedup_hard_states": 397,
            "top1_min_taut_safe": 374,
            "top2_min_taut_additional_safe": 23,
            "top2_min_taut_misses": 0,
            "role": "DISCOVERY_ONLY__NO_PROOF_AUTHORITY",
        },
        "prospective_corpus": {
            "definition": "FIRST_52_UNSEEN_UNIQUE_REACHABLE_FIXPOINTS_FROM_ONE_SWAP_FRONTIER_ORDINALS_65_THROUGH_256",
            "start_ordinal": PROSPECTIVE_START_ORDINAL,
            "end_ordinal": PROSPECTIVE_END_ORDINAL,
            "target_unique_roots": TARGET_PROSPECTIVE_ROOTS,
            "actual_unique_roots": len(roots),
            "disjoint_from_R49I_52_DISCOVERY_ROOT_HASHES": True,
        },
        "selector": {
            "name": "TOP2_MIN_TAUTOLOGICAL_CROSS_PAIR_COUNT_THEN_VARIABLE_ID",
            "k": SELECTOR_K,
            "truth_blind": True,
            "uses_R47J_outcome_for_ranking": False,
            "uses_variable_numeric_id_only_as_deterministic_tiebreak": True,
            "proof_authority": False,
        },
        "metrics": {
            "assigned_roots": len(assigned),
            "roots_attempted": len(records),
            "roots_covered": sum(1 for r in records if r["covered"]),
            "counterexamples": 0 if first_counterexample is None else 1,
            "hard_states_tested": len(hard_probes),
            "rank1_safe": first_rank,
            "rank2_safe_after_rank1_fail": second_rank,
            "top2_misses": misses,
            "token_verifier_calls": sum(int(r["total_token_verifier_calls"]) for r in records),
            "mean_token_verifier_calls_per_hard_state": (
                0.0 if not hard_probes
                else sum(int(r["total_token_verifier_calls"]) for r in records) / len(hard_probes)
            ),
        },
        "first_counterexample": None if first_counterexample is None else first_counterexample["counterexample"],
        "roots": [compact_root(r) for r in records],
        "interpretation": {
            "one_counterexample_refutes_top2_selector_conjecture": first_counterexample is not None,
            "finite_green_proves_universal_top2_selector": False,
            "if_finite_green_next": "ATTEMPT_SYMBOLIC_TOP2_EXISTENCE_LEMMA_OR_EXPAND_TO_TWO_SWAP_UNSEEN_FALSIFIER",
            "if_counterexample_next": "MINIMIZE_COUNTEREXAMPLE_AND_CLASSIFY_WHICH_LOCAL_GEOMETRY_FEATURE_WAS_MISSING",
        },
        "firewall": {
            "TOP2_MIN_TAUTO_UNIVERSAL_COVERAGE": "REFUTED" if first_counterexample is not None else "OPEN",
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard-index", type=int, default=0)
    ap.add_argument("--shard-count", type=int, default=4)
    args = ap.parse_args()
    out = run(args.shard_index, args.shard_count)
    path = Path(
        f"artifacts/JANUS_TRUMP_R50C_TOP2_MIN_TAUTO_PROSPECTIVE_FALSIFIER_SHARD_{args.shard_index}_OF_{args.shard_count}.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "shard": out["shard"],
        "metrics": out["metrics"],
        "first_counterexample": out["first_counterexample"],
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
