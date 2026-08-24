#!/usr/bin/env python3
"""C025-B standalone verifier for context-independent proof-carrying reasons.

Reason language v0:
  - canonical root CNF;
  - AXIOM nodes pointing to root clauses;
  - exact RESOLVE nodes;
  - a final globally derived clause C;
  - reuse is allowed only when the current partial assignment falsifies C.

This probe verifies reason soundness mechanics only.  It does not prove that
reason discovery, total proof size, cache lookup, or SAT search is polynomial in
the original input length.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable, Mapping

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Assignment = Mapping[int, bool]


def canonical_clause(clause: Iterable[int]) -> Clause | None:
    literals = set(int(literal) for literal in clause)
    if 0 in literals:
        raise ValueError("literal 0 is not allowed")
    if any(-literal in literals for literal in literals):
        return None
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


def canonical_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    normalized: set[Clause] = set()
    for clause in clauses:
        candidate = canonical_clause(clause)
        if candidate is None:
            continue
        normalized.add(candidate)
    return tuple(sorted(normalized, key=lambda clause: (len(clause), clause)))


def formula_fingerprint(cnf: CNF) -> str:
    payload = json.dumps(
        [list(clause) for clause in canonical_cnf(cnf)],
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def resolve_clauses(left: Clause, right: Clause, pivot: int) -> Clause:
    if pivot <= 0:
        raise ValueError("pivot must be a positive variable id")

    if pivot in left and -pivot in right:
        left_drop, right_drop = pivot, -pivot
    elif -pivot in left and pivot in right:
        left_drop, right_drop = -pivot, pivot
    else:
        raise ValueError("parents do not contain complementary pivot literals")

    merged = (set(left) - {left_drop}) | (set(right) - {right_drop})
    candidate = canonical_clause(merged)
    if candidate is None:
        raise ValueError("tautological resolvent is not a reusable reason clause")
    return candidate


@dataclass(frozen=True)
class ProofNode:
    kind: str
    clause: Clause
    source_clause: int | None = None
    left: int | None = None
    right: int | None = None
    pivot: int | None = None


@dataclass(frozen=True)
class ReasonRef:
    final_node: int
    root_fingerprint: str


@dataclass(frozen=True)
class Propagation:
    literal: int
    antecedent_node: int


class ProofStore:
    def __init__(self, root_cnf: CNF):
        self.root_cnf = canonical_cnf(root_cnf)
        self.root_fingerprint = formula_fingerprint(self.root_cnf)
        self.nodes: list[ProofNode] = []

    def add_axiom(self, source_clause: int) -> int:
        if not 0 <= source_clause < len(self.root_cnf):
            raise IndexError("source clause index out of range")
        node = ProofNode(
            kind="AXIOM",
            clause=self.root_cnf[source_clause],
            source_clause=source_clause,
        )
        self.nodes.append(node)
        return len(self.nodes) - 1

    def add_resolve(self, left: int, right: int, pivot: int) -> int:
        if not (0 <= left < len(self.nodes) and 0 <= right < len(self.nodes)):
            raise IndexError("parent proof node out of range")
        clause = resolve_clauses(
            self.nodes[left].clause,
            self.nodes[right].clause,
            pivot,
        )
        self.nodes.append(
            ProofNode(
                kind="RESOLVE",
                clause=clause,
                left=left,
                right=right,
                pivot=pivot,
            )
        )
        return len(self.nodes) - 1

    def verify_all(self) -> bool:
        try:
            for index, node in enumerate(self.nodes):
                if node.kind == "AXIOM":
                    if node.source_clause is None:
                        return False
                    if node.left is not None or node.right is not None or node.pivot is not None:
                        return False
                    if not 0 <= node.source_clause < len(self.root_cnf):
                        return False
                    if node.clause != self.root_cnf[node.source_clause]:
                        return False
                    continue

                if node.kind != "RESOLVE":
                    return False
                if node.left is None or node.right is None or node.pivot is None:
                    return False
                if not (0 <= node.left < index and 0 <= node.right < index):
                    return False
                expected = resolve_clauses(
                    self.nodes[node.left].clause,
                    self.nodes[node.right].clause,
                    node.pivot,
                )
                if node.clause != expected:
                    return False
            return True
        except (ValueError, IndexError):
            return False

    def reason(self, final_node: int) -> ReasonRef:
        if not 0 <= final_node < len(self.nodes):
            raise IndexError("final node out of range")
        return ReasonRef(final_node, self.root_fingerprint)

    def axiom_for_clause(self, clause: Iterable[int]) -> int:
        candidate = canonical_clause(clause)
        if candidate is None:
            raise ValueError("tautological clause is not a root axiom target")
        try:
            source = self.root_cnf.index(candidate)
        except ValueError as exc:
            raise ValueError("clause is not present in canonical root CNF") from exc
        return self.add_axiom(source)


def literal_false(literal: int, assignment: Assignment) -> bool:
    variable = abs(literal)
    if variable not in assignment:
        return False
    value = bool(assignment[variable])
    literal_true = value if literal > 0 else not value
    return not literal_true


def assignment_falsifies(clause: Clause, assignment: Assignment) -> bool:
    return all(literal_false(literal, assignment) for literal in clause)


def verify_reason(store: ProofStore, reason: ReasonRef) -> bool:
    return (
        reason.root_fingerprint == store.root_fingerprint
        and 0 <= reason.final_node < len(store.nodes)
        and store.verify_all()
    )


def reason_applies(store: ProofStore, reason: ReasonRef, assignment: Assignment) -> bool:
    return verify_reason(store, reason) and assignment_falsifies(
        store.nodes[reason.final_node].clause,
        assignment,
    )


def combine_branch_reasons(
    store: ProofStore,
    parent_assignment: Mapping[int, bool],
    pivot: int,
    false_reason: ReasonRef,
    true_reason: ReasonRef,
) -> ReasonRef:
    if not verify_reason(store, false_reason) or not verify_reason(store, true_reason):
        raise ValueError("child reason verification failed")
    if pivot in parent_assignment:
        raise ValueError("pivot is already assigned in parent context")

    false_assignment = dict(parent_assignment)
    false_assignment[pivot] = False
    true_assignment = dict(parent_assignment)
    true_assignment[pivot] = True

    false_clause = store.nodes[false_reason.final_node].clause
    true_clause = store.nodes[true_reason.final_node].clause

    if not assignment_falsifies(false_clause, false_assignment):
        raise ValueError("false-child reason is not applicable")
    if not assignment_falsifies(true_clause, true_assignment):
        raise ValueError("true-child reason is not applicable")

    if assignment_falsifies(false_clause, parent_assignment):
        return false_reason
    if assignment_falsifies(true_clause, parent_assignment):
        return true_reason

    if pivot not in false_clause or -pivot not in true_clause:
        raise ValueError("branch-dependent reasons lack complementary pivot literals")

    parent_node = store.add_resolve(
        false_reason.final_node,
        true_reason.final_node,
        pivot,
    )
    parent_reason = store.reason(parent_node)
    if not assignment_falsifies(store.nodes[parent_node].clause, parent_assignment):
        raise AssertionError("derived parent reason is not falsified by parent assignment")
    return parent_reason


def lift_unit_conflict(
    store: ProofStore,
    decision_assignment: Mapping[int, bool],
    propagations: list[Propagation],
    conflict_reason: ReasonRef,
) -> ReasonRef:
    if not verify_reason(store, conflict_reason):
        raise ValueError("conflict reason verification failed")

    full_assignment = dict(decision_assignment)

    for step in propagations:
        if not 0 <= step.antecedent_node < len(store.nodes):
            raise ValueError("antecedent node out of range")
        clause = store.nodes[step.antecedent_node].clause
        literal = step.literal
        variable = abs(literal)
        if literal not in clause:
            raise ValueError("antecedent does not contain propagated literal")
        if variable in full_assignment:
            raise ValueError("propagated variable was already assigned")
        for other in clause:
            if other == literal:
                continue
            if not literal_false(other, full_assignment):
                raise ValueError("antecedent was not unit under trace prefix")
        full_assignment[variable] = literal > 0

    current_node = conflict_reason.final_node
    if not assignment_falsifies(store.nodes[current_node].clause, full_assignment):
        raise ValueError("conflict clause is not falsified by full assignment")

    for step in reversed(propagations):
        current_clause = store.nodes[current_node].clause
        if -step.literal not in current_clause:
            continue
        current_node = store.add_resolve(
            current_node,
            step.antecedent_node,
            abs(step.literal),
        )

    final_clause = store.nodes[current_node].clause
    if not assignment_falsifies(final_clause, decision_assignment):
        raise AssertionError("lifted reason still depends on propagated assignments")
    return store.reason(current_node)


def self_test() -> None:
    direct = ProofStore(canonical_cnf([(-1, 2), (-1, -2)]))
    d0 = direct.axiom_for_clause((-1, 2))
    d1 = direct.axiom_for_clause((-1, -2))
    d2 = direct.add_resolve(d0, d1, 2)
    direct_reason = direct.reason(d2)
    assert direct.nodes[d2].clause == (-1,)
    assert reason_applies(direct, direct_reason, {1: True})
    assert not reason_applies(direct, direct_reason, {1: False})
    assert reason_applies(direct, direct_reason, {1: True, 7: False, 9: True})

    branch = ProofStore(canonical_cnf([(1, 2), (-1, 3)]))
    b0 = branch.axiom_for_clause((1, 2))
    b1 = branch.axiom_for_clause((-1, 3))
    parent_reason = combine_branch_reasons(
        branch,
        parent_assignment={2: False, 3: False},
        pivot=1,
        false_reason=branch.reason(b0),
        true_reason=branch.reason(b1),
    )
    assert branch.nodes[parent_reason.final_node].clause == (2, 3)
    assert reason_applies(branch, parent_reason, {2: False, 3: False})

    unit = ProofStore(canonical_cnf([(1, 2), (-2, 3), (-3,)]))
    u_y = unit.axiom_for_clause((1, 2))
    u_z = unit.axiom_for_clause((-2, 3))
    u_conflict = unit.axiom_for_clause((-3,))
    lifted = lift_unit_conflict(
        unit,
        decision_assignment={1: False},
        propagations=[Propagation(2, u_y), Propagation(3, u_z)],
        conflict_reason=unit.reason(u_conflict),
    )
    assert unit.nodes[lifted.final_node].clause == (1,)
    assert reason_applies(unit, lifted, {1: False})

    wrong_root = ProofStore(canonical_cnf([(1,), (-1,)]))
    wrong_root.axiom_for_clause((1,))
    assert not verify_reason(wrong_root, direct_reason)

    malformed = ProofStore(canonical_cnf([(1, 2), (-1, 3)]))
    m0 = malformed.axiom_for_clause((1, 2))
    m1 = malformed.axiom_for_clause((-1, 3))
    malformed.nodes.append(
        ProofNode(
            kind="RESOLVE",
            clause=(2,),
            left=m0,
            right=m1,
            pivot=1,
        )
    )
    assert not malformed.verify_all()

    print("C025_B_STANDALONE_REASON_VERIFIER = PASS")
    print("C025_B_CONTEXT_REUSE = PASS")
    print("C025_B_BRANCH_COMPOSITION = PASS")
    print("C025_B_UNIT_CONFLICT_LIFT = PASS")
    print("C025_B_MALFORMED_CERTIFICATE_REJECTION = PASS")
    print("C025_B_ROOT_FINGERPRINT_REJECTION = PASS")
    print(
        "claim_boundary = reason soundness and local extraction mechanics only; "
        "reason discovery, total DAG size, global proof search and P-vs-NP remain open"
    )


if __name__ == "__main__":
    self_test()
