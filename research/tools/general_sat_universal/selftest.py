#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from switching_normal_form import build_receipt
from independent_switching_checker import verify


def main() -> int:
    controls = [
        {"name": "mixed_sat", "clauses": [[1, -2, 3], [-1, 2, 4], [2, -3, -4]]},
        {"name": "two_var_unsat", "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]},
        {"name": "tautology_and_duplicates", "clauses": [[1, -1, 2], [2, 2, -3], [-2, 3]]},
        {"name": "unit_mix", "clauses": [[1], [-2], [-1, 2, 3]]},
    ]

    for control in controls:
        receipt = build_receipt(control["clauses"])
        checked = verify(receipt, exhaustive_limit=16)
        assert checked["verdict"] == "PASS_EXACT_SWITCHING_NORMAL_FORM_CHECK"
        assert checked["semantic_coordinate_change_verified"] is True
        print(control["name"], checked["verdict"], "D=", checked["defect_dimension"])

    # Linear-defect control: n=m=7, each variable has degree 3.
    n = 7
    clauses = []
    for i in range(1, n + 1):
        a = i
        b = (i % n) + 1
        c = ((i + 1) % n) + 1
        # deterministic mixed signs, irrelevant to the dimension calculation
        clauses.append([a, -b if i % 2 else b, -c if i % 3 == 0 else c])
    receipt = build_receipt(clauses)
    checked = verify(receipt, exhaustive_limit=16)
    assert checked["incidence_count"] == 3 * n
    assert checked["active_variable_count"] == n
    assert checked["defect_dimension"] == 2 * n
    print("linear_defect_control", checked["verdict"], "D=", checked["defect_dimension"])

    print("PASS_SWITCHING_NORMAL_FORM_SELFTEST")
    print("GENERAL_SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
