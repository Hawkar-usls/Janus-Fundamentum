#!/usr/bin/env python3
"""Stage6A external generic q-Horn certificate proposer.

Scientific role: PROPOSER ONLY. This script uses the public Z3 SMT engine to
propose integer q-Horn weights. It is not a q-Horn recognizer authority and it
does not solve SAT for the input CNF.
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, time, traceback
from pathlib import Path


def formula_sequence_sha256(clauses):
    raw=json.dumps(clauses, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()


def propose(row, index: int, timeout_ms: int):
    import z3
    clauses=row["residual_formula"]
    variables=sorted({abs(l) for c in clauses for l in c})
    weights={v:z3.Int(f"w_pos_{v}") for v in variables}
    s=z3.Solver()
    s.set(timeout=timeout_ms)
    for v in variables:
        s.add(weights[v] >= 0, weights[v] <= 2)
    for clause in clauses:
        terms=[]
        for lit in clause:  # preserve every original occurrence
            p=weights[abs(lit)]
            terms.append(p if lit > 0 else 2-p)
        s.add(z3.Sum(terms) <= 2)
    t0=time.perf_counter()
    status=s.check()
    runtime=time.perf_counter()-t0
    out={
      "schema":"janus.trump.stage6.external_generic_qhorn_weight_proposal.v1",
      "authority":"EXTERNAL_GENERIC_SMT_PROPOSER_ONLY__NOT_QHORN_OR_SAT_AUTHORITY",
      "index":index,
      "family":row.get("family"),
      "source_residual_hash":row.get("residual_hash"),
      "raw_cnf_sha256":formula_sequence_sha256(clauses),
      "normalization_applied":False,
      "normalized_cnf_sha256":None,
      "variable_count":len(variables),
      "clause_count":len(clauses),
      "literal_occurrence_count":sum(len(c) for c in clauses),
      "tool":{
        "name":"z3-solver",
        "z3_version":z3.get_version_string(),
        "python_package_version":importlib.metadata.version("z3-solver")
      },
      "timeout_ms":timeout_ms,
      "runtime_seconds":runtime,
      "solver_status":str(status).upper()
    }
    if status == z3.sat:
        m=s.model()
        cert={}
        for v in variables:
            wp=m.eval(weights[v], model_completion=True).as_long()
            cert[str(v)]=wp
            cert[str(-v)]=2-wp
        cert_bytes=(json.dumps(cert,sort_keys=True,separators=(",", ":"))+"\n").encode()
        out["certificate"]={"weights":cert,"sha256":hashlib.sha256(cert_bytes).hexdigest(),"bytes":len(cert_bytes)}
    elif status == z3.unknown:
        out["reason_unknown"]=s.reason_unknown()
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("outdir")
    ap.add_argument("--indices", required=True, help="comma separated residual indices")
    ap.add_argument("--timeout-ms", type=int, default=20000)
    ns=ap.parse_args()
    source=Path(ns.source); outdir=Path(ns.outdir); outdir.mkdir(parents=True,exist_ok=True)
    data=json.loads(source.read_text(encoding="utf-8"))
    indices=[int(x) for x in ns.indices.split(",") if x.strip()]
    receipt=[]
    for i in indices:
        p=outdir/f"r50g25x_{i:02d}.proposal.json"
        try:
            obj=propose(data["residuals"][i],i,ns.timeout_ms)
        except Exception as e:
            obj={
              "schema":"janus.trump.stage6.external_generic_qhorn_weight_proposal.v1",
              "authority":"EXTERNAL_GENERIC_SMT_PROPOSER_ONLY__NOT_QHORN_OR_SAT_AUTHORITY",
              "index":i,"solver_status":"ERROR","error_type":type(e).__name__,"error":str(e),
              "traceback":traceback.format_exc()
            }
        p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        receipt.append({"index":i,"proposal_file":p.name,"proposal_file_sha256":file_sha256(p),"solver_status":obj.get("solver_status"),"runtime_seconds":obj.get("runtime_seconds")})
        print(json.dumps(receipt[-1],sort_keys=True),flush=True)
    (outdir/"manifest.json").write_text(json.dumps({
      "schema":"janus.trump.stage6.external_generic_qhorn_proposal_manifest.v1",
      "source_file_sha256":file_sha256(source),"indices":indices,"rows":receipt
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
