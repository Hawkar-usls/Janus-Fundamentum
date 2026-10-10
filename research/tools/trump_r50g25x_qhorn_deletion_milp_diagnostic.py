#!/usr/bin/env python3
"""Finite q-Horn deletion-distance diagnostic via MILP.

This is NOT the public O(12^k k^5 ell) FPT algorithm.
It is a finite comparator for frozen formulas.

q-Horn valuation used:
  alpha_x in {0, 1/2, 1}
  for every clause C:
    sum_{x in C+} alpha_x + sum_{~x in C-} (1-alpha_x) <= 1.

For each variable choose exactly one state:
  DELETE, alpha=0, alpha=1/2, alpha=1.
Objective: minimize DELETE count.

Every returned incumbent is replayed exactly against the ternary q-Horn
inequalities. MILP optimality status is computational evidence only and is not
promoted to JANUS proof authority without an independently checkable optimum
certificate.
"""
from __future__ import annotations
import json
import sys
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix, csr_matrix


def solve(clauses, time_limit=15.0):
    variables = sorted({abs(l) for c in clauses for l in c})
    pos = {v: i for i, v in enumerate(variables)}
    n = len(variables)
    m = 4 * n

    objective = np.zeros(m)
    objective[0::4] = 1.0

    exactly_one = lil_matrix((n, m), dtype=float)
    for i in range(n):
        exactly_one[i, 4*i:4*i+4] = 1.0

    clause_rows = lil_matrix((len(clauses), m), dtype=float)
    for row, clause in enumerate(clauses):
        for lit in clause:
            i = pos[abs(lit)]
            # scaled by 2:
            # DELETE -> 0
            # alpha=0 -> positive 0, negative 2
            # alpha=1/2 -> positive 1, negative 1
            # alpha=1 -> positive 2, negative 0
            if lit > 0:
                clause_rows[row, 4*i+2] += 1.0
                clause_rows[row, 4*i+3] += 2.0
            else:
                clause_rows[row, 4*i+1] += 2.0
                clause_rows[row, 4*i+2] += 1.0

    constraints = [
        LinearConstraint(csr_matrix(exactly_one), np.ones(n), np.ones(n)),
        LinearConstraint(
            csr_matrix(clause_rows),
            -np.inf*np.ones(len(clauses)),
            2.0*np.ones(len(clauses)),
        ),
    ]

    result = milp(
        objective,
        integrality=np.ones(m),
        bounds=Bounds(np.zeros(m), np.ones(m)),
        constraints=constraints,
        options={"time_limit": time_limit, "mip_rel_gap": 0.0},
    )

    out = {
        "success_optimal_status": bool(result.success),
        "status": int(result.status),
        "message": result.message,
        "objective_incumbent": None if result.fun is None else float(result.fun),
        "optimizer_dual_bound": (
            None if getattr(result, "mip_dual_bound", None) is None
            else float(result.mip_dual_bound)
        ),
        "optimizer_gap": getattr(result, "mip_gap", None),
    }

    if result.x is None:
        return out

    x = np.rint(result.x).astype(int)
    deletion = []
    alpha = {}
    for i, var in enumerate(variables):
        if x[4*i]:
            deletion.append(var)
            alpha[var] = "DELETED"
        elif x[4*i+1]:
            alpha[var] = 0
        elif x[4*i+2]:
            alpha[var] = "1/2"
        elif x[4*i+3]:
            alpha[var] = 1
        else:
            raise AssertionError("NO_STATE")

    # Exact replay in units of halves.
    for clause in clauses:
        total2 = 0
        for lit in clause:
            state = alpha[abs(lit)]
            if state == "DELETED":
                continue
            a2 = 0 if state == 0 else 1 if state == "1/2" else 2
            total2 += a2 if lit > 0 else 2-a2
        if total2 > 2:
            raise AssertionError(("QHORN_REPLAY_FAIL", clause, total2))

    out["deletion_set"] = deletion
    out["deletion_size"] = len(deletion)
    out["ternary_qhorn_replay"] = "PASS"
    return out


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: qhorn_del.py artifact.json [seconds]")
    time_limit = float(sys.argv[2]) if len(sys.argv) == 3 else 15.0
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    rows = []
    for index, row in enumerate(data["residuals"]):
        result = solve(row["residual_formula"], time_limit)
        result.update({
            "index": index,
            "family": row["family"],
            "hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
        })
        rows.append(result)
        print(json.dumps(result), flush=True)

    print(json.dumps({
        "schema": "janus.trump.r50g25x.qhorn_deletion_milp_diagnostic.v1",
        "authority": "FINITE_MILP_DIAGNOSTIC__INCUMBENTS_EXACTLY_REPLAYED__OPTIMALITY_NOT_PROOF_CARRIED",
        "rows": rows,
        "claim_ceiling": {
            "public_fpt_algorithm_reimplemented": False,
            "universal_complexity_claim": False,
            "p_vs_np": "OPEN",
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
