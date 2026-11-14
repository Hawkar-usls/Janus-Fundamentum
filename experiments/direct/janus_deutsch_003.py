#!/usr/bin/env python3
"""JANUS-DEUTSCH-003: reversible block-pebbling space/control trade-off.

Research only. Reuses a B-bit clause-violation work register across S=ceil(m/B)
blocks, and stores S summary bits until the final controlled output gate.
After output, it reversibly uncomputes every summary bit. This is exact for
clean scratch/summary ancillas and a permutation of ALL basis states.

Trade-off: fewer clean qubits and lower maximum control count, but ~2x more
clause checks and Toffoli decomposition gates. Neither a quantum speedup
nor an asymptotically faster SAT algorithm is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Iterable, Iterator, Mapping

from janus_deutsch_002 import (
    DirectOracle, MAX_STATEVECTOR_INPUTS, _ccx,
)
from janus_ufr_001 import verify_renaming


@dataclass(frozen=True)
class GateStep:
    kind: str  # "clause", "summary", "target"
    index: int = 0
    clause_index: int = 0
    active_bits: int = 0


@dataclass(frozen=True)
class BlockOracle:
    original: DirectOracle
    block_size: int

    @classmethod
    def compile(cls, rows: Iterable[Iterable[int]], n: int,
                kind: str = "SAT", *, block_size: int = 32) -> "BlockOracle":
        if type(block_size) is not int or not 1 <= block_size <= 8192:
            raise ValueError("block size must be integer 1..8192")
        return cls(DirectOracle.compile(rows, n, kind), block_size)

    @classmethod
    def from_direct(cls, original: DirectOracle, *,
                    block_size: int = 32) -> "BlockOracle":
        if type(block_size) is not int or not 1 <= block_size <= 8192:
            raise ValueError("invalid block size")
        return cls(original, block_size)

    @property
    def clauses(self) -> int:
        return self.original.work_qubits

    @property
    def blocks(self) -> int:
        return ceil(self.clauses / self.block_size)

    @property
    def scratch_bits(self) -> int:
        return min(self.block_size, self.clauses)

    @property
    def block_widths(self) -> tuple[int, ...]:
        return tuple(min(self.block_size, self.clauses - i * self.block_size)
                     for i in range(self.blocks))

    @property
    def total_clean_ancillas(self) -> int:
        return self.scratch_bits + self.blocks

    @property
    def maximum_controls(self) -> int:
        return max((self.original.encoded_max_width, self.scratch_bits,
                    self.blocks))

    @property
    def decomposition_scratch_bits(self) -> int:
        return max(0, self.maximum_controls - 2)

    @property
    def qubit_estimate(self) -> int:
        return (self.original.n + 1 + self.total_clean_ancillas
                + self.decomposition_scratch_bits)

    @property
    def logical_mcx_gates(self) -> int:
        # Every block is computed TWICE, around the central target:
        # 2*2*m clause toggles + 2*S summary toggles + output.
        return 4 * self.clauses + 2 * self.blocks + 1

    @property
    def estimated_toffolis(self) -> int:
        clause_cost = 4 * sum(_ccx(g.controls) for g in self.original.gates)
        summary_cost = 2 * sum(_ccx(width) for width in self.block_widths)
        return clause_cost + summary_cost + _ccx(self.blocks)

    @property
    def estimated_polarity_x_gates(self) -> int:
        # Four uses per clause (eight X per negative-control literal);
        # two uses per summary (four X per work flag); final positive control.
        return 8 * sum(g.false_mask.bit_count() for g in self.original.gates) + 4 * self.clauses

    def iter_instructions(self) -> Iterator[GateStep]:
        def run_block(index: int):
            start = index * self.block_size
            width = self.block_widths[index]
            for local in range(width):
                yield GateStep("clause", local, start + local)
            yield GateStep("summary", index, active_bits=width)
            for local in range(width - 1, -1, -1):
                yield GateStep("clause", local, start + local)
        for index in range(self.blocks):
            yield from run_block(index)
        yield GateStep("target")
        for index in range(self.blocks - 1, -1, -1):
            yield from run_block(index)

    def apply_basis(self, x: int, target: int, scratch: int = 0,
                    summaries: int = 0) -> tuple[int, int, int, int]:
        """Execution on basis states; returns BOTH ancilla registers unchanged.

        The output is F(x) iff scratch=summaries=0 on entry; on dirty states
        it remains a reversible permutation but does not equal SAT predicate.
        """
        n = self.original.n
        if type(x) is not int or not 0 <= x < 1 << n:
            raise ValueError("input assignment out of range")
        if type(target) is not int or target not in (0, 1):
            raise ValueError("target out of range")
        if type(scratch) is not int or not 0 <= scratch < 1 << self.scratch_bits:
            raise ValueError("scratch register out of range")
        if type(summaries) is not int or not 0 <= summaries < 1 << self.blocks:
            raise ValueError("summaries register out of range")

        # Fast *classical basis* interpreter: contract compute/uncompute
        # pairs algebraically, without allocating GateStep objects or storing
        # per-clause outputs. This does NOT remove any gates from the actual
        # coherent reversible schedule described by iter_instructions().
        # The independent slow gate-by-gate test checks the maps coincide.
        summary_bank = summaries
        gates = self.original.gates
        size = self.block_size
        widths = self.block_widths

        def toggle_summary(block_index: int, current_summaries: int) -> int:
            start = block_index * size
            temporary = scratch
            for local, gate in enumerate(gates[start:start + widths[block_index]]):
                if gate.fires(x):
                    temporary ^= 1 << local
            if temporary & ((1 << widths[block_index]) - 1) == 0:
                current_summaries ^= 1 << block_index
            return current_summaries

        for block_index in range(self.blocks):
            summary_bank = toggle_summary(block_index, summary_bank)
        out = target ^ int(summary_bank == (1 << self.blocks) - 1)
        for block_index in range(self.blocks - 1, -1, -1):
            summary_bank = toggle_summary(block_index, summary_bank)
        assert summary_bank == summaries
        return x, out, scratch, summary_bank

    def evaluate(self, x: int) -> bool:
        return bool(self.apply_basis(x, 0)[1])

    def phase(self, x: int) -> int:
        return -1 if self.apply_basis(x, 0)[1] else 1

    def resources(self) -> dict:
        old = self.original.resources()
        return {
            "n": self.original.n,
            "input_cnf_clauses": len(self.original.rows),
            "deduplicated_non_tautological_clauses": self.clauses,
            "block_size": self.block_size,
            "block_count": self.blocks,
            "clause_scratch_qubits": self.scratch_bits,
            "summary_qubits": self.blocks,
            "live_clean_ancillas": self.total_clean_ancillas,
            "max_controlled_x_controls": self.maximum_controls,
            "logical_mcx_gates": self.logical_mcx_gates,
            "toffoli_count_clean_decomposition_estimate": self.estimated_toffolis,
            "negative_control_x_conjugation_estimate": self.estimated_polarity_x_gates,
            "clean_chain_extra_scratch_estimate": self.decomposition_scratch_bits,
            "qubit_count_with_clean_decomposition_estimate": self.qubit_estimate,
            "previous_deutsch_002": old,
            "truth_table_required_for_compilation": False,
            "no_hardware_execution_or_fault_tolerance_model": True,
        }


def candidate_sizes(m: int, *, max_size: int | None = None) -> tuple[int, ...]:
    if type(m) is not int or m < 0:
        raise ValueError("m must be nonnegative integer")
    if m == 0:
        return (1,)
    stop = min(m, max_size or m)
    return tuple(range(1, stop + 1))


def choose_block_size(direct: DirectOracle, *, max_controls: int | None = None,
                      max_size: int | None = None) -> BlockOracle:
    """Exact finite deterministic resource trade-off; no data-driven SAT fit.

    Prefer minimal *estimated physical qubits*, then minimal max controls,
    then fewest estimated Toffolis. Any max_controls is a strict ceiling.
    """
    if max_controls is not None and (type(max_controls) is not int or max_controls < 0):
        raise ValueError("max_controls must be a nonnegative integer")
    if max_size is not None and (type(max_size) is not int or max_size <= 0):
        raise ValueError("max_size must be a positive integer")
    # Precompute the input's largest clause width ONCE. Candidate design
    # requires only integer arithmetic, not O(m) rescans of every clause for
    # every block size.
    m = direct.work_qubits
    widest_clause = direct.encoded_max_width
    choices = []
    for b in candidate_sizes(m, max_size=max_size):
        scratch = min(b, m)
        summaries = (m + b - 1) // b
        maxctrl = max(widest_clause, scratch, summaries)
        if max_controls is not None and maxctrl > max_controls:
            continue
        qubits = direct.n + 1 + scratch + summaries + max(0, maxctrl - 2)
        choices.append((qubits, maxctrl, b))
    if not choices:
        raise ValueError("no valid block size under control ceiling")
    best_qubits, best_ctrl = min((q, ctrl) for q, ctrl, b in choices)
    tied = [BlockOracle.from_direct(direct, block_size=b)
            for q, ctrl, b in choices if (q, ctrl) == (best_qubits, best_ctrl)]
    return min(tied, key=lambda c: (c.estimated_toffolis, c.block_size))


def verify_ufr_covariance(left: BlockOracle, right: BlockOracle,
                          mapping: Mapping[int, int], *,
                          sampled_assignments: Iterable[int] = ()) -> bool:
    """Complete structural bijection check; basis checks on a specified sample.

    Structural isomorphism guarantees all assignments in principle, with
    independently verified mapping and explicit empirical sampled checks.
    """
    n = left.original.n
    if n != right.original.n or left.original.kind != right.original.kind:
        return False
    if set(mapping) != set(range(1, n + 1)) or set(mapping.values()) != set(range(1, n + 1)):
        return False
    if not verify_renaming(left.original.rows, right.original.rows, mapping,
                           left.original.kind):
        return False
    for x in (range(1 << n) if n <= MAX_STATEVECTOR_INPUTS else sampled_assignments):
        renamed = 0
        for source, target in mapping.items():
            if x & (1 << (source - 1)):
                renamed |= 1 << (target - 1)
        if left.evaluate(x) != right.evaluate(renamed):
            return False
    return True
