from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_cotree_cutset.cotree_cutset import compile_log_cotree_cutset
from research.tools.apma_ss_partial_mosaic.partial_mosaic import compile_source_mosaic, solve_mosaic


def eval_cnf(source, assignment):
    return all(any(bool(assignment[abs(l)]) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def verify_terminal(source, n, result):
    if result["status"] == "CERTIFIED_SAT_COTREE_CUTSET":
        return eval_cnf(source, result["witness"])
    if result["status"] == "CERTIFIED_UNSAT_COTREE_CUTSET":
        actual, _ = brute(source, n)
        return not actual
    return True


def signed_cube3():
    return tuple(tuple(signs[i] * (i + 1) for i in range(3)) for signs in itertools.product((-1, 1), repeat=3))


def triangle_sat_case():
    return ((-1, -3, 4), (1, 2, 5), (-2, 3)), 5


def triangle_unsat_case():
    return (
        (1,), (-3,), (1, 3),
        (-1, -2, 4), (-1, -2, -4),
        (2, 3, 5), (2, 3, -5),
    ), 5


def hyperedge_case():
    return ((-1, -4, 5), (1, 2, 6), (-1, 3)), 6


def ring_case(m, rng=None):
    assert m >= 4 and m % 2 == 0
    clauses = []
    for i in range(m):
        left = ((i - 1) % m) + 1
        right = i + 1
        private = m + i + 1
        if i % 2 == 0:
            p = 1 if (rng is not None and rng.randrange(2)) else -1
            clauses.append((-left, -right, p * private))
        else:
            p = -1 if (rng is not None and rng.randrange(2)) else 1
            clauses.append((left, right, p * private))
    return tuple(clauses), 2 * m


def dense_bipartite_case(p=6):
    def e(i, j): return i * p + j + 1
    clauses = []
    for i in range(p):
        row = [e(i, j) for j in range(p)]
        for j in range(p - 2):
            clauses.append(tuple(-v for v in row[j:j + 3]))
    for j in range(p):
        col = [e(i, j) for i in range(p)]
        for i in range(p - 2):
            clauses.append(tuple(col[i:i + 3]))
    return tuple(clauses), p * p


def carriers_individually_sat(source, n):
    from research.tools.apma_ss_provenance.apma_ss_controller import solve_source
    kinds = {"2CNF": "2CNF", "HORN3": "HORN", "DUAL_HORN3": "DUAL_HORN"}
    compiled = compile_source_mosaic(source, n)
    state = compiled["state"]
    seen = 0
    for kind, solver_kind in kinds.items():
        clauses = state["carriers"].get(kind, ())
        if not clauses:
            continue
        seen += 1
        if solve_source(clauses, n, solver_kind)["sat"] is not True:
            return False
    return seen >= 2


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}

    forest = signed_cube3()
    rf = compile_log_cotree_cutset(forest, 3)
    checks["forest_reduces_to_zero_cutset"] = rf["status"] == "CERTIFIED_UNSAT_COTREE_CUTSET" and rf["cutset_size"] == 0 and verify_terminal(forest, 3, rf)

    ts, nts = triangle_sat_case(); rs = compile_log_cotree_cutset(ts, nts)
    checks["triangle_sat_closes"] = rs["status"] == "CERTIFIED_SAT_COTREE_CUTSET" and rs["cutset_size"] == 1 and verify_terminal(ts, nts, rs)
    examples["triangle_sat"] = {k: rs.get(k) for k in ("status", "cutset", "cutset_size", "budget", "branch_count", "total_rows")}

    tu, ntu = triangle_unsat_case(); ru = compile_log_cotree_cutset(tu, ntu)
    checks["triangle_unsat_each_carrier_sat"] = carriers_individually_sat(tu, ntu)
    checks["triangle_unsat_closes"] = ru["status"] == "CERTIFIED_UNSAT_COTREE_CUTSET" and ru["cutset_size"] == 1 and ru["branch_count"] == 2 and verify_terminal(tu, ntu, ru)
    checks["triangle_unsat_row_bound"] = ru.get("total_rows", 10**9) <= ru.get("row_bound", -1)
    examples["triangle_unsat"] = {k: ru.get(k) for k in ("status", "cutset", "cutset_size", "budget", "branch_count", "total_rows", "row_bound")}

    long_ring, nlr = ring_case(64)
    rlr = compile_log_cotree_cutset(long_ring, nlr)
    checks["long_ring_closes"] = rlr["status"] == "CERTIFIED_SAT_COTREE_CUTSET" and rlr["cutset_size"] == 1 and eval_cnf(long_ring, rlr["witness"])
    examples["long_ring"] = {k: rlr.get(k) for k in ("status", "cutset_size", "budget", "branch_count", "total_rows", "module_count", "cotree_edge_count")}

    dense, nd = dense_bipartite_case(6)
    rd = compile_log_cotree_cutset(dense, nd)
    checks["dense_bipartite_opens_cutset_width"] = rd["status"] == "OPEN_CYCLE_CUTSET_WIDTH" and rd["cutset_size"] > rd["budget"]
    examples["dense_bipartite"] = {k: rd.get(k) for k in ("status", "cutset_size", "budget", "module_count", "cotree_edge_count")}

    hyp, nh = hyperedge_case()
    rh = compile_log_cotree_cutset(hyp, nh)
    checks["hyperedge_remains_open"] = rh["status"] == "OPEN_INTERFACE_HYPEREDGE"

    rng = random.Random(20260914)
    random_ok = []
    for _ in range(30):
        m = rng.choice((4, 6))
        src, n = ring_case(m, rng)
        rr = compile_log_cotree_cutset(src, n)
        actual, _ = brute(src, n)
        if rr["status"] == "CERTIFIED_SAT_COTREE_CUTSET":
            random_ok.append(actual and eval_cnf(src, rr["witness"]))
        elif rr["status"] == "CERTIFIED_UNSAT_COTREE_CUTSET":
            random_ok.append(not actual)
        else:
            random_ok.append(False)
    checks["random_admitted_cycles_30_of_30"] = all(random_ok)

    import research.tools.apma_cotree_cutset.cotree_cutset as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["dpll", "random.", "brute", "repeat=n", "minimum_feedback", "best_cutset", "score_candidate"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_EXACT_LOG_COTREE_CUTSET_INTERACTION__SMALL_CYCLES_CLOSED__HIGH_CYCLE_RANK_OPEN"
        if ok else "FAIL_APMA_LOG_COTREE_CUTSET_INTERACTION_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_LOG_COTREE_CUTSET_INTERACTION_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "count": 30},
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "attack high-cycle-rank and/or high-width shared interaction with a symbolic carrier rather than unbounded cutset enumeration",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
