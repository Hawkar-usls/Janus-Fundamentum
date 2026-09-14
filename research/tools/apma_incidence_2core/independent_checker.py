from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_incidence_2core.incidence_2core import (
    compile_incidence_2core, eval_source, encoding_size,
)
from research.tools.apma_trinity_sovereign.trinity_v3 import run_trinity_v3


def eval_cnf(source, assignment):
    return all(any(bool(assignment.get(abs(l), False)) == (l > 0) for l in c) for c in source)


def brute(source, n):
    assert n <= 8
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def exact_or_open(source, n, result):
    status = result.get("status", "")
    if status == "OPEN_INCIDENCE_2CORE_WIDTH":
        return result.get("enumerated_assignments") == 0
    if status == "CERTIFIED_SAT_INCIDENCE_2CORE":
        return eval_cnf(source, result.get("witness", {}))
    if status == "CERTIFIED_UNSAT_INCIDENCE_2CORE":
        actual, _ = brute(source, n)
        return not actual
    return False


def random_formula(rng, n, m):
    out = []
    for _ in range(m):
        width = rng.choice((1, 2, 3))
        vs = rng.sample(range(1, n + 1), width)
        out.append(tuple(v if rng.randrange(2) else -v for v in vs))
    return tuple(out)


def mixed_forest_family(length=40):
    clauses = []
    leaf0 = length + 2
    for i in range(1, length + 1):
        y = leaf0 + i - 1
        clauses.append((i, -(i + 1), y if i % 2 else -y))
    n = 2 * length + 1
    return tuple(clauses), n


def small_cycle_sat_with_trees():
    source = (
        (1, 2),
        (-2, 3),
        (-3, -1),
        (1, -4, 5),
        (2, 6, -7),
    )
    return source, 7


def small_cycle_unsat():
    return ((1, 2), (-1, 2), (1, -2), (-1, -2)), 2


def large_cycle(n=64):
    clauses = []
    for i in range(1, n + 1):
        j = 1 if i == n else i + 1
        clauses.append((i, -j if i % 2 else j))
    return tuple(clauses), n


def relabel(source, mapping):
    return tuple(tuple((1 if lit > 0 else -1) * mapping[abs(lit)] for lit in clause) for clause in source)


