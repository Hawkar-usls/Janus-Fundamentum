from __future__ import annotations

import itertools
import json
import random

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47a3_post_subsumption_first_descent as r47a3

SEEDS = {5: 475005, 6: 475006, 7: 475007}
RESTARTS = 40
STEPS = 25
CLAUSE_COUNTS = {5: (13, 15, 17), 6: (16, 18, 20), 7: (19, 22, 25)}


def all_3clauses(n: int):
    out = []
    for vs in itertools.combinations(range(1, n + 1), 3):
        for signs in itertools.product((-1, 1), repeat=3):
            out.append(tuple(s * v for s, v in zip(signs, vs)))
    return tuple(out)


def is_bipolar(formula) -> bool:
    return all(
        any(v in c for c in formula) and any(-v in c for c in formula)
        for v in r33.variables(formula)
    )


def lean_unchanged(formula) -> bool:
    simp = r33.simplify(formula)
    return (
        simp["terminal"] == "STALLED_STACK_LEAN_CORE"
        and simp["total_rule_applications"] == 0
        and r33.canonical_formula(simp["final_formula"]) == formula
    )


def structural_rows(formula):
    rows = []
    identity_ok = True
    for v in r33.variables(formula):
        row = r47a3.post_subsumption_gain(formula, int(v))
        if row is None:
            return None, False
        base_size = len(formula) - row["p"] - row["n"]
        d_v = len(formula) - base_size
        s_v = row["post_subsumption_clauses"] - base_size
        g_v = len(formula) - row["post_subsumption_clauses"]
        ok = g_v == d_v - s_v == row["gain"]
        identity_ok = identity_ok and ok
        rows.append({
            "var": int(v),
            "d_v": d_v,
            "s_v": s_v,
            "g_v": g_v,
            "obstruction_margin": s_v - d_v,
            "p": row["p"],
            "n": row["n"],
            "raw_unique_resolvents": row["raw_unique_resolvents"],
            "post_subsumption_clauses": row["post_subsumption_clauses"],
            "identity_ok": ok,
        })
    return rows, identity_ok


def score_rows(rows):
    # A true obstruction has every g_v <= 0. Minimize the largest remaining descent gain.
    return max(r["g_v"] for r in rows)


def evaluate(formula):
    if not lean_unchanged(formula) or not is_bipolar(formula):
        return None
    rows, identity_ok = structural_rows(formula)
    if rows is None or not identity_ok:
        raise AssertionError("R47A5 accounting identity drift")
    return {
        "score": score_rows(rows),
        "rows": rows,
        "obstruction": all(r["g_v"] <= 0 for r in rows),
    }


def mutate(rng, formula, universe):
    current = list(formula)
    used = set(current)
    idx = rng.randrange(len(current))
    choices = [c for c in universe if c not in used]
    if not choices:
        return formula
    current[idx] = rng.choice(choices)
    return r33.canonical_formula(current)


def analyze_counterexample(formula, rows):
    affine = r34.recognize_complete_affine_cnf(formula)
    rup = r35b.run_candidate(formula)
    replay = r35b.independent_certificate_replay(formula, rup)
    macro = r45a.select_macro(formula)
    selected = macro.get("selected") or macro.get("selected_macro") or macro.get("macro")
    if selected is None and isinstance(macro.get("candidates"), list):
        accepted = [x for x in macro["candidates"] if x.get("accepted")]
        selected = min(accepted, key=lambda x: tuple(x.get("selection_key", []))) if accepted else None
    return {
        "formula": [list(c) for c in formula],
        "CLV": list(r33.measure(formula)),
        "rows": rows,
        "affine_recognized": bool(affine["recognized"]),
        "RUP_status": rup["status"],
        "RUP_independent_replay_pass": bool(replay["pass"]),
        "R45A_has_selection": selected is not None,
        "R45A_selected_var": None if selected is None else selected.get("var"),
        "R45A_selected_net_CLV_descent": None if selected is None else selected.get("net_CLV_descent"),
    }


def run():
    evaluated = 0
    valid_lean = 0
    identity_checks = 0
    best = None
    counterexample = None

    for n in (5, 6, 7):
        universe = all_3clauses(n)
        rng = random.Random(SEEDS[n])
        for restart in range(RESTARTS):
            m = CLAUSE_COUNTS[n][restart % len(CLAUSE_COUNTS[n])]
            current = r33.canonical_formula(rng.sample(universe, m))
            current_eval = evaluate(current)
            evaluated += 1
            if current_eval is not None:
                valid_lean += 1
                identity_checks += len(current_eval["rows"])
                if best is None or current_eval["score"] < best["eval"]["score"]:
                    best = {"formula": current, "eval": current_eval, "n": n}
                if current_eval["obstruction"]:
                    counterexample = analyze_counterexample(current, current_eval["rows"])
                    break
            for _ in range(STEPS):
                proposal = mutate(rng, current, universe)
                pe = evaluate(proposal)
                evaluated += 1
                if pe is None:
                    continue
                valid_lean += 1
                identity_checks += len(pe["rows"])
                if best is None or pe["score"] < best["eval"]["score"]:
                    best = {"formula": proposal, "eval": pe, "n": n}
                if pe["obstruction"]:
                    counterexample = analyze_counterexample(proposal, pe["rows"])
                    break
                # Deterministic hill-climb acceptance with occasional seeded sideways move.
                if current_eval is None or pe["score"] < current_eval["score"] or (
                    pe["score"] == current_eval["score"] and rng.random() < 0.15
                ):
                    current, current_eval = proposal, pe
            if counterexample is not None:
                break
        if counterexample is not None:
            break

    best_receipt = None
    if best is not None:
        best_receipt = {
            "n": best["n"],
            "score_max_gain": best["eval"]["score"],
            "formula": [list(c) for c in best["formula"]],
            "rows": best["eval"]["rows"],
        }

    verdict = (
        "EXPLICIT_COUNTEREXAMPLE_FOUND"
        if counterexample is not None
        else "STRUCTURAL_NECESSARY_CONDITION_SEALED__UNIVERSAL_EXISTENCE_OPEN"
    )
    out = {
        "gate": "JANUS_TRUMP_R47A5_POST_SUBSUMPTION_DESCENT_STRUCTURAL_THEOREM_OR_COUNTEREXAMPLE",
        "verdict": verdict,
        "universal_identity": "g_v=d_v-s_v",
        "identity_checks": identity_checks,
        "search": {
            "evaluated": evaluated,
            "valid_r33_lean_bipolar": valid_lean,
            "restarts_per_n": RESTARTS,
            "steps_per_restart": STEPS,
            "best": best_receipt,
        },
        "counterexample": counterexample,
        "interpretation": {
            "finite_no_counterexample_is_not_theorem": True,
            "symbolic_universal_existence_proof_present": False,
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
