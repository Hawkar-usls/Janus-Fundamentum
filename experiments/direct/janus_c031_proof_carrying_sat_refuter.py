#!/usr/bin/env python3
"""C031 proof-carrying SAT refuter bridge.

This artifact verifies the certificate plumbing needed by the constructive
circuit-lower-bound route.  It does not construct a universal SAT refuter.

A valid refuter output contains:

* a CNF formula F;
* its true SAT label b;
* either a full satisfying assignment (b=1) or a RUP refutation (b=0);
* a candidate circuit C such that C(encode(F)) != b.

The mathematical bridge recorded by C031 is immediate but important:
if a polynomial-time algorithm produces such an output against every circuit
of size s(n), then no size-s(n) circuit decides SAT on n-bit encodings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple, Union

Literal = int
Clause = Tuple[Literal, ...]
CNF = Tuple[Clause, ...]
Assignment = Dict[int, bool]
RupProof = Sequence[Clause]
Certificate = Union[Assignment, RupProof]


@dataclass(frozen=True)
class Formula:
    nvars: int
    clauses: CNF

    def encode(self) -> bytes:
        payload = {
            "nvars": self.nvars,
            "clauses": [list(clause) for clause in self.clauses],
        }
        return json.dumps(
            payload, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")


def eval_literal(literal: Literal, assignment: Assignment) -> bool:
    value = assignment[abs(literal)]
    return value if literal > 0 else not value


def verify_sat_assignment(formula: Formula, assignment: Assignment) -> bool:
    if set(assignment) != set(range(1, formula.nvars + 1)):
        return False
    return all(
        any(eval_literal(literal, assignment) for literal in clause)
        for clause in formula.clauses
    )


def unit_conflict(
    clauses: Sequence[Clause], assumptions: Sequence[Literal] = ()
) -> bool:
    """Return True iff unit propagation derives a contradiction."""

    assignment: Assignment = {}
    database = [tuple(clause) for clause in clauses]
    database.extend((literal,) for literal in assumptions)

    changed = True
    while changed:
        changed = False
        for clause in database:
            satisfied = False
            unassigned: List[Literal] = []
            for literal in clause:
                variable = abs(literal)
                if variable in assignment:
                    value = assignment[variable]
                    if (literal > 0 and value) or (literal < 0 and not value):
                        satisfied = True
                        break
                else:
                    unassigned.append(literal)

            if satisfied:
                continue
            if not unassigned:
                return True
            if len(unassigned) == 1:
                literal = unassigned[0]
                variable = abs(literal)
                value = literal > 0
                if variable in assignment and assignment[variable] != value:
                    return True
                if variable not in assignment:
                    assignment[variable] = value
                    changed = True

    return False


def verify_rup(formula: Formula, proof: RupProof) -> bool:
    """Verify a sequence of RUP additions ending in the empty clause."""

    database: List[Clause] = list(formula.clauses)
    for clause in proof:
        assumptions = tuple(-literal for literal in clause)
        if not unit_conflict(database, assumptions):
            return False
        database.append(tuple(clause))
    return bool(proof) and tuple(proof[-1]) == tuple()


class Circuit:
    def evaluate(self, encoded_formula: bytes) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class ConstantCircuit(Circuit):
    value: bool

    def evaluate(self, encoded_formula: bytes) -> bool:
        del encoded_formula
        return self.value


@dataclass(frozen=True)
class FirstByteParityCircuit(Circuit):
    def evaluate(self, encoded_formula: bytes) -> bool:
        return bool(sum(encoded_formula) & 1)


def verify_proof_carrying_error(
    circuit: Circuit,
    formula: Formula,
    true_label: bool,
    certificate: Certificate,
) -> bool:
    """Independently verify the semantic label and the circuit error."""

    if true_label:
        if not isinstance(certificate, dict):
            return False
        if not verify_sat_assignment(formula, certificate):
            return False
    else:
        if isinstance(certificate, dict):
            return False
        if not verify_rup(formula, certificate):
            return False

    return circuit.evaluate(formula.encode()) != true_label


def certified_xor_embedding(seed: Tuple[int, int]) -> Tuple[Formula, bool, Certificate]:
    """A plumbing-only certificate-preserving embedding of XOR_2 into SAT.

    This deliberately simple map is not hardness preserving: its only purpose
    is to test the transfer interface and both certificate polarities.
    """

    label = bool(seed[0] ^ seed[1])
    if label:
        return Formula(1, ((1,),)), True, {1: True}
    return Formula(1, ((1,), (-1,))), False, [tuple()]


def refute_constant_on_xor(circuit: ConstantCircuit) -> Tuple[int, int]:
    for seed in ((0, 0), (0, 1), (1, 0), (1, 1)):
        label = bool(seed[0] ^ seed[1])
        if circuit.value != label:
            return seed
    raise AssertionError("a constant circuit cannot compute XOR_2")


def run_self_test() -> dict:
    sat_formula = Formula(1, ((1,),))
    unsat_formula = Formula(1, ((1,), (-1,)))

    checks = {
        "sat_assignment_accepts": verify_sat_assignment(sat_formula, {1: True}),
        "bad_assignment_rejects": not verify_sat_assignment(sat_formula, {1: False}),
        "rup_unsat_accepts": verify_rup(unsat_formula, [tuple()]),
        "bad_rup_rejects": not verify_rup(sat_formula, [tuple()]),
        "false_negative_certified": verify_proof_carrying_error(
            ConstantCircuit(False), sat_formula, True, {1: True}
        ),
        "false_positive_certified": verify_proof_carrying_error(
            ConstantCircuit(True), unsat_formula, False, [tuple()]
        ),
        "correct_sat_answer_not_error": not verify_proof_carrying_error(
            ConstantCircuit(True), sat_formula, True, {1: True}
        ),
        "correct_unsat_answer_not_error": not verify_proof_carrying_error(
            ConstantCircuit(False), unsat_formula, False, [tuple()]
        ),
    }

    transfer_checks = []
    for value in (False, True):
        source_circuit = ConstantCircuit(value)
        seed = refute_constant_on_xor(source_circuit)
        formula, label, certificate = certified_xor_embedding(seed)
        # The composed SAT circuit is constant as well.
        transferred = verify_proof_carrying_error(
            ConstantCircuit(value), formula, label, certificate
        )
        transfer_checks.append(
            {
                "source_constant": value,
                "seed": list(seed),
                "label": label,
                "transferred_error_verified": transferred,
            }
        )

    checks["embedding_transfer_plumbing"] = all(
        row["transferred_error_verified"] for row in transfer_checks
    )
    if not all(checks.values()):
        raise AssertionError(checks)

    result = {
        "artifact_id": "C031-PROOF-CARRYING-SAT-REFUTER",
        "status": "PASS",
        "checks": checks,
        "transfer_checks": transfer_checks,
        "theorem_boundary": (
            "The verifier proves certificate correctness for proposed errors. "
            "It does not produce errors against arbitrary small SAT circuits."
        ),
        "p_vs_np": "OPEN",
    }
    canonical = json.dumps(
        result, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    result["integrity_sha256"] = hashlib.sha256(canonical).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_self_test()
    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    print(json.dumps(result, indent=2, sort_keys=True))

    if args.self_test:
        assert result["status"] == "PASS"


if __name__ == "__main__":
    main()
