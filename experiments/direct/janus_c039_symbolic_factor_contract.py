#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Protocol

CERT_SCHEMA = "janus.c039.symbolic-factor-operation.v1"
MESSAGE_SCHEMA = "janus.c039.symbolic-message.v1"
DOMAIN = b"JANUS-C039-OP-V1\0"
SHA = re.compile(r"^sha256:[0-9a-f]{64}$")

FORBIDDEN_TYPES = {
    "RAW_BITMAP", "EVALUATION_VECTOR", "ROW_MATRIX", "TRUTH_TABLE_BLOB",
    "ASSIGNMENT_INDEX", "ARBITRARY_LOOKUP_TABLE",
}
ALLOWED_TYPES = {
    "HORN_CLOSURE", "AFFINE_RREF", "BETA_ACYCLIC_ELIMINATION",
    "COMPOSED_C036_1_MESSAGE", "SYMBOLIC_CONTINUATION",
    "SYMBOLIC_STATE_PAIR",
}
FORBIDDEN_KEYS = {
    "assignments", "assignment_rows", "communication_rows", "evaluation_vector",
    "row_matrix", "truth_table", "truth_table_blob", "raw_bitmap",
    "assignment_index", "lookup_table",
}
LANGUAGES = {"HORN_V1", "AFFINE_GF2_V1", "BETA_ACYCLIC_V1", "COMPOSED_C036_1_V1"}


class Operator(str, Enum):
    LEAF = "LEAF"
    JOIN = "JOIN"
    PROJECT = "PROJECT"
    MERGE = "MERGE"
    SEPARATE = "SEPARATE"


class Terminal(str, Enum):
    FACTOR_BUILT = "FACTOR_BUILT"
    MERGED_CERTIFIED = "MERGED_CERTIFIED"
    SEPARATED_CERTIFIED = "SEPARATED_CERTIFIED"
    CLOSED_POLY = "CLOSED_POLY"
    OPEN_LANGUAGE = "OPEN_LANGUAGE"
    OPEN_BUDGET = "OPEN_BUDGET"
    OPEN_EQUIVALENCE = "OPEN_EQUIVALENCE"
    OPEN_REPRESENTATION_GROWTH = "OPEN_REPRESENTATION_GROWTH"
    OPEN_COMPOSITION = "OPEN_COMPOSITION"
    INVALID_CERTIFICATE = "INVALID_CERTIFICATE"


OPEN = {
    Terminal.OPEN_LANGUAGE, Terminal.OPEN_BUDGET, Terminal.OPEN_EQUIVALENCE,
    Terminal.OPEN_REPRESENTATION_GROWTH, Terminal.OPEN_COMPOSITION,
}


@dataclass(frozen=True)
class Result:
    terminal: Terminal
    operation_digest: str | None
    output_message_digest: str | None


class OpenCoreVaultSink(Protocol):
    async def current_capability_digest(self) -> bytes: ...
    async def record_open(
        self, core_digest: bytes, capability_digest: bytes,
        open_trace: Mapping[str, Any],
    ) -> None: ...
    async def record_poly(
        self, core_digest: bytes, capability_digest: bytes,
        certificate_digest: bytes,
    ) -> None: ...


class InMemoryVaultAdapter:
    def __init__(self, capability: bytes):
        self.capability = capability
        self.open_records: list[tuple[Any, ...]] = []
        self.poly_records: list[tuple[Any, ...]] = []

    async def current_capability_digest(self) -> bytes:
        return self.capability

    async def record_open(self, core_digest, capability_digest, open_trace) -> None:
        self.open_records.append((core_digest, capability_digest, dict(open_trace)))

    async def record_poly(self, core_digest, capability_digest, certificate_digest) -> None:
        self.poly_records.append((core_digest, capability_digest, certificate_digest))


def canonical_json(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool, int)):
            return
        if isinstance(item, float):
            raise TypeError("floats forbidden")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict) and all(isinstance(k, str) for k in item):
            for child in item.values():
                check(child)
            return
        raise TypeError("non-canonical JSON value")
    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode()


