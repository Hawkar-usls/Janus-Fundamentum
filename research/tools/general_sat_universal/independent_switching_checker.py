#!/usr/bin/env python3
"""Independent exact checker for the signed-CNF switching-normal-form receipt.

This checker intentionally does not import switching_normal_form.py.
It validates the semantic coordinate change syntactically in O(|I|) time and,
for small controls only, can exhaustively replay the assignment bijection.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from typing import Dict, List, Sequence, Tuple


def pol(lit: int) -> int:
    return 1 if int(lit) < 0 else 0


def lit_for(clause: Sequence[int], v: int) -> int:
    hits = [int(l) for l in clause if abs(int(l)) == v]
    if len(hits) != 1:
        raise AssertionError(f"expected exactly one occurrence of variable {v}")
    return hits[0]


def eval_cnf(cnf: Sequence[Sequence[int]], a: Dict[int, int]) -> bool:
    for clause in cnf:
        if not any((lit > 0 and a[abs(lit)] == 1) or (lit < 0 and a[abs(lit)] == 0) for lit in clause):
            return False
    return True


def verify(receipt_obj: dict, exhaustive_limit: int = 16) -> dict:
    if receipt_obj.get("authority") != "EXACT_NORMAL_FORM_ONLY__NOT_A_SOLVER":
        raise AssertionError("unexpected authority")
    r = receipt_obj["receipt"]
    src: List[List[int]] = r["normalized_input_clauses"]
    dst: List[List[int]] = r["transformed_clauses"]
    if len(src) != len(dst):
        raise AssertionError("clause count changed")

    switch = {int(v): int(b) for v, b in r["switch_by_variable"].items()}
    roots = {int(v): int(i) for v, i in r["root_clause_index_by_variable"].items()}
    variables = sorted(switch)

    inc = 0
    for i, (c0, c1) in enumerate(zip(src, dst)):
        if [abs(x) for x in c0] != [abs(x) for x in c1]:
            raise AssertionError(f"incidence structure changed at clause {i}")
        for a, b in zip(c0, c1):
            v = abs(int(a))
            if pol(int(b)) != (pol(int(a)) ^ switch[v]):
                raise AssertionError(f"bad switched polarity at clause {i}, variable {v}")
            inc += 1

    for v, i in roots.items():
        if pol(lit_for(dst[i], v)) != 0:
            raise AssertionError(f"root incidence not normalized for variable {v}")

    expected_D = inc - len(variables)
    if int(r["incidence_count"]) != inc:
        raise AssertionError("incidence count mismatch")
    if int(r["active_variable_count"]) != len(variables):
        raise AssertionError("active variable count mismatch")
    if int(r["defect_dimension"]) != expected_D:
        raise AssertionError("defect dimension mismatch")

    # Independently check every declared defect against source root polarities.
    expected_rows = []
    for i, clause in enumerate(src):
        for lit in clause:
            v = abs(int(lit))
            rp = pol(lit_for(src[roots[v]], v))
            expected_rows.append((i, v, roots[v] == i, pol(int(lit)) ^ rp))
    got_rows = [
        (int(x["clause_index"]), int(x["variable"]), bool(x["is_root"]), int(x["defect"]))
        for x in r["defects"]
    ]
    if got_rows != expected_rows:
        raise AssertionError("defect rows mismatch")

    exhaustive_checked = False
    if len(variables) <= exhaustive_limit:
        exhaustive_checked = True
        for bits in itertools.product((0, 1), repeat=len(variables)):
            y = dict(zip(variables, bits))
            x = {v: y[v] ^ switch[v] for v in variables}
            if eval_cnf(src, x) != eval_cnf(dst, y):
                raise AssertionError("assignment bijection replay failed")

    return {
        "verdict": "PASS_EXACT_SWITCHING_NORMAL_FORM_CHECK",
        "semantic_coordinate_change_verified": True,
        "incidence_count": inc,
        "active_variable_count": len(variables),
        "defect_dimension": expected_D,
        "small_control_exhaustive_bijection_replay": exhaustive_checked,
        "general_sat_in_p": "NOT_PROVED",
        "p_vs_np": "OPEN"
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--exhaustive-limit", type=int, default=16)
    args = ap.parse_args()
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            obj = json.load(f)
    else:
        obj = json.load(sys.stdin)
    out = verify(obj, args.exhaustive_limit)
    json.dump(out, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
