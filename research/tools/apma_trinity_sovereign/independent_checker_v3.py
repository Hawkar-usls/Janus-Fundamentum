from pathlib import Path
import hashlib, inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_trinity_sovereign.trinity_v2 import run_trinity_v2, FROZEN_DOOR_ORDER as V2_ORDER
from research.tools.apma_trinity_sovereign.trinity_v3 import (
    run_trinity_v3, akinator_propose, FROZEN_DOOR_ORDER, IMPORT_PROVENANCE, DENSE,
)
from research.tools.apma_dense_bipartite_grid.dense_bipartite_grid import compile_dense_bipartite_grid
from research.tools.apma_renamable_horn.renamable_horn import apply_renaming

EXPECTED_DENSE_BLOB = "243ee05b8f34c1b67bc5cb14fba5ecbd990ae7f8"
EXPECTED_DENSE_SEAL = "45140abcc163fd99d67c0b94e6fa37d9d6e023e2"
DENSE_PATH = ROOT / "research/tools/apma_dense_bipartite_grid/dense_bipartite_grid.py"


def git_blob_sha(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def eval_cnf(source, assignment):
    return all(any(bool(assignment.get(abs(l), False)) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def exact_trinity(source, n, result):
    actual, _ = brute(source, n)
    decision = result["sovereign"]["decision"]
    if decision == "COMMIT_SAT":
        return actual and eval_cnf(source, {int(k): bool(v) for k, v in result["sovereign"]["witness"].items()})
    if decision == "COMMIT_UNSAT":
        return not actual
    if decision == "OPEN_UNKNOWN_STATE_CLASS":
        return result["root_hash"] == result["sovereign"]["authority_root_hash"]
    if decision == "ROLLBACK_CAPTAIN_REJECT":
        return result["root_hash"] == result["sovereign"]["authority_root_hash"] and len(result["attempts"]) == 0
    return False


def complete_negative_triples(n):
    return tuple(tuple(-v for v in c) for c in itertools.combinations(range(1, n + 1), 3))


def triangle_cycle_case():
    return ((-1, -3, 4), (1, 2, 5), (-2, 3)), 5


def wide_edge_case(k=12):
    hpriv, dpriv = k + 1, k + 2
    h = [(-i, -(i + 1), -hpriv) for i in range(1, k)]
    d = [(i, i + 1, dpriv) for i in range(1, k)]
    return tuple(h + d), k + 2


def pure_boundary_wide_case(k=12):
    h = [(-i, -(i + 1), -(i + 2)) for i in range(1, k - 1)]
    d = [(i, i + 1, i + 2) for i in range(1, k - 1)]
    return tuple(h + d), k


def high_renamable_case(n=14):
    base = complete_negative_triples(n)
    flips = {i: (i % 2 == 0) for i in range(1, n + 1)}
    return apply_renaming(base, flips), n


def dense_bipartite_case(p=6):
    def e(i, j):
        return i * p + j + 1
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


def random_formula(rng, n, m):
    out = []
    for _ in range(m):
        width = rng.choice((1, 2, 3))
        vs = rng.sample(range(1, n + 1), width)
        out.append(tuple(v if rng.randrange(2) else -v for v in vs))
    return tuple(out)


def frozen_prior_cases():
    tri, tn = triangle_cycle_case()
    wide, wn = wide_edge_case()
    high, hn = high_renamable_case()
    return [
        ("native_2cnf", ((1, 2), (-1, 2)), 2),
        ("cardinality", complete_negative_triples(5), 5),
        ("cycle_cut", tri, tn),
        ("symbolic", wide, wn),
        ("renamable", high, hn),
    ]


def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}

    observed_blob = git_blob_sha(DENSE_PATH)
    checks["sealed_dense_blob_exact"] = observed_blob == EXPECTED_DENSE_BLOB
    checks["sealed_dense_provenance_exact"] = (
        IMPORT_PROVENANCE[DENSE]["sealed_commit"] == EXPECTED_DENSE_SEAL
        and IMPORT_PROVENANCE[DENSE]["git_blob_sha1"] == EXPECTED_DENSE_BLOB
    )
    checks["old_seven_order_preserved_and_dense_appended"] = (
        tuple(FROZEN_DOOR_ORDER[:-1]) == tuple(V2_ORDER)
        and FROZEN_DOOR_ORDER[-1] == DENSE
        and len(FROZEN_DOOR_ORDER) == len(V2_ORDER) + 1
    )

    regressions = []
    prior_examples = {}
    for name, source, n in frozen_prior_cases():
        old = run_trinity_v2(source, n)
        new = run_trinity_v3(source, n)
        old_decision = old["sovereign"]["decision"]
        new_decision = new["sovereign"]["decision"]
        old_door = old["sovereign"].get("door")
        new_door = new["sovereign"].get("door")
        exact = exact_trinity(source, n, new)
        same = old_decision == new_decision and old_door == new_door and exact
        if not same:
            regressions.append(name)
        prior_examples[name] = {
            "v2": [old_decision, old_door],
            "v3": [new_decision, new_door],
        }
    checks["frozen_prior_terminal_regression_free"] = not regressions
    examples["prior_terminal_controls"] = prior_examples

    dense, dn = dense_bipartite_case(6)
    old_dense = run_trinity_v2(dense, dn)
    direct_dense = compile_dense_bipartite_grid(dense, dn)
    new_dense = run_trinity_v3(dense, dn)
    checks["dense_was_v2_open"] = old_dense["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS"
    checks["dense_direct_sealed_door_certifies_sat"] = (
        direct_dense.get("status") == "CERTIFIED_SAT_DENSE_BIPARTITE_GRID"
        and eval_cnf(dense, direct_dense.get("witness", {}))
    )
    checks["dense_v3_closes_via_new_door"] = (
        new_dense["sovereign"]["decision"] == "COMMIT_SAT"
        and new_dense["sovereign"].get("door") == DENSE
        and exact_trinity(dense, dn, new_dense)
    )
    examples["dense_k66"] = {
        "v2": old_dense["sovereign"]["decision"],
        "v3": [new_dense["sovereign"]["decision"], new_dense["sovereign"].get("door")],
        "attempts": [(a["door"], a["status"]) for a in new_dense["attempts"]],
    }

    pure, pn = pure_boundary_wide_case()
    old_pure = run_trinity_v2(pure, pn)
    new_pure = run_trinity_v3(pure, pn)
    checks["pure_boundary_v2_was_open"] = old_pure["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS"
    checks["pure_boundary_v3_exact_or_open_root_preserved"] = exact_trinity(pure, pn, new_pure)
    examples["pure_boundary_wide"] = {
        "v2": old_pure["sovereign"]["decision"],
        "v3": [new_pure["sovereign"]["decision"], new_pure["sovereign"].get("door")],
        "attempts": [(a["door"], a["status"]) for a in new_pure["attempts"]],
    }

    proposal = akinator_propose(dense, dn)
    tampered = dict(proposal)
    tampered["door_order"] = list(reversed(proposal["door_order"]))
    bad = run_trinity_v3(dense, dn, forced_proposal=tampered)
    checks["captain_rejects_tampered_v3_order"] = bad["sovereign"]["decision"] == "ROLLBACK_CAPTAIN_REJECT"
    checks["captain_reject_preserves_root"] = (
        bad["root_hash"] == bad["sovereign"]["authority_root_hash"] and len(bad["attempts"]) == 0
    )

    rng = random.Random(20260914)
    random_exact = []
    v2_terminal_regression = []
    open_examples = []
    v2_open = 0
    v3_open = 0
    door_counts = {}
    for idx in range(60):
        n = rng.randint(3, 7)
        src = random_formula(rng, n, rng.randint(3, 14))
        old = run_trinity_v2(src, n)
        new = run_trinity_v3(src, n)
        random_exact.append(exact_trinity(src, n, new))
        if old["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS":
            v2_open += 1
        else:
            if (old["sovereign"]["decision"], old["sovereign"].get("door")) != (
                new["sovereign"]["decision"], new["sovereign"].get("door")
            ):
                v2_terminal_regression.append(idx)
        key = new["sovereign"].get("door", new["sovereign"]["decision"])
        door_counts[key] = door_counts.get(key, 0) + 1
        if new["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS":
            v3_open += 1
            if len(open_examples) < 5:
                open_examples.append({
                    "index": idx,
                    "n": n,
                    "clauses": len(src),
                    "root_hash": new["root_hash"],
                    "attempt_statuses": [(a["door"], a["status"]) for a in new["attempts"]],
                })
    checks["random_v3_exact_60_of_60"] = all(random_exact)
    checks["random_v2_terminal_regression_free"] = not v2_terminal_regression
    examples["random_controls"] = {
        "seed": 20260914,
        "count": 60,
        "v2_open_count": v2_open,
        "v3_open_count": v3_open,
        "v3_terminal_or_open_counts": door_counts,
        "remaining_open_examples": open_examples,
    }

    import research.tools.apma_trinity_sovereign.trinity_v3 as cand
    import research.tools.apma_dense_bipartite_grid.dense_bipartite_grid as dense_cand
    text = (inspect.getsource(cand) + "\n" + inspect.getsource(dense_cand)).lower()
    forbidden = ["random.", "itertools.product", "brute(", "score_candidate", "best_door", "dpll(", "assignment_cube"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits

    remaining_named_falsifiers = []
    if new_pure["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS":
        remaining_named_falsifiers.append("pure_boundary_wide")
    if new_dense["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS":
        remaining_named_falsifiers.append("dense_k66_nonrenamable")

    ok = all(bool(v) for v in checks.values())
    if ok and (remaining_named_falsifiers or v3_open):
        verdict = "PASS_APMA_TRINITY_V3_DENSE_GRID_IMPORTED__KNOWN_FALSIFIER_CLOSED__OPEN_FRONTIER_REMAINS"
    elif ok:
        verdict = "PASS_APMA_TRINITY_V3_DENSE_GRID_IMPORTED__FROZEN_HUNT_ALL_TERMINAL__NO_COMPLETENESS_THEOREM"
    else:
        verdict = "FAIL_APMA_TRINITY_V3_IMPORT_OR_REGRESSION_MISMATCH"

    out = {
        "schema": "JANUS_TRUMP_APMA_TRINITY_IMPORT_DENSE_GRID_RETEST_FRONTIER_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "remaining_named_falsifiers": remaining_named_falsifiers,
        "captain_guard_hits": hits,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "interpretation": "Closing finite frozen falsifiers demonstrates only portfolio growth. Any remaining OPEN falsifies completeness of this finite portfolio only; absence of OPEN in this frozen hunt would still not prove a universal selector theorem.",
        "scientific_status": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "Pi_negative_evidence_weight": 0,
        },
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
