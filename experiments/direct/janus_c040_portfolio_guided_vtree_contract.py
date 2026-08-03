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

DISCOVERY_SCHEMA = "janus.c040.semantic-vtree-discovery.v1"
FEATURE_SCHEMA = "janus.c040.discovery-feature.v1"
CANDIDATE_SCHEMA = "janus.c040.vtree-candidate.v1"
PROBE_SCHEMA = "janus.c040.c039-probe-receipt.v1"
DOMAIN = b"JANUS-C040-DISCOVERY-V1\0"
SHA = re.compile(r"^sha256:[0-9a-f]{64}$")

CONSTRUCTORS = {
    "FIXED_CANONICAL_BASELINE_V1",
    "BALANCED_PRIMAL_SEPARATOR_V1",
    "CLAUSE_COOCCURRENCE_V1",
    "EQUALITY_CONTRACTED_V1",
    "AFFINE_SUPPORT_CLUSTER_V1",
    "HORN_HEAD_DISJOINT_V1",
    "BETA_ELIMINATION_V1",
}
FEATURE_KINDS = {
    "CLAUSE_INCIDENCE",
    "EQUALITY_FOREST",
    "FORCED_LITERAL_SET",
    "AFFINE_ROW_SUPPORT",
    "AFFINE_HULL_STATUS",
    "HORN_HEAD_MAP",
    "BETA_ELIMINATION_ORDER",
    "EXACT_OPEN_TRACE",
}
C039_TERMINALS = {
    "CLOSED_POLY",
    "OPEN_LANGUAGE",
    "OPEN_BUDGET",
    "OPEN_EQUIVALENCE",
    "OPEN_REPRESENTATION_GROWTH",
    "OPEN_COMPOSITION",
}
FORBIDDEN_KEYS = {
    "assignments",
    "assignment_rows",
    "communication_rows",
    "evaluation_vector",
    "row_matrix",
    "truth_table",
    "truth_table_blob",
    "raw_bitmap",
    "assignment_index",
    "lookup_table",
    "branch_assignment",
    "branch_values",
}


class Terminal(str, Enum):
    VTREE_SELECTED_CERTIFIED = "VTREE_SELECTED_CERTIFIED"
    OPEN_PORTFOLIO_EXHAUSTED = "OPEN_PORTFOLIO_EXHAUSTED"
    OPEN_DISCOVERY_BUDGET = "OPEN_DISCOVERY_BUDGET"
    OPEN_FEATURE_LANGUAGE = "OPEN_FEATURE_LANGUAGE"
    OPEN_CAPABILITY_STALE = "OPEN_CAPABILITY_STALE"
    INVALID_DISCOVERY_CERTIFICATE = "INVALID_DISCOVERY_CERTIFICATE"


OPEN = {
    Terminal.OPEN_PORTFOLIO_EXHAUSTED,
    Terminal.OPEN_DISCOVERY_BUDGET,
    Terminal.OPEN_FEATURE_LANGUAGE,
    Terminal.OPEN_CAPABILITY_STALE,
}


@dataclass(frozen=True)
class Result:
    terminal: Terminal
    discovery_digest: str | None
    selected_vtree_digest: str | None


