#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path, PurePosixPath


def run(cmd,cwd=None,text=False): return subprocess.check_output(cmd,cwd=cwd,text=text,stderr=subprocess.STDOUT)
def sha256(b): return hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True); ap.add_argument("--ref",required=True); ap.add_argument("--path",required=True)
    ap.add_argument("--expected-blob-sha",required=True); ap.add_argument("--out",required=True); ap.add_argument("--receipt",required=True)
    ap.add_argument("--max-bytes",type=int,default=8_000_000)
    a=ap.parse_args()
    if a.path.startswith("/") or ".." in PurePosixPath(a.path).parts: raise SystemExit("unsafe path")
    url=f"https://github.com/{a.repo}.git"
    with tempfile.TemporaryDirectory(prefix="physarius-pull-") as td:
        bare=Path(td)/"repo.git"; subprocess.check_call(["git","init","--bare",str(bare)],stdout=subprocess.DEVNULL)
        subprocess.check_call(["git","-C",str(bare),"remote","add","origin",url])
        subprocess.check_call(["git","-C",str(bare),"fetch","--filter=blob:none","--no-tags","--depth=1","origin",a.ref],stdout=subprocess.DEVNULL)
        commit=run(["git","-C",str(bare),"rev-parse","FETCH_HEAD"],text=True).strip()
        actual=run(["git","-C",str(bare),"rev-parse",f"{commit}:{a.path}"],text=True).strip()
        if actual!=a.expected_blob_sha: raise SystemExit(f"blob binding mismatch expected={a.expected_blob_sha} actual={actual}")
        data=run(["git","-C",str(bare),"show",f"{commit}:{a.path}"],text=False)
        if len(data)>a.max_bytes: raise SystemExit(f"blob exceeds max bytes: {len(data)} > {a.max_bytes}")
        out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data)
        receipt={"schema":"janus.physarius.git_selective_pull_receipt.v1","repo":a.repo,"requested_ref":a.ref,"resolved_commit_sha":commit,"path":a.path,"git_blob_sha":actual,"bytes":len(data),"content_sha256":sha256(data),"source_mutation_authority":False,"status":"BOUND_BLOB_PULL_OK"}
        Path(a.receipt).parent.mkdir(parents=True,exist_ok=True); Path(a.receipt).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(receipt,indent=2,sort_keys=True))
if __name__=="__main__": main()
