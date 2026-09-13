from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CERT_REL = Path("research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_FRESH_EXACT_BERKOWITZ_CHUNKED_COMPLETE_MACRO_DAG_CERTIFICATE_2026-09-12")
RECEIPT_REL = Path("research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_EXACT_BERKOWITZ_Q_BOUNDARY_CENSUS_RECEIPT_2026-09-13.json")
DEFAULT_OUT = REPO / "research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_EXACT_BERKOWITZ_Q_BOUNDARY_CENSUS_CHECKER_RECEIPT_2026-09-13.json"


def slots_of(shape):
    if not isinstance(shape, list):
        raise ValueError("bad shape type")
    result = 1
    for d in shape:
        if type(d) is not int or d <= 0:
            raise ValueError("bad shape dimension")
        result *= d
    return result


def frozen_q_binding(node):
    role = node.get("semantic_role", "")
    core = node.get("determinant_core_role")
    stage = node.get("stage_d")
    if core not in {"SHARED", "C0", "C1"} or type(stage) is not int or not 1 <= stage <= 744:
        return False
    return role == "BERKOWITZ_SHARED_STAGE_Q_D1" or (role.startswith("BERKOWITZ_") and role.endswith("_Q"))


def load_graph(cert_dir: Path):
    manifest = json.loads((cert_dir / "manifest.json").read_text(encoding="utf-8"))
    n = manifest["total_logical_node_count"]
    last_child = [-1] * n
    support = [0] * n
    slot_count = [0] * n
    metadata = [None] * n
    q_nodes = []
    edge_count = 0
    expected_id = 0
    for desc in manifest["ordered_chunk_descriptors_and_sha256s"]:
        raw = (cert_dir / "chunks" / desc["file_name"]).read_bytes()
        if len(raw) != desc["raw_byte_count"] or hashlib.sha256(raw).hexdigest() != desc["sha256"]:
            raise ValueError(f"chunk binding fail: {desc['file_name']}")
        for line in raw.splitlines():
            node = json.loads(line)
            i = node["node_id"]
            if i != expected_id:
                raise ValueError("node order fail")
            parents = node["ordered_parent_ids"]
            if any(type(p) is not int or p < 0 or p >= i for p in parents):
                raise ValueError(f"parent order fail at {i}")
            edge_count += len(parents)
            bits = 0
            for p in parents:
                last_child[p] = i
                bits |= support[p]
            if node["opcode"] == "FINITE_DOMAIN_S4_SELECT":
                idx = node["exact_index_parameters"]["residual_coordinate_index"]
                if type(idx) is not int or not 0 <= idx < 280:
                    raise ValueError("coordinate binding fail")
                bits |= 1 << idx
            support[i] = bits
            shape = node.get("output_shape", [])
            slot_count[i] = slots_of(shape)
            metadata[i] = {
                "node_id": i,
                "opcode": node["opcode"],
                "semantic_role": node.get("semantic_role"),
                "core": node.get("determinant_core_role"),
                "stage_d": node.get("stage_d"),
                "output_shape": shape,
            }
            if frozen_q_binding(node):
                q_nodes.append((i, node.get("determinant_core_role"), node.get("stage_d")))
            expected_id += 1
    if expected_id != n or edge_count != manifest["total_dependency_edge_count"]:
        raise ValueError("frozen count binding fail")
    return manifest, last_child, support, slot_count, metadata, q_nodes

