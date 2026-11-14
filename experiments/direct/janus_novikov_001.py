#!/usr/bin/env python3
"""JANUS-NOVIKOV-001: global consistency of speculative SAT end states.

Research analogy to Novikov's self-consistency principle; entirely classical
forward-time code. No physical CTC, tachyon, future message, P=NP, or SAT
completeness shortcut. A speculation must satisfy EVERY clause to be promoted
to a model. A bad prediction is repaired by ordinary strict-descent greedy
1-bit local search. A stalled prediction is NOT UNSAT; complete DPLL fallback
or the independent C023 certificate must make that decision.

Each repair step has a checkable, strictly decreasing violated-row energy.
Therefore loops cannot silently appear, and neither a fabricated fixed point
nor an unsound proof can cross from the guess into trusted solver evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from janus_tachyon_001 import (
    _valid, evaluate, initial_echo, search, MAX_ROWS,
)
from janus_ufr_001 import verify_model


@dataclass(frozen=True)
class RepairStep:
    bits: int
    violated_clauses: int
    changed_variable: int | None


@dataclass(frozen=True)
class ConsistencyReceipt:
    status: str
    original_candidate: int
    final_candidate: int
    start_violations: int
    final_violations: int
    steps: tuple[RepairStep, ...]
    independently_verified: bool


@dataclass(frozen=True)
class GuidedResult:
    answer: bool
    candidate: int | None
    nodes: int
    full_wall_seconds: float
    repair_wall_seconds: float
    hypothesis_status: str
    repair_steps: int
    independent_repair_audit_pass: bool
    independent_search_verification_pass: bool
    fallback_strategy: str


def violated_rows(rows: tuple[tuple[int, ...], ...], bits: int, kind: str) -> int:
    """Energy is the number of violated original clauses, not a belief score."""
    return sum(not evaluate((row,), bits, kind) for row in rows)


def _bits_to_hint(bits: int, n: int) -> tuple[int, ...]:
    return tuple((bits >> i) & 1 for i in range(n))


def _candidate_int(hint: tuple[int, ...], n: int) -> int:
    if (type(hint) is not tuple or len(hint) != n or
            any(type(bit) is not int or bit not in (0, 1) for bit in hint)):
        raise ValueError("candidate must be a full binary tuple")
    return sum(bit << i for i, bit in enumerate(hint))


def independent_model(rows, n: int, kind: str, bits: int) -> bool:
    """Use separately implemented UFR semantics, not energy bookkeeping."""
    assignment = {i: bool(bits & (1 << (i - 1))) for i in range(1, n+1)}
    return verify_model(rows, assignment, kind)


def repair(rows, n: int, kind: str = "SAT", *,
           hint: tuple[int, ...] | None = None) -> ConsistencyReceipt:
    """Attempt deterministic global agreement; do not infer UNSAT from stalling.

    Select the single-bit neighbor with STRICTLY fewer violated clauses.
    Ties are resolved deterministically by (remaining violations, Hamming
    distance to initial proposal, variable index). Each successful step costs
    at least one whole violated clause, so there are <= len(rows) steps.
    """
    formula = _valid(rows, n, kind)
    proposal = initial_echo(formula, n) if hint is None else hint
    seed = _candidate_int(proposal, n)
    current = seed
    energy = violated_rows(formula, current, kind)
    initial_energy = energy
    steps = [RepairStep(current, energy, None)]
    while energy > 0:
        candidates = []
        for i in range(n):
            changed = current ^ (1 << i)
            changed_energy = violated_rows(formula, changed, kind)
            if changed_energy < energy:
                distance_to_seed = (changed ^ seed).bit_count()
                candidates.append((changed_energy, distance_to_seed, i, changed))
        if not candidates:
            break
        best_energy, _, i, new = min(candidates)
        current, energy = new, best_energy
        steps.append(RepairStep(current, energy, i + 1))
        if len(steps) > len(formula) + 1:
            raise AssertionError("strict descent did not terminate in <= clauses")
    is_model = energy == 0
    independently_verified = independent_model(formula, n, kind, current)
    if independently_verified != is_model:
        raise AssertionError("independent CNF semantics contradict energy count")
    return ConsistencyReceipt(
        status="GLOBAL_MODEL_VERIFIED" if is_model else "LOCAL_MINIMUM_NOT_UNSAT",
        original_candidate=seed, final_candidate=current,
        start_violations=initial_energy, final_violations=energy,
        steps=tuple(steps), independently_verified=independently_verified,
    )


def audit_repair(rows, n: int, kind: str, receipt: ConsistencyReceipt) -> bool:
    """Recompute the entire repair transcript, including deterministic ties.

    Test author cannot freely forge a 'Novikov certificate': the audit only
    authenticates a candidate/local descent, NEVER a proof of UNSAT.
    """
    formula = _valid(rows, n, kind)
    if not isinstance(receipt, ConsistencyReceipt) or not receipt.steps:
        raise AssertionError("missing finite repair transcript")
    if receipt.steps[0] != RepairStep(
        receipt.original_candidate,
        violated_rows(formula, receipt.original_candidate, kind), None):
        raise AssertionError("invalid initial state/energy")
    if len(receipt.steps) > len(formula) + 1:
        raise AssertionError("repair transcript exceeds strict-descent bound")
    # Re-derive what the deterministic algorithm itself would do from this
    # externally provided seed; do not trust its stage metadata.
    reference = repair(formula, n, kind,
                       hint=_bits_to_hint(receipt.original_candidate, n))
    if reference != receipt:
        raise AssertionError("tampered energy, step, tie-break, or verdict")
    return True


def finite_fixed_points(mapping: tuple[int, ...]) -> tuple[int, ...]:
    """Toy self-referential histories: x=F(x), NEVER a workflow feedback edge.

    A map with no fixed point is an inconsistent toy feedback model, but
    it does not demonstrate the physical absence of time loops.
    """
    if (type(mapping) is not tuple or not 1 <= len(mapping) <= 1024 or
            any(type(v) is not int or v < 0 or v >= len(mapping)
                for v in mapping)):
        raise ValueError("finite map must be total, in range and bounded")
    return tuple(i for i, j in enumerate(mapping) if i == j)


def guided_search(rows, n: int, kind: str = "SAT", *,
                  hint: tuple[int, ...] | None = None,
                  fallback: str = "candidate_first") -> GuidedResult:
    """Run actual bounded SAT solver with input-derived *checked* hint.

    Both variants pay for exactly the same greedy projection and replay.
    On local-minimum failure, candidate is merely branch guidance; full
    fallback explores all alternatives and independent UNSAT enumeration.
    """
    if fallback not in ("candidate_first", "retrograde"):
        raise ValueError("only complete fallbacks are permitted")
    start = perf_counter()
    formula = _valid(rows, n, kind)
    if hint is None:
        hint = initial_echo(formula, n)
    phase_start = perf_counter()
    receipt = repair(formula, n, kind, hint=hint)
    if not audit_repair(formula, n, kind, receipt):
        raise AssertionError("consistency transcript failed independent audit")
    repair_wall = perf_counter() - phase_start
    output = search(formula, n, kind, echo=_bits_to_hint(receipt.final_candidate, n),
                    strategy=fallback, gac=True)
    if receipt.independently_verified and (
            output.candidate != receipt.final_candidate or not output.answer):
        raise AssertionError("verified fixed point was not returned by solver")
    if not output.result_verified:
        raise AssertionError("unverified solver output")
    return GuidedResult(
        answer=output.answer, candidate=output.candidate, nodes=output.nodes,
        full_wall_seconds=perf_counter() - start,
        repair_wall_seconds=repair_wall,
        hypothesis_status=receipt.status,
        repair_steps=len(receipt.steps)-1,
        independent_repair_audit_pass=True,
        independent_search_verification_pass=True,
        fallback_strategy=fallback,
    )
