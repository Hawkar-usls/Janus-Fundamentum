from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_symbolic_projection.symbolic_projection import (
    build_symbolic_projection,
    compile_symbolic_typed_boundary_projection,
)


def eval_cnf(source, assignment):
    return all(any(bool(assignment[abs(l)]) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None

def wide_edge_case(k=12):
    hpriv, dpriv = k + 1, k + 2
    h = [(-i, -(i + 1), -hpriv) for i in range(1, k)]
    d = [(i, i + 1, dpriv) for i in range(1, k)]
    return tuple(h + d), k + 2


def pure_boundary_wide_case(k=12):
    h = [(-i, -(i + 1), -(i + 2)) for i in range(1, k - 1)]
    d = [(i, i + 1, i + 2) for i in range(1, k - 1)]
    return tuple(h + d), k


def two_cnf_chain_case():
    return ((-1, 3), (-3, 4), (-4, 2), (1, 2, 5)), 5


def unsupported_horn_case():
    return ((-1, -3, 4), (-4, -2, 5), (1, 2, 6)), 6


def projection_unsat_case():
    return ((3,), (-3,)), 3

def verify_terminal(source, n, result):
    actual, _ = brute(source, n)
    st = result["status"]
    if st == "CERTIFIED_SAT_SYMBOLIC_PROJECTION":
        witness = {i: bool(result["witness"].get(i, False)) for i in range(1, n + 1)}
        return actual and eval_cnf(source, witness)
    if st == "CERTIFIED_UNSAT_SYMBOLIC_PROJECTION":
        return not actual
    return True


def random_formula(rng, n, m):
    out = []
    for _ in range(m):
        width = rng.choice((1, 2, 3))
        vs = rng.sample(range(1, n + 1), width)
        out.append(tuple(v if rng.randrange(2) else -v for v in vs))
    return tuple(out)


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}
    wide, nw = wide_edge_case()
    rw = compile_symbolic_typed_boundary_projection(wide, nw)
    checks["wide_edge_closes_sat"] = rw["status"] == "CERTIFIED_SAT_SYMBOLIC_PROJECTION" and verify_terminal(wide, nw, rw)
    recs = rw.get("projection", {}).get("records", [])
    checks["wide_edge_projected_true"] = len(recs) == 2 and all(r["action"] == "PROJECT_UNATE" and len(r["projected_clauses"]) == 0 for r in recs)
    examples["wide_edge"] = {"status": rw["status"], "parent_status": rw.get("parent", {}).get("status"), "records": recs}
    pure, npure = pure_boundary_wide_case()
    rp = compile_symbolic_typed_boundary_projection(pure, npure)
    checks["pure_boundary_wide_stays_open"] = rp["status"] == "OPEN_AFTER_SYMBOLIC_PROJECTION" and rp.get("parent_status") == "OPEN_INTERFACE_WIDTH"

    chain, nc = two_cnf_chain_case()
    pc = build_symbolic_projection(chain, nc)
    two = [r for r in pc.get("records", []) if r["kind"] == "2CNF"]
    checks["two_cnf_chain_projected"] = len(two) == 1 and two[0]["action"] == "PROJECT_2CNF" and (-1, 2) in tuple(two[0]["projected_clauses"])
    rc = compile_symbolic_typed_boundary_projection(chain, nc)
    checks["two_cnf_chain_terminal_exact"] = rc["status"] in {"CERTIFIED_SAT_SYMBOLIC_PROJECTION", "CERTIFIED_UNSAT_SYMBOLIC_PROJECTION"} and verify_terminal(chain, nc, rc)

    uns, nu = unsupported_horn_case()
    pu = build_symbolic_projection(uns, nu)
    kept = [r for r in pu.get("records", []) if r["action"] == "KEPT_UNSUPPORTED"]
    checks["unsupported_preserved"] = len(kept) >= 1 and all(tuple(r["projected_clauses"]) for r in kept)

    bad, nb = projection_unsat_case()
    rb = compile_symbolic_typed_boundary_projection(bad, nb)
    checks["projection_unsat_exact"] = rb["status"] == "CERTIFIED_UNSAT_SYMBOLIC_PROJECTION" and verify_terminal(bad, nb, rb)
    rng = random.Random(20260914)
    exact = []
    terminals = 0
    for _ in range(72):
        n = rng.randint(3, 6)
        src = random_formula(rng, n, rng.randint(2, 10))
        rr = compile_symbolic_typed_boundary_projection(src, n)
        if rr["status"] in {"CERTIFIED_SAT_SYMBOLIC_PROJECTION", "CERTIFIED_UNSAT_SYMBOLIC_PROJECTION"}:
            terminals += 1
            exact.append(verify_terminal(src, n, rr))
        else:
            exact.append(True)
    checks["random_small_exact_72_of_72"] = all(exact)
    checks["random_has_terminal_cases"] = terminals > 0

    import research.tools.apma_symbolic_projection.symbolic_projection as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["random.", "brute", "dpll", "itertools.product", "repeat=n", "minimum_feedback"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = "PASS_APMA_EXACT_SYMBOLIC_TYPED_BOUNDARY_PROJECTION__WIDE_UNATE_COLLAPSES__PURE_BOUNDARY_WIDTH_OPEN" if ok else "FAIL_APMA_SYMBOLIC_TYPED_BOUNDARY_PROJECTION_MISMATCH"
    out = {
        "schema": "JANUS_TRUMP_APMA_SYMBOLIC_TYPED_BOUNDARY_PROJECTION_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "random_controls": {"seed": 20260914, "count": 72, "terminal_count": terminals},
        "captain_guard_hits": hits,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "extend symbolic interface carriers beyond globally unate and 2CNF projection without hidden exponential discovery"
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
