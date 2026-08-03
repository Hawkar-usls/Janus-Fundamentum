#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json

import janus_c045_joint_basis_discovery as legacy
from janus_c045_basis_portfolio_core import digest
from janus_c045_basis_portfolio_solver import solve_basis_portfolio
from janus_c045_basis_portfolio_verifier_v2 import verify_basis_portfolio_v2


def run_audit(seed: int = 450045) -> dict:
    # Reuse the complete semantic fixture suite, but route every verification
    # through the hardened independent verifier.
    legacy.verify_basis_portfolio = verify_basis_portfolio_v2
    result = legacy.run_audit(seed)
    result.pop("integrity_sha256", None)

    budget_cnf = ((1,),)
    work_refusal = solve_basis_portfolio(
        budget_cnf,
        (),
        nvars_hint=1,
        selector_work_cap=1,
    )
    assert work_refusal["status"] == "OPEN_DISCOVERY_BUDGET"
    assert verify_basis_portfolio_v2(
        budget_cnf, (), work_refusal, nvars_hint=1
    )

    certificate_refusal = solve_basis_portfolio(
        budget_cnf,
        (),
        nvars_hint=1,
        selector_certificate_cap=128,
    )
    assert certificate_refusal["status"] == "OPEN_CERTIFICATE_VOLUME"
    assert verify_basis_portfolio_v2(
        budget_cnf, (), certificate_refusal, nvars_hint=1
    )

    corrupt_open = copy.deepcopy(work_refusal)
    corrupt_open["overflow_evidence"]["selector_work_limit"] = 2
    corrupt_open["integrity_sha256"] = digest(
        {
            key: value
            for key, value in corrupt_open.items()
            if key != "integrity_sha256"
        }
    )
    assert not verify_basis_portfolio_v2(
        budget_cnf, (), corrupt_open, nvars_hint=1
    )

    result.update(
        {
            "selector_work_refusal": work_refusal["status"],
            "selector_certificate_refusal": certificate_refusal["status"],
            "tampered_open_evidence": "REJECTED",
        }
    )
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--seed", type=int, default=450045)
    args = parser.parse_args()
    result = run_audit(args.seed)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["status"] == "PASS"
        assert result["mismatches"] == 0
        assert result["witness_failures"] == 0
        assert result["independent_verification_failures"] == 0
        assert result["selector_work_refusal"] == "OPEN_DISCOVERY_BUDGET"
        assert result["selector_certificate_refusal"] == "OPEN_CERTIFICATE_VOLUME"


if __name__ == "__main__":
    main()
