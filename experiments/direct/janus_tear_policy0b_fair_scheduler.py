#!/usr/bin/env python3
"""C025-A: complete fair one-layer Resolution pair scheduler.

This is a scheduler primitive, not a SAT solver.  It visits every complementary
parent pair from the frozen input clause set exactly once.  It intentionally
returns candidate resolvents instead of mutating the clause database so that
retention/state-size policy remains a separate C025-E gate.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def canonical_clause(clause: Iterable[int]) -> Clause | None:
    literals = set(clause)
    if any(-literal in literals for literal in literals):
        return None
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


def canonical_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    normalized: set[Clause] = set()
    for clause in clauses:
        candidate = canonical_clause(clause)
        if candidate is not None:
            normalized.add(candidate)
    return tuple(sorted(normalized, key=lambda clause: (len(clause), clause)))


@dataclass(frozen=True)
class FairScanResult:
    literal_occurrences: int
    attempts: int
    eligible_pivots: tuple[int, ...]
    attempts_by_pivot: tuple[tuple[int, int], ...]
    non_tautological_candidates: int
    distinct_candidates: int


def fair_frozen_layer_scan(cnf: CNF) -> FairScanResult:
    frozen = canonical_cnf(cnf)
    positive: dict[int, list[Clause]] = defaultdict(list)
    negative: dict[int, list[Clause]] = defaultdict(list)

    for clause in frozen:
        for literal in clause:
            (positive if literal > 0 else negative)[abs(literal)].append(clause)

    pivots = tuple(sorted(set(positive) & set(negative)))
    attempts = 0
    attempts_by_pivot: list[tuple[int, int]] = []
    candidates: set[Clause] = set()
    non_tautological = 0

    for pivot in pivots:
        local_attempts = 0
        for left in positive[pivot]:
            for right in negative[pivot]:
                attempts += 1
                local_attempts += 1
                resolvent = (set(left) - {pivot}) | (set(right) - {-pivot})
                normalized = canonical_clause(resolvent)
                if normalized is None:
                    continue
                non_tautological += 1
                candidates.add(normalized)
        attempts_by_pivot.append((pivot, local_attempts))

    L = sum(len(clause) for clause in frozen)
    assert 4 * attempts <= L * L

    return FairScanResult(
        literal_occurrences=L,
        attempts=attempts,
        eligible_pivots=pivots,
        attempts_by_pivot=tuple(attempts_by_pivot),
        non_tautological_candidates=non_tautological,
        distinct_candidates=len(candidates),
    )


def starvation_fixture(p: int = 80) -> tuple[CNF, int, int]:
    """Small analogue of the C024 sink plus one later informative core pivot."""
    d, a = 1, 2
    next_var = 3
    clauses: list[Clause] = []

    for _ in range(p):
        u = next_var
        next_var += 1
        clauses.append((d, a, u))
    for _ in range(p):
        v = next_var
        next_var += 1
        clauses.append((-d, -a, v))

    core = next_var
    y = next_var + 1
    z = next_var + 2
    clauses.extend(((core, y), (-core, z)))
    return canonical_cnf(clauses), d, core


def self_test() -> None:
    cnf, sink_pivot, core_pivot = starvation_fixture()
    result = fair_frozen_layer_scan(cnf)
    attempts = dict(result.attempts_by_pivot)

    assert result.eligible_pivots[0] == sink_pivot
    assert attempts[sink_pivot] == 80 * 80
    assert core_pivot in result.eligible_pivots
    assert attempts[core_pivot] == 1
    assert result.attempts == 80 * 80 + 1
    assert 4 * result.attempts <= result.literal_occurrences**2

    print("JANUS_POLICY0B_FAIR_SCHEDULER = PASS")
    print(f"literal_occurrences = {result.literal_occurrences}")
    print(f"attempts = {result.attempts}")
    print(f"eligible_pivots = {result.eligible_pivots}")
    print(f"sink_attempts = {attempts[sink_pivot]}")
    print(f"core_attempts = {attempts[core_pivot]}")
    print(f"distinct_non_tautological_candidates = {result.distinct_candidates}")
    print("claim_boundary = scheduler-only; candidate retention and global polynomiality remain open")


if __name__ == "__main__":
    self_test()