def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}

    forest, fn = mixed_forest_family(40)
    rf = compile_incidence_2core(forest, fn)
    checks["large_mixed_forest_terminal"] = rf.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE"
    checks["large_mixed_forest_core_zero"] = rf.get("core_width") == 0
    checks["large_mixed_forest_witness_replays"] = eval_cnf(forest, rf.get("witness", {}))
    examples["large_mixed_forest"] = {k: rf.get(k) for k in ("status", "core_width", "budget", "enumerated_assignments", "branch_bound")}

    sat_src, sat_n = small_cycle_sat_with_trees()
    rs = compile_incidence_2core(sat_src, sat_n)
    actual_sat, _ = brute(sat_src, sat_n)
    checks["small_cyclic_core_sat_exact"] = actual_sat and rs.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE" and eval_cnf(sat_src, rs.get("witness", {}))
    checks["small_cyclic_core_within_budget"] = rs.get("core_width", 999) <= rs.get("budget", -1)
    checks["small_cyclic_core_polynomial_branch_bound"] = rs.get("branch_bound", 10**9) <= rs.get("encoding_size", -1)
    examples["small_cycle_sat"] = {k: rs.get(k) for k in ("status", "core_width", "budget", "enumerated_assignments", "branch_bound", "encoding_size")}

    unsat_src, unsat_n = small_cycle_unsat()
    ru = compile_incidence_2core(unsat_src, unsat_n)
    actual_unsat, _ = brute(unsat_src, unsat_n)
    checks["small_cyclic_core_unsat_exact"] = (not actual_unsat) and ru.get("status") == "CERTIFIED_UNSAT_INCIDENCE_2CORE"
    checks["unsat_exhaustion_bounded"] = ru.get("enumerated_assignments") == ru.get("branch_bound") and ru.get("branch_bound", 10**9) <= ru.get("encoding_size", -1)
    examples["small_cycle_unsat"] = {k: ru.get(k) for k in ("status", "core_width", "budget", "enumerated_assignments", "branch_bound", "encoding_size")}

    big, bn = large_cycle(64)
    rb = compile_incidence_2core(big, bn)
    checks["large_core_fails_closed_before_enumeration"] = rb.get("status") == "OPEN_INCIDENCE_2CORE_WIDTH" and rb.get("enumerated_assignments") == 0
    checks["large_core_really_exceeds_budget"] = rb.get("core_width", 0) > rb.get("budget", 10**9)
    examples["large_cycle"] = {k: rb.get(k) for k in ("status", "core_width", "budget", "encoding_size", "enumerated_assignments")}

    rng = random.Random(20260914)
    random_exact = []
    terminal_count = 0
    open_count = 0
    for _ in range(100):
        n = rng.randint(2, 7)
        src = random_formula(rng, n, rng.randint(1, 14))
        rr = compile_incidence_2core(src, n)
        random_exact.append(exact_or_open(src, n, rr))
        if rr.get("status", "").startswith("CERTIFIED_"):
            terminal_count += 1
        elif rr.get("status") == "OPEN_INCIDENCE_2CORE_WIDTH":
            open_count += 1
    checks["random_small_exact_or_open_100_of_100"] = all(random_exact)
    examples["random_small"] = {"seed": 20260914, "count": 100, "terminal_count": terminal_count, "open_count": open_count}

    base, base_n = small_cycle_sat_with_trees()
    relabel_ok = []
    for _ in range(32):
        labels = list(range(1, base_n + 1))
        rng.shuffle(labels)
        perm = relabel(base, {i + 1: labels[i] for i in range(base_n)})
        rr = compile_incidence_2core(perm, base_n)
        relabel_ok.append(rr.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE" and eval_cnf(perm, rr.get("witness", {})))
    checks["relabeling_invariant_32_of_32"] = all(relabel_ok)

    frontier_rng = random.Random(20260914)
    target_count = 0
    closed_count = 0
    closed_sat = 0
    closed_unsat = 0
    frontier_exact = []
    newly_closed = []
    still_open = []
    for idx in range(60):
        n = frontier_rng.randint(3, 7)
        src = random_formula(frontier_rng, n, frontier_rng.randint(3, 14))
        tri = run_trinity_v3(src, n)
        if tri["sovereign"]["decision"] != "OPEN_UNKNOWN_STATE_CLASS":
            continue
        target_count += 1
        rr = compile_incidence_2core(src, n)
        frontier_exact.append(exact_or_open(src, n, rr))
        if rr.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE":
            closed_count += 1
            closed_sat += 1
            if len(newly_closed) < 8:
                newly_closed.append({"index": idx, "n": n, "clauses": len(src), "status": rr["status"], "core_width": rr["core_width"], "budget": rr["budget"]})
        elif rr.get("status") == "CERTIFIED_UNSAT_INCIDENCE_2CORE":
            closed_count += 1
            closed_unsat += 1
            if len(newly_closed) < 8:
                newly_closed.append({"index": idx, "n": n, "clauses": len(src), "status": rr["status"], "core_width": rr["core_width"], "budget": rr["budget"]})
        else:
            if len(still_open) < 8:
                still_open.append({"index": idx, "n": n, "clauses": len(src), "status": rr.get("status"), "core_width": rr.get("core_width"), "budget": rr.get("budget")})
    checks["frontier_binding_target_is_16"] = target_count == 16
    checks["frontier_candidate_exact_or_open_16_of_16"] = len(frontier_exact) == 16 and all(frontier_exact)
    examples["trinity_v3_open_frontier"] = {
        "target_count": target_count,
        "closed_count": closed_count,
        "closed_sat": closed_sat,
        "closed_unsat": closed_unsat,
        "still_open_count": target_count - closed_count,
        "newly_closed": newly_closed,
        "still_open": still_open,
    }

    import research.tools.apma_incidence_2core.incidence_2core as cand
    text = inspect.getsource(cand).lower()
    forbidden = ["random.", "minimum_feedback", "treewidth", "backdoor", "score_candidate", "best_cut", "dpll", "brute(", "assignment_cube"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits
    try:
        guard_pos = text.index("if k > budget")
        enum_pos = text.index("for mask in range(branch_count)")
        branch_guard_pos = text.index("if branch_count > l")
        checks["budget_guards_precede_enumeration"] = guard_pos < branch_guard_pos < enum_pos
    except ValueError:
        checks["budget_guards_precede_enumeration"] = False

    ok = all(bool(v) for v in checks.values())
    if ok and closed_count > 0:
        verdict = "PASS_APMA_CANONICAL_INCIDENCE_2CORE_CARRIER__TRINITY_V3_OPEN_FRONTIER_PARTIALLY_CLOSED__WIDTH_FRONTIER_REMAINS"
    elif ok:
        verdict = "PASS_APMA_CANONICAL_INCIDENCE_2CORE_CARRIER__NO_FROZEN_TRINITY_OPEN_CLOSED__WIDTH_FRONTIER_REMAINS"
    else:
        verdict = "FAIL_APMA_CANONICAL_INCIDENCE_2CORE_CARRIER_MISMATCH"

    out = {
        "schema": "JANUS_TRUMP_APMA_MIXED_SIGN_INTERFACE_HYPEREDGE_2CORE_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "proved_scope_if_pass": "Arbitrary-sign CNF whose canonical source-incidence 2-core contains at most floor(log2 L) variable nodes, solved by complete bounded core assignment plus exact residual incidence-forest message passing.",
        "complexity_claim_if_pass": "At most 2^k <= L core branches; each branch uses polynomial simplification and linear forest messages. This is a scoped polynomial carrier, not a general SAT algorithm.",
        "not_proved": [
            "No theorem that every mixed-sign CNF has logarithmic incidence 2-core variable width.",
            "No optimal or minimum feedback-variable set is computed.",
            "No universal Trinity completeness theorem.",
            "No SAT-in-P or P=NP claim."
        ],
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
