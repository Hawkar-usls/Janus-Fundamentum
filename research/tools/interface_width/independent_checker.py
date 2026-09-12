from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CERT = REPO / "research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_FRESH_EXACT_BERKOWITZ_CHUNKED_COMPLETE_MACRO_DAG_CERTIFICATE_2026-09-12"
MEASUREMENT = REPO / "research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_EXACT_MACROIR_INTERFACE_WIDTH_MEASUREMENT_RECEIPT_2026-09-13.json"
CHECKER_OUT = REPO / "research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_EXACT_MACROIR_INTERFACE_WIDTH_CHECKER_RECEIPT_2026-09-13.json"


def check(cert_dir: Path, measurement_path: Path):
    manifest = json.loads((cert_dir / "manifest.json").read_text(encoding="utf-8"))
    claimed = json.loads(measurement_path.read_text(encoding="utf-8"))
    n = manifest["total_logical_node_count"]
    final_use = [-1] * n
    deps = [0] * n
    edges = 0
    next_id = 0
    full_count = 0
    max_support = 0
    first_full = None

    for desc in manifest["ordered_chunk_descriptors_and_sha256s"]:
        raw = (cert_dir / "chunks" / desc["file_name"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != desc["sha256"]:
            raise AssertionError(f"chunk digest mismatch: {desc['file_name']}")
        for line in raw.splitlines():
            node = json.loads(line)
            node_id = node["node_id"]
            if node_id != next_id:
                raise AssertionError(f"node id mismatch {node_id} != {next_id}")
            bits = 0
            for p in node["ordered_parent_ids"]:
                if p >= node_id:
                    raise AssertionError(f"parent order violation at {node_id}")
                final_use[p] = node_id
                bits |= deps[p]
                edges += 1
            if node["opcode"] == "FINITE_DOMAIN_S4_SELECT":
                idx = node["exact_index_parameters"]["residual_coordinate_index"]
                bits |= 1 << idx
            deps[node_id] = bits
            size = bits.bit_count()
            max_support = max(max_support, size)
            if size == 280:
                full_count += 1
                if first_full is None:
                    first_full = node_id
            next_id += 1

    if next_id != n or edges != manifest["total_dependency_edge_count"]:
        raise AssertionError("manifest cardinality mismatch")

    starts, ends = Counter(), Counter()
    for node_id, last in enumerate(final_use):
        if last > node_id:
            starts[node_id] += 1
            ends[last] += 1
    live = 0
    width = 0
    first_max_cut = 0
    for cut in range(n):
        live += starts[cut]
        live -= ends[cut]
        if live > width:
            width = live
            first_max_cut = cut

    root_supports = {
        name: deps[node_id].bit_count()
        for name, node_id in manifest["all_six_root_node_ids"].items()
    }
    expected = {
        "certificate_digest": manifest["certificate_digest"],
        "semantic_source_digest": manifest["semantic_source_digest"],
        "node_count": n,
        "edge_count": edges,
        "canonical_node_order_live_frontier_width": width,
        "canonical_node_order_first_max_cut": first_max_cut,
        "root_coordinate_support_sizes": root_supports,
        "maximum_coordinate_support_size": max_support,
        "first_node_with_all_280_coordinates": first_full,
        "nodes_with_all_280_coordinates": full_count,
    }
    mismatches = {k: {"claimed": claimed.get(k), "recomputed": v} for k, v in expected.items() if claimed.get(k) != v}
    return {
        "schema": "TRUMP_EXACT_MACROIR_INTERFACE_WIDTH_CHECKER_V1",
        "status": "PASS_INDEPENDENT_EXACT_STRUCTURAL_REPLAY" if not mismatches else "FAIL_BINDING_OR_CHECKER",
        "mismatches": mismatches,
        "recomputed": expected,
        "firewall": "THIS_CHECKS_ONLY_FROZEN_STRUCTURAL_METRICS_NOT_SEMANTIC_CONGRUENCE_OR_COMPLEXITY"
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--measurement", type=Path, default=MEASUREMENT)
    ap.add_argument("--out", type=Path, default=CHECKER_OUT)
    args = ap.parse_args()
    result = check(args.certificate, args.measurement)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS_INDEPENDENT_EXACT_STRUCTURAL_REPLAY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
