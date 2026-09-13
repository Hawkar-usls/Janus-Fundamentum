from __future__ import annotations
import argparse, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CERT_REL = Path("research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_FRESH_EXACT_BERKOWITZ_CHUNKED_COMPLETE_MACRO_DAG_CERTIFICATE_2026-09-12")
DEFAULT_OUT = REPO / "research/TRUMP_USF_R0_FIXED_STS31_HPS_R4_PI24_EXACT_BERKOWITZ_Q_BOUNDARY_CENSUS_RECEIPT_2026-09-13.json"
ALLOWED_CORES = {"SHARED", "C0", "C1"}


def scalar_slots(shape):
    if not isinstance(shape, list):
        raise ValueError("output_shape must be a list")
    if not shape:
        return 1
    out = 1
    for dim in shape:
        if type(dim) is not int or dim <= 0:
            raise ValueError(f"invalid output dimension: {dim!r}")
        out *= dim
    return out


def is_q_node(node):
    role = node.get("semantic_role", "")
    core = node.get("determinant_core_role")
    stage = node.get("stage_d")
    if core not in ALLOWED_CORES or type(stage) is not int or not 1 <= stage <= 744:
        return False
    if role == "BERKOWITZ_SHARED_STAGE_Q_D1":
        return True
    return role.startswith("BERKOWITZ_") and role.endswith("_Q")


def expected_q_pairs():
    expected = {("SHARED", d) for d in range(1, 617)}
    expected |= {("C0", d) for d in range(617, 745)}
    expected |= {("C1", d) for d in range(617, 745)}
    return expected


def read_certificate(cert_dir: Path):
    manifest_path = cert_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    n = manifest["total_logical_node_count"]
    last_child = [-1] * n
    supports = [0] * n
    slots = [0] * n
    briefs = [None] * n
    q_nodes = []
    edge_count = 0
    expected_id = 0
    for desc in manifest["ordered_chunk_descriptors_and_sha256s"]:
        path = cert_dir / "chunks" / desc["file_name"]
        raw = path.read_bytes()
        if len(raw) != desc["raw_byte_count"]:
            raise ValueError(f"byte count mismatch: {path.name}")
        if hashlib.sha256(raw).hexdigest() != desc["sha256"]:
            raise ValueError(f"sha256 mismatch: {path.name}")
        for line in raw.splitlines():
            node = json.loads(line)
            node_id = node["node_id"]
            if node_id != expected_id:
                raise ValueError(f"node order mismatch: {node_id} != {expected_id}")
            parents = node["ordered_parent_ids"]
            if any(type(p) is not int or p < 0 or p >= node_id for p in parents):
                raise ValueError(f"non-topological parent at node {node_id}")
            edge_count += len(parents)
            support = 0
            for p in parents:
                last_child[p] = node_id
                support |= supports[p]
            if node["opcode"] == "FINITE_DOMAIN_S4_SELECT":
                idx = node["exact_index_parameters"]["residual_coordinate_index"]
                if type(idx) is not int or not 0 <= idx < 280:
                    raise ValueError(f"bad coordinate index {idx!r}")
                support |= 1 << idx
            supports[node_id] = support
            shape = node.get("output_shape", [])
            slots[node_id] = scalar_slots(shape)
            briefs[node_id] = {
                "node_id": node_id,
                "opcode": node["opcode"],
                "semantic_role": node.get("semantic_role"),
                "core": node.get("determinant_core_role"),
                "stage_d": node.get("stage_d"),
                "output_shape": shape,
            }
            if is_q_node(node):
                q_nodes.append((node_id, node.get("determinant_core_role"), node.get("stage_d")))
            expected_id += 1
    if expected_id != n:
        raise ValueError(f"node count mismatch: {expected_id} != {n}")
    if edge_count != manifest["total_dependency_edge_count"]:
        raise ValueError(f"edge count mismatch: {edge_count}")
    actual_pairs = {(core, stage) for _, core, stage in q_nodes}
    expected_pairs = expected_q_pairs()
    if actual_pairs != expected_pairs or len(q_nodes) != len(expected_pairs):
        missing = sorted(expected_pairs - actual_pairs)
        extra = sorted(actual_pairs - expected_pairs)
        raise ValueError(f"Q binding mismatch: count={len(q_nodes)} missing={missing[:8]} extra={extra[:8]}")
    return manifest, last_child, supports, slots, briefs, q_nodes, edge_count

