#!/usr/bin/env python3
"""Mechanically translate a non-affine Policy-0T trace into Resolution.

This executable closes the two finite proof gaps identified after C020:

1. lift residual local Resolution lines back to clauses derived from root axioms;
2. eliminate propagated-unit literals by resolving backwards through their
   recorded reason clauses.

The translator consumes the independently replayed trace emitted by
`janus_tear_policy0t_trace_certificate.py`.  It is still a finite positive
control.  The general size/depth theorem for every non-affine Policy-0T run
remains a mathematical induction to formalize and attack.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from janus_tear_policy0t_trace_certificate import (
    CNF,
    Clause,
    N_VARS,
    TracePolicy,
    UNSAT_FORMULA,
    canonical_clause,
    canonical_cnf,
    simplify_one,
    verify_trace,
    visible_affine_root_decision,
)


@dataclass(frozen=True)
class Axiom:
    clause: Clause


@dataclass(frozen=True)
class Resolution:
    clause: Clause
    left: int
    right: int
    pivot: int


ProofLine = Axiom | Resolution
Records = dict[Clause, int]
Assignment = dict[int, bool]
Reason = tuple[int, int]  # assigned literal, proof line deriving its reason clause


def restrict_clause(clause: Clause, assignment: Assignment) -> Clause | None:
    """Restrict a root-level proof clause; None denotes a satisfied clause."""

    residual: list[int] = []
    for literal in clause:
        variable = abs(literal)
        if variable not in assignment:
            residual.append(literal)
            continue
        value = assignment[variable]
        if (literal > 0 and value) or (literal < 0 and not value):
            return None
    return canonical_clause(residual)


def decision_boundary(assignment: Assignment) -> set[int]:
    """Return the literals falsified by the current assignment."""

    return {
        variable if not value else -variable
        for variable, value in assignment.items()
    }


def resolve_clauses(left: Clause, right: Clause, pivot: int) -> Clause:
    if pivot in left and -pivot in right:
        raw = (set(left) - {pivot}) | (set(right) - {-pivot})
    elif -pivot in left and pivot in right:
        raw = (set(left) - {-pivot}) | (set(right) - {pivot})
    else:
        raise AssertionError(f"pivot {pivot} is not complementary")
    clause = canonical_clause(raw)
    assert clause is not None, "translator generated a tautological resolvent"
    return clause


class ResolutionProof:
    def __init__(self, root: CNF):
        self.lines: list[ProofLine] = []
        self.axiom_line: dict[Clause, int] = {}
        for clause in canonical_cnf(root):
            line = len(self.lines)
            self.lines.append(Axiom(clause))
            self.axiom_line[clause] = line

    def clause(self, line: int) -> Clause:
        return self.lines[line].clause

    def add_resolution(self, left: int, right: int, pivot: int) -> int:
        clause = resolve_clauses(self.clause(left), self.clause(right), pivot)
        line = len(self.lines)
        self.lines.append(Resolution(clause, left, right, pivot))
        return line

    def verify(self, root: CNF) -> tuple[int, int, int, int]:
        axioms = set(canonical_cnf(root))
        depths: list[int] = []
        axiom_lines = 0
        resolution_lines = 0

        for index, line in enumerate(self.lines):
            if isinstance(line, Axiom):
                assert line.clause in axioms
                depth = 0
                axiom_lines += 1
            else:
                assert 0 <= line.left < index
                assert 0 <= line.right < index
                assert line.left != line.right
                derived = resolve_clauses(
                    self.clause(line.left), self.clause(line.right), line.pivot
                )
                assert derived == line.clause
                depth = 1 + max(depths[line.left], depths[line.right])
                resolution_lines += 1
            depths.append(depth)

        maximum_width = max(len(line.clause) for line in self.lines)
        proof_depth = depths[-1]
        return axiom_lines, resolution_lines, maximum_width, proof_depth


class TraceTranslator:
    def __init__(self, root: CNF, nodes: dict[int, dict[str, object]]):
        self.root = canonical_cnf(root)
        self.nodes = nodes
        self.proof = ResolutionProof(self.root)
        self.translated_nodes = 0
        self.unit_reason_resolutions = 0
        self.branch_resolutions = 0

    def initial_records(self) -> Records:
        return dict(self.proof.axiom_line)

    def restrict_records(
        self, records: Records, assignment: Assignment
    ) -> tuple[Records, list[int]]:
        restricted: Records = {}
        conflicts: list[int] = []
        for line in sorted(set(records.values())):
            residual = restrict_clause(self.proof.clause(line), assignment)
            if residual is None:
                continue
            if residual == ():
                conflicts.append(line)
            restricted.setdefault(residual, line)
        return restricted, conflicts

    def check_boundary(self, line: int, assignment: Assignment) -> None:
        clause = self.proof.clause(line)
        assert set(clause) <= decision_boundary(assignment)
        assert restrict_clause(clause, assignment) == ()

    def eliminate_reasons(
        self, conflict_line: int, reasons: list[Reason], entry: Assignment
    ) -> int:
        line = conflict_line
        for literal, reason_line in reversed(reasons):
            falsified_literal = -literal
            if falsified_literal not in self.proof.clause(line):
                continue
            assert literal in self.proof.clause(reason_line)
            line = self.proof.add_resolution(
                line, reason_line, abs(literal)
            )
            self.unit_reason_resolutions += 1
        self.check_boundary(line, entry)
        return line

    def unit_phase(
        self,
        records: Records,
        assignment: Assignment,
        expected_events: object,
    ) -> tuple[Records, Assignment, list[Reason], int | None]:
        assert isinstance(expected_events, list)
        emitted_events: list[dict[str, object]] = []
        reasons: list[Reason] = []
        batch = 0

        while True:
            cnf = canonical_cnf(records)
            units = [clause[0] for clause in cnf if len(clause) == 1]
            if not units:
                assert emitted_events == expected_events
                return records, assignment, reasons, None

            assignments: dict[int, bool] = {}
            reason_literals: dict[int, int] = {}
            reason_lines: dict[int, int] = {}
            for literal in units:
                variable = abs(literal)
                value = literal > 0
                if variable in assignments and assignments[variable] != value:
                    emitted_events.append(
                        {
                            "batch": batch,
                            "kind": "opposite_units",
                            "units": tuple(sorted(units)),
                        }
                    )
                    positive = records[(variable,)]
                    negative = records[(-variable,)]
                    conflict = self.proof.add_resolution(
                        positive, negative, variable
                    )
                    assert emitted_events == expected_events
                    return records, assignment, reasons, conflict
                assignments[variable] = value
                reason_literals[variable] = literal
                reason_lines[variable] = records[(literal,)]

            batch_cnf = cnf
            for variable, value in sorted(assignments.items()):
                literal = variable if value else -variable
                before = cnf
                expected_after = simplify_one(cnf, variable, value)
                emitted_events.append(
                    {
                        "batch": batch,
                        "kind": "unit",
                        "literal": literal,
                        "reason": (reason_literals[variable],),
                        "batch_cnf": batch_cnf,
                        "before": before,
                        "after": expected_after,
                    }
                )

                assignment = dict(assignment)
                assignment[variable] = value
                reasons.append((literal, reason_lines[variable]))
                records, conflicts = self.restrict_records(records, assignment)
                actual_after = None if conflicts else canonical_cnf(records)
                assert actual_after == expected_after

                if conflicts:
                    assert emitted_events == expected_events
                    return records, assignment, reasons, conflicts[0]
                if not records:
                    assert emitted_events == expected_events
                    return records, assignment, reasons, None
                cnf = canonical_cnf(records)
            batch += 1

    def add_local_resolution_events(
        self,
        records: Records,
        assignment: Assignment,
        events: object,
    ) -> tuple[Records, int | None]:
        assert isinstance(events, list)
        initial = dict(records)
        conflict: int | None = None

        for event in events:
            assert isinstance(event, dict)
            left = event["left"]
            right = event["right"]
            pivot = int(event["pivot"])
            residual = event["resolvent"]
            assert isinstance(left, tuple)
            assert isinstance(right, tuple)
            assert isinstance(residual, tuple)
            assert left in initial and right in initial

            line = self.proof.add_resolution(
                initial[left], initial[right], pivot
            )
            assert restrict_clause(self.proof.clause(line), assignment) == residual
            records.setdefault(residual, line)
            if residual == ():
                conflict = line
                break
        return records, conflict

    def combine_children(
        self,
        variable: int,
        false_line: int,
        true_line: int,
        parent_assignment: Assignment,
    ) -> int:
        false_clause = self.proof.clause(false_line)
        true_clause = self.proof.clause(true_line)

        if variable not in false_clause:
            line = false_line
        elif -variable not in true_clause:
            line = true_line
        else:
            line = self.proof.add_resolution(
                false_line, true_line, variable
            )
            self.branch_resolutions += 1

        self.check_boundary(line, parent_assignment)
        return line

    def translate_node(
        self,
        node_id: int,
        records: Records,
        assignment: Assignment,
    ) -> tuple[bool, int | None]:
        self.translated_nodes += 1
        node = self.nodes[node_id]
        assert canonical_cnf(records) == node["input"]
        entry = dict(assignment)

        records, assignment, pre_reasons, conflict = self.unit_phase(
            records, assignment, node["pre_units"]
        )
        if conflict is not None:
            return False, self.eliminate_reasons(conflict, pre_reasons, entry)
        if not records:
            return True, None
        assert canonical_cnf(records) == node["pre_result"]

        records, conflict = self.add_local_resolution_events(
            records, assignment, node["resolution_events"]
        )
        assert canonical_cnf(records) == node["resolution_output"]
        if conflict is not None:
            return False, self.eliminate_reasons(conflict, pre_reasons, entry)

        records, assignment, post_reasons, conflict = self.unit_phase(
            records, assignment, node["post_units"]
        )
        all_reasons = pre_reasons + post_reasons
        if conflict is not None:
            return False, self.eliminate_reasons(conflict, all_reasons, entry)
        if not records:
            return True, None
        assert canonical_cnf(records) == node["post_result"]

        variable = int(node["branch_var"])
        children = node["children"]
        assert isinstance(children, list)
        child_conflicts: dict[bool, int] = {}

        for child_record in children:
            assert isinstance(child_record, dict)
            value = bool(child_record["value"])
            child_assignment = dict(assignment)
            child_assignment[variable] = value
            child_records, direct_conflicts = self.restrict_records(
                records, child_assignment
            )

            if direct_conflicts:
                assert child_record["direct_conflict"] is True
                answer = False
                child_line = direct_conflicts[0]
            else:
                assert child_record["direct_conflict"] is False
                child_id = child_record["child"]
                assert isinstance(child_id, int)
                answer, child_line = self.translate_node(
                    child_id, child_records, child_assignment
                )

            assert answer == child_record["result"]
            if answer:
                return True, None
            assert child_line is not None
            self.check_boundary(child_line, child_assignment)
            child_conflicts[value] = child_line

        assert False in child_conflicts and True in child_conflicts
        combined = self.combine_children(
            variable,
            child_conflicts[False],
            child_conflicts[True],
            assignment,
        )
        return False, self.eliminate_reasons(combined, all_reasons, entry)

    def translate(self, root_id: int) -> int:
        answer, line = self.translate_node(
            root_id, self.initial_records(), {}
        )
        assert answer is False
        assert line is not None
        assert self.proof.clause(line) == ()
        return line


def self_test() -> None:
    root = canonical_cnf(UNSAT_FORMULA)
    affine_answer, affine_equations = visible_affine_root_decision(root, N_VARS)
    assert affine_answer is None
    assert affine_equations == 0

    policy = TracePolicy()
    answer, root_id = policy.search(root)
    assert answer is False
    assert verify_trace(policy.nodes, root_id, root) is False

    translator = TraceTranslator(root, policy.nodes)
    final_line = translator.translate(root_id)
    axiom_lines, resolution_lines, maximum_width, proof_depth = (
        translator.proof.verify(root)
    )

    assert translator.translated_nodes == len(policy.nodes)
    assert translator.proof.clause(final_line) == ()
    assert proof_depth <= N_VARS

    print("JANUS_POLICY0T_RECURSIVE_TRACE_TRANSLATOR = PASS")
    print(f"trace_nodes = {len(policy.nodes)}")
    print(f"axiom_lines = {axiom_lines}")
    print(f"resolution_lines = {resolution_lines}")
    print(f"proof_lines = {len(translator.proof.lines)}")
    print(f"unit_reason_resolutions = {translator.unit_reason_resolutions}")
    print(f"branch_resolutions = {translator.branch_resolutions}")
    print(f"maximum_width = {maximum_width}")
    print(f"proof_depth = {proof_depth}")
    print("final_clause = EMPTY")
    print("scope = non-affine Policy-0T search core")
    print("claim_boundary = finite recursive translator; uniform asymptotic theorem remains open")


if __name__ == "__main__":
    self_test()
