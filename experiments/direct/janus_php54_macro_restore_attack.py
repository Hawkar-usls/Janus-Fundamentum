#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as v1
from experiments.direct.janus_unified_macro_restore_v2 import solve_fail_closed_v2


def var_php(p: int, h: int, holes: int) -> int:
    return (p - 1) * holes + h


def pigeonhole(pigeons: int, holes: int):
    clauses = []
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


def compact(result):
    kinds = [e.get("kind") for e in result["events"]]
    macros = [e for e in result["events"] if e.get("kind") == "JEC_MACRO_RESTORE_CAP"]
    return {
        "status": result["status"],
        "reason": result["reason"],
        "residual_units": result["residual_units"],
        "progress_phi": result["progress_phi"],
        "question_count": result["ledger"]["question_count"],
        "extension_count": result["ledger"]["extension_count"],
        "proposal_work": result["ledger"]["proposal_work"],
        "elimination_pair_work": result["ledger"]["elimination_pair_work"],
        "verification_work": result["ledger"]["verification_work"],
        "max_state_units": result["ledger"]["max_state_units"],
        "jec_used": "JEC_MACRO_RESTORE_CAP" in kinds,
        "macro_kinds": [m["macro"]["kind"] for m in macros],
        "macro_occurrences": [m["macro"].get("replaced_occurrences", m["macro"].get("reused_occurrences")) for m in macros],
        "macro_pivots": [m["pivot"] for m in macros],
    }


def main() -> None:
    f = pigeonhole(5, 4)
    old = v1.solve_fail_closed(f, cap_exponent=1, extension_exponent=1)
    new = solve_fail_closed_v2(f, cap_exponent=1, extension_exponent=1)

    if new["status"] == "SAT":
        assert new["witness"] is not None
        assert v1.verify_total_assignment(v1.canon_cnf(f), new["witness"])
        raise AssertionError("PHP_5_4 unexpectedly has a verified SAT witness")

    report = {
        "schema": "JANUS/C025/PHP54-MACRO-RESTORE-ATTACK/v2",
        "P_VS_NP": "OPEN",
        "frozen_case": "PHP_5_4_C1",
        "N": old["N"],
        "state_cap": old["state_cap"],
        "v1_repeated_only": compact(old),
        "v2_exhaustive_or_pairs": compact(new),
        "status_changed": old["status"] != new["status"],
        "reason_changed": old["reason"] != new["reason"],
        "scientific_boundary": {
            "finite_attack_only": True,
            "heuristic_promotion": False,
            "universal_cap_availability": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
