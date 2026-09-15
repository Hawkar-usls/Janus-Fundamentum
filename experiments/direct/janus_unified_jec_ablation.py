#!/usr/bin/env python3
from __future__ import annotations

import json
import random
from typing import List

import janus_unified_proof_carrying_akinator_jec as engine


def var_php(p: int, h: int, holes: int) -> int:
    return (p - 1) * holes + h


def pigeonhole(pigeons: int, holes: int) -> List[List[int]]:
    clauses: List[List[int]] = []
    for p in range(1, pigeons + 1):
        clauses.append([var_php(p, h, holes) for h in range(1, holes + 1)])
        for h1 in range(1, holes + 1):
            for h2 in range(h1 + 1, holes + 1):
                clauses.append([-var_php(p, h1, holes), -var_php(p, h2, holes)])
    for h in range(1, holes + 1):
        for p1 in range(1, pigeons + 1):
            for p2 in range(p1 + 1, pigeons + 1):
                clauses.append([-var_php(p1, h, holes), -var_php(p2, h, holes)])
    return clauses


def random_3cnf(n: int, m: int, rng: random.Random) -> List[List[int]]:
    out = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        out.append([v if rng.randrange(2) else -v for v in vs])
    return out


def target_r3_n8_3() -> List[List[int]]:
    rng = random.Random(20260826)
    target = None
    for n in (5, 6, 7, 8):
        for idx in range(5):
            f = random_3cnf(n, 4 * n + 2, rng)
            if n == 8 and idx == 3:
                target = f
    assert target is not None
    return target


def run_without_jec(clauses):
    original = engine.discover_macro_restore
    try:
        engine.discover_macro_restore = lambda state: None
        return engine.solve_fail_closed(clauses, cap_exponent=1, extension_exponent=1)
    finally:
        engine.discover_macro_restore = original


def compact(r):
    kinds = [e.get("kind") for e in r["events"]]
    return {
        "status": r["status"],
        "reason": r["reason"],
        "jec_used": "JEC_MACRO_RESTORE_CAP" in kinds,
        "extension_count": r["ledger"]["extension_count"],
        "question_count": r["ledger"]["question_count"],
        "proposal_work": r["ledger"]["proposal_work"],
        "elimination_pair_work": r["ledger"]["elimination_pair_work"],
        "verification_work": r["ledger"]["verification_work"],
        "proof_bytes": r["ledger"]["proof_bytes"],
        "max_state_units": r["ledger"]["max_state_units"],
    }


def compare(name, clauses):
    with_jec = engine.solve_fail_closed(clauses, cap_exponent=1, extension_exponent=1)
    without_jec = run_without_jec(clauses)
    return {
        "name": name,
        "with_jec": compact(with_jec),
        "without_jec": compact(without_jec),
        "status_changed": with_jec["status"] != without_jec["status"],
        "reason_changed": with_jec["reason"] != without_jec["reason"],
    }


def main() -> None:
    report = {
        "schema": "JANUS/C025/jec-ablation/v1",
        "P_VS_NP": "OPEN",
        "heuristic_promotion": False,
        "comparisons": [
            compare("R3_N8_3_C1", target_r3_n8_3()),
            compare("PHP_5_4_C1", pigeonhole(5, 4)),
        ],
        "interpretation": (
            "Ablation is a finite causal implementation control only. A change from OPEN to a verified terminal "
            "demonstrates that JEC contributed on that frozen input; it does not imply universal cap availability."
        ),
    }
    # We already observed JEC on both frozen with-JEC traces. Keep this as a regression guard.
    assert all(c["with_jec"]["jec_used"] for c in report["comparisons"])
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
