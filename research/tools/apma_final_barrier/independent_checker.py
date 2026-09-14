from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_final_barrier.interaction_barrier import classify_clause, compile_identity_mosaic


def eval_clause(c, a):
    return any(bool(a[abs(l)]) == (l > 0) for l in c)


def eval_formula(source, a):
    return all(eval_clause(c, a) for c in source)


def flatten_carriers(compiled):
    out = []
    for k in ("2CNF", "HORN3", "DUAL_HORN3"):
        out.extend(compiled["carriers"][k])
    return tuple(sorted(out))


def random_formula(rng, n, m):
    out = []
    for _ in range(m):
        w = rng.randint(1, 3)
        vs = rng.sample(range(1, n + 1), w)
        out.append(tuple(v if rng.randrange(2) else -v for v in vs))
    return tuple(out)


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}

    pattern_results = []
    for signs in itertools.product((-1, 1), repeat=3):
        c = tuple(signs[i] * (i + 1) for i in range(3))
        kind, _ = classify_clause(c)
        positives = sum(1 for x in c if x > 0)
        expected = "HORN3" if positives <= 1 else "DUAL_HORN3"
        pattern_results.append(kind == expected)
    checks["all_eight_signed_width3_patterns"] = all(pattern_results)

    width_small = []
    for c in ((1,), (-1,), (1, 2), (1, -2), (-1, -2)):
        width_small.append(classify_clause(c)[0] == "2CNF")
    checks["width1_width2_route_2cnf"] = all(width_small)

    rng = random.Random(20260914)
    recomposition_ok, semantics_ok, linear_ok = [], [], []
    for _ in range(64):
        n = 6
        source = random_formula(rng, n, rng.randint(4, 16))
        comp = compile_identity_mosaic(source)
        recomposition_ok.append(flatten_carriers(comp) == comp["source_clean"])
        in_literals = sum(len(c) for c in comp["source_clean"])
        out_literals = sum(len(c) for c in flatten_carriers(comp))
        linear_ok.append(in_literals == out_literals)
        for _ in range(8):
            a = {i: bool(rng.randrange(2)) for i in range(1, n + 1)}
            semantics_ok.append(eval_formula(comp["source_clean"], a) == eval_formula(flatten_carriers(comp), a))
    checks["random_recomposition_64_of_64"] = all(recomposition_ok)
    checks["random_assignment_semantics"] = all(semantics_ok)
    checks["linear_size_identity"] = all(linear_ok)

    import research.tools.apma_final_barrier.interaction_barrier as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["dpll", "brute", "random.", "itertools.product", "solve_source", "sat_solver"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_FINAL_INTERACTION_COMPLETENESS_BARRIER__UNRESTRICTED_TYPED_INTERACTION_IS_3SAT_IDENTITY_IMAGE"
        if ok else "FAIL_APMA_FINAL_INTERACTION_IDENTITY_BRIDGE_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_FINAL_INTERACTION_COMPLETENESS_BARRIER_V1",
        "verdict": verdict,
        "checks": checks,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "formulas": 64, "assignments_per_formula": 8},
        "theorem_bridge": {
            "reduction": "identity clause partition from arbitrary width<=3 CNF into 2CNF/HORN3/DUAL_HORN3 carriers",
            "size": "linear",
            "semantics": "exact conjunction equality",
            "np_membership": "one Boolean assignment verifies every carrier in linear time",
            "hardness_basis": "standard NP-completeness of 3SAT"
        },
        "consequence": "A polynomial universal compiler deciding unrestricted APMA shared interaction would imply SAT_IN_P and therefore P_EQUALS_NP; current structured PASSes do not establish that compiler.",
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "STOP_APMA_ROUTE_AND_REPORT_EXACT_FRONTIER",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
