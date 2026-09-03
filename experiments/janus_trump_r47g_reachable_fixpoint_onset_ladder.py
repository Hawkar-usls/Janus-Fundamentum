from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f

N_VALUES = tuple(range(10, 49, 2))
RATIOS = (3.8, 4.0, 4.2, 4.3, 4.5)
ATTEMPTS = 24
ANCHOR = {"n": 48, "ratio": 4.3, "seed": 43004}


def seed_for(n: int, ratio: float, attempt: int) -> int:
    return 470000 + 100 * int(n) + 10 * round(10 * float(ratio)) + int(attempt)


def generated_formula(n: int, ratio: float, attempt: int):
    seed = seed_for(n, ratio, attempt)
    return seed, r33.deterministic_random_3cnf(seed, n=n, ratio=ratio)


def witness_receipt(source: dict, original, reached):
    fixpoint = r33.canonical_formula(reached["formula"])
    rows, selected = r47f.macro_rows(fixpoint)
    return {
        "source": source,
        "original_formula": [list(c) for c in original],
        "original_hash": r47f.formula_hash(original),
        "original_CLV": list(r33.measure(original)),
        "fixpoint_formula": [list(c) for c in fixpoint],
        "fixpoint_hash": r47f.formula_hash(fixpoint),
        "fixpoint_CLV": list(r33.measure(fixpoint)),
        "trajectory": reached["trajectory"],
        "macro_rows_prefix": rows,
        "macro_selection": selected,
        "macro_covered": selected is not None,
    }


def run():
    tested_by_n = {}
    first = None
    for n in N_VALUES:
        tested = 0
        for ratio in RATIOS:
            for attempt in range(ATTEMPTS):
                seed, original = generated_formula(n, ratio, attempt)
                tested += 1
                reached = r47f.reachable_fixpoint(original)
                if reached is None:
                    continue
                first = witness_receipt(
                    {"kind": "LADDER", "n": n, "ratio": ratio, "attempt": attempt, "seed": seed},
                    original,
                    reached,
                )
                break
            if first is not None:
                break
        tested_by_n[str(n)] = tested
        if first is not None:
            break

        if n == ANCHOR["n"]:
            original = r33.deterministic_random_3cnf(ANCHOR["seed"], n=ANCHOR["n"], ratio=ANCHOR["ratio"])
            tested_by_n[str(n)] += 1
            reached = r47f.reachable_fixpoint(original)
            if reached is not None:
                first = witness_receipt({"kind": "HISTORICAL_ANCHOR", **ANCHOR}, original, reached)
                break

    if first is None:
        verdict = "NO_FIXPOINT_THROUGH_N48_INCLUDING_HISTORICAL_ANCHOR_INTEGRITY_FAILURE"
    elif first["macro_covered"]:
        verdict = "EARLIEST_FROZEN_LADDER_FIXPOINT_FOUND_AND_MACRO_COVERED"
    else:
        verdict = "EARLIEST_FROZEN_LADDER_FIXPOINT_FOUND_AND_MACRO_DEAD"

    first_n = None if first is None else int(first["source"]["n"])
    all_smaller_exhausted = True
    if first_n is not None:
        for n in N_VALUES:
            if n >= first_n:
                break
            if tested_by_n.get(str(n), 0) != len(RATIOS) * ATTEMPTS:
                all_smaller_exhausted = False
                break

    out = {
        "gate": "JANUS_TRUMP_R47G_REACHABLE_FIXPOINT_ONSET_LADDER",
        "verdict": verdict,
        "ladder": {"n_values": list(N_VALUES), "ratios": list(RATIOS), "attempts_per_cell": ATTEMPTS, "historical_anchor": ANCHOR},
        "tested_by_n": tested_by_n,
        "first_fixpoint_n": first_n,
        "all_smaller_ladder_sizes_exhausted": all_smaller_exhausted,
        "witness": first,
        "interpretation": {"ladder_minimum_is_not_global_minimum": True, "finite_macro_coverage_is_not_O4": True},
        "firewall": {"O4_UNIVERSAL_COVERAGE": "OPEN", "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "TRUMP_finished": False},
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
