#!/usr/bin/env python3
"""Executable regression for C025 unit-free raw elimination envelope.

The theorem is algebraic. This finite regression checks the theorem against the
frozen eliminate_var_capped implementation on many small canonical unit-free
states. Finite enumeration is implementation evidence only. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


def envelope(s: int) -> float:
    return 1.0 + ((s - 1) ** 2) / 12.0


def polarity_counts(cnf: base.CNF, x: int) -> tuple[int, int]:
    return sum(x in c for c in cnf), sum(-x in c for c in cnf)


def verify_state(cnf: base.CNF) -> int:
    if any(len(c) < 2 for c in cnf):
        raise ValueError("UNIT_FREE_STATE_REQUIRED")
    s = base.state_units(cnf)
    checked = 0
    # Huge cap so we inspect actual raw accounting rather than intentionally abort.
    cap = max(10_000, s * s * s)
    for x in base.vars_of(cnf):
        p, q = polarity_counts(cnf, x)
        out, stats = base.eliminate_var_capped(cnf, x, cap)
        if out is None:
            raise AssertionError("UNEXPECTED_ABORT_UNDER_REGRESSION_CAP")
        raw = int(stats["raw_units"])
        if p and q:
            if raw > envelope(s) + 1e-12:
                raise AssertionError(("MIXED_RAW_ENVELOPE_FAILURE", cnf, x, s, raw, envelope(s)))
        else:
            if raw > s:
                raise AssertionError(("PURE_RAW_ENVELOPE_FAILURE", cnf, x, s, raw))
        if not base.verify_elimination_transition(cnf, x, out, cap):
            raise AssertionError("ELIMINATION_REPLAY_FAILED")
        checked += 1
    return checked


def clause_universe_3vars_unit_free() -> tuple[base.Clause, ...]:
    rows = set()
    # All signed supports of width 2 or 3 on variables 1..3.
    for support_size in (2, 3):
        for support in combinations((1, 2, 3), support_size):
            for mask in range(1 << support_size):
                c = tuple(v if ((mask >> i) & 1) else -v for i, v in enumerate(support))
                cc = base.canon_clause(c)
                if cc is not None:
                    rows.add(cc)
    return tuple(sorted(rows, key=lambda c: (len(c), c)))


def exhaustive_regression() -> tuple[int, int]:
    U = clause_universe_3vars_unit_free()
    seen: set[base.CNF] = set()
    pivots = 0
    for k in (1, 2, 3, 4):
        for selected in combinations(U, k):
            cnf = base.canon_cnf(selected)
            if not cnf or cnf in seen or any(len(c) < 2 for c in cnf):
                continue
            seen.add(cnf)
            pivots += verify_state(cnf)
    return len(seen), pivots


def first_ordinary_small_root_regression() -> int:
    roots = (
        base.canon_cnf(((1, 2), (-1, 3), (2, -3))),
        base.canon_cnf(((1, 2, 3), (-1, 2, 3), (1, -2, 3), (1, 2, -3))),
        base.canon_cnf(((1,), (-1, 2, 3), (2, -3))),
    )
    checked = 0
    for root in roots:
        N = base.input_size_units(root)
        residual, implied, ok, _ = base.unit_propagate(root)
        if not ok or () in residual or not residual:
            continue
        # If one pass produced units, drive to the same fixed point the solver
        # reaches by repeating its unit stage.
        while True:
            nxt, imp2, ok2, _ = base.unit_propagate(residual)
            if not ok2 or () in nxt or not nxt:
                residual = nxt
                break
            if not imp2:
                residual = nxt
                break
            residual = nxt
        if not residual or any(len(c) < 2 for c in residual):
            continue
        assert base.state_units(residual) <= base.state_units(root)
        for x in base.vars_of(residual):
            out, stats = base.eliminate_var_capped(residual, x, N * N)
            if out is None:
                raise AssertionError(("FIRST_ORDINARY_ROOT_PIVOT_ABORTED", root, x, N))
            checked += 1
    return checked


def selftest() -> None:
    states, pivots = exhaustive_regression()
    root_pivots = first_ordinary_small_root_regression()
    print(f"UNIT_FREE_ENVELOPE_SMALL_STATES={states}")
    print(f"UNIT_FREE_ENVELOPE_SMALL_PIVOTS={pivots}")
    print(f"FIRST_ORDINARY_ROOT_PIVOTS={root_pivots}")
    print("UNIT_FREE_RAW_ENVELOPE=PASS")
    print("FIRST_ORDINARY_ALL_PIVOTS_SAFE_REGRESSION=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
