from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import product
from typing import Iterable

@dataclass(frozen=True)
class SATInstance:
    n: int
    clauses: tuple[tuple[int, ...], ...]
    occurrences: tuple[tuple[tuple[int, bool], ...], ...]

    @classmethod
    def build(cls, n: int, clauses: Iterable[Iterable[int]]) -> "SATInstance":
        cs = tuple(tuple(c) for c in clauses)
        occ: list[list[tuple[int, bool]]] = [[] for _ in range(n)]
        for ci, clause in enumerate(cs):
            seen: set[int] = set()
            for lit in clause:
                v = abs(lit) - 1
                if not 0 <= v < n:
                    raise ValueError(f"literal {lit} outside 1..{n}")
                if v in seen:
                    raise ValueError("duplicate variable inside clause")
                seen.add(v)
                occ[v].append((ci, lit < 0))
        return cls(n=n, clauses=cs, occurrences=tuple(tuple(x) for x in occ))


class SATState:
    def __init__(self, inst: SATInstance, assignment: list[int]):
        self.inst = inst
        self.a = assignment.copy()
        self.counts = [0] * len(inst.clauses)
        self.unsat: set[int] = set()
        for ci, clause in enumerate(inst.clauses):
            cnt = 0
            for lit in clause:
                v = abs(lit) - 1
                cnt += self.a[v] if lit > 0 else 1 - self.a[v]
            self.counts[ci] = cnt
            if cnt == 0:
                self.unsat.add(ci)
        self.satisfied = len(inst.clauses) - len(self.unsat)

    def delta(self, v: int, weights: list[float] | None = None) -> float:
        d = 0.0
        old_value = self.a[v]
        for ci, neg in self.inst.occurrences[v]:
            old_lit = (1 - old_value) if neg else old_value
            new_count = self.counts[ci] + (1 - old_lit) - old_lit
            before = self.counts[ci] > 0
            after = new_count > 0
            if before != after:
                w = 1.0 if weights is None else weights[ci]
                d += w if after else -w
        return d

    def flip(self, v: int) -> int:
        old_value = self.a[v]
        for ci, neg in self.inst.occurrences[v]:
            old_lit = (1 - old_value) if neg else old_value
            was_sat = self.counts[ci] > 0
            self.counts[ci] += (1 - old_lit) - old_lit
            now_sat = self.counts[ci] > 0
            if was_sat and not now_sat:
                self.unsat.add(ci)
                self.satisfied -= 1
            elif not was_sat and now_sat:
                self.unsat.discard(ci)
                self.satisfied += 1
        self.a[v] ^= 1
        return self.satisfied

    def hot_unsat_charge(self, clause_ids: Iterable[int], charge: list[float]) -> float:
        return sum(charge[i] for i in clause_ids if i in self.unsat)


def gen_planted(n: int, m: int, k: int, rng: random.Random) -> SATInstance:
    planted = [rng.randrange(2) for _ in range(n)]
    clauses: list[list[int]] = []
    for _ in range(m):
        vs = rng.sample(range(n), k)
        while True:
            lits = []
            satisfied = False
            for v in vs:
                neg = bool(rng.randrange(2))
                lit = -(v + 1) if neg else (v + 1)
                lits.append(lit)
                satisfied |= bool((1 - planted[v]) if neg else planted[v])
            if satisfied:
                clauses.append(lits)
                break
    return SATInstance.build(n, clauses)


def gen_unsat_core(n: int, m: int, k: int, rng: random.Random) -> SATInstance:
    """Guaranteed UNSAT k-CNF: all 2^k sign patterns on one variable set, plus random distractor clauses."""
    if m < 2**k:
        raise ValueError("m must fit the complete contradiction core")
    core_vars = rng.sample(range(n), k)
    clauses: list[list[int]] = []
    for signs in product((False, True), repeat=k):
        clauses.append([-(v + 1) if neg else (v + 1) for v, neg in zip(core_vars, signs)])
    while len(clauses) < m:
        vs = rng.sample(range(n), k)
        clauses.append([-(v + 1) if rng.randrange(2) else (v + 1) for v in vs])
    rng.shuffle(clauses)
    return SATInstance.build(n, clauses)


def touched_variables(inst: SATInstance, unsat: set[int]) -> set[int]:
    return {abs(lit) - 1 for ci in unsat for lit in inst.clauses[ci]}


def common_diag(**kwargs) -> dict:
    base = {
        "escapes": 0,
        "escape_attempts": 0,
        "immediate_improving_escapes": 0,
        "accepted_uphill": 0,
        "max_depth": 0.0,
        "mean_depth": 0.0,
        "thermal_rejects": 0,
    }
    base.update(kwargs)
    return base
