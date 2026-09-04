from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5

GATE = "JANUS_TRUMP_R50G7_IMMEDIATE_BVE_SAME_PIVOT_W4_SAFETY"
WIDTH_CAP = 4
PIVOT = 1
SHIFT_OFFSET = 100
MAX_EXACT_FAMILY_CANDIDATES = 2000


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def fhash(f):
    return r50g4.fhash(canon(f))


def shift_formula(formula, offset: int):
    return canon(
        tuple((1 if lit > 0 else -1) * (abs(int(lit)) + offset) for lit in clause)
        for clause in canon(formula)
    )


def signed(v: int, bit: int) -> int:
    return int(v) if bit else -int(v)


def no_subsumption_interaction(core, p, n):
    csets = [set(c) for c in canon(core)]
    ps, ns = set(p), set(n)
    for s in csets:
        if s <= ps or ps <= s or s <= ns or ns <= s:
            return False
    return True


def exact_pre_bve_clean(formula):
    f = canon(formula)
    if any(r33.is_tautology(c) for c in f):
        return False
    if any(len(c) == 1 for c in f):
        return False
    if r33.pure_literals(f):
        return False
    if r33.first_subsumed_clause(f) is not None:
        return False
    if r33.first_blocked_clause(f) is not None:
        return False
    return True


def frozen_shifted_core():
    _sealed, core = r47j.load_counterexample()
    core = canon(core)
    norm = r47j.normalize_to_certified_fixpoint(core)
    if norm["terminal"] is not None:
        raise AssertionError("R50G7_FROZEN_CORE_BECAME_TERMINAL")
    if canon(norm["final_formula"]) != core:
        raise AssertionError("R50G7_FROZEN_CORE_NOT_NORMALIZATION_FIXED")
    if max_width(core) > WIDTH_CAP:
        raise AssertionError("R50G7_FROZEN_CORE_NOT_W4")
    shifted = shift_formula(core, SHIFT_OFFSET)
    return core, shifted


def check_family_member(core, five_vars, pos_indices, sign_bits):
    lits = [signed(v, b) for v, b in zip(five_vars, sign_bits)]
    pos_i = set(pos_indices)
    a = [lits[i] for i in range(5) if i in pos_i]
    b = [lits[i] for i in range(5) if i not in pos_i]
    if len(a) != 3 or len(b) != 2:
        raise AssertionError("R50G7_SPLIT_NOT_3_PLUS_2")
    residual = canon([a + b])[0]
    if len(residual) != 5 or r33.is_tautology(residual):
        return {"eligible": False, "reason": "RESOLVENT_NOT_EXACT_WIDTH5"}

    p = r33.canonical_clause([PIVOT] + a)
    n = r33.canonical_clause([-PIVOT] + b)
    if len(p) != 4 or len(n) != 3:
        return {"eligible": False, "reason": "PARENT_WIDTH_DRIFT"}
    if not no_subsumption_interaction(core, p, n):
        return {"eligible": False, "reason": "PARENT_CORE_SUBSUMPTION_INTERACTION"}

    f = canon(list(core) + [p, n])
    if max_width(f) > WIDTH_CAP:
        raise AssertionError("R50G7_INPUT_LEFT_W4")
    if not exact_pre_bve_clean(f):
        return {"eligible": False, "reason": "EARLIER_R33_RULE_EXISTS"}

    micro = r50g4.micro_r33_status(f)
    if micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        return {"eligible": False, "reason": "NOT_IMMEDIATE_BVE_ESCAPE"}
    direct = r50g4.first_r33_micro_candidate(f)
    if direct.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct.get("var", -1)) != PIVOT:
        return {"eligible": False, "reason": "FIRST_BVE_NOT_FROZEN_PIVOT"}

    claimed_resolvents = {tuple(c) for c in direct["resolvents"]}
    if tuple(residual) not in claimed_resolvents:
        raise AssertionError("R50G7_WIDTH5_RESOLVENT_MISSING")

    cand = r47j.macro_candidate_fixpoint(f, PIVOT)
    if cand is None:
        raise AssertionError("R50G7_SAME_PIVOT_R47J_MISSING")
    replay = r47j.independent_fixpoint_macro_replay(f, cand)
    if not replay["pass"]:
        raise AssertionError(("R50G7_INDEPENDENT_REPLAY_FAIL", replay))
    final = canon(cand["normalization"]["final_formula"])
    terminal = cand["normalization"]["terminal"]
    final_w = max_width(final)
    wide_survivor = terminal is None and final_w > WIDTH_CAP

    return {
        "eligible": True,
        "input_hash": fhash(f),
        "pivot": PIVOT,
        "positive_parent": list(p),
        "negative_parent": list(n),
        "width5_resolvent": list(residual),
        "input_CLV": list(r33.measure(f)),
        "raw_escape_width": max_width(direct["after"]),
        "final_hash": fhash(final),
        "final_CLV": list(r33.measure(final)),
        "final_width": final_w,
        "terminal": terminal,
        "same_pivot_machine_safe": bool(terminal is not None or final_w <= WIDTH_CAP),
        "same_pivot_wide_survivor": bool(wide_survivor),
        "independent_replay_pass": True,
        "formula": [list(c) for c in f] if wide_survivor else None,
        "final_formula": [list(c) for c in final] if wide_survivor else None,
    }


