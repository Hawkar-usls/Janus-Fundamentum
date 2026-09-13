import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.query_factorized_quotient.query_factorized import (
    UNSAT_STATE, factor_reduce, final_query_classes, normalize_formula,
    run_query_quotient
)

def clause_sat(clause, a):
    if not clause:
        return False
    return any(a[abs(l)] if l > 0 else not a[abs(l)] for l in clause)

def brute_sat(clauses, variables=None):
    if variables is None:
        variables = sorted({abs(l) for c in clauses for l in c})
    for bits in itertools.product((False, True), repeat=len(variables)):
        a = dict(zip(variables, bits))
        if all(clause_sat(c, a) for c in clauses):
            return True
    return False

def state_sat(state):
    if state == UNSAT_STATE:
        return False
    return brute_sat(list(state))

def transform_sat(result):
    return any(mass > 0 and state_sat(state)
               for state, mass in result["states"].items())

def selector_family(k):
    boundary = list(range(1, k + 1))
    clauses = []
    internal = []
    nxt = k + 1
    for j, x in enumerate(boundary, start=3):
        s = j
        a = list(range(nxt, nxt + s + 1)); nxt += s + 1
        b = list(range(nxt, nxt + s + 1)); nxt += s + 1
        internal += a + b
        star_edges = [(a[0], a[t]) for t in range(1, s + 1)]
        path_edges = [(b[t], b[t + 1]) for t in range(s)]
        clauses += [[x, u, v] for u, v in star_edges]
        clauses += [[-x, u, v] for u, v in path_edges]
    return clauses, boundary, internal

def connected_selector_backbone(k):
    selectors = list(range(1, k + 1))
    gate = k + 1
    boundary = selectors + [gate]
    clauses = []
    internal = []
    nxt = gate + 1
    for j, x in enumerate(selectors, start=3):
        s = j
        a = list(range(nxt, nxt + s + 1)); nxt += s + 1
        b = list(range(nxt, nxt + s + 1)); nxt += s + 1
        ta, tb = nxt, nxt + 1; nxt += 2
        internal += a + b + [ta, tb]
        clauses += [[x, a[0], a[t]] for t in range(1, s + 1)]
        clauses += [[-x, b[t], b[t + 1]] for t in range(s)]
        clauses += [[a[0], gate, ta], [b[0], gate, tb]]
    return clauses, boundary, internal

def check_controls():
    out = {}
    contradictory = [[1, 2, 2], [1, -2, -2]]
    r = run_query_quotient(contradictory, [1])
    classes = final_query_classes(r)
    out["closed_2sat_contradiction"] = {
        "pass": classes.get("SAT_CERTIFIED", 0) == 1 and classes.get("UNSAT_CERTIFIED", 0) == 1,
        "classes": classes,
        "stats": r["stats"],
    }
    mixed3 = [[1, 2, 3], [-1, 2, 3]]
    state, stats = factor_reduce(normalize_formula(mixed3), [])
    out["closed_mixed_width3_retained"] = {
        "pass": state not in (UNSAT_STATE, ()) and stats.get("closed_unresolved_kept", 0) == 1,
        "stats": stats,
        "independent_sat": brute_sat(mixed3),
    }
    open_unate = [[1, 2, 3]]
    state, stats = factor_reduce(normalize_formula(open_unate), [1])
    out["remaining_boundary_not_dropped"] = {
        "pass": state not in (UNSAT_STATE, ()) and stats.get("open_kept", 0) == 1,
        "stats": stats,
    }
    return out

def random_case(rng):
    kb = rng.randint(0, 4)
    ki = rng.randint(0, 5)
    boundary = list(range(1, kb + 1))
    internal = list(range(kb + 1, kb + ki + 1))
    pool = boundary + internal
    clauses = []
    if pool:
        for _ in range(rng.randint(0, 8)):
            width = rng.randint(1, min(3, len(pool)))
            vs = rng.sample(pool, width)
            clauses.append([v if rng.random() < .5 else -v for v in vs])
    return clauses, boundary, internal

