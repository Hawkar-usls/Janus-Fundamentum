from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import inspect
import itertools
import json
import time

from research.tools.apma_ss_provenance.apma_ss_controller import encode_c023
from research.tools.apma_dense_cardinality.apma_dense_cardinality import eval_cardinality
from research.tools.apma_ss_portfolio.apma_ss_portfolio import MORPH_CATALOG, run_portfolio


def eval_cnf(cnf, assignment):
    return all(any(bool(assignment[abs(l)]) == (l > 0) for l in clause) for clause in cnf)


def brute_sat(cnf, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(cnf, a):
            return True, a
    return False, None


def corrupt_provenance(image):
    out = {**image, "provenance": dict(image["provenance"])}
    out["provenance"]["schema"] = "BROKEN_FOR_APMA_SS_CONTROL"
    return out

def dense_positive(n):
    return tuple(tuple(c) for c in itertools.combinations(range(1, n + 1), 3))


def controls():
    return {
        "HORN_SAT": (((1,), (-1, 2), (-2, -3, 4), (-4, 5)), 5),
        "HORN_UNSAT": (((1,), (-1, 2), (-2, 3), (-3,)), 3),
        "DUAL_HORN": (((-1, 2, 3), (-2, 4, 5), (1, 3, 5), (-4, 2, 5)), 5),
        "TWO_CNF": (((1, 2), (-1, 3), (-2, -3), (2, -4), (4,)), 4),
        "GENERAL_3CNF": (((1, 2, -3), (-1, -2, 3), (1, -2, -3)), 3),
    }


def ledger_rollbacks_exact(result):
    start = result["checkpoint_hash"]
    for row in result["ledger"]:
        if "ROLLED_BACK" in row["status"]:
            if not row.get("rollback_exact"):
                return False
            if row.get("rollback_hash") != start or row.get("checkpoint_hash") != start:
                return False
    return True


def expected_terminal_ok(name, source, n, result):
    sat, witness = brute_sat(source, n)
    if name == "GENERAL_3CNF":
        return result["status"] == "OPEN_GENERAL_SOURCE_3CNF" and not result["terminal"]
    expected = "CERTIFIED_SAT" if sat else "CERTIFIED_UNSAT"
    if result["status"] != expected or not result["terminal"]:
        return False
    if sat and not eval_cnf(source, result["witness"]):
        return False
    return True

def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}

    for name, (source, n) in controls().items():
        image = corrupt_provenance(encode_c023(source, n))
        result = run_portfolio(image)
        examples[name] = result
        checks[name + "_SEMANTICS"] = expected_terminal_ok(name, source, n, result)
        checks[name + "_ROLLBACK"] = ledger_rollbacks_exact(result)
        if name != "GENERAL_3CNF":
            checks[name + "_PATH"] = (
                result["attempt_count"] == 3
                and [row["morph"] for row in result["ledger"]] == list(MORPH_CATALOG)
                and result["ledger"][0]["status"] == "MORPH_FAIL_ROLLED_BACK"
                and result["ledger"][1]["status"] == "MORPH_FAIL_ROLLED_BACK"
                and result["ledger"][2]["status"] == "MORPH_PASS_TERMINAL"
            )

    dense_source = dense_positive(6)
    dense_image = corrupt_provenance(encode_c023(dense_source, 6))
    dense_result = run_portfolio(dense_image)
    examples["DENSE_POSITIVE"] = dense_result
    checks["DENSE_PATH"] = dense_result["attempt_count"] == 2 and [x["morph"] for x in dense_result["ledger"]] == list(MORPH_CATALOG[:2])
    checks["DENSE_CARDINALITY_TERMINAL"] = dense_result["status"] == "CARDINALITY_CARRIER" and dense_result["terminal"]
    checks["DENSE_ROLLBACK"] = ledger_rollbacks_exact(dense_result)
    dense_semantic = True
    for bits in itertools.product((False, True), repeat=6):
        a = {i + 1: bits[i] for i in range(6)}
        full = {i: a[i] for i in range(1, 7)}
        full.update({6 + i: not a[i] for i in range(1, 7)})
        if eval_cnf(dense_source, a) != eval_cardinality(dense_result["carrier"], full):
            dense_semantic = False
            break
    checks["DENSE_EXHAUSTIVE_SEMANTICS"] = dense_semantic

    bad_affine = corrupt_provenance(encode_c023(controls()["TWO_CNF"][0], 4))
    rows = list(bad_affine["affine"])
    rows[0] = (rows[0][0], 0)
    bad_affine["affine"] = tuple(rows)
    corrupt_result = run_portfolio(bad_affine)
    examples["CORRUPT_AFFINE"] = corrupt_result
    checks["CORRUPT_AFFINE_OPEN"] = corrupt_result["status"] == "OPEN_NO_AUTHORIZED_MORPH"
    checks["CORRUPT_AFFINE_ROLLBACK"] = ledger_rollbacks_exact(corrupt_result)

    import research.tools.apma_ss_portfolio.apma_ss_portfolio as candidate
    text = inspect.getsource(candidate).lower()
    forbidden = ["random.", "dpll", "best_of", "score_candidate", "itertools.product"]
    hits = [token for token in forbidden if token in text]
    checks["CAPTAIN_GUARD"] = not hits
    checks["FIXED_CATALOG_SIZE"] = len(MORPH_CATALOG) == 3
    checks["ATTEMPT_BOUND"] = all(ex["attempt_count"] <= len(MORPH_CATALOG) for ex in examples.values())
    ok = all(bool(v) for v in checks.values())
    out = {
        "schema": "JANUS_TRUMP_APMA_SS_NONSYMMETRIC_MORPH_PORTFOLIO_GATE_V1",
        "verdict": (
            "PASS_APMA_SS_NONSYMMETRIC_PORTFOLIO__ROLLBACK_EXACT__GENERAL_3CNF_OPEN"
            if ok else "FAIL_SEMANTIC_OR_ROLLBACK_MISMATCH"
        ),
        "checks": checks,
        "captain_guard_hits": hits,
        "examples": examples,
        "runtime_ms": round((time.perf_counter() - t0) * 1000, 3),
        "scientific_status": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "Pi_negative_evidence_weight": 0,
        },
        "next": "expand exact morph catalog only by preregistered proof-carrying child gates; do not infer universality from finite portfolio coverage",
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
