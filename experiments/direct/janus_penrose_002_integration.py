#!/usr/bin/env python3
"""JANUS-PENROSE-002: cross-contour causal DAG and proof-bound integration.

Source CNF fans out independently into (1) UFR solver/certificate/replay and
(2) reversible Deutsch oracle/schedule/sampled truth checks. Only independently
replayed UFR isomorphism edges are allowed to cross into the oracle-covariance
test; the two branches join at a final evidence gate.

All edges denote STRICT causal event precedence, not physical register reuse.
The same Penrose-001 DAG validator rejects circular/future dependencies.
No quantum hardware, SAT speedup, or production C023 replacement is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import random
from typing import Any, Iterable

from janus_deutsch_002 import DirectOracle
from janus_deutsch_003 import BlockOracle, choose_block_size
from janus_penrose_001 import analyze_strict_precedence, audit_reversible_schedule
from janus_tear_policy0a_masked_tseitin import canonical_cnf
from janus_ufr_001 import verify_renaming, verify_model
from janus_ufr_001_adversarial import fixtures
from janus_ufr_001_certified_fc import (
    UFRFCTracePolicy, dump_ufr_json, load_ufr_json, replay_ufr_json,
)

STAGES = (
    "SOURCE", "UFR_PRODUCE", "UFR_CERTIFICATE", "INDEPENDENT_REPLAY",
    "ORACLE_COMPILE", "SCHEDULE_AUDIT", "ORACLE_TRUTH",
    "UFR_ORACLE_COVARIANCE", "FINAL_GATE",
)
REQUIRED_EDGES = (
    ("SOURCE", "UFR_PRODUCE"),
    ("UFR_PRODUCE", "UFR_CERTIFICATE"),
    ("UFR_CERTIFICATE", "INDEPENDENT_REPLAY"),
    ("SOURCE", "INDEPENDENT_REPLAY"),
    ("SOURCE", "ORACLE_COMPILE"),
    ("ORACLE_COMPILE", "SCHEDULE_AUDIT"),
    ("ORACLE_COMPILE", "ORACLE_TRUTH"),
    ("SOURCE", "ORACLE_TRUTH"),
    ("INDEPENDENT_REPLAY", "UFR_ORACLE_COVARIANCE"),
    ("ORACLE_COMPILE", "UFR_ORACLE_COVARIANCE"),
    ("INDEPENDENT_REPLAY", "FINAL_GATE"),
    ("SCHEDULE_AUDIT", "FINAL_GATE"),
    ("ORACLE_TRUTH", "FINAL_GATE"),
    ("UFR_ORACLE_COVARIANCE", "FINAL_GATE"),
)
ALLOWED_FIXTURES = (
    "TSEITIN_K4_NONAFFINE_WRAPPED",
    "RENAMED_TWIN_POSITIVE_CONTROL",
    "MAJ3_K4",
)


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(data: Any) -> str:
    return sha256(stable_json(data).encode("utf-8")).hexdigest()


def get_fixture(name: str):
    if name not in ALLOWED_FIXTURES:
        raise ValueError("fixture not approved for cross-contour replay")
    candidates = dict(fixtures(extended=name == "MAJ3_K4"))
    rows, n = candidates[name]
    return canonical_cnf(rows), n


def source_id(cnf, n: int) -> str:
    return digest({"variable_count": n, "cnf": cnf})


def check_dependencies(edges: Iterable[tuple[str, str]] = REQUIRED_EDGES):
    selected = tuple(tuple(x) for x in edges)
    if len(selected) != len(set(selected)):
        raise AssertionError("duplicate edges are not allowed")
    if not set(REQUIRED_EDGES).issubset(selected):
        raise AssertionError("missing mandatory dependency")
    if any(a not in STAGES or b not in STAGES for a, b in selected):
        raise AssertionError("unknown stage in dependency")
    schedule = analyze_strict_precedence(STAGES, selected)
    if not schedule.consistent:
        raise AssertionError(
            "Penrose-like circular dependency: " + " -> ".join(schedule.cycle_witness))
    h = dict(schedule.ranks)
    if any(h[a] >= h[b] for a, b in selected):
        raise AssertionError("inconsistent global event ranks")
    # UFR proof must not depend on oracle output; no pre-verification evidence
    # may flow backwards from the final gate into the original computation.
    if any(a == "FINAL_GATE" or b == "SOURCE" for a, b in selected):
        raise AssertionError("source/final trust boundary violation")
    return schedule


def sampled_inputs(n: int, count: int = 32, seed: int = 574):
    if type(n) is not int or not (1 <= n <= 64) or not (0 <= count <= 128):
        raise ValueError("invalid bounded sampling contract")
    if n <= 6:
        return tuple(range(1 << n))
    rng = random.Random(seed)
    return tuple([0, (1 << n) - 1] + [rng.getrandbits(n) for _ in range(count)])


def _transport_bits(x: int, mapping: dict[int, int]) -> int:
    out = 0
    for old, new in mapping.items():
        if x & (1 << (old - 1)):
            out |= 1 << (new - 1)
    return out


def inspect_proof_and_oracle(name: str, wire: str, *, sample_count: int = 32,
                             max_iso_oracle_edges: int = 8) -> dict:
    """Independently reconstruct all *decisive* evidence from trusted fixture.

    Does NOT trust producer-side 'answer', stage summaries, or dependencies.
    Any UFR result is established only by independent serialized replay.
    """
    root, n = get_fixture(name)
    proof = load_ufr_json(wire)
    replayed_answer = replay_ufr_json(root, n, wire)
    calls, states = proof["calls"], proof["states"]
    iso = [(call_id, call) for call_id, call in calls.items()
           if call.get("terminal") == "ISOMORPHIC_CACHE_HIT"]
    direct = DirectOracle.compile(root, n, "SAT")
    block = choose_block_size(direct)
    schedule = audit_reversible_schedule(block)
    if not schedule.passed or schedule.events != block.logical_mcx_gates:
        raise AssertionError("reversible oracle scheduling was not independently approved")

    samples = sampled_inputs(n, sample_count)
    for x in samples:
        assignment = {v: bool(x & (1 << (v-1))) for v in range(1, n+1)}
        independently = verify_model(root, assignment, "SAT")
        if direct.evaluate(x) != independently or block.evaluate(x) != independently:
            raise AssertionError("source/proof vs reversible oracle predicate mismatch")

    checked_iso = 0
    for call_id, call in iso[:max_iso_oracle_edges]:
        target_id = call["cache_target"]
        if target_id not in states:
            raise AssertionError("isomorphic target not present in serialized trace")
        source_residual, target_residual = call["key"], states[target_id]["key"]
        renaming = dict(call["renaming"])
        if not verify_renaming(source_residual, target_residual, renaming, "SAT"):
            raise AssertionError("untrusted producer UFR map is not a literal bijection")
        left, right = DirectOracle.compile(source_residual, n), DirectOracle.compile(target_residual, n)
        for x in sampled_inputs(n, 8, seed=574 + checked_iso):
            if left.evaluate(x) != right.evaluate(_transport_bits(x, renaming)):
                raise AssertionError("UFR mapping changed reversible residual semantics")
        checked_iso += 1

    # Strong absence property: don't silently claim any UFR iso hit if
    # no completed state is available, and never mix proof from another CNF.
    if replayed_answer is not proof["calls"][proof["root_call"]]["result"]:
        raise AssertionError("independent replay and producer answer disagree")

    return {
        "SOURCE": {"source_sha256": source_id(root, n), "variables": n,
                   "clauses": len(root), "fixture": name},
        "UFR_PRODUCE": {"root_answer": replayed_answer, "calls": len(calls),
                        "states": len(states), "iso_hits": len(iso)},
        "UFR_CERTIFICATE": {"wire_sha256": sha256(wire.encode()).hexdigest(),
                            "bytes": len(wire.encode()), "schema": proof["schema"]},
        "INDEPENDENT_REPLAY": {"verified": True, "answer": replayed_answer,
                               "trusted_source_sha256": source_id(root, n)},
        "ORACLE_COMPILE": {"blocks": block.blocks, "block_size": block.block_size,
                           "qubits_estimate": block.qubit_estimate,
                           "maximum_controls": block.maximum_controls,
                           "logical_mcx_gates": block.logical_mcx_gates},
        "SCHEDULE_AUDIT": {"passed": schedule.passed,
                           "events": schedule.events,
                           "dependency_count": schedule.strict_event_schedule.constraint_count},
        "ORACLE_TRUTH": {"independent_checks": len(samples), "all_match": True},
        "UFR_ORACLE_COVARIANCE": {"verified_iso_edges_in_proof": len(iso),
                                  "oracle_checked_iso_edges": checked_iso,
                                  "all_checked_maps_valid": True},
        "FINAL_GATE": {"accepted": True, "answer": replayed_answer,
                       "classical_simulator_only": True,
                       "production_c023_unchanged": True},
    }


def build_receipts(payloads: dict, edges: tuple[tuple[str, str], ...]):
    """Tamper-evident DAG: receipt binds payload and *all parent* receipts."""
    check_dependencies(edges)
    receipts = {}
    for stage in STAGES:
        parents = {parent: receipts[parent]
                   for parent, child in edges if child == stage}
        receipts[stage] = digest({"stage": stage, "payload": payloads[stage],
                                  "parents": parents})
    return receipts


def build_bundle(name: str, *, samples: int = 32, max_iso_edges: int = 8):
    root, n = get_fixture(name)
    policy = UFRFCTracePolicy(state_cap=3000, max_variables=24,
                              max_candidates=120, max_literals=120)
    result, root_call = policy.solve(root, n)
    if root_call is None or result.answer is None:
        raise AssertionError("inconclusive or root-affine non-replayed proof")
    wire = dump_ufr_json(policy, root_call)
    payloads = inspect_proof_and_oracle(
        name, wire, sample_count=samples, max_iso_oracle_edges=max_iso_edges)
    if payloads["FINAL_GATE"]["answer"] is not result.answer:
        raise AssertionError("actual solver result differs from independent replay")
    edges = tuple(REQUIRED_EDGES)
    report = {
        "schema": "JANUS-PENROSE-002-CROSS-CONTOUR-V1",
        "fixture": name, "sampling": samples, "max_iso_oracle_edges": max_iso_edges,
        "stage_order": list(STAGES), "dependencies": [list(e) for e in edges],
        "global_consistency": check_dependencies(edges).as_dict(),
        "stage_payloads": payloads,
        "stage_receipts": build_receipts(payloads, edges),
        "proof_file_sha256": sha256(wire.encode()).hexdigest(),
        "claim_boundary": "Research-only; UFR replay authenticates Boolean output, reversible oracle checks finite assignments; no quantum speedup or new UNSAT theorem",
    }
    verify_bundle(report, wire)
    return report, wire


def verify_bundle(report: dict, wire: str) -> bool:
    """Independent verdict; reject forged manifest, proof, and stage receipts."""
    if report.get("schema") != "JANUS-PENROSE-002-CROSS-CONTOUR-V1":
        raise AssertionError("unknown manifest schema")
    if report.get("stage_order") != list(STAGES):
        raise AssertionError("stage order omitted/reordered")
    edges = tuple(tuple(e) for e in report["dependencies"])
    independent_dag = check_dependencies(edges)
    if report["global_consistency"] != independent_dag.as_dict():
        raise AssertionError("attested DAG certificate differs from reconstructed graph")
    if report["proof_file_sha256"] != sha256(wire.encode()).hexdigest():
        raise AssertionError("proof bytes tampered/mismatched")
    independent_payloads = inspect_proof_and_oracle(
        report["fixture"], wire, sample_count=report["sampling"],
        max_iso_oracle_edges=report["max_iso_oracle_edges"])
    if report["stage_payloads"] != independent_payloads:
        raise AssertionError("stage payload differs from independent evidence")
    if report["stage_receipts"] != build_receipts(independent_payloads, edges):
        raise AssertionError("causal receipt chain is invalid")
    return True
