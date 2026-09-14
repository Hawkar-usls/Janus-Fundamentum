from pathlib import Path
import hashlib, inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_trinity_sovereign.trinity_v2 import (
    run_trinity_v2, akinator_propose, FROZEN_DOOR_ORDER,
    CYCLE, SYMBOLIC, RENAMABLE,
)
from research.tools.apma_cycle_cut.cycle_cut import compile_canonical_cycle_cut
from research.tools.apma_symbolic_projection.symbolic_projection import compile_symbolic_typed_boundary_projection
from research.tools.apma_renamable_horn.renamable_horn import apply_renaming, compile_renamable_horn

EXPECTED_BLOBS = {
    ROOT / "research/tools/apma_cycle_cut/cycle_cut.py": "899ca44ab8850dff66dd6afff22f0f5dc74897c4",
    ROOT / "research/tools/apma_symbolic_projection/symbolic_projection.py": "1da70f106692ce0a93103b27289b0dc7ea86977e",
    ROOT / "research/tools/apma_renamable_horn/renamable_horn.py": "b9aa81086cc65c14571b42c879f2bdbf63bbb11b",
}


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
    return decision in {"OPEN_UNKNOWN_STATE_CLASS", "ROLLBACK_CAPTAIN_REJECT"}


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
    witness = {e(i, j): bool((i + j) % 2) for i in range(p) for j in range(p)}
    return tuple(clauses), p * p, witness


def random_formula(rng, n, m):
    out = []
    for _ in range(m):
        width = rng.choice((1, 2, 3))
        vs = rng.sample(range(1, n + 1), width)
        out.append(tuple(v if rng.randrange(2) else -v for v in vs))
    return tuple(out)


def direct_terminal_exact(source, n, result):
    actual, _ = brute(source, n)
    st = result["status"]
    if st.startswith("CERTIFIED_SAT"):
        return actual and eval_cnf(source, {int(k): bool(v) for k, v in (result.get("witness") or {}).items()})
    if st.startswith("CERTIFIED_UNSAT"):
        return not actual
    return False


