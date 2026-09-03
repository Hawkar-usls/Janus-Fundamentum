from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
from collections import defaultdict, deque
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r45b_frozen_26_stall_quotient_macro_coverage as r45b

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]
PARENT_R45B = "08f879bd2e20fbd98aae85f0da27314a877373d9"


def lit_key(lit: int) -> Tuple[int, int]:
    return (abs(int(lit)), 0 if int(lit) > 0 else 1)


def formula_hash(formula: Formula) -> str:
    return r42.formula_hash(r33.canonical_formula(formula))


def watched_unit_propagation_trace(formula: Formula, assumptions: Iterable[int]) -> dict:
    """Deterministic two-watched-literal UP producer.

    The watch structure is query-local in R46A.  This deliberately isolates the
    semantic drop-in test from the later incremental-state optimization.
    """
    clauses = r33.canonical_formula(formula)
    assignment: Dict[int, bool] = {}
    trail: List[dict] = []
    queue = deque()
    metrics = {
        "watch_build_literal_inspections": 0,
        "watch_clause_touches": 0,
        "watch_replacement_literal_inspections": 0,
        "watch_moves": 0,
        "queue_pops": 0,
    }

    def lit_state(lit: int) -> int:
        v = abs(lit)
        if v not in assignment:
            return 0
        return 1 if assignment[v] == (lit > 0) else -1

    def enqueue(lit: int, reason) -> Optional[str]:
        v, val = abs(int(lit)), int(lit) > 0
        if v in assignment:
            return None if assignment[v] == val else "ASSIGNMENT_CONTRADICTION"
        assignment[v] = val
        trail.append({"literal": int(lit), "reason": reason})
        queue.append(int(lit))
        return None

    for lit in assumptions:
        if enqueue(int(lit), "ASSUMPTION") is not None:
            return {"conflict": True, "conflict_kind": "ASSUMPTION_CONTRADICTION", "conflict_clause": None,
                    "trail": trail, **metrics}

    watch_pos: List[List[int]] = []
    buckets: Dict[int, List[int]] = defaultdict(list)
    units: List[Tuple[int, Clause]] = []
    for cid, clause in enumerate(clauses):
        metrics["watch_build_literal_inspections"] += len(clause)
        if len(clause) == 0:
            return {"conflict": True, "conflict_kind": "EMPTY_CLAUSE", "conflict_clause": [],
                    "trail": trail, **metrics}
        if len(clause) == 1:
            watch_pos.append([0])
            buckets[clause[0]].append(cid)
            units.append((clause[0], clause))
        else:
            watch_pos.append([0, 1])
            buckets[clause[0]].append(cid)
            buckets[clause[1]].append(cid)

    for lit, clause in sorted(units, key=lambda x: lit_key(x[0])):
        if enqueue(lit, list(clause)) is not None:
            return {"conflict": True, "conflict_kind": "UNIT_ASSIGNMENT_CONTRADICTION",
                    "conflict_clause": list(clause), "trail": trail, **metrics}

    while queue:
        assigned_lit = queue.popleft()
        metrics["queue_pops"] += 1
        false_lit = -assigned_lit
        watching = buckets.get(false_lit, [])
        i = 0
        while i < len(watching):
            cid = watching[i]
            clause = clauses[cid]
            metrics["watch_clause_touches"] += 1
            pos = watch_pos[cid]
            if len(pos) == 1:
                if lit_state(clause[pos[0]]) == -1:
                    return {"conflict": True, "conflict_kind": "EMPTY_RESIDUAL_CLAUSE",
                            "conflict_clause": list(clause), "trail": trail, **metrics}
                i += 1
                continue

            if clause[pos[0]] == false_lit:
                false_slot, other_slot = 0, 1
            elif clause[pos[1]] == false_lit:
                false_slot, other_slot = 1, 0
            else:
                # Stale bucket entry is never semantically authoritative.
                watching.pop(i)
                continue

            other_pos = pos[other_slot]
            other_lit = clause[other_pos]
            if lit_state(other_lit) == 1:
                i += 1
                continue

            replacement = None
            for j, candidate in enumerate(clause):
                if j == pos[0] or j == pos[1]:
                    continue
                metrics["watch_replacement_literal_inspections"] += 1
                if lit_state(candidate) != -1:
                    replacement = j
                    break

            if replacement is not None:
                new_lit = clause[replacement]
                pos[false_slot] = replacement
                watching.pop(i)
                buckets[new_lit].append(cid)
                metrics["watch_moves"] += 1
                continue

            state = lit_state(other_lit)
            if state == -1:
                return {"conflict": True, "conflict_kind": "EMPTY_RESIDUAL_CLAUSE",
                        "conflict_clause": list(clause), "trail": trail, **metrics}
            if state == 0:
                if enqueue(other_lit, list(clause)) is not None:
                    return {"conflict": True, "conflict_kind": "UNIT_ASSIGNMENT_CONTRADICTION",
                            "conflict_clause": list(clause), "trail": trail, **metrics}
            i += 1

    return {"conflict": False, "conflict_kind": None, "conflict_clause": None,
            "trail": trail, "assignment_count": len(assignment), **metrics}


