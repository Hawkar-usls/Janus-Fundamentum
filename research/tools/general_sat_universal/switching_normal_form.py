#!/usr/bin/env python3
"""Exact variable-switching normal form for signed CNF.

Research utility only. This is NOT a SAT solver and carries no P-vs-NP authority.

Input JSON on stdin or --input PATH:
  {"clauses": [[1,-2,3],[-1,2,4], ...]}

Literal convention: positive integer v is x_v; negative integer -v is not x_v.
Output is a deterministic rooted switching normal form relative to the fixed encoded
variable names and normalized clause ordering, plus an exact reconstruction switch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Clause = Tuple[int, ...]
CNF = Tuple[Clause, ...]


def _lit_key(lit: int) -> Tuple[int, int]:
    return (abs(lit), 1 if lit < 0 else 0)


def normalize_clause(clause: Sequence[int]) -> Optional[Clause]:
    """Collapse duplicate literals and drop tautological clauses.

    Returns None for a tautology. Raises on literal 0.
    """
    signs: Dict[int, int] = {}
    for raw in clause:
        lit = int(raw)
        if lit == 0:
            raise ValueError("literal 0 is not a variable literal")
        v = abs(lit)
        p = 1 if lit < 0 else 0
        if v in signs and signs[v] != p:
            return None
        signs[v] = p
    return tuple(sorted(((-v if p else v) for v, p in signs.items()), key=_lit_key))


def normalize_cnf(clauses: Iterable[Sequence[int]]) -> CNF:
    out: List[Clause] = []
    for clause in clauses:
        c = normalize_clause(clause)
        if c is None:
            continue
        out.append(c)
    # Clause order is nonsemantic. Sorting here makes the fixed-name encoding stable
    # under input clause permutation; no claim of canonical variable renaming is made.
    return tuple(sorted(out, key=lambda c: tuple(_lit_key(l) for l in c)))


def active_variables(cnf: CNF) -> Tuple[int, ...]:
    return tuple(sorted({abs(lit) for clause in cnf for lit in clause}))


def polarity(lit: int) -> int:
    """Forbidden-value bit: +v -> 0, -v -> 1."""
    return 1 if lit < 0 else 0


def root_incidence(cnf: CNF) -> Dict[int, int]:
    """Choose the first normalized clause containing each active variable."""
    roots: Dict[int, int] = {}
    for i, clause in enumerate(cnf):
        for lit in clause:
            roots.setdefault(abs(lit), i)
    return roots


def _literal_for_var(clause: Clause, v: int) -> int:
    for lit in clause:
        if abs(lit) == v:
            return lit
    raise KeyError(v)


def rooted_switch(cnf: CNF) -> Tuple[Dict[int, int], Dict[int, int]]:
    roots = root_incidence(cnf)
    switch: Dict[int, int] = {}
    for v, i in roots.items():
        switch[v] = polarity(_literal_for_var(cnf[i], v))
    return roots, switch


def apply_switch(cnf: CNF, switch: Dict[int, int]) -> CNF:
    transformed: List[Clause] = []
    for clause in cnf:
        c: List[int] = []
        for lit in clause:
            v = abs(lit)
            p2 = polarity(lit) ^ int(switch.get(v, 0))
            c.append(-v if p2 else v)
        transformed.append(tuple(c))
    return tuple(transformed)


def defect_rows(cnf: CNF, roots: Dict[int, int]) -> List[dict]:
    root_p = {
        v: polarity(_literal_for_var(cnf[i], v))
        for v, i in roots.items()
    }
    rows: List[dict] = []
    for i, clause in enumerate(cnf):
        for lit in clause:
            v = abs(lit)
            rows.append(
                {
                    "clause_index": i,
                    "variable": v,
                    "is_root": roots[v] == i,
                    "defect": polarity(lit) ^ root_p[v],
                }
            )
    return rows


def eval_cnf(cnf: CNF, assignment: Dict[int, int]) -> bool:
    for clause in cnf:
        clause_true = False
        for lit in clause:
            v = abs(lit)
            bit = int(assignment[v])
            if (lit > 0 and bit == 1) or (lit < 0 and bit == 0):
                clause_true = True
                break
        if not clause_true:
            return False
    return True


def map_assignment_y_to_x(y: Dict[int, int], switch: Dict[int, int]) -> Dict[int, int]:
    return {v: int(y[v]) ^ int(switch.get(v, 0)) for v in y}


def canonical_json_sha256(obj: object) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build_receipt(raw_clauses: Iterable[Sequence[int]]) -> dict:
    cnf = normalize_cnf(raw_clauses)
    roots, switch = rooted_switch(cnf)
    transformed = apply_switch(cnf, switch)
    variables = active_variables(cnf)
    incidence_count = sum(len(c) for c in cnf)
    defect_dimension = incidence_count - len(variables)

    # Exact local sanity condition: each chosen root incidence is positive after switch.
    for v, i in roots.items():
        lit = _literal_for_var(transformed[i], v)
        if polarity(lit) != 0:
            raise AssertionError("root normalization failed")

    core = {
        "normalized_input_clauses": [list(c) for c in cnf],
        "root_clause_index_by_variable": {str(v): i for v, i in sorted(roots.items())},
        "switch_by_variable": {str(v): b for v, b in sorted(switch.items())},
        "transformed_clauses": [list(c) for c in transformed],
        "defects": defect_rows(cnf, roots),
        "active_variable_count": len(variables),
        "incidence_count": incidence_count,
        "defect_dimension": defect_dimension,
        "switching_orbit_size": f"2^{len(variables)}",
        "switching_orbit_count_for_fixed_incidence_structure": f"2^{defect_dimension}",
    }
    return {
        "schema": "JANUS/TRUMP-SIGNED-CNF-SWITCHING-NORMAL-FORM/v1",
        "authority": "EXACT_NORMAL_FORM_ONLY__NOT_A_SOLVER",
        "general_sat_in_p": "NOT_PROVED",
        "p_vs_np": "OPEN",
        "receipt": core,
        "receipt_sha256": canonical_json_sha256(core),
    }


def _load(args: argparse.Namespace) -> dict:
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    args = ap.parse_args()
    payload = _load(args)
    if not isinstance(payload, dict) or "clauses" not in payload:
        raise SystemExit("expected JSON object with 'clauses'")
    result = build_receipt(payload["clauses"])
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
