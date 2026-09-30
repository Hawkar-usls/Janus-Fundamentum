#!/usr/bin/env python3
"""Linear-autarky finite screen for frozen R50G25X residuals.

Public condition:
  for clause-variable sign matrix M, any nonzero x with Mx >= 0 induces
  an autarky via sign(x).

The LP solver is proposal-only. A positive candidate is accepted only after an
exact Boolean autarky replay: every clause touched by the partial assignment
must be satisfied by it.

A negative LP feasibility status is diagnostic only; no exact Farkas
certificate is emitted by this script.
"""
from __future__ import annotations
import json
import sys
import numpy as np
from scipy.optimize import linprog


def find_linear_autarky(clauses):
    variables = sorted({abs(l) for c in clauses for l in c})
    pos = {v: i for i, v in enumerate(variables)}
    M = np.zeros((len(clauses), len(variables)))
    for i, clause in enumerate(clauses):
        for lit in clause:
            M[i, pos[abs(lit)]] += 1.0 if lit > 0 else -1.0

    # Homogeneous cone. If a nonzero bounded solution exists, after scaling
    # at least one coordinate can be fixed to +1 or -1 inside [-1,1].
    for j, var in enumerate(variables):
        for sign in (1.0, -1.0):
            bounds = [(-1.0, 1.0)] * len(variables)
            bounds[j] = (sign, sign)
            res = linprog(
                np.zeros(len(variables)),
                A_ub=-M,
                b_ub=np.zeros(len(clauses)),
                bounds=bounds,
                method="highs",
            )
            if not res.success:
                continue

            assignment = {
                variables[i]: bool(res.x[i] > 0)
                for i in range(len(variables))
                if abs(res.x[i]) > 1e-8
            }
            if not assignment:
                continue

            touched = []
            for ci, clause in enumerate(clauses):
                if not any(abs(l) in assignment for l in clause):
                    continue
                sat = any(
                    abs(l) in assignment
                    and ((l > 0 and assignment[abs(l)]) or (l < 0 and not assignment[abs(l)]))
                    for l in clause
                )
                if not sat:
                    raise AssertionError(("AUTARKY_REPLAY_FAIL", ci, clause, assignment))
                touched.append(ci)

            if touched:
                return assignment, touched
    return None, None


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: linear_autarky_screen.py artifact.json")
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    rows = []
    for index, row in enumerate(data["residuals"]):
        clauses = [list(c) for c in row["residual_formula"]]
        assignment, touched = find_linear_autarky(clauses)
        out = {
            "index": index,
            "family": row["family"],
            "hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
            "candidate_found": assignment is not None,
            "removed_clause_count_if_candidate": 0 if touched is None else len(touched),
            "positive_candidate_replay": "N/A" if assignment is None else "PASS",
        }
        rows.append(out)
        print(json.dumps(out), flush=True)

    print(json.dumps({
        "schema": "janus.trump.r50g25x.linear_autarky_lp_screen.v1",
        "authority": "FINITE_LP_PROPOSAL_SCREEN__POSITIVE_REPLAY_EXACT__NEGATIVE_STATUS_NOT_EXACT_CERTIFICATE",
        "rows": rows,
        "all_fifteen_no_candidate": all(not r["candidate_found"] for r in rows),
        "claim_ceiling": {
            "linearly_lean_exactly_proved": False,
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN",
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
