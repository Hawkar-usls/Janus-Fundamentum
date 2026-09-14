from pathlib import Path
import inspect, itertools, json, random, sys, time

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.apma_incidence_2core.incidence_2core import compile_incidence_2core, eval_source
from research.tools.apma_incidence_2core_c2.incidence_2core_c2 import (
    compile_incidence_2core_c2,
    FROZEN_C,
)
from research.tools.apma_trinity_sovereign.trinity_v3 import run_trinity_v3, FROZEN_DOOR_ORDER as V3_ORDER
from research.tools.apma_trinity_sovereign.trinity_v4 import (
    run_trinity_v4,
    akinator_propose,
    FROZEN_DOOR_ORDER as V4_ORDER,
    INCIDENCE_C2,
)


def eval_cnf(source, assignment):
    return all(any(bool(assignment.get(abs(l), False)) == (l > 0) for l in c) for c in source)


def brute(source, n):
    assert n <= 8
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def random_formula(rng, n, m):
    out = []
    for _ in range(m):
        width = rng.randint(1, min(3, n))
        vs = rng.sample(range(1, n + 1), width)
        out.append(tuple(v if rng.randrange(2) else -v for v in vs))
    return tuple(out)


def exact_carrier(source, n, result):
    actual, _ = brute(source, n)
    st = result.get("status", "")
    if st == "CERTIFIED_SAT_INCIDENCE_2CORE_C2":
        return actual and eval_cnf(source, result.get("witness", {}))
    if st == "CERTIFIED_UNSAT_INCIDENCE_2CORE_C2":
        return not actual
    if st == "OPEN_INCIDENCE_2CORE_C2_WIDTH":
        return result.get("enumerated_assignments") == 0
    return False


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


def large_cycle(n=64):
    clauses = []
    for i in range(1, n + 1):
        j = 1 if i == n else i + 1
        clauses.append((i, -j if i % 2 else j))
    return tuple(clauses), n


def small_unsat_cycle():
    return ((1, 2), (-1, 2), (1, -2), (-1, -2)), 2


def small_sat_cycle():
    return ((1, 2), (-2, 3), (-3, -1), (1, -4, 5), (2, 6, -7)), 7


