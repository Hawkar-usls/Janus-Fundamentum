#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


SCHEMA_IN = "TSEITIN_EXPANDER_SEARCH_SOURCE_V1"
SCHEMA_CAND = "PROOF_CARRYING_AFFINE_PRIORITY_SEARCH_V1"


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(source_path: Path, candidate_path: Path):
    source = json.loads(source_path.read_text())
    cand = json.loads(candidate_path.read_text())
    if source["schema"] != SCHEMA_IN:
        raise AssertionError("wrong source schema")
    if cand["schema"] != SCHEMA_CAND:
        raise AssertionError("wrong candidate schema")
    if cand["source_sha256"] != file_sha256(source_path):
        raise AssertionError("candidate/source hash mismatch")

    d = cand["derivation"]
    assert d["special_function_recognizer_used"] is False
    assert d["reference_import_used"] is False
    assert d["SAT_solver_calls"] == 0
    assert d["generic_SK0LEM_VALID_calls"] == 0
    assert d["generic_DAG_tautology_calls"] == 0
    assert d["truth_table_enumeration"] is False
    assert d["boundary_assignment_enumeration"] is False
    assert d["old_tseitin_artifact_import_used"] is False
    assert d["spectral_metadata_used"] is False
    assert d["calculus_mutation_used"] is False

    start = time.perf_counter_ns()
    nodes = cand["proof_nodes"]
    if not isinstance(nodes, dict) or not nodes:
        raise AssertionError("empty proof DAG")

    allowed = {"CONST", "AFFINE_XOR", "GUARDED_ITE"}
    content_to_pid = {}
    for pid, node in nodes.items():
        rule = node.get("rule")
        assert rule in allowed
        key = json.dumps(node, sort_keys=True, separators=(",", ":"))
        assert key not in content_to_pid, "proof DAG is not hash-consed"
        content_to_pid[key] = pid

    def node_id(payload):
        key = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        assert key in content_to_pid, f"missing proof node: {payload}"
        return content_to_pid[key]

    vertices = source["witness_decode_order"]
    vertex_rec = {x["vertex_id"]: x for x in source["vertices"]}
    n = len(vertices)
    assert n > 0 and n & (n - 1) == 0
    assert set(vertices) == set(vertex_rec)
    assert len(source["witness_bits"]) == int(math.log2(n))
    assert cand["encoding"] == "LSB_FIRST_VERTEX_INDEX"

    incident = defaultdict(list)
    edge_counts = Counter()
    for e in source["edges"]:
        y = e["boundary_var"]
        incident[e["u"]].append(y)
        incident[e["v"]].append(y)
        edge_counts[y] += 2

    dp = cand["domain_proof"]
    assert dp["proof_object_class"] == "AFFINE_XOR_SUM_CERTIFICATE"
    assert dp["conclusion"] == "DOMAIN_TRUE"
    assert dp["calculus_rule_extension_used"] is False
    guards = dp["terms_by_vertex"]
    assert set(guards) == set(vertices)

    used = set()
    verifier_visits = 0
    for v in vertices:
        verifier_visits += 1
        expected = {
            "rule": "AFFINE_XOR",
            "constant": int(vertex_rec[v]["charge"]),
            "support": sorted(incident[v]),
        }
        pid = guards[v]
        assert pid in nodes
        assert nodes[pid] == expected
        used.add(pid)

    # Symbolic domain proof: XOR all local violation equations.
    # Every edge variable appears twice and therefore cancels in GF(2);
    # odd total charge leaves constant 1.
    support_parity = Counter()
    charge_xor = 0
    for v in vertices:
        node = nodes[guards[v]]
        charge_xor ^= int(node["constant"])
        for y in node["support"]:
            support_parity[y] ^= 1
    assert charge_xor == 1
    assert all(parity == 0 for parity in support_parity.values())
    assert set(support_parity) == set(edge_counts)
    assert all(count == 2 for count in edge_counts.values())
    assert dp["observed_charge_xor"] == 1
    assert dp["normal_form_target"] == {"constant": 1, "support": []}
    assert cand["domain"] == {"class": "TRUE_BY_ODD_CHARGE_XOR_CANCELLATION"}

    const_pid = {}
    for value in (0, 1):
        payload = {"rule": "CONST", "value": value}
        key = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        if key in content_to_pid:
            const_pid[value] = content_to_pid[key]

    roots = cand["witness_roots"]
    assert set(roots) == set(source["witness_bits"])
    for bit_index, bit_name in enumerate(source["witness_bits"]):
        leaf_value = ((n - 1) >> bit_index) & 1
        assert leaf_value in const_pid
        current = const_pid[leaf_value]
        used.add(current)
        for index in range(n - 2, -1, -1):
            verifier_visits += 1
            true_value = (index >> bit_index) & 1
            assert true_value in const_pid
            true_pid = const_pid[true_value]
            used.add(true_pid)
            if true_pid == current:
                continue
            payload = {
                "rule": "GUARDED_ITE",
                "guard": guards[vertices[index]],
                "true_child": true_pid,
                "false_child": current,
            }
            current = node_id(payload)
            used.add(current)
        assert roots[bit_name] == current

    # All candidate proof nodes must be justified and reachable either from
    # the exact domain proof or from the witness roots.
    stack = list(roots.values())
    while stack:
        pid = stack.pop()
        if pid in used:
            node = nodes[pid]
        else:
            assert pid in nodes
            used.add(pid)
            node = nodes[pid]
        if node["rule"] == "GUARDED_ITE":
            assert node["guard"] in nodes
            assert nodes[node["guard"]]["rule"] == "AFFINE_XOR"
            used.add(node["guard"])
            stack.extend([node["true_child"], node["false_child"]])
    assert used == set(nodes), "candidate contains unexplained or unreachable proof nodes"

    metrics = cand["metrics"]
    actual_guard_nodes = sum(1 for p in nodes.values() if p["rule"] == "AFFINE_XOR")
    actual_ite_nodes = sum(1 for p in nodes.values() if p["rule"] == "GUARDED_ITE")
    selector_steps = len(source["witness_bits"]) * (n - 1)
    expected_state_visits = n + selector_steps
    naive_unshared = n + len(source["witness_bits"]) * (2 * n - 1)
    expected_bytes = len(
        canonical_bytes(
            {
                "domain_proof": cand["domain_proof"],
                "witness_roots": cand["witness_roots"],
                "proof_nodes": nodes,
            }
        )
    )
    assert metrics["S_synth_DAG_nodes"] == len(nodes)
    assert metrics["S_synth_DAG_bytes"] == expected_bytes
    assert metrics["max_live_shared_nodes"] == len(nodes)
    assert metrics["constructor_state_visits"] == expected_state_visits
    assert metrics["derived_affine_guard_count"] == actual_guard_nodes == n
    assert metrics["guarded_ITE_node_count"] == actual_ite_nodes
    assert metrics["naive_unshared_node_occurrences"] == naive_unshared
    expected_ratio = naive_unshared / max(1, len(nodes))
    assert abs(metrics["sharing_ratio_before_after_hashcons"] - expected_ratio) < 1e-12

    elapsed = time.perf_counter_ns() - start
    return {
        "verdict": "PASS_INDEPENDENT_AFFINE_PRIORITY_PROOF_CARRYING_WITNESS",
        "T_verify_ns": elapsed,
        "verifier_node_visits": verifier_visits,
        "domain_verified": "TRUE_BY_SYMBOLIC_ODD_CHARGE_XOR_CANCELLATION",
        "witness_verified": "CANONICAL_PRIORITY_SELECTION_OF_A_VIOLATED_VERTEX",
        "reference_DAG_read": False,
        "candidate_constructor_imported": False,
        "semantic_truth_table_used": False,
        "boundary_assignment_enumeration": False,
        "generic_validity_used": False,
    }


def main(source_s, candidate_s, out_s):
    result = verify(Path(source_s), Path(candidate_s))
    Path(out_s).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: independent_verify.py SOURCE.json CANDIDATE.json OUT.json")
    main(sys.argv[1], sys.argv[2], sys.argv[3])
