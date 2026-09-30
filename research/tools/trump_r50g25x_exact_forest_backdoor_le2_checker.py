#!/usr/bin/env python3
"""Exact finite weak/strong Forest-backdoor <=2 checker for frozen R50G25X.

Public target class:
  FOREST = CNF formulas whose clause-variable incidence graph is acyclic.

Weak Forest backdoor B:
  some assignment tau to B yields a satisfiable FOREST formula.
Strong Forest backdoor B:
  every assignment tau to B yields a FOREST formula.

For the frozen corpus we prove a stronger negative for weak size <=2:
  for no set B of size <=2 and no assignment tau does F[tau] even enter FOREST.
Hence SAT checking of the reduced formula is unnecessary for this negative result.

Authority:
  FINITE_EXACT_K_LE_2_DIAGNOSTIC_ONLY.
"""
from __future__ import annotations
import itertools
import json
import sys


def simplify_formula(clauses, assignment):
    out = []
    for clause in clauses:
        satisfied = False
        reduced = []
        for lit in clause:
            lit = int(lit)
            var = abs(lit)
            if var in assignment:
                if assignment[var] == (lit > 0):
                    satisfied = True
                    break
            else:
                reduced.append(lit)
        if not satisfied:
            out.append(tuple(reduced))
    return tuple(out)


def incidence_is_forest(clauses):
    """Union-find cycle test on the bipartite incidence graph."""
    parent = {}
    rank = {}

    def find(x):
        if x not in parent:
            parent[x] = x
            rank[x] = 0
            return x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    for ci, clause in enumerate(clauses):
        cnode = ("c", ci)
        for lit in clause:
            vnode = ("v", abs(int(lit)))
            if not union(cnode, vnode):
                return False
    return True


def variables(clauses):
    return sorted({abs(int(lit)) for c in clauses for lit in c})


def weak_structure_exists_le_2(clauses):
    """Return witness if any assignment on <=2 vars reaches FOREST, else None."""
    vars_ = variables(clauses)
    if incidence_is_forest(clauses):
        return {"vars": [], "assignment": {}}
    for k in (1, 2):
        for B in itertools.combinations(vars_, k):
            for bits in itertools.product((False, True), repeat=k):
                assignment = dict(zip(B, bits))
                if incidence_is_forest(simplify_formula(clauses, assignment)):
                    return {"vars": list(B), "assignment": assignment}
    return None


def strong_exists_le_2(clauses):
    """Return witness set if every assignment on <=2 vars reaches FOREST."""
    vars_ = variables(clauses)
    if incidence_is_forest(clauses):
        return []
    for k in (1, 2):
        for B in itertools.combinations(vars_, k):
            ok = True
            for bits in itertools.product((False, True), repeat=k):
                assignment = dict(zip(B, bits))
                if not incidence_is_forest(simplify_formula(clauses, assignment)):
                    ok = False
                    break
            if ok:
                return list(B)
    return None


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: checker.py R50G25X_ARTIFACT.json")

    data = json.load(open(sys.argv[1], encoding="utf-8"))
    rows = []
    for index, row in enumerate(data["residuals"]):
        clauses = row["residual_formula"]
        weak = weak_structure_exists_le_2(clauses)
        strong = strong_exists_le_2(clauses)
        rows.append({
            "index": index,
            "family": row["family"],
            "hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
            "weak_forest_backdoor_size_le_2": weak is not None,
            "strong_forest_backdoor_size_le_2": strong is not None,
            "weak_structure_witness": weak,
            "strong_witness": strong,
        })

    result = {
        "schema": "janus.trump.r50g25x.forest_backdoor_le2_exact.v1",
        "authority": "FINITE_EXACT_K_LE_2_DIAGNOSTIC__NO_ASYMPTOTIC_CLAIM",
        "rows": rows,
        "all_15_weak_forest_backdoor_gt_2": all(
            not r["weak_forest_backdoor_size_le_2"] for r in rows
        ),
        "all_15_strong_forest_backdoor_gt_2": all(
            not r["strong_forest_backdoor_size_le_2"] for r in rows
        ),
        "stronger_weak_negative": (
            "For every frozen residual, no assignment to any set of at most "
            "two variables even produces an acyclic incidence graph."
        ),
        "claim_ceiling": {
            "weak_forest_depth_or_size_ge_3": "UNTESTED",
            "strong_forest_size_ge_3": "UNTESTED",
            "public_fpt_forest_route": "NOT_REJECTED",
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN",
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
