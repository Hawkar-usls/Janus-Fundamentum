import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.open_component_query_message.open_message import (
    UNSAT_STATE, normalize_formula, project_open_state,
    run_open_message_quotient
)


def clause_sat(clause, assignment):
    if not clause:
        return False
    return any(assignment[abs(l)] if l > 0 else not assignment[abs(l)]
               for l in clause)


def formula_sat(clauses, assignment):
    if clauses == UNSAT_STATE:
        return False
    return all(clause_sat(c, assignment) for c in clauses)


def existential_profile(clauses, boundary):
    boundary = list(boundary)
    all_vars = sorted({abs(l) for c in clauses if c != UNSAT_STATE for l in c}) if clauses != UNSAT_STATE else []
    internal = [v for v in all_vars if v not in set(boundary)]
    out = []
    for bbits in itertools.product((False, True), repeat=len(boundary)):
        base = dict(zip(boundary, bbits))
        ok = False
        for ibits in itertools.product((False, True), repeat=len(internal)):
            a = dict(base)
            a.update(zip(internal, ibits))
            if formula_sat(clauses, a):
                ok = True
                break
        out.append(ok)
    return tuple(out)


def connected_selector_backbone(k):
    selectors = list(range(1, k + 1))
    gate = k + 1
    boundary = selectors + [gate]
    clauses = []
    nxt = gate + 1
    for j, x in enumerate(selectors, start=3):
        s = j
        a = list(range(nxt, nxt + s + 1)); nxt += s + 1
        b = list(range(nxt, nxt + s + 1)); nxt += s + 1
        ta, tb = nxt, nxt + 1; nxt += 2
        clauses += [[x, a[0], a[t]] for t in range(1, s + 1)]
        clauses += [[-x, b[t], b[t + 1]] for t in range(s)]
        clauses += [[a[0], gate, ta], [b[0], gate, tb]]
    return clauses, boundary


def check_controls():
    out = {}
    two = [[-1, 3], [-3, 2]]
    projected, stats = project_open_state(normalize_formula(two), [1, 2])
    out["2SAT_PROJECTS_TO_NONTRIVIAL_BOUNDARY_RELATION"] = {
        "pass": projected == ((-1, 2),),
        "projected": projected,
        "stats": stats,
    }
    contradiction = [[3], [-3]]
    projected, stats = project_open_state(normalize_formula(contradiction), [1])
    out["2SAT_INTERNAL_CONTRADICTION_PROJECTS_TO_UNSAT"] = {
        "pass": projected == UNSAT_STATE,
        "stats": stats,
    }
    unate = [[1, 3, 4], [-2, 4]]
    projected, stats = project_open_state(normalize_formula(unate), [1, 2])
    out["UNATE_OPEN_FACTOR_PROJECTS_WITHOUT_ENUMERATION"] = {
        "pass": projected == (), "projected": projected, "stats": stats,
    }
    boundary_only = [[1, -2], [3, 4]]
    projected, stats = project_open_state(normalize_formula(boundary_only), [1, 2, 3, 4])
    out["BOUNDARY_ONLY_CLAUSES_ARE_PRESERVED"] = {
        "pass": projected == normalize_formula(boundary_only),
        "projected": projected, "stats": stats,
    }
    mixed = [[1, 3, 4], [-1, -3, 5]]
    projected, stats = project_open_state(normalize_formula(mixed), [1])
    out["GENERAL_MIXED_3CNF_FACTOR_REMAINS_UNRESOLVED"] = {
        "pass": projected == normalize_formula(mixed) and stats.get("open_unresolved_kept", 0) == 1,
        "stats": stats,
    }
    return out


