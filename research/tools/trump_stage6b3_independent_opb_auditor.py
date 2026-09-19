#!/usr/bin/env python3
"""Independent Stage6B.3 semantic OPB auditor.

Does not import the generator. Re-derives the exact PB instance from the
canonical-CNF audit and checks the serialized OPB constraint-by-constraint.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

TERM_RE=re.compile(r"([+-]?\d+)\s+(x\d+)")


def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_mapping(vars_):
    out={}
    n=1
    for v in vars_:
        out[str(v)]={"D":f"x{n}","W0":f"x{n+1}","W1":f"x{n+2}","W2":f"x{n+3}"}
        n+=4
    return out


def constraint(terms,rel,rhs):
    acc={}
    for c,n in terms:
        acc[n]=acc.get(n,0)+int(c)
    acc={k:v for k,v in acc.items() if v!=0}
    return {"terms":dict(sorted(acc.items())),"relation":rel,"rhs":int(rhs)}


def expected(audit):
    if audit["status"]!="CANONICALIZATION_AUDIT_PASS":
        raise ValueError("canonicalization audit not PASS")
    if audit["complementary_pair_clause_count"]!=0:
        raise ValueError("complementary pair guard violated")

    vars_=list(audit["variable_set"])
    mp=independent_mapping(vars_)
    exp=[]

    for v in vars_:
        m=mp[str(v)]
        exp.append(constraint([(1,m[s]) for s in ("D","W0","W1","W2")],"=",1))

    for clause in audit["canonical_clauses"]:
        terms=[]
        for lit in clause:
            m=mp[str(abs(lit))]
            terms.append((1,m["W1"]))
            terms.append((2,m["W2"] if lit>0 else m["W0"]))
        exp.append(constraint(terms,"<=",2))

    exp.append(constraint([(1,mp[str(v)]["D"]) for v in vars_],"<=",audit["boundary_k"]))
    return mp,exp


def parse_constraint(line):
    s=line.strip()
    if not s.endswith(";"):
        raise ValueError(f"missing semicolon: {line!r}")
    s=s[:-1].strip()
    if "<=" in s:
        lhs,rhs=s.rsplit("<=",1); rel="<="
    elif ">=" in s:
        lhs,rhs=s.rsplit(">=",1); rel=">="
    elif "=" in s:
        lhs,rhs=s.rsplit("=",1); rel="="
    else:
        raise ValueError(f"no relation: {line!r}")
    terms=[(int(c),n) for c,n in TERM_RE.findall(lhs)]
    residue=TERM_RE.sub("",lhs).strip()
    if residue not in ("","0"):
        raise ValueError(f"unparsed lhs residue {residue!r}")
    return constraint(terms,rel,int(rhs.strip()))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("audit")
    ap.add_argument("opb")
    ap.add_argument("generator_receipt")
    ap.add_argument("output")
    ns=ap.parse_args()

    audit=json.loads(Path(ns.audit).read_text(encoding="utf-8"))
    gen=json.loads(Path(ns.generator_receipt).read_text(encoding="utf-8"))
    opbp=Path(ns.opb)
    text=opbp.read_text(encoding="utf-8")
    lines=text.splitlines()

    header=[l for l in lines if l.startswith("*")]
    body=[l for l in lines if l.strip() and not l.startswith("*")]
    objective_lines=[l for l in body if l.lstrip().startswith(("min:","max:"))]
    mp,exp=expected(audit)

    parsed=[]
    parse_error=None
    try:
        parsed=[parse_constraint(l) for l in body if l not in objective_lines]
    except Exception as e:
        parse_error=f"{type(e).__name__}: {e}"

    expected_var_count=4*len(audit["variable_set"])
    expected_constraint_count=len(exp)
    header_ok=False
    if len(header)==1:
        m=re.search(r"#variable=\s*(\d+)\s+#constraint=\s*(\d+)",header[0])
        if m:
            header_ok=(int(m.group(1))==expected_var_count and
                       int(m.group(2))==expected_constraint_count)

    failures=[]
    if parse_error: failures.append({"kind":"PARSE_ERROR","detail":parse_error})
    if objective_lines: failures.append({"kind":"OBJECTIVE_PRESENT","lines":objective_lines})
    if not header_ok: failures.append({"kind":"HEADER_COUNT_MISMATCH","header":header})
    if gen.get("mapping")!=mp: failures.append({"kind":"GENERATOR_MAPPING_MISMATCH"})
    if gen.get("raw_cnf_sha256")!=audit["raw_cnf_sha256"]: failures.append({"kind":"RAW_HASH_BINDING_MISMATCH"})
    if gen.get("canonical_cnf_sha256")!=audit["canonical_cnf_sha256"]: failures.append({"kind":"CANONICAL_HASH_BINDING_MISMATCH"})
    if gen.get("boundary_k")!=audit["boundary_k"]: failures.append({"kind":"K_BINDING_MISMATCH"})
    if not parse_error and parsed!=exp:
        first=None
        for i in range(max(len(parsed),len(exp))):
            a=parsed[i] if i<len(parsed) else None
            b=exp[i] if i<len(exp) else None
            if a!=b:
                first={"constraint_index":i,"actual":a,"expected":b}; break
        failures.append({"kind":"CONSTRAINT_SET_MISMATCH","first_difference":first,
                         "actual_count":len(parsed),"expected_count":len(exp)})

    coeff=sum(len(c["terms"]) for c in parsed) if not parse_error else None
    out={
      "schema":"janus.trump.stage6b3.independent_opb_semantic_audit.v1",
      "index":audit["index"],
      "boundary_k":audit["boundary_k"],
      "status":"OPB_SEMANTIC_AUDIT_PASS" if not failures else "INFRASTRUCTURE_ERROR",
      "raw_cnf_sha256":audit["raw_cnf_sha256"],
      "canonical_cnf_sha256":audit["canonical_cnf_sha256"],
      "OPB_sha256":sha(opbp),
      "PB_variable_count":expected_var_count,
      "constraint_count":len(parsed) if not parse_error else None,
      "coefficient_occurrence_count":coeff,
      "objective_present":bool(objective_lines),
      "exact_variable_mapping_verified":gen.get("mapping")==mp,
      "exact_constraint_sequence_verified":not parse_error and parsed==exp,
      "deletion_boundary_verified":not parse_error and bool(parsed) and parsed[-1]==exp[-1],
      "no_unauthorized_preprocessing_verified":not failures,
      "failures":failures
    }
    Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in ("index","boundary_k","status","OPB_sha256","constraint_count","PB_variable_count")},sort_keys=True))
    if failures:
        raise SystemExit(2)


if __name__=="__main__":
    main()
