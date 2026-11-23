#!/usr/bin/env python3
"""JANUS-DEUTSCH-002: direct reversible SAT / Exact-One clause oracle.

Research-only, no physical quantum processor. Circuit compilation never
enumerates 2**n assignments. A clean work register contains one violation flag
per CNF clause. Compute flags, flip the answer when every flag is 0, uncompute.

A mixed-polarity multi-controlled-X is a reversible *logical* operation.
Report transparent idealized decomposition costs; do not claim real device
fidelity, gate-depth advantage, or a polynomial-time SAT algorithm.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import asin, pi, sin, sqrt
from typing import Iterable, Mapping

from janus_ufr_001 import normalize, verify_renaming

Rows = tuple[tuple[int, ...], ...]
MAX_INPUT_VARIABLES = 64
MAX_CLAUSES = 8192
MAX_STATEVECTOR_INPUTS = 8


def _ccx(k: int) -> int:
    """Textbook clean-ancilla 2-control Toffoli decomposition upper estimate."""
    return 0 if k < 2 else 1 if k == 2 else 2 * k - 3


@dataclass(frozen=True)
class ClauseGate:
    true_mask: int    # Input bits that must be 1 for clause to be false
    false_mask: int   # Input bits that must be 0 for clause to be false
    clause: tuple[int, ...]

    def fires(self, x: int) -> bool:
        return (x & self.true_mask) == self.true_mask and not (x & self.false_mask)

    @property
    def controls(self) -> int:
        return (self.true_mask | self.false_mask).bit_count()


@dataclass(frozen=True)
class DirectOracle:
    n: int
    kind: str
    rows: Rows
    gates: tuple[ClauseGate, ...]
    encoded_clause_count: int
    encoded_literal_count: int
    encoding_generated_pairs: int

    @classmethod
    def compile(cls, rows: Iterable[Iterable[int]], n: int,
                kind: str = "SAT") -> "DirectOracle":
        if type(n) is not int or not 1 <= n <= MAX_INPUT_VARIABLES:
            raise ValueError("structural oracle supports 1..64 input variables")
        if kind not in ("SAT", "EXACT_ONE"):
            raise ValueError("kind must be SAT or EXACT_ONE")
        original = normalize(rows)
        if any(abs(lit) > n for row in original for lit in row):
            raise ValueError("literal exceeds input register")
        # Encode Exact-One as: at least one true literal, and each pair
        # cannot both be true. Works with repeated literals and complements.
        # Crucially, construction cost is O(sum row_width**2), not 2**n.
        clauses = []
        pairs = 0
        for row in original:
            clauses.append(row)
            if kind == "EXACT_ONE":
                for a, b in combinations(row, 2):
                    clauses.append((-a, -b))
                    pairs += 1
        if len(clauses) > MAX_CLAUSES:
            raise ValueError("CNF encoding clause cap exceeded")
        seen = set()
        gates = []
        for clause in clauses:
            positive = 0
            negative = 0
            for lit in clause:
                bit = 1 << (abs(lit) - 1)
                if lit > 0:
                    positive |= bit
                else:
                    negative |= bit
            if positive & negative:
                # Tautology: at least one literal always true, even with
                # repeated occurrences. Skipping is logically exact.
                continue
            signature = (negative, positive)
            if signature in seen:
                continue
            seen.add(signature)
            gates.append(ClauseGate(negative, positive, clause))
        return cls(n, kind, original, tuple(gates), len(clauses),
                   sum(len(row) for row in clauses), pairs)

    @property
    def work_qubits(self) -> int:
        return len(self.gates)

    @property
    def logical_mcx_gates(self) -> int:
        # m clause-violation flags + one final output toggle + uncompute m.
        return 2 * self.work_qubits + 1

    @property
    def total_qubits_without_decomposition(self) -> int:
        return self.n + 1 + self.work_qubits

    @property
    def scratch_qubits_upper_bound(self) -> int:
        # A textbook chain of Toffolis with clean intermediate bits for
        # a k-controlled X uses at most max(0,k-2) extra clean scratch bits.
        return max([0, self.work_qubits - 2] +
                   [max(0, gate.controls - 2) for gate in self.gates])

    @property
    def all_qubits_with_clean_decomposition(self) -> int:
        return self.total_qubits_without_decomposition + self.scratch_qubits_upper_bound

    @property
    def estimated_toffoli_count(self) -> int:
        return sum(2 * _ccx(g.controls) for g in self.gates) + _ccx(self.work_qubits)

    @property
    def estimated_control_polarity_x_count(self) -> int:
        # Two conjugating X for each negative control: compute+uncompute,
        # and all m work register controls are zero in the final gate.
        return 4 * sum(g.false_mask.bit_count() for g in self.gates) + 2 * self.work_qubits

    @property
    def encoded_max_width(self) -> int:
        return max((g.controls for g in self.gates), default=0)

    def violation_mask(self, x: int) -> int:
        """Computes m work flags; no full truth table is constructed."""
        if type(x) is not int or x < 0 or x >= 1 << self.n:
            raise ValueError("assignment outside input register")
        flags = 0
        for i, gate in enumerate(self.gates):
            if gate.fires(x):
                flags |= 1 << i
        return flags

    def apply_basis(self, x: int, target: int,
                    work: int = 0) -> tuple[int, int, int]:
        """True reversible extension for *all* work-register basis states.

        For clean work=0: (x,b,0) -> (x,b xor F(x),0).
        For arbitrary work=w:  (x,b,w) -> (x,b xor [w xor BAD(x)==0],w).
        Both directions are identical; the map is a permutation/involution.
        """
        if type(target) is not int or target not in (0, 1):
            raise ValueError("target must be a basis bit")
        if type(work) is not int or work < 0 or work >= (1 << self.work_qubits):
            raise ValueError("work register outside allocated range")
        bad = self.violation_mask(x)
        computed = work ^ bad
        toggled = target ^ int(computed == 0)
        return x, toggled, computed ^ bad

    def evaluate(self, x: int) -> bool:
        return self.violation_mask(x) == 0

    def phase(self, x: int) -> int:
        """Phase kickback from a clean |-> target; exact +/-1."""
        return -1 if self.apply_basis(x, 0, 0)[1] else 1

    def resources(self) -> dict:
        # Do not represent a 1000-control X as a single cheap hardware gate.
        return {
            "input_qubits": self.n,
            "original_constraint_rows": len(self.rows),
            "encoded_clauses_before_tautology_and_dedup": self.encoded_clause_count,
            "encoded_total_literals_before_dedup": self.encoded_literal_count,
            "exact_one_added_pairwise_constraints": self.encoding_generated_pairs,
            "work_qubits": self.work_qubits,
            "logical_mcx_gates": self.logical_mcx_gates,
            "encoded_max_width": self.encoded_max_width,
            "max_controlled_x_controls": max(self.encoded_max_width, self.work_qubits),
            "textbook_clean_decomposition_extra_qubits_estimate":
                self.scratch_qubits_upper_bound,
            "qubit_count_with_clean_decomposition_estimate":
                self.all_qubits_with_clean_decomposition,
            "toffoli_count_clean_decomposition_estimate": self.estimated_toffoli_count,
            "negative_control_x_conjugation_estimate":
                self.estimated_control_polarity_x_count,
            "truth_table_required_for_compilation": False,
            "max_structural_compilation_clauses": MAX_CLAUSES,
        }


def check_ufr_covariance(left: DirectOracle, right: DirectOracle,
                         mapping: Mapping[int, int], *,
                         exhaustive_limit: int = 8,
                         sample_indices: Iterable[int] = ()) -> bool:
    """Independently verify structure and output agreement of assignments."""
    if left.n != right.n or left.kind != right.kind:
        return False
    if set(mapping) != set(range(1, left.n + 1)):
        return False
    if set(mapping.values()) != set(range(1, right.n + 1)):
        return False
    if not verify_renaming(left.rows, right.rows, mapping, left.kind):
        return False

    def renamed_index(x: int) -> int:
        out = 0
        for old, new in mapping.items():
            if x & (1 << (old - 1)):
                out |= 1 << (new - 1)
        return out

    indices = (range(1 << left.n) if left.n <= exhaustive_limit
               else sample_indices)
    return all(left.evaluate(x) == right.evaluate(renamed_index(x))
               for x in indices)


def phase_statevector(oracle: DirectOracle,
                      input_state: tuple[complex, ...]) -> tuple[complex, ...]:
    """Small classical statevector control; O(2^n) is NOT compilation cost."""
    if oracle.n > MAX_STATEVECTOR_INPUTS:
        raise ValueError("statevector simulation capped at 8 input variables")
    if len(input_state) != 1 << oracle.n:
        raise ValueError("wrong statevector length")
    return tuple(amplitude * oracle.phase(x)
                 for x, amplitude in enumerate(input_state))


def deutsch_jozsa_probability(oracle: DirectOracle) -> float:
    from janus_deutsch_001 import hadamard_all
    if oracle.n > MAX_STATEVECTOR_INPUTS:
        raise ValueError("statevector cap")
    initial = (1+0j,) + (0j,) * ((1 << oracle.n) - 1)
    result = hadamard_all(phase_statevector(oracle, hadamard_all(initial)))
    return abs(result[0]) ** 2


@dataclass(frozen=True)
class DirectGrover:
    solutions: int
    iterations: int
    success_probability: float
    basis_predicate_evaluations: int
    gate_condition_evaluations: int
    candidate: int | None
    candidate_verified: bool


def grover_statevector(oracle: DirectOracle, iterations: int | None = None) -> DirectGrover:
    """Full classical truth scan used to choose t; no free M oracle allowed."""
    nstates = 1 << oracle.n if oracle.n <= MAX_STATEVECTOR_INPUTS else 0
    if not nstates:
        raise ValueError("Grover statevector cap n<=8")
    m = sum(oracle.evaluate(x) for x in range(nstates))
    if iterations is None:
        iterations = max(0, round(pi / 4 * sqrt(nstates / m) - 0.5)) if 0 < m < nstates else 0
    if type(iterations) is not int or not 0 <= iterations <= 32:
        raise ValueError("iteration cap 0..32")
    state = [complex(1 / sqrt(nstates))] * nstates
    for _ in range(iterations):
        state = list(phase_statevector(oracle, tuple(state)))
        mean = sum(state) / nstates
        state = [2 * mean - amp for amp in state]
    probability = sum(abs(state[x]) ** 2 for x in range(nstates)
                      if oracle.evaluate(x))
    best = max(range(nstates), key=lambda x: abs(state[x]) ** 2)
    verified = oracle.evaluate(best)
    return DirectGrover(
        solutions=m, iterations=iterations,
        success_probability=min(1.0, max(0.0, probability)),
        basis_predicate_evaluations=nstates * (2 + iterations) + 1,
        gate_condition_evaluations=(nstates * (2 + iterations) + 1) * oracle.work_qubits,
        candidate=best if verified else None,
        candidate_verified=verified,
    )
