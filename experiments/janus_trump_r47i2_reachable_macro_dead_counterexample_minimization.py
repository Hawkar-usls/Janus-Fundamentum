from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47h_27_core_compensation_ledger as r47h
import janus_trump_r47i_reachable_compensation_dead_core_hillclimb as r47i

Formula = Tuple[Tuple[int, ...], ...]

SEED = 473383
N = 30
RATIO = 3.8
MUTATION_SLOT = 115
EXPECTED_PARENT_HASH = "b39e9f1e479f17f3efb24fe0eb44a7c1a93f0db8eab606b936734f74eafb9e34"
EXPECTED_PARENT_CORE_HASH = "485fbea627110fc5ff0876072245f66661dfe8d306fc25735657038b8e62eeea"
EXPECTED_PARENT_SOURCE_CLV = (114, 342, 30)
EXPECTED_PARENT_CORE_CLV = (89, 245, 26)
BLOCK_SIZES = (16, 8, 4, 2, 1)
MAX_PROPERTY_EVALUATIONS = 1200


def canonical_hash(formula: Formula) -> str:
    f = r33.canonical_formula(formula)
    return hashlib.sha256(json.dumps([list(c) for c in f], separators=(",", ":")).encode("utf-8")).hexdigest()


def clv(formula: Formula) -> Tuple[int, int, int]:
    return tuple(int(x) for x in r33.measure(r33.canonical_formula(formula)))


def exact3cnf_integrity(formula: Formula) -> bool:
    f = r33.canonical_formula(formula)
    return bool(f) and all(len(c) == 3 and not r33.is_tautology(c) for c in f)


def reconstruct_parent_source() -> Formula:
    base = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    mutated = r47i.mutate_sign_flip(base, MUTATION_SLOT)
    if mutated is None:
        raise AssertionError("R47I2_PARENT_MUTATION_NO_LONGER_VALID")
    mutated = r33.canonical_formula(mutated)
    if canonical_hash(mutated) != EXPECTED_PARENT_HASH:
        raise AssertionError(("R47I2_PARENT_HASH_DRIFT", canonical_hash(mutated), EXPECTED_PARENT_HASH))
    if clv(mutated) != EXPECTED_PARENT_SOURCE_CLV:
        raise AssertionError(("R47I2_PARENT_CLV_DRIFT", clv(mutated), EXPECTED_PARENT_SOURCE_CLV))
    return mutated


def macro_dead_check(core: Formula, preserve_full_receipts: bool = False) -> dict:
    core = r33.canonical_formula(core)
    variable_order = tuple(int(v) for v in r33.variables(core))
    receipts = []
    candidate_count = 0
    for var in variable_order:
        candidate = r45a.macro_candidate_for_var(core, var)
        if candidate is None:
            continue
        candidate_count += 1
        replay = r45a.independent_macro_replay(core, candidate)
        if not replay["pass"]:
            raise AssertionError(("R47I2_MACRO_REPLAY_FAIL", var, replay))
        if not candidate["DP_independent_replay"]["pass"]:
            raise AssertionError(("R47I2_DP_REPLAY_FAIL", var))
        if not candidate["polynomial_intermediate_envelope"]["pass"]:
            raise AssertionError(("R47I2_POLY_ENVELOPE_FAIL", var))
        if candidate["accepted"]:
            return {
                "macro_dead": False,
                "candidate_count": candidate_count,
                "first_accepted_pivot": int(var),
                "first_accepted_terminal": candidate["normalization"].get("terminal"),
                "first_accepted_final_CLV": candidate["final_CLV"],
            }
        if preserve_full_receipts:
            receipt = r47h.pivot_receipt(core, var)
            if receipt is None:
                raise AssertionError(("R47I2_EXPECTED_RECEIPT_MISSING", var))
            receipts.append(receipt)
    if candidate_count == 0:
        raise AssertionError("R47I2_NO_BIPOLAR_MACRO_CANDIDATES")
    return {
        "macro_dead": True,
        "candidate_count": candidate_count,
        "first_accepted_pivot": None,
        "full_receipts": receipts if preserve_full_receipts else None,
    }