def d(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


def db(value: str) -> bytes:
    if SHA.fullmatch(value) is None:
        raise ValueError("invalid digest")
    return bytes.fromhex(value[7:])


def operation_digest(cert: Mapping[str, Any]) -> str:
    semantic = dict(cert)
    semantic.pop("operation_digest", None)
    return "sha256:" + hashlib.sha256(DOMAIN + canonical_json(semantic)).hexdigest()


def reject_enumeration(item: Any) -> None:
    if isinstance(item, dict):
        for key, value in item.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError("enumerative field")
            reject_enumeration(value)
    elif isinstance(item, list):
        for value in item:
            reject_enumeration(value)


def digest(value: Any) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def string_set(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(x, str) and x for x in value)
        and len(value) == len(set(value))
    )


def common(cert: Mapping[str, Any]) -> tuple[Operator, set[str]]:
    canonical_json(cert)
    reject_enumeration(cert)
    if cert.get("schema") != CERT_SCHEMA:
        raise ValueError("schema")
    op = Operator(cert.get("operator"))
    for field in (
        "formula_digest", "vtree_digest", "vtree_node_digest",
        "capability_digest", "language_profile_digest", "payload_digest",
        "output_message_digest",
    ):
        if not digest(cert.get(field)):
            raise ValueError(field)
    if cert.get("language_profile") not in LANGUAGES:
        raise ValueError("language")
    payload = cert.get("message_payload")
    if not isinstance(payload, dict) or payload.get("schema") != MESSAGE_SCHEMA:
        raise ValueError("payload")
    ptype = payload.get("payload_type")
    if ptype in FORBIDDEN_TYPES or ptype not in ALLOWED_TYPES:
        raise ValueError("payload type")
    inputs = cert.get("input_message_digests")
    if not isinstance(inputs, list) or not all(digest(x) for x in inputs):
        raise ValueError("input digests")
    for field in ("input_scope", "output_scope", "input_boundary", "output_boundary"):
        if not string_set(cert.get(field)):
            raise ValueError(field)
    ledger = cert.get("work_ledger")
    if (
        not isinstance(ledger, dict)
        or any(not isinstance(ledger.get(k), int) or ledger[k] < 0
               for k in ("work_units", "max_work_units"))
    ):
        raise ValueError("work")
    if any(not isinstance(cert.get(k), int) or cert[k] < 0
           for k in ("representation_size", "declared_size_bound")):
        raise ValueError("size")
    refs = cert.get("proof_refs")
    if not isinstance(refs, list):
        raise ValueError("proof refs")
    kinds = set()
    for ref in refs:
        if (
            not isinstance(ref, dict)
            or not isinstance(ref.get("kind"), str)
            or not digest(ref.get("digest"))
        ):
            raise ValueError("proof ref")
        kinds.add(ref["kind"])
    return op, kinds


async def validate(cert: Mapping[str, Any]) -> Result:
    try:
        op, proofs = common(cert)
    except (TypeError, ValueError):
        return Result(Terminal.INVALID_CERTIFICATE, None, None)

    od = operation_digest(cert)
    if cert["work_ledger"]["work_units"] > cert["work_ledger"]["max_work_units"]:
        return Result(Terminal.OPEN_BUDGET, od, None)
    if cert["representation_size"] > cert["declared_size_bound"]:
        return Result(Terminal.OPEN_REPRESENTATION_GROWTH, od, None)

    ins, outs = set(cert["input_scope"]), set(cert["output_scope"])
    inb, outb = set(cert["input_boundary"]), set(cert["output_boundary"])
    meta = cert.get("operator_metadata")
    if not isinstance(meta, dict):
        return Result(Terminal.INVALID_CERTIFICATE, None, None)

    if op is Operator.LEAF:
        valid = "NATIVE_REPLAY" in proofs and not cert["input_message_digests"]
        terminal = Terminal.FACTOR_BUILT
    elif op is Operator.JOIN:
        left, right = set(meta.get("left_scope", [])), set(meta.get("right_scope", []))
        valid = (
            not left & right and left | right == outs == ins
            and len(cert["input_message_digests"]) == 2
            and "JOIN_REPLAY" in proofs
        )
        terminal = Terminal.FACTOR_BUILT
    elif op is Operator.PROJECT:
        retained = set(meta.get("retained_boundary", []))
        valid = (
            retained == outb and outb <= inb and outs <= ins
            and "PROJECTION_REPLAY" in proofs
        )
        terminal = Terminal.FACTOR_BUILT
    elif op is Operator.MERGE:
        valid = len(cert["input_message_digests"]) == 2 and "EQUIVALENCE" in proofs
        terminal = Terminal.MERGED_CERTIFIED
    else:
        inputs = cert["input_message_digests"]
        valid = (
            len(inputs) == 2 and inputs[0] != inputs[1]
            and "SEPARATOR" in proofs and digest(meta.get("separator_digest"))
        )
        terminal = Terminal.SEPARATED_CERTIFIED

    if not valid:
        return Result(Terminal.INVALID_CERTIFICATE, None, None)
    return Result(terminal, od, cert["payload_digest"])


