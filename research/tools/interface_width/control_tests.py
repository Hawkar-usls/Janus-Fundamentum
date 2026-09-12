from __future__ import annotations
import hashlib, json, tempfile
from pathlib import Path
from analyze_macroir import analyze, canon


def node(node_id, parents=(), opcode="INTEGER_CONSTANT"):
    return {
        "coefficient_variable_order": [],
        "determinant_core_role": None,
        "exact_index_parameters": {},
        "exact_integer_constants": [1] if opcode == "INTEGER_CONSTANT" else [],
        "input_shapes": [],
        "local_index": None,
        "node_id": node_id,
        "opcode": opcode,
        "ordered_parent_ids": list(parents),
        "output_shape": [1],
        "semantic_role": f"CONTROL_{node_id}",
        "semantic_source_commit": "CONTROL",
        "semantic_source_section": "CONTROL",
        "stage_d": None,
    }


def write_cert(base: Path, nodes):
    chunks = base / "chunks"
    chunks.mkdir(parents=True)
    raw = b"".join((canon(n) + "\n").encode("utf-8") for n in nodes)
    (chunks / "chunk_000000.jsonl").write_bytes(raw)
    edges = sum(len(n["ordered_parent_ids"]) for n in nodes)
    root = nodes[-1]["node_id"]
    manifest = {
        "certificate_digest": "CONTROL_DIGEST",
        "semantic_source_digest": "CONTROL_SOURCE",
        "total_logical_node_count": len(nodes),
        "total_dependency_edge_count": edges,
        "ordered_chunk_descriptors_and_sha256s": [{
            "file_name": "chunk_000000.jsonl",
            "raw_byte_count": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }],
        "all_six_root_node_ids": {
            "widehat_S23": root, "widehat_Theta3": root, "widehat_Xi23": root,
            "widehat_Omega0": root, "widehat_Omega1": root, "widehat_Pi": root,
        },
    }
    (base / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def run_case(name, nodes, expected_width, expected_duplicates=None):
    with tempfile.TemporaryDirectory() as td:
        cert = Path(td)
        write_cert(cert, nodes)
        result = analyze(cert)
    assert result["canonical_node_order_live_frontier_width"] == expected_width, (name, result)
    if expected_duplicates is not None:
        assert result["syntactic_exact_duplicate_node_count"] == expected_duplicates, (name, result)
    return {"name": name, "width": expected_width, "duplicates": result["syntactic_exact_duplicate_node_count"]}

def main():
    results = []
    results.append(run_case("CHAIN", [node(0), node(1, [0], "DOT_PRODUCT"), node(2, [1], "DOT_PRODUCT"), node(3, [2], "DOT_PRODUCT")], 1))
    results.append(run_case("BALANCED_TREE", [
        node(0), node(1), node(2), node(3),
        node(4, [0, 1], "DOT_PRODUCT"), node(5, [2, 3], "DOT_PRODUCT"),
        node(6, [4, 5], "DOT_PRODUCT")
    ], 4))
    results.append(run_case("WIDE_FANIN", [
        *[node(i) for i in range(8)], node(8, list(range(8)), "DOT_PRODUCT")
    ], 8))
    results.append(run_case("DUPLICATED_EXACT_SUBGRAPH", [
        node(0), node(1),
        node(2, [0], "DOT_PRODUCT"), node(3, [1], "DOT_PRODUCT"),
        node(4, [2, 3], "POLYNOMIAL_VECTOR_ADD")
    ], 2, expected_duplicates=2))
    receipt = {
        "schema": "TRUMP_EXACT_MACROIR_INTERFACE_WIDTH_CONTROL_TESTS_V1",
        "status": "PASS_ALL_FROZEN_CONTROLS",
        "results": results,
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
