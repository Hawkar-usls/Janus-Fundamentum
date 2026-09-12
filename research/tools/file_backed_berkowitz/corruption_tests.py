from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
DOMAIN=b"JANUS_TRUMP_FRESH_BERKOWITZ_MACRO_DAG_V1\x00"
def jcs(o): return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
def sha(b): return hashlib.sha256(b).hexdigest()
def run_checker(repo, checker, cert):
    p=subprocess.run(["python",str(checker),"--repo",str(repo),"--cert",str(cert)],capture_output=True,text=True)
    return {"returncode":p.returncode,"stdout":p.stdout.strip()[-2000:],"stderr":p.stderr.strip()[-2000:]}
def copy_cert(src,root,name):
    dst=root/name
    shutil.copytree(src,dst)
    return dst
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",required=True); ap.add_argument("--cert",required=True); ap.add_argument("--checker",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); repo=Path(a.repo).resolve(); src=(repo/a.cert).resolve(); checker=(repo/a.checker).resolve(); out=(repo/a.out).resolve()
    results=[]
    with tempfile.TemporaryDirectory(prefix="janus_berkowitz_corruption_") as td:
        root=Path(td)
        # 1. Raw byte flip: digest must fail before semantic parsing.
        c1=copy_cert(src,root,"raw_flip")
        p=c1/"chunks"/"chunk_000000.jsonl"; b=bytearray(p.read_bytes()); b[10]^=1; p.write_bytes(b)
        r=run_checker(repo,checker,c1); r["test"]="RAW_CHUNK_BYTE_FLIP"; r["expected"]="FAIL_CHUNK_DIGEST_MISMATCH"; r["pass"]=(r["returncode"]!=0 and "FAIL_CHUNK_DIGEST_MISMATCH" in r["stderr"]); results.append(r)
        shutil.rmtree(c1)
        # 2. Missing chunk: completeness must fail.
        c2=copy_cert(src,root,"missing_chunk")
        (c2/"chunks"/"chunk_000010.jsonl").unlink()
        r=run_checker(repo,checker,c2); r["test"]="MISSING_CHUNK"; r["expected"]="MISSING_CHUNK"; r["pass"]=(r["returncode"]!=0 and "MISSING_CHUNK" in r["stderr"]); results.append(r)
        shutil.rmtree(c2)
        # 3. Semantically invalid DOT record with chunk+manifest hashes re-sealed.
        c3=copy_cert(src,root,"semantic_dot")
        mpath=c3/"manifest.json"; m=json.loads(mpath.read_bytes())
        changed=None
        for desc in m["ordered_chunk_descriptors_and_sha256s"]:
            cp=c3/"chunks"/desc["file_name"]
            lines=cp.read_bytes().splitlines()
            for i,line in enumerate(lines):
                obj=json.loads(line)
                if obj.get("opcode")=="DOT_PRODUCT":
                    obj["local_index"]=9999; obj["exact_index_parameters"]["right_chain_index"]=9999
                    lines[i]=jcs(obj); raw=b"\n".join(lines)+b"\n"; cp.write_bytes(raw)
                    desc["raw_byte_count"]=len(raw); desc["sha256"]=sha(raw); changed=(desc["chunk_index"],obj["node_id"]); break
            if changed: break
        core=dict(m); core.pop("certificate_digest",None); m["certificate_digest"]=sha(DOMAIN+jcs(core)); mpath.write_bytes(jcs(m)+b"\n")
        r=run_checker(repo,checker,c3); r["test"]="REHASHED_SEMANTIC_DOT_CORRUPTION"; r["expected"]="DOT_LOCAL_INDEX"; r["mutated"]={"chunk_index":changed[0],"node_id":changed[1]}; r["pass"]=(r["returncode"]!=0 and "DOT_LOCAL_INDEX" in r["stderr"]); results.append(r)
        shutil.rmtree(c3)
    receipt={"schema":"JANUS_TRUMP_BERKOWITZ_CORRUPTION_TESTS_V1","all_pass":all(x["pass"] for x in results),"tests":results}
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"all_pass":receipt["all_pass"],"tests":[{"test":x["test"],"pass":x["pass"],"returncode":x["returncode"]} for x in results]},sort_keys=True))
    return 0 if receipt["all_pass"] else 1
if __name__=="__main__": raise SystemExit(main())
