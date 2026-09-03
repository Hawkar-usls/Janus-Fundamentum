from __future__ import annotations

import itertools
import json
import random

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47a3_post_subsumption_first_descent as r47a3

SEED_SCHEDULE = (470401, 470402, 470403)
CLAUSE_COUNTS = {
    5: (12, 13, 14, 15, 16),
    6: (15, 16, 17, 18, 19, 20),
    7: (18, 19, 20, 21, 22, 23, 24),
}
ATTEMPTS_PER_CLAUSE_COUNT = 250


def all_3clauses(n: int):
    clauses = []
    for vars3 in itertools.combinations(range(1, n + 1), 3):
        for signs in itertools.product((-1, 1), repeat=3):
            clauses.append(tuple(s * v for s, v in zip(signs, vars3)))
    return tuple(clauses)


def candidate_formula(rng: random.Random, universe, m: int):
    return r33.canonical_formula(rng.sample(universe, m))


def is_bipolar(formula) -> bool:
    for v in r33.variables(formula):
        if not any(v in c for c in formula):
            return False
        if not any(-v in c for c in formula):
            return False
    return True


def post_subsumption_rows(formula):
    rows = []
    for v in r33.variables(formula):
        row = r47a3.post_subsumption_gain(formula, int(v))
        if row is None:
            return None
        rows.append({
            "var": int(v),
            "p": row["p"],
            "n": row["n"],
            "raw_unique_resolvents": row["raw_unique_resolvents"],
            "pool_clauses": row["pool_clauses"],
            "post_subsumption_clauses": row["post_subsumption_clauses"],
            "gain": row["gain"],
            "pair_checks": row["pair_checks"],
        })
    return rows


def analyze_survivor(formula, rows):
    affine = r34.recognize_complete_affine_cnf(formula)
    rup = r35b.run_candidate(formula)
    rup_replay = r35b.independent_certificate_replay(formula, rup)
    macro = r45a.select_macro(formula)
    selected = macro.get("selected") or macro.get("selected_macro") or macro.get("macro")
    if selected is None and isinstance(macro.get("candidates"), list):
        accepted = [x for x in macro["candidates"] if x.get("accepted")]
        selected = min(accepted, key=lambda x: tuple(x.get("selection_key", []))) if accepted else None
    selected_norm = None if selected is None else selected.get("normalization", {})
    return {
        "formula": [list(c) for c in formula],
        "CLV": list(r33.measure(formula)),
        "post_subsumption_rows": rows,
        "affine": {"recognized": bool(affine["recognized"]), "reason": affine.get("reason")},
        "RUP": {
            "status": rup["status"],
            "successful_strengthening_count": len(rup.get("strengthenings", [])),
            "independent_replay_pass": bool(rup_replay["pass"]),
            "final_CLV": list(r33.measure(r33.canonical_formula(rup["final_formula"]))),
        },
        "R45A": {
            "has_selected_macro": selected is not None,
            "selected_var": None if selected is None else selected.get("var"),
            "selected_terminal": None if selected is None else selected_norm.get("terminal"),
            "selected_net_CLV_descent": None if selected is None else selected.get("net_CLV_descent"),
            "selected_final_CLV": None if selected is None else selected.get("final_CLV"),
            "selection_key": None if selected is None else selected.get("selection_key"),
            "normalization_status": None if selected is None else selected_norm.get("status"),
        },
    }


def run():
    counters = {
        "generated": 0,
        "r33_lean_unchanged": 0,
        "bipolar": 0,
        "true_post_subsumption_obstructions": 0,
    }
    survivor = None
    for n, seed in zip((5, 6, 7), SEED_SCHEDULE):
        universe = all_3clauses(n)
        rng = random.Random(seed)
        for m in CLAUSE_COUNTS[n]:
            for _ in range(ATTEMPTS_PER_CLAUSE_COUNT):
                formula = candidate_formula(rng, universe, m)
                counters["generated"] += 1
                simp = r33.simplify(formula)
                final_formula = r33.canonical_formula(simp["final_formula"])
                if not (
                    simp["terminal"] == "STALLED_STACK_LEAN_CORE"
                    and simp["total_rule_applications"] == 0
                    and final_formula == formula
                ):
                    continue
                counters["r33_lean_unchanged"] += 1
                if not is_bipolar(formula):
                    continue
                counters["bipolar"] += 1
                rows = post_subsumption_rows(formula)
                if rows is None:
                    continue
                if all(row["gain"] <= 0 for row in rows):
                    counters["true_post_subsumption_obstructions"] += 1
                    survivor = analyze_survivor(formula, rows)
                    break
            if survivor is not None:
                break
        if survivor is not None:
            break

    out = {
        "gate": "JANUS_TRUMP_R47A4_POST_SUBSUMPTION_UNIVERSAL_OBSTRUCTION_HUNT",
        "search_budget": {
            "seed_schedule": list(SEED_SCHEDULE),
            "clause_counts": {str(k): list(v) for k, v in CLAUSE_COUNTS.items()},
            "attempts_per_clause_count": ATTEMPTS_PER_CLAUSE_COUNT,
        },
        "counters": counters,
        "status": "FOUND_SURVIVOR" if survivor is not None else "NO_SURVIVOR_WITHIN_BUDGET",
        "survivor": survivor,
        "interpretation": {
            "finite_search_only": True,
            "universal_theorem_elevation_allowed": False,
        },
        "firewall": {
            "R47A_UNIVERSAL_COVERAGE": "OPEN",
            "DIRECT_POST_SUBSUMPTION_DP_UNIVERSAL": "NOT_PROVED",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
