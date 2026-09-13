import itertools
import json
import random
from pathlib import Path

from research.tools.structural_residual_canon.structural_canon import (
    normalize_formula, run_boundary_structural, solve_structural_boundary,
    verify_explicit_mapping
)

def clause_sat(clause, assignment):
    if not clause:
        return False
    return any(assignment[abs(l)] if l > 0 else not assignment[abs(l)] for l in clause)

def brute_histogram(clauses, variables):
    hist = [0] * (len(clauses) + 1)
    for bits in itertools.product((False, True), repeat=len(variables)):
        a = dict(zip(variables, bits))
        score = sum(1 for c in clauses if clause_sat(c, a))
        hist[score] += 1
    return hist

def symmetry_family(k):
    boundary = list(range(1, k + 1))
    ys = list(range(k + 1, 2 * k + 1))
    zs = list(range(2 * k + 1, 3 * k + 1))
    clauses = []
    for x, y, z in zip(boundary, ys, zs):
        clauses += [[x, y, y], [-x, z, z]]
    return clauses, boundary, ys + zs

def selector_family(k):
    boundary = list(range(1, k + 1))
    clauses = []
    internal = []
    nxt = k + 1
    gadget_meta = []
    for j, x in enumerate(boundary, start=3):
        s = j
        a = list(range(nxt, nxt + s + 1)); nxt += s + 1
        b = list(range(nxt, nxt + s + 1)); nxt += s + 1
        internal += a + b
        star_edges = [(a[0], a[t]) for t in range(1, s + 1)]
        path_edges = [(b[t], b[t + 1]) for t in range(s)]
        clauses += [[x, u, v] for u, v in star_edges]
        clauses += [[-x, u, v] for u, v in path_edges]
        gadget_meta.append({"selector": x, "edges": s})
    return clauses, boundary, internal, gadget_meta

def random_case(rng):
    kb = rng.randint(0, 4)
    ki = rng.randint(0, 4)
    boundary = list(range(1, kb + 1))
    internal = list(range(kb + 1, kb + ki + 1))
    pool = boundary + internal
    clauses = []
    if not pool:
        return clauses, boundary, internal
    for _ in range(rng.randint(0, 7)):
        width = rng.randint(1, min(3, len(pool)))
        vs = rng.sample(pool, width)
        clauses.append([v if rng.random() < .5 else -v for v in vs])
    return clauses, boundary, internal

def check_controls():
    controls = {}
    clauses, boundary, internal = symmetry_family(5)
    got = solve_structural_boundary(clauses, boundary, internal)
    want = brute_histogram(clauses, boundary + internal)
    controls["symmetry_exact"] = {
        "pass": got["histogram"] == want,
        "final_boundary_states": len(got["boundary_states"]),
        "peak_boundary_states": got["peak_boundary_states"]
    }
    pin_clauses = [[1, 2, 2], [-1, 3, 3]]
    _, pin_layers, _ = run_boundary_structural(pin_clauses, [1, 2, 3])
    controls["remaining_boundary_pinning"] = {
        "pass": pin_layers[1]["states"] == 2,
        "layer1_states": pin_layers[1]["states"]
    }
    a = normalize_formula([[10]])
    b = normalize_formula([[-20]])
    controls["wrong_bijection_rejected"] = {
        "pass": not verify_explicit_mapping(a, b, {10: 20})
    }
    empty = solve_structural_boundary([[], [1]], [1], [])
    controls["empty_clause_preserved"] = {
        "pass": empty["histogram"] == [1, 1, 0],
        "histogram": empty["histogram"]
    }
    return controls

def random_exactness(seed=20260913, total=64):
    rng = random.Random(seed)
    passed = 0
    failure = None
    for i in range(total):
        clauses, boundary, internal = random_case(rng)
        got = solve_structural_boundary(clauses, boundary, internal)["histogram"]
        want = brute_histogram(clauses, boundary + internal)
        if got == want:
            passed += 1
        elif failure is None:
            failure = {"index": i, "clauses": clauses, "boundary": boundary,
                       "internal": internal, "got": got, "want": want}
    return {"passed": passed, "total": total, "seed": seed, "failure": failure}

