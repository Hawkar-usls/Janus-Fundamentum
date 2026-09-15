#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct.janus_unified_macro_restore_v2 import solve_fail_closed_v2
from experiments.direct.janus_unified_macro_restore_v3 import solve_fail_closed_v3


def compact(r: dict) -> dict:
    tail_events = [e for e in r["events"] if e.get("kind") == "JEC_EXTENSION_TAIL_DESCENT_V3"]
    return {
        "status": r["status"],
        "reason": r["reason"],
        "residual_units": r["residual_units"],
        "progress_phi": r["progress_phi"],
        "extension_count": r["ledger"]["extension_count"],
        "question_count": r["ledger"]["question_count"],
        "proposal_work": r["ledger"]["proposal_work"],
        "elimination_pair_work": r["ledger"]["elimination_pair_work"],
        "verification_work": r["ledger"]["verification_work"],
        "max_state_units": r["ledger"]["max_state_units"],
        "tail_event_count": len(tail_events),
        "tail_pivots": [e["pivots"] for e in tail_events],
        "tail_phi": [[e["before_phi"], e["after_phi"]] for e in tail_events],
    }


def main() -> None:
    f = pigeonhole(5, 4)
    v2 = solve_fail_closed_v2(f, cap_exponent=1, extension_exponent=1)
    v3 = solve_fail_closed_v3(f, cap_exponent=1, extension_exponent=1)

    # PHP(5,4) is UNSAT.  A SAT result is only acceptable if a root witness
    # verifies, in which case the frozen generator itself would be contradicted.
    if v3["status"] == "SAT":
        assert v3["witness"] is not None
        assert base.verify_total_assignment(base.canon_cnf(f), v3["witness"])
        raise AssertionError("PHP_5_4 unexpectedly has a verified SAT witness")

    report = {
        "schema": "JANUS/C025/PHP54-EXTENSION-TAIL-V3/v1",
        "P_VS_NP": "OPEN",
        "frozen_case": "PHP_5_4_C1",
        "N": v3["N"],
        "state_cap": v3["state_cap"],
        "v2": compact(v2),
        "v3": compact(v3),
        "status_changed": v2["status"] != v3["status"],
        "reason_changed": v2["reason"] != v3["reason"],
        "scientific_boundary": {
            "fixed_tail_chain_length": 2,
            "heuristic_promotion": False,
            "unbounded_backtracking": False,
            "general_sat_oracle": False,
            "finite_attack_only": True,
            "universal_cap_availability": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
