import itertools, json, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.open_connected_query_message.open_query_message import (
    UNSAT_STATE, message_reduce, normalize_formula,
    project_2cnf_factor, run_open_message_quotient
)

def clause_sat(clause, a):
    return bool(clause) and any(a[abs(l)] if l > 0 else not a[abs(l)] for l in clause)

def formula_sat_under_boundary(clauses, boundary_assign, internal):
    for bits in itertools.product((False, True), repeat=len(internal)):
        a = dict(boundary_assign); a.update(zip(internal, bits))
        if all(clause_sat(c, a) for c in clauses):
            return True
    return False

def reduced_sat_under_boundary(state, boundary_assign):
    if state == UNSAT_STATE:
        return False
    vars_ = sorted({abs(l) for c in state for l in c} - set(boundary_assign))
    return formula_sat_under_boundary(list(state), boundary_assign, vars_)

def all_vars(clauses):
    return sorted({abs(l) for c in clauses for l in c})

def connected_selector_backbone(k):
    selectors = list(range(1, k + 1))
    gate = k + 1
    boundary = selectors + [gate]
    clauses = []; nxt = gate + 1
    for j, x in enumerate(selectors, start=3):
        s = j
        a = list(range(nxt, nxt + s + 1)); nxt += s + 1
        b = list(range(nxt, nxt + s + 1)); nxt += s + 1
        ta, tb = nxt, nxt + 1; nxt += 2
        clauses += [[x, a[0], a[t]] for t in range(1, s + 1)]
        clauses += [[-x, b[t], b[t + 1]] for t in range(s)]
        clauses += [[a[0], gate, ta], [b[0], gate, tb]]
    return clauses, boundary

def check_2sat_projection():
    factor = normalize_formula([[1, 3], [-3, 2]])
    projected, stats = project_2cnf_factor(factor, [1, 2])
    expected = normalize_formula([[1, 2]])
    truth_ok = True
    for xb, zb in itertools.product((False, True), repeat=2):
        b = {1: xb, 2: zb}
        old = formula_sat_under_boundary([[1, 3], [-3, 2]], b, [3])
        new = reduced_sat_under_boundary(projected, b)
        truth_ok &= (old == new)
    return {"pass": projected == expected and truth_ok,
            "projected": projected, "expected": expected, "stats": stats}

def check_2sat_unsat():
    projected, stats = project_2cnf_factor(normalize_formula([[3], [-3]]), [])
    return {"pass": projected == UNSAT_STATE, "projected": projected, "stats": stats}

def check_unate_projection():
    clauses = [[1, 3], [1, 4], [2]]
    reduced, stats = message_reduce(normalize_formula(clauses), [1, 2])
    expected = normalize_formula([[2]])
    truth_ok = True
    for x1, x2 in itertools.product((False, True), repeat=2):
        b = {1: x1, 2: x2}
        old = formula_sat_under_boundary(clauses, b, [3, 4])
        new = reduced_sat_under_boundary(reduced, b)
        truth_ok &= (old == new)
    return {"pass": reduced == expected and truth_ok,
            "reduced": reduced, "expected": expected, "stats": stats}

def check_general_mixed3_kept():
    clauses = [[1, 2, 3], [-1, -2, 3]]
    reduced, stats = message_reduce(normalize_formula(clauses), [1])
    return {"pass": reduced == normalize_formula(clauses)
                    and stats.get("open_general_factor_kept", 0) == 1,
            "reduced": reduced, "stats": stats}

def random_case(rng):
    n = rng.randint(1, 6)
    vars_ = list(range(1, n + 1))
    bcount = rng.randint(0, n)
    boundary = sorted(rng.sample(vars_, bcount))
    clauses = []
    for _ in range(rng.randint(0, 8)):
        width = rng.randint(1, min(3, n))
        vs = rng.sample(vars_, width)
        clauses.append([v if rng.random() < .5 else -v for v in vs])
    return clauses, boundary

def check_projection_equivalence(clauses, boundary):
    original_vars = set(all_vars(clauses)); internal = sorted(original_vars - set(boundary))
    reduced, stats = message_reduce(normalize_formula(clauses), boundary)
    for bits in itertools.product((False, True), repeat=len(boundary)):
        b = dict(zip(boundary, bits))
        if formula_sat_under_boundary(clauses, b, internal) != reduced_sat_under_boundary(reduced, b):
            return False, reduced, stats, b
    return True, reduced, stats, None

def random_projection_exactness(seed=20260913, total=64):
    rng = random.Random(seed); passed = 0; failure = None
    for i in range(total):
        clauses, boundary = random_case(rng)
        ok, reduced, stats, witness = check_projection_equivalence(clauses, boundary)
        if ok:
            passed += 1
        elif failure is None:
            failure = {"index": i, "clauses": clauses, "boundary": boundary,
                       "reduced": reduced, "stats": stats, "witness": witness}
    return {"passed": passed, "total": total, "seed": seed, "failure": failure}

def connected_backbone_ladder(kmax=16):
    rows = []
    for k in range(1, kmax + 1):
        clauses, boundary = connected_selector_backbone(k)
        result = run_open_message_quotient(clauses, boundary)
        rows.append({"k": k, "explicit_selector_rows": 2 ** k,
                     "formula_clauses": len(clauses),
                     "peak_states": result["peak_states"],
                     "final_states": len(result["states"]),
                     "mass": sum(result["states"].values()),
                     "stats": result["stats"]})
    return rows

def captain_obvious_guard():
    text = Path(__file__).with_name("open_query_message.py").read_text(encoding="utf-8")
    forbidden = ["itertools.product", "brute_sat", "dpll(", "permutations(", "solve_all_assignments"]
    hits = [x for x in forbidden if x in text]
    return {"pass": not hits, "hits": hits,
            "rule": "message construction may use restricted polynomial projectors but not full boundary enumeration or a general SAT solver"}

def main():
    controls = {
        "two_sat_projection": check_2sat_projection(),
        "two_sat_unsat": check_2sat_unsat(),
        "unate_projection": check_unate_projection(),
        "general_mixed3_kept": check_general_mixed3_kept(),
    }
    random_result = random_projection_exactness()
    ladder = connected_backbone_ladder()
    captain = captain_obvious_guard()
    controls_ok = all(x["pass"] for x in controls.values())
    random_ok = random_result["passed"] == random_result["total"]
    collapse_ok = all(x["peak_states"] == 1 and x["final_states"] == 1 for x in ladder)
    mass_ok = all(x["mass"] == 2 ** (x["k"] + 1) for x in ladder)
    if controls_ok and random_ok and collapse_ok and mass_ok and captain["pass"]:
        verdict = "PASS_EXACT_OPEN_QUERY_MESSAGE__CONNECTED_BACKBONE_COLLAPSES__GENERAL_3CNF_OPEN"
    elif controls_ok and random_ok and captain["pass"]:
        verdict = "PASS_EXACT_PROJECTION__NO_BACKBONE_COLLAPSE"
    else:
        verdict = "FALSIFIED_EXACT_OPEN_QUERY_MESSAGE"
    result = {
        "schema": "JANUS_TRUMP_OPEN_CONNECTED_QUERY_MESSAGE_GATE_V1",
        "verdict": verdict,
        "controls": controls,
        "random_projection_exactness": random_result,
        "captain_obvious_guard": captain,
        "connected_backbone_ladder": ladder,
        "interpretation": "boundary-separator factorization plus certified existential projection can discharge open factors before physical separation; arbitrary mixed 3-CNF factors remain unresolved",
        "next": "extend the exact message language for arbitrary open 3-CNF factors without enumerating their boundary relation",
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0}
    }
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
