from __future__ import annotations

import hashlib
import itertools
import json
import random

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a

NS = (6, 7, 8, 9)
OFFSETS = (-3, -2, -1, 0, 1, 2, 3)
ATTEMPTS = 80
SEEDS = {6: 470601, 7: 470701, 8: 470801, 9: 470901}


def formula_hash(formula):
    payload = json.dumps([list(c) for c in r33.canonical_formula(formula)], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def universe(n: int):
    out = []
    for vs in itertools.combinations(range(1, n + 1), 3):
        for signs in itertools.product((-1, 1), repeat=3):
            out.append(tuple(s * v for s, v in zip(signs, vs)))
    return tuple(out)


def reachable_fixpoint(original):
    original = r33.canonical_formula(original)
    state = original
    rank = r42.rank_parameters(original)
    rank0 = r42.mu(original, rank)
    trajectory = []
    for cycle in range(rank0 + 1):
        before = state
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            return None
        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            return None
        rup = r35b.run_candidate(after_r33)
        replay = r35b.independent_certificate_replay(after_r33, rup)
        if not replay["pass"]:
            raise AssertionError(("R47F_RUP_REPLAY_FAIL", cycle))
        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            return None
        after_rup = r33.canonical_formula(rup["final_formula"])
        bve, _ = r42.best_sa_bve_candidate(after_rup)
        after_bve = r33.canonical_formula(bve["transformed"]) if bve is not None else after_rup
        trajectory.append({
            "cycle": cycle,
            "before_CLV": list(r33.measure(before)),
            "R33_apps": int(reduced["total_rule_applications"]),
            "after_R33_CLV": list(r33.measure(after_r33)),
            "RUP_history": len(rup.get("history", [])),
            "after_RUP_CLV": list(r33.measure(after_rup)),
            "BVE_applied": bve is not None,
            "after_BVE_CLV": list(r33.measure(after_bve)),
        })
        if after_bve == before:
            if reduced["history"] or after_r33 != before:
                raise AssertionError("R47F_FALSE_R33_FIXPOINT")
            if rup.get("history", []) or after_rup != before:
                raise AssertionError("R47F_FALSE_RUP_FIXPOINT")
            if bve is not None:
                raise AssertionError("R47F_FALSE_BVE_FIXPOINT")
            return {"formula": before, "trajectory": trajectory}
        state = after_bve
    raise AssertionError("R47F_R42_RANK_EXHAUSTED")


def macro_rows(fixpoint):
    before = r33.canonical_formula(fixpoint)
    rows = []
    selected = None
    for var in r33.variables(before):
        candidate = r45a.macro_candidate_for_var(before, int(var))
        if candidate is None:
            rows.append({"var": int(var), "candidate": False, "accepted": False})
            continue
        row = {
            "var": int(var),
            "candidate": True,
            "accepted": bool(candidate["accepted"]),
            "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
            "final_CLV": candidate["final_CLV"],
            "terminal": candidate["normalization"].get("terminal"),
            "net_CLV_descent": bool(candidate["net_CLV_descent"]),
            "temporary_internal_ascent": bool(candidate["temporary_internal_ascent"]),
            "DP_replay_pass": bool(candidate["DP_independent_replay"]["pass"]),
            "poly_envelope_pass": bool(candidate["polynomial_intermediate_envelope"]["pass"]),
        }
        rows.append(row)
        if candidate["accepted"] and selected is None:
            replay = r45a.independent_macro_replay(before, candidate)
            if not replay["pass"]:
                raise AssertionError(("R47F_MACRO_REPLAY_FAIL", var, replay))
            selected = {"var": int(var), "replay_pass": True, "final_CLV": candidate["final_CLV"], "terminal": candidate["normalization"].get("terminal")}
            break
    return rows, selected


def run():
    counters = {
        "generated": 0,
        "reachable_fixpoints": 0,
        "unique_reachable_fixpoints": 0,
        "covered_by_first_certified_macro": 0,
        "macro_dead_fixpoints": 0,
    }
    seen_fixpoints = set()
    counterexample = None
    for n in NS:
        U = universe(n)
        rng = random.Random(SEEDS[n])
        for offset in OFFSETS:
            m = 4 * n + offset
            if m <= 0 or m > len(U):
                continue
            for attempt in range(ATTEMPTS):
                original = r33.canonical_formula(rng.sample(U, m))
                counters["generated"] += 1
                reached = reachable_fixpoint(original)
                if reached is None:
                    continue
                counters["reachable_fixpoints"] += 1
                fixpoint = r33.canonical_formula(reached["formula"])
                h = formula_hash(fixpoint)
                if h in seen_fixpoints:
                    continue
                seen_fixpoints.add(h)
                counters["unique_reachable_fixpoints"] += 1
                rows, selected = macro_rows(fixpoint)
                if selected is not None:
                    counters["covered_by_first_certified_macro"] += 1
                    continue
                counters["macro_dead_fixpoints"] += 1
                counterexample = {
                    "n": n,
                    "m": m,
                    "attempt": attempt,
                    "original_formula": [list(c) for c in original],
                    "original_hash": formula_hash(original),
                    "original_CLV": list(r33.measure(original)),
                    "fixpoint_formula": [list(c) for c in fixpoint],
                    "fixpoint_hash": h,
                    "fixpoint_CLV": list(r33.measure(fixpoint)),
                    "trajectory": reached["trajectory"],
                    "macro_rows": rows,
                }
                break
            if counterexample is not None:
                break
        if counterexample is not None:
            break

    verdict = (
        "EXPLICIT_SMALL_REACHABLE_MACRO_COVERAGE_COUNTEREXAMPLE_FOUND"
        if counterexample is not None
        else "NO_COUNTEREXAMPLE_IN_FROZEN_SMALL_REACHABLE_SEARCH__O4_OPEN"
    )
    out = {
        "gate": "JANUS_TRUMP_R47F_SMALL_REACHABLE_FIXPOINT_FULL_MACRO_FALSIFIER",
        "verdict": verdict,
        "search": {"variables": list(NS), "offsets": list(OFFSETS), "attempts_per_cell": ATTEMPTS, "seeds": SEEDS},
        "counters": counters,
        "counterexample": counterexample,
        "interpretation": {"finite_search_only": True, "universal_theorem_elevation_allowed": False},
        "firewall": {"O4_UNIVERSAL_COVERAGE": "OPEN", "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "TRUMP_finished": False},
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
