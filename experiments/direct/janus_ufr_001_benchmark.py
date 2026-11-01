#!/usr/bin/env python3
"""Bounded standalone UFR solver benchmark (NOT a C023 Policy-0A speedup).

Two modes run identical complete DPLL search; only the memo key differs:
exact uses original residual and ufr uses verified variable-renaming key.
A SAT cache hit transports and checks its model. UNSAT is recursively derived.
"""
from __future__ import annotations

import json
import random
import time
import tracemalloc
from dataclasses import dataclass

from janus_ufr_001 import canonicalize, normalize, variables, verify_model


def restrict(rows, variable, value, kind):
    remaining = []
    for row in rows:
        true_count = sum(abs(l) == variable and (l > 0) == value for l in row)
        rest = tuple(l for l in row if abs(l) != variable)
        if kind == 'SAT':
            if true_count:
                continue
            if not rest:
                return None
            remaining.append(rest)
        else:
            if true_count > 1:
                return None
            if true_count == 1:
                remaining.extend([(-lit,) for lit in rest])
            else:
                if not rest:
                    return None
                remaining.append(rest)
    return normalize(remaining)


@dataclass
class Stats:
    recursive_calls: int = 0
    cache_hits: int = 0
    unique_states: int = 0
    ufr_fallbacks: int = 0
    witness_checks: int = 0


class BudgetExceeded(Exception):
    pass


class DPLL:
    def __init__(self, kind='SAT', mode='exact', max_calls=100000):
        self.kind, self.mode, self.max_calls = kind, mode, max_calls
        self.memo = {}
        self.stats = Stats()

    def search(self, rows):
        self.stats.recursive_calls += 1
        if self.stats.recursive_calls > self.max_calls:
            raise BudgetExceeded
        rows = normalize(rows)
        if not rows:
            return True, {}
        if any(not row for row in rows):
            return False, None
        if self.mode == 'ufr':
            can = canonicalize(rows, self.kind)
            forward = can.mapping()
            inverse = {c: old for old, c in forward.items()}
            key = (self.kind, can.key)
            self.stats.ufr_fallbacks += int(not can.exhaustive)
        else:
            key = (self.kind, rows)
            forward = {v: v for v in variables(rows)}
            inverse = forward
        if key in self.memo:
            self.stats.cache_hits += 1
            answer, old_model = self.memo[key]
            if not answer:
                return False, None
            restored = {inverse[v]: b for v, b in old_model.items()}
            restored = {v: restored.get(v, False) for v in variables(rows)}
            if not verify_model(rows, restored, self.kind):
                raise AssertionError('SAT witness transport failed')
            self.stats.witness_checks += 1
            return True, restored
        self.stats.unique_states += 1
        frequency = {}
        for row in rows:
            for lit in row:
                frequency[abs(lit)] = frequency.get(abs(lit), 0) + 1
        pivot = min(frequency, key=lambda v: (-frequency[v], v))
        for value in (False, True):
            child = restrict(rows, pivot, value, self.kind)
            if child is None:
                continue
            answer, model = self.search(child)
            if answer:
                assert model is not None
                model = {**model, pivot: value}
                model = {v: model.get(v, False) for v in variables(rows)}
                assert verify_model(rows, model, self.kind)
                cached_model = {forward[v]: b for v, b in model.items()}
                self.memo[key] = (True, cached_model)
                return True, model
        self.memo[key] = (False, None)
        return False, None


def workload():
    random_gen = random.Random(101)
    source_sat = ((1, 2, 3), (-1, 2, -3), (1, -2, 4), (-1, -3, -4),
                  (2, 3, -4), (-2, -3, 4), (1, -3, 4))
    source_one = ((1, 2, -3), (-1, 3, 4), (-2, -4, 5), (2, -4, -5))
    source_unsat = ((1, 2), (-1, 2), (1, -2), (-1, -2))
    families = [('SAT', source_sat), ('EXACT_ONE', source_one), ('SAT', source_unsat)]
    for kind, source in families:
        originals = sorted({abs(l) for row in source for l in row})
        formulas = [source]
        for _ in range(12):
            targets = random_gen.sample(range(20, 300), len(originals))
            mapping = dict(zip(originals, targets))
            formulas.append(tuple(tuple((1 if l > 0 else -1) * mapping[abs(l)] for l in row)
                                  for row in source))
        yield kind, formulas


def benchmark_group(kind, formulas, mode):
    solver = DPLL(kind, mode)
    tracemalloc.start()
    start = time.perf_counter()
    results = []
    status = 'COMPLETE'
    try:
        for f in formulas:
            sat, model = solver.search(f)
            if sat:
                assert model is not None and verify_model(f, model, kind)
            results.append(sat)
    except BudgetExceeded:
        status = 'BUDGET_EXCEEDED'
    seconds = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return dict(status=status, answers=results, wall_seconds=round(seconds, 6),
                peak_tracemalloc_bytes=peak, **vars(solver.stats))


def main():
    outputs = []
    for index, (kind, formulas) in enumerate(workload()):
        exact = benchmark_group(kind, formulas, 'exact')
        ufr = benchmark_group(kind, formulas, 'ufr')
        assert exact['status'] == ufr['status'] == 'COMPLETE'
        assert exact['answers'] == ufr['answers']
        outputs.append({'family': f'SYNTHETIC_{index}_{kind}', 'formulas': len(formulas),
                        'exact': exact, 'ufr': ufr})
    print(json.dumps({'experiment': 'JANUS-UFR-001', 'status': 'LOCAL_SYNTHETIC_ONLY',
          'baseline': 'standalone exact DPLL, not C023',
          'claim_boundary': 'finite results, no universal complexity or P-vs-NP claim',
          'groups': outputs}, indent=2))


if __name__ == '__main__':
    main()
