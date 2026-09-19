#!/usr/bin/env python3
"""Stage6B.3 canonical OPB generator.

Consumes only a PASS canonical-CNF audit object. Uses standard OPB xN variable
names and emits an explicit mapping back to D/W0/W1/W2 states.

No objective, no optimization, no preprocessing.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def sha_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def file_sha(path:Path)->str:
    return sha_bytes(path.read_bytes())


def state_mapping(vars_):
    mapping={}
    next_id=1
    for v in vars_:
        mapping[str(v)]={}
        for state in ("D","W0","W1","W2"):
            mapping[str(v)][state]=f"x{next_id}"
            next_id+=1
    return mapping


def term(coeff,name):
    sign="+" if coeff>=0 else "-"
    return f"{sign}{abs(coeff)} {name}"


def emit(audit):
    if audit["status"]!="CANONICALIZATION_AUDIT_PASS":
        raise ValueError(f"canonicalization status is {audit['status']}")
    if audit["complementary_pair_clause_count"]!=0:
        raise ValueError("complementary pair guard violated")

    vars_=list(audit["variable_set"])
    clauses=audit["canonical_clauses"]
    k=int(audit["boundary_k"])
    mp=state_mapping(vars_)
    lines=[]
    coefficient_occurrences=0

    # Exactly-one state constraint per original variable.
    for v in vars_:
        m=mp[str(v)]
        names=[m["D"],m["W0"],m["W1"],m["W2"]]
        lines.append(" ".join(term(1,n) for n in names)+" = 1 ;")
        coefficient_occurrences += 4

    # q-Horn weight inequality for each canonical clause.
    for clause in clauses:
        terms=[]
        for lit in clause:
            m=mp[str(abs(lit))]
            terms.append((1,m["W1"]))
            terms.append((2,m["W2"] if lit>0 else m["W0"]))
        if terms:
            lines.append(" ".join(term(c,n) for c,n in terms)+" <= 2 ;")
            coefficient_occurrences += len(terms)
        else:
            lines.append("0 <= 2 ;")

    # Frozen deletion-cardinality boundary.
    lines.append(" ".join(term(1,mp[str(v)]["D"]) for v in vars_)+f" <= {k} ;")
    coefficient_occurrences += len(vars_)

    variable_count=4*len(vars_)
    constraint_count=len(lines)
    header=f"* #variable= {variable_count} #constraint= {constraint_count}\n"
    body=header+"\n".join(lines)+"\n"
    return body,{
      "schema":"janus.trump.stage6b3.canonical_opb_generation_receipt.v1",
      "index":audit["index"],
      "boundary_k":k,
      "raw_cnf_sha256":audit["raw_cnf_sha256"],
      "canonical_cnf_sha256":audit["canonical_cnf_sha256"],
      "mapping":mp,
      "original_variable_set":vars_,
      "PB_variable_count":variable_count,
      "constraint_count":constraint_count,
      "coefficient_occurrence_count":coefficient_occurrences,
      "exactly_one_constraint_count":len(vars_),
      "canonical_clause_constraint_count":len(clauses),
      "deletion_boundary_constraint_count":1,
      "objective_present":False,
      "unauthorized_preprocessing_applied":False
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("audit")
    ap.add_argument("opb")
    ap.add_argument("receipt")
    ns=ap.parse_args()

    audit=json.loads(Path(ns.audit).read_text(encoding="utf-8"))
    opb,receipt=emit(audit)
    opbp=Path(ns.opb); rp=Path(ns.receipt)
    opbp.parent.mkdir(parents=True,exist_ok=True)
    rp.parent.mkdir(parents=True,exist_ok=True)
    opbp.write_text(opb,encoding="utf-8")
    receipt["OPB_sha256"]=file_sha(opbp)
    receipt["OPB_bytes"]=opbp.stat().st_size
    rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "index":receipt["index"],
      "k":receipt["boundary_k"],
      "OPB_sha256":receipt["OPB_sha256"],
      "PB_variable_count":receipt["PB_variable_count"],
      "constraint_count":receipt["constraint_count"],
      "coefficient_occurrence_count":receipt["coefficient_occurrence_count"]
    },sort_keys=True))


if __name__=="__main__":
    main()
