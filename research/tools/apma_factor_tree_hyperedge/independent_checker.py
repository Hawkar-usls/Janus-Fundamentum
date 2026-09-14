from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_factor_tree_hyperedge.factor_tree import (
    compile_factor_tree_hyperedge,
    encoding_size,
)


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
    return True


def hyperedge_case():
    return ((-1, -4, 5), (1, 2, 6), (-1, 3)), 6


def triangle_case():
    return ((-1, -3, 4), (1, 2, 5), (-2, 3)), 5


def disjoint_case():
    return ((-1, -2, 3), (4, 5, -6)), 6


def wide_center_case(k=12):
    v0 = 1
    shared = list(range(2, 2 + k))
    nextv = 2 + k
    clauses = []
    for v in shared:
        p = nextv; q = nextv + 1; nextv += 2
        clauses.append((-v, -v0, -p))
        clauses.append((v, q))
    return tuple(clauses), nextv - 1


def chain_case(m, rng=None):
    edges = list(range(1, m))
    nextv = m
    clauses = []
    for i in range(m):
        left = edges[i - 1] if i > 0 else None
        right = edges[i] if i < m - 1 else None
        kind = i % 3
        vals = [v for v in (left, right) if v is not None]
        need = 2 if kind == 0 else 3
        while len(vals) < need:
            vals.append(nextv); nextv += 1
        if kind == 0:
            s1 = -1 if rng and rng.randrange(2) else 1
            s2 = -1 if rng and rng.randrange(2) else 1
            clauses.append((s1 * vals[0], s2 * vals[1]))
        elif kind == 1:
            lits = [-v for v in vals[:3]]
            if rng and rng.randrange(2):
                lits[rng.randrange(3)] *= -1
            clauses.append(tuple(lits))
        else:
            lits = [v for v in vals[:3]]
            if rng and rng.randrange(2):
                lits[rng.randrange(3)] *= -1
            clauses.append(tuple(lits))
    return tuple(clauses), nextv - 1


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}

    hyp, nh = hyperedge_case()
    rh = compile_factor_tree_hyperedge(hyp, nh)
    checks["prior_hyperedge_closes"] = rh["status"] in {"CERTIFIED_SAT_FACTOR_TREE", "CERTIFIED_UNSAT_FACTOR_TREE"} and verify_terminal(hyp, nh, rh)
    checks["degree3_supported"] = rh.get("max_variable_degree", 0) == 3
    examples["hyperedge"] = {k: rh.get(k) for k in ("status", "row_count", "module_count", "max_variable_degree", "max_module_boundary")}
    tri, nt = triangle_case()
    rt = compile_factor_tree_hyperedge(tri, nt)
    checks["factor_cycle_open"] = rt["status"] == "OPEN_FACTOR_GRAPH_CYCLE"

    wide, nw = wide_center_case()
    rw = compile_factor_tree_hyperedge(wide, nw)
    checks["wide_center_open"] = rw["status"] == "OPEN_INTERFACE_WIDTH"
    examples["wide_center"] = {"status": rw["status"], "budget": rw.get("budget")}

    dis, nd = disjoint_case()
    rd = compile_factor_tree_hyperedge(dis, nd)
    checks["disjoint_components_compose"] = rd["status"] == "CERTIFIED_SAT_FACTOR_TREE" and verify_terminal(dis, nd, rd)

    rng = random.Random(20260914)
    random_ok = []
    for _ in range(24):
        src, n = chain_case(rng.randint(2, 6), rng)
        rr = compile_factor_tree_hyperedge(src, n)
        random_ok.append(rr["status"] in {"CERTIFIED_SAT_FACTOR_TREE", "CERTIFIED_UNSAT_FACTOR_TREE"} and verify_terminal(src, n, rr))
    checks["random_admitted_24_of_24"] = all(random_ok)

    src, n = chain_case(32)
    rl = compile_factor_tree_hyperedge(src, n)
    checks["long_chain_terminal"] = rl["status"] in {"CERTIFIED_SAT_FACTOR_TREE", "CERTIFIED_UNSAT_FACTOR_TREE"}
    if checks["long_chain_terminal"]:
        L = encoding_size(src, n)
        checks["long_chain_row_bound"] = rl["row_count"] <= rl["module_count"] * L
    else:
        checks["long_chain_row_bound"] = False
    examples["long_chain"] = {k: rl.get(k) for k in ("status", "row_count", "module_count", "max_variable_degree", "max_module_boundary")}
    import research.tools.apma_factor_tree_hyperedge.factor_tree as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["dpll", "random.", "brute", "product((false, true), repeat=n", "best_", "score_"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_EXACT_FACTOR_TREE_HYPEREDGE_INTERACTION__PRIOR_HYPEREDGE_CLOSED__CYCLE_AND_WIDTH_OPEN"
        if ok else "FAIL_APMA_FACTOR_TREE_HYPEREDGE_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_FACTOR_TREE_HYPEREDGE_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "count": 24},
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "attack cyclic factor graphs or high-width module boundaries without hiding exponential work",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
