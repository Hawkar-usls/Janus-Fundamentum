#!/usr/bin/env python3
"""C025-C1 exact incremental applicability index for certified clause reasons.

The index does not prove clauses and does not search for new reasons. Its input
is a set of already-certified non-tautological reason clauses. A reason applies
exactly when the current partial assignment falsifies every literal.

Claim ceiling: deterministic lookup work polynomial in explicit cache volume M;
no input-relative polynomial claim without an independent M=poly(N) theorem.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

Clause = tuple[int, ...]


def canonical_clause(clause: Iterable[int]) -> Clause:
    literals = set(int(literal) for literal in clause)
    if 0 in literals:
        raise ValueError("literal 0 is not allowed")
    if any(-literal in literals for literal in literals):
        raise ValueError("tautological clauses are not reason-cache entries")
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


@dataclass(frozen=True)
class TrailEvent:
    variable: int
    value: bool
    false_literal: int
    touched_reason_ids: tuple[int, ...]


class ReasonCacheIndex:
    def __init__(self, reasons: Iterable[Iterable[int]]):
        canonical = sorted(
            {canonical_clause(reason) for reason in reasons},
            key=lambda clause: (len(clause), clause),
        )
        self.reasons: tuple[Clause, ...] = tuple(canonical)
        temp: dict[int, list[int]] = defaultdict(list)
        for reason_id, clause in enumerate(self.reasons):
            for literal in clause:
                temp[literal].append(reason_id)
        self.occurrences = {literal: tuple(ids) for literal, ids in sorted(temp.items())}
        self.false_count = [0] * len(self.reasons)
        self.assignment: dict[int, bool] = {}
        self.trail: list[TrailEvent] = []
        self.applicable: set[int] = {
            reason_id for reason_id, clause in enumerate(self.reasons) if not clause
        }
        self.forward_counter_updates = 0
        self.rollback_counter_updates = 0

    @property
    def literal_volume(self) -> int:
        return sum(len(clause) for clause in self.reasons)

    def checkpoint(self) -> int:
        return len(self.trail)

    def assign(self, variable: int, value: bool) -> tuple[int, ...]:
        if variable <= 0:
            raise ValueError("variable ids must be positive")
        if variable in self.assignment:
            raise ValueError("variable already assigned; rollback before reassignment")
        value = bool(value)
        false_literal = -variable if value else variable
        touched = self.occurrences.get(false_literal, ())
        self.assignment[variable] = value
        newly: list[int] = []
        for reason_id in touched:
            self.false_count[reason_id] += 1
            self.forward_counter_updates += 1
            if self.false_count[reason_id] == len(self.reasons[reason_id]):
                self.applicable.add(reason_id)
                newly.append(reason_id)
        self.trail.append(TrailEvent(variable, value, false_literal, tuple(touched)))
        return tuple(sorted(newly))

    def rollback(self, checkpoint: int) -> None:
        if not 0 <= checkpoint <= len(self.trail):
            raise ValueError("invalid rollback checkpoint")
        while len(self.trail) > checkpoint:
            event = self.trail.pop()
            for reason_id in reversed(event.touched_reason_ids):
                if self.false_count[reason_id] == len(self.reasons[reason_id]):
                    self.applicable.discard(reason_id)
                self.false_count[reason_id] -= 1
                self.rollback_counter_updates += 1
                if self.false_count[reason_id] < 0:
                    raise AssertionError("negative counter")
            del self.assignment[event.variable]

    def applicable_reason_ids(self) -> tuple[int, ...]:
        return tuple(sorted(self.applicable))

    def applicable_clauses(self) -> tuple[Clause, ...]:
        return tuple(self.reasons[i] for i in self.applicable_reason_ids())

    def direct_recompute(self) -> tuple[int, ...]:
        false_literals = {
            (-variable if value else variable)
            for variable, value in self.assignment.items()
        }
        return tuple(
            i for i, clause in enumerate(self.reasons) if set(clause) <= false_literals
        )

    def assert_exact(self) -> None:
        if self.applicable_reason_ids() != self.direct_recompute():
            raise AssertionError("incremental index disagrees with direct subset oracle")


def self_test() -> None:
    index = ReasonCacheIndex([(), (1, 2), (1, 2), (-1, 3), (2,), (-4, -5, 6)])
    assert index.applicable_clauses() == ((),)
    index.assert_exact()

    root = index.checkpoint()
    index.assign(1, False)
    index.assert_exact()
    after_x = index.checkpoint()
    index.assign(2, False)
    index.assert_exact()
    assert (2,) in index.applicable_clauses()
    assert (1, 2) in index.applicable_clauses()

    index.rollback(after_x)
    index.assert_exact()
    assert (2,) not in index.applicable_clauses()
    index.rollback(root)
    index.assert_exact()

    index.assign(1, True)
    index.assign(3, False)
    index.assert_exact()
    assert (-1, 3) in index.applicable_clauses()
    before = index.forward_counter_updates
    index.assign(99, True)
    assert index.forward_counter_updates == before
    index.rollback(root)
    index.assert_exact()

    monotone = ReasonCacheIndex([(1, 2), (-1, 3), (2,), (-4, -5, 6)])
    for variable, value in ((1, False), (2, False), (3, True), (4, True), (5, True), (6, False)):
        monotone.assign(variable, value)
        monotone.assert_exact()
    assert monotone.forward_counter_updates <= monotone.literal_volume
    touched = monotone.forward_counter_updates
    monotone.rollback(0)
    monotone.assert_exact()
    assert monotone.rollback_counter_updates == touched

    try:
        ReasonCacheIndex([(7, -7)])
    except ValueError:
        pass
    else:
        raise AssertionError("tautological reason must be rejected")

    print("C025_C1_REASON_CACHE_INDEX = PASS")
    print("C025_C1_SUBSET_QUERY_EXACTNESS = PASS")
    print("C025_C1_ROLLBACK_EXACTNESS = PASS")
    print("C025_C1_MONOTONE_UPDATES_LE_LITERAL_VOLUME = PASS")
    print("C025_C1_DUPLICATE_CANONICALIZATION = PASS")
    print("C025_C1_TAUTOLOGY_REJECTION = PASS")
    print(f"fixture_literal_volume = {monotone.literal_volume}")
    print(f"fixture_forward_updates = {touched}")
    print("claim_boundary = lookup polynomial in explicit cache volume only; M=poly(N) and new-reason proof search remain open")


if __name__ == "__main__":
    self_test()
