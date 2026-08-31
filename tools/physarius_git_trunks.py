#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, tempfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath


def run(cmd, cwd=None, text=True):
    return subprocess.check_output(cmd, cwd=cwd, text=text, stderr=subprocess.STDOUT)


def canonical_sha(obj):
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def dump(obj,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")


def ext_of(path):
    s=PurePosixPath(path).suffix.lower()
    return s if s else "NO_EXTENSION"


def index_repo(spec,out_root):
    repo=spec["github_repo"]
    rid=spec["repo_id"]
    out=Path(out_root)/rid
    out.mkdir(parents=True,exist_ok=True)
    url=f"https://github.com/{repo}.git"
    with tempfile.TemporaryDirectory(prefix="physarius-git-") as td:
        bare=Path(td)/"mirror.git"
        run(["git","init","--bare",str(bare)])
        run(["git","-C",str(bare),"remote","add","origin",url])
        # Fetch commits and trees for every head, but deliberately omit blobs.
        run(["git","-C",str(bare),"fetch","--filter=blob:none","--no-tags","origin","+refs/heads/*:refs/remotes/origin/*"])
        refs=run(["git","-C",str(bare),"for-each-ref","--format=%(refname:strip=3)\t%(objectname)","refs/remotes/origin/"])
        branches=[]
        for line in refs.splitlines():
            if not line.strip(): continue
            name,sha=line.split("\t",1)
            if name=="HEAD": continue
            branches.append((name,sha))
        branches.sort()
        commit_to_branches=defaultdict(list)
        for name,sha in branches: commit_to_branches[sha].append(name)
        extension_counts=Counter(); top_counts=Counter(); blob_addresses=defaultdict(list)
        path_records=[]
        for commit_sha,names in sorted(commit_to_branches.items()):
            raw=run(["git","-C",str(bare),"ls-tree","-r","-z",commit_sha],text=False)
            for rec in raw.split(b"\x00"):
                if not rec: continue
                head,pathb=rec.split(b"\t",1)
                mode,typ,blob_sha=head.decode().split()
                if typ!="blob": continue
                path=pathb.decode("utf-8","surrogateescape")
                ext=ext_of(path); extension_counts[ext]+=len(names)
                top=path.split("/",1)[0]; top_counts[top]+=len(names)
                for branch in names:
                    row={"branch":branch,"commit_sha":commit_sha,"path":path,"mode":mode,"blob_sha":blob_sha,"extension":ext}
                    path_records.append(row)
                    blob_addresses[blob_sha].append({"branch":branch,"commit_sha":commit_sha,"path":path})
        path_records.sort(key=lambda x:(x["branch"],x["path"],x["blob_sha"]))
        with (out/"path_index.jsonl").open("w",encoding="utf-8") as f:
            for r in path_records: f.write(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n")
        with (out/"unique_blobs.jsonl").open("w",encoding="utf-8") as f:
            for sha,addresses in sorted(blob_addresses.items()):
                f.write(json.dumps({"blob_sha":sha,"address_count":len(addresses),"addresses":addresses},sort_keys=True,ensure_ascii=False)+"\n")
        branch_heads=[{"branch":n,"commit_sha":s} for n,s in branches]
        receipt={
            "schema":"janus.physarius.git_trunk_receipt.v1",
            "repo_id":rid,"github_repo":repo,"role":spec.get("role"),"authority":spec.get("authority"),
            "status":"TREE_INDEX_OK","branch_policy":spec.get("branch_policy"),
            "branch_count":len(branches),"unique_head_commits":len(commit_to_branches),
            "path_address_count":len(path_records),"unique_blob_count":len(blob_addresses),
            "branch_heads":branch_heads,
            "extension_address_summary":dict(sorted(extension_counts.items())),
            "top_level_address_summary":dict(sorted(top_counts.items())),
            "path_index_sha256":canonical_sha(path_records),
            "blob_index_sha256":canonical_sha([{"blob_sha":s,"addresses":a} for s,a in sorted(blob_addresses.items())]),
            "blob_content_bytes_read":0,
            "path_names_exposed":True,"blob_content_exposed":False,
            "source_mutation_authority":False
        }
        receipt["receipt_sha256"]=canonical_sha(receipt)
        dump(receipt,out/"receipt.json")
        return receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    m=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    receipts=[index_repo(s,args.out) for s in m["repositories"]]
    summary={
      "schema":"janus.physarius.internal_repo_network_receipt.v1",
      "network_id":m["network_id"],
      "status":"INTERNAL_TRUNKS_INDEXED" if all(r["status"]=="TREE_INDEX_OK" for r in receipts) else "INTERNAL_TRUNKS_PARTIAL",
      "repo_count":len(receipts),"blob_content_exposed":False,"source_mutation_authority":False,
      "total_branch_heads":sum(r["branch_count"] for r in receipts),
      "total_path_addresses":sum(r["path_address_count"] for r in receipts),
      "total_unique_blobs_by_repo":sum(r["unique_blob_count"] for r in receipts),
      "repositories":[{k:r[k] for k in ("repo_id","github_repo","role","status","branch_count","unique_head_commits","path_address_count","unique_blob_count","path_index_sha256","blob_index_sha256","receipt_sha256")} for r in receipts]
    }
    summary["network_sha256"]=canonical_sha(summary)
    dump(summary,Path(args.out)/"network_receipt.json")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__": main()
