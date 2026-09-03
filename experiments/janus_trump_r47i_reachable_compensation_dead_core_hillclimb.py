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

Formula = Tuple[Tuple[int, ...], ...]

SEED = 473383
N = 30
RATIO = 3.8
EXPECTED_CLAUSES = 114
NEIGHBOR_SLOTS = EXPECTED_CLAUSES * 3
ROUND_SLOTS = 128
PERM_A = 73
PERM_B = 19
R47G_FIXPOINT_HASH = "3130377ee52a6d6abf01f44fdc5f1a96cf83d701e30f70debea26cd347b7a495"


def formula_hash(formula: Formula) -> str:
    payload = json.dumps([list(c) for c in r33.canonical_formula(formula)], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def frozen_slots() -> Tuple[int, ...]:
    slots = tuple((PERM_A * k + PERM_B) % NEIGHBOR_SLOTS for k in range(ROUND_SLOTS))
    if len(set(slots)) != ROUND_SLOTS:
        raise AssertionError("R47I_SLOT_PERMUTATION_COLLISION")
    return slots


def mutate_sign_flip(formula: Formula, slot: int) -> Optional[Formula]:
    base = r33.canonical_formula(formula)
    if len(base) != EXPECTED_CLAUSES or any(len(c) != 3 for c in base):
        raise AssertionError(("R47I_MUTATION_BASE_NOT_FROZEN_EXACT_3CNF", len(base)))
    ci, li = divmod(int(slot), 3)
    clause = list(base[ci])
    clause[li] = -clause[li]
    mutated_clauses = list(base)
    mutated_clauses[ci] = tuple(clause)
    mutated = r33.canonical_formula(mutated_clauses)
    if len(mutated) != len(base):
        return None
    if any(len(c) != 3 or r33.is_tautology(c) for c in mutated):
        return None
    return mutated


def first_certified_probe(core: Formula) -> dict:
    core = r33.canonical_formula(core)
    variable_order = tuple(int(v) for v in r33.variables(core))
    rejected = []
    candidate_count = 0
    for ordinal, var in enumerate(variable_order, 1):
        candidate = r45a.macro_candidate_for_var(core, var)
        if candidate is None:
            continue
        candidate_count += 1
        compact = {
            "ordinal": ordinal,
            "pivot": var,
            "accepted": bool(candidate["accepted"]),
            "terminal": candidate["normalization"].get("terminal"),
            "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
            "final_CLV": candidate["final_CLV"],
            "DP_independent_replay_pass": bool(candidate["DP_independent_replay"]["pass"]),
            "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope"]["pass"]),
        }
        if candidate["accepted"]:
            replay = r45a.independent_macro_replay(core, candidate)
            compact["macro_independent_replay_pass"] = bool(replay["pass"])
            if not replay["pass"]:
                raise AssertionError(("R47I_FIRST_ACCEPTED_REPLAY_FAIL", var, replay))
            return {
                "macro_dead": False,
                "first_accepted_ordinal": ordinal,
                "first_accepted_pivot": var,
                "rejected_before_first_accept": len(rejected),
                "candidate_count_to_first_accept": candidate_count,
                "first_accepted": compact,
                "rejected_prefix": rejected,
            }
        rejected.append(compact)

    # Potential scientific target: full independent accounting replay before sealing it.
    full_receipts = []
    for var in variable_order:
        receipt = r47h.pivot_receipt(core, var)
        if receipt is None:
            continue
        full_receipts.append(receipt)
    all_rejected = bool(full_receipts) and all(not bool(r["accepted"]) for r in full_receipts)
    all_replays = all(bool(r["DP_independent_replay_pass"] and r["macro_independent_replay_pass"] and r["polynomial_intermediate_envelope_pass"]) for r in full_receipts)
    all_debt_valid = all(r["debt_class"] in {"CLAUSE_DEBT", "LITERAL_DEBT"} for r in full_receipts)
    if not (all_rejected and all_replays and all_debt_valid):
        raise AssertionError(("R47I_MACRO_DEAD_SEAL_INTEGRITY_FAIL", all_rejected, all_replays, all_debt_valid))
    return {
        "macro_dead": True,
        "first_accepted_ordinal": None,
        "first_accepted_pivot": None,
        "rejected_before_first_accept": len(full_receipts),
        "candidate_count_to_first_accept": len(full_receipts),
        "first_accepted": None,
        "rejected_prefix": rejected,
        "full_counterexample_receipts": full_receipts,
    }


def evaluate_formula(original: Formula, mutation: dict) -> dict:
    original = r33.canonical_formula(original)
    reached = r47f.reachable_fixpoint(original)
    if reached is None:
        return {
            "mutation": mutation,
            "original_hash": formula_hash(original),
            "reachable_fixpoint": False,
            "macro_dead": False,
        }
    core = r33.canonical_formula(reached["formula"])
    integrity = r47h.genuine_fixpoint_integrity(core)
    if not integrity["pass"]:
        raise AssertionError(("R47I_REACHED_CORE_INTEGRITY_FAIL", mutation, integrity))
    probe = first_certified_probe(core)
    return {
        "mutation": mutation,
        "original_hash": formula_hash(original),
        "original_CLV": list(r33.measure(original)),
        "reachable_fixpoint": True,
        "trajectory": reached["trajectory"],
        "core_hash": r42.formula_hash(core),
        "core_CLV": list(r33.measure(core)),
        "genuine_fixpoint_integrity": integrity,
        **probe,
        "original_formula": [list(c) for c in original] if probe["macro_dead"] else None,
        "core_formula": [list(c) for c in core] if probe["macro_dead"] else None,
    }


