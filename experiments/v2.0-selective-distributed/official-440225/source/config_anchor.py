from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

from sat_core import SATInstance, SATState, touched_variables


@dataclass(frozen=True)
class V20Config:
    charge_growth: float = 1.075
    charge_add: float = 0.16
    charge_decay: float = 0.988
    charge_cap: float = 56.0
    survive_stagn_factor: float = 0.42
    chaos_stagn_factor: float = 0.78
    memory_gap: int = 2
    max_packet_width: int = 5
    packet_samples: int = 2
    telemetry_period_ticks: int = 8
    proof_scan: bool = True
    allow_single_uphill: bool = True
    enable_zim_from_n: int = 64


def complete_sign_core_witness(inst: SATInstance):
    """Sound but deliberately narrow UNSAT witness.

    If every sign pattern over one fixed variable set appears as a clause,
    no assignment can satisfy all clauses. Not finding this witness is not
    evidence of satisfiability.
    """
    groups: dict[tuple[int, ...], set[int]] = defaultdict(set)
    for clause in inst.clauses:
        vars_ = tuple(sorted(abs(lit) - 1 for lit in clause))
        if not vars_ or len(vars_) > 12:
            continue
        signs = {abs(lit) - 1: lit > 0 for lit in clause}
        mask = 0
        for j, v in enumerate(vars_):
            if signs[v]:
                mask |= 1 << j
        groups[vars_].add(mask)
    for vars_, masks in groups.items():
        if len(masks) == 1 << len(vars_):
            return {"variables": list(vars_), "patterns": len(masks)}
    return None


def _restore_state(st: SATState, target: list[int]) -> int:
    used = 0
    for v, (a, b) in enumerate(zip(st.a, target)):
        if a != b:
            st.flip(v)
            used += 1
    return used


class AnchorLane:
    """Stable control lane: counted version of the original Junction Base."""

    def __init__(self, inst: SATInstance, initial: list[int], rng: random.Random):
        self.inst = inst
        self.rng = rng
        self.st = SATState(inst, initial)
        self.n = inst.n
        self.m = len(inst.clauses)
        self.charge = [1.0] * self.m
        self.momentum = [0.0] * self.n
        self.best = self.st.satisfied
        self.best_assignment = self.st.a.copy()
        self.stagn = 0
        self.ticks = 0
        self.committed_flips = 0
        self.escapes = 0

    @property
    def solved(self) -> bool:
        return not self.st.unsat

    def tick(self) -> None:
        if self.solved:
            return
        self.ticks += 1
        us = self.st.unsat.copy()
        for i in range(self.m):
            self.charge[i] = min(24.0, self.charge[i] * 1.12 + 0.15) if i in us else max(1.0, self.charge[i] * 0.985)
        for j in range(self.n):
            self.momentum[j] *= 0.90
        touched = touched_variables(self.inst, us)
        if not touched:
            return
        v = max((sum(self.charge[i] for i, _ in self.inst.occurrences[vv] if i in us)
                 + 1.8 * self.st.delta(vv, self.charge)
                 + 0.35 * self.momentum[vv]
                 + self.rng.uniform(-0.2, 0.2), vv) for vv in touched)[1]
        old = self.st.satisfied
        new = self.st.flip(v)
        self.committed_flips += 1
        self.momentum[v] = 0.75 * self.momentum[v] + new - old
        if new > self.best:
            self.best = new
            self.best_assignment = self.st.a.copy()
            self.stagn = 0
        else:
            self.stagn += 1

        if self.stagn > max(20, self.n // 2) and self.st.unsat:
            hottest = sorted(self.st.unsat, key=lambda i: self.charge[i], reverse=True)[:max(2, self.n // 16)]
            pool = list({abs(lit) - 1 for i in hottest for lit in self.inst.clauses[i]})
            if pool:
                width = min(len(pool), max(1, self.n // 20))
                for vv in self.rng.sample(pool, width):
                    self.st.flip(vv)
                    self.committed_flips += 1
                if self.st.satisfied > self.best:
                    self.best = self.st.satisfied
                    self.best_assignment = self.st.a.copy()
                self.escapes += 1
            self.stagn = 0
