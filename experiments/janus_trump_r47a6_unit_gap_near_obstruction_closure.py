from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47a5_post_subsumption_descent_structural_theorem_or_counterexample as r47a5

SEED = r33.canonical_formula([
    [-3,-5,-7],[-3,4,6],[-3,6,7],[-2,-5,7],[-2,-4,7],[-1,-3,7],[-1,-2,-3],
    [-1,2,-4],[-1,3,6],[-1,4,6],[1,-4,-6],[1,2,3],[1,5,-6],[2,4,5],
    [3,-4,-7],[3,4,-5],[3,4,6],[4,-6,-7],[4,-5,6],
])
N = 7
BEAM = 32


def score(eval_result):
    rows = eval_result["rows"]
    gains = [r["g_v"] for r in rows]
    return (
        max(gains),
        sum(g > 0 for g in gains),
        sum(max(g, 0) for g in gains),
        sum(gains),
    )


def receipt(formula, eval_result):
    return {
        "formula": [list(c) for c in formula],
        "score": list(score(eval_result)),
        "gain_vector": [r["g_v"] for r in eval_result["rows"]],
        "rows": eval_result["rows"],
    }


def one_swap_neighbors(formula, universe):
    used = set(formula)
    for old in formula:
        base = used - {old}
        for new in universe:
            if new in base or new == old:
                continue
            yield r33.canonical_formula(list(base) + [new])


def run():
    seed_eval = r47a5.evaluate(SEED)
    assert seed_eval is not None
    assert score(seed_eval)[0] == 1
    assert [r["g_v"] for r in seed_eval["rows"]] == [1, 1, 1, -1, 0, 1, 1]

    universe = r47a5.all_3clauses(N)
    stats = {
        "stage1_generated": 0,
        "stage1_unique": 0,
        "stage1_valid_lean_bipolar": 0,
        "stage2_generated": 0,
        "stage2_unique_new": 0,
        "stage2_valid_lean_bipolar": 0,
    }
    seen = {SEED}
    stage1_valid = []
    counterexample = None
    best_formula = SEED
    best_eval = seed_eval
    best_score = score(seed_eval)

    for candidate in one_swap_neighbors(SEED, universe):
        stats["stage1_generated"] += 1
        if candidate in seen:
            continue
        seen.add(candidate)
        stats["stage1_unique"] += 1
        ev = r47a5.evaluate(candidate)
        if ev is None:
            continue
        stats["stage1_valid_lean_bipolar"] += 1
        sc = score(ev)
        stage1_valid.append((sc, candidate, ev))
        if sc < best_score:
            best_score, best_formula, best_eval = sc, candidate, ev
        if ev["obstruction"]:
            counterexample = r47a5.analyze_counterexample(candidate, ev["rows"])
            break

    if counterexample is None:
        stage1_valid.sort(key=lambda x: (x[0], x[1]))
        frontier = stage1_valid[:BEAM]
        for _, center, _ in frontier:
            for candidate in one_swap_neighbors(center, universe):
                stats["stage2_generated"] += 1
                if candidate in seen:
                    continue
                seen.add(candidate)
                stats["stage2_unique_new"] += 1
                ev = r47a5.evaluate(candidate)
                if ev is None:
                    continue
                stats["stage2_valid_lean_bipolar"] += 1
                sc = score(ev)
                if sc < best_score:
                    best_score, best_formula, best_eval = sc, candidate, ev
                if ev["obstruction"]:
                    counterexample = r47a5.analyze_counterexample(candidate, ev["rows"])
                    break
            if counterexample is not None:
                break

    verdict = (
        "EXPLICIT_DIRECT_DP_COUNTEREXAMPLE_FOUND"
        if counterexample is not None
        else "UNIT_GAP_SURVIVES_DETERMINISTIC_TWO_HOP_CLOSURE__UNIVERSAL_OPEN"
    )
    out = {
        "gate": "JANUS_TRUMP_R47A6_UNIT_GAP_NEAR_OBSTRUCTION_CLOSURE",
        "verdict": verdict,
        "seed": receipt(SEED, seed_eval),
        "best": receipt(best_formula, best_eval),
        "stats": stats,
        "beam": BEAM,
        "counterexample": counterexample,
        "interpretation": {
            "deterministic_bounded_neighborhood_only": True,
            "universal_theorem_elevation_allowed": False,
        },
        "firewall": {
            "DIRECT_POST_SUBSUMPTION_DP_UNIVERSAL": "NOT_PROVED",
            "R47A_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
