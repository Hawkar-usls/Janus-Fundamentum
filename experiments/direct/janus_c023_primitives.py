"""C023 CNF and Horn proof primitives."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Equation = tuple[tuple[int, ...], int]

DEFAULT_SEED = 9379992
CANONICAL_SEED_SHA256 = "44e21fdc9d37fda98e2e73b0c9eb268bd04cdca9d84d0519e4f1166be22b46fc"


# ---------------------------------------------------------------------------
# CNF primitives
# ---------------------------------------------------------------------------

def canonical_clause(raw: Iterable[int]) -> Clause | None:
    literals = set(int(x) for x in raw)
    if any(-lit in literals for lit in literals):
        return None
    return tuple(sorted(literals, key=lambda x: (abs(x), x < 0)))


def canonical_cnf(raw: Iterable[Iterable[int]]) -> CNF:
    clauses: set[Clause] = set()
    for clause in raw:
        c = canonical_clause(clause)
        if c is not None:
            clauses.add(c)
    return tuple(sorted(clauses))


def cnf_variables(formula: CNF) -> list[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def equation_variables(equations: list[Equation]) -> list[int]:
    return sorted({v for vars_, _ in equations for v in vars_})


def satisfies_cnf(formula: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
        for clause in formula
    )


def satisfies_affine(equations: list[Equation], assignment: dict[int, bool]) -> bool:
    for vars_, rhs in equations:
        value = 0
        for v in vars_:
            value ^= int(assignment[v])
        if value != (rhs & 1):
            return False
    return True


def simplify_cnf(formula: CNF, fixed: dict[int, bool]) -> CNF:
    out: list[Clause] = []
    for clause in formula:
        reduced: list[int] = []
        satisfied = False
        for lit in clause:
            v = abs(lit)
            if v not in fixed:
                reduced.append(lit)
            elif fixed[v] == (lit > 0):
                satisfied = True
                break
        if not satisfied:
            out.append(tuple(reduced))
    return canonical_cnf(out)


def is_horn(formula: CNF) -> bool:
    return all(sum(1 for lit in clause if lit > 0) <= 1 for clause in formula)


def brute_force_mixed(
    equations: list[Equation],
    horn: CNF,
    universe: list[int],
) -> tuple[bool, dict[int, bool] | None, int]:
    checks = 0
    for bits in itertools.product([False, True], repeat=len(universe)):
        checks += 1
        assignment = dict(zip(universe, bits))
        if satisfies_affine(equations, assignment) and satisfies_cnf(horn, assignment):
            return True, assignment, checks
    return False, None, checks


# ---------------------------------------------------------------------------
# Horn solver and certificates
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HornCertificate:
    kind: str
    fixed: tuple[tuple[int, bool], ...]
    fired_rules: tuple[int, ...]
    conflict_rule: int
    true_variables: tuple[int, ...]


@dataclass
class HornResult:
    sat: bool
    assignment: dict[int, bool] | None
    certificate: HornCertificate | None
    rule_scans: int
    fired_count: int


def horn_solve(
    formula: CNF,
    fixed: dict[int, bool] | None = None,
) -> HornResult:
    if not is_horn(formula):
        raise ValueError("formula is not Horn")

    fixed = dict(fixed or {})
    residual = simplify_cnf(formula, fixed)
    all_vars = set(cnf_variables(formula)) | set(fixed)

    rules: list[tuple[frozenset[int], int | None]] = []
    for clause in residual:
        positives = [lit for lit in clause if lit > 0]
        antecedent = frozenset(abs(lit) for lit in clause if lit < 0)
        consequent = positives[0] if positives else None
        rules.append((antecedent, consequent))

    true_vars: set[int] = set()
    fired: list[int] = []
    scans = 0
    changed = True
    while changed:
        changed = False
        for idx, (antecedent, consequent) in enumerate(rules):
            scans += 1
            if not antecedent.issubset(true_vars):
                continue
            if consequent is None:
                cert = HornCertificate(
                    kind="HORN_FORWARD_CONTRADICTION",
                    fixed=tuple(sorted(fixed.items())),
                    fired_rules=tuple(fired),
                    conflict_rule=idx,
                    true_variables=tuple(sorted(true_vars)),
                )
                if not verify_horn_certificate(formula, cert):
                    raise AssertionError("generated Horn certificate did not verify")
                return HornResult(False, None, cert, scans, len(fired))
            if consequent not in true_vars:
                true_vars.add(consequent)
                fired.append(idx)
                changed = True

    assignment = {v: (v in true_vars) for v in all_vars if v not in fixed}
    assignment.update(fixed)
    if not satisfies_cnf(formula, assignment):
        raise AssertionError("Horn least model failed original formula")
    return HornResult(True, assignment, None, scans, len(fired))


def verify_horn_certificate(formula: CNF, cert: HornCertificate) -> bool:
    if cert.kind != "HORN_FORWARD_CONTRADICTION" or not is_horn(formula):
        return False
    fixed = dict(cert.fixed)
    residual = simplify_cnf(formula, fixed)
    rules: list[tuple[frozenset[int], int | None]] = []
    for clause in residual:
        positives = [lit for lit in clause if lit > 0]
        antecedent = frozenset(abs(lit) for lit in clause if lit < 0)
        consequent = positives[0] if positives else None
        rules.append((antecedent, consequent))

    true_vars: set[int] = set()
    for idx in cert.fired_rules:
        if not (0 <= idx < len(rules)):
            return False
        antecedent, consequent = rules[idx]
        if consequent is None or not antecedent.issubset(true_vars):
            return False
        true_vars.add(consequent)

    idx = cert.conflict_rule
    if not (0 <= idx < len(rules)):
        return False
    antecedent, consequent = rules[idx]
    return (
        consequent is None
        and antecedent.issubset(true_vars)
        and tuple(sorted(true_vars)) == cert.true_variables
    )
