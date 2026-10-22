#!/usr/bin/env python3
"""Independent verifier for an authors-produced Backdoor DNF.

Input:
  * DIMACS CNF source,
  * runner.py stdout containing a final line 'Result: [[...], ...]',
  * base class HORN or KROM.

Checks:
  1. every term is a consistent partial assignment;
  2. every reduced formula belongs syntactically to the declared base class;
  3. the DNF is tautological by exact DPLL UNSAT checking of its negation.

No detector logic from the authors' implementation is reused here.
"""
from __future__ import annotations

import argparse
import ast
import json
from functools import lru_cache
from pathlib import Path


def parse_dimacs(path: Path):
    clauses = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("c") or s.startswith("p"):
            continue
        vals = [int(x) for x in s.split()]
        if not vals or vals[-1] != 0:
            raise ValueError(f"bad DIMACS line: {raw!r}")
        clauses.append(tuple(vals[:-1]))
    return clauses


def parse_result(path: Path):
    marker = "Result:"
    found = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith(marker):
            found = raw[len(marker):].strip()
    if found is None:
        raise ValueError("NO_RESULT_LINE")
    obj = ast.literal_eval(found)
    if not isinstance(obj, list):
        raise ValueError("RESULT_NOT_LIST")
    terms = []
    for term in obj:
        if not isinstance(term, (list, tuple, set)):
            raise ValueError("TERM_NOT_SEQUENCE")
        vals = tuple(sorted({int(x) for x in term}, key=lambda z:(abs(z),z)))
        if any(-x in vals for x in vals):
            raise ValueError("INCONSISTENT_TERM")
        terms.append(vals)
    return terms


def simplify(clauses, term):
    t = set(term)
    out = []
    for clause in clauses:
        if any(l in t for l in clause):
            continue
        out.append(tuple(l for l in clause if -l not in t))
    return out


def in_base(clauses, base):
    if base == "HORN":
        return all(sum(l > 0 for l in c) <= 1 for c in clauses)
    if base == "DUAL_HORN":
        return all(sum(l < 0 for l in c) <= 1 for c in clauses)
    if base == "KROM":
        return all(len(c) <= 2 for c in clauses)
    raise ValueError(base)


def canon_cnf(clauses):
    cleaned = []
    for c in clauses:
        s = frozenset(c)
        if any(-x in s for x in s):
            continue
        cleaned.append(s)
    # subsumption is satisfiability-preserving and helps the verifier
    uniq = sorted(set(cleaned), key=lambda s:(len(s), tuple(sorted(s))))
    keep = []
    for c in uniq:
        if not any(k <= c for k in keep):
            keep.append(c)
    return tuple(tuple(sorted(c)) for c in keep)


def exact_unsat(clauses):
    nodes = 0

    @lru_cache(maxsize=None)
    def sat(state):
        nonlocal nodes
        nodes += 1
        cls = [set(c) for c in state]
        if any(len(c) == 0 for c in cls):
            return False
        if not cls:
            return True

        # Unit propagation.
        units = [next(iter(c)) for c in cls if len(c) == 1]
        if units:
            lit = units[0]
            nxt = []
            for c in cls:
                if lit in c:
                    continue
                nc = c - {-lit}
                nxt.append(tuple(sorted(nc)))
            return sat(canon_cnf(nxt))

        # Pure-literal elimination.
        lits = set().union(*cls)
        for lit in sorted(lits, key=lambda z:(abs(z), z)):
            if -lit not in lits:
                nxt = [tuple(sorted(c)) for c in cls if lit not in c]
                return sat(canon_cnf(nxt))

        # Deterministic branch from the shortest clause.
        pivot_clause = min(cls, key=lambda c:(len(c), tuple(sorted(c))))
        lit = min(pivot_clause, key=lambda z:(abs(z),z))
        for chosen in (lit, -lit):
            nxt = []
            for c in cls:
                if chosen in c:
                    continue
                nc = c - {-chosen}
                nxt.append(tuple(sorted(nc)))
            if sat(canon_cnf(nxt)):
                return True
        return False

    root = canon_cnf(clauses)
    is_sat = sat(root)
    return (not is_sat), nodes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cnf")
    ap.add_argument("runner_log")
    ap.add_argument("base", choices=["HORN","DUAL_HORN","KROM"])
    ap.add_argument("output")
    ns = ap.parse_args()

    source = parse_dimacs(Path(ns.cnf))
    terms = parse_result(Path(ns.runner_log))
    if not terms:
        raise SystemExit("EMPTY_DNF")

    term_rows = []
    all_base = True
    for i, term in enumerate(terms):
        residual = simplify(source, term)
        ok = in_base(residual, ns.base)
        all_base &= ok
        term_rows.append({
            "term_index": i,
            "term": list(term),
            "term_size": len(term),
            "residual_clause_count": len(residual),
            "base_membership": ok,
            "empty_clause_present": any(len(c) == 0 for c in residual),
        })

    # not(T1 or ... or Tr) == AND_i not(T_i).
    neg_dnf = [tuple(-lit for lit in term) for term in terms]
    tautology, dpll_nodes = exact_unsat(neg_dnf)

    result = {
        "schema":"janus.trump.backdoor_dnf_independent_verify.v1",
        "base":ns.base,
        "term_count":len(terms),
        "max_term_size":max(map(len,terms)),
        "union_variable_count":len({abs(x) for t in terms for x in t}),
        "all_terms_base_membership":all_base,
        "dnf_tautology":tautology,
        "tautology_dpll_nodes":dpll_nodes,
        "terms":term_rows,
        "verdict":"PASS" if all_base and tautology else "FAIL",
    }
    Path(ns.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "base","term_count","max_term_size","union_variable_count",
        "all_terms_base_membership","dnf_tautology","tautology_dpll_nodes","verdict"
    )},sort_keys=True))
    if result["verdict"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