def boundary_census(cert_dir: Path):
    manifest, last_child, supports, slots, briefs, q_nodes, edge_count = read_certificate(cert_dir)
    n = manifest["total_logical_node_count"]
    ends = defaultdict(list)
    for node_id, end in enumerate(last_child):
        if end > node_id:
            ends[end].append(node_id)
    q_by_id = {node_id: (core, stage) for node_id, core, stage in q_nodes}
    active = set()
    active_slots = 0
    boundaries = []
    for cut in range(n):
        for p in ends.get(cut, ()):
            active.remove(p)
            active_slots -= slots[p]
        if last_child[cut] > cut:
            active.add(cut)
            active_slots += slots[cut]
        if cut not in q_by_id:
            continue
        core, stage = q_by_id[cut]
        live_nodes = []
        for p in sorted(active):
            b = dict(briefs[p])
            b["scalar_slots"] = slots[p]
            b["coordinate_support_size"] = supports[p].bit_count()
            live_nodes.append(b)
        boundaries.append({
            "q_node_id": cut,
            "core": core,
            "stage_d": stage,
            "live_node_count": len(live_nodes),
            "live_output_scalar_slots": active_slots,
            "live_nodes": live_nodes,
        })

    summaries = {}
    for core in ("SHARED", "C0", "C1"):
        rows = [x for x in boundaries if x["core"] == core]
        count_hist = Counter(x["live_node_count"] for x in rows)
        slot_hist = Counter(x["live_output_scalar_slots"] for x in rows)
        min_count = min(x["live_node_count"] for x in rows)
        max_count = max(x["live_node_count"] for x in rows)
        min_slots = min(x["live_output_scalar_slots"] for x in rows)
        max_slots = max(x["live_output_scalar_slots"] for x in rows)
        representatives = []
        selected = set()
        for pred in (
            lambda x: x["stage_d"] == min(r["stage_d"] for r in rows),
            lambda x: x["stage_d"] == max(r["stage_d"] for r in rows),
            lambda x: x["live_node_count"] == min_count,
            lambda x: x["live_node_count"] == max_count,
            lambda x: x["live_output_scalar_slots"] == min_slots,
            lambda x: x["live_output_scalar_slots"] == max_slots,
        ):
            for row in rows:
                if pred(row) and row["q_node_id"] not in selected:
                    representatives.append(row)
                    selected.add(row["q_node_id"])
                    break
        summaries[core] = {
            "q_boundary_count": len(rows),
            "live_node_count_histogram": {str(k): count_hist[k] for k in sorted(count_hist)},
            "live_output_scalar_slots_histogram": {str(k): slot_hist[k] for k in sorted(slot_hist)},
            "minimum_live_node_count": min_count,
            "maximum_live_node_count": max_count,
            "minimum_live_output_scalar_slots": min_slots,
            "maximum_live_output_scalar_slots": max_slots,
            "representative_boundaries": representatives,
        }

    return {
        "schema": "TRUMP_EXACT_BERKOWITZ_Q_BOUNDARY_CENSUS_V1",
        "status": "PASS_EXACT_Q_BOUNDARY_CENSUS",
        "certificate_digest": manifest["certificate_digest"],
        "semantic_source_digest": manifest["semantic_source_digest"],
        "node_count": manifest["total_logical_node_count"],
        "edge_count": edge_count,
        "q_binding_expected_count": len(expected_q_pairs()),
        "q_binding_observed_count": len(q_nodes),
        "summaries_by_core": summaries,
        "boundaries": boundaries,
        "firewalls": [
            "NODE_COUNT_NE_MESSAGE_CARDINALITY",
            "SCALAR_SLOT_COUNT_NE_BIT_COMPLEXITY",
            "FINITE_CENSUS_NE_ASYMPTOTIC_THEOREM",
            "STRUCTURAL_Q_BOUNDARY_NE_CERTIFIED_SEMANTIC_CONGRUENCE",
            "NO_SAT_OR_PI_AUTHORITY",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certificate", type=Path, default=REPO / CERT_REL)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    receipt = boundary_census(args.certificate)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    concise = {k: receipt[k] for k in ("schema", "status", "certificate_digest", "q_binding_observed_count")}
    concise["summaries_by_core"] = receipt["summaries_by_core"]
    print(json.dumps(concise, sort_keys=True))


if __name__ == "__main__":
    main()
