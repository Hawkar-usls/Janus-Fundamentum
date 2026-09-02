#!/usr/bin/env python3
"""C025-B standalone verifier for portable context-independent reasons.

Returned reason v1 is self-contained:

    R = (root_fingerprint, advertised_clause, final_node, proof_DAG)

The proof DAG uses only indexed root clauses as axioms and exact Resolution.
No decision assignment is a proof axiom.  A clean verifier needs only the root
CNF and the returned certificate; it does not share the producer's ProofStore.

Claim ceiling: reason soundness / portability / local lifting mechanics only.
Reason discovery, total proof-DAG size, cache indexing, global proof search and
P-vs-NP remain open.
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
        if candidate is not None:
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
class ReasonCertificate:
    root_fingerprint: str
    advertised_clause: Clause
    final_node: int
    nodes: tuple[ProofNode, ...]


@dataclass(frozen=True)
class Propagation:
    literal: int
    antecedent_node: int


class ProofStore:
    """Mutable producer ledger. Returned certificates never depend on it."""

    def __init__(self, root_cnf: CNF):
        self.root_cnf = canonical_cnf(root_cnf)
        self.root_fingerprint = formula_fingerprint(self.root_cnf)
        self.nodes: list[ProofNode] = []

    def add_axiom(self, source_clause: int) -> int:
        if not 0 <= source_clause < len(self.root_cnf):
            raise IndexError("source clause index out of range")
        self.nodes.append(
            ProofNode(
                kind="AXIOM",
                clause=self.root_cnf[source_clause],
                source_clause=source_clause,
            )
        )
        return len(self.nodes) - 1

    def axiom_for_clause(self, clause: Iterable[int]) -> int:
        candidate = canonical_clause(clause)
        if candidate is None:
            raise ValueError("tautological clause is not a root axiom target")
        try:
            source = self.root_cnf.index(candidate)
        except ValueError as exc:
            raise ValueError("clause is not present in canonical root CNF") from exc
        return self.add_axiom(source)

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

    def export_certificate(self, final_node: int) -> ReasonCertificate:
        if not 0 <= final_node < len(self.nodes):
            raise IndexError("final node out of range")

        reachable: set[int] = set()

        def visit(index: int) -> None:
            if index in reachable:
                return
            node = self.nodes[index]
            if node.kind == "RESOLVE":
                assert node.left is not None and node.right is not None
                visit(node.left)
                visit(node.right)
            reachable.add(index)

        visit(final_node)
        ordered = sorted(reachable)
        remap = {old: new for new, old in enumerate(ordered)}
        exported: list[ProofNode] = []

        for old in ordered:
            node = self.nodes[old]
            if node.kind == "AXIOM":
                exported.append(node)
            else:
                assert node.left is not None and node.right is not None
                exported.append(
                    ProofNode(
                        kind="RESOLVE",
                        clause=node.clause,
                        left=remap[node.left],
                        right=remap[node.right],
                        pivot=node.pivot,
                    )
                )

        final = remap[final_node]
        return ReasonCertificate(
            root_fingerprint=self.root_fingerprint,
            advertised_clause=exported[final].clause,
            final_node=final,
            nodes=tuple(exported),
        )


def _certificate_reachable(certificate: ReasonCertificate) -> set[int]:
    reachable: set[int] = set()

    def visit(index: int) -> None:
        if index in reachable:
            return
        node = certificate.nodes[index]
        if node.kind == "RESOLVE":
            assert node.left is not None and node.right is not None
            visit(node.left)
            visit(node.right)
        reachable.add(index)

    visit(certificate.final_node)
    return reachable


def verify_certificate(root_cnf: CNF, certificate: ReasonCertificate) -> bool:
    root = canonical_cnf(root_cnf)
    try:
        if certificate.root_fingerprint != formula_fingerprint(root):
            return False
        advertised = canonical_clause(certificate.advertised_clause)
        if advertised is None or advertised != certificate.advertised_clause:
            return False
        if not 0 <= certificate.final_node < len(certificate.nodes):
            return False

        for index, node in enumerate(certificate.nodes):
            if node.kind == "AXIOM":
                if node.source_clause is None:
                    return False
                if node.left is not None or node.right is not None or node.pivot is not None:
                    return False
                if not 0 <= node.source_clause < len(root):
                    return False
                if node.clause != root[node.source_clause]:
                    return False
                continue

            if node.kind != "RESOLVE":
                return False
            if node.left is None or node.right is None or node.pivot is None:
                return False
            if not (0 <= node.left < index and 0 <= node.right < index):
                return False
            expected = resolve_clauses(
                certificate.nodes[node.left].clause,
                certificate.nodes[node.right].clause,
                node.pivot,
            )
            if node.clause != expected:
                return False

        if certificate.nodes[certificate.final_node].clause != certificate.advertised_clause:
            return False
        if _certificate_reachable(certificate) != set(range(len(certificate.nodes))):
            return False
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def literal_false(literal: int, assignment: Assignment) -> bool:
    variable = abs(literal)
    if variable not in assignment:
        return False
    value = bool(assignment[variable])
    literal_true = value if literal > 0 else not value
    return not literal_true


def assignment_falsifies(clause: Clause, assignment: Assignment) -> bool:
    return all(literal_false(literal, assignment) for literal in clause)


def certificate_applies(root_cnf: CNF, certificate: ReasonCertificate, assignment: Assignment) -> bool:
    return verify_certificate(root_cnf, certificate) and assignment_falsifies(
        certificate.advertised_clause,
        assignment,
    )


def _append_certificate(target: list[ProofNode], certificate: ReasonCertificate) -> int:
    offset = len(target)
    for node in certificate.nodes:
        if node.kind == "AXIOM":
            target.append(node)
        else:
            assert node.left is not None and node.right is not None
            target.append(
                ProofNode(
                    kind="RESOLVE",
                    clause=node.clause,
                    left=node.left + offset,
                    right=node.right + offset,
                    pivot=node.pivot,
                )
            )
    return certificate.final_node + offset


def combine_branch_certificates(
    root_cnf: CNF,
    parent_assignment: Mapping[int, bool],
    pivot: int,
    false_certificate: ReasonCertificate,
    true_certificate: ReasonCertificate,
) -> ReasonCertificate:
    root = canonical_cnf(root_cnf)
    if not verify_certificate(root, false_certificate):
        raise ValueError("false-child certificate failed verification")
    if not verify_certificate(root, true_certificate):
        raise ValueError("true-child certificate failed verification")
    if pivot in parent_assignment:
        raise ValueError("pivot is already assigned in parent context")

    false_assignment = dict(parent_assignment)
    false_assignment[pivot] = False
    true_assignment = dict(parent_assignment)
    true_assignment[pivot] = True

    if not assignment_falsifies(false_certificate.advertised_clause, false_assignment):
        raise ValueError("false-child reason is not applicable")
    if not assignment_falsifies(true_certificate.advertised_clause, true_assignment):
        raise ValueError("true-child reason is not applicable")

    if assignment_falsifies(false_certificate.advertised_clause, parent_assignment):
        return false_certificate
    if assignment_falsifies(true_certificate.advertised_clause, parent_assignment):
        return true_certificate

    if pivot not in false_certificate.advertised_clause:
        raise ValueError("false-child reason lacks positive branch literal")
    if -pivot not in true_certificate.advertised_clause:
        raise ValueError("true-child reason lacks negative branch literal")

    nodes: list[ProofNode] = []
    left = _append_certificate(nodes, false_certificate)
    right = _append_certificate(nodes, true_certificate)
    clause = resolve_clauses(
        false_certificate.advertised_clause,
        true_certificate.advertised_clause,
        pivot,
    )
    nodes.append(ProofNode(kind="RESOLVE", clause=clause, left=left, right=right, pivot=pivot))
    result = ReasonCertificate(
        root_fingerprint=formula_fingerprint(root),
        advertised_clause=clause,
        final_node=len(nodes) - 1,
        nodes=tuple(nodes),
    )
    if not verify_certificate(root, result):
        raise AssertionError("composed portable certificate failed verification")
    if not assignment_falsifies(clause, parent_assignment):
        raise AssertionError("composed reason is not falsified by parent assignment")
    return result


def lift_unit_conflict_in_store(
    store: ProofStore,
    decision_assignment: Mapping[int, bool],
    propagations: list[Propagation],
    conflict_node: int,
) -> ReasonCertificate:
    if not 0 <= conflict_node < len(store.nodes):
        raise ValueError("conflict node out of range")

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
            if other != literal and not literal_false(other, full_assignment):
                raise ValueError("antecedent was not unit under trace prefix")
        full_assignment[variable] = literal > 0

    current_node = conflict_node
    if not assignment_falsifies(store.nodes[current_node].clause, full_assignment):
        raise ValueError("conflict clause is not falsified by full assignment")

    for step in reversed(propagations):
        if -step.literal not in store.nodes[current_node].clause:
            continue
        current_node = store.add_resolve(current_node, step.antecedent_node, abs(step.literal))

    certificate = store.export_certificate(current_node)
    if not assignment_falsifies(certificate.advertised_clause, decision_assignment):
        raise AssertionError("lifted reason still depends on propagated assignments")
    if not verify_certificate(store.root_cnf, certificate):
        raise AssertionError("lifted standalone certificate failed verification")
    return certificate


def self_test() -> None:
    root_direct = canonical_cnf([(-1, 2), (-1, -2)])
    producer = ProofStore(root_direct)
    d0 = producer.axiom_for_clause((-1, 2))
    d1 = producer.axiom_for_clause((-1, -2))
    d2 = producer.add_resolve(d0, d1, 2)
    direct = producer.export_certificate(d2)
    assert direct.advertised_clause == (-1,)
    assert verify_certificate(root_direct, direct)
    assert certificate_applies(root_direct, direct, {1: True})
    assert certificate_applies(root_direct, direct, {1: True, 7: False, 9: True})
    assert not certificate_applies(root_direct, direct, {1: False})

    unrelated_store = ProofStore(root_direct)
    unrelated_store.axiom_for_clause((-1, -2))
    assert verify_certificate(unrelated_store.root_cnf, direct)
    assert certificate_applies(unrelated_store.root_cnf, direct, {1: True})

    root_branch = canonical_cnf([(1, 2), (-1, 3)])
    false_store = ProofStore(root_branch)
    f = false_store.export_certificate(false_store.axiom_for_clause((1, 2)))
    true_store = ProofStore(root_branch)
    t = true_store.export_certificate(true_store.axiom_for_clause((-1, 3)))
    parent = combine_branch_certificates(
        root_branch,
        parent_assignment={2: False, 3: False},
        pivot=1,
        false_certificate=f,
        true_certificate=t,
    )
    assert parent.advertised_clause == (2, 3)
    assert certificate_applies(root_branch, parent, {2: False, 3: False})
    assert len(parent.nodes) == len(f.nodes) + len(t.nodes) + 1

    root_unit = canonical_cnf([(1, 2), (-2, 3), (-3,)])
    unit_store = ProofStore(root_unit)
    u_y = unit_store.axiom_for_clause((1, 2))
    u_z = unit_store.axiom_for_clause((-2, 3))
    u_conflict = unit_store.axiom_for_clause((-3,))
    lifted = lift_unit_conflict_in_store(
        unit_store,
        decision_assignment={1: False},
        propagations=[Propagation(2, u_y), Propagation(3, u_z)],
        conflict_node=u_conflict,
    )
    assert lifted.advertised_clause == (1,)
    assert verify_certificate(root_unit, lifted)
    assert certificate_applies(root_unit, lifted, {1: False})

    wrong_root = canonical_cnf([(1,), (-1,)])
    assert not verify_certificate(wrong_root, direct)

    tampered_advertised = ReasonCertificate(
        root_fingerprint=direct.root_fingerprint,
        advertised_clause=(1,),
        final_node=direct.final_node,
        nodes=direct.nodes,
    )
    assert not verify_certificate(root_direct, tampered_advertised)

    bad_nodes = list(parent.nodes)
    bad_final = bad_nodes[-1]
    bad_nodes[-1] = ProofNode(
        kind="RESOLVE",
        clause=(2,),
        left=bad_final.left,
        right=bad_final.right,
        pivot=bad_final.pivot,
    )
    tampered_proof = ReasonCertificate(
        root_fingerprint=parent.root_fingerprint,
        advertised_clause=(2,),
        final_node=parent.final_node,
        nodes=tuple(bad_nodes),
    )
    assert not verify_certificate(root_branch, tampered_proof)

    garbage = ReasonCertificate(
        root_fingerprint=direct.root_fingerprint,
        advertised_clause=direct.advertised_clause,
        final_node=direct.final_node,
        nodes=direct.nodes + (ProofNode(kind="AXIOM", clause=root_direct[0], source_clause=0),),
    )
    assert not verify_certificate(root_direct, garbage)

    print("C025_B_STANDALONE_PORTABLE_CERTIFICATE = PASS")
    print("C025_B_CONTEXT_REUSE = PASS")
    print("C025_B_STORE_ALIAS_REJECTION_BY_DESIGN = PASS")
    print("C025_B_BRANCH_COMPOSITION = PASS")
    print("C025_B_UNIT_CONFLICT_LIFT = PASS")
    print("C025_B_ROOT_FINGERPRINT_REJECTION = PASS")
    print("C025_B_ADVERTISED_CLAUSE_TAMPER_REJECTION = PASS")
    print("C025_B_PROOF_TAMPER_REJECTION = PASS")
    print("C025_B_UNREACHABLE_GARBAGE_REJECTION = PASS")
    print(
        "claim_boundary = portable reason soundness only; portable materialization "
        "may copy child DAGs, and reason discovery / total DAG size / global proof "
        "search / P-vs-NP remain open"
    )


if __name__ == "__main__":
    self_test()
