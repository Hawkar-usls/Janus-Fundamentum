#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, hashlib, json
from pathlib import Path

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def dump(obj, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

def size_bucket(n):
    if n < 1_000_000:
        return "LT_1MB"
    if n < 100_000_000:
        return "1MB_TO_100MB"
    if n < 1_000_000_000:
        return "100MB_TO_1GB"
    return "GE_1GB"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--receipts-root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--member-node-cap", type=int, default=512)
    args = ap.parse_args()
    manifest = load(args.manifest)
    root = Path(args.receipts_root)
    nodes, edges = [], []
    root_id = "physarius-network:" + manifest["network_id"]
    nodes.append({
        "id": root_id,
        "type": "PHYSARIUS_NETWORK",
        "label": "Physarius Vascular Network",
        "read_only": True,
        "authority": "DISCOVERY_ONLY",
        "content_authority": False
    })
    for v in manifest["vessels"]:
        vid = v["vessel_id"]
        rp = root / vid / "receipt.json"
        r = load(rp) if rp.exists() else {"status": "RECEIPT_MISSING"}
        vn = "vessel:" + vid
        nodes.append({
            "id": vn,
            "type": "REMOTE_VESSEL",
            "label": vid,
            "read_only": True,
            "authority": "DISCOVERY_ONLY",
            "content_authority": False,
            "role": v.get("role"),
            "scientific_lineage": v.get("scientific_lineage"),
            "status": r.get("status"),
            "archive_size": r.get("archive_size"),
            "total_entries": r.get("total_entries"),
            "index_sha256": r.get("index_sha256"),
            "content_policy": v.get("content_policy")
        })
        edges.append({"source": root_id, "target": vn, "type": "HAS_VESSEL"})
        if r.get("status") != "INDEX_OK":
            continue
        entries = r.get("entries", [])
        if len(entries) <= args.member_node_cap:
            for e in entries:
                mid = "member:" + vid + ":" + e["member_id"]
                nodes.append({
                    "id": mid,
                    "type": "BLIND_REMOTE_MEMBER",
                    "label": e.get("extension") or "NO_EXTENSION",
                    "read_only": True,
                    "content_authority": False,
                    "member_id": e["member_id"],
                    "extension": e.get("extension"),
                    "compressed_size": e.get("compressed_size"),
                    "uncompressed_size": e.get("uncompressed_size"),
                    "size_bucket": size_bucket(int(e.get("uncompressed_size") or 0)),
                    "content_exposed": False
                })
                edges.append({"source": vn, "target": mid, "type": "CONTAINS_BLIND_MEMBER"})
        else:
            groups = collections.Counter(
                (e.get("extension") or "NO_EXTENSION", size_bucket(int(e.get("uncompressed_size") or 0)))
                for e in entries
            )
            for (ext, bucket), count in sorted(groups.items()):
                gid = f"bucket:{vid}:{hashlib.sha256((ext+'|'+bucket).encode()).hexdigest()[:16]}"
                nodes.append({
                    "id": gid,
                    "type": "BLIND_MEMBER_BUCKET",
                    "label": f"{ext} · {bucket}",
                    "read_only": True,
                    "content_authority": False,
                    "extension": ext,
                    "size_bucket": bucket,
                    "count": count,
                    "content_exposed": False
                })
                edges.append({"source": vn, "target": gid, "type": "SUMMARIZES_BLIND_MEMBERS"})
    graph = {
        "schema": "janus.hrain.physarius_graph.v1",
        "status": "READ_ONLY_BLIND_REMOTE_GRAPH",
        "source_network": manifest["network_id"],
        "mutationPolicy": {"write": False, "delete": False, "sourceMutation": False},
        "contentPolicy": {"contentExposed": False, "memberNamesExposed": False, "unblindRequiresExternalGate": True},
        "nodes": nodes,
        "edges": edges,
        "claim_ceiling": [
            "HRAIN_GRAPH_NE_SOURCE_AUTHORITY",
            "BLIND_MEMBER_NE_SCIENTIFIC_RESULT",
            "GRAPH_POSITION_NE_EVIDENCE_STRENGTH",
            "SAME_LINEAGE_NE_INDEPENDENT_REPLICATION"
        ]
    }
    graph["graph_sha256"] = hashlib.sha256(
        json.dumps({"nodes": nodes, "edges": edges}, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    dump(graph, args.out)

if __name__ == "__main__":
    main()
