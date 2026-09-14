from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_renamable_horn.renamable_horn import (
    apply_renaming,
    compile_renamable_horn,
    verify_renaming,
)
from research.tools.apma_cotree_cutset.cotree_cutset import compile_log_cotree_cutset


def eval_cnf(source, assignment):
    return all(any(bool(assignment[abs(l)]) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def complete_negative_triples(n):
    return tuple(tuple(-v for v in c) for c in itertools.combinations(range(1, n + 1), 3))


def rename_formula(source, n, flipped):
    flips = {i: (i in set(flipped)) for i in range(1, n + 1)}
    return apply_renaming(source, flips)


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


def signed_cube3():
    return tuple(tuple(signs[i] * (i + 1) for i in range(3)) for signs in itertools.product((-1, 1), repeat=3))


def random_horn(rng, n, m):
    clauses = []
    for _ in range(m):
        w = rng.randint(1, 3)
        vs = rng.sample(range(1, n + 1), w)
        head = rng.randrange(w + 1)
        clause = []
        for i, v in enumerate(vs):
            clause.append(v if i == head and head < w else -v)
        clauses.append(tuple(clause))
    return tuple(clauses)


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}

    n = 14
    base = complete_negative_triples(n)
    flipset = tuple(i for i in range(1, n + 1) if i % 2 == 0)
    high = rename_formula(base, n, flipset)
    prior = compile_log_cotree_cutset(high, n)
    now = compile_renamable_horn(high, n)
    checks["high_width_prior_open"] = prior["status"] in {"OPEN_POST_CUTSET_FOREST", "OPEN_CYCLE_CUTSET_WIDTH", "OPEN_INTERFACE_HYPEREDGE"}
    checks["high_width_renamable_closes"] = now["status"] == "CERTIFIED_SAT_RENAMABLE_HORN" and eval_cnf(high, now["witness"])
    examples["high_width"] = {"prior": prior["status"], "current": now["status"], "flipped_count": len(now.get("certificate", {}).get("flipped_variables", ())) }

    n2 = 8
    base_unsat = complete_negative_triples(n2) + ((1,), (2,), (3,))
    flipset2 = (2, 4, 6, 8)
    unsat_src = rename_formula(base_unsat, n2, flipset2)
    unsat_res = compile_renamable_horn(unsat_src, n2)
    actual_unsat, _ = brute(unsat_src, n2)
    checks["renamable_unsat_closes"] = unsat_res["status"] == "CERTIFIED_UNSAT_RENAMABLE_HORN" and not actual_unsat

    dense, nd = dense_bipartite_case(6)
    dense_res = compile_renamable_horn(dense, nd)
    checks["dense_k66_remains_open"] = dense_res["status"] == "OPEN_NOT_RENAMABLE_HORN"
    examples["dense_k66"] = {"status": dense_res["status"], "flip_constraints": dense_res.get("flip_constraint_count")}

    cube = signed_cube3()
    cube_res = compile_renamable_horn(cube, 3)
    checks["signed_cube_remains_open"] = cube_res["status"] == "OPEN_NOT_RENAMABLE_HORN"

    good_flips = {i: (i in set(now["certificate"]["flipped_variables"])) for i in range(1, n + 1)}
    bad_flips = dict(good_flips)
    for i in (1, 2, 3):
        bad_flips[i] = not bad_flips[i]
    checks["corrupted_flip_rejected"] = not verify_renaming(high, bad_flips)

    rng = random.Random(20260914)
    random_ok = []
    for _ in range(64):
        nr = 6
        horn = random_horn(rng, nr, rng.randint(5, 14))
        flips = tuple(i for i in range(1, nr + 1) if rng.randrange(2))
        src = rename_formula(horn, nr, flips)
        rr = compile_renamable_horn(src, nr)
        actual, _ = brute(src, nr)
        if rr["status"] == "CERTIFIED_SAT_RENAMABLE_HORN":
            random_ok.append(actual and eval_cnf(src, rr["witness"]))
        elif rr["status"] == "CERTIFIED_UNSAT_RENAMABLE_HORN":
            random_ok.append(not actual)
        else:
            random_ok.append(False)
    checks["random_renamable_horn_64_of_64"] = all(random_ok)

    import research.tools.apma_renamable_horn.renamable_horn as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["dpll", "random.", "brute", "itertools.product", "best_flip", "score_candidate"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_EXACT_RENAMABLE_HORN_HIGH_WIDTH_MORPH__PRIOR_WIDTH_OPEN_CLOSED__NONRENAMABLE_OPEN"
        if ok else "FAIL_APMA_RENAMABLE_HORN_HIGH_WIDTH_MORPH_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_RENAMABLE_HORN_HIGH_WIDTH_MORPH_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "count": 64},
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "next": "add q-Horn or another proof-carrying high-width carrier; do not infer universality from renamable-Horn coverage",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
