#!/usr/bin/env python3
"""Exact finite checker for backdoor depth <= 2 into Horn, dual-Horn, and Krom.

Authority:
  FINITE_DIAGNOSTIC_CHECKER_ONLY.
This implements the recursive component-backdoor-depth definition directly:
  depth_C(F)=0 if F in C;
  max over incidence components if disconnected;
  1 + min_x max_b depth_C(F[x=b]) if connected and outside C.

The checker only decides whether depth is 0, 1, 2, or >2.
It does not implement the public FPT-approximation algorithm for arbitrary k.
"""
from __future__ import annotations
import json
import sys
from collections import defaultdict


def canon(clauses):
    out = []
    for clause in clauses:
        s = set(clause)
        if any(-lit in s for lit in s):
            continue
        out.append(tuple(sorted(s)))
    return tuple(sorted(set(out)))


def in_base(F, base):
    if base == "KROM":
        return all(len(c) <= 2 for c in F)
    if base == "HORN":
        return all(sum(l > 0 for l in c) <= 1 for c in F)
    if base == "DUAL_HORN":
        return all(sum(l < 0 for l in c) <= 1 for c in F)
    raise ValueError(base)


def assign(F, var, value):
    sat = var if value else -var
    falsified = -sat
    out = []
    for clause in F:
        if sat in clause:
            continue
        if falsified in clause:
            out.append(tuple(l for l in clause if l != falsified))
        else:
            out.append(clause)
    return canon(out)


def components(F):
    if not F:
        return []
    var_to_clauses = defaultdict(list)
    for i, clause in enumerate(F):
        for lit in clause:
            var_to_clauses[abs(lit)].append(i)

    seen = set()
    ans = []
    for root in range(len(F)):
        if root in seen:
            continue
        stack = [root]
        seen.add(root)
        ids = []
        while stack:
            ci = stack.pop()
            ids.append(ci)
            for lit in F[ci]:
                for cj in var_to_clauses[abs(lit)]:
                    if cj not in seen:
                        seen.add(cj)
                        stack.append(cj)
        ans.append(canon([F[i] for i in ids]))
    return ans


def variables(F):
    return sorted({abs(l) for c in F for l in c})


def depth_le_1(F, base, memo):
    key = (F, base)
    if key in memo:
        return memo[key]
    if in_base(F, base):
        memo[key] = True
        return True
    comps = components(F)
    if len(comps) > 1:
        ans = all(depth_le_1(c, base, memo) for c in comps)
        memo[key] = ans
        return ans
    for var in variables(F):
        if in_base(assign(F, var, False), base) and in_base(assign(F, var, True), base):
            memo[key] = True
            return True
    memo[key] = False
    return False


def exact_depth_bucket_le_2(F, base):
    if in_base(F, base):
        return 0
    memo = {}
    comps = components(F)

    if len(comps) > 1:
        if all(depth_le_1(c, base, memo) for c in comps):
            return 1
        for c in comps:
            if depth_le_1(c, base, memo):
                continue
            ok = False
            for var in variables(c):
                if depth_le_1(assign(c, var, False), base, memo) and depth_le_1(assign(c, var, True), base, memo):
                    ok = True
                    break
            if not ok:
                return ">2"
        return 2

    if depth_le_1(F, base, memo):
        return 1

    for var in variables(F):
        if depth_le_1(assign(F, var, False), base, memo) and depth_le_1(assign(F, var, True), base, memo):
            return 2

    return ">2"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: checker.py R50G25X_ARTIFACT.json")
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    rows = []
    for index, row in enumerate(data["residuals"]):
        F = canon(row["residual_formula"])
        out = {
            "index": index,
            "family": row["family"],
            "hash": row["residual_hash"],
            "CLV": row["residual_CLV"],
        }
        for base in ("HORN", "DUAL_HORN", "KROM"):
            out[base] = exact_depth_bucket_le_2(F, base)
        rows.append(out)

    result = {
        "schema": "janus.trump.r50g25x.backdoor_depth_le2_exact.v1",
        "authority": "FINITE_EXACT_DEPTH_LE2_DIAGNOSTIC__NOT_GENERAL_FPT_IMPLEMENTATION",
        "rows": rows,
        "all_fifteen_depth_gt_2_for_all_three_bases": all(
            row[b] == ">2" for row in rows for b in ("HORN", "DUAL_HORN", "KROM")
        ),
        "claim_ceiling": {
            "depth_3_or_more": "UNTESTED",
            "bounded_depth_route": "NOT_REJECTED",
            "general_sat_in_p": "NOT_PROVED",
            "p_vs_np": "OPEN",
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
