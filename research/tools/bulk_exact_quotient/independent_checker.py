import inspect
import itertools
import json
import random
from pathlib import Path

import bulk_quotient as candidate

SEED = 20260913

def sat_clause(clause, assignment):
    if not clause:
        return False
    for lit in clause:
        v = abs(lit)
        val = assignment[v]
        if (lit > 0 and val) or (lit < 0 and not val):
            return True
    return False

def brute_histogram(clauses, variables):
    hist = [0] * (len(clauses) + 1)
    for bits in itertools.product((False, True), repeat=len(variables)):
        a = dict(zip(variables, bits))
        score = sum(1 for c in clauses if sat_clause(c, a))
        hist[score] += 1
    return hist

def future_signature_from_state(state, internal):
    sat0, dead0, residual = state
    m = sat0 + dead0 + len(residual)
    hist = [0] * (m + 1)
    for bits in itertools.product((False, True), repeat=len(internal)):
        a = dict(zip(internal, bits))
        score = sat0 + sum(1 for c in residual if sat_clause(c, a))
        hist[score] += 1
    return hist

def captain_obvious_guard():
    src = inspect.getsource(candidate)
    forbidden = ["itertools.product", "product((False, True)", "range(1 <<"]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "hits": hits}

def random_clause(pool, rng):
    width = rng.randint(0, 3)
    if width == 0:
        return []
    out = []
    for _ in range(width):
        v = rng.choice(pool)
        out.append(v if rng.random() < 0.5 else -v)
    return out

def random_exactness_suite():
    rng = random.Random(SEED)
    passed = 0
    failure = None
    for case in range(64):
        k = rng.randint(1, 5)
        r = rng.randint(0, 3)
        boundary = list(range(1, k + 1))
        internal = list(range(k + 1, k + r + 1))
        pool = boundary + internal
        clauses = [random_clause(pool, rng) for _ in range(rng.randint(0, 8))]
        got = candidate.solve_histogram_bulk(clauses, boundary, internal)["histogram"]
        want = brute_histogram(clauses, boundary + internal)
        if got != want:
            failure = {"case": case, "clauses": clauses, "boundary": boundary,
                       "internal": internal, "got": got, "want": want}
            break
        passed += 1
    return {"passed": passed, "total": 64, "failure": failure}

def irrelevant_control(k=12):
    boundary = list(range(1, k + 1))
    internal = [100]
    clauses = [[100, 100, 100], [-100, -100, -100]]
    out = candidate.solve_histogram_bulk(clauses, boundary, internal)
    boundary_layers = out["layers"][1:k + 1]
    return {
        "pass": all(x["states"] == 1 for x in boundary_layers),
        "states": [x["states"] for x in boundary_layers],
        "histogram_exact": out["histogram"] == brute_histogram(clauses, boundary + internal),
    }

def unitlike_control(k=12):
    boundary = list(range(1, k + 1))
    clauses = [[i, i, i] for i in boundary]
    out = candidate.solve_histogram_bulk(clauses, boundary, [])
    expected = [i + 1 for i in range(1, k + 1)]
    got = [x["states"] for x in out["layers"][1:]]
    return {
        "pass": got == expected and out["histogram"] == brute_histogram(clauses, boundary),
        "states": got,
        "expected": expected,
    }

def empty_clause_control():
    clauses = [[], [1, 1, 1]]
    out = candidate.solve_histogram_bulk(clauses, [1], [])
    dead_seen = any(state[1] >= 1 for state in out["boundary_states"])
    return {
        "pass": dead_seen and out["histogram"] == brute_histogram(clauses, [1]),
        "dead_state_preserved": dead_seen,
        "histogram": out["histogram"],
    }

