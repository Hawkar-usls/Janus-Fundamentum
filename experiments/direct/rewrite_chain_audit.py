#!/usr/bin/env python3
"""Finite exact auditor for R7-shaped circuit rewrite chains.

The tool verifies tiny explicit circuit chains by truth tables and a declared
edit budget of at most seven replacement gates per step.  It is deliberately
not presented as an implementation of every clause of Krajicek's relation.
Its role is to freeze endpoint equivalence, edit accounting, and potential
Lipschitz checks for candidate H110/H111 artifacts.
"""

from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Gate:
    op: str
    inputs: tuple[int, ...] = ()
    variable: int | None = None


@dataclass(frozen=True)
class Circuit:
    variable_count: int
    gates: tuple[Gate, ...]
    output: int


def evaluate(circuit: Circuit, assignment: tuple[bool, ...]) -> bool:
    values: list[bool] = []
    for index, gate in enumerate(circuit.gates):
        if gate.op == "VAR":
            if gate.variable is None or not 0 <= gate.variable < circuit.variable_count:
                raise ValueError(f"gate {index}: invalid variable")
            value = assignment[gate.variable]
        elif gate.op == "NOT":
            if len(gate.inputs) != 1:
                raise ValueError(f"gate {index}: NOT arity")
            value = not values[gate.inputs[0]]
        elif gate.op in {"AND", "OR"}:
            if len(gate.inputs) != 2:
                raise ValueError(f"gate {index}: binary arity")
            left, right = (values[parent] for parent in gate.inputs)
            value = left and right if gate.op == "AND" else left or right
        else:
            raise ValueError(f"gate {index}: unsupported op {gate.op}")
        if any(parent >= index or parent < 0 for parent in gate.inputs):
            raise ValueError(f"gate {index}: non-topological input")
        values.append(value)
    if not 0 <= circuit.output < len(values):
        raise ValueError("invalid output gate")
    return values[circuit.output]


def truth_table(circuit: Circuit) -> tuple[bool, ...]:
    return tuple(
        evaluate(circuit, assignment)
        for assignment in itertools.product((False, True), repeat=circuit.variable_count)
    )


def gate_fingerprint(gate: Gate) -> tuple:
    return (gate.op, gate.inputs, gate.variable)


def multiset_edit_additions(source: Circuit, target: Circuit) -> int:
    """Count target gates not cancellable against identical source gates."""
    remaining = [gate_fingerprint(gate) for gate in source.gates]
    additions = 0
    for gate in target.gates:
        fingerprint = gate_fingerprint(gate)
        try:
            remaining.remove(fingerprint)
        except ValueError:
            additions += 1
    return additions


def verify_step(
    source: Circuit,
    target: Circuit,
    potential: Callable[[Circuit], int],
    maximum_added_gates: int = 7,
    maximum_potential_change: int | None = None,
) -> None:
    if source.variable_count != target.variable_count:
        raise ValueError("variable count changed")
    if truth_table(source) != truth_table(target):
        raise ValueError("rewrite endpoints are not equivalent")
    additions = multiset_edit_additions(source, target)
    if additions > maximum_added_gates:
        raise ValueError(f"rewrite adds {additions} gates; budget is {maximum_added_gates}")
    if maximum_potential_change is not None:
        delta = abs(potential(target) - potential(source))
        if delta > maximum_potential_change:
            raise ValueError(
                f"potential changes by {delta}; bound is {maximum_potential_change}"
            )


def verify_chain(
    chain: tuple[Circuit, ...],
    potential: Callable[[Circuit], int],
    maximum_potential_change: int,
) -> None:
    if len(chain) < 2:
        raise ValueError("chain must contain at least two circuits")
    for source, target in zip(chain, chain[1:], strict=False):
        verify_step(
            source,
            target,
            potential,
            maximum_added_gates=7,
            maximum_potential_change=maximum_potential_change,
        )


def size_potential(circuit: Circuit) -> int:
    return len(circuit.gates)


def self_test() -> None:
    # x0 AND x1
    direct = Circuit(
        2,
        (
            Gate("VAR", variable=0),
            Gate("VAR", variable=1),
            Gate("AND", (0, 1)),
        ),
        2,
    )
    # NOT(NOT(x0 AND x1))
    double_negation = Circuit(
        2,
        (
            Gate("VAR", variable=0),
            Gate("VAR", variable=1),
            Gate("AND", (0, 1)),
            Gate("NOT", (2,)),
            Gate("NOT", (3,)),
        ),
        4,
    )
    verify_chain((direct, double_negation), size_potential, 2)

    nonequivalent = Circuit(
        2,
        (
            Gate("VAR", variable=0),
            Gate("VAR", variable=1),
            Gate("OR", (0, 1)),
        ),
        2,
    )
    try:
        verify_step(direct, nonequivalent, size_potential)
    except ValueError as exc:
        assert "not equivalent" in str(exc)
    else:
        raise AssertionError("accepted a non-equivalent rewrite")

    oversized = Circuit(
        2,
        direct.gates + tuple(Gate("NOT", (2 + index,)) for index in range(8)),
        10,
    )
    try:
        verify_step(direct, oversized, size_potential)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted an over-budget rewrite")

    print("JANUS_REWRITE_CHAIN_AUDIT = PASS")
    print("SEMANTICS = EXACT_TRUTH_TABLE_FOR_TINY_FIXTURES")
    print("ADDED_GATE_BUDGET = 7")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    parser.error("only --self-test is supported")


if __name__ == "__main__":
    raise SystemExit(main())