async def leaf(cert): return await validate(cert) if cert.get("operator") == "LEAF" else Result(Terminal.INVALID_CERTIFICATE, None, None)
async def join(cert): return await validate(cert) if cert.get("operator") == "JOIN" else Result(Terminal.INVALID_CERTIFICATE, None, None)
async def project(cert): return await validate(cert) if cert.get("operator") == "PROJECT" else Result(Terminal.INVALID_CERTIFICATE, None, None)
async def merge(cert): return await validate(cert) if cert.get("operator") == "MERGE" else Result(Terminal.INVALID_CERTIFICATE, None, None)
async def separate(cert): return await validate(cert) if cert.get("operator") == "SEPARATE" else Result(Terminal.INVALID_CERTIFICATE, None, None)


async def route_vault(
    sink: OpenCoreVaultSink, result: Result, *, core: bytes,
    capability: bytes, certificate: bytes,
) -> str:
    if await sink.current_capability_digest() != capability:
        raise ValueError("capability mismatch")
    if result.terminal is Terminal.CLOSED_POLY:
        await sink.record_poly(core, capability, certificate)
        return "record_poly"
    if result.terminal in OPEN:
        await sink.record_open(core, capability, {
            "schema": "janus.c039.open-trace.v1",
            "terminal": result.terminal.value,
            "operation_digest": result.operation_digest,
        })
        return "record_open"
    raise ValueError("terminal not routable")


def base(op: Operator, language="HORN_V1", ptype="HORN_CLOSURE") -> dict[str, Any]:
    return {
        "schema": CERT_SCHEMA, "operator": op.value,
        "formula_digest": d("formula"), "vtree_digest": d("vtree"),
        "vtree_node_digest": d("node"), "capability_digest": d("capability"),
        "language_profile": language, "language_profile_digest": d(language),
        "input_message_digests": [], "output_message_digest": d(op.value + "-out"),
        "input_scope": ["x"], "output_scope": ["x"],
        "input_boundary": ["x"], "output_boundary": ["x"],
        "message_payload": {
            "schema": MESSAGE_SCHEMA, "payload_type": ptype,
            "symbolic_terms": ["fixture-only"],
        },
        "payload_digest": d(op.value + "-payload"), "proof_refs": [],
        "work_ledger": {"work_units": 3, "max_work_units": 20},
        "representation_size": 4, "declared_size_bound": 20,
        "operator_metadata": {}, "terminal": "SPECIFICATION_ONLY",
    }


def horn() -> dict[str, Any]:
    c = base(Operator.LEAF)
    c["proof_refs"] = [{"kind": "NATIVE_REPLAY", "digest": d("horn-proof")}]
    c["message_payload"]["symbolic_terms"] = ["x=>y", "y=>z"]
    return c


def affine() -> dict[str, Any]:
    c = base(Operator.PROJECT, "AFFINE_GF2_V1", "AFFINE_RREF")
    c.update({
        "input_message_digests": [d("affine-in")],
        "input_scope": ["x", "y", "z"], "output_scope": ["x", "z"],
        "input_boundary": ["x", "y", "z"], "output_boundary": ["x", "z"],
        "operator_metadata": {"retained_boundary": ["x", "z"]},
        "proof_refs": [{"kind": "PROJECTION_REPLAY", "digest": d("affine-proof")}],
    })
    c["message_payload"]["symbolic_terms"] = ["x+y=0", "y+z=1"]
    return c


def beta() -> dict[str, Any]:
    c = base(Operator.JOIN, "BETA_ACYCLIC_V1", "BETA_ACYCLIC_ELIMINATION")
    c.update({
        "input_message_digests": [d("left"), d("right")],
        "input_scope": ["a", "b"], "output_scope": ["a", "b"],
        "input_boundary": ["a", "b"], "output_boundary": ["a", "b"],
        "operator_metadata": {"left_scope": ["a"], "right_scope": ["b"]},
        "proof_refs": [{"kind": "JOIN_REPLAY", "digest": d("join-proof")}],
    })
    return c


