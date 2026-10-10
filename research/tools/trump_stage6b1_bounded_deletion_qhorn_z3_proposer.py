#!/usr/bin/env python3
"""Stage6B.1 bounded deletion-q-Horn feasibility proposer.

Scientific role: PROPOSER ONLY.

For one frozen residual and one preregistered deletion budget k, this script
asks a public generic Z3 Solver only for feasibility. It uses Boolean/PB
states D,W0,W1,W2 and no optimization objective.

SAT is only a candidate witness. UNSAT/UNKNOWN are telemetry only and have no
lower-bound or minimality authority.
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


def stable_json_receipt(obj):
    raw=(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest(),len(raw)


def propose(row,index:int,k:int,timeout_ms:int):
    import z3

    clauses=row["residual_formula"]
    variables=sorted({abs(l) for c in clauses for l in c})

    s=z3.Solver()
    s.set(timeout=timeout_ms)

    D={v:z3.Bool(f"D_{v}") for v in variables}
    W0={v:z3.Bool(f"W0_{v}") for v in variables}
    W1={v:z3.Bool(f"W1_{v}") for v in variables}
    W2={v:z3.Bool(f"W2_{v}") for v in variables}

    for v in variables:
        s.add(z3.PbEq([(D[v],1),(W0[v],1),(W1[v],1),(W2[v],1)],1))

    for clause in clauses:
        terms=[]
        for lit in clause:  # preserve every original literal occurrence
            v=abs(lit)
            if lit>0:
                terms.append((W1[v],1))
                terms.append((W2[v],2))
            else:
                terms.append((W1[v],1))
                terms.append((W0[v],2))
        s.add(z3.PbLe(terms,2))

    s.add(z3.PbLe([(D[v],1) for v in variables],k))

    t0=time.perf_counter()
    status=s.check()
    runtime=time.perf_counter()-t0

    out={
      "schema":"janus.trump.stage6b1.bounded_deletion_qhorn_feasibility_proposal.v1",
      "authority":"EXTERNAL_GENERIC_FEASIBILITY_PROPOSER_ONLY__NO_LOWER_BOUND_OR_MINIMALITY_AUTHORITY",
      "index":index,
      "k":k,
      "family":row.get("family"),
      "source_residual_hash":row.get("residual_hash"),
      "raw_cnf_sha256":formula_sequence_sha256(clauses),
      "normalization_applied":False,
      "variable_count":len(variables),
      "clause_count":len(clauses),
      "literal_occurrence_count":sum(len(c) for c in clauses),
      "tool":{
        "name":"z3-solver",
        "mode":"Solver_Boolean_PseudoBoolean_Feasibility",
        "z3_version":z3.get_version_string(),
        "python_package_version":importlib.metadata.version("z3-solver")
      },
      "timeout_ms":timeout_ms,
      "runtime_seconds":runtime,
      "solver_status":str(status).upper(),
      "status_interpretation":{
        "SAT":"CANDIDATE_ONLY_REQUIRES_INDEPENDENT_VERIFICATION",
        "UNSAT":"DISCOVERY_TELEMETRY_ONLY_NO_LOWER_BOUND_AUTHORITY",
        "UNKNOWN":"DISCOVERY_TELEMETRY_ONLY",
        "ERROR":"INFRASTRUCTURE_OR_PROPOSER_TELEMETRY"
      }
    }

    if status==z3.sat:
        m=s.model()
        states={}
        B=[]
        weights={}
        for v in variables:
            flags={
              "D":z3.is_true(m.eval(D[v],model_completion=True)),
              "W0":z3.is_true(m.eval(W0[v],model_completion=True)),
              "W1":z3.is_true(m.eval(W1[v],model_completion=True)),
              "W2":z3.is_true(m.eval(W2[v],model_completion=True))
            }
            true_states=[name for name,val in flags.items() if val]
            state=true_states[0] if len(true_states)==1 else "INVALID_MODEL_STATE"
            states[str(v)]=state
            if state=="D":
                B.append(v)
            elif state=="W0":
                weights[str(v)]=0
                weights[str(-v)]=2
            elif state=="W1":
                weights[str(v)]=1
                weights[str(-v)]=1
            elif state=="W2":
                weights[str(v)]=2
                weights[str(-v)]=0

        B=sorted(B)
        bsha,bbytes=stable_json_receipt(B)
        ssha,sbytes=stable_json_receipt(states)
        wsha,wbytes=stable_json_receipt(weights)
        out.update({
          "states":states,
          "B":B,
          "B_size":len(B),
          "B_certificate_sha256":bsha,
          "B_certificate_bytes":bbytes,
          "state_certificate_sha256":ssha,
          "state_certificate_bytes":sbytes,
          "qhorn_certificate":{
            "weights":weights,
            "sha256":wsha,
            "bytes":wbytes
          }
        })
    elif status==z3.unknown:
        out["reason_unknown"]=s.reason_unknown()

    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--index",type=int,required=True)
    ap.add_argument("--k",type=int,required=True)
    ap.add_argument("--timeout-ms",type=int,default=10000)
    ns=ap.parse_args()

    source=Path(ns.source)
    output=Path(ns.output)
    data=json.loads(source.read_text(encoding="utf-8"))

    try:
        obj=propose(data["residuals"][ns.index],ns.index,ns.k,ns.timeout_ms)
    except Exception as e:
        obj={
          "schema":"janus.trump.stage6b1.bounded_deletion_qhorn_feasibility_proposal.v1",
          "authority":"EXTERNAL_GENERIC_FEASIBILITY_PROPOSER_ONLY__NO_LOWER_BOUND_OR_MINIMALITY_AUTHORITY",
          "index":ns.index,
          "k":ns.k,
          "solver_status":"ERROR",
          "error_type":type(e).__name__,
          "error":str(e),
          "traceback":traceback.format_exc()
        }

    output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    output.write_text(raw,encoding="utf-8")

    print(json.dumps({
      "index":ns.index,
      "k":ns.k,
      "solver_status":obj.get("solver_status"),
      "runtime_seconds":obj.get("runtime_seconds"),
      "reason_unknown":obj.get("reason_unknown"),
      "B_size":obj.get("B_size"),
      "proposal_sha256":hashlib.sha256(raw.encode("utf-8")).hexdigest()
    },sort_keys=True))


if __name__=="__main__":
    main()
