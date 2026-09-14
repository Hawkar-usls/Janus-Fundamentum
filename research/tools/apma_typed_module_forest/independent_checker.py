from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_typed_module_forest.module_forest import (
    compile_typed_module_forest,
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


def signed_cube3():
    out = []
    for signs in itertools.product((-1, 1), repeat=3):
        out.append(tuple(signs[i] * (i + 1) for i in range(3)))
    return tuple(out)


def verify_result(source, n, result):
    actual, _ = brute(source, n)
    st = result["status"]
    if st == "CERTIFIED_SAT_MODULE_FOREST":
        w = {i: bool(result["witness"].get(i, False)) for i in range(1, n + 1)}
        return actual and eval_cnf(source, w)
    if st == "CERTIFIED_UNSAT_MODULE_FOREST":
        return not actual
    return True


def triangle_case():
    return (
        (-1, -3, 4),
        (1, 2, 5),
        (-2, 3),
    ), 5


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


def chain_case(m):
    edge = list(range(1, m))
    nextv = m
    clauses = []
    for i in range(m):
        left = edge[i - 1] if i > 0 else None
        right = edge[i] if i < m - 1 else None
        kind = i % 3
        if kind == 2:
            vals = []
            for v in (left, right):
                if v is not None:
                    vals.append(v)
            while len(vals) < 2:
                nextv += 1; vals.append(nextv)
            clauses.append((vals[0], -vals[1]))
        else:
            vals = []
            for v in (left, right):
                if v is not None:
                    vals.append(v)
            while len(vals) < 3:
                nextv += 1; vals.append(nextv)
            if kind == 0:
                clauses.append(tuple(-v for v in vals[:3]))
            else:
                clauses.append(tuple(v for v in vals[:3]))
    return tuple(clauses), nextv


def random_chain_case(rng, m):
    edge = list(range(1, m))
    nextv = m
    clauses = []
    kinds = []
    for i in range(m):
        choices = [0, 1, 2]
        if kinds:
            choices.remove(kinds[-1])
        kind = rng.choice(choices); kinds.append(kind)
        left = edge[i - 1] if i > 0 else None
        right = edge[i] if i < m - 1 else None
        vals = [v for v in (left, right) if v is not None]
        need = 2 if kind == 2 else 3
        while len(vals) < need:
            nextv += 1; vals.append(nextv)
        if kind == 2:
            s1 = rng.choice((-1, 1)); s2 = rng.choice((-1, 1))
            clauses.append((s1 * vals[0], s2 * vals[1]))
        elif kind == 0:
            lits = [-v for v in vals[:3]]
            if rng.randrange(2): lits[rng.randrange(3)] *= -1
            clauses.append(tuple(lits))
        else:
            lits = [v for v in vals[:3]]
            if rng.randrange(2): lits[rng.randrange(3)] *= -1
            clauses.append(tuple(lits))
    return tuple(clauses), nextv


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}
    sc = signed_cube3(); r = compile_typed_module_forest(sc, 3)
    checks["signed_cube_certified_unsat"] = r["status"] == "CERTIFIED_UNSAT_MODULE_FOREST"
    checks["signed_cube_exact"] = verify_result(sc, 3, r)
    examples["signed_cube"] = {k: r.get(k) for k in ("status", "budget", "row_count", "module_count", "edge_vars")}
    dis = ((-1, -2, 3), (4, 5, -6))
    rd = compile_typed_module_forest(dis, 6)
    checks["disjoint_sat"] = rd["status"] == "CERTIFIED_SAT_MODULE_FOREST" and verify_result(dis, 6, rd)

    tri, nt = triangle_case(); rt = compile_typed_module_forest(tri, nt)
    checks["triangle_open_cycle"] = rt["status"] == "OPEN_MODULE_CYCLE"
    hyp, nh = hyperedge_case(); rh = compile_typed_module_forest(hyp, nh)
    checks["hyperedge_open"] = rh["status"] == "OPEN_INTERFACE_HYPEREDGE"
    wide, nw = wide_edge_case(); rw = compile_typed_module_forest(wide, nw)
    checks["wide_open"] = rw["status"] == "OPEN_INTERFACE_WIDTH"

    small_chain_ok = []
    for m in range(2, 9):
        src, n = chain_case(m)
        rr = compile_typed_module_forest(src, n)
        small_chain_ok.append(rr["status"] in {"CERTIFIED_SAT_MODULE_FOREST", "CERTIFIED_UNSAT_MODULE_FOREST"} and verify_result(src, n, rr))
    checks["small_chains_exact"] = all(small_chain_ok)

    big, nb = chain_case(32); rb = compile_typed_module_forest(big, nb)
    checks["long_chain_terminal"] = rb["status"] in {"CERTIFIED_SAT_MODULE_FOREST", "CERTIFIED_UNSAT_MODULE_FOREST"}
    if checks["long_chain_terminal"]:
        L = encoding_size(big, nb)
        checks["long_chain_row_bound"] = rb["row_count"] <= rb["module_count"] * L
    else:
        checks["long_chain_row_bound"] = False
    examples["long_chain"] = {k: rb.get(k) for k in ("status", "budget", "row_count", "module_count", "max_boundary")}
    rng = random.Random(20260914)
    random_ok = []
    terminal_count = 0
    for _ in range(30):
        m = rng.randint(2, 6)
        src, n = random_chain_case(rng, m)
        rr = compile_typed_module_forest(src, n)
        term = rr["status"] in {"CERTIFIED_SAT_MODULE_FOREST", "CERTIFIED_UNSAT_MODULE_FOREST"}
        terminal_count += int(term)
        random_ok.append(term and verify_result(src, n, rr))
    checks["random_admitted_30_of_30"] = all(random_ok) and terminal_count == 30

    import research.tools.apma_typed_module_forest.module_forest as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["dpll", "random.", "brute", "product((false, true), repeat=n", "product((0, 1), repeat=n"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_EXACT_TYPED_MODULE_FOREST_INTERACTION__SIGNED_CUBE_CLOSED__CYCLE_AND_WIDTH_OPEN"
        if ok else "FAIL_APMA_TYPED_MODULE_FOREST_INTERACTION_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_TYPED_MODULE_FOREST_INTERACTION_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "count": 30},
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "attack cyclic and/or high-boundary typed interaction without hiding exponential discovery",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
