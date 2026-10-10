#!/usr/bin/env python3
"""Stage6B external deletion-q-Horn candidate proposer.

Scientific role: EXTERNAL PROPOSER ONLY.

The public generic Z3 Optimize engine jointly proposes:
  * B, a set of original variables to delete, and
  * integer q-Horn literal weights for F-B.

The optimizer objective min |B| is search guidance only. Neither Z3's
OPTIMAL/SAT status nor its reported objective is scientific authority for
minimum deletion distance. Independent authority lives in the separate JANUS
checker.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import time
import traceback
from pathlib import Path


def formula_sequence_sha256(clauses):
    raw=json.dumps(clauses,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def stable_json_sha256(obj):
    raw=(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest(),len(raw)


def file_sha256(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def propose(row,index:int,timeout_ms:int):
    import z3

    clauses=row["residual_formula"]
    variables=sorted({abs(l) for c in clauses for l in c})

    opt=z3.Optimize()
    opt.set(timeout=timeout_ms)

    d={v:z3.Int(f"d_{v}") for v in variables}
    w={v:z3.Int(f"w_{v}") for v in variables}

    for v in variables:
        opt.add(d[v]>=0,d[v]<=1)
        opt.add(w[v]>=0,w[v]<=2)

    for clause in clauses:
        retained=[]
        for lit in clause:  # preserve every original literal occurrence
            lv=w[abs(lit)] if lit>0 else 2-w[abs(lit)]
            retained.append(z3.If(d[abs(lit)]==1,0,lv))
        opt.add(z3.Sum(retained)<=2)

    objective=z3.Sum([d[v] for v in variables]) if variables else z3.IntVal(0)
    handle=opt.minimize(objective)

    t0=time.perf_counter()
    status=opt.check()
    runtime=time.perf_counter()-t0

    out={
      "schema":"janus.trump.stage6b.external_generic_deletion_qhorn_proposal.v1",
      "authority":"EXTERNAL_GENERIC_OPTIMIZATION_PROPOSER_ONLY__NO_MINIMALITY_AUTHORITY",
      "index":index,
      "family":row.get("family"),
      "source_residual_hash":row.get("residual_hash"),
      "raw_cnf_sha256":formula_sequence_sha256(clauses),
      "normalization_applied":False,
      "variable_count":len(variables),
      "clause_count":len(clauses),
      "literal_occurrence_count":sum(len(c) for c in clauses),
      "tool":{
        "name":"z3-solver",
        "mode":"Optimize",
        "z3_version":z3.get_version_string(),
        "python_package_version":importlib.metadata.version("z3-solver")
      },
      "timeout_ms":timeout_ms,
      "runtime_seconds":runtime,
      "optimizer_status":str(status).upper(),
      "objective_role":"PROPOSER_SEARCH_HEURISTIC_ONLY__NOT_SCIENTIFIC_AUTHORITY"
    }

    if status==z3.sat:
        m=opt.model()
        B=sorted(v for v in variables if m.eval(d[v],model_completion=True).as_long()==1)
        retained_vars=sorted(set(variables)-set(B))
        weights={}
        for v in retained_vars:
            wp=m.eval(w[v],model_completion=True).as_long()
            weights[str(v)]=wp
            weights[str(-v)]=2-wp

        bsha,bbytes=stable_json_sha256(B)
        wsha,wbytes=stable_json_sha256(weights)

        out.update({
          "B":B,
          "B_size":len(B),
          "PROPOSER_REPORTED_OBJECTIVE":m.eval(objective,model_completion=True).as_long(),
          "B_certificate_sha256":bsha,
          "B_certificate_bytes":bbytes,
          "qhorn_certificate":{
            "weights":weights,
            "sha256":wsha,
            "bytes":wbytes
          }
        })

        try:
            out["optimizer_reported_lower_bound"]=str(opt.lower(handle))
            out["optimizer_reported_upper_bound"]=str(opt.upper(handle))
        except Exception as e:
            out["optimizer_bound_read_error"]=f"{type(e).__name__}: {e}"

    elif status==z3.unknown:
        out["reason_unknown"]=opt.reason_unknown()

    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("outdir")
    ap.add_argument("--indices",required=True)
    ap.add_argument("--timeout-ms",type=int,default=20000)
    ns=ap.parse_args()

    source=Path(ns.source)
    outdir=Path(ns.outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    data=json.loads(source.read_text(encoding="utf-8"))
    indices=[int(x) for x in ns.indices.split(",") if x.strip()]

    receipt=[]
    for i in indices:
        path=outdir/f"r50g25x_{i:02d}.proposal.json"
        try:
            obj=propose(data["residuals"][i],i,ns.timeout_ms)
        except Exception as e:
            obj={
              "schema":"janus.trump.stage6b.external_generic_deletion_qhorn_proposal.v1",
              "authority":"EXTERNAL_GENERIC_OPTIMIZATION_PROPOSER_ONLY__NO_MINIMALITY_AUTHORITY",
              "index":i,
              "optimizer_status":"ERROR",
              "error_type":type(e).__name__,
              "error":str(e),
              "traceback":traceback.format_exc()
            }

        path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        row={
          "index":i,
          "proposal_file":path.name,
          "proposal_file_sha256":file_sha256(path),
          "optimizer_status":obj.get("optimizer_status"),
          "runtime_seconds":obj.get("runtime_seconds"),
          "PROPOSER_REPORTED_OBJECTIVE":obj.get("PROPOSER_REPORTED_OBJECTIVE")
        }
        receipt.append(row)
        print(json.dumps(row,sort_keys=True),flush=True)

    (outdir/"manifest.json").write_text(json.dumps({
      "schema":"janus.trump.stage6b.external_generic_deletion_qhorn_proposal_manifest.v1",
      "source_file_sha256":file_sha256(source),
      "indices":indices,
      "rows":receipt
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
