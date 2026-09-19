#!/usr/bin/env python3
"""Independent Stage6B.3 SAT-model and q-Horn witness verifier.

Authority requires BOTH:
  1) a complete model satisfying the exact audited OPB, and
  2) an independently reconstructed deletion-qHorn witness on canonical F.

The solver's textual SAT claim alone is never authority.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from trump_stage6_qhorn_independent_checker import qhorn_terminal, verify_weights  # noqa
from trump_stage6b_deletion_qhorn_independent_checker import deletion_projection  # noqa

TERM_RE=re.compile(r"([+-]?\d+)\s+(x\d+)")


def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_model_text(text, expected_vars):
    assignments={}
    candidates=[]
    for raw in text.splitlines():
        s=raw.strip()
        if not s.startswith("v"):
            continue
        payload=s[1:].strip()
        if not payload:
            continue
        candidates.append(payload)

    for payload in candidates:
        toks=payload.replace(";", " ").split()
        # Binary bitstring format, exactly one token.
        if len(toks)==1 and set(toks[0])<=set("01") and len(toks[0])==len(expected_vars):
            return (
                {name:(bit=="1") for name,bit in zip(
                    sorted(expected_vars,key=lambda x:int(x[1:])),toks[0]
                )},
                "BINARY_V_LINE"
            )

        local={}
        ok=True
        for tok in toks:
            if tok in ("0","SAT","SATISFIABLE"): continue
            if "=" in tok:
                name,val=tok.split("=",1)
                if name in expected_vars and val in ("0","1"):
                    local[name]=(val=="1"); continue
                ok=False; break
            neg=tok.startswith("~")
            body=tok[1:] if neg else tok
            if body in expected_vars:
                local[body]=not neg; continue
            # DIMACS-like signed integer token.
            try:
                n=int(tok)
            except Exception:
                ok=False; break
            if n==0: continue
            name=f"x{abs(n)}"
            if name not in expected_vars:
                ok=False; break
            local[name]=(n>0)
        if ok and local:
            assignments.update(local)

    if set(assignments)==set(expected_vars):
        return assignments,"LITERAL_V_LINES"
    return None,"NO_COMPLETE_MODEL"


def parse_opb(opb_path):
    constraints=[]
    varset=set()
    for line in opb_path.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("*") or s.startswith(("min:","max:")):
            continue
        if not s.endswith(";"):
            raise ValueError("OPB constraint missing semicolon")
        s=s[:-1].strip()
        if "<=" in s:
            lhs,rhs=s.rsplit("<=",1); rel="<="
        elif ">=" in s:
            lhs,rhs=s.rsplit(">=",1); rel=">="
        elif "=" in s:
            lhs,rhs=s.rsplit("=",1); rel="="
        else:
            raise ValueError("OPB relation missing")
        terms=[]
        for c,n in TERM_RE.findall(lhs):
            terms.append((int(c),n)); varset.add(n)
        residue=TERM_RE.sub("",lhs).strip()
        if residue not in ("","0"):
            raise ValueError(f"unparsed OPB lhs residue {residue!r}")
        constraints.append((terms,rel,int(rhs.strip())))
    return constraints,varset


def replay_opb(constraints,model):
    failures=[]
    for ci,(terms,rel,rhs) in enumerate(constraints):
        lhs=sum(c*(1 if model[n] else 0) for c,n in terms)
        good=(lhs<=rhs if rel=="<=" else lhs>=rhs if rel==">=" else lhs==rhs)
        if not good:
            failures.append({"constraint_index":ci,"lhs":lhs,"relation":rel,"rhs":rhs})
    return failures


def decode(mapping,model):
    B=[]
    weights={}
    state_receipt={}
    for sv,m in mapping.items():
        v=int(sv)
        true_states=[s for s,n in m.items() if model[n]]
        if len(true_states)!=1:
            raise ValueError(f"state cardinality failure for original variable {v}: {true_states}")
        state=true_states[0]
        state_receipt[sv]=state
        if state=="D":
            B.append(v)
        elif state=="W0":
            weights[str(v)]=0; weights[str(-v)]=2
        elif state=="W1":
            weights[str(v)]=1; weights[str(-v)]=1
        elif state=="W2":
            weights[str(v)]=2; weights[str(-v)]=0
        else:
            raise ValueError(state)
    return sorted(B),weights,state_receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("canonical_audit")
    ap.add_argument("generator_receipt")
    ap.add_argument("opb_audit")
    ap.add_argument("opb")
    ap.add_argument("solver_stdout")
    ap.add_argument("output")
    ns=ap.parse_args()

    ca=json.loads(Path(ns.canonical_audit).read_text(encoding="utf-8"))
    gr=json.loads(Path(ns.generator_receipt).read_text(encoding="utf-8"))
    oa=json.loads(Path(ns.opb_audit).read_text(encoding="utf-8"))
    opbp=Path(ns.opb)
    stdoutp=Path(ns.solver_stdout)

    out={
      "schema":"janus.trump.stage6b3.sat_model_qhorn_replay.v1",
      "index":ca["index"],
      "boundary_k":ca["boundary_k"],
      "OPB_sha256":sha(opbp),
      "solver_stdout_sha256":sha(stdoutp),
      "PB_MODEL_REPLAY_VERIFIED":False,
      "QHORN_WITNESS_REPLAY_VERIFIED":False
    }

    if ca["status"]!="CANONICALIZATION_AUDIT_PASS" or oa["status"]!="OPB_SEMANTIC_AUDIT_PASS":
        out["failure"]="PRE_SOLVER_AUDIT_NOT_PASS"
    elif gr["OPB_sha256"]!=out["OPB_sha256"] or oa["OPB_sha256"]!=out["OPB_sha256"]:
        out["failure"]="OPB_HASH_BINDING_MISMATCH"
    else:
        constraints,varset=parse_opb(opbp)
        model,fmt=parse_model_text(stdoutp.read_text(encoding="utf-8",errors="replace"),varset)
        out["model_format"]=fmt
        if model is None:
            out["failure"]="NO_COMPLETE_PB_MODEL"
        else:
            failures=replay_opb(constraints,model)
            out["PB_model_variable_count"]=len(model)
            out["PB_constraint_replay_failures"]=failures
            out["PB_MODEL_REPLAY_VERIFIED"]=(len(failures)==0)
            if not failures:
                try:
                    B,weights,states=decode(gr["mapping"],model)
                    out["decoded_B"]=B
                    out["decoded_B_size"]=len(B)
                    out["decoded_states"]=states
                    if len(B)>ca["boundary_k"]:
                        out["failure"]="DECODED_B_EXCEEDS_BOUNDARY"
                    else:
                        reduced=deletion_projection(ca["canonical_clauses"],set(B))
                        ok,detail=verify_weights(reduced,weights)
                        out["qhorn_certificate_verified"]=ok
                        if not ok:
                            out["failure"]={"QHORN_WEIGHT_REPLAY_FAIL":detail}
                        else:
                            terminal=qhorn_terminal(reduced,detail["weights"])
                            out["terminal_replay"]=terminal
                            out["QHORN_WITNESS_REPLAY_VERIFIED"]=bool(terminal.get("terminal_replay_verified"))
                            if out["QHORN_WITNESS_REPLAY_VERIFIED"]:
                                out["verdict"]="VERIFIED_SMALLER_DELETION_QHORN_WITNESS"
                                out["verified_upper_bound"]=len(B)
                            else:
                                out["failure"]="QHORN_TERMINAL_REPLAY_FAIL"
                except Exception as e:
                    out["failure"]=f"DECODE_OR_REPLAY_ERROR:{type(e).__name__}:{e}"

    Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "index":out["index"],
      "PB_MODEL_REPLAY_VERIFIED":out["PB_MODEL_REPLAY_VERIFIED"],
      "QHORN_WITNESS_REPLAY_VERIFIED":out["QHORN_WITNESS_REPLAY_VERIFIED"],
      "decoded_B_size":out.get("decoded_B_size"),
      "verdict":out.get("verdict"),
      "failure":out.get("failure")
    },sort_keys=True))


if __name__=="__main__":
    main()