def fitness_key(row: dict) -> tuple:
    if not row.get("reachable_fixpoint"):
        return (0, 0, 0)
    if row.get("macro_dead"):
        return (2, 10**9, 10**9)
    return (
        1,
        int(row.get("first_accepted_ordinal") or 0),
        int(row.get("rejected_before_first_accept") or 0),
    )


def choose_best(rows: Sequence[dict]) -> Optional[dict]:
    residual = [r for r in rows if r.get("reachable_fixpoint")]
    if not residual:
        return None
    # Maximize frozen fitness; stable final tie-break is lexicographically smallest residual hash.
    best_fitness = max(fitness_key(r) for r in residual)
    tied = [r for r in residual if fitness_key(r) == best_fitness]
    return min(tied, key=lambda r: str(r.get("core_hash", "")))


def build_mutations(base: Formula, round_id: int, avoid_hash: Optional[str] = None) -> List[Tuple[Formula, dict]]:
    out = []
    base_hash = formula_hash(base)
    for order, slot in enumerate(frozen_slots(), 1):
        mutated = mutate_sign_flip(base, slot)
        if mutated is None:
            continue
        mh = formula_hash(mutated)
        # Round 2 must not simply undo the round-1 move back to the original source.
        if avoid_hash is not None and mh == avoid_hash:
            continue
        out.append((mutated, {
            "round": int(round_id),
            "slot_order": int(order),
            "slot": int(slot),
            "base_hash": base_hash,
            "mutated_hash": mh,
        }))
    return out


def _worker(args):
    formula, mutation = args
    return evaluate_formula(formula, mutation)


def evaluate_batch(items: Sequence[Tuple[Formula, dict]], workers: int) -> List[dict]:
    if not items:
        return []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(_worker, items))
    rows.sort(key=lambda r: (int(r["mutation"]["slot_order"]), str(r["mutation"]["mutated_hash"])))
    return rows


def compact_row(row: Optional[dict]) -> Optional[dict]:
    if row is None:
        return None
    keep = {
        "mutation", "original_hash", "original_CLV", "reachable_fixpoint", "core_hash", "core_CLV",
        "macro_dead", "first_accepted_ordinal", "first_accepted_pivot", "rejected_before_first_accept",
        "candidate_count_to_first_accept", "first_accepted"
    }
    return {k: v for k, v in row.items() if k in keep}