def merge_cert(proof=True) -> dict[str, Any]:
    c = base(Operator.MERGE, ptype="SYMBOLIC_STATE_PAIR")
    c["input_message_digests"] = [d("state-a"), d("state-b")]
    if proof:
        c["proof_refs"] = [{"kind": "EQUIVALENCE", "digest": d("eq-proof")}]
    return c


def separate_cert() -> dict[str, Any]:
    c = base(Operator.SEPARATE, ptype="SYMBOLIC_CONTINUATION")
    c["input_message_digests"] = [d("state-a"), d("state-b")]
    c["proof_refs"] = [{"kind": "SEPARATOR", "digest": d("sep-proof")}]
    c["operator_metadata"] = {"separator_digest": d("continuation")}
    return c


async def self_test() -> dict[str, Any]:
    # 1 digest determinism
    h = horn()
    assert operation_digest(h) == operation_digest(dict(reversed(list(h.items()))))
    # 2 capability/vtree/language versioning
    baseline, changed = operation_digest(h), []
    for key, value in (
        ("capability_digest", d("cap2")), ("vtree_digest", d("tree2")),
        ("language_profile_digest", d("lang2")),
    ):
        item = dict(h); item[key] = value; changed.append(operation_digest(item))
    assert all(x != baseline for x in changed) and len(set(changed)) == 3
    # 3 native LEAF proof
    item = horn(); item["proof_refs"] = []
    assert (await leaf(item)).terminal is Terminal.INVALID_CERTIFICATE
    # 4 JOIN scopes
    item = beta(); item["operator_metadata"]["right_scope"] = ["a", "b"]
    assert (await join(item)).terminal is Terminal.INVALID_CERTIFICATE
    # 5 encoded truth table
    item = affine(); item["message_payload"]["payload_type"] = "EVALUATION_VECTOR"
    assert (await project(item)).terminal is Terminal.INVALID_CERTIFICATE
    # 6 uncertified MERGE
    assert (await merge(merge_cert(False))).terminal is Terminal.INVALID_CERTIFICATE
    # 7 deterministic certified MERGE
    a = await merge(merge_cert()); b = await merge(dict(reversed(list(merge_cert().items()))))
    assert a.terminal is Terminal.MERGED_CERTIFIED and a.operation_digest == b.operation_digest
    # 8 replayable SEPARATE
    a, b = await separate(separate_cert()), await separate(separate_cert())
    assert a.terminal is Terminal.SEPARATED_CERTIFIED and a.operation_digest == b.operation_digest
    # 9 budget OPEN has no partial factor
    item = affine(); item["work_ledger"]["work_units"] = 21
    a = await project(item)
    item = affine(); item["representation_size"] = 21
    b = await project(item)
    assert a.terminal is Terminal.OPEN_BUDGET and a.output_message_digest is None
    assert b.terminal is Terminal.OPEN_REPRESENTATION_GROWTH and b.output_message_digest is None
    # 10 terminal-specific, capability-locked Vault routing
    capability, core, certificate = db(d("vault-cap")), db(d("core")), db(d("cert"))
    sink = InMemoryVaultAdapter(capability)
    closed = Result(Terminal.CLOSED_POLY, d("closed"), None)
    opened = Result(Terminal.OPEN_LANGUAGE, d("open"), None)
    assert await route_vault(sink, closed, core=core, capability=capability, certificate=certificate) == "record_poly"
    assert await route_vault(sink, opened, core=core, capability=capability, certificate=certificate) == "record_open"
    blocked = False
    try:
        await route_vault(sink, opened, core=core, capability=db(d("wrong")), certificate=certificate)
    except ValueError:
        blocked = True
    assert blocked and len(sink.poly_records) == len(sink.open_records) == 1

    return {
        "status": "PASS", "canonical_id": "C039", "stage": "SPECIFICATION_ONLY",
        "acceptance_checks": 10, "operation_digest_deterministic": True,
        "capability_vtree_language_versioned": True, "native_leaf_proof_required": True,
        "join_scope_guarded": True, "encoded_truth_tables_rejected": True,
        "uncertified_merge_rejected": True, "merge_replay_deterministic": True,
        "separator_replay_deterministic": True,
        "budget_open_has_no_partial_factor": True,
        "vault_routing_capability_locked": True,
        "language_implementations_claimed": False, "p_vs_np": "OPEN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("use --self-test")
    print(json.dumps(asyncio.run(self_test()), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
