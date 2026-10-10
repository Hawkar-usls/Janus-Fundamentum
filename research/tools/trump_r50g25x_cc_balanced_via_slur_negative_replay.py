#!/usr/bin/env python3
"""Exact finite SLUR give-up witness replay for the frozen R50G25X corpus.

Purpose
-------
CC-balanced CNF is a subclass of SLUR.  A CNF is in SLUR only if the SLUR
procedure never returns GIVE_UP for any legal nondeterministic variable/branch
choices.  Therefore one replayable GIVE_UP execution is a finite exact
non-membership certificate for SLUR, and hence for CC-balanced.

This tool does NOT implement general CC-balanced recognition.
"""
from __future__ import annotations

import json
import sys


WITNESS_CHOICES = {
    0:  [(16,1),(13,0),(27,0),(12,1),(20,1),(8,None)],
    1:  [(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(11,1),(12,None)],
    2:  [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,1),(9,1),(10,0),(11,1),(12,None)],
    3:  [(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(11,1),(12,None)],
    4:  [(1,0),(3,0),(4,0),(5,0),(6,0),(8,0),(9,0),(10,0),(11,0),(12,0),(13,0),(14,1),(15,None)],
    5:  [(34,1),(6,1),(40,None)],
    6:  [(1,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(11,1),(12,None)],
    7:  [(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(11,1),(12,None)],
    8:  [(11,1),(32,0),(26,1),(46,None)],
    9:  [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,1),(9,1),(10,0),(11,1),(12,None)],
    10: [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,1),(9,1),(10,0),(11,1),(12,None)],
    11: [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,1),(9,1),(10,0),(11,1),(12,None)],
    12: [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,1),(9,1),(10,0),(11,1),(12,None)],
    13: [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,1),(9,1),(10,0),(11,1),(12,None)],
    14: [(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,1),(9,1),(10,0),(11,1),(12,None)],
}


def canon(clauses):
    out = []
    for clause in clauses:
        s = set(int(x) for x in clause)
        if any(-x in s for x in s):
            continue
        out.append(tuple(sorted(s)))
    return tuple(sorted(set(out)))


def simplify(formula, assignment):
    out = []
    for clause in formula:
        nc = []
        satisfied = False
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if assignment[v] == (lit > 0):
                    satisfied = True
                    break
            else:
                nc.append(lit)
        if satisfied:
            continue
        if not nc:
            return None
        out.append(tuple(nc))
    return canon(out)


def unitprop(formula, assignment=None):
    assignment = {} if assignment is None else dict(assignment)
    formula = canon(formula)
    while True:
        reduced = simplify(formula, assignment)
        if reduced is None:
            return None, assignment
        units = [c[0] for c in reduced if len(c) == 1]
        if not units:
            return reduced, assignment
        changed = False
        for lit in units:
            v, val = abs(lit), lit > 0
            if v in assignment and assignment[v] != val:
                return None, assignment
            if v not in assignment:
                assignment[v] = val
                changed = True
        if not changed:
            return reduced, assignment


def branch(formula, assignment, var, value):
    a = dict(assignment)
    a[var] = bool(value)
    return unitprop(formula, a)


def replay_give_up(formula, witness):
    formula, assignment = unitprop(formula)
    if formula is None:
        return {"pass": False, "reason": "top-level unit propagation already UNSAT"}

    transcript = []
    depth = 0
    for var, chosen in witness:
        if formula is None or not formula:
            return {"pass": False, "reason": "trace continues after termination"}

        present = {abs(l) for c in formula for l in c}
        if var not in present:
            return {"pass": False, "reason": f"variable {var} absent at step {depth}"}

        f0, a0 = branch(formula, assignment, var, False)
        f1, a1 = branch(formula, assignment, var, True)
        row = {
            "depth": depth,
            "var": var,
            "false_conflict": f0 is None,
            "true_conflict": f1 is None,
            "chosen": chosen,
        }

        if chosen is None:
            row["give_up"] = (depth > 0 and f0 is None and f1 is None)
            transcript.append(row)
            return {
                "pass": bool(row["give_up"]),
                "depth": depth,
                "transcript": transcript,
            }

        if f0 is None and f1 is None:
            return {"pass": False, "reason": "both branches conflict before declared terminal"}

        if bool(chosen):
            if f1 is None:
                return {"pass": False, "reason": "chosen true branch conflicts"}
            formula, assignment = f1, a1
        else:
            if f0 is None:
                return {"pass": False, "reason": "chosen false branch conflicts"}
            formula, assignment = f0, a0

        transcript.append(row)
        depth += 1

    return {"pass": False, "reason": "trace ended without GIVE_UP"}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: cc_balanced_slur_negative_replay.py R50G25X_ARTIFACT.json")
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    rows = []
    for i, row in enumerate(data["residuals"]):
        replay = replay_give_up(row["residual_formula"], WITNESS_CHOICES[i])
        if not replay["pass"]:
            raise AssertionError((i, replay))
        rows.append({
            "index": i,
            "hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
            "give_up_depth": replay["depth"],
            "witness_choices": WITNESS_CHOICES[i],
            "replay_pass": True,
        })

    print(json.dumps({
        "schema": "janus.trump.r50g25x.cc_balanced_via_slur_negative_replay.v1",
        "authority": "FINITE_EXACT_NEGATIVE_MEMBERSHIP_CERTIFICATES",
        "logic": "CC_BALANCED subseteq SLUR; one legal SLUR GIVE_UP trace implies NOT_SLUR and therefore NOT_CC_BALANCED.",
        "rows": rows,
        "all_15_not_slur": True,
        "all_15_not_cc_balanced": True,
        "claim_ceiling": {
            "general_cc_balanced_recognizer_implemented": False,
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN"
        }
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