def run(max_workers: Optional[int] = None) -> dict:
    source = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    source = r33.canonical_formula(source)
    if len(source) != EXPECTED_CLAUSES or any(len(c) != 3 for c in source):
        raise AssertionError(("R47I_SOURCE_DRIFT", len(source), r33.measure(source)))
    source_hash = formula_hash(source)
    baseline_reached = r47f.reachable_fixpoint(source)
    if baseline_reached is None:
        raise AssertionError("R47I_R47G_BASELINE_NO_LONGER_REACHES_FIXPOINT")
    baseline_core = r33.canonical_formula(baseline_reached["formula"])
    if r42.formula_hash(baseline_core) != R47G_FIXPOINT_HASH:
        raise AssertionError(("R47I_R47G_BASELINE_HASH_DRIFT", r42.formula_hash(baseline_core)))
    baseline_probe = first_certified_probe(baseline_core)
    if baseline_probe["macro_dead"] or int(baseline_probe["first_accepted_pivot"] or -1) != 7:
        raise AssertionError(("R47I_BASELINE_FIRST_ACCEPT_DRIFT", baseline_probe))

    workers = max_workers or min(4, max(1, os.cpu_count() or 1))
    round1_items = build_mutations(source, 1)
    round1 = evaluate_batch(round1_items, workers)
    target = next((r for r in round1 if r.get("macro_dead")), None)
    best1 = choose_best(round1)

    round2: List[dict] = []
    best2 = None
    if target is None and best1 is not None:
        best1_original = r33.canonical_formula(best1["original_formula"] if best1.get("original_formula") is not None else [])
        if not best1_original:
            # Covered survivors intentionally omit full formula; deterministically rebuild it from source + stored round-1 slot.
            rebuilt = mutate_sign_flip(source, int(best1["mutation"]["slot"]))
            if rebuilt is None or formula_hash(rebuilt) != best1["original_hash"]:
                raise AssertionError("R47I_BEST1_REBUILD_FAIL")
            best1_original = rebuilt
        round2_items = build_mutations(best1_original, 2, avoid_hash=source_hash)
        round2 = evaluate_batch(round2_items, workers)
        target = next((r for r in round2 if r.get("macro_dead")), None)
        best2 = choose_best(round2)

    all_rows = round1 + round2
    best = target or choose_best(all_rows)
    if target is not None:
        verdict = "EXPLICIT_REACHABLE_CURRENT_MACRO_COVERAGE_COUNTEREXAMPLE_FOUND"
    else:
        verdict = "NO_MACRO_DEAD_CORE_IN_FROZEN_LOCAL_SEARCH__BEST_REACHABLE_SURVIVOR_PRESERVED__O4_OPEN"

    counters = {
        "round1_mutations_evaluated": len(round1),
        "round1_reachable_fixpoints": sum(bool(r.get("reachable_fixpoint")) for r in round1),
        "round1_macro_dead": sum(bool(r.get("macro_dead")) for r in round1),
        "round2_mutations_evaluated": len(round2),
        "round2_reachable_fixpoints": sum(bool(r.get("reachable_fixpoint")) for r in round2),
        "round2_macro_dead": sum(bool(r.get("macro_dead")) for r in round2),
        "total_evaluated": len(all_rows),
        "total_reachable_fixpoints": sum(bool(r.get("reachable_fixpoint")) for r in all_rows),
        "total_macro_dead": sum(bool(r.get("macro_dead")) for r in all_rows),
    }

    # Preserve full payload only for the scientific target; covered survivors are reproducible by mutation slots.
    counterexample = None
    if target is not None:
        counterexample = {
            "mutation": target["mutation"],
            "original_hash": target["original_hash"],
            "original_CLV": target["original_CLV"],
            "original_formula": target["original_formula"],
            "core_hash": target["core_hash"],
            "core_CLV": target["core_CLV"],
            "core_formula": target["core_formula"],
            "trajectory": target["trajectory"],
            "full_counterexample_receipts": target["full_counterexample_receipts"],
        }

    return {
        "schema": "JANUS_TRUMP_R47I_REACHABLE_COMPENSATION_DEAD_CORE_HILLCLIMB_RESULT",
        "version": "1.0",
        "date": "2026-09-03",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNCOMMITTED"),
        "gate": "JANUS_TRUMP_R47I_REACHABLE_COMPENSATION_DEAD_CORE_HILLCLIMB",
        "verdict": verdict,
        "baseline": {
            "seed": SEED,
            "n": N,
            "ratio": RATIO,
            "source_hash": source_hash,
            "fixpoint_hash": r42.formula_hash(baseline_core),
            "fixpoint_CLV": list(r33.measure(baseline_core)),
            "first_accepted_ordinal": baseline_probe["first_accepted_ordinal"],
            "first_accepted_pivot": baseline_probe["first_accepted_pivot"],
        },
        "search_contract": {
            "neighbor_slots": NEIGHBOR_SLOTS,
            "slot_permutation": "(73*k+19) mod 342",
            "round_slots": ROUND_SLOTS,
            "workers": workers,
            "workers_are_proof_authority": False,
        },
        "counters": counters,
        "best_round1": compact_row(best1),
        "best_round2": compact_row(best2),
        "best_overall": compact_row(best),
        "counterexample": counterexample,
        "rows_digest_sha256": hashlib.sha256(json.dumps([
            compact_row(r) for r in all_rows
        ], sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "interpretation": {
            "finite_search_only": True,
            "universal_theorem_elevation_allowed": False,
            "macro_dead_if_found_refutes_current_frozen_grammar_on_that_reachable_state": True,
        },
        "epistemic_firewall": {
            "FINITE_SEARCH_IMPLIES_O4": False,
            "CURRENT_GRAMMAR_COUNTEREXAMPLE_IMPLIES_P_NE_NP": False,
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def self_test() -> None:
    slots = frozen_slots()
    assert len(slots) == ROUND_SLOTS and len(set(slots)) == ROUND_SLOTS
    source = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    assert len(source) == EXPECTED_CLAUSES
    m = mutate_sign_flip(source, slots[0])
    assert m is None or (len(m) == EXPECTED_CLAUSES and all(len(c) == 3 for c in m))
    fake = [
        {"reachable_fixpoint": True, "macro_dead": False, "first_accepted_ordinal": 5, "rejected_before_first_accept": 4, "core_hash": "b"},
        {"reachable_fixpoint": True, "macro_dead": False, "first_accepted_ordinal": 7, "rejected_before_first_accept": 6, "core_hash": "c"},
        {"reachable_fixpoint": True, "macro_dead": False, "first_accepted_ordinal": 7, "rejected_before_first_accept": 6, "core_hash": "a"},
    ]
    assert choose_best(fake)["core_hash"] == "a"
    print("R47I_SELF_TEST_PASS")


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
    compact = {
        "gate": result["gate"],
        "verdict": result["verdict"],
        "baseline": result["baseline"],
        "counters": result["counters"],
        "best_round1": result["best_round1"],
        "best_round2": result["best_round2"],
        "best_overall": result["best_overall"],
        "counterexample_found": result["counterexample"] is not None,
        "epistemic_firewall": result["epistemic_firewall"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