def random_case(rng):
    kb = rng.randint(0, 3)
    ki = rng.randint(0, 4)
    boundary = list(range(1, kb + 1))
    internal = list(range(kb + 1, kb + ki + 1))
    pool = boundary + internal
    clauses = []
    if pool:
        for _ in range(rng.randint(0, 7)):
            width = rng.randint(1, min(3, len(pool)))
            vs = rng.sample(pool, width)
            clauses.append([v if rng.random() < .5 else -v for v in vs])
    return clauses, boundary

def random_projection_exactness(seed=20260913, total=64):
    rng = random.Random(seed)
    passed = 0
    failure = None
    for i in range(total):
        clauses, boundary = random_case(rng)
        original = normalize_formula(clauses)
        projected, stats = project_open_state(original, boundary)
        got = existential_profile(projected, boundary)
        want = existential_profile(original, boundary)
        if got == want:
            passed += 1
        elif failure is None:
            failure = {"index": i, "clauses": clauses, "boundary": boundary,
                       "got": got, "want": want, "stats": stats,
                       "projected": projected}
    return {"passed": passed, "total": total, "seed": seed,
            "failure": failure}


def backbone_ladder(kmax=16):
    rows = []
    for k in range(1, kmax + 1):
        clauses, boundary = connected_selector_backbone(k)
        result = run_open_message_quotient(clauses, boundary)
        rows.append({
            "k": k,
            "input_clauses": len(clauses),
            "explicit_selector_rows": 2 ** k,
            "boundary_variables": len(boundary),
            "peak_query_states": result["peak_states"],
            "final_states": len(result["states"]),
            "final_mass": sum(result["states"].values()),
            "projection_stats": result["stats"],
        })
    return rows

def captain_obvious_guard():
    text = Path(__file__).with_name("open_message.py").read_text(encoding="utf-8")
    forbidden = ["itertools.product", "permutations(", "brute_sat", "dpll(", "solve_all_assignments"]
    hits = [x for x in forbidden if x in text]
    return {
        "pass": not hits,
        "hits": hits,
        "rule": "candidate may eliminate internal variables symbolically but may not enumerate the full boundary cube or invoke a general SAT solver to build the message",
    }


def main():
    controls = check_controls()
    random_result = random_projection_exactness()
    backbone = backbone_ladder()
    captain = captain_obvious_guard()
    controls_ok = all(x["pass"] for x in controls.values())
    random_ok = random_result["passed"] == random_result["total"]
    backbone_ok = all(
        x["peak_query_states"] == 1 and x["final_states"] == 1 and
        x["final_mass"] == 2 ** x["boundary_variables"]
        for x in backbone
    )
    if controls_ok and random_ok and backbone_ok and captain["pass"]:
        verdict = "PASS_EXACT_OPEN_QUERY_MESSAGE__CONNECTED_BACKBONE_COLLAPSES__GENERAL_3CNF_OPEN"
    elif controls_ok and random_ok and captain["pass"]:
        verdict = "PASS_EXACT_PROJECTION__NO_BACKBONE_COLLAPSE"
    else:
        verdict = "FALSIFIED_EXACT_OPEN_QUERY_MESSAGE"
    result = {
        "schema": "JANUS_TRUMP_OPEN_CONNECTED_COMPONENT_QUERY_MESSAGE_GATE_V1",
        "verdict": verdict,
        "captain_obvious_guard": captain,
        "controls": controls,
        "random_projection_exactness": random_result,
        "connected_selector_backbone_ladder": backbone,
        "interpretation": "exact existential projection of supported open factors can discharge internal variables while their boundary variables remain symbolic, so physical component separation is not required for those factors",
        "limitation": "the frozen projector language covers internal-unate CNF and 2-CNF only; unsupported mixed 3-CNF factors remain explicit and no polynomial message for arbitrary 3-CNF is claimed",
        "next": "extend the exact open-message language beyond unate/2-CNF or prove a factorized composition rule that keeps arbitrary 3-CNF boundary messages polynomial without enumerating the boundary cube",
        "scientific_status": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "Pi_negative_evidence_weight": 0,
        },
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
