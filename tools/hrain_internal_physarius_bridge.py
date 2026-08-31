#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def csha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def dump(obj,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--manifest",required=True); ap.add_argument("--receipts-root",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); m=json.loads(Path(a.manifest).read_text(encoding="utf-8")); root=Path(a.receipts_root)
    nodes=[{"id":f"internal-physarius:{m['network_id']}","type":"PHYSARIUS_INTERNAL_REPO_NETWORK","label":"JANUS Internal Knowledge Trunks","authority":"DISCOVERY_AND_INTERNAL_MEMORY_ONLY","read_only":True,"content_authority":False}]
    edges=[]; repo_receipts=[]
    for spec in m["repositories"]:
        r=json.loads((root/spec["repo_id"]/"receipt.json").read_text(encoding="utf-8")); repo_receipts.append(r)
        repo_node=f"repo:{spec['repo_id']}"
        nodes.append({"id":repo_node,"type":"INTERNAL_GIT_TRUNK","label":spec["github_repo"],"role":spec["role"],"authority":spec["authority"],"read_only":True,"content_authority":False,"branch_count":r["branch_count"],"unique_head_commits":r["unique_head_commits"],"path_address_count":r["path_address_count"],"unique_blob_count":r["unique_blob_count"],"path_index_sha256":r["path_index_sha256"],"blob_index_sha256":r["blob_index_sha256"],"extension_summary":r["extension_address_summary"]})
        edges.append({"source":nodes[0]["id"],"target":repo_node,"type":"HAS_INTERNAL_TRUNK"})
        for h in r["branch_heads"]:
            bid=f"branch:{spec['repo_id']}:{hashlib.sha256(h['branch'].encode()).hexdigest()[:16]}"
            nodes.append({"id":bid,"type":"GIT_BRANCH_HEAD","label":h["branch"],"commit_sha":h["commit_sha"],"repo_id":spec["repo_id"],"read_only":True,"content_authority":False})
            edges.append({"source":repo_node,"target":bid,"type":"HAS_BRANCH_HEAD"})
    graph={
      "schema":"janus.hrain.physarius_internal_graph.v1",
      "source_network":m["network_id"],"status":"READ_ONLY_INTERNAL_REPO_GRAPH",
      "claim_ceiling":["INTERNAL_MEMORY_NE_EXTERNAL_EVIDENCE","LAPIS_MECHANISM_NE_TRUTH","BRANCH_RECURRENCE_NE_INDEPENDENT_REPLICATION","GRAPH_POSITION_NE_EVIDENCE_STRENGTH"],
      "contentPolicy":{"contentExposed":False,"pathNamesExposed":True,"selectivePullRequiresBinding":True},
      "mutationPolicy":{"write":False,"delete":False,"sourceMutation":False},
      "nodes":nodes,"edges":edges,
      "receipt_roots":[{"repo_id":r["repo_id"],"receipt_sha256":r["receipt_sha256"]} for r in repo_receipts]
    }
    graph["graph_sha256"]=csha({k:v for k,v in graph.items() if k!="graph_sha256"})
    dump(graph,a.out)
    print(json.dumps({"status":graph["status"],"nodes":len(nodes),"edges":len(edges),"graph_sha256":graph["graph_sha256"]},indent=2))
if __name__=="__main__": main()