def search_algebraic_family(limit: int = MAX_EXACT_FAMILY_CANDIDATES):
    _core_original, core = frozen_shifted_core()
    vs = tuple(r33.variables(core))
    exact_eligible = 0
    enumerated = 0
    rejects = {}
    first_witness = None

    for five in itertools.combinations(vs, 5):
        for pos_indices in itertools.combinations(range(5), 3):
            for sign_bits in itertools.product((0, 1), repeat=5):
                enumerated += 1
                row = check_family_member(core, five, pos_indices, sign_bits)
                if not row["eligible"]:
                    reason = row["reason"]
                    rejects[reason] = rejects.get(reason, 0) + 1
                    continue
                exact_eligible += 1
                if row["same_pivot_wide_survivor"]:
                    first_witness = {
                        "five_variables": list(five),
                        "positive_indices": list(pos_indices),
                        "sign_bits": list(sign_bits),
                        **row,
                    }
                    break
                if exact_eligible >= limit:
                    break
            if first_witness is not None or exact_eligible >= limit:
                break
        if first_witness is not None or exact_eligible >= limit:
            break

    return {
        "enumerated_parameter_tuples": enumerated,
        "exact_eligible_candidates_tested": exact_eligible,
        "frozen_exact_candidate_cap": limit,
        "reject_histogram": dict(sorted(rejects.items())),
        "first_local_wide_survivor": first_witness,
        "local_counterexample_found": first_witness is not None,
    }


def replay_frozen_reachable_roots():
    immediate = 0
    unsafe = []
    terminal = 0
    reentry = 0
    for worker, n in enumerate(range(6, 11)):
        for i in range(80):
            m = 3 * n + (i % (3 * n + 1))
            seed = 50_700_000 + worker * 100_000 + i
            root, _ = r50g.make_planted(seed, n, m, "3CNF")
            if len(r33.variables(root)) != n:
                continue
            result = r50g5.trace_root(root, {"worker": worker, "seed": seed, "n": n, "m": m})
            for row in result["escape_rows"]:
                immediate += 1
                if row["same_pivot_terminal"]:
                    terminal += 1
                elif row["same_pivot_W4_reentry"]:
                    reentry += 1
                if not row["same_pivot_R47J_machine_safe"]:
                    unsafe.append({"worker": worker, "n": n, "seed": seed, **row})
    return {
        "frozen_roots": 400,
        "immediate_BVE_states": immediate,
        "same_pivot_terminal": terminal,
        "same_pivot_W4_reentry": reentry,
        "same_pivot_unsafe": len(unsafe),
        "first_reachable_unsafe": unsafe[0] if unsafe else None,
    }


def firewall(local_found: bool, reachable_found: bool):
    return {
        "HEURISTIC_AUTHORITY": False,
        "LEARNED_SELECTOR": False,
        "PROBABILISTIC_AUTHORITY": False,
        "NEW_SEMANTIC_INFERENCE_RULE": False,
        "FINITE_NO_FIND_IMPLIES_THEOREM": False,
        "LOCAL_SAME_PIVOT_W4_SAFETY": "REFUTED" if local_found else "OPEN",
        "REACHABLE_SAME_PIVOT_W4_SAFETY": "REFUTED" if reachable_found else "OPEN",
        "IMMEDIATE_BVE_CASE_ELIMINATED": False,
        "U_MU": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def run(limit: int):
    family = search_algebraic_family(limit)
    reachable = replay_frozen_reachable_roots()
    local_found = bool(family["local_counterexample_found"])
    reachable_found = bool(reachable["same_pivot_unsafe"])
    if reachable_found:
        verdict = "EXPLICIT_REACHABLE_IMMEDIATE_BVE_SAME_PIVOT_W4_SAFETY_COUNTEREXAMPLE_FOUND"
    elif local_found:
        verdict = "LOCAL_SAME_PIVOT_W4_SAFETY_REFUTED_BY_EXACT_ALGEBRAIC_WIDE_SURVIVOR__REACHABLE_THEOREM_REQUIRES_REACHABILITY_INVARIANT"
    else:
        verdict = "NO_WIDE_SURVIVOR_FOUND_IN_FROZEN_ALGEBRAIC_FAMILY_OR_REACHABLE_REPLAY__UNIVERSAL_THEOREMS_REMAIN_OPEN"
    return {
        "gate": GATE,
        "mode": "EXACT_THEOREM_FALSIFIER",
        "source_reduction": [
            "R50G5_SAME_PIVOT_SAFE_IFF_TERMINAL_OR_FINAL_WIDTH_LE_4",
            "R50G6_STRONG_LOCAL_TERMINALITY_REFUTED",
            "ONLY_REMAINING_LOCAL_FAILURE_IS_NONTERMINAL_FINAL_WIDTH_GT_4",
        ],
        "algebraic_family": family,
        "reachable_replay": reachable,
        "verdict": verdict,
        "critical_next_obligation": (
            "REACHABILITY_SPECIFIC_W4_SAFETY_INVARIANT" if local_found and not reachable_found
            else "UNIVERSAL_SAME_PIVOT_W4_SAFETY_PROOF_OR_STRONGER_EXACT_COUNTEREXAMPLE"
        ),
        "firewall": firewall(local_found, reachable_found),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=MAX_EXACT_FAMILY_CANDIDATES)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.limit != MAX_EXACT_FAMILY_CANDIDATES:
        raise AssertionError("R50G7_FROZEN_EXACT_CANDIDATE_CAP_DRIFT")
    out = run(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2))
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
