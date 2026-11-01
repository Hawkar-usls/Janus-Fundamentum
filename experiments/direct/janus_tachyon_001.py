#!/usr/bin/env python3
"""JANUS-TACHYON-001: speculative future-echo / retrograde SAT guidance.

No tachyons, backwards-in-time communication, quantum advantage or P=NP.
"Future echo" is a FALLIBLE candidate model reconstructed from current clauses.
It can suggest value/variable ordering and can be accepted as a SAT witness
ONLY after independently evaluating every constraint; it never eliminates
other branches, changes proof semantics or establishes UNSAT.

A separate bounded generalized-arc-consistency (GAC) pass is sound, based on
EXACT support in each local constraint and independent of the untrusted echo.
This is ordinary bidirectional constraint reasoning, not a new SAT theorem.
Research-only branch, n<=10 for independent exhaustive falsification.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from time import perf_counter
from typing import Iterable

from janus_ufr_001 import normalize

MAX_VARS = 10
MAX_ROW_VARS = 8
MAX_ROWS = 128
ZERO, ONE, BOTH = 1, 2, 3


def _valid(rows: Iterable[Iterable[int]], n: int, kind: str):
    if type(n) is not int or not 1 <= n <= MAX_VARS:
        raise ValueError("bounded research n must be 1..10")
    if kind not in ("SAT", "EXACT_ONE"):
        raise ValueError("kind must be SAT or EXACT_ONE")
    rs = normalize(rows)  # Preserves repeated literal multiplicity in Exact-One
    if len(rs) > MAX_ROWS or any(
        len({abs(lit) for lit in row}) > MAX_ROW_VARS or
        any(abs(lit) > n for lit in row)
        for row in rs
    ):
        raise ValueError("unbounded constraint width, count or variable")
    return rs


def evaluate(rows: tuple[tuple[int, ...], ...], x: int, kind: str) -> bool:
    for row in rows:
        count = sum(bool((x >> (abs(lit) - 1)) & 1) == (lit > 0)
                    for lit in row)
        if kind == "SAT" and count == 0:
            return False
        if kind == "EXACT_ONE" and count != 1:
            return False
    return True


def initial_echo(rows, n: int) -> tuple[int, ...]:
    """Untrusted terminal-state hypothesis from weighted literal votes."""
    scores = [0] * n
    for row in rows:
        # Short constraints get greater voting weight, without SAT inference.
        width = max(1, len(row))
        vote = max(1, 64 // width)
        for lit in row:
            scores[abs(lit) - 1] += vote if lit > 0 else -vote
    return tuple(int(score >= 0) for score in scores)


def domains_gac(rows, n: int, kind: str, domains: tuple[int, ...],
                *, arc_consistency: bool) -> tuple[int, ...] | None:
    """Constraint propagation, never driven by the speculative future echo.

    For SAT/Exact-One each local variable value is retained iff it has
    a supporting assignment of *all other variables in that same row*.
    Repeated variables are enumerated ONCE, repeated literals counted as-is.
    """
    current = list(domains)
    if any(type(d) is not int or d not in (ZERO, ONE, BOTH) for d in current):
        raise ValueError("invalid domain")
    if not arc_consistency:
        # Baseline only applies forced constraints (unit propagation) by
        # assigning values if *all* satisfying assignments agree on a var.
        # This is still local sound propagation, weaker than generalized AC.
        return _propagate(rows, n, kind, current, gac=False)
    return _propagate(rows, n, kind, current, gac=True)


def _propagate(rows, n, kind, current, *, gac: bool):
    while True:
        changed = False
        for row in rows:
            scope = tuple(sorted({abs(lit) for lit in row}))
            support = {v: 0 for v in scope}
            exists = False
            options = [
                tuple(value for value in (0, 1) if current[v - 1] & (1 << value))
                for v in scope
            ]
            for values in product(*options):
                bits = dict(zip(scope, values))
                hits = sum(bits[abs(l)] == int(l > 0) for l in row)
                if (hits >= 1 if kind == "SAT" else hits == 1):
                    exists = True
                    for v, value in bits.items():
                        support[v] |= (1 << value)
            if not exists:
                return None
            for v in scope:
                old = current[v - 1]
                target = old & support[v]
                if not target:
                    return None
                if gac:
                    # GAC: remove every local unsupported value.
                    updated = target
                else:
                    # Conservative unit/fixed-value propagation; a smaller
                    # support set can be accepted only when singleton.
                    updated = target if target in (ZERO, ONE) else old
                if updated != old:
                    current[v - 1] = updated
                    changed = True
        if not changed:
            return tuple(current)


@dataclass(frozen=True)
class SearchResult:
    answer: bool
    candidate: int | None
    nodes: int
    echoed_candidate_checked: bool
    echoed_candidate_accepted: bool
    exact_support_pruning: bool
    elapsed_seconds: float
    result_verified: bool


def search(rows: Iterable[Iterable[int]], n: int, kind: str = "SAT", *,
           echo: tuple[int, ...] | None = None, strategy: str = "retrograde",
           gac: bool = True) -> SearchResult:
    """Complete bounded DPLL with speculative candidate checked, never assumed.

    The speculative echo changes only the candidate-first and branch order.
    Exhaustive fallback always explores both values before declaring UNSAT.
    """
    formula = _valid(rows, n, kind)
    if strategy not in ("retrograde", "forward"):
        raise ValueError("strategy must be retrograde or forward")
    if echo is None:
        echo = initial_echo(formula, n)
    if (type(echo) is not tuple or len(echo) != n or
        any(type(v) is not int or v not in (0, 1) for v in echo)):
        raise ValueError("untrusted echo must be a complete 0/1 hypothesis")

    start = perf_counter()
    echoed = sum(v << i for i, v in enumerate(echo))
    accepted = strategy == "retrograde" and evaluate(formula, echoed, kind)
    nodes = 0
    found = echoed if accepted else None
    # Baseline starts with zero and branches first in 0,1 order.
    if found is None:
        incidence = [0] * n
        for row in formula:
            for v in {abs(lit) for lit in row}:
                incidence[v - 1] += 1

        def descend(domains: tuple[int, ...]) -> int | None:
            nonlocal nodes
            nodes += 1
            filtered = domains_gac(formula, n, kind, domains, arc_consistency=gac)
            if filtered is None:
                return None
            undecided = [v for v in range(n) if filtered[v] == BOTH]
            if not undecided:
                x = sum((d == ONE) << i for i, d in enumerate(filtered))
                # A complete model is NEVER inferred from hints.
                return x if evaluate(formula, x, kind) else None
            if strategy == "retrograde":
                v = max(undecided, key=lambda i: (incidence[i], -i))
                choices = (ONE, ZERO) if echo[v] else (ZERO, ONE)
            else:
                v = min(undecided)
                choices = (ZERO, ONE)
            for value in choices:
                trial = list(filtered)
                trial[v] = value
                result = descend(tuple(trial))
                if result is not None:
                    return result
            return None

        found = descend((BOTH,) * n)
    answer = found is not None
    verified = (
        evaluate(formula, found, kind) if found is not None
        else all(not evaluate(formula, x, kind) for x in range(1 << n))
    )
    if not verified:
        raise AssertionError("incorrect SAT candidate or UNSAT verdict")
    return SearchResult(
        answer=answer, candidate=found, nodes=nodes,
        echoed_candidate_checked=(strategy == "retrograde"),
        echoed_candidate_accepted=accepted,
        exact_support_pruning=gac,
        elapsed_seconds=perf_counter() - start,
        result_verified=True,
    )