def first_watched_rup_strengthening(formula: Formula) -> Tuple[Optional[dict], dict]:
    ledger = defaultdict(int)
    checks = 0
    for clause in formula:
        if not clause:
            continue
        for removed_literal in sorted(clause, key=lit_key):
            strengthened = tuple(l for l in clause if l != removed_literal)
            assumptions = tuple(-l for l in sorted(strengthened, key=lit_key))
            receipt = watched_unit_propagation_trace(formula, assumptions)
            checks += 1
            for key in ("watch_build_literal_inspections", "watch_clause_touches",
                        "watch_replacement_literal_inspections", "watch_moves", "queue_pops"):
                ledger[key] += int(receipt[key])
            if receipt["conflict"]:
                return {
                    "source_clause": clause,
                    "removed_literal": removed_literal,
                    "strengthened_clause": strengthened,
                    "assumptions": assumptions,
                    "up_receipt": receipt,
                }, {"rup_checks": checks, **dict(ledger)}
    return None, {"rup_checks": checks, **dict(ledger)}


def run_candidate_watched(initial_formula: Formula) -> dict:
    formula = r33.canonical_formula(initial_formula)
    initial_measure = r35b.formula_measure(formula)
    history: List[dict] = []
    ledger = defaultdict(int)

    def meter(receipt: dict) -> None:
        for key in ("watch_build_literal_inspections", "watch_clause_touches",
                    "watch_replacement_literal_inspections", "watch_moves", "queue_pops"):
            ledger[key] += int(receipt[key])

    initial_up = watched_unit_propagation_trace(formula, ())
    meter(initial_up)
    if initial_up["conflict"]:
        return {"status": "UNSAT_BY_UNIT_PROPAGATION", "initial_measure": list(initial_measure),
                "final_measure": list(r35b.formula_measure(formula)), "history": history,
                "final_up_receipt": initial_up, "ledger": dict(ledger),
                "successful_strengthenings": 0, "final_formula": [list(c) for c in formula]}

    max_successes = initial_measure[0]
    for step in range(max_successes + 1):
        if step == max_successes and len(history) == max_successes:
            raise AssertionError("R46A_STRENGTHENING_BOUND_EXHAUSTED")
        proposal, scan = first_watched_rup_strengthening(formula)
        for key, value in scan.items():
            ledger[key] += int(value)
        if proposal is None:
            final_up = watched_unit_propagation_trace(formula, ())
            meter(final_up)
            return {"status": "UNSAT_BY_UNIT_PROPAGATION" if final_up["conflict"] else "STALLED_RUP_CORE",
                    "initial_measure": list(initial_measure), "final_measure": list(r35b.formula_measure(formula)),
                    "history": history, "final_up_receipt": final_up, "ledger": dict(ledger),
                    "successful_strengthenings": len(history), "final_formula": [list(c) for c in formula]}

        source = proposal["source_clause"]
        strengthened = proposal["strengthened_clause"]
        before_hash = formula_hash(formula)
        before_measure = r35b.formula_measure(formula)
        updated = r35b.replace_clause_with_subclause(formula, source, strengthened)
        after_measure = r35b.formula_measure(updated)
        if not after_measure < before_measure:
            raise AssertionError("R46A_PROGRESS_MEASURE_FAIL")
        history.append({
            "step": len(history) + 1,
            "formula_hash_before": before_hash,
            "source_clause": list(source),
            "removed_literal": int(proposal["removed_literal"]),
            "strengthened_clause": list(strengthened),
            "assumptions": list(proposal["assumptions"]),
            "up_receipt": proposal["up_receipt"],
            "measure_before": list(before_measure),
            "measure_after": list(after_measure),
            "formula_hash_after": formula_hash(updated),
        })
        formula = updated
        final_up = watched_unit_propagation_trace(formula, ())
        meter(final_up)
        if final_up["conflict"]:
            return {"status": "UNSAT_BY_UNIT_PROPAGATION", "initial_measure": list(initial_measure),
                    "final_measure": list(r35b.formula_measure(formula)), "history": history,
                    "final_up_receipt": final_up, "ledger": dict(ledger),
                    "successful_strengthenings": len(history), "final_formula": [list(c) for c in formula]}
    raise AssertionError("R46A_UNREACHABLE")


