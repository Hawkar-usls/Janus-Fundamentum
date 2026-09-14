from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_dense_bipartite_grid.dense_bipartite_grid import compile_dense_bipartite_grid
from research.tools.apma_trinity_sovereign.trinity_v2 import run_trinity_v2


def eval_cnf(source, assignment):
    return all(any(bool(assignment.get(abs(l), False)) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def grid_family(rows, cols):
    def v(i, j):
        return i * cols + j + 1
    clauses = []
    for i in range(rows):
        for j in range(cols - 2):
            clauses.append(tuple(-v(i, k) for k in range(j, j + 3)))
    for j in range(cols):
        for i in range(rows - 2):
            clauses.append(tuple(v(k, j) for k in range(i, i + 3)))
    return tuple(clauses), rows * cols


def relabel(source, mapping):
    return tuple(tuple((1 if lit > 0 else -1) * mapping[abs(lit)] for lit in c) for c in source)


def witness_ok(source, result):
    return result.get("status") == "CERTIFIED_SAT_DENSE_BIPARTITE_GRID" and eval_cnf(source, result.get("witness", {}))


def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}

    dense, nd = grid_family(6, 6)
    before = run_trinity_v2(dense, nd)
    now = compile_dense_bipartite_grid(dense, nd)
    checks["dense_k66_was_current_portfolio_open"] = before["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS"
    checks["dense_k66_closed_exactly"] = witness_ok(dense, now)
    checks["dense_k66_line_certificate"] = now.get("negative_lines") == 6 and now.get("positive_lines") == 6
    examples["dense_k66"] = {"before": before["sovereign"]["decision"], "after": now.get("status"), "lines": now.get("line_count")}

    rect_ok = []
    for rows, cols in ((3, 5), (4, 7), (7, 4), (8, 9)):
        src, n = grid_family(rows, cols)
        rr = compile_dense_bipartite_grid(src, n)
        rect_ok.append(witness_ok(src, rr))
    checks["rectangular_generalization_4_of_4"] = all(rect_ok)

    rng = random.Random(20260914)
    perm_ok = []
    for _ in range(64):
        rows = rng.randint(3, 7)
        cols = rng.randint(3, 7)
        src, n = grid_family(rows, cols)
        labels = list(range(1, n + 1))
        rng.shuffle(labels)
        mapping = {i + 1: labels[i] for i in range(n)}
        perm = relabel(src, mapping)
        rr = compile_dense_bipartite_grid(perm, n)
        perm_ok.append(witness_ok(perm, rr))
    checks["permuted_admitted_64_of_64"] = all(perm_ok)

    base, nb = grid_family(6, 6)
    mixed = list(base)
    first = mixed[0]
    mixed[0] = (first[0], -first[1], first[2])
    rm = compile_dense_bipartite_grid(tuple(mixed), nb)
    checks["mixed_polarity_fails_closed"] = rm.get("status") == "OPEN_UNSUPPORTED_CLAUSE_SHAPE"

    missing = list(base)
    del missing[1]
    rmiss = compile_dense_bipartite_grid(tuple(missing), nb)
    checks["missing_internal_window_fails_closed"] = rmiss.get("status") == "OPEN_NOT_EXACT_THREE_WINDOW_PATH"

    duplicate = tuple(base) + (base[0],)
    rdup = compile_dense_bipartite_grid(duplicate, nb)
    checks["duplicate_extra_clause_fails_closed"] = rdup.get("status") == "OPEN_NOT_EXACT_THREE_WINDOW_PATH"

    odd = ((-1, -2, -3), (1, 3, 4))
    rodd = compile_dense_bipartite_grid(odd, 4)
    actual_odd, _ = brute(odd, 4)
    checks["nonbipartite_union_is_not_called_unsat"] = actual_odd and rodd.get("status") == "OPEN_NONBIPARTITE_LINE_GRAPH"
    examples["nonbipartite"] = {"actual_sat": actual_odd, "carrier": rodd.get("status")}

    small_ok = []
    for _ in range(24):
        src, n = grid_family(3, 3)
        labels = list(range(1, n + 1))
        rng.shuffle(labels)
        perm = relabel(src, {i + 1: labels[i] for i in range(n)})
        actual, _ = brute(perm, n)
        rr = compile_dense_bipartite_grid(perm, n)
        small_ok.append(actual and witness_ok(perm, rr))
    checks["checker_bruteforce_small_24_of_24"] = all(small_ok)

    import research.tools.apma_dense_bipartite_grid.dense_bipartite_grid as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["itertools.product", "random.", "brute", "dpll", "minimum_feedback", "treewidth", "backdoor", "score_candidate"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_EXACT_DENSE_BIPARTITE_GRID_CARRIER__DENSE_K66_FALSIFIER_CLOSED__MALFORMED_AND_NONBIPARTITE_OPEN"
        if ok else "FAIL_APMA_EXACT_DENSE_BIPARTITE_GRID_CARRIER_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_EXACT_DENSE_BIPARTITE_GRID_CARRIER_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "random_controls": {"seed": 20260914, "permuted_count": 64, "small_bruteforce_count": 24},
        "captain_guard_hits": hits,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "proved_scope": "Exact SAT carrier for all-positive/all-negative exact 3-window path-factor systems whose reconstructed consecutive-adjacency union is bipartite.",
        "not_proved": ["No general dense bipartite interaction theorem.", "No decision procedure for nonbipartite reconstructed unions.", "No universal 3SAT selector theorem."],
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "Import this carrier into Trinity, then attack pure_boundary_wide and the remaining OPEN random controls or generalize from exact 3-window paths to a proof-carrying bounded-pattern line language."
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
