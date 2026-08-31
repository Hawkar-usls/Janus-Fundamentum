#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from physarius_tube import HttpRangeSource, read_zip_index, zenodo_file_url

SAFE_HEADER_KEYS = ("accept-ranges", "content-range", "content-type", "content-length", "content-disposition", "x-source")

def dump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

def safe_headers(source):
    h = {str(k).lower(): str(v) for k, v in getattr(source, "last_headers", {}).items()}
    return {k: h[k] for k in SAFE_HEADER_KEYS if k in h}

def run_vessel(v, out_root: Path, timeout: int):
    vid = v["vessel_id"]
    out = out_root / vid
    out.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "janus.physarius.vessel_receipt.v1",
        "vessel_id": vid,
        "scientific_lineage": v.get("scientific_lineage"),
        "role": v.get("role"),
        "content_policy": v.get("content_policy"),
        "member_names_exposed": False,
        "member_content_exposed": False,
    }
    try:
        if v.get("provider") != "zenodo":
            raise RuntimeError(f"unsupported provider: {v.get('provider')}")
        url = zenodo_file_url(str(v["record_id"]), v["filename"])
        src = HttpRangeSource(url, timeout=timeout, user_agent="JANUS-Physarius-Network/1.0")
        size = src.size()
        tail = src.read_range(max(0, size - 64), size - 1)
        idx = read_zip_index(src)
        entries = [e.to_dict(reveal_names=False) for e in idx.entries]
        receipt.update({
            "status": "INDEX_OK",
            "source": url,
            "archive_size": size,
            "declared_size_bytes": v.get("declared_size_bytes"),
            "declared_size_matches": (v.get("declared_size_bytes") in (None, size)),
            "http_headers": safe_headers(src),
            "tail_probe_sha256": hashlib.sha256(tail).hexdigest(),
            "zip64": idx.zip64,
            "central_directory_size": idx.central_directory_size,
            "total_entries": idx.total_entries,
            "entries": entries,
            "index_sha256": hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        })
    except Exception as e:
        receipt.update({"status": "VESSEL_BLOCKED", "error_type": type(e).__name__, "error": str(e)[:1000]})
    dump(receipt, out / "receipt.json")
    return receipt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=90)
    args = ap.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    out_root = Path(args.out)
    receipts = [run_vessel(v, out_root, args.timeout) for v in manifest["vessels"]]
    summary = {
        "schema": "janus.physarius.network_receipt.v1",
        "network_id": manifest["network_id"],
        "status": "NETWORK_INDEX_COMPLETE" if all(r["status"] == "INDEX_OK" for r in receipts) else "NETWORK_INDEX_PARTIAL",
        "vessel_count": len(receipts),
        "index_ok": sum(r["status"] == "INDEX_OK" for r in receipts),
        "blocked": sum(r["status"] != "INDEX_OK" for r in receipts),
        "content_exposed": False,
        "receipts": [{k:r.get(k) for k in ("vessel_id","scientific_lineage","role","status","archive_size","total_entries","index_sha256","error")} for r in receipts],
    }
    dump(summary, out_root / "network_receipt.json")

if __name__ == "__main__":
    main()
