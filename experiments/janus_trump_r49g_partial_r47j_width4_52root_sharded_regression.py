from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48q_width4_full_frozen_frontier_falsifier as r48q
import janus_trump_r49e_partial_r47j_width4_direct_controller as r49e

GATE = "JANUS_TRUMP_R49G_PARTIAL_R47J_WIDTH4_52ROOT_SHARDED_REGRESSION"
EXPECTED_ROOTS = 52
MAX_ORDINAL = 64
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return tuple(r33.measure(canon(f)))


def fhash(f):
    return r47f.formula_hash(canon(f))


def max_width(f):
    x = canon(f)
    return max((len(c) for c in x), default=0)


def collect_roots():
    center_original, _, center_fixpoint = r47x.load_center_original()
    roots = []
    seen = set()

    center = canon(center_fixpoint)
    roots.append((center, {
        "kind": "CENTER_CONTROL",
        "frontier_ordinal": 0,
        "phase": "CENTER",
        "source_clause": None,
        "replacement_clause": None,
        "mutated_original_hash": None,
    }))
    seen.add(fhash(center))

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if ordinal > MAX_ORDINAL:
            break
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
        roots.append((root, {
            "kind": "ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original_hash": fhash(mutated),
        }))

    if len(roots) != EXPECTED_ROOTS:
        raise AssertionError(("R49G_ROOT_CORPUS_DRIFT", len(roots), EXPECTED_ROOTS))
    return roots


def run_partial_root(root, provenance):
    root = canon(root)
    if max_width(root) > WIDTH_CAP:
        return {
            "covered": False,
            "root_hash": fhash(root),
            "root_CLV": list(clv(root)),
            "root_max_width": max_width(root),
            "provenance": provenance,
            "candidate_probe_count": 0,
            "selected_path": [],
            "max_persisted_width": max_width(root),
            "old_CLV_rejected_selected_count": 0,
            "obstruction": {"kind": "ROOT_ALREADY_EXCEEDS_WIDTH_CAP"},
            "terminal": None,
        }

    current = root
    V0 = clv(root)[2]
    selected_path = []
    selected_nonterminal = []
    total_probes = 0
    max_persisted = max_width(root)
    old_clv_rejected = 0
    total_selected_RUP_checks = 0

    for state_index in range(V0 + 1):
        if state_index >= V0:
            raise AssertionError(("R49G_STEP_CAP_EXHAUSTED", fhash(root), clv(current)))
        if max_width(current) > WIDTH_CAP:
            raise AssertionError(("R49G_PERSISTED_WIDTH_DRIFT", fhash(root), state_index, max_width(current)))

        rows, candidates = r49e.scan(current, replay_all=False)
        total_probes += len(rows)
        if total_probes > V0 * V0:
            raise AssertionError(("R49G_PROBE_CAP_EXCEEDED", fhash(root), total_probes, V0 * V0))
        safe = [x for x in rows if x.get("width4_safe", False)]

        if not safe:
            replay_rows, _ = r49e.scan(current, replay_all=True)
            replay_safe = [x for x in replay_rows if x.get("width4_safe", False)]
            if replay_safe:
                raise AssertionError(("R49G_OBSTRUCTION_REPLAY_FOUND_SAFE", fhash(root), replay_safe))
            return {
                "covered": False,
                "root_hash": fhash(root),
                "root_CLV": list(clv(root)),
                "root_max_width": max_width(root),
                "provenance": provenance,
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "max_persisted_width": max_persisted,
                "old_CLV_rejected_selected_count": old_clv_rejected,
                "total_selected_RUP_checks": total_selected_RUP_checks,
                "obstruction": {
                    "kind": "NO_PARTIAL_R47J_WIDTH4_SAFE_SUCCESSOR",
                    "state_index": int(state_index),
                    "state_hash": fhash(current),
                    "state_CLV": list(clv(current)),
                    "state_max_width": max_width(current),
                    "state_formula": [list(c) for c in current],
                    "candidate_rows": replay_rows,
                },
                "terminal": None,
            }

        chosen_row = min(safe, key=lambda x: int(x["var"]))
        chosen = candidates[int(chosen_row["var"])]
        replay = r49e.r47j.independent_fixpoint_macro_replay(current, chosen)
        if not replay["pass"]:
            raise AssertionError(("R49G_SELECTED_REPLAY_FAIL", fhash(root), chosen_row["var"], replay))
        row = r49e.candidate_row(current, chosen, True)
        final = canon(chosen["normalization"]["final_formula"])
        if not row["R47J_legacy_CLV_accepted_flag"]:
            old_clv_rejected += 1
        total_selected_RUP_checks += int(row["R47J_RUP_checks"])

        selected_path.append({
            "step": len(selected_path) + 1,
            "state_hash": fhash(current),
            "state_CLV": list(clv(current)),
            "state_max_width": max_width(current),
            "var": int(row["var"]),
            "final_CLV": row["final_CLV"],
            "final_max_width": int(row["final_max_width"]),
            "terminal": row["terminal"],
            "semantic_sat": row["semantic_sat"],
            "old_CLV_accepted": bool(row["R47J_legacy_CLV_accepted_flag"]),
            "R47J_RUP_checks": int(row["R47J_RUP_checks"]),
            "R47J_independent_replay_pass": True,
            "SA_BVE_application_count": 0,
        })

        if row["terminal"] is not None:
            lift = r49e.lift_root_sat(root, selected_nonterminal, chosen)
            if row["semantic_sat"] is True and not lift["pass"]:
                raise AssertionError(("R49G_ROOT_SAT_LIFT_FAIL", fhash(root)))
            return {
                "covered": True,
                "root_hash": fhash(root),
                "root_CLV": list(clv(root)),
                "root_max_width": max_width(root),
                "provenance": provenance,
                "candidate_probe_count": total_probes,
                "selected_path": selected_path,
                "selected_pivots": [int(x["var"]) for x in selected_path],
                "max_persisted_width": max(max_persisted, max_width(final)),
                "old_CLV_rejected_selected_count": old_clv_rejected,
                "total_selected_RUP_checks": total_selected_RUP_checks,
                "obstruction": None,
                "terminal": {
                    "kind": row["terminal"],
                    "semantic_sat": row["semantic_sat"],
                    "final_hash": fhash(final),
                    "final_CLV": list(clv(final)),
                    "SAT_root_reconstruction_pass": bool(lift["pass"]),
                },
            }

        if row["final_max_width"] > WIDTH_CAP or row["delta_V_eliminated"] < 1 or not row["no_fresh_variables"]:
            raise AssertionError(("R49G_SELECTED_PROGRESS_OR_WIDTH_FAIL", fhash(root), row))
        selected_nonterminal.append((current, chosen))
        max_persisted = max(max_persisted, int(row["final_max_width"]))
        current = final

    raise AssertionError(("R49G_UNREACHABLE_EXIT", fhash(root)))


