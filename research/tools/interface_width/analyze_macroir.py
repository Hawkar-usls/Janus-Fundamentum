from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CERT_REL = Path("research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_FRESH_EXACT_BERKOWITZ_CHUNKED_COMPLETE_MACRO_DAG_CERTIFICATE_2026-09-12")
DEFAULT_OUT = REPO / "research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_EXACT_MACROIR_INTERFACE_WIDTH_MEASUREMENT_RECEIPT_2026-09-13.json"


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def computational_signature(node, parent_classes):
    payload = {
        "opcode": node["opcode"],
        "parents": parent_classes,
        "exact_index_parameters": node.get("exact_index_parameters", {}),
        "exact_integer_constants": node.get("exact_integer_constants", []),
        "input_shapes": node.get("input_shapes", []),
        "output_shape": node.get("output_shape", []),
        "coefficient_variable_order": node.get("coefficient_variable_order", []),
    }
    return canon(payload)

def analyze(cert_dir: Path):
    manifest = json.loads((cert_dir / "manifest.json").read_text(encoding="utf-8"))
    n = manifest["total_logical_node_count"]
    last_child = [-1] * n
    supports = [0] * n
    class_ids = [0] * n
    class_map = {}
    class_counts = []
    op_counts = Counter()
    support_hist = Counter()
    edge_count = 0
    expected_id = 0
    previous_stage = None
    stage_cuts = []

    for desc in manifest["ordered_chunk_descriptors_and_sha256s"]:
        path = cert_dir / "chunks" / desc["file_name"]
        raw = path.read_bytes()
        if len(raw) != desc["raw_byte_count"]:
            raise ValueError(f"byte count mismatch: {path.name}")
        if hashlib.sha256(raw).hexdigest() != desc["sha256"]:
            raise ValueError(f"chunk sha256 mismatch: {path.name}")
        for line in raw.splitlines():
            node = json.loads(line)
            node_id = node["node_id"]
            if node_id != expected_id:
                raise ValueError(f"node order mismatch: {node_id} != {expected_id}")
            parents = node["ordered_parent_ids"]
            if any(p >= node_id or p < 0 for p in parents):
                raise ValueError(f"non-topological parent at node {node_id}")
            edge_count += len(parents)
            for p in parents:
                last_child[p] = node_id

            support = 0
            for p in parents:
                support |= supports[p]
            if node["opcode"] == "FINITE_DOMAIN_S4_SELECT":
                idx = node["exact_index_parameters"]["residual_coordinate_index"]
                if not 0 <= idx < 280:
                    raise ValueError(f"bad coordinate index {idx}")
                support |= 1 << idx
            supports[node_id] = support
            support_hist[support.bit_count()] += 1
            op_counts[node["opcode"]] += 1

            key = (node.get("determinant_core_role"), node.get("stage_d"))
            if previous_stage is not None and key != previous_stage:
                stage_cuts.append((node_id - 1, previous_stage))
            previous_stage = key

            sig = computational_signature(node, [class_ids[p] for p in parents])
            cid = class_map.get(sig)
            if cid is None:
                cid = len(class_counts)
                class_map[sig] = cid
                class_counts.append(0)
            class_ids[node_id] = cid
            class_counts[cid] += 1
            expected_id += 1

    if expected_id != n:
        raise ValueError(f"node count mismatch: {expected_id} != {n}")
    if edge_count != manifest["total_dependency_edge_count"]:
        raise ValueError(f"edge count mismatch: {edge_count}")
    if previous_stage is not None:
        stage_cuts.append((n - 1, previous_stage))

    diff = [0] * (n + 1)
    for node_id, last in enumerate(last_child):
        if last > node_id:
            diff[node_id] += 1
            diff[last] -= 1
    frontier = [0] * n
    live = 0
    max_frontier = 0
    max_cut = 0
    for cut in range(n):
        live += diff[cut]
        frontier[cut] = live
        if live > max_frontier:
            max_frontier, max_cut = live, cut

    root_supports = {
        name: supports[node_id].bit_count()
        for name, node_id in manifest["all_six_root_node_ids"].items()
    }
    first_full = next((i for i, s in enumerate(supports) if s.bit_count() == 280), None)
    stage_frontiers = [
        {"cut": cut, "core": key[0], "stage_d": key[1], "frontier": frontier[cut]}
        for cut, key in stage_cuts if cut < n
    ]
    top_classes = sorted(enumerate(class_counts), key=lambda x: (-x[1], x[0]))[:20]
    duplicated_nodes = sum(c - 1 for c in class_counts if c > 1)

    return {
        "schema": "TRUMP_EXACT_MACROIR_INTERFACE_WIDTH_MEASUREMENT_V1",
        "status": "PASS_SCOPED_EXACT_STRUCTURAL_MEASUREMENT",
        "certificate_digest": manifest["certificate_digest"],
        "semantic_source_digest": manifest["semantic_source_digest"],
        "node_count": n,
        "edge_count": edge_count,
        "canonical_node_order_live_frontier_width": max_frontier,
        "canonical_node_order_first_max_cut": max_cut,
        "root_coordinate_support_sizes": root_supports,
        "maximum_coordinate_support_size": max(support_hist),
        "first_node_with_all_280_coordinates": first_full,
        "nodes_with_all_280_coordinates": support_hist[280],
        "coordinate_support_histogram": {str(k): support_hist[k] for k in sorted(support_hist)},
        "stage_cut_count": len(stage_frontiers),
        "maximum_stage_cut_frontier": max((x["frontier"] for x in stage_frontiers), default=0),
        "stage_cut_frontier_top20": sorted(stage_frontiers, key=lambda x: (-x["frontier"], x["cut"]))[:20],
        "syntactic_exact_class_count": len(class_counts),
        "syntactic_exact_duplicate_node_count": duplicated_nodes,
        "syntactic_exact_top20_class_multiplicities": [
            {"class_id": cid, "multiplicity": count} for cid, count in top_classes
        ],
        "opcode_counts": dict(sorted(op_counts.items())),
        "interpretation_firewall": [
            "STRUCTURAL_WIDTH_IS_NOT_SEMANTIC_INTERFACE_LOWER_BOUND_WITHOUT_A_SEPARATE_THEOREM",
            "SYNTACTIC_CONGRUENCE_IS_NOT_GENERAL_SEMANTIC_CONGRUENCE",
            "FINITE_MEASUREMENT_IS_NOT_ASYMPTOTIC_COMPLEXITY_PROOF",
            "NO_SAT_OR_PI_AUTHORITY"
        ]
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certificate", type=Path, default=REPO / CERT_REL)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    receipt = analyze(args.certificate)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
