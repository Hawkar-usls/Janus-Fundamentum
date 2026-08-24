#!/usr/bin/env python3
"""C025-B2 extension-aware portable reason verifier v0.

The certificate may introduce fresh extension variables with definitions

    e <-> (a AND b)

and may use exact Resolution over root and definitional clauses.  The reusable
advertised clause must mention original/root variables only.

This removes one known plain-Resolution proof-size obstruction as a language
restriction, but makes no universal proof-size or proof-search claim.
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


def root_variables(cnf: CNF) -> set[int]:
    return {abs(literal) for clause in cnf for literal in clause}


def resolve_clauses(left: Clause, right: Clause, pivot: int) -> Clause:
    if pivot <= 0:
        raise ValueError("pivot must be positive")
    if pivot in left and -pivot in right:
        left_drop, right_drop = pivot, -pivot
    elif -pivot in left and pivot in right:
        left_drop, right_drop = -pivot, pivot
    else:
        raise ValueError("parents lack complementary pivot literals")
    merged = (set(left) - {left_drop}) | (set(right) - {right_drop})
    candidate = canonical_clause(merged)
    if candidate is None:
        raise ValueError("tautological resolvent is not admitted in v0")
    return candidate


@dataclass(frozen=True)
class ExtensionDef:
    variable: int
    left_literal: int
    right_literal: int


def extension_clause(definition: ExtensionDef, slot: int) -> Clause:
    e = definition.variable
    a = definition.left_literal
    b = definition.right_literal
    raw: tuple[int, ...]
    if slot == 0:
        raw = (-e, a)
    elif slot == 1:
        raw = (-e, b)
    elif slot == 2:
        raw = (e, -a, -b)
    else:
        raise ValueError("extension slot must be 0, 1 or 2")
    clause = canonical_clause(raw)
    if clause is None:
        raise ValueError("v0 disallows degenerate extension definitions")
    return clause


@dataclass(frozen=True)
class ProofNode:
    kind: str
    clause: Clause
    source_clause: int | None = None
    definition: int | None = None
    slot: int | None = None
    left: int | None = None
    right: int | None = None
    pivot: int | None = None


@dataclass(frozen=True)
class ExtensionReasonCertificate:
    root_fingerprint: str
    definitions: tuple[ExtensionDef, ...]
    advertised_clause: Clause
    final_node: int
    nodes: tuple[ProofNode, ...]


def verify_definitions(root: CNF, definitions: tuple[ExtensionDef, ...]) -> tuple[bool, set[int]]:
    original = root_variables(root)
    available = set(original)
    last_id = max(original, default=0)

    for definition in definitions:
        e = definition.variable
        a = definition.left_literal
        b = definition.right_literal
        if e <= last_id or e in available:
            return False, set()
        if a == 0 or b == 0:
            return False, set()
        if abs(a) not in available or abs(b) not in available:
            return False, set()
        if abs(a) == abs(b):
            return False, set()
        try:
            for slot in range(3):
                extension_clause(definition, slot)
        except ValueError:
            return False, set()
        available.add(e)
        last_id = e

    return True, available


def _reachable(certificate: ExtensionReasonCertificate) -> set[int]:
    reached: set[int] = set()

    def visit(index: int) -> None:
        if index in reached:
            return
        node = certificate.nodes[index]
        if node.kind == "RESOLVE":
            assert node.left is not None and node.right is not None
            visit(node.left)
            visit(node.right)
        reached.add(index)

    visit(certificate.final_node)
    return reached


def verify_certificate(root_cnf: CNF, certificate: ExtensionReasonCertificate) -> bool:
    root = canonical_cnf(root_cnf)
    original = root_variables(root)
    try:
        if certificate.root_fingerprint != formula_fingerprint(root):
            return False
        definitions_ok, available = verify_definitions(root, certificate.definitions)
        if not definitions_ok:
            return False

        advertised = canonical_clause(certificate.advertised_clause)
        if advertised is None or advertised != certificate.advertised_clause:
            return False
        if any(abs(literal) not in original for literal in advertised):
            return False
        if not 0 <= certificate.final_node < len(certificate.nodes):
            return False

        for index, node in enumerate(certificate.nodes):
            if node.kind == "ROOT_AXIOM":
                if node.source_clause is None:
                    return False
                if any(value is not None for value in (node.definition, node.slot, node.left, node.right, node.pivot)):
                    return False
                if not 0 <= node.source_clause < len(root):
                    return False
                if node.clause != root[node.source_clause]:
                    return False
                continue

            if node.kind == "EXTENSION_AXIOM":
                if node.definition is None or node.slot is None:
                    return False
                if any(value is not None for value in (node.source_clause, node.left, node.right, node.pivot)):
                    return False
                if not 0 <= node.definition < len(certificate.definitions):
                    return False
                expected = extension_clause(certificate.definitions[node.definition], node.slot)
                if node.clause != expected:
                    return False
                continue

            if node.kind != "RESOLVE":
                return False
            if node.left is None or node.right is None or node.pivot is None:
                return False
            if node.source_clause is not None or node.definition is not None or node.slot is not None:
                return False
            if not (0 <= node.left < index and 0 <= node.right < index):
                return False
            if node.pivot not in available:
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
        if _reachable(certificate) != set(range(len(certificate.nodes))):
            return False
        return True
    except (AssertionError, IndexError, ValueError):
        return False


def literal_false(literal: int, assignment: Assignment) -> bool:
    variable = abs(literal)
    if variable not in assignment:
        return False
    value = bool(assignment[variable])
    return not (value if literal > 0 else not value)


def certificate_applies(
    root_cnf: CNF,
    certificate: ExtensionReasonCertificate,
    assignment: Assignment,
) -> bool:
    return verify_certificate(root_cnf, certificate) and all(
        literal_false(literal, assignment)
        for literal in certificate.advertised_clause
    )


class Builder:
    def __init__(self, root_cnf: CNF, definitions: Iterable[ExtensionDef]):
        self.root = canonical_cnf(root_cnf)
        self.definitions = tuple(definitions)
        ok, _ = verify_definitions(self.root, self.definitions)
        if not ok:
            raise ValueError("invalid extension definitions")
        self.nodes: list[ProofNode] = []

    def root_axiom(self, clause: Iterable[int]) -> int:
        candidate = canonical_clause(clause)
        if candidate is None:
            raise ValueError("tautological root target")
        source = self.root.index(candidate)
        self.nodes.append(ProofNode("ROOT_AXIOM", candidate, source_clause=source))
        return len(self.nodes) - 1

    def extension_axiom(self, definition: int, slot: int) -> int:
        clause = extension_clause(self.definitions[definition], slot)
        self.nodes.append(
            ProofNode(
                "EXTENSION_AXIOM",
                clause,
                definition=definition,
                slot=slot,
            )
        )
        return len(self.nodes) - 1

    def resolve(self, left: int, right: int, pivot: int) -> int:
        clause = resolve_clauses(self.nodes[left].clause, self.nodes[right].clause, pivot)
        self.nodes.append(
            ProofNode("RESOLVE", clause, left=left, right=right, pivot=pivot)
        )
        return len(self.nodes) - 1

    def export(self, final_node: int) -> ExtensionReasonCertificate:
        if not 0 <= final_node < len(self.nodes):
            raise IndexError("bad final node")
        reached: set[int] = set()

        def visit(index: int) -> None:
            if index in reached:
                return
            node = self.nodes[index]
            if node.kind == "RESOLVE":
                assert node.left is not None and node.right is not None
                visit(node.left)
                visit(node.right)
            reached.add(index)

        visit(final_node)
        ordered = sorted(reached)
        remap = {old: new for new, old in enumerate(ordered)}
        exported: list[ProofNode] = []
        for old in ordered:
            node = self.nodes[old]
            if node.kind == "RESOLVE":
                assert node.left is not None and node.right is not None
                exported.append(
                    ProofNode(
                        "RESOLVE",
                        node.clause,
                        left=remap[node.left],
                        right=remap[node.right],
                        pivot=node.pivot,
                    )
                )
            else:
                exported.append(node)
        final = remap[final_node]
        return ExtensionReasonCertificate(
            root_fingerprint=formula_fingerprint(self.root),
            definitions=self.definitions,
            advertised_clause=exported[final].clause,
            final_node=final,
            nodes=tuple(exported),
        )


def valid_fixture() -> tuple[CNF, ExtensionReasonCertificate]:
    # a=1, b=2, c=3, d=4, e=5 := a AND b
    root = canonical_cnf([(1, 3), (2, 3), (-1, -2, 4)])
    builder = Builder(root, [ExtensionDef(5, 1, 2)])

    a_or_c = builder.root_axiom((1, 3))
    b_or_c = builder.root_axiom((2, 3))
    not_a_not_b_or_d = builder.root_axiom((-1, -2, 4))
    not_e_or_a = builder.extension_axiom(0, 0)
    not_e_or_b = builder.extension_axiom(0, 1)
    e_or_not_a_not_b = builder.extension_axiom(0, 2)

    e_not_b_c = builder.resolve(e_or_not_a_not_b, a_or_c, 1)
    e_or_c = builder.resolve(e_not_b_c, b_or_c, 2)

    not_e_not_b_d = builder.resolve(not_a_not_b_or_d, not_e_or_a, 1)
    not_e_or_d = builder.resolve(not_e_not_b_d, not_e_or_b, 2)

    c_or_d = builder.resolve(e_or_c, not_e_or_d, 5)
    certificate = builder.export(c_or_d)
    return root, certificate


def self_test() -> None:
    root, certificate = valid_fixture()
    assert certificate.advertised_clause == (3, 4)
    assert verify_certificate(root, certificate)
    assert certificate_applies(root, certificate, {3: False, 4: False})
    assert not certificate_applies(root, certificate, {3: True, 4: False})

    assert not verify_certificate(canonical_cnf([(1,), (-1,)]), certificate)

    bad_collision = ExtensionReasonCertificate(
        root_fingerprint=formula_fingerprint(root),
        definitions=(ExtensionDef(1, 2, 3),),
        advertised_clause=certificate.advertised_clause,
        final_node=certificate.final_node,
        nodes=certificate.nodes,
    )
    assert not verify_certificate(root, bad_collision)

    bad_forward = ExtensionReasonCertificate(
        root_fingerprint=formula_fingerprint(root),
        definitions=(ExtensionDef(5, 1, 6),),
        advertised_clause=certificate.advertised_clause,
        final_node=certificate.final_node,
        nodes=certificate.nodes,
    )
    assert not verify_certificate(root, bad_forward)

    ext_builder = Builder(root, [ExtensionDef(5, 1, 2)])
    ext_node = ext_builder.extension_axiom(0, 2)
    ext_clause_certificate = ext_builder.export(ext_node)
    assert any(abs(lit) == 5 for lit in ext_clause_certificate.advertised_clause)
    assert not verify_certificate(root, ext_clause_certificate)

    nodes = list(certificate.nodes)
    ext_index = next(i for i, node in enumerate(nodes) if node.kind == "EXTENSION_AXIOM")
    ext_node_original = nodes[ext_index]
    nodes[ext_index] = ProofNode(
        "EXTENSION_AXIOM",
        (999,),
        definition=ext_node_original.definition,
        slot=ext_node_original.slot,
    )
    bad_ext_clause = ExtensionReasonCertificate(
        certificate.root_fingerprint,
        certificate.definitions,
        certificate.advertised_clause,
        certificate.final_node,
        tuple(nodes),
    )
    assert not verify_certificate(root, bad_ext_clause)

    garbage = ExtensionReasonCertificate(
        certificate.root_fingerprint,
        certificate.definitions,
        certificate.advertised_clause,
        certificate.final_node,
        certificate.nodes
        + (ProofNode("ROOT_AXIOM", root[0], source_clause=0),),
    )
    assert not verify_certificate(root, garbage)

    print("C025_B2_EXTENSION_AWARE_VERIFIER = PASS")
    print("C025_B2_CONSERVATIVE_ORIGINAL_CLAUSE_REUSE = PASS")
    print("C025_B2_EXTENSION_PARTICIPATING_FIXTURE = PASS")
    print("C025_B2_ROOT_COLLISION_REJECTION = PASS")
    print("C025_B2_FORWARD_DEPENDENCY_REJECTION = PASS")
    print("C025_B2_EXTENSION_LEAK_REJECTION = PASS")
    print("C025_B2_EXTENSION_AXIOM_TAMPER_REJECTION = PASS")
    print("C025_B2_UNREACHABLE_GARBAGE_REJECTION = PASS")
    print(
        "claim_boundary = extension-aware certificate soundness mechanics only; "
        "universal proof size, extension-definition discovery, active representation, "
        "global proof search and P-vs-NP remain open"
    )


if __name__ == "__main__":
    self_test()
