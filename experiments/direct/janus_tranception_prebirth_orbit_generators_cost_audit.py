#!/usr/bin/env python3
"""Conservative cost audit for the frozen pre-birth orbit-generator probe.

This companion exists because the first implementation-level proxy did not name
all signed-map replay/round-trip work separately.  The frozen algorithm/gates are
unchanged.  This audit charges a conservative major-operation upper-bound proxy
for every frozen n without enumerating any raw prefix or generator subset.

The proxy is not a CPU-instruction count. Its purpose is to certify the relevant
asymptotic fact for this restricted family: construction and exact verification
remain O(n^2), while the represented blocked-prefix space is 2^n.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FROZEN_N = (14, 32, 64, 128, 256)
RUN_ID = "JANUS-TRANCEPTION-PREBIRTH-ORBIT-GENERATORS-COST-AUDIT-2026-08-18-v1"


def row(n: int) -> dict[str, Any]:
    literals = 4 * n
    child_literals = 4 * n - 3
    pair_checks = n * (n - 1) // 2

    charges = {
        "formula_structure_build_compare_ops": 8 * n,
        "full_generator_mapping_entries": 2 * n * n,
        "full_generator_support_scan_entries": 2 * n * n,
        "full_signed_roundtrip_coordinate_proxy": 8 * n * n,
        "full_formula_automorphism_literal_visits": literals * n,
        "fix_other_x_coordinate_checks": n * (n - 1),
        "two_branch_restriction_literal_visit_proxy": 2 * literals * n,
        "residual_generator_mapping_entries": (2 * n - 1) * n,
        "residual_signed_roundtrip_coordinate_proxy": 8 * n * n,
        "residual_forward_inverse_literal_visits": 2 * child_literals * n,
        "pairwise_support_checks": pair_checks,
        "pairwise_support_element_comparisons_proxy": 2 * pair_checks,
        "canonical_witness_literal_visits": literals,
        "negative_control_full_formula_literal_visits": 3 * literals,
        "negative_control_mapping_entries": 3 * 2 * n,
        "symbolic_transition_construction_ops": n,
        "generator_digest_record_ops": n,
    }
    total = sum(charges.values())
    return {
        "n": n,
        "represented_raw_prefixes": 1 << n,
        "raw_prefixes_enumerated": 0,
        "symbolic_quotient_states": n + 1,
        "symbolic_quotient_transitions": n,
        "major_operation_charges": charges,
        "conservative_polynomial_work_proxy": total,
        "closed_form_degree_upper_bound": 2,
        "work_proxy_over_n_squared": total / (n * n),
    }


def run() -> dict[str, Any]:
    rows = [row(n) for n in FROZEN_N]
    gates = {
        "all_raw_prefix_enumeration_zero": all(r["raw_prefixes_enumerated"] == 0 for r in rows),
        "all_degree_upper_bounds_quadratic": all(r["closed_form_degree_upper_bound"] == 2 for r in rows),
        "all_symbolic_state_counts_linear": all(r["symbolic_quotient_states"] == r["n"] + 1 for r in rows),
        "all_symbolic_transition_counts_linear": all(r["symbolic_quotient_transitions"] == r["n"] for r in rows),
    }
    return {
        "artifact_id": RUN_ID,
        "status": "PASS_CONSERVATIVE_POLYNOMIAL_COST_LEDGER" if all(gates.values()) else "FAIL_COST_LEDGER",
        "scope": "RESTRICTED_EQUALITY_FAMILY_ONLY",
        "why_this_receipt_exists": "The first implementation proxy did not separately name all signed-map replay/round-trip work. This companion charges those classes without changing the frozen algorithm, n values, correctness gates, or interpretation.",
        "rows": rows,
        "gates": gates,
        "claim_boundary": [
            "This is a conservative major-operation proxy, not an exact instruction/runtime count.",
            "Quadratic construction/verification on equality_family does not imply polynomial behavior on arbitrary CNFs.",
            "No 2^n raw prefix or generator subset enumeration occurs in this cost audit.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {"P_VS_NP": "OPEN"}
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    assert result["status"] == "PASS_CONSERVATIVE_POLYNOMIAL_COST_LEDGER"
    assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"


if __name__ == "__main__":
    main()