def property_check(source: Formula, preserve_full: bool = False) -> dict:
    source = r33.canonical_formula(source)
    result = {
        "source_hash": canonical_hash(source),
        "source_CLV": list(clv(source)),
        "source_clause_count": len(source),
        "exact3cnf_integrity": exact3cnf_integrity(source),
        "preserves": False,
        "failure_stage": None,
    }
    if not result["exact3cnf_integrity"]:
        result["failure_stage"] = "NOT_EXACT_3CNF"
        return result

    reached = r47f.reachable_fixpoint(source)
    if reached is None:
        result["failure_stage"] = "NO_GENUINE_R42_FIXPOINT"
        return result
    core = r33.canonical_formula(reached["formula"])
    integrity = r47h.genuine_fixpoint_integrity(core)
    if not integrity["pass"]:
        raise AssertionError(("R47I2_REACHED_CORE_INTEGRITY_FAIL", result["source_hash"], integrity))
    probe = macro_dead_check(core, preserve_full_receipts=preserve_full)
    result.update({
        "core_hash": r42.formula_hash(core),
        "core_CLV": list(clv(core)),
        "genuine_fixpoint_integrity": integrity,
        "macro_dead": bool(probe["macro_dead"]),
        "candidate_count": int(probe["candidate_count"]),
        "first_accepted_pivot": probe.get("first_accepted_pivot"),
    })
    if not probe["macro_dead"]:
        result["failure_stage"] = "CURRENT_R45A_COVERED"
        result["first_accepted_terminal"] = probe.get("first_accepted_terminal")
        result["first_accepted_final_CLV"] = probe.get("first_accepted_final_CLV")
        return result

    result["preserves"] = True
    result["failure_stage"] = None
    if preserve_full:
        result["source_formula"] = [list(c) for c in source]
        result["core_formula"] = [list(c) for c in core]
        result["trajectory"] = reached["trajectory"]
        result["full_counterexample_receipts"] = probe["full_receipts"]
    return result


def delete_block(source: Formula, start: int, size: int) -> Formula:
    source = r33.canonical_formula(source)
    end = min(len(source), int(start) + int(size))
    return r33.canonical_formula(source[:start] + source[end:])


def _worker(task):
    source, start, size = task
    candidate = delete_block(source, start, size)
    row = property_check(candidate, preserve_full=False)
    row.update({
        "delete_start": int(start),
        "delete_size_requested": int(size),
        "delete_size_actual": min(int(size), len(source) - int(start)),
    })
    return row


def evaluate_deletion_round(source: Formula, size: int, remaining_budget: int, workers: int) -> Tuple[List[dict], bool]:
    source = r33.canonical_formula(source)
    starts = list(range(0, len(source)))
    # Deduplicate truncating tail blocks by their exact deleted index range.
    seen = set()
    unique_starts = []
    for start in starts:
        key = (start, min(len(source), start + size))
        if key in seen:
            continue
        seen.add(key)
        unique_starts.append(start)
    if len(unique_starts) > remaining_budget:
        return [], True
    tasks = [(source, start, size) for start in unique_starts]
    if not tasks:
        return [], False
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(_worker, tasks))
    rows.sort(key=lambda r: (int(r["delete_start"]), str(r["source_hash"])))
    return rows, False


def choose_preserving(rows: Sequence[dict]) -> Optional[dict]:
    good = [r for r in rows if r.get("preserves")]
    if not good:
        return None
    return min(good, key=lambda r: str(r["source_hash"]))


