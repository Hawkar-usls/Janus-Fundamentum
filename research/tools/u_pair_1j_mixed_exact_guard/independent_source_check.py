#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, deque
from pathlib import Path

import numpy as np

DEGREE = 3
THRESHOLD = 0.99
SERIES = (16, 32, 64, 128, 256)
ATOM_SUPPORT_SIZE = 2
PREREG_COMMIT = "6097218416d0a8a244cf526d01ba8a00fc0ba1fa"


def sha256_path(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_one(p: Path, row: dict):
    obj = json.loads(p.read_text())
    n = obj["n_vertices"]
    assert n == row["n"] and n in SERIES
    assert obj["schema"] == "CONNECTED_MIXED_AFFINE_OR3_SOURCE_V1"
    assert obj["target"] == "CONNECTED_MIXED_AFFINE_OR3_EXPANDER_INTERLEAVE"
    assert obj["attack_name"] == "SYNTHESIS_OF_MIXED_EXACT_GUARDS"
    assert obj["degree"] == DEGREE
    assert n & (n - 1) == 0
    assert len(obj["witness_bits"]) == int(math.log2(n))

    vids = [v["vertex_id"] for v in obj["vertices"]]
    assert len(vids) == n and len(set(vids)) == n
    assert obj["witness_decode_order"] == vids
    charges = {v["vertex_id"]: int(v["charge"]) for v in obj["vertices"]}
    assert set(charges.values()) <= {0, 1}
    assert sum(charges.values()) % 2 == 1

    edges = obj["edges"]
    assert len(edges) == 3 * n // 2 == obj["n_edges"]
    degree = {v: 0 for v in vids}
    seen_edges = set()
    bvars = set()
    incident_bvars = {v: set() for v in vids}
    A = np.zeros((n, n), dtype=float)
    pos = {v: i for i, v in enumerate(vids)}
    adjacency = {v: [] for v in vids}
    for e in edges:
        u, v = e["u"], e["v"]
        assert u in degree and v in degree and u != v
        key = tuple(sorted((u, v)))
        assert key not in seen_edges
        seen_edges.add(key)
        y = e["boundary_var"]
        assert y not in bvars
        bvars.add(y)
        degree[u] += 1
        degree[v] += 1
        incident_bvars[u].add(y)
        incident_bvars[v].add(y)
        adjacency[u].append(v)
        adjacency[v].append(u)
        A[pos[u], pos[v]] = A[pos[v], pos[u]] = 1.0
    assert all(x == DEGREE for x in degree.values())

    q = deque([vids[0]])
    reached = {vids[0]}
    while q:
        u = q.popleft()
        for v in adjacency[u]:
            if v not in reached:
                reached.add(v)
                q.append(v)
    assert len(reached) == n

    vals = np.sort(np.linalg.eigvalsh(A))[::-1]
    ratio = float(vals[1] / DEGREE)
    assert ratio <= THRESHOLD
    assert abs(ratio - float(obj["qualification_record"]["lambda2_over_degree"])) < 1e-10
    assert obj["qualification_record"]["finite_spectral_stress_gate_pass"] is True
    assert obj["source_provenance"]["graph_selection_uses_spectral_metric"] is False
    assert obj["source_provenance"]["constructor_existed_when_source_generated"] is False
    assert obj["source_provenance"]["resampling_after_constructor_observation"] is False

    atoms = {a["atom_id"]: a for a in obj["affine_atoms"]}
    assert len(atoms) == 3 * n // 2
    for a in atoms.values():
        assert int(a["constant"]) in (0, 1)
        assert len(a["support"]) == ATOM_SUPPORT_SIZE
        assert len(set(a["support"])) == ATOM_SUPPORT_SIZE
        assert set(a["support"]) <= bvars

    blocks = {o["or3_id"]: o for o in obj["or3_blocks"]}
    assert len(blocks) == n // 2
    for o in blocks.values():
        assert len(o["atom_ids"]) == 3
        assert len(set(o["atom_ids"])) == 3
        assert set(o["atom_ids"]) <= set(atoms)
        assert o["literal_polarities"] == [1, 1, 1]
        supports = [set(atoms[aid]["support"]) for aid in o["atom_ids"]]
        assert supports[0].isdisjoint(supports[1])
        assert supports[0].isdisjoint(supports[2])
        assert supports[1].isdisjoint(supports[2])

    pair_records = obj["pairing"]
    assert len(pair_records) == n // 2
    paired_vertices = []
    used_blocks = set()
    block_vertices = {}
    for rec in pair_records:
        assert len(rec["vertices"]) == 2
        assert len(set(rec["vertices"])) == 2
        assert set(rec["vertices"]) <= set(vids)
        oid = rec["or3_id"]
        assert oid in blocks and oid not in used_blocks
        used_blocks.add(oid)
        paired_vertices.extend(rec["vertices"])
        block_vertices[oid] = list(rec["vertices"])

        o_support = set()
        for aid in blocks[oid]["atom_ids"]:
            o_support.update(atoms[aid]["support"])
        for v in rec["vertices"]:
            assert o_support.isdisjoint(incident_bvars[v])
    assert Counter(paired_vertices) == Counter({v: 1 for v in vids})
    assert used_blocks == set(blocks)

    interleave = obj["candidate_interleave"]
    assert len(interleave) == n
    interleave_map = {}
    block_ref_counts = Counter()
    for rec in interleave:
        v, oid = rec["vertex_id"], rec["or3_id"]
        assert v in vids and oid in blocks
        assert v not in interleave_map
        assert v in block_vertices[oid]
        interleave_map[v] = oid
        block_ref_counts[oid] += 1
    assert set(interleave_map) == set(vids)
    assert all(block_ref_counts[oid] == 2 for oid in blocks)

    anti = obj["anti_cheat"]
    assert anti["precomputed_mixed_guard_nodes_present"] is False
    assert anti["precomputed_or3_output_nodes_present"] is False
    assert anti["precomputed_affine_substitution_into_or3_present"] is False
    assert anti["explicit_witness_output_node_present"] is False
    assert anti["old_connected_mixed_result_import_present"] is False
    assert anti["old_tseitin_candidate_import_present"] is False

    # Independent mixed-incidence connectivity check.
    inc = {}
    def link(a, b):
        inc.setdefault(a, set()).add(b)
        inc.setdefault(b, set()).add(a)

    for e in edges:
        link("V:" + e["u"], "Y:" + e["boundary_var"])
        link("V:" + e["v"], "Y:" + e["boundary_var"])
    for aid, a in atoms.items():
        for y in a["support"]:
            link("A:" + aid, "Y:" + y)
    for oid, o in blocks.items():
        for aid in o["atom_ids"]:
            link("O:" + oid, "A:" + aid)
        for v in block_vertices[oid]:
            link("O:" + oid, "V:" + v)

    start = "V:" + vids[0]
    dq = deque([start])
    inc_reached = {start}
    while dq:
        x = dq.popleft()
        for y in inc.get(x, ()):
            if y not in inc_reached:
                inc_reached.add(y)
                dq.append(y)
    assert len(inc_reached) == len(inc)

    # Symbolic totality ingredients, without synthesizing any mixed guard:
    # XOR_v A_v = 1 by odd charge + double edge occurrence.
    # Every raw OR3 block is referenced exactly twice, so XOR_v O_pair(v)=0.
    edge_occurrence = Counter()
    for v in vids:
        edge_occurrence.update(incident_bvars[v])
    assert all(edge_occurrence[y] == 2 for y in bvars)
    assert sum(charges.values()) % 2 == 1
    assert all(block_ref_counts[oid] == 2 for oid in blocks)

    return {
        "n": n,
        "n_edges": len(edges),
        "charge_xor": 1,
        "lambda2_over_degree": ratio,
        "pair_count": len(pair_records),
        "or3_block_count": len(blocks),
        "affine_atom_count": len(atoms),
        "source_sha256": sha256_path(p),
        "simple_3_regular_connected": True,
        "mixed_incidence_connected": True,
        "all_or3_atom_supports_pairwise_disjoint": True,
        "all_linked_or3_supports_disjoint_from_base_affine_supports": True,
        "every_or3_block_referenced_exactly_twice": True,
        "symbolic_domain_parity_ingredients_valid": True,
    }


def main(srcdir_s: str, out_s: str, freeze_sha: str):
    src = Path(srcdir_s)
    manifest = json.loads((src / "source_manifest.json").read_text())
    assert manifest["prereg_commit"] == PREREG_COMMIT
    assert manifest["selection_firewall"]["constructor_not_implemented_at_source_freeze"] is True
    assert manifest["selection_firewall"]["mixed_guard_not_precomputed"] is True
    assert manifest["selection_firewall"]["or3_output_not_precomputed"] is True
    assert manifest["selection_firewall"]["spectral_metric_used_for_graph_selection"] is False
    assert [r["n"] for r in manifest["series"]] == list(SERIES)

    rows = []
    for row in manifest["series"]:
        p = src / row["file"]
        assert sha256_path(p) == row["sha256"]
        got = check_one(p, row)
        assert got["source_sha256"] == row["sha256"]
        rows.append(got)

    result = {
        "artifact_id": "JANUS-U-PAIR-1J-CONNECTED-MIXED-AFFINE-OR3-INDEPENDENT-SOURCE-CHECK-2026-09-18-v1.0",
        "source_freeze_commit": freeze_sha,
        "prereg_commit": manifest["prereg_commit"],
        "checks": {
            "all_sha256_match_manifest": True,
            "all_simple_3_regular_connected": True,
            "all_odd_charge": True,
            "all_finite_spectral_stress_gate_pass": True,
            "all_mixed_incidence_connected": True,
            "all_or3_blocks_raw_without_output_nodes": True,
            "all_affine_atoms_raw": True,
            "all_or3_atom_supports_pairwise_disjoint": True,
            "all_linked_or3_supports_disjoint_from_base_affine_supports": True,
            "every_or3_block_referenced_exactly_twice": True,
            "symbolic_domain_parity_ingredients_valid": True,
            "no_precomputed_mixed_guards": True,
            "no_explicit_witness_output_nodes": True,
            "constructor_not_implemented_at_source_freeze": True,
        },
        "rows": rows,
        "verdict": "PASS_SOURCE_FREEZE_INDEPENDENT_CHECK",
        "scientific_firewall": {
            "hostile_synthesis_not_run": True,
            "killer_control_not_run": True,
            "finite_spectral_gate_is_not_asymptotic_expander_theorem": True,
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }
    Path(out_s).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: independent_source_check.py SRC_DIR OUT_JSON SOURCE_FREEZE_SHA"
        )
    main(sys.argv[1], sys.argv[2], sys.argv[3])
