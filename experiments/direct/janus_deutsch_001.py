#!/usr/bin/env python3
"""JANUS-DEUTSCH-001: bounded, classical quantum-circuit reference simulator.

Research only. Implements a truth-table-derived, reversible controlled-X
Boolean oracle, phase kickback, the Deutsch–Jozsa interference control and
Grover amplitude amplification. Every statevector is CLASSICALLY simulated.
No quantum hardware, resource advantage or general SAT speedup is claimed.

Reversible synthesis via algebraic normal form (ANF) is exact but may require
exponentially many gates. The simulator explicitly caps n <= 8.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt
from typing import Iterable, Mapping

from janus_ufr_001 import normalize, verify_renaming

Rows = tuple[tuple[int, ...], ...]
MAX_QUBITS = 8


def validate(rows: Iterable[Iterable[int]], n: int, kind: str) -> Rows:
    if type(n) is not int or not (1 <= n <= MAX_QUBITS):
        raise ValueError("Only 1..8 input qubits are supported by this simulator")
    if kind not in ("SAT", "EXACT_ONE"):
        raise ValueError("kind must be SAT or EXACT_ONE")
    result = normalize(rows)  # Exact-One multiplicity is intentionally retained.
    if any(abs(literal) > n for clause in result for literal in clause):
        raise ValueError("literal references variable outside the input register")
    return result


def evaluate(rows: Rows, index: int, kind: str) -> bool:
    """Inputs are fixed by validate; index bit (v-1) is Boolean variable v."""
    for clause in rows:
        true_count = sum(
            bool(index & (1 << (abs(lit) - 1))) == (lit > 0)
            for lit in clause
        )
        if kind == "SAT" and true_count == 0:
            return False
        if kind == "EXACT_ONE" and true_count != 1:
            return False
    return True


def truth_table(rows: Rows, n: int, kind: str) -> tuple[int, ...]:
    normalized = validate(rows, n, kind)
    return tuple(int(evaluate(normalized, x, kind)) for x in range(1 << n))


def anf_gates(table: tuple[int, ...]) -> tuple[int, ...]:
    """Möbius transform: f(x) = XOR_{mask subset x} a[mask].

    A 'gate' is an open-target multi-controlled-X acting on ancilla b;
    mask=0 is unconditional NOT. This describes a logically reversible
    circuit; hardware decomposition and fault tolerance are NOT modeled.
    """
    size = len(table)
    if size < 2 or size > 1 << MAX_QUBITS or size & (size - 1):
        raise ValueError("truth table length must be power of 2 in [2,256]")
    if any(type(v) is not int or v not in (0, 1) for v in table):
        raise ValueError("truth values must be 0 or 1")
    coeff = list(table)
    n = size.bit_length() - 1
    for bit in range(n):
        for mask in range(size):
            if mask & (1 << bit):
                coeff[mask] ^= coeff[mask ^ (1 << bit)]
    return tuple(mask for mask in range(size) if coeff[mask])


def apply_anf(x: int, ancilla: int, gates: tuple[int, ...], n: int) -> tuple[int, int]:
    """Classical basis-state action of a reversible (n+1)-qubit circuit."""
    if type(x) is not int or not (0 <= x < 1 << n) or ancilla not in (0, 1):
        raise ValueError("invalid basis state")
    y = ancilla
    for mask in gates:
        if x & mask == mask:
            y ^= 1
    return x, y


@dataclass(frozen=True)
class Circuit:
    n: int
    kind: str
    rows: Rows
    table: tuple[int, ...]
    gates: tuple[int, ...]

    @classmethod
    def build(cls, rows: Iterable[Iterable[int]], n: int, kind: str = "SAT") -> "Circuit":
        normalized = validate(rows, n, kind)
        table = truth_table(normalized, n, kind)
        return cls(n, kind, normalized, table, anf_gates(table))

    def check_reversible(self) -> bool:
        """Full truth-table and involution checks for every x and both b."""
        for x, fx in enumerate(self.table):
            for b in (0, 1):
                output = apply_anf(x, b, self.gates, self.n)
                if output != (x, b ^ fx):
                    return False
                if apply_anf(*output, self.gates, self.n) != (x, b):
                    return False
        return True

    @property
    def total_controls(self) -> int:
        return sum(mask.bit_count() for mask in self.gates)


def relabel_index(index: int, mapping: Mapping[int, int]) -> int:
    """Push assignment through a verified old-variable -> new-variable bijection."""
    if len(set(mapping.values())) != len(mapping) or any(
        type(v) is not int or v <= 0 for v in (*mapping.keys(), *mapping.values())
    ):
        raise ValueError("mapping must be positive integer variable bijection")
    output = 0
    for old, new in mapping.items():
        if index & (1 << (old - 1)):
            output |= 1 << (new - 1)
    return output


def check_ufr_covariance(left: Circuit, right: Circuit,
                         mapping: Mapping[int, int]) -> bool:
    if left.n != right.n or left.kind != right.kind:
        return False
    if set(mapping) != set(range(1, left.n + 1)) or set(mapping.values()) != set(
        range(1, left.n + 1)
    ):
        return False
    if not verify_renaming(left.rows, right.rows, mapping, left.kind):
        return False
    return all(
        left.table[x] == right.table[relabel_index(x, mapping)]
        for x in range(1 << left.n)
    )


def phase_kickback(circuit: Circuit, input_state: tuple[complex, ...]) -> tuple[complex, ...]:
    """Uf on |x>|-> produces (-1)^f(x) phase on input x, with clean ancilla."""
    if len(input_state) != 1 << circuit.n:
        raise ValueError("statevector dimension mismatch")
    result = [0j] * len(input_state)
    for x, amp in enumerate(input_state):
        _, out_zero = apply_anf(x, 0, circuit.gates, circuit.n)
        _, out_one = apply_anf(x, 1, circuit.gates, circuit.n)
        # Negative eigenstate of X; explicit ancilla consistency check.
        assert out_one == 1 - out_zero
        result[x] = (-amp if out_zero else amp)
    return tuple(result)


def hadamard_all(state: tuple[complex, ...]) -> tuple[complex, ...]:
    """Normalized Walsh-Hadamard transform; no external quantum library."""
    n_states = len(state)
    if n_states < 2 or n_states & (n_states - 1):
        raise ValueError("statevector size must be power of two")
    out = list(state)
    stride = 1
    while stride < n_states:
        for start in range(0, n_states, stride * 2):
            for k in range(start, start + stride):
                a, b = out[k], out[k + stride]
                out[k] = (a + b) / sqrt(2)
                out[k + stride] = (a - b) / sqrt(2)
        stride *= 2
    return tuple(out)


def deutsch_jozsa_zero_probability(circuit: Circuit) -> float:
    """P(measure 0..0) after H^n, phase Uf, H^n; exact DJ promise test."""
    basis_zero = (1 + 0j,) + (0j,) * ((1 << circuit.n) - 1)
    result = hadamard_all(phase_kickback(circuit, hadamard_all(basis_zero)))
    return abs(result[0]) ** 2


@dataclass(frozen=True)
class GroverResult:
    iterations: int
    solutions: int
    success_probability: float
    oracle_basis_evaluations: int
    synthesized_gate_applications: int
    statevector_amplitudes: int
    best_candidate: int | None
    best_candidate_validated: bool


def grover_simulate(circuit: Circuit, *, iterations: int | None = None) -> GroverResult:
    """Ideal Grover diffuser on a classical statevector.

    The M=number-of-solutions scan is a FULL 2^n classical preprocessing pass,
    not a free parameter. Every phase-oracle evaluation applies ANF gates to
    each basis state. Counting this work is essential to honest comparisons.
    """
    n_states = 1 << circuit.n
    m = sum(circuit.table)  # Already cost 2^n classical evaluations to build.
    if iterations is None:
        iterations = (max(0, round(pi / 4 * sqrt(n_states / m) - 0.5))
                      if 0 < m < n_states else 0)
    if type(iterations) is not int or not (0 <= iterations <= 32):
        raise ValueError("iteration cap 0..32")
    state = [complex(1 / sqrt(n_states))] * n_states
    for _ in range(iterations):
        state = list(phase_kickback(circuit, tuple(state)))
        mean = sum(state) / n_states
        state = [2 * mean - z for z in state]
    probability = sum(abs(state[x]) ** 2 for x, value in enumerate(circuit.table) if value)
    # A sampled measurement can fail. Report the highest-probability outcome
    # only as a testable candidate, never a certified SAT witness on its own.
    best = max(range(n_states), key=lambda x: abs(state[x]) ** 2)
    validated = bool(circuit.table[best])
    return GroverResult(
        iterations=iterations, solutions=m,
        success_probability=min(1.0, max(0.0, probability)),
        oracle_basis_evaluations=n_states * (1 + iterations),
        synthesized_gate_applications=n_states * iterations * len(circuit.gates),
        statevector_amplitudes=n_states,
        best_candidate=best if validated else None,
        best_candidate_validated=validated,
    )
