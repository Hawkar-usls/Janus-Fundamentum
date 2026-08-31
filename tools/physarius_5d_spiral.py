#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, hashlib, json, math, statistics
from pathlib import Path


def dump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def size_bucket(n: int) -> str:
    if n <= 0: return "ZERO"
    if n < 1_000_000: return "LT_1MB"
    if n < 100_000_000: return "1MB_TO_100MB"
    if n < 1_000_000_000: return "100MB_TO_1GB"
    return "GE_1GB"


def ratio_bucket(r):
    if r is None: return "NA"
    if r < 0.1: return "R_LT_0_1"
    if r < 0.3: return "R_0_1_0_3"
    if r < 0.6: return "R_0_3_0_6"
    if r < 0.9: return "R_0_6_0_9"
    if r < 1.1: return "R_0_9_1_1"
    return "R_GT_1_1"


def canonical_hash(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def load_receipts(root: Path):
    out=[]
    for p in sorted(root.glob("*/receipt.json")):
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("status") != "INDEX_OK":
            raise RuntimeError(f"blocked vessel: {p}: {d.get('status')}")
        if d.get("member_names_exposed") is not False or d.get("member_content_exposed") is not False:
            raise RuntimeError(f"blindness firewall failed: {p}")
        out.append(d)
    if not out:
        raise RuntimeError("no vessel receipts")
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--receipts-root", required=True)
    ap.add_argument("--contract", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    contract=json.loads(Path(args.contract).read_text(encoding="utf-8"))
    recs=load_receipts(Path(args.receipts_root))

    entries=[]
    for d in recs:
        for x in d["entries"]:
            u=int(x["uncompressed_size"]); c=int(x["compressed_size"])
            ratio=(c/u) if u else None
            ext=(x.get("extension") or "").lower()
            sig=(ext,size_bucket(u),int(x["compression_method"]),bool(x["is_directory"]),ratio_bucket(ratio))
            entries.append({
                "vessel":d["vessel_id"], "lineage":d["scientific_lineage"], "role":d["role"],
                "policy":d["content_policy"], "member_id":x["member_id"], "ordinal":int(x["ordinal"]),
                "ext":ext, "u":u, "c":c, "ratio":ratio, "method":int(x["compression_method"]),
                "dir":bool(x["is_directory"]), "sig":sig
            })

    sig_count=collections.Counter(e["sig"] for e in entries)
    sig_lineages=collections.defaultdict(set)
    for e in entries: sig_lineages[e["sig"]].add(e["lineage"])

    byv=collections.defaultdict(list)
    for e in entries: byv[e["vessel"]].append(e)
    for _, xs in byv.items():
        xs.sort(key=lambda e:e["ordinal"])
        ratios=[e["ratio"] for e in xs if not e["dir"] and e["ratio"] is not None]
        med=statistics.median(ratios) if ratios else 0.0
        mad=statistics.median([abs(r-med) for r in ratios]) if ratios else 0.0
        for i,e in enumerate(xs):
            prev=xs[i-1] if i else None; nxt=xs[i+1] if i+1 < len(xs) else None
            e["packaging_boundary"]=int((prev is not None and prev["sig"] != e["sig"]) or (nxt is not None and nxt["sig"] != e["sig"]))
            e["ratio_anom"]=0.0 if e["ratio"] is None or mad == 0 else min(10.0, abs(e["ratio"]-med)/(mad+1e-12))

    for e in entries:
        rarity=1/math.sqrt(sig_count[e["sig"]])
        cross=math.log2(1+len(sig_lineages[e["sig"]]))/math.log2(7)
        anomaly=min(e["ratio_anom"],5)/5
        manageable=1.0 if (not e["dir"] and e["u"] <= 256*1024*1024) else 0.0
        parseable=1.0 if e["ext"] in {".txt",".csv",".xlsx",".json",".npy",".dat",".mat"} else 0.25 if e["ext"] in {".tif",".png",".pdb",".xyz"} else 0.0
        e["score"]=0.30*rarity+0.25*cross+0.20*anomaly+0.05*e["packaging_boundary"]+0.20*(manageable*parseable)

    role_survivors={}
    for role in sorted({e["role"] for e in entries}):
        pool=sorted((e for e in entries if e["role"]==role and not e["dir"]), key=lambda e:(-e["score"],e["member_id"]))[:20]
        role_survivors[role]=[{
            "member_id":e["member_id"],"vessel":e["vessel"],"lineage":e["lineage"],"extension":e["ext"],
            "uncompressed_size":e["u"],"spiral_score":round(e["score"],6),
            "lineage_recurrence":len(sig_lineages[e["sig"]]),"shape_count":sig_count[e["sig"]]
        } for e in pool]

    motifs=[]
    for sig,cnt in sig_count.items():
        lins=sorted(sig_lineages[sig])
        if len(lins) >= 2:
            motifs.append({"signature":list(sig),"count":cnt,"lineages":lins,"score":len(lins)/math.sqrt(cnt)})
    motifs.sort(key=lambda m:(-m["score"],json.dumps(m["signature"])))

    tum=[e for e in entries if e["role"]=="HOLDOUT_CANDIDATE" and not e["dir"]]
    eligible=[e for e in tum if e["ext"] in {".txt",".xlsx"} and e["u"] <= 256*1024*1024]
    selected=[]
    xlsx=sorted((e for e in eligible if e["ext"]==".xlsx"), key=lambda e:e["member_id"])
    if xlsx: selected.append(xlsx[0])
    txt=sorted((e for e in eligible if e["ext"]==".txt"), key=lambda e:(e["u"],e["member_id"]))
    if txt:
        for i in sorted(set([0,len(txt)//2,len(txt)-1])): selected.append(txt[i])
    seen=set(); selected=[e for e in selected if not (e["member_id"] in seen or seen.add(e["member_id"]))]

    result={
      "schema":"janus.physarius.blind_5d_spiral.result.v1",
      "status":"SPIRAL_METADATA_PASS__CONTENT_NOT_UNBLINDED",
      "contract_sha256":canonical_hash(contract),
      "origin":{"entries":len(entries),"vessels":len(recs),"lineages":len({e['lineage'] for e in entries}),"claim_ceiling":["BLIND_METADATA_ONLY","NO_SCIENTIFIC_OUTCOME","NO_MEMBER_NAMES","NO_CONTENT"]},
      "spiral":{"generation":1,"geometry":contract["geometry"],"local_deltas":["FULL_MEMBER_SHAPE_GRAPH_TYPED","CROSS_LINEAGE_SHAPE_RECURRENCE_COMPUTED","PACKAGING_BOUNDARIES_LOCALIZED_NOT_INTERPRETED_AS_BIOLOGICAL_TIME","ROLE_SPECIFIC_SURVIVORS_RANKED","TUM_METADATA_ONLY_PULL_SELECTOR_FROZEN"]},
      "counts_by_vessel":{v:len(xs) for v,xs in sorted(byv.items())},
      "counts_by_role":dict(sorted(collections.Counter(e["role"] for e in entries).items())),
      "cross_lineage_motifs_top20":motifs[:20],
      "holdout_selector":{"vessel":"tum_droplet_source_11074305","rule":contract["tum_holdout_selector"]["selection"],"eligible_count":len(eligible),"selected":[{"member_id":e["member_id"],"extension":e["ext"],"uncompressed_size":e["u"],"compressed_size":e["c"],"spiral_score":round(e["score"],6)} for e in selected],"content_exposed":False,"member_names_exposed":False},
      "role_survivors":role_survivors,
      "origin_prime":{"generation":2,"state_delta":"SEARCH_SPACE_REDUCED_WITHOUT_CONTENT_UNBLINDING","next_entry_points":["TUM_SELECTED_OPAQUE_MEMBERS","CALIBRATION_ROLE_SURVIVORS","CROSS_LINEAGE_METADATA_MOTIFS"],"scientific_breakthrough":False},
      "firewalls":contract["firewalls"]
    }
    result["result_sha256"]=canonical_hash(result)
    dump(result,Path(args.out))
    print(json.dumps({"status":result["status"],"entries":len(entries),"vessels":len(recs),"motifs":len(motifs),"tum_eligible":len(eligible),"tum_selected":len(selected),"result_sha256":result["result_sha256"]},indent=2))

if __name__ == "__main__":
    main()