def random_exactness(seed=20260913, total=64):
    rng = random.Random(seed)
    passed = 0
    failure = None
    for i in range(total):
        clauses, boundary, internal = random_case(rng)
        result = run_query_quotient(clauses, boundary)
        got = transform_sat(result)
        want = brute_sat(clauses, boundary + internal)
        mass_ok = sum(result["states"].values()) == 2 ** len(boundary)
        if got == want and mass_ok:
            passed += 1
        elif failure is None:
            failure = {"index": i, "clauses": clauses, "boundary": boundary,
                       "internal": internal, "got": got, "want": want,
                       "mass": sum(result["states"].values())}
    return {"passed": passed, "total": total, "seed": seed, "failure": failure}

def selector_ladder(kmax=16):
    rows = []
    for k in range(1, kmax + 1):
        clauses, boundary, _ = selector_family(k)
        result = run_query_quotient(clauses, boundary)
        rows.append({"k": k, "explicit_rows": 2 ** k,
                     "peak_states": result["peak_states"],
                     "final_states": len(result["states"]),
                     "mass": sum(result["states"].values()),
                     "classes": final_query_classes(result),
                     "formula_clauses": len(clauses)})
    return rows

def connected_ladder(kmax=7):
    rows = []
    for k in range(1, kmax + 1):
        clauses, boundary, _ = connected_selector_backbone(k)
        result = run_query_quotient(clauses, boundary)
        pre_gate_peak = max(x["states"] for x in result["layers"][:-1])
        rows.append({"k": k, "selector_rows": 2 ** k,
                     "boundary_variables": len(boundary),
                     "pre_gate_peak_states": pre_gate_peak,
                     "overall_peak_states": result["peak_states"],
                     "final_states": len(result["states"]),
                     "mass": sum(result["states"].values()),
                     "classes": final_query_classes(result),
                     "formula_clauses": len(clauses)})
    return rows

def captain_obvious_guard():
    text = Path(__file__).with_name("query_factorized.py").read_text(encoding="utf-8")
    forbidden = ["itertools.product", "permutations(", "brute_sat", "dpll(", "solve_all_assignments"]
    hits = [x for x in forbidden if x in text]
    return {"pass": not hits, "hits": hits,
            "rule": "candidate may branch current quotient states but may not enumerate the full boundary cube or invoke a general SAT search to build its quotient key"}

def main():
    controls = check_controls()
    random_result = random_exactness()
    selector = selector_ladder()
    connected = connected_ladder()
    captain = captain_obvious_guard()
    exact_ok = all(x["pass"] for x in controls.values()) and random_result["passed"] == random_result["total"]
    selector_ok = all(x["peak_states"] == 1 and x["final_states"] == 1 and
                      x["mass"] == 2 ** x["k"] for x in selector)
    connected_exp = all(x["pre_gate_peak_states"] == 2 ** x["k"] for x in connected)
    connected_final = all(x["final_states"] == 1 and x["mass"] == 2 ** x["boundary_variables"] for x in connected)
    if exact_ok and selector_ok and connected_exp and connected_final and captain["pass"]:
        verdict = "PASS_QUERY_FACTORIZATION_COLLAPSES_NONISOMORPHIC_SELECTOR__CONNECTED_CORE_REMAINS_OPEN"
    elif exact_ok and selector_ok and connected_final and captain["pass"]:
        verdict = "PASS_QUERY_FACTORIZATION_WITH_POLYNOMIAL_STATE_BOUND_ON_FROZEN_FAMILIES_ONLY"
    else:
        verdict = "FALSIFIED_QUERY_FACTORIZATION_EXACTNESS"
    result = {
        "schema": "JANUS_TRUMP_QUERY_SPECIFIC_FACTORIZED_QUOTIENT_GATE_V1",
        "verdict": verdict,
        "captain_obvious_guard": captain,
        "controls": controls,
        "random_exactness": random_result,
        "selector_ladder": selector,
        "connected_selector_backbone_ladder": connected,
        "interpretation": "SAT-query factorization can discard closed certified-P components even when their residual CNFs are non-isomorphic; this removes the prior star/path structural distinction without solving general SAT.",
        "limitation": "if components remain connected to an unprocessed boundary variable, exact discharge is delayed and quotient width may grow before the final factor split; finite ladder evidence is not an asymptotic theorem.",
        "next": "seek exact projection/factor messages that summarize still-open connected components before physical separation, with polynomial-size representation and polynomial update cost.",
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0}
    }
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
