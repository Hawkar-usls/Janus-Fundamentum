from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_trinity_sovereign.trinity import (
    run_trinity, akinator_propose, DIRECT, CARD, FOREST, FACTOR,
)


def eval_cnf(source, assignment):
    return all(any(bool(assignment[abs(l)]) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def exact_outcome(source, n, result):
    actual, _ = brute(source, n)
    decision = result["sovereign"]["decision"]
    if decision == "COMMIT_SAT":
        w = result["sovereign"]["witness"]
        return actual and eval_cnf(source, {int(k): bool(v) for k, v in w.items()})
    if decision == "COMMIT_UNSAT":
        return not actual
    return decision in {"OPEN_UNKNOWN_STATE_CLASS", "ROLLBACK_CAPTAIN_REJECT"}


def complete_negative_triples(n):
    return tuple(tuple(-v for v in c) for c in itertools.combinations(range(1, n + 1), 3))


def signed_cube3():
    return tuple(tuple(signs[i] * (i + 1) for i in range(3))
                 for signs in itertools.product((-1, 1), repeat=3))


def prior_hyperedge_case():
    return ((-1, -4, 5), (1, 2, 6), (-1, 3)), 6


def unsat_hyperedge_star():
    return (
        (-1, -2, -3), (1, 4, 5),
        (2,), (3,), (-4,), (-5,), (1, 6), (-6,),
    ), 6


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


def random_2cnf(rng, n=6, m=12):
    clauses = []
    for _ in range(m):
        a, b = rng.sample(range(1, n + 1), 2)
        clauses.append((rng.choice((-1, 1)) * a, rng.choice((-1, 1)) * b))
    return tuple(clauses), n


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}
    sat2 = ((1, 2), (-1, 2), (1, -2))
    rs = run_trinity(sat2, 2)
    checks["direct_2cnf_sat"] = rs["proposal"]["door"] == DIRECT and exact_outcome(sat2, 2, rs)

    unsat2 = ((1,), (-1,))
    ru = run_trinity(unsat2, 1)
    checks["direct_2cnf_unsat"] = ru["proposal"]["door"] == DIRECT and exact_outcome(unsat2, 1, ru)

    horn = ((-1, -2, 3), (-3, 4), (-4,))
    rh = run_trinity(horn, 4)
    checks["direct_horn"] = rh["proposal"]["door"] == DIRECT and exact_outcome(horn, 4, rh)

    dual = ((1, 2, -3), (3, -4), (4,))
    rd = run_trinity(dual, 4)
    checks["direct_dual_horn"] = rd["proposal"]["door"] == DIRECT and exact_outcome(dual, 4, rd)

    dense = complete_negative_triples(6)
    rc = run_trinity(dense, 6)
    checks["dense_selects_cardinality"] = rc["proposal"]["door"] == CARD
    checks["dense_cardinality_exact"] = exact_outcome(dense, 6, rc)
    examples["dense"] = {"door": rc["proposal"]["door"],
                         "decision": rc["sovereign"]["decision"]}

    cube = signed_cube3()
    rcu = run_trinity(cube, 3)
    checks["signed_cube_selects_forest"] = rcu["proposal"]["door"] == FOREST
    checks["signed_cube_exact"] = exact_outcome(cube, 3, rcu)
    examples["signed_cube"] = {"door": rcu["proposal"]["door"],
                                "decision": rcu["sovereign"]["decision"]}

    hyper, hn = prior_hyperedge_case()
    rhy = run_trinity(hyper, hn)
    checks["hyperedge_selects_factor_tree"] = rhy["proposal"]["door"] == FACTOR
    checks["hyperedge_exact"] = exact_outcome(hyper, hn, rhy)

    ustar, un = unsat_hyperedge_star()
    rus = run_trinity(ustar, un)
    checks["unsat_hyperedge_selects_factor_tree"] = rus["proposal"]["door"] == FACTOR
    checks["unsat_hyperedge_exact"] = exact_outcome(ustar, un, rus)

    cyc, cn = triangle_cycle_case()
    rcy = run_trinity(cyc, cn)
    checks["cycle_fails_closed_open"] = rcy["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS"
    checks["cycle_root_preserved"] = rcy["root_hash"] == rcy["sovereign"]["authority_root_hash"]

    wide, wn = wide_center_tree()
    rwi = run_trinity(wide, wn)
    checks["wide_fails_closed_open"] = rwi["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS"
    checks["wide_root_preserved"] = rwi["root_hash"] == rwi["sovereign"]["authority_root_hash"]

    good = akinator_propose(sat2, 2)
    tampered = dict(good)
    tampered["door"] = FACTOR
    rt = run_trinity(sat2, 2, forced_proposal=tampered)
    checks["tampered_proposal_rejected"] = rt["sovereign"]["decision"] == "ROLLBACK_CAPTAIN_REJECT"
    checks["tampered_root_preserved"] = rt["root_hash"] == rt["sovereign"]["authority_root_hash"]

    rng = random.Random(20260914)
    random_ok = []
    door_counts = {}
    for i in range(40):
        if i % 2:
            src, n = random_star_case(rng)
        else:
            src, n = random_2cnf(rng)
        rr = run_trinity(src, n)
        random_ok.append(exact_outcome(src, n, rr))
        d = rr["proposal"].get("door")
        door_counts[d] = door_counts.get(d, 0) + 1
    checks["random_small_admitted_40_of_40"] = all(random_ok)
    examples["random_door_counts"] = door_counts

    roles = [e["role"] for e in rhy["trace"]]
    checks["trinity_roles_present"] = all(x in roles for x in (
        "AKINATOR", "CAPTAIN_OBVIOUS", "JANUS_DEMIURGE", "JANUS_SOVEREIGN"))
    checks["janus_two_faces_separated"] = roles.index("JANUS_DEMIURGE") < roles.index("JANUS_SOVEREIGN")

    import research.tools.apma_trinity_sovereign.trinity as candidate
    text = inspect.getsource(candidate).lower()
    forbidden = ["itertools.product", "random.", "brute(", "dpll", "score_candidate", "best_candidate"]
    hits = [token for token in forbidden if token in text]
    checks["captain_source_guard"] = not hits
    checks["open_controls_never_halt_mismatch"] = all(
        r["sovereign"]["decision"] != "HALT_INTERNAL_MISMATCH" for r in (rcy, rwi)
    )

    ok = all(bool(v) for v in checks.values())
    verdict = (
        "PASS_APMA_TRINITY_SOVEREIGN_FIRST_RUN__KNOWN_DOORS_SELECTED__UNKNOWN_CLASSES_FAIL_CLOSED"
        if ok else "FAIL_APMA_TRINITY_SOVEREIGN_FIRST_RUN_MISMATCH"
    )
    out = {
        "schema": "JANUS_TRUMP_APMA_TRINITY_SOVEREIGN_FIRST_RUN_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "random_controls": {"seed": 20260914, "count": 40},
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN",
                              "Pi_negative_evidence_weight": 0},
        "next": "import sealed sibling doors explicitly, then attack universal-selector completeness with falsifiers",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