def check(cert_dir: Path, receipt_path: Path):
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    manifest, last_child, support, slot_count, metadata, q_nodes = load_graph(cert_dir)
    n = manifest["total_logical_node_count"]
    diff_count = [0] * (n + 1)
    diff_slots = [0] * (n + 1)
    for p, end in enumerate(last_child):
        if end > p:
            diff_count[p] += 1
            diff_count[end] -= 1
            diff_slots[p] += slot_count[p]
            diff_slots[end] -= slot_count[p]
    q_lookup = {i: (core, stage) for i, core, stage in q_nodes}
    claimed = {row["q_node_id"]: row for row in receipt["boundaries"]}
    if set(claimed) != set(q_lookup):
        raise ValueError("receipt Q set differs from certificate Q set")
    live_count = 0
    live_slots = 0
    mismatches = []
    checked_boundaries = 0
    for cut in range(n):
        live_count += diff_count[cut]
        live_slots += diff_slots[cut]
        if cut not in q_lookup:
            continue
        core, stage = q_lookup[cut]
        row = claimed[cut]
        if row["core"] != core or row["stage_d"] != stage:
            mismatches.append({"cut": cut, "kind": "Q_IDENTITY"})
        if row["live_node_count"] != live_count or row["live_output_scalar_slots"] != live_slots:
            mismatches.append({"cut": cut, "kind": "COUNT_OR_SLOT_SUM", "expected_count": live_count, "expected_slots": live_slots})
        ids = [x["node_id"] for x in row["live_nodes"]]
        if len(ids) != len(set(ids)) or len(ids) != live_count:
            mismatches.append({"cut": cut, "kind": "LIVE_ID_CARDINALITY"})
        for item in row["live_nodes"]:
            p = item["node_id"]
            if not (0 <= p <= cut < last_child[p]):
                mismatches.append({"cut": cut, "kind": "NONLIVE_REPORTED_NODE", "node_id": p})
                continue
            expected = dict(metadata[p])
            expected["scalar_slots"] = slot_count[p]
            expected["coordinate_support_size"] = support[p].bit_count()
            if item != expected:
                mismatches.append({"cut": cut, "kind": "LIVE_NODE_METADATA", "node_id": p})
        checked_boundaries += 1

    summary_mismatches = []
    for core in ("SHARED", "C0", "C1"):
        rows = [claimed[i] for i, c, _ in q_nodes if c == core]
        count_hist = Counter(r["live_node_count"] for r in rows)
        slot_hist = Counter(r["live_output_scalar_slots"] for r in rows)
        actual = receipt["summaries_by_core"][core]
        expected_fields = {
            "q_boundary_count": len(rows),
            "live_node_count_histogram": {str(k): count_hist[k] for k in sorted(count_hist)},
            "live_output_scalar_slots_histogram": {str(k): slot_hist[k] for k in sorted(slot_hist)},
            "minimum_live_node_count": min(r["live_node_count"] for r in rows),
            "maximum_live_node_count": max(r["live_node_count"] for r in rows),
            "minimum_live_output_scalar_slots": min(r["live_output_scalar_slots"] for r in rows),
            "maximum_live_output_scalar_slots": max(r["live_output_scalar_slots"] for r in rows),
        }
        for key, value in expected_fields.items():
            if actual.get(key) != value:
                summary_mismatches.append({"core": core, "field": key, "expected": value, "claimed": actual.get(key)})
        by_id = {r["q_node_id"]: r for r in rows}
        for rep in actual.get("representative_boundaries", []):
            if rep.get("q_node_id") not in by_id or rep != by_id[rep["q_node_id"]]:
                summary_mismatches.append({"core": core, "field": "representative_boundaries", "q_node_id": rep.get("q_node_id")})

    if receipt.get("certificate_digest") != manifest["certificate_digest"]:
        mismatches.append({"kind": "CERTIFICATE_DIGEST"})
    if receipt.get("semantic_source_digest") != manifest["semantic_source_digest"]:
        mismatches.append({"kind": "SEMANTIC_SOURCE_DIGEST"})
    if receipt.get("q_binding_observed_count") != len(q_nodes) or len(q_nodes) != 872:
        mismatches.append({"kind": "Q_COUNT", "observed": len(q_nodes)})
    status = "PASS_INDEPENDENT_EXACT_Q_BOUNDARY_REPLAY" if not mismatches and not summary_mismatches else "FAIL_BINDING_OR_CHECKER"
    return {
        "schema": "TRUMP_EXACT_BERKOWITZ_Q_BOUNDARY_CENSUS_CHECKER_V1",
        "status": status,
        "certificate_digest": manifest["certificate_digest"],
        "checked_q_boundaries": checked_boundaries,
        "q_binding_count": len(q_nodes),
        "mismatches": mismatches,
        "summary_mismatches": summary_mismatches,
        "firewall": "FINITE_STRUCTURAL_REPLAY_ONLY__NO_SEMANTIC_CONGRUENCE_OR_COMPLEXITY_PROMOTION",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certificate", type=Path, default=REPO / CERT_REL)
    ap.add_argument("--receipt", type=Path, default=REPO / RECEIPT_REL)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = check(args.certificate, args.receipt)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"].startswith("PASS") else 1)


if __name__ == "__main__":
    main()