class OpenCoreVaultSink(Protocol):
    async def current_capability_digest(self) -> bytes: ...
    async def record_open(
        self,
        core_digest: bytes,
        capability_digest: bytes,
        open_trace: Mapping[str, Any],
    ) -> None: ...
    async def record_poly(
        self,
        core_digest: bytes,
        capability_digest: bytes,
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
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def d(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


def db(value: str) -> bytes:
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise ValueError("invalid digest")
    return bytes.fromhex(value[7:])


def is_digest(value: Any) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def reject_enumeration(item: Any) -> None:
    if isinstance(item, dict):
        for key, value in item.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError("enumerative or branch-dependent field")
            reject_enumeration(value)
    elif isinstance(item, list):
        for value in item:
            reject_enumeration(value)


def discovery_digest(cert: Mapping[str, Any]) -> str:
    semantic = dict(cert)
    semantic.pop("discovery_digest", None)
    return "sha256:" + hashlib.sha256(DOMAIN + canonical_json(semantic)).hexdigest()


def string_set(value: Any, *, sorted_required: bool = False) -> bool:
    if not (
        isinstance(value, list)
        and all(isinstance(x, str) and x for x in value)
        and len(value) == len(set(value))
    ):
        return False
    return not sorted_required or value == sorted(value)


def validate_vtree(tree: Mapping[str, Any], variables: list[str]) -> str:
    if not isinstance(tree, dict):
        raise ValueError("vtree")
    leaves = tree.get("leaves")
    internal = tree.get("internal_nodes")
    root = tree.get("root")
    if not isinstance(leaves, dict) or not isinstance(internal, list) or not isinstance(root, str):
        raise ValueError("vtree shape")
    if set(leaves.values()) != set(variables) or len(leaves) != len(variables):
        raise ValueError("vtree leaf coverage")
    if len(set(leaves.values())) != len(variables):
        raise ValueError("duplicate vtree variable")

    children: dict[str, tuple[str, str]] = {}
    for node in internal:
        if not isinstance(node, dict) or set(node) != {"id", "left", "right"}:
            raise ValueError("internal node")
        node_id, left, right = node["id"], node["left"], node["right"]
        if not all(isinstance(x, str) and x for x in (node_id, left, right)):
            raise ValueError("internal identifiers")
        if node_id in children or node_id in leaves or left == right:
            raise ValueError("duplicate/internal collision")
        children[node_id] = (left, right)

    all_ids = set(leaves) | set(children)
    if root not in all_ids or len(all_ids) != 2 * len(variables) - 1:
        raise ValueError("vtree node count")
    for left, right in children.values():
        if left not in all_ids or right not in all_ids:
            raise ValueError("dangling child")

    seen: set[str] = set()
    stack: set[str] = set()

    def walk(node_id: str) -> set[str]:
        if node_id in stack:
            raise ValueError("vtree cycle")
        if node_id in leaves:
            seen.add(node_id)
            return {leaves[node_id]}
        stack.add(node_id)
        left, right = children[node_id]
        lvars, rvars = walk(left), walk(right)
        if lvars & rvars:
            raise ValueError("vtree duplicate reachability")
        stack.remove(node_id)
        seen.add(node_id)
        return lvars | rvars

    covered = walk(root)
    if covered != set(variables) or seen != all_ids:
        raise ValueError("vtree disconnected")
    return "sha256:" + hashlib.sha256(canonical_json(tree)).hexdigest()


def validate_feature(
    feature: Mapping[str, Any], formula_digest: str, capability_digest: str
) -> str:
    if not isinstance(feature, dict) or feature.get("schema") != FEATURE_SCHEMA:
        raise ValueError("feature schema")
    if feature.get("kind") not in FEATURE_KINDS:
        raise ValueError("feature kind")
    if feature.get("formula_digest") != formula_digest:
        raise ValueError("feature formula")
    if feature.get("capability_digest") != capability_digest:
        raise ValueError("feature capability")
    if not is_digest(feature.get("proof_digest")):
        raise ValueError("feature proof")
    if not string_set(feature.get("scope"), sorted_required=True):
        raise ValueError("feature scope")
    if feature["kind"] == "EXACT_OPEN_TRACE" and feature.get("advisory_only") is not True:
        raise ValueError("OPEN trace must be advisory only")
    payload = dict(feature)
    payload.pop("feature_digest", None)
    computed = "sha256:" + hashlib.sha256(canonical_json(payload)).hexdigest()
    if feature.get("feature_digest") != computed:
        raise ValueError("feature digest")
    return computed


def score(probe: Mapping[str, Any]) -> tuple[int, int, int, str]:
    return (
        probe["max_node_representation"],
        probe["total_representation"],
        probe["total_work_units"],
        probe["vtree_digest"],
    )


def validate(cert: Mapping[str, Any]) -> Result:
    try:
        canonical_json(cert)
        reject_enumeration(cert)
        if cert.get("schema") != DISCOVERY_SCHEMA:
            raise ValueError("schema")
        for field in (
            "formula_digest",
            "canonicalizer_digest",
            "capability_digest",
            "c039_contract_digest",
            "candidate_manifest_digest",
        ):
            if not is_digest(cert.get(field)):
                raise ValueError(field)
        variables = cert.get("variables")
        if not string_set(variables, sorted_required=True) or not variables:
            raise ValueError("variables")
        if cert.get("candidate_phase") != "FROZEN_BEFORE_PROBES":
            raise ValueError("candidate phase")
        if cert.get("depends_on_assignment_values") is not False:
            raise ValueError("branch-dependent discovery")

        budgets = cert.get("budgets")
        required_budget_fields = {
            "max_candidates",
            "max_feature_work_units",
            "max_candidate_generation_work_units",
            "max_probe_work_units",
            "max_total_work_units",
            "max_certificate_bytes",
        }
        if not isinstance(budgets, dict) or set(budgets) != required_budget_fields:
            raise ValueError("budgets")
        if any(not isinstance(budgets[k], int) or budgets[k] < 0 for k in budgets):
            raise ValueError("budget values")

        ledger = cert.get("work_ledger")
        required_ledger_fields = {
            "feature_work_units",
            "candidate_generation_work_units",
            "probe_work_units",
            "total_work_units",
            "certificate_bytes",
        }
        if not isinstance(ledger, dict) or set(ledger) != required_ledger_fields:
            raise ValueError("ledger")
        if any(not isinstance(ledger[k], int) or ledger[k] < 0 for k in ledger):
            raise ValueError("ledger values")

        features = cert.get("features")
        if not isinstance(features, list):
            raise ValueError("features")
        feature_digests = [
            validate_feature(f, cert["formula_digest"], cert["capability_digest"])
            for f in features
        ]
        if len(feature_digests) != len(set(feature_digests)):
            raise ValueError("duplicate features")

        candidates = cert.get("candidates")
        probes = cert.get("probes")
        if not isinstance(candidates, list) or not isinstance(probes, list):
            raise ValueError("candidate/probe lists")
        if len(candidates) != cert.get("frozen_candidate_count"):
            raise ValueError("candidate freeze mismatch")
        if len(candidates) > budgets["max_candidates"]:
            return Result(Terminal.OPEN_DISCOVERY_BUDGET, discovery_digest(cert), None)

        manifest_payload = []
        candidate_by_id: dict[str, dict[str, Any]] = {}
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict) or candidate.get("schema") != CANDIDATE_SCHEMA:
                raise ValueError("candidate schema")
            candidate_id = candidate.get("candidate_id")
            if candidate_id != f"candidate-{index:04d}" or candidate_id in candidate_by_id:
                raise ValueError("candidate order/id")
            if candidate.get("constructor") not in CONSTRUCTORS:
                raise ValueError("constructor")
            if not is_digest(candidate.get("constructor_digest")):
                raise ValueError("constructor digest")
            if not is_digest(candidate.get("generation_proof_digest")):
                raise ValueError("generation proof")
            if candidate.get("generated_before_probe") is not True:
                raise ValueError("adaptive candidate")
            if candidate.get("depends_on_assignment_values") is not False:
                raise ValueError("branch-dependent candidate")
            refs = candidate.get("feature_digests")
            if not isinstance(refs, list) or any(x not in feature_digests for x in refs):
                raise ValueError("candidate feature refs")
            tree_digest = validate_vtree(candidate.get("vtree"), variables)
            if candidate.get("vtree_digest") != tree_digest:
                raise ValueError("vtree digest")
            payload = dict(candidate)
            payload.pop("candidate_digest", None)
            computed_candidate_digest = "sha256:" + hashlib.sha256(
                canonical_json(payload)
            ).hexdigest()
            if candidate.get("candidate_digest") != computed_candidate_digest:
                raise ValueError("candidate digest")
            candidate_by_id[candidate_id] = candidate
            manifest_payload.append(candidate["candidate_digest"])

        computed_manifest_digest = "sha256:" + hashlib.sha256(
            canonical_json(manifest_payload)
        ).hexdigest()
        if cert["candidate_manifest_digest"] != computed_manifest_digest:
            raise ValueError("manifest digest")

        if len(probes) != len(candidates):
            raise ValueError("one probe per frozen candidate")
        probe_by_id: dict[str, dict[str, Any]] = {}
        for index, probe in enumerate(probes):
            if not isinstance(probe, dict) or probe.get("schema") != PROBE_SCHEMA:
                raise ValueError("probe schema")
            candidate_id = probe.get("candidate_id")
            if candidate_id != f"candidate-{index:04d}" or candidate_id in probe_by_id:
                raise ValueError("probe order/id")
            candidate = candidate_by_id.get(candidate_id)
            if candidate is None:
                raise ValueError("probe candidate")
            if probe.get("vtree_digest") != candidate["vtree_digest"]:
                raise ValueError("probe vtree")
            if probe.get("formula_digest") != cert["formula_digest"]:
                raise ValueError("probe formula")
            if probe.get("capability_digest") != cert["capability_digest"]:
                raise ValueError("probe capability")
            if probe.get("c039_contract_digest") != cert["c039_contract_digest"]:
                raise ValueError("probe contract")
            if probe.get("terminal") not in C039_TERMINALS:
                raise ValueError("probe terminal")
            if not is_digest(probe.get("c039_certificate_digest")):
                raise ValueError("probe certificate")
            if probe.get("full_compile") is not True:
                raise ValueError("partial probe")
            for field in (
                "max_node_representation",
                "total_representation",
                "total_work_units",
            ):
                if not isinstance(probe.get(field), int) or probe[field] < 0:
                    raise ValueError("probe ledger")
            probe_by_id[candidate_id] = probe

        if ledger["feature_work_units"] > budgets["max_feature_work_units"]:
            return Result(Terminal.OPEN_DISCOVERY_BUDGET, discovery_digest(cert), None)
        if ledger["candidate_generation_work_units"] > budgets[
            "max_candidate_generation_work_units"
        ]:
            return Result(Terminal.OPEN_DISCOVERY_BUDGET, discovery_digest(cert), None)
        if ledger["probe_work_units"] > budgets["max_probe_work_units"]:
            return Result(Terminal.OPEN_DISCOVERY_BUDGET, discovery_digest(cert), None)
        if ledger["total_work_units"] > budgets["max_total_work_units"]:
            return Result(Terminal.OPEN_DISCOVERY_BUDGET, discovery_digest(cert), None)
        if ledger["certificate_bytes"] > budgets["max_certificate_bytes"]:
            return Result(Terminal.OPEN_DISCOVERY_BUDGET, discovery_digest(cert), None)

        winners = [p for p in probes if p["terminal"] == "CLOSED_POLY"]
        selected = cert.get("selected_candidate_digest")
        declared_terminal = cert.get("terminal")
        if winners:
            best = min(winners, key=score)
            expected = candidate_by_id[best["candidate_id"]]["candidate_digest"]
            if selected != expected or declared_terminal != Terminal.VTREE_SELECTED_CERTIFIED.value:
                raise ValueError("selection/tie-break")
            return Result(
                Terminal.VTREE_SELECTED_CERTIFIED,
                discovery_digest(cert),
                best["vtree_digest"],
            )
        if selected is not None or declared_terminal != Terminal.OPEN_PORTFOLIO_EXHAUSTED.value:
            raise ValueError("open selection discipline")
        return Result(Terminal.OPEN_PORTFOLIO_EXHAUSTED, discovery_digest(cert), None)
    except (TypeError, ValueError, KeyError):
        return Result(Terminal.INVALID_DISCOVERY_CERTIFICATE, None, None)


async def route_vault(
    sink: OpenCoreVaultSink,
    result: Result,
    *,
    core: bytes,
    capability: bytes,
    certificate: bytes,
) -> str:
    if await sink.current_capability_digest() != capability:
        raise ValueError("capability mismatch")
    if result.terminal is Terminal.VTREE_SELECTED_CERTIFIED:
        await sink.record_poly(core, capability, certificate)
        return "record_poly"
    if result.terminal in OPEN:
        await sink.record_open(
            core,
            capability,
            {
                "schema": "janus.c040.open-trace.v1",
                "terminal": result.terminal.value,
                "discovery_digest": result.discovery_digest,
            },
        )
        return "record_open"
    raise ValueError("terminal not routable")


def feature(kind: str, label: str, formula: str, capability: str) -> dict[str, Any]:
    item = {
        "schema": FEATURE_SCHEMA,
        "kind": kind,
        "formula_digest": formula,
        "capability_digest": capability,
        "scope": ["x", "y"],
        "proof_digest": d(label + "-proof"),
        "advisory_only": kind == "EXACT_OPEN_TRACE",
    }
    item["feature_digest"] = "sha256:" + hashlib.sha256(canonical_json(item)).hexdigest()
    return item


def tree_xy(swapped: bool = False) -> dict[str, Any]:
    left, right = ("leaf-y", "leaf-x") if swapped else ("leaf-x", "leaf-y")
    return {
        "root": "root",
        "leaves": {"leaf-x": "x", "leaf-y": "y"},
        "internal_nodes": [{"id": "root", "left": left, "right": right}],
    }


def candidate(
    index: int,
    constructor: str,
    feature_digests: list[str],
    tree: dict[str, Any],
) -> dict[str, Any]:
    item = {
        "schema": CANDIDATE_SCHEMA,
        "candidate_id": f"candidate-{index:04d}",
        "constructor": constructor,
        "constructor_digest": d(constructor),
        "feature_digests": feature_digests,
        "generation_proof_digest": d(f"generation-{index}"),
        "generated_before_probe": True,
        "depends_on_assignment_values": False,
        "vtree": tree,
        "vtree_digest": "sha256:" + hashlib.sha256(canonical_json(tree)).hexdigest(),
    }
    payload = dict(item)
    item["candidate_digest"] = "sha256:" + hashlib.sha256(canonical_json(payload)).hexdigest()
    return item


def probe(
    candidate_item: Mapping[str, Any],
    formula: str,
    capability: str,
    contract: str,
    terminal: str,
    work: int,
    size: int,
    max_node: int,
) -> dict[str, Any]:
    return {
        "schema": PROBE_SCHEMA,
        "candidate_id": candidate_item["candidate_id"],
        "formula_digest": formula,
        "capability_digest": capability,
        "c039_contract_digest": contract,
        "vtree_digest": candidate_item["vtree_digest"],
        "full_compile": True,
        "terminal": terminal,
        "c039_certificate_digest": d(candidate_item["candidate_id"] + terminal),
        "max_node_representation": max_node,
        "total_representation": size,
        "total_work_units": work,
    }


def fixture(closed: bool = True) -> dict[str, Any]:
    formula, capability, contract = d("formula"), d("capability"), d("c039-contract")
    f1 = feature("EQUALITY_FOREST", "eq", formula, capability)
    f2 = feature("AFFINE_ROW_SUPPORT", "affine", formula, capability)
    c1 = candidate(0, "EQUALITY_CONTRACTED_V1", [f1["feature_digest"]], tree_xy())
    c2 = candidate(1, "AFFINE_SUPPORT_CLUSTER_V1", [f2["feature_digest"]], tree_xy(True))
    p1 = probe(c1, formula, capability, contract, "CLOSED_POLY" if closed else "OPEN_COMPOSITION", 20, 12, 8)
    p2 = probe(c2, formula, capability, contract, "CLOSED_POLY" if closed else "OPEN_LANGUAGE", 18, 12, 8)
    manifest = [c1["candidate_digest"], c2["candidate_digest"]]
    selected = c2["candidate_digest"] if closed else None
    cert = {
        "schema": DISCOVERY_SCHEMA,
        "formula_digest": formula,
        "canonicalizer_digest": d("canonicalizer"),
        "capability_digest": capability,
        "c039_contract_digest": contract,
        "variables": ["x", "y"],
        "candidate_phase": "FROZEN_BEFORE_PROBES",
        "depends_on_assignment_values": False,
        "features": [f1, f2],
        "candidates": [c1, c2],
        "frozen_candidate_count": 2,
        "candidate_manifest_digest": "sha256:" + hashlib.sha256(canonical_json(manifest)).hexdigest(),
        "probes": [p1, p2],
        "selected_candidate_digest": selected,
        "budgets": {
            "max_candidates": 8,
            "max_feature_work_units": 100,
            "max_candidate_generation_work_units": 100,
            "max_probe_work_units": 100,
            "max_total_work_units": 300,
            "max_certificate_bytes": 100000,
        },
        "work_ledger": {
            "feature_work_units": 12,
            "candidate_generation_work_units": 9,
            "probe_work_units": 38,
            "total_work_units": 59,
            "certificate_bytes": 6000,
        },
        "terminal": (
            Terminal.VTREE_SELECTED_CERTIFIED.value
            if closed
            else Terminal.OPEN_PORTFOLIO_EXHAUSTED.value
        ),
    }
    cert["discovery_digest"] = discovery_digest(cert)
    return cert


async def self_test() -> dict[str, Any]:
    checks = 0

    cert = fixture()
    a = validate(cert)
    reordered = dict(reversed(list(cert.items())))
    b = validate(reordered)
    assert a.terminal is Terminal.VTREE_SELECTED_CERTIFIED
    assert a.discovery_digest == b.discovery_digest
    checks += 1

    # Deterministic tie-break picks lower work candidate 1.
    assert a.selected_vtree_digest == cert["candidates"][1]["vtree_digest"]
    checks += 1

    item = fixture()
    item["candidates"][0]["generation_proof_digest"] = None
    assert validate(item).terminal is Terminal.INVALID_DISCOVERY_CERTIFICATE
    checks += 1

    item = fixture()
    item["depends_on_assignment_values"] = True
    assert validate(item).terminal is Terminal.INVALID_DISCOVERY_CERTIFICATE
    checks += 1

    item = fixture()
    item["candidates"][1]["generated_before_probe"] = False
    assert validate(item).terminal is Terminal.INVALID_DISCOVERY_CERTIFICATE
    checks += 1

    item = fixture()
    item["candidates"][0]["vtree"]["leaves"]["leaf-y"] = "x"
    assert validate(item).terminal is Terminal.INVALID_DISCOVERY_CERTIFICATE
    checks += 1

    item = fixture()
    open_feature = feature("EXACT_OPEN_TRACE", "open", item["formula_digest"], d("stale-cap"))
    item["features"].append(open_feature)
    assert validate(item).terminal is Terminal.INVALID_DISCOVERY_CERTIFICATE
    checks += 1

    item = fixture(False)
    assert validate(item).terminal is Terminal.OPEN_PORTFOLIO_EXHAUSTED
    checks += 1

    item = fixture()
    item["budgets"]["max_candidates"] = 1
    assert validate(item).terminal is Terminal.OPEN_DISCOVERY_BUDGET
    checks += 1

    item = fixture()
    item["work_ledger"]["total_work_units"] = 301
    assert validate(item).terminal is Terminal.OPEN_DISCOVERY_BUDGET
    checks += 1

    item = fixture()
    item["features"][0]["truth_table"] = [0, 1]
    assert validate(item).terminal is Terminal.INVALID_DISCOVERY_CERTIFICATE
    checks += 1

    capability = db(d("capability"))
    sink = InMemoryVaultAdapter(capability)
    selected = validate(fixture())
    opened = validate(fixture(False))
    core, certificate = db(d("core")), db(d("certificate"))
    assert await route_vault(sink, selected, core=core, capability=capability, certificate=certificate) == "record_poly"
    assert await route_vault(sink, opened, core=core, capability=capability, certificate=certificate) == "record_open"
    blocked = False
    try:
        await route_vault(sink, opened, core=core, capability=db(d("wrong")), certificate=certificate)
    except ValueError:
        blocked = True
    assert blocked and len(sink.poly_records) == len(sink.open_records) == 1
    checks += 1

    return {
        "status": "PASS",
        "canonical_id": "C040",
        "stage": "SPECIFICATION_ONLY",
        "acceptance_checks": checks,
        "candidate_manifest_frozen_before_probes": True,
        "assignment_independent_vtree_required": True,
        "one_full_c039_probe_per_candidate": True,
        "certified_closed_candidate_required": True,
        "deterministic_cost_tie_break": True,
        "all_open_returns_open_portfolio_exhausted": True,
        "exact_open_trace_advisory_only": True,
        "hidden_enumeration_rejected": True,
        "vault_routing_capability_locked": True,
        "universal_candidate_completeness_claimed": False,
        "p_vs_np": "OPEN",
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
