#!/usr/bin/env python3
"""Independent Stage6B.4 certified bracket + PB24 query auditor."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

TERM_RE=re.compile(r"([+-]?\d+)\s+(x\d+)")


def fsha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stable(obj):
    return hashlib.sha256((json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()


def parse_last_constraint(opb):
    body=[]
    objective=[]
    for line in Path(opb).read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("*"): continue
        if s.startswith(("min:","max:")):
            objective.append(s); continue
        body.append(s)
    if not body: raise ValueError("empty OPB")
    s=body[-1]
    if not s.endswith(";"): raise ValueError("missing semicolon")
    s=s[:-1].strip()
    if ">=" not in s: raise ValueError("deletion constraint not >=")
    lhs,rhs=s.rsplit(">=",1)
    terms=[(int(c),n) for c,n in TERM_RE.findall(lhs)]
    residue=TERM_RE.sub("",lhs).strip()
    if residue not in ("","0"): raise ValueError(f"unparsed lhs {residue}")
    return terms,int(rhs.strip()),objective,len(body)


def independent_mapping(variable_set):
    out={}; n=1
    for v in variable_set:
        out[str(v)]={"D":f"x{n}","W0":f"x{n+1}","W1":f"x{n+2}","W2":f"x{n+3}"}
        n+=4
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_canonical")
    ap.add_argument("state")
    ap.add_argument("query_audit")
    ap.add_argument("query_binding_receipt")
    ap.add_argument("generation_receipt")
    ap.add_argument("pb24_audit")
    ap.add_argument("opb")
    ap.add_argument("output")
    ns=ap.parse_args()

    src=json.loads(Path(ns.source_canonical).read_text())
    st=json.loads(Path(ns.state).read_text())
    qa=json.loads(Path(ns.query_audit).read_text())
    qb=json.loads(Path(ns.query_binding_receipt).read_text())
    gen=json.loads(Path(ns.generation_receipt).read_text())
    pa=json.loads(Path(ns.pb24_audit).read_text())
    failures=[]

    L=int(st["L"]); U=int(st["U"])
    expected_k=(L+U)//2 if U>L+1 else None
    if expected_k is None: failures.append("BRACKET_ALREADY_CLOSED")
    if int(qb.get("selected_k",-1))!=expected_k: failures.append("QUERY_BINDING_K_MISMATCH")
    if int(qa.get("boundary_k",-1))!=expected_k: failures.append("QUERY_AUDIT_K_MISMATCH")
    bind=qa.get("stage6b4_query_binding",{})
    if int(bind.get("L_before",-1))!=L or int(bind.get("U_before",-1))!=U or int(bind.get("selected_k",-1))!=expected_k:
        failures.append("QUERY_AUDIT_BRACKET_BINDING_MISMATCH")
    if bind.get("selection_rule")!="floor((L+U)/2)": failures.append("SELECTION_RULE_MISMATCH")

    for field in ("raw_cnf_sha256","canonical_cnf_sha256","canonical_clauses","variable_set"):
        if qa.get(field)!=src.get(field): failures.append(f"CANONICAL_SOURCE_CHANGED:{field}")
    if src.get("status")!="CANONICALIZATION_AUDIT_PASS" or qa.get("status")!="CANONICALIZATION_AUDIT_PASS":
        failures.append("CANONICALIZATION_NOT_PASS")
    if int(qa.get("duplicate_literal_occurrence_count",-1))!=int(src.get("duplicate_literal_occurrence_count",-2)):
        failures.append("DUPLICATE_AUDIT_CHANGED")
    if int(qa.get("complementary_pair_clause_count",-1))!=0:
        failures.append("COMPLEMENTARY_PAIR_GUARD")

    if pa.get("status")!="OPB_SEMANTIC_AUDIT_PASS" or pa.get("PB24_SEMANTIC_AUDIT")!="PASS":
        failures.append("PB24_SEMANTIC_AUDIT_NOT_PASS")
    if int(pa.get("boundary_k",-1))!=expected_k: failures.append("PB24_AUDIT_K_MISMATCH")
    if pa.get("canonical_cnf_sha256")!=src.get("canonical_cnf_sha256"):
        failures.append("PB24_CANONICAL_HASH_MISMATCH")
    if gen.get("OPB_sha256")!=fsha(ns.opb) or pa.get("OPB_sha256")!=fsha(ns.opb):
        failures.append("OPB_HASH_BINDING_MISMATCH")
    if int(gen.get("boundary_k",-1))!=expected_k:
        failures.append("GENERATOR_K_MISMATCH")
    if gen.get("objective_present") is not False:
        failures.append("GENERATOR_OBJECTIVE_PRESENT")

    try:
        terms,rhs,objective,body_count=parse_last_constraint(ns.opb)
        mp=independent_mapping(src["variable_set"])
        expected_terms=[(-1,mp[str(v)]["D"]) for v in src["variable_set"]]
        if terms!=expected_terms or rhs!=-expected_k:
            failures.append("DELETION_BOUNDARY_SERIALIZATION_MISMATCH")
        if objective: failures.append("OBJECTIVE_PRESENT")
        if body_count!=int(gen.get("constraint_count",-1)):
            failures.append("CONSTRAINT_COUNT_MISMATCH")
    except Exception as e:
        terms=[]; rhs=None; objective=[]; body_count=None
        failures.append(f"OPB_DIRECT_PARSE_ERROR:{type(e).__name__}:{e}")

    out={
      "schema":"janus.trump.stage6b4.independent_bracket_opb_audit.v1",
      "index":int(st["index"]),
      "round":int(st["round"])+1,
      "L_before":L,"U_before":U,"selected_k":expected_k,
      "selection_rule":"floor((L+U)/2)",
      "raw_cnf_sha256":src.get("raw_cnf_sha256"),
      "canonical_cnf_sha256":src.get("canonical_cnf_sha256"),
      "query_audit_sha256":fsha(ns.query_audit),
      "query_binding_receipt_sha256":fsha(ns.query_binding_receipt),
      "OPB_sha256":fsha(ns.opb),
      "PB24_audit_receipt_sha256":fsha(ns.pb24_audit),
      "PB24_SEMANTIC_AUDIT":pa.get("PB24_SEMANTIC_AUDIT"),
      "direct_deletion_constraint_verified":not any(x.startswith("DELETION_BOUNDARY") for x in failures),
      "objective_present":bool(objective),
      "status":"B4_BRACKET_OPB_AUDIT_PASS" if not failures else "INFRASTRUCTURE_ERROR",
      "failures":failures
    }
    Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ("index","round","L_before","U_before","selected_k","status","OPB_sha256")},sort_keys=True))
    if failures: raise SystemExit(2)


if __name__=="__main__": main()