def result_digest(rows: Sequence[dict]) -> str:
    compact = [
        {
            "source_hash": r["source_hash"],
            "delete_start": r["delete_start"],
            "delete_size_requested": r["delete_size_requested"],
            "delete_size_actual": r["delete_size_actual"],
            "preserves": bool(r["preserves"]),
            "failure_stage": r.get("failure_stage"),
            "core_hash": r.get("core_hash"),
            "core_CLV": r.get("core_CLV"),
            "first_accepted_pivot": r.get("first_accepted_pivot"),
        }
        for r in rows
    ]
    return hashlib.sha256(json.dumps(compact, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def run(max_workers: Optional[int] = None) -> dict:
    source = reconstruct_parent_source()
    parent = property_check(source, preserve_full=False)
    if not parent["preserves"]:
        raise AssertionError(("R47I2_PARENT_NO_LONGER_PRESERVES", parent))
    if parent["core_hash"] != EXPECTED_PARENT_CORE_HASH or tuple(parent["core_CLV"]) != EXPECTED_PARENT_CORE_CLV:
        raise AssertionError(("R47I2_PARENT_CORE_DRIFT", parent["core_hash"], parent["core_CLV"]))

    workers = max_workers or min(4, max(1, os.cpu_count() or 1))
    evaluations = 1  # parent property replay
    current = source
    accepted_deletions: List[dict] = []
    round_receipts: List[dict] = []
    resource_limit = False

    for size in BLOCK_SIZES:
        while True:
            remaining = MAX_PROPERTY_EVALUATIONS - evaluations
            rows, budget_blocked = evaluate_deletion_round(current, size, remaining, workers)
            if budget_blocked:
                resource_limit = True
                round_receipts.append({
                    "block_size": size,
                    "source_hash_before": canonical_hash(current),
                    "source_clause_count_before": len(current),
                    "status": "RESOURCE_BUDGET_INSUFFICIENT_FOR_COMPLETE_ROUND",
                    "remaining_budget": remaining,
                    "required_evaluations": len(current),
                })
                break
            evaluations += len(rows)
            chosen = choose_preserving(rows)
            round_receipts.append({
                "block_size": size,
                "source_hash_before": canonical_hash(current),
                "source_clause_count_before": len(current),
                "tested_deletions": len(rows),
                "preserving_deletions": sum(bool(r["preserves"]) for r in rows),
                "tested_digest_sha256": result_digest(rows),
                "chosen_source_hash": None if chosen is None else chosen["source_hash"],
                "chosen_delete_start": None if chosen is None else chosen["delete_start"],
                "chosen_delete_size_actual": None if chosen is None else chosen["delete_size_actual"],
                "status": "NO_PRESERVING_DELETION" if chosen is None else "PRESERVING_DELETION_ACCEPTED",
            })
            if chosen is None:
                break
            before = current
            current = delete_block(current, int(chosen["delete_start"]), int(chosen["delete_size_actual"]))
            if canonical_hash(current) != chosen["source_hash"]:
                raise AssertionError("R47I2_CHOSEN_REPLAY_HASH_FAIL")
            accepted_deletions.append({
                "block_size_stage": size,
                "delete_start": int(chosen["delete_start"]),
                "delete_size": int(chosen["delete_size_actual"]),
                "source_hash_before": canonical_hash(before),
                "source_CLV_before": list(clv(before)),
                "source_hash_after": canonical_hash(current),
                "source_CLV_after": list(clv(current)),
                "reachable_core_hash_after": chosen["core_hash"],
                "reachable_core_CLV_after": chosen["core_CLV"],
            })
        if resource_limit:
            break

    final_full = property_check(current, preserve_full=True)
    evaluations += 1
    if not final_full["preserves"]:
        raise AssertionError(("R47I2_FINAL_PROPERTY_LOST", final_full))

    final_single_rows: List[dict] = []
    single_clause_1minimal = False
    if not resource_limit:
        remaining = MAX_PROPERTY_EVALUATIONS - evaluations
        if len(current) <= remaining:
            final_single_rows, budget_blocked = evaluate_deletion_round(current, 1, remaining, workers)
            if budget_blocked:
                resource_limit = True
            else:
                evaluations += len(final_single_rows)
                single_clause_1minimal = all(not bool(r["preserves"]) for r in final_single_rows)
                # The size=1 minimizer should already have reached a no-preserving-deletion round.
                if not single_clause_1minimal:
                    raise AssertionError("R47I2_FINAL_SINGLE_PASS_FOUND_UNAPPLIED_PRESERVING_DELETION")
        else:
            resource_limit = True

    if resource_limit:
        verdict = "REACHABLE_MACRO_DEAD_COUNTEREXAMPLE_REDUCED_BUT_NOT_1MINIMAL_WITHIN_RESOURCE_BUDGET" if len(current) < len(source) else "MINIMIZATION_RESOURCE_LIMIT__PARENT_COUNTEREXAMPLE_REMAINS_SEALED"
    elif single_clause_1minimal:
        verdict = "REACHABLE_MACRO_DEAD_COUNTEREXAMPLE_MINIMIZED_AND_SINGLE_CLAUSE_1MINIMAL"
    else:
        verdict = "REACHABLE_MACRO_DEAD_COUNTEREXAMPLE_REDUCED_BUT_NOT_1MINIMAL_WITHIN_RESOURCE_BUDGET"

    out = {
        "schema": "JANUS_TRUMP_R47I2_REACHABLE_MACRO_DEAD_COUNTEREXAMPLE_MINIMIZATION_RESULT",
        "version": "1.0",
        "date": "2026-09-03",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNCOMMITTED"),
        "gate": "JANUS_TRUMP_R47I2_REACHABLE_MACRO_DEAD_COUNTEREXAMPLE_MINIMIZATION",
        "verdict": verdict,
        "resource": {
            "max_property_evaluations": MAX_PROPERTY_EVALUATIONS,
            "property_evaluations_used": evaluations,
            "workers": workers,
            "parallel_scheduling_is_proof_authority": False,
            "resource_limit_hit": resource_limit,
        },
        "parent": {
            "source_hash": canonical_hash(source),
            "source_CLV": list(clv(source)),
            "core_hash": parent["core_hash"],
            "core_CLV": parent["core_CLV"],
        },
        "minimized": {
            "source_hash": final_full["source_hash"],
            "source_CLV": final_full["source_CLV"],
            "source_formula": final_full["source_formula"],
            "core_hash": final_full["core_hash"],
            "core_CLV": final_full["core_CLV"],
            "core_formula": final_full["core_formula"],
            "trajectory": final_full["trajectory"],
            "full_counterexample_receipts": final_full["full_counterexample_receipts"],
            "candidate_count": final_full["candidate_count"],
            "single_clause_1minimal": single_clause_1minimal,
        },
        "accepted_deletions": accepted_deletions,
        "round_receipts": round_receipts,
        "final_single_clause_tests": [
            {
                "delete_start": r["delete_start"],
                "candidate_source_hash": r["source_hash"],
                "preserves": bool(r["preserves"]),
                "failure_stage": r.get("failure_stage"),
                "core_hash": r.get("core_hash"),
                "core_CLV": r.get("core_CLV"),
                "first_accepted_pivot": r.get("first_accepted_pivot"),
            }
            for r in final_single_rows
        ],
        "final_single_clause_tests_digest_sha256": result_digest(final_single_rows) if final_single_rows else None,
        "interpretation": {
            "current_frozen_R45A_coverage_already_refuted_by_parent": True,
            "minimization_changes_that_scientific_scope": False,
            "single_clause_1minimal_means_global_minimum": False,
            "purpose": "Expose the smallest local clause-deletion structure we can seal before proposing an extended macro."
        },
        "epistemic_firewall": {
            "CURRENT_FROZEN_R45A_O4": "REFUTED_BY_REACHABLE_COUNTEREXAMPLE",
            "FUTURE_EXTENDED_GRAMMAR_O4": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    return out


def self_test() -> None:
    parent = reconstruct_parent_source()
    assert len(parent) == 114 and exact3cnf_integrity(parent)
    toy = r33.canonical_formula([(1,2,3),(1,-2,4),(-1,3,4),(2,3,-4)])
    assert len(delete_block(toy, 1, 2)) == 2
    print("R47I2_SELF_TEST_PASS", {"parent_hash": canonical_hash(parent), "parent_CLV": list(clv(parent))})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-workers", type=int)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = run(max_workers=args.max_workers)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "resource": result["resource"],
        "parent": result["parent"],
        "minimized": {
            "source_hash": result["minimized"]["source_hash"],
            "source_CLV": result["minimized"]["source_CLV"],
            "core_hash": result["minimized"]["core_hash"],
            "core_CLV": result["minimized"]["core_CLV"],
            "candidate_count": result["minimized"]["candidate_count"],
            "single_clause_1minimal": result["minimized"]["single_clause_1minimal"],
        },
        "accepted_deletion_count": len(result["accepted_deletions"]),
        "firewall": result["epistemic_firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
