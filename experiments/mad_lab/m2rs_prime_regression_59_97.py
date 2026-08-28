#!/usr/bin/env python3
"""Prime-only regression for the frozen M2R-S/Tranception runner.

Uses only the frozen public visit()/compare_mirror() interface.  No theorem
promotion is possible here; this is finite experimental replay only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.mad_lab import m2rs_tranception_meet as M

PRIMES = [59, 61, 67, 71, 73, 79, 83, 89, 97]


def run() -> dict:
    rows = []
    for N in PRIMES:
        lr = M.visit(N, "LR")
        rl = M.visit(N, "RL")
        meet = M.compare_mirror(lr, rl)
        rows.append({
            "N": N,
            "direct": lr["direct"]["verdict"],
            "direct_first_open": lr["direct"]["first_open_signature"],
            "m2rs_lr": lr["m2rs"]["verdict"],
            "m2rs_rl": rl["m2rs"]["verdict"],
            "relation_lr": lr["relation"],
            "relation_rl": rl["relation"],
            "meet": meet["verdict"],
            "meet_checks": meet["checks"],
            "action_availability_certified": False,
            "theorem_credit_allowed": False,
            "P_VS_NP": "OPEN",
        })
    return {
        "schema": "JANUS/MAD-LAB/M2RS-PRIME-REGRESSION/v1",
        "primes": PRIMES,
        "rows": rows,
        "all_direct_open": all(r["direct"] == "OPEN" for r in rows),
        "all_mirror_consensus": all(r["meet"] == "MIRROR_CONSENSUS" for r in rows),
        "shadow_selector_advantages": sum(
            r["relation_lr"] == "SHADOW_SELECTOR_ADVANTAGE_ONLY" for r in rows
        ),
        "theorem_credit_allowed": False,
        "P_VS_NP": "OPEN",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("artifacts/mad_lab/m2rs_prime_regression_59_97.json"))
    args = ap.parse_args()
    result = run()
    assert result["P_VS_NP"] == "OPEN"
    assert not result["theorem_credit_allowed"]
    for row in result["rows"]:
        assert row["P_VS_NP"] == "OPEN"
        assert not row["theorem_credit_allowed"]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
