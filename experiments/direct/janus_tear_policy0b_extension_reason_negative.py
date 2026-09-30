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
        root_fingerprint=(certificate.root_fingerprint if root_fingerprint is None else root_fingerprint),
        definitions=(certificate.definitions if definitions is None else definitions),
        advertised_clause=(certificate.advertised_clause if advertised_clause is None else advertised_clause),
        final_node=(certificate.final_node if final_node is None else final_node),
        nodes=(certificate.nodes if nodes is None else nodes),
    )


def first_extension_axiom(certificate: ExtensionReasonCertificate) -> int:
    return next(index for index, node in enumerate(certificate.nodes) if node.kind == "EXTENSION_AXIOM")


def first_resolution(certificate: ExtensionReasonCertificate) -> int:
    return next(index for index, node in enumerate(certificate.nodes) if node.kind == "RESOLVE")


def self_test() -> None:
    root, certificate = valid_fixture()
    assert verify_certificate(root, certificate)

    assert not verify_certificate(root, rebuild(certificate, definitions=(ExtensionDef(1, 2, 3),)))

    assert not verify_certificate(
        root,
        rebuild(certificate, definitions=(ExtensionDef(5, 1, 2), ExtensionDef(5, 3, 4))),
    )

    assert not verify_certificate(
        root,
        rebuild(certificate, definitions=(ExtensionDef(6, 1, 2), ExtensionDef(5, 3, 4))),
    )

    assert not verify_certificate(
        root,
        rebuild(certificate, definitions=(ExtensionDef(5, 1, 6), ExtensionDef(6, 1, 2))),
    )

    assert not verify_certificate(
        root,
        rebuild(certificate, definitions=(ExtensionDef(5, 1, 6), ExtensionDef(6, 2, 5))),
    )

    ext_builder = Builder(root, [ExtensionDef(5, 1, 2)])
    leaked = ext_builder.export(ext_builder.extension_axiom(0, 2))
    assert any(abs(literal) == 5 for literal in leaked.advertised_clause)
    assert not verify_certificate(root, leaked)

    nodes = list(certificate.nodes)
    ext_index = first_extension_axiom(certificate)
    nodes[ext_index] = replace(nodes[ext_index], clause=(999,))
    assert not verify_certificate(root, rebuild(certificate, nodes=tuple(nodes)))

    nodes = list(certificate.nodes)
    ext_index = first_extension_axiom(certificate)
    nodes[ext_index] = replace(nodes[ext_index], slot=3)
    assert not verify_certificate(root, rebuild(certificate, nodes=tuple(nodes)))

    nodes = list(certificate.nodes)
    resolution_index = first_resolution(certificate)
    nodes[resolution_index] = replace(nodes[resolution_index], clause=(777,))
    assert not verify_certificate(root, rebuild(certificate, nodes=tuple(nodes)))

    assert not verify_certificate(root, rebuild(certificate, advertised_clause=(3,)))

    wrong_root = rebuild(
        certificate,
        root_fingerprint=formula_fingerprint(canonical_cnf([(1,), (-1,)])),
    )
    assert not verify_certificate(root, wrong_root)

    garbage = rebuild(
        certificate,
        nodes=certificate.nodes + (ProofNode("ROOT_AXIOM", root[0], source_clause=0),),
    )
    assert not verify_certificate(root, garbage)

    unused_definition = rebuild(
        certificate,
        definitions=certificate.definitions + (ExtensionDef(6, 3, 4),),
    )
    assert not verify_certificate(root, unused_definition)

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
    print("C025_B2_NEGATIVE_UNREACHABLE_NODE_GARBAGE = PASS")
    print("C025_B2_NEGATIVE_UNUSED_DEFINITION_GARBAGE = PASS")
    print(
        "claim_boundary = adversarial verifier admission only; universal proof "
        "size, extension discovery, total representation and proof search remain open"
    )


if __name__ == "__main__":
    self_test()
