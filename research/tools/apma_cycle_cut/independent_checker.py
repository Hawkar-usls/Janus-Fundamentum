from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_cycle_cut.cycle_cut import compile_canonical_cycle_cut
from research.tools.apma_typed_module_forest.module_forest import encoding_size


def eval_cnf(source, a):
    return all(any(bool(a[abs(l)]) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def verify(source, n, result):
    actual, _ = brute(source, n)
    st = result["status"]
    if st in {"CERTIFIED_SAT_CANONICAL_CYCLE_CUT", "CERTIFIED_SAT_MODULE_FOREST"}:
        w = {i: bool(result.get("witness", {}).get(i, False)) for i in range(1, n + 1)}
        return actual and eval_cnf(source, w)
    if st in {"CERTIFIED_UNSAT_CANONICAL_CYCLE_CUT", "CERTIFIED_UNSAT_MODULE_FOREST"}:
        return not actual
    return True

def triangle_case():
    return (
        (-1, -3, 4),
        (1, 2, 5),
        (-2, 3),
    ), 5


def four_cycle_case():
    return (
        (-4, -1, -5),
        (1, 2, 6),
        (-2, -3, -7),
        (3, 4, 8),
    ), 8


def signed_cube3():
    return tuple(
        tuple(signs[i] * (i + 1) for i in range(3))
        for signs in itertools.product((-1, 1), repeat=3)
    )


def hyperedge_case():
    return (
        (-1, -4, 5),
        (1, 2, 6),
        (-1, 3),
    ), 6


def wide_edge_case(k=12):
    hpriv, dpriv = k + 1, k + 2
    h = [(-i, -(i + 1), -hpriv) for i in range(1, k)]
    d = [(i, i + 1, dpriv) for i in range(1, k)]
    return tuple(h + d), k + 2

def many_triangles_case(m=12):
    clauses = []
    nextv = 0
    for _ in range(m):
        a, b, c, ph, pd = range(nextv + 1, nextv + 6)
        nextv += 5
        clauses.append((-a, -c, -ph))
        clauses.append((a, b, pd))
        clauses.append((-b, c))
    return tuple(clauses), nextv


def random_triangle(rng):
    h_private = 4 if rng.randrange(2) else -4
    d_private = -5 if rng.randrange(2) else 5
    q = (rng.choice((-1, 1)) * 2, rng.choice((-1, 1)) * 3)
    return (
        (-1, -3, h_private),
        (1, 2, d_private),
        q,
    ), 5


def forest_regression():
    return (
        (-1, -2, 4),
        (2, 3, 5),
    ), 5


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}
    tri, nt = triangle_case(); rt = compile_canonical_cycle_cut(tri, nt)
    checks["triangle_terminal"] = rt["status"] in {"CERTIFIED_SAT_CANONICAL_CYCLE_CUT", "CERTIFIED_UNSAT_CANONICAL_CYCLE_CUT"}
    checks["triangle_exact"] = verify(tri, nt, rt)
    checks["triangle_cut_width_1"] = rt.get("cut_width") == 1
    examples["triangle"] = {k: rt.get(k) for k in ("status", "cut_width", "budget", "cut_assignment_count", "total_rows")}
    cyc4, n4 = four_cycle_case(); r4 = compile_canonical_cycle_cut(cyc4, n4)
    checks["four_cycle_terminal"] = r4["status"] in {"CERTIFIED_SAT_CANONICAL_CYCLE_CUT", "CERTIFIED_UNSAT_CANONICAL_CYCLE_CUT"}
    checks["four_cycle_exact"] = verify(cyc4, n4, r4)
    checks["four_cycle_cut_width_1"] = r4.get("cut_width") == 1
    examples["four_cycle"] = {k: r4.get(k) for k in ("status", "cut_width", "budget", "cut_assignment_count", "total_rows")}

    sc = signed_cube3(); rs = compile_canonical_cycle_cut(sc, 3)
    checks["signed_cube_unsat"] = rs["status"] == "CERTIFIED_UNSAT_MODULE_FOREST" and verify(sc, 3, rs)
    checks["signed_cube_forest_delegation"] = rs.get("route") == "SEALED_FOREST_DELEGATION"

    fr, nf = forest_regression(); rf = compile_canonical_cycle_cut(fr, nf)
    checks["forest_regression"] = rf["status"] in {"CERTIFIED_SAT_MODULE_FOREST", "CERTIFIED_UNSAT_MODULE_FOREST"} and verify(fr, nf, rf)

    hyp, nh = hyperedge_case(); rh = compile_canonical_cycle_cut(hyp, nh)
    checks["hyperedge_open"] = rh["status"] == "OPEN_INTERFACE_HYPEREDGE"
    wide, nw = wide_edge_case(); rw = compile_canonical_cycle_cut(wide, nw)
    checks["wide_forest_open"] = rw["status"] == "OPEN_INTERFACE_WIDTH"

    many, nm = many_triangles_case(); rm = compile_canonical_cycle_cut(many, nm)
    checks["over_budget_open"] = rm["status"] == "OPEN_CYCLE_CUT_WIDTH"
    if rm["status"] == "OPEN_CYCLE_CUT_WIDTH":
        checks["over_budget_really_over"] = rm["cut_width"] > rm["budget"]
    else:
        checks["over_budget_really_over"] = False
    examples["over_budget"] = {k: rm.get(k) for k in ("status", "cut_width", "budget")}
    rng = random.Random(20260914)
    random_ok = []
    for _ in range(30):
        src, n = random_triangle(rng)
        rr = compile_canonical_cycle_cut(src, n)
        terminal = rr["status"] in {"CERTIFIED_SAT_CANONICAL_CYCLE_CUT", "CERTIFIED_UNSAT_CANONICAL_CYCLE_CUT"}
        random_ok.append(terminal and verify(src, n, rr))
    checks["random_admitted_cycles_30_of_30"] = all(random_ok)

    import research.tools.apma_cycle_cut.cycle_cut as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["dpll", "random.", "minimum_feedback", "best_cut", "brute", "repeat=n"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_EXACT_CANONICAL_CYCLE_CUT_INTERACTION__SMALL_CYCLES_CLOSED__CUT_WIDTH_OPEN"
        if ok else "FAIL_APMA_CANONICAL_CYCLE_CUT_INTERACTION_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_CANONICAL_CYCLE_CUT_INTERACTION_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "count": 30},
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "attack high cycle-cut width and interface hyperedges with exact symbolic interaction carriers",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