def main():
    t0 = time.perf_counter(); checks = {}; examples = {}; falsifiers = []

    observed = {str(path.relative_to(ROOT)): git_blob_sha(path) for path in EXPECTED_BLOBS}
    checks["sealed_import_blobs_3_of_3"] = all(git_blob_sha(path) == sha for path, sha in EXPECTED_BLOBS.items())
    examples["import_blobs"] = observed

    cyc, cn = triangle_cycle_case()
    direct_cycle = compile_canonical_cycle_cut(cyc, cn)
    checks["cycle_import_executes_exactly"] = direct_cycle["status"] == "CERTIFIED_SAT_CANONICAL_CYCLE_CUT" and direct_terminal_exact(cyc, cn, direct_cycle)
    tr_cycle = run_trinity_v2(cyc, cn)
    checks["trinity_cycle_terminal_exact"] = tr_cycle["sovereign"]["decision"] in {"COMMIT_SAT", "COMMIT_UNSAT"} and exact_trinity(cyc, cn, tr_cycle)
    examples["triangle_cycle"] = {"door": tr_cycle["sovereign"].get("door"), "decision": tr_cycle["sovereign"]["decision"], "direct_status": direct_cycle["status"]}

    wide, wn = wide_edge_case()
    direct_symbolic = compile_symbolic_typed_boundary_projection(wide, wn)
    checks["symbolic_import_executes_exactly"] = direct_symbolic["status"] == "CERTIFIED_SAT_SYMBOLIC_PROJECTION" and direct_terminal_exact(wide, wn, direct_symbolic)
    tr_wide = run_trinity_v2(wide, wn)
    checks["trinity_wide_terminal_exact"] = tr_wide["sovereign"]["decision"] in {"COMMIT_SAT", "COMMIT_UNSAT"} and exact_trinity(wide, wn, tr_wide)
    examples["wide_unate"] = {"door": tr_wide["sovereign"].get("door"), "decision": tr_wide["sovereign"]["decision"], "direct_status": direct_symbolic["status"]}

    high, hn = high_renamable_case()
    direct_ren = compile_renamable_horn(high, hn)
    checks["renamable_import_executes_exactly"] = direct_ren["status"] == "CERTIFIED_SAT_RENAMABLE_HORN" and direct_terminal_exact(high, hn, direct_ren)
    tr_high = run_trinity_v2(high, hn)
    checks["trinity_high_renamable_terminal_exact"] = tr_high["sovereign"]["decision"] in {"COMMIT_SAT", "COMMIT_UNSAT"} and exact_trinity(high, hn, tr_high)
    examples["high_renamable"] = {"door": tr_high["sovereign"].get("door"), "decision": tr_high["sovereign"]["decision"], "direct_status": direct_ren["status"]}

    proposal = akinator_propose(cyc, cn)
    tampered = dict(proposal)
    tampered["door_order"] = list(reversed(proposal["door_order"]))
    tr_bad = run_trinity_v2(cyc, cn, forced_proposal=tampered)
    checks["tampered_order_captain_reject"] = tr_bad["sovereign"]["decision"] == "ROLLBACK_CAPTAIN_REJECT"
    checks["tampered_order_root_preserved"] = tr_bad["root_hash"] == tr_bad["sovereign"]["authority_root_hash"] and len(tr_bad["attempts"]) == 0

    pure, pn = pure_boundary_wide_case()
    tr_pure = run_trinity_v2(pure, pn)
    checks["pure_boundary_no_false_terminal"] = exact_trinity(pure, pn, tr_pure)
    if tr_pure["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS":
        checks["pure_boundary_open_root_preserved"] = tr_pure["root_hash"] == tr_pure["sovereign"]["authority_root_hash"] and tr_pure["sovereign"].get("portfolio_falsifier") is True
        falsifiers.append({"name": "pure_boundary_wide", "n": pn, "clauses": len(pure)})
    else:
        checks["pure_boundary_open_root_preserved"] = True
    examples["pure_boundary_wide"] = {"decision": tr_pure["sovereign"]["decision"], "door": tr_pure["sovereign"].get("door"), "attempts": [(a["door"], a["status"]) for a in tr_pure["attempts"]]}

    dense, dn, known_witness = dense_bipartite_case(6)
    checks["dense_k66_known_sat_witness"] = eval_cnf(dense, known_witness)
    tr_dense = run_trinity_v2(dense, dn)
    dd = tr_dense["sovereign"]["decision"]
    if dd == "COMMIT_SAT":
        checks["dense_k66_no_false_terminal"] = eval_cnf(dense, {int(k): bool(v) for k, v in tr_dense["sovereign"]["witness"].items()})
    elif dd == "COMMIT_UNSAT":
        checks["dense_k66_no_false_terminal"] = False
    else:
        checks["dense_k66_no_false_terminal"] = dd == "OPEN_UNKNOWN_STATE_CLASS" and tr_dense["root_hash"] == tr_dense["sovereign"]["authority_root_hash"]
        if checks["dense_k66_no_false_terminal"]:
            falsifiers.append({"name": "dense_k66_nonrenamable", "n": dn, "clauses": len(dense)})
    examples["dense_k66"] = {"decision": dd, "door": tr_dense["sovereign"].get("door"), "attempts": [(a["door"], a["status"]) for a in tr_dense["attempts"]]}

    rng = random.Random(20260914)
    random_ok = []; random_open = 0; door_counts = {}
    for _ in range(40):
        n = rng.randint(3, 7)
        src = random_formula(rng, n, rng.randint(3, 14))
        rr = run_trinity_v2(src, n)
        random_ok.append(exact_trinity(src, n, rr))
        d = rr["sovereign"].get("door", rr["sovereign"]["decision"])
        door_counts[d] = door_counts.get(d, 0) + 1
        if rr["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS":
            random_open += 1
    checks["random_small_exact_40_of_40"] = all(random_ok)
    examples["random_controls"] = {"seed": 20260914, "count": 40, "open_count": random_open, "terminal_or_open_counts": door_counts}

    import research.tools.apma_trinity_sovereign.trinity_v2 as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["random.", "itertools.product", "brute(", "score_candidate", "best_door", "dpll(", "assignment_cube"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits
    checks["frozen_order_preserved"] = tuple(akinator_propose(cyc, cn)["door_order"]) == tuple(FROZEN_DOOR_ORDER)

    ok = all(bool(v) for v in checks.values())
    if ok and falsifiers:
        verdict = "PASS_APMA_TRINITY_EXECUTABLE_DOORS_IMPORTED__CURRENT_PORTFOLIO_FALSIFIER_FOUND"
    elif ok:
        verdict = "PASS_APMA_TRINITY_EXECUTABLE_DOORS_IMPORTED__NO_FALSIFIER_IN_FROZEN_HUNT__NO_COMPLETENESS_THEOREM"
    else:
        verdict = "FAIL_APMA_TRINITY_EXECUTABLE_DOOR_IMPORT_OR_EXACTNESS_MISMATCH"
    out = {
        "schema": "JANUS_TRUMP_APMA_TRINITY_EXECUTABLE_DOOR_IMPORT_FALSIFIER_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "portfolio_falsifiers": falsifiers,
        "captain_guard_hits": hits,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
        "interpretation": "A found OPEN falsifies completeness of this frozen finite door portfolio only. It is not a hardness proof and not evidence for P!=NP.",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
