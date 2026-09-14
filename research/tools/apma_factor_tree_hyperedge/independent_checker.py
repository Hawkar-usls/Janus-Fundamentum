from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_factor_tree_hyperedge.factor_tree import compile_factor_tree_hyperedge
from research.tools.apma_typed_module_forest.module_forest import compile_typed_module_forest


def eval_cnf(source, a):
    return all(any(bool(a[abs(l)]) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def verify_terminal(source, n, r):
    actual, _ = brute(source, n)
    if r["status"] == "CERTIFIED_SAT_FACTOR_TREE":
        w = {i: bool(r["witness"].get(i, False)) for i in range(1, n + 1)}
        return actual and eval_cnf(source, w)
    if r["status"] == "CERTIFIED_UNSAT_FACTOR_TREE":
        return not actual
    return False


def prior_hyperedge_case():
    return ((-1, -4, 5), (1, 2, 6), (-1, 3)), 6


def unsat_hyperedge_star():
    source = (
        (-1, -2, -3),
        (1, 4, 5),
        (2,), (3,), (-4,), (-5,),
        (1, 6), (-6,),
    )
    return source, 6


def triangle_cycle_case():
    return ((-1, -3, 4), (1, 2, 5), (-2, 3)), 5


def wide_center_tree(k=12):
    clauses = []
    x = list(range(1, k + 1))
    y0 = k + 1
    y = list(range(y0, y0 + k + 1))
    nxt = y[-1]
    for i in range(k):
        clauses.append((-x[i], -y[i], y[i + 1]))
    for i in range(k):
        a, b = nxt + 1, nxt + 2
        nxt += 2
        clauses.append((x[i], a, b))
    return tuple(clauses), nxt


def random_star_case(rng):
    horn = rng.choice(((-1, -2, -3), (1, -2, -3), (-1, 2, -3), (-1, -2, 3)))
    dual = rng.choice(((1, 4, 5), (-1, 4, 5), (1, -4, 5), (1, 4, -5)))
    q = (rng.choice((-1, 1)), rng.choice((-6, 6)))
    return (horn, dual, q), 6


def main():
    t0 = time.perf_counter()
    checks, examples = {}, {}

    src, n = prior_hyperedge_case()
    prior = compile_typed_module_forest(src, n)
    now = compile_factor_tree_hyperedge(src, n)
    checks["prior_hyperedge_was_open"] = prior["status"] == "OPEN_INTERFACE_HYPEREDGE"
    checks["prior_hyperedge_now_closes"] = verify_terminal(src, n, now)
    checks["variable_degree_three_admitted"] = now.get("max_variable_degree") == 3
    examples["prior_hyperedge"] = {k: now.get(k) for k in (
        "status", "module_count", "row_count", "max_variable_degree", "max_module_boundary", "budget"
    )}

    usrc, un = unsat_hyperedge_star()
    ur = compile_factor_tree_hyperedge(usrc, un)
    checks["unsat_hyperedge_star"] = ur["status"] == "CERTIFIED_UNSAT_FACTOR_TREE" and verify_terminal(usrc, un, ur)
    examples["unsat_hyperedge_star"] = {k: ur.get(k) for k in (
        "status", "module_count", "row_count", "max_variable_degree", "max_module_boundary", "budget"
    )}

    cyc, cn = triangle_cycle_case()
    cr = compile_factor_tree_hyperedge(cyc, cn)
    checks["factor_cycle_stays_open"] = cr["status"] == "OPEN_FACTOR_GRAPH_CYCLE"

    wide, wn = wide_center_tree()
    wr = compile_factor_tree_hyperedge(wide, wn)
    checks["wide_center_tree_stays_open"] = wr["status"] == "OPEN_INTERFACE_WIDTH"
    examples["wide_center"] = {k: wr.get(k) for k in ("status", "budget", "too_wide")}

    rng = random.Random(20260914)
    random_ok = []
    for _ in range(30):
        rsrc, rn = random_star_case(rng)
        rr = compile_factor_tree_hyperedge(rsrc, rn)
        random_ok.append(verify_terminal(rsrc, rn, rr))
    checks["random_admitted_factor_trees_30_of_30"] = all(random_ok)

    import research.tools.apma_factor_tree_hyperedge.factor_tree as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["dpll", "random.", "brute", "repeat=n", "best_cut", "score_candidate"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_EXACT_FACTOR_TREE_HYPEREDGE_INTERACTION__PRIOR_HYPEREDGE_CLOSED__CYCLE_AND_WIDTH_OPEN"
        if ok else "FAIL_APMA_FACTOR_TREE_HYPEREDGE_INTERACTION_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_FACTOR_TREE_HYPEREDGE_INTERACTION_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "count": 30},
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "attack factor-graph cycles and pure-boundary high width without hiding exponential discovery",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
