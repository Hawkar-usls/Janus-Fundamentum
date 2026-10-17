#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

SERIES = (16, 32, 64, 128, 256)
DEGREE = 3
THRESHOLD = 0.99
ATOM_SUPPORT_SIZE = 2
TAG = "U_PAIR_1J_CONNECTED_MIXED_AFFINE_OR3_EXACT_GUARD_2026_09_18"
PREREG_COMMIT = "6097218416d0a8a244cf526d01ba8a00fc0ba1fa"


def h16(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def seed_int(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:16], 16)


def generate_3_regular(n: int):
    for attempt in range(100000):
        rnd = random.Random(seed_int(f"{TAG}|GRAPH|n={n}|attempt={attempt}"))
        stubs = [v for v in range(n) for _ in range(DEGREE)]
        rnd.shuffle(stubs)
        seen = set()
        edges = []
        ok = True
        for i in range(0, len(stubs), 2):
            a, b = stubs[i], stubs[i + 1]
            if a == b:
                ok = False
                break
            e = tuple(sorted((a, b)))
            if e in seen:
                ok = False
                break
            seen.add(e)
            edges.append(e)
        if not ok:
            continue
        adj = [[] for _ in range(n)]
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)
        if any(len(xs) != DEGREE for xs in adj):
            continue
        stack = [0]
        reached = {0}
        for x in stack:
            for y in adj[x]:
                if y not in reached:
                    reached.add(y)
                    stack.append(y)
        if len(reached) != n:
            continue
        return sorted(edges), attempt
    raise RuntimeError("failed deterministic simple connected 3-regular generation")


def lambda2_ratio(n: int, edges):
    A = np.zeros((n, n), dtype=float)
    for a, b in edges:
        A[a, b] = A[b, a] = 1.0
    vals = np.sort(np.linalg.eigvalsh(A))[::-1]
    return float(vals[1] / DEGREE)


def charge_bits(n: int):
    bits = [seed_int(f"{TAG}|CHARGE|n={n}|v={v}") & 1 for v in range(n)]
    adjusted = False
    if sum(bits) % 2 == 0:
        bits[0] ^= 1
        adjusted = True
    return bits, adjusted


def deterministic_pairs(n: int):
    order = list(range(n))
    random.Random(seed_int(f"{TAG}|PAIRING|n={n}")).shuffle(order)
    return [(order[i], order[i + 1]) for i in range(0, n, 2)]