def compact_record(record):
    return {
        "covered": bool(record["covered"]),
        "root_hash": record["root_hash"],
        "root_CLV": record["root_CLV"],
        "root_max_width": int(record["root_max_width"]),
        "provenance": record["provenance"],
        "candidate_probe_count": int(record["candidate_probe_count"]),
        "selected_step_count": len(record["selected_path"]),
        "selected_pivots": [int(x["var"]) for x in record["selected_path"]],
        "max_persisted_width": int(record["max_persisted_width"]),
        "old_CLV_rejected_selected_count": int(record["old_CLV_rejected_selected_count"]),
        "total_selected_RUP_checks": int(record.get("total_selected_RUP_checks", 0)),
        "terminal": record["terminal"],
        "obstruction": None if record["obstruction"] is None else {
            "kind": record["obstruction"]["kind"],
            "state_index": record["obstruction"].get("state_index"),
            "state_hash": record["obstruction"].get("state_hash"),
            "state_CLV": record["obstruction"].get("state_CLV"),
            "state_max_width": record["obstruction"].get("state_max_width"),
        },
    }


def run(start: int, end: int):
    if not (1 <= start <= end <= EXPECTED_ROOTS):
        raise AssertionError(("R49G_INVALID_SHARD", start, end))
    roots = collect_roots()
    records = []
    obstruction = None

    for idx in range(start, end + 1):
        root, provenance = roots[idx - 1]
        record = run_partial_root(root, {**provenance, "frozen_root_index": int(idx)})
        records.append(compact_record(record))
        if not record["covered"]:
            obstruction = record
            break

    covered = [x for x in records if x["covered"]]
    hardest = max(
        covered,
        key=lambda x: (int(x["candidate_probe_count"]), int(x["selected_step_count"]), tuple(x["root_CLV"]), x["root_hash"]),
        default=None,
    )
    return {
        "gate": GATE,
        "verdict": "EXPLICIT_PARTIAL_R47J_WIDTH4_ROOT_OBSTRUCTION_FOUND" if obstruction is not None else "PARTIAL_R47J_SHARD_COVERED__FINITE_ONLY",
        "shard": {"root_index_start": int(start), "root_index_end": int(end)},
        "metrics": {
            "roots_attempted": len(records),
            "covered_roots": len(covered),
            "obstruction_roots": sum(1 for x in records if not x["covered"]),
            "total_candidate_probes": sum(int(x["candidate_probe_count"]) for x in records),
            "total_selected_steps": sum(int(x["selected_step_count"]) for x in records),
            "total_old_CLV_rejected_selected_steps": sum(int(x["old_CLV_rejected_selected_count"]) for x in records),
            "total_selected_RUP_checks": sum(int(x["total_selected_RUP_checks"]) for x in records),
        },
        "hardest_covered_root": hardest,
        "first_obstruction": None if obstruction is None else compact_record(obstruction),
        "roots": records,
        "interpretation": {
            "finite_52root_regression_shard_only": True,
            "all_4_shards_green_proves_universal_partial_W4": False,
            "one_obstruction_refutes_only_partial_R47J_controller": True,
            "full_R48Q_R47M_controller_reference_covered_all_52": True,
        },
        "firewall": {
            "PARTIAL_R47J_WIDTH4_CONTROLLER_UNIVERSAL_COVERAGE": "NOT_PROVED_UNLESS_REFUTED_BY_THIS_GATE",
            "DIRECT_W4_STEP_COVERAGE": "OPEN",
            "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED",
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
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = run(a.start, a.end)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "shard": out["shard"],
        "metrics": out["metrics"],
        "hardest_covered_root": out["hardest_covered_root"],
        "first_obstruction": out["first_obstruction"],
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