def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}

    checks["frozen_c_is_exactly_2"] = FROZEN_C == 2
    checks["v4_is_v3_plus_one_door"] = tuple(V4_ORDER[:-1]) == tuple(V3_ORDER) and V4_ORDER[-1] == INCIDENCE_C2 and len(V4_ORDER) == len(V3_ORDER) + 1

    sat_src, sat_n = small_sat_cycle()
    c1_sat = compile_incidence_2core(sat_src, sat_n)
    c2_sat = compile_incidence_2core_c2(sat_src, sat_n)
    checks["c2_sat_exact"] = exact_carrier(sat_src, sat_n, c2_sat) and c2_sat.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE_C2"
    checks["c2_exact_bound_sat"] = c2_sat.get("branch_count", 10**9) <= c2_sat.get("polynomial_branch_bound", -1) == c2_sat.get("encoding_size", -1) ** 2
    checks["c1_admitted_sat_consistent"] = c1_sat.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE"

    unsat_src, unsat_n = small_unsat_cycle()
    c2_unsat = compile_incidence_2core_c2(unsat_src, unsat_n)
    checks["c2_unsat_exact"] = exact_carrier(unsat_src, unsat_n, c2_unsat) and c2_unsat.get("status") == "CERTIFIED_UNSAT_INCIDENCE_2CORE_C2"
    checks["c2_unsat_exhaustion_bounded"] = c2_unsat.get("enumerated_assignments") == c2_unsat.get("branch_count") and c2_unsat.get("branch_count", 10**9) <= c2_unsat.get("polynomial_branch_bound", -1)

    big, bn = large_cycle(64)
    big_r = compile_incidence_2core_c2(big, bn)
    checks["too_wide_fails_closed_before_enumeration"] = big_r.get("status") == "OPEN_INCIDENCE_2CORE_C2_WIDTH" and big_r.get("enumerated_assignments") == 0
    checks["too_wide_exact_integer_guard"] = big_r.get("branch_count", 0) > big_r.get("polynomial_branch_bound", 10**100) and big_r.get("polynomial_branch_bound") == big_r.get("encoding_size") ** 2
    examples["large_cycle"] = {k: big_r.get(k) for k in ("status", "core_width", "encoding_size", "branch_count", "polynomial_branch_bound", "enumerated_assignments")}

    rng = random.Random(20260914)
    carrier_exact = []
    c1_to_c2_consistent = []
    c2_terminal = 0
    c2_open = 0
    for _ in range(100):
        n = rng.randint(3, 7)
        src = random_formula(rng, n, rng.randint(1, 14))
        r1 = compile_incidence_2core(src, n)
        r2 = compile_incidence_2core_c2(src, n)
        carrier_exact.append(exact_carrier(src, n, r2))
        if r2.get("status", "").startswith("CERTIFIED_"):
            c2_terminal += 1
        elif r2.get("status") == "OPEN_INCIDENCE_2CORE_C2_WIDTH":
            c2_open += 1
        if r1.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE":
            c1_to_c2_consistent.append(r2.get("status") == "CERTIFIED_SAT_INCIDENCE_2CORE_C2" and eval_cnf(src, r2.get("witness", {})))
        elif r1.get("status") == "CERTIFIED_UNSAT_INCIDENCE_2CORE":
            c1_to_c2_consistent.append(r2.get("status") == "CERTIFIED_UNSAT_INCIDENCE_2CORE_C2")
    checks["random_c2_exact_or_open_100_of_100"] = all(carrier_exact)
    checks["c1_terminal_subset_consistent"] = all(c1_to_c2_consistent)
    examples["random_c2"] = {"count": 100, "seed": 20260914, "terminal_count": c2_terminal, "open_count": c2_open, "c1_terminal_consistency_count": len(c1_to_c2_consistent)}

    frontier_rng = random.Random(20260914)
    v3_open_indices = []
    v4_closed = []
    v4_still_open = []
    v3_terminal_regressions = []
    v4_exact = []
    remaining_four = {0, 9, 27, 40}
    remaining_four_outcomes = {}
    for idx in range(60):
        n = frontier_rng.randint(3, 7)
        src = random_formula(frontier_rng, n, frontier_rng.randint(3, 14))
        old = run_trinity_v3(src, n)
        new = run_trinity_v4(src, n)
        v4_exact.append(exact_trinity(src, n, new))
        old_dec = old["sovereign"]["decision"]
        new_dec = new["sovereign"]["decision"]
        if old_dec == "OPEN_UNKNOWN_STATE_CLASS":
            v3_open_indices.append(idx)
            if new_dec in {"COMMIT_SAT", "COMMIT_UNSAT"}:
                v4_closed.append({"index": idx, "decision": new_dec, "door": new["sovereign"].get("door")})
            else:
                v4_still_open.append({"index": idx, "decision": new_dec})
        else:
            old_pair = (old_dec, old["sovereign"].get("door"))
            new_pair = (new_dec, new["sovereign"].get("door"))
            if old_pair != new_pair:
                v3_terminal_regressions.append({"index": idx, "v3": old_pair, "v4": new_pair})
        if idx in remaining_four:
            remaining_four_outcomes[idx] = {
                "v3": old_dec,
                "v4": new_dec,
                "door": new["sovereign"].get("door"),
                "last_attempt": (new["attempts"][-1]["status"] if new.get("attempts") else None),
            }

    checks["binding_v3_open_count_is_16"] = len(v3_open_indices) == 16
    checks["binding_v3_open_indices_include_frozen_four"] = remaining_four.issubset(set(v3_open_indices))
    checks["v4_exact_60_of_60"] = all(v4_exact)
    checks["v3_terminal_regression_free"] = not v3_terminal_regressions
    checks["frozen_four_processed_without_open_assumption"] = set(remaining_four_outcomes) == remaining_four
    examples["frontier"] = {
        "v3_open_count": len(v3_open_indices),
        "v4_closed_count": len(v4_closed),
        "v4_still_open_count": len(v4_still_open),
        "v4_closed": v4_closed,
        "v4_still_open": v4_still_open,
        "remaining_four_outcomes": remaining_four_outcomes,
        "v3_terminal_regressions": v3_terminal_regressions,
    }

    proposal = akinator_propose(sat_src, sat_n)
    tampered = dict(proposal)
    tampered["door_order"] = list(reversed(proposal["door_order"]))
    tamper_result = run_trinity_v4(sat_src, sat_n, forced_proposal=tampered)
    checks["captain_rejects_tampered_v4_order"] = tamper_result["sovereign"]["decision"] == "ROLLBACK_CAPTAIN_REJECT"
    checks["captain_tamper_preserves_root"] = tamper_result["root_hash"] == tamper_result["sovereign"]["authority_root_hash"] and len(tamper_result["attempts"]) == 0

    import research.tools.apma_incidence_2core_c2.incidence_2core_c2 as c2mod
    import research.tools.apma_trinity_sovereign.trinity_v4 as v4mod
    text = (inspect.getsource(c2mod) + "\n" + inspect.getsource(v4mod)).lower()
    forbidden = ["random.", "itertools.product", "brute(", "minimum_feedback", "treewidth", "backdoor", "score_candidate", "best_cut", "dpll(", "assignment_cube"]
    hits = [x for x in forbidden if x in text]
    checks["captain_guard"] = not hits
    try:
        guard_pos = text.index("if branch_count > polynomial_branch_bound")
        enum_pos = text.index("for mask in range(branch_count)")
        checks["integer_polynomial_guard_precedes_enumeration"] = guard_pos < enum_pos
    except ValueError:
        checks["integer_polynomial_guard_precedes_enumeration"] = False

    ok = all(bool(v) for v in checks.values())
    if ok and not v4_still_open:
        verdict = "PASS_APMA_INCIDENCE_2CORE_FIXED_C2__TRINITY_V4_CLOSES_FROZEN_V3_OPEN_CORPUS__NO_UNIVERSAL_COMPLETENESS_THEOREM"
    elif ok and len(v4_closed) > 0:
        verdict = "PASS_APMA_INCIDENCE_2CORE_FIXED_C2__TRINITY_V4_PARTIALLY_CLOSES_V3_OPEN_CORPUS__OPEN_FRONTIER_REMAINS"
    elif ok:
        verdict = "PASS_APMA_INCIDENCE_2CORE_FIXED_C2__TRINITY_V4_NO_NEW_FROZEN_CLOSURE__OPEN_FRONTIER_REMAINS"
    else:
        verdict = "FAIL_APMA_INCIDENCE_2CORE_FIXED_C2_OR_TRINITY_V4_MISMATCH"

    out = {
        "schema": "JANUS_TRUMP_APMA_INCIDENCE_2CORE_FIXED_C2_TRINITY_V4_GATE_V1",
        "verdict": verdict,
        "checks": checks,
        "examples": examples,
        "captain_guard_hits": hits,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "proved_scope_if_pass": "Arbitrary-sign CNF whose canonical source-incidence 2-core has k variable nodes satisfying exact integer guard 2^k <= L^2. This is equivalent to a fixed-c logarithmic-width family with c=2 up to floor effects.",
        "complexity_claim_if_pass": "At most L^2 canonical core branches, each with polynomial simplification and exact residual incidence-forest messages; fixed degree 2 is polynomial.",
        "not_proved": [
            "No theorem that every CNF satisfies 2^k <= L^2.",
            "No adaptive choice of c is allowed.",
            "Finite closure of the frozen v3 OPEN corpus does not imply a universal Trinity selector theorem.",
            "No SAT-in-P or P=NP claim."
        ],
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