def write_source(n: int, outdir: Path):
    edges, attempt = generate_3_regular(n)
    ratio = lambda2_ratio(n, edges)
    charge, adjusted = charge_bits(n)

    vids = [f"mv_{h16(f'{TAG}|VERTEX|n={n}|v={v}')}" for v in range(n)]
    edge_records = []
    incident_edge_indices = {v: set() for v in range(n)}
    for j, (a, b) in enumerate(edges):
        bvar = f"y_{h16(f'{TAG}|BOUNDARY|n={n}|j={j}|a={a}|b={b}')}"
        edge_records.append(
            {
                "edge_id": f"me_{h16(f'{TAG}|EDGE|n={n}|j={j}|a={a}|b={b}')}",
                "u": vids[a],
                "v": vids[b],
                "boundary_var": bvar,
            }
        )
        incident_edge_indices[a].add(j)
        incident_edge_indices[b].add(j)

    pairs = deterministic_pairs(n)
    affine_atoms = []
    or3_blocks = []
    pairing = []
    candidate_interleave = []

    for pair_index, (a, b) in enumerate(pairs):
        pair_id = f"mp_{h16(f'{TAG}|PAIR|n={n}|j={pair_index}|a={a}|b={b}')}"
        block_id = f"mo_{h16(f'{TAG}|OR3|n={n}|j={pair_index}|a={a}|b={b}')}"
        forbidden = incident_edge_indices[a] | incident_edge_indices[b]
        eligible = [j for j in range(len(edge_records)) if j not in forbidden]
        rnd = random.Random(seed_int(f"{TAG}|ATOM_SUPPORTS|n={n}|pair={pair_index}"))
        rnd.shuffle(eligible)
        need = 3 * ATOM_SUPPORT_SIZE
        if len(eligible) < need:
            raise RuntimeError("insufficient nonlocal boundary edges for affine atoms")
        chosen = eligible[:need]

        atom_ids = []
        for k in range(3):
            support_indices = chosen[k * ATOM_SUPPORT_SIZE : (k + 1) * ATOM_SUPPORT_SIZE]
            atom_id = f"ma_{h16(f'{TAG}|ATOM|n={n}|pair={pair_index}|k={k}')}"
            atom_ids.append(atom_id)
            affine_atoms.append(
                {
                    "atom_id": atom_id,
                    "constant": seed_int(f"{TAG}|ATOM_CONST|n={n}|pair={pair_index}|k={k}") & 1,
                    "support": [edge_records[j]["boundary_var"] for j in support_indices],
                }
            )

        or3_blocks.append(
            {
                "or3_id": block_id,
                "atom_ids": atom_ids,
                "literal_polarities": [1, 1, 1],
            }
        )
        pairing.append(
            {
                "pair_id": pair_id,
                "vertices": [vids[a], vids[b]],
                "or3_id": block_id,
            }
        )
        candidate_interleave.extend(
            [
                {"vertex_id": vids[a], "or3_id": block_id},
                {"vertex_id": vids[b], "or3_id": block_id},
            ]
        )

    obj = {
        "schema": "CONNECTED_MIXED_AFFINE_OR3_SOURCE_V1",
        "target": "CONNECTED_MIXED_AFFINE_OR3_EXPANDER_INTERLEAVE",
        "attack_name": "SYNTHESIS_OF_MIXED_EXACT_GUARDS",
        "n_vertices": n,
        "degree": DEGREE,
        "n_edges": len(edge_records),
        "witness_bits": [f"w_{i}" for i in range(int(math.log2(n)))],
        "witness_decode_order": vids,
        "vertices": [{"vertex_id": vids[v], "charge": charge[v]} for v in range(n)],
        "edges": edge_records,
        "affine_atoms": affine_atoms,
        "or3_blocks": or3_blocks,
        "pairing": pairing,
        "candidate_interleave": candidate_interleave,
        "relation_contract": {
            "base_affine_truth": "charge(vertex) XOR XOR incident boundary edge bits",
            "raw_or3_truth": "OR of the three linked raw affine atom truth values",
            "candidate_admissibility": "By frozen preregistration only: XOR(base_affine_truth, linked_raw_or3_truth)",
            "domain": "TRUE_BY_ODD_BASE_PARITY_PLUS_EVEN_DUPLICATED_OR3_INCIDENCE",
        },
        "anti_cheat": {
            "precomputed_mixed_guard_nodes_present": False,
            "precomputed_or3_output_nodes_present": False,
            "precomputed_affine_substitution_into_or3_present": False,
            "explicit_witness_output_node_present": False,
            "old_connected_mixed_result_import_present": False,
            "old_tseitin_candidate_import_present": False,
        },
        "source_provenance": {
            "generator_tag": TAG,
            "graph_attempt": attempt,
            "charge_parity_adjusted_at_fixed_vertex_zero": adjusted,
            "graph_selection_uses_spectral_metric": False,
            "constructor_existed_when_source_generated": False,
            "resampling_after_constructor_observation": False,
        },
        "qualification_record": {
            "simple": True,
            "regular_degree": DEGREE,
            "connected": True,
            "charge_xor": sum(charge) % 2,
            "lambda2_over_degree": ratio,
            "threshold": THRESHOLD,
            "finite_spectral_stress_gate_pass": ratio <= THRESHOLD,
            "pair_count": len(pairing),
            "or3_block_count": len(or3_blocks),
            "affine_atom_count": len(affine_atoms),
            "atom_support_size": ATOM_SUPPORT_SIZE,
        },
    }

    p = outdir / f"source_n{n}.json"
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    return {
        "n": n,
        "file": p.name,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "graph_attempt": attempt,
        "lambda2_over_degree": ratio,
        "charge_weight": sum(charge),
        "pair_count": len(pairing),
        "affine_atom_count": len(affine_atoms),
    }


def main(outdir_s: str):
    outdir = Path(outdir_s)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = [write_source(n, outdir) for n in SERIES]
    manifest = {
        "artifact_id": "JANUS-U-PAIR-1J-CONNECTED-MIXED-AFFINE-OR3-SOURCE-FREEZE-MANIFEST-2026-09-18-v1.0",
        "prereg_commit": PREREG_COMMIT,
        "generator_tag": TAG,
        "series": rows,
        "selection_firewall": {
            "spectral_metric_used_for_graph_selection": False,
            "resampling_after_constructor_observation": False,
            "constructor_not_implemented_at_source_freeze": True,
            "mixed_guard_not_precomputed": True,
            "or3_output_not_precomputed": True,
        },
    }
    (outdir / "source_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: input_generator.py OUT_DIR")
    main(sys.argv[1])