def bad_merge_control():
    clauses = [[1, 2, 2], [-1, -2, -2], [2, 2, 2]]
    out = candidate.solve_histogram_bulk(clauses, [1], [2])
    states = list(out["boundary_states"])
    same_coarse = len(states) == 2 and states[0][:2] == states[1][:2]
    distinct_residual = len(states) == 2 and states[0][2] != states[1][2]
    sigs = [future_signature_from_state(s, [2]) for s in states]
    return {
        "pass": same_coarse and distinct_residual and len({tuple(x) for x in sigs}) == 2,
        "same_sat_dead": same_coarse,
        "distinct_residual": distinct_residual,
        "future_signatures": sigs,
    }

def semantic_one_class_family(k):
    boundary = list(range(1, k + 1))
    ys = list(range(k + 1, 2 * k + 1))
    zs = list(range(2 * k + 1, 3 * k + 1))
    clauses = []
    for x, y, z in zip(boundary, ys, zs):
        clauses.append([x, y, y])
        clauses.append([-x, z, z])
    _, layers, edges, boundary_map = candidate.run_bulk(clauses, boundary, boundary_len=k)
    boundary_states = len(boundary_map)
    return {
        "k": k,
        "candidate_boundary_states": boundary_states,
        "explicit_rows": 2 ** k,
        "candidate_equals_2_pow_k": boundary_states == 2 ** k,
        "semantic_future_classes_by_family_symmetry": 1,
        "formula_clauses": len(clauses),
        "variables": 3 * k,
    }

def semantic_family_bruteforce_confirmation(k=5):
    info = semantic_one_class_family(k)
    boundary = list(range(1, k + 1))
    ys = list(range(k + 1, 2 * k + 1))
    zs = list(range(2 * k + 1, 3 * k + 1))
    clauses = []
    for x, y, z in zip(boundary, ys, zs):
        clauses += [[x, y, y], [-x, z, z]]
    bulk = candidate.solve_histogram_bulk(clauses, boundary, ys + zs)
    sigs = {tuple(future_signature_from_state(s, ys + zs))
            for s in bulk["boundary_states"]}
    return {"k": k, "unique_future_signatures": len(sigs), "pass": len(sigs) == 1}

def main():
    guard = captain_obvious_guard()
    random_suite = random_exactness_suite()
    controls = {
        "irrelevant": irrelevant_control(),
        "unitlike": unitlike_control(),
        "empty_clause": empty_clause_control(),
        "bad_merge": bad_merge_control(),
    }
    killer = [semantic_one_class_family(k) for k in range(1, 13)]
    killer_confirm = semantic_family_bruteforce_confirmation(5)
    exact_ok = (
        guard["pass"]
        and random_suite["failure"] is None
        and all(x["pass"] for x in controls.values())
        and killer_confirm["pass"]
    )
    hits_exp = all(x["candidate_equals_2_pow_k"] for x in killer)
    if not guard["pass"]:
        verdict = "FALSIFIED_CAPTAIN_OBVIOUS_ENUMERATE_BEFORE_MERGE"
    elif not exact_ok:
        verdict = "FALSIFIED_BY_SEMANTIC_MISMATCH"
    elif hits_exp:
        verdict = "PASS_EXACT_BUT_STATE_GROWTH_REACHES_2_POW_K"
    else:
        verdict = "PASS_EXACT_BULK_QUOTIENT_WITH_SUBEXPONENTIAL_SCOPED_COMPRESSION"
    result = {
        "schema": "JANUS_TRUMP_BULK_EXACT_QUOTIENT_GATE_V1",
        "verdict": verdict,
        "captain_obvious_guard": guard,
        "random_exactness": random_suite,
        "controls": controls,
        "semantic_one_class_killer_ladder": killer,
        "killer_bruteforce_confirmation": killer_confirm,
        "interpretation": (
            "Immediate merge of byte-identical exact residual states is sound and can avoid explicit 2^k rows on compressible families, "
            "but exact residual labels can still force 2^k quotient states even when all boundary assignments have one future occupancy signature by symmetry."
        ),
        "next": (
            "Replace byte-identity residual canonicalization by a stronger exact structure/renaming/factor canonical form that can merge semantically isomorphic future states without enumerating assignments."
        ),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
    }
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if exact_ok else 1)

if __name__ == "__main__":
    main()