def normalized(candidate: dict) -> dict:
    steps = [{k: row[k] for k in ("source_clause", "removed_literal", "strengthened_clause", "assumptions")}
             for row in candidate["history"]]
    return {
        "status": candidate["status"],
        "final_formula_hash": formula_hash(r33.canonical_formula(candidate["final_formula"])),
        "successful_strengthenings": int(candidate["successful_strengthenings"]),
        "steps": steps,
        "final_conflict": bool(candidate["final_up_receipt"]["conflict"]),
    }


def compare_formula(formula: Formula) -> dict:
    legacy = r35b.run_candidate(formula)
    watched = run_candidate_watched(formula)
    legacy_n, watched_n = normalized(legacy), normalized(watched)
    replay = r35b.independent_certificate_replay(formula, watched)
    return {
        "pass": legacy_n == watched_n and bool(replay["pass"]),
        "semantic_equal": legacy_n == watched_n,
        "independent_replay_pass": bool(replay["pass"]),
        "legacy": legacy_n,
        "watched": watched_n,
        "legacy_ledger": legacy["ledger"],
        "watched_ledger": watched["ledger"],
    }


def rup_eligible_post_dp(stall: Formula) -> Sequence[Tuple[int, Formula]]:
    out = []
    for var in r33.variables(stall):
        dp = r45a.exact_dp_record(stall, int(var))
        if dp is None:
            continue
        forced = r33.canonical_formula(dp["transformed"])
        reduced = r33.simplify(forced)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            continue
        if r34.recognize_complete_affine_cnf(after_r33)["recognized"]:
            continue
        out.append((int(var), after_r33))
    return out


def audit_seed(seed: int) -> dict:
    label, source = r45b.frozen_case_map()[int(seed)]
    _, stall = r45b.replay_r42_terminal_formula(source, label)
    direct = compare_formula(stall)
    generated = []
    for var, formula in rup_eligible_post_dp(stall):
        cmp = compare_formula(formula)
        generated.append({"var": var, "formula_hash": formula_hash(formula), "pass": cmp["pass"],
                          "semantic_equal": cmp["semantic_equal"],
                          "independent_replay_pass": cmp["independent_replay_pass"],
                          "legacy_ledger": cmp["legacy_ledger"], "watched_ledger": cmp["watched_ledger"]})
    return {"seed": int(seed), "stall_hash": formula_hash(stall), "direct": direct, "generated": generated,
            "pass": direct["pass"] and all(x["pass"] for x in generated)}