def symmetry_ladder(kmax=16):
    out = []
    for k in range(1, kmax + 1):
        clauses, boundary, _ = symmetry_family(k)
        states, layers, stats = run_boundary_structural(clauses, boundary)
        out.append({"k": k, "explicit_rows": 2 ** k,
                    "final_states": len(states),
                    "peak_states": max(x["states"] for x in layers),
                    "mass": sum(states.values()),
                    "verified_merges": stats.get("verified", 0)})
    return out

def selector_ladder(kmax=8):
    out = []
    for k in range(1, kmax + 1):
        clauses, boundary, _, meta = selector_family(k)
        states, layers, stats = run_boundary_structural(clauses, boundary)
        out.append({"k": k, "formula_clauses": len(clauses),
                    "explicit_rows": 2 ** k,
                    "final_states": len(states),
                    "peak_states": max(x["states"] for x in layers),
                    "mass": sum(states.values()),
                    "gadget_edges": [m["edges"] for m in meta],
                    "verified_merges": stats.get("verified", 0)})
    return out

def symbolic_selector_argument(kmax=32):
    checks = []
    for s in range(3, kmax + 3):
        star_deg = tuple(sorted([s] + [1] * s))
        path_deg = tuple(sorted([1, 1] + [2] * (s - 1)))
        checks.append({"edges": s, "star_ne_path": star_deg != path_deg,
                       "star_degree_sequence": star_deg,
                       "path_degree_sequence": path_deg})
    return {
        "pass": all(x["star_ne_path"] for x in checks),
        "checked_edge_counts": [x["edges"] for x in checks],
        "argument": "connected components have unique edge counts; within each component star and path have distinct degree sequences, so every selector bit is recoverable from the residual isomorphism class"
    }

def captain_obvious_guard():
    path = Path(__file__).with_name("structural_canon.py")
    text = path.read_text(encoding="utf-8")
    forbidden = ["itertools.product", "permutations(", "product((False, True)"]
    hits = [x for x in forbidden if x in text]
    return {"pass": not hits, "hits": hits,
            "rule": "candidate may branch quotient states incrementally but may not enumerate all boundary assignments or variable permutations before merge"}

def main():
    controls = check_controls()
    random_result = random_exactness()
    sym = symmetry_ladder()
    selector = selector_ladder()
    symbolic = symbolic_selector_argument()
    captain = captain_obvious_guard()
    exact_ok = all(x["pass"] for x in controls.values()) and random_result["passed"] == random_result["total"]
    sym_ok = all(x["final_states"] == 1 and x["mass"] == 2 ** x["k"] for x in sym)
    selector_exp = all(x["final_states"] == 2 ** x["k"] for x in selector)
    if exact_ok and sym_ok and selector_exp and symbolic["pass"] and captain["pass"]:
        verdict = "PASS_SOUND_STRUCTURAL_RENAMING_MERGE__SYMMETRY_COLLAPSES_BUT_RENAMING_QUOTIENT_STILL_EXPONENTIAL_ON_SELECTOR_FAMILY"
    elif exact_ok and sym_ok and captain["pass"]:
        verdict = "PASS_SOUND_STRUCTURAL_RENAMING_MERGE__NO_EXPONENTIAL_ADVERSARY_OBSERVED"
    else:
        verdict = "FALSIFIED_STRUCTURAL_RENAMING_MERGE"
    result = {
        "schema": "JANUS_TRUMP_STRUCTURAL_RESIDUAL_CANON_GATE_V1",
        "verdict": verdict,
        "controls": controls,
        "random_exactness": random_result,
        "captain_obvious_guard": captain,
        "symmetry_ladder": sym,
        "selector_ladder": selector,
        "selector_argument": symbolic,
        "interpretation": "verified internal-variable renaming can merge structurally identical residual futures without boundary enumeration; however residual isomorphism alone can still expose 2^k exact classes on a polynomial-size selector family",
        "next": "seek a coarser exact query-specific/factorized quotient that can aggregate non-isomorphic residuals by the information actually needed for SAT/occupancy readout, with polynomial update and representation bounds",
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0}
    }
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
