#!/usr/bin/env python3
"""Adversarial negative replay for C025-B2 extension-aware reasons v0.

A PASS means the frozen verifier rejects the listed malformed certificates.
It does not establish a polynomial proof-size or proof-search theorem.
"""

from __future__ import annotations

from dataclasses import replace

from janus_tear_policy0b_extension_reason_v0 import (
    Builder,
    ExtensionDef,
    ExtensionReasonCertificate,
    ProofNode,
    canonical_cnf,
    formula_fingerprint,
    valid_fixture,
    verify_certificate,
)


def rebuild(
    certificate: ExtensionReasonCertificate,
    *,
    definitions=None,
    advertised_clause=None,
    final_node=None,
    nodes=None,
    root_fingerprint=None,
) -> ExtensionReasonCertificate:
    return ExtensionReasonCertificate(
        root_fingerprint=(
            certificate.root_fingerprint
            if root_fingerprint is None
            else root_fingerprint
        ),
        definitions=(certificate.definitions if definitions is None else definitions),
        advertised_clause=(
            certificate.advertised_clause
            if advertised_clause is None
            else advertised_clause
        ),
        final_node=(certificate.final_node if final_node is None else final_node),
        nodes=(certificate.nodes if nodes is None else nodes),
    )


def first_extension_axiom(certificate: ExtensionReasonCertificate) -> int:
    return next(
        index
        for index, node in enumerate(certificate.nodes)
        if node.kind == "EXTENSION_AXIOM"
    )


def first_resolution(certificate: ExtensionReasonCertificate) -> int:
    return next(
        index
        for index, node in enumerate(certificate.nodes)
        if node.kind == "RESOLVE"
    )


def self_test() -> None:
    root, certificate = valid_fixture()
    assert verify_certificate(root, certificate)

    root_collision = rebuild(
        certificate,
        definitions=(ExtensionDef(1, 2, 3),),
    )
    assert not verify_certificate(root, root_collision)

    duplicate_extension_id = rebuild(
        certificate,
        definitions=(
            ExtensionDef(5, 1, 2),
            ExtensionDef(5, 3, 4),
        ),
    )
    assert not verify_certificate(root, duplicate_extension_id)

    descending_extension_ids = rebuild(
        certificate,
        definitions=(
            ExtensionDef(6, 1, 2),
            ExtensionDef(5, 3, 4),
        ),
    )
    assert not verify_certificate(root, descending_extension_ids)

    forward_dependency = rebuild(
        certificate,
        definitions=(
            ExtensionDef(5, 1, 6),
            ExtensionDef(6, 1, 2),
        ),
    )
    assert not verify_certificate(root, forward_dependency)

    cyclic_dependency = rebuild(
        certificate,
        definitions=(
            ExtensionDef(5, 1, 6),
            ExtensionDef(6, 2, 5),
        ),
    )
    assert not verify_certificate(root, cyclic_dependency)

    ext_builder = Builder(root, [ExtensionDef(5, 1, 2)])
    ext_node = ext_builder.extension_axiom(0, 2)
    leaked = ext_builder.export(ext_node)
    assert any(abs(literal) == 5 for literal in leaked.advertised_clause)
    assert not verify_certificate(root, leaked)

    nodes = list(certificate.nodes)
    ext_index = first_extension_axiom(certificate)
    ext_node = nodes[ext_index]
    nodes[ext_index] = replace(ext_node, clause=(999,))
    tampered_extension_axiom = rebuild(certificate, nodes=tuple(nodes))
    assert not verify_certificate(root, tampered_extension_axiom)

    nodes = list(certificate.nodes)
    ext_index = first_extension_axiom(certificate)
    ext_node = nodes[ext_index]
    nodes[ext_index] = replace(ext_node, slot=3)
    tampered_extension_slot = rebuild(certificate, nodes=tuple(nodes))
    assert not verify_certificate(root, tampered_extension_slot)

    nodes = list(certificate.nodes)
    resolution_index = first_resolution(certificate)
    resolution_node = nodes[resolution_index]
    nodes[resolution_index] = replace(resolution_node, clause=(777,))
    tampered_resolution = rebuild(certificate, nodes=tuple(nodes))
    assert not verify_certificate(root, tampered_resolution)

    advertised_tamper = rebuild(certificate, advertised_clause=(3,))
    assert not verify_certificate(root, advertised_tamper)

    wrong_root = rebuild(
        certificate,
        root_fingerprint=formula_fingerprint(canonical_cnf([(1,), (-1,)])),
    )
    assert not verify_certificate(root, wrong_root)

    garbage = rebuild(
        certificate,
        nodes=certificate.nodes
        + (ProofNode("ROOT_AXIOM", root[0], source_clause=0),),
    )
    assert not verify_certificate(root, garbage)

    print("C025_B2_NEGATIVE_FRESH_ROOT_COLLISION = PASS")
    print("C025_B2_NEGATIVE_DUPLICATE_EXTENSION_ID = PASS")
    print("C025_B2_NEGATIVE_DESCENDING_EXTENSION_ID = PASS")
    print("C025_B2_NEGATIVE_FORWARD_DEPENDENCY = PASS")
    print("C025_B2_NEGATIVE_CYCLIC_DEPENDENCY = PASS")
    print("C025_B2_NEGATIVE_EXTENSION_LEAK = PASS")
    print("C025_B2_NEGATIVE_EXTENSION_AXIOM_TAMPER = PASS")
    print("C025_B2_NEGATIVE_EXTENSION_SLOT_TAMPER = PASS")
    print("C025_B2_NEGATIVE_RESOLUTION_TAMPER = PASS")
    print("C025_B2_NEGATIVE_ADVERTISED_CLAUSE_TAMPER = PASS")
    print("C025_B2_NEGATIVE_ROOT_BINDING = PASS")
    print("C025_B2_NEGATIVE_UNREACHABLE_GARBAGE = PASS")
    print(
        "claim_boundary = adversarial verifier admission only; universal proof "
        "size, extension discovery, total representation and proof search remain open"
    )


if __name__ == "__main__":
    self_test()