def microtests() -> dict:
    cases = {
        "EMPTY": (r33.canonical_formula([()]), ()),
        "UNIT_CHAIN": (r33.canonical_formula([(1,), (-1, 2), (-2, 3)]), ()),
        "ASSUMPTION_CONTRADICTION": (r33.canonical_formula([(1, 2)]), (1, -1)),
        "NO_CONFLICT": (r33.canonical_formula([(1, 2), (-1, 3)]), ()),
        "WATCH_REPLACEMENT": (r33.canonical_formula([(1, 2, 3), (-1,), (-2,)]), ()),
        "LONG_CHAIN": (r33.canonical_formula([(1,), (-1, 2), (-2, 3), (-3, 4), (-4, 5), (-5,)]), ()),
    }
    out = {}
    for name, (formula, assumptions) in cases.items():
        watched = watched_unit_propagation_trace(formula, assumptions)
        independent = r35b.independent_up_conflict_checker(formula, assumptions)
        out[name] = {"pass": bool(watched["conflict"]) == bool(independent),
                     "watched_conflict": bool(watched["conflict"]), "independent_conflict": bool(independent)}
    return out


def sum_ledgers(rows: Sequence[dict]) -> dict:
    legacy, watched = defaultdict(int), defaultdict(int)
    def add(cmp):
        for k, v in cmp["legacy_ledger"].items(): legacy[k] += int(v)
        for k, v in cmp["watched_ledger"].items(): watched[k] += int(v)
    for row in rows:
        add(row["direct"])
        for item in row["generated"]:
            for k, v in item["legacy_ledger"].items(): legacy[k] += int(v)
            for k, v in item["watched_ledger"].items(): watched[k] += int(v)
    return {"legacy": dict(sorted(legacy.items())), "watched": dict(sorted(watched.items()))}


def run_audit(max_workers: Optional[int] = None) -> dict:
    micro = microtests()
    workers = max_workers or min(4, max(1, os.cpu_count() or 1), len(r45b.FROZEN_STALL_SEEDS))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(audit_seed, r45b.FROZEN_STALL_SEEDS))
    rows.sort(key=lambda x: x["seed"])
    generated_count = sum(len(r["generated"]) for r in rows)
    mismatches = sum(0 if r["direct"]["semantic_equal"] else 1 for r in rows)
    mismatches += sum(0 if x["semantic_equal"] else 1 for r in rows for x in r["generated"])
    replay_failures = sum(0 if r["direct"]["independent_replay_pass"] else 1 for r in rows)
    replay_failures += sum(0 if x["independent_replay_pass"] else 1 for r in rows for x in r["generated"])
    passed = mismatches == 0 and replay_failures == 0 and all(x["pass"] for x in micro.values()) and all(r["pass"] for r in rows)
    return {
        "schema": "JANUS_TRUMP_R46A_WATCHED_RUP_DROPIN_SEMANTIC_EQUIVALENCE_RESULT",
        "parent_R45B_commit": PARENT_R45B,
        "frozen_stall_count": len(rows),
        "generated_RUP_eligible_candidate_formula_count": generated_count,
        "semantic_mismatch_count": mismatches,
        "independent_replay_failure_count": replay_failures,
        "microtests": micro,
        "resource_ledger": sum_ledgers(rows),
        "rows": rows,
        "status": {
            "R46A_WATCHED_RUP_DROPIN_SEMANTIC_EQUIVALENCE": passed,
            "FAST_PRODUCER_SIMPLE_INDEPENDENT_VERIFIER": passed,
            "FIRST_CERTIFIED_DESCENT_PROVEN": False,
            "JANUS_RANKER_AUTHORITY": False,
            "INCREMENTAL_GLOBAL_CACHE_PROVEN": False,
            "RUNTIME_QUOTIENT_COMPRESSION_PROVEN": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
        "verdict": "R46A_PASS__WATCHED_RUP_DROPIN_ZERO_SEMANTIC_DRIFT" if passed else "R46A_FAIL__SEMANTIC_OR_REPLAY_MISMATCH",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-workers", type=int, default=None)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    result = run_audit(args.max_workers)
    if args.compact:
        compact = {k: v for k, v in result.items() if k != "rows"}
        print(json.dumps(compact, sort_keys=True))
    else:
        print(json.dumps(result, sort_keys=True))
    if not result["status"]["R46A_WATCHED_RUP_DROPIN_SEMANTIC_EQUIVALENCE"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
