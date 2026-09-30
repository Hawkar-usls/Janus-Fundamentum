#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import random
from typing import Dict, Iterable, List, Sequence

from janus_unified_proof_carrying_akinator_jec import (
    canon_cnf,
    solve_fail_closed,
    verify_total_assignment,
)


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


def xor_constraint(support: Sequence[int], rhs: int) -> List[List[int]]:
    out: List[List[int]] = []
    for bits in itertools.product((0, 1), repeat=len(support)):
        if (sum(bits) & 1) == rhs:
            continue
        # Clause falsified by exactly this forbidden local assignment.
        out.append([v if bit == 0 else -v for v, bit in zip(support, bits)])
    return out


def inconsistent_parity_triangle() -> List[List[int]]:
    clauses: List[List[int]] = []
    clauses += xor_constraint([1, 2], 0)
    clauses += xor_constraint([2, 3], 0)
    clauses += xor_constraint([1, 3], 1)
    return clauses


def equality_chain(n: int) -> List[List[int]]:
    # x_i <-> y_i, variable ids x=1..n, y=n+1..2n.
    clauses: List[List[int]] = []
    for i in range(1, n + 1):
        y = n + i
        clauses.append([-i, y])
        clauses.append([i, -y])
    return clauses


def brute_sat(clauses: Sequence[Sequence[int]], max_vars: int = 10) -> bool | None:
    cnf = canon_cnf(clauses)
    variables = sorted({abs(l) for c in cnf for l in c})
    if len(variables) > max_vars:
        return None
    for bits in itertools.product((0, 1), repeat=len(variables)):
        a = dict(zip(variables, bits))
        if verify_total_assignment(cnf, a):
            return True
    return False


def summarize(name: str, clauses: Sequence[Sequence[int]], cap_exponent: int, extension_exponent: int) -> Dict[str, object]:
    expected = brute_sat(clauses)
    r = solve_fail_closed(
        clauses,
        cap_exponent=cap_exponent,
        extension_exponent=extension_exponent,
    )
    kinds = [e.get("kind") for e in r["events"]]
    terminal_truth = None if r["status"] == "OPEN" else (r["status"] == "SAT")
    if expected is not None and terminal_truth is not None:
        assert terminal_truth == expected, (name, expected, r)
    if r["status"] == "SAT":
        assert verify_total_assignment(canon_cnf(clauses), r["witness"])
    return {
        "name": name,
        "cap_exponent": cap_exponent,
        "extension_exponent": extension_exponent,
        "status": r["status"],
        "reason": r["reason"],
        "N": r["N"],
        "state_cap": r["state_cap"],
        "extension_cap": r["extension_cap"],
        "max_state_units": r["ledger"]["max_state_units"],
        "extension_count": r["ledger"]["extension_count"],
        "question_count": r["ledger"]["question_count"],
        "elimination_pair_work": r["ledger"]["elimination_pair_work"],
        "proposal_work": r["ledger"]["proposal_work"],
        "verification_work": r["ledger"]["verification_work"],
        "proof_bytes": r["ledger"]["proof_bytes"],
        "jec_used": "JEC_MACRO_RESTORE_CAP" in kinds,
        "two_sat_used": "CERTIFICATE_PORTFOLIO_2SAT" in kinds,
        "gf2_used": "CERTIFICATE_PORTFOLIO_GF2" in kinds,
        "bounded_resolution_used": "CERTIFICATE_PORTFOLIO_BOUNDED_RESOLUTION" in kinds,
        "expected_sat_if_bruteforced": expected,
    }


def random_3cnf(n: int, m: int, rng: random.Random) -> List[List[int]]:
    out = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        out.append([v if rng.randrange(2) else -v for v in vs])
    return out


def repeated_pair_pressure(seed: int) -> List[List[int]]:
    # Deliberately repeats (x1 OR x2) through many clauses while mixing a pivot.
    rng = random.Random(seed)
    clauses: List[List[int]] = []
    for i in range(12):
        pivot = 3 if i < 6 else -3
        tail_v = 4 + (i % 4)
        tail = tail_v if rng.randrange(2) else -tail_v
        clauses.append([1, 2, pivot, tail])
    # Add non-pair structure so the instance is not solved by the 2-SAT lane.
    clauses += [[-1, 4, 5], [-2, -4, 6], [3, -5, 7], [-3, 5, -7]]
    return clauses


def main() -> None:
    rows: List[Dict[str, object]] = []

    # Pigeonhole: run loose and tight cap versions.
    for holes in (2, 3, 4):
        f = pigeonhole(holes + 1, holes)
        rows.append(summarize(f"PHP_{holes+1}_{holes}_C2", f, 2, 1))
        rows.append(summarize(f"PHP_{holes+1}_{holes}_C1", f, 1, 1))

    # GF(2)/Tseitin-like inconsistent parity system.
    rows.append(summarize("PARITY_TRIANGLE_UNSAT_C2", inconsistent_parity_triangle(), 2, 1))

    # Hostile equality representation; certificate portfolio should recognize 2-SAT
    # rather than forcing the general eliminator through a bad order.
    rows.append(summarize("EQUALITY_6_C1", equality_chain(6), 1, 1))

    # Deterministic random 3-SAT scaling samples.
    rng = random.Random(20260826)
    for n in (5, 6, 7, 8):
        for idx in range(5):
            f = random_3cnf(n, 4 * n + 2, rng)
            rows.append(summarize(f"R3_N{n}_{idx}_C2", f, 2, 1))
            rows.append(summarize(f"R3_N{n}_{idx}_C1", f, 1, 1))

    # Deterministic JEC-pressure corpus.
    for seed in range(8):
        rows.append(summarize(f"JEC_PRESSURE_{seed}_C1", repeated_pair_pressure(seed), 1, 1))

    status_counts: Dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    report = {
        "schema": "JANUS/C025/unified-family-probe/v1",
        "P_VS_NP": "OPEN",
        "heuristic_promotion": False,
        "cases": len(rows),
        "status_counts": status_counts,
        "jec_used_cases": sum(bool(r["jec_used"]) for r in rows),
        "max_state_units": max(int(r["max_state_units"]) for r in rows),
        "max_elimination_pair_work": max(int(r["elimination_pair_work"]) for r in rows),
        "rows": rows,
        "interpretation": "Finite adversarial probe only. OPEN is a valid refusal and no finite PASS implies a universal polynomial theorem.",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
