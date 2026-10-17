#!/usr/bin/env python3
"""Stage6B.4 independent SAT model + q-Horn witness verifier."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from trump_stage6_qhorn_independent_checker import qhorn_terminal, verify_weights  # noqa
from trump_stage6b_deletion_qhorn_independent_checker import deletion_projection  # noqa

TERM_RE=re.compile(r"([+-]?\d+)\s+(x\d+)")


def fsha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stable(obj):
    return hashlib.sha256((json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()


def independent_mapping(vars_):
    out={}; n=1
    for v in vars_:
        out[str(v)]={"D":f"x{n}","W0":f"x{n+1}","W1":f"x{n+2}","W2":f"x{n+3}"}
        n+=4
    return out


def assign_once(a,name,val,conflicts,repeats):
    if name in a:
        repeats.append({"variable":name,"existing":a[name],"new":val})
        if a[name]!=val: conflicts.append({"variable":name,"existing":a[name],"new":val})
    else: a[name]=val


def parse_model(text,expected):
    expected=set(expected); assignments={}; conflicts=[]; repeats=[]; extras=[]; bad=[]; fmts=set()
    payloads=[l.strip()[1:].strip() for l in text.splitlines() if l.strip().startswith("v") and l.strip()[1:].strip()]
    if len(payloads)==1:
        toks=payloads[0].replace(";"," ").split()
        if len(toks)==1 and set(toks[0])<=set("01") and len(toks[0])==len(expected):
            ordered=sorted(expected,key=lambda x:int(x[1:]))
            return {n:b=="1" for n,b in zip(ordered,toks[0])},{"status":"COMPLETE","format":"BINARY_V_LINE"}
    for payload in payloads:
        for tok in payload.replace(";"," ").split():
            if tok in ("0","SAT","SATISFIABLE"): continue
            if "=" in tok:
                name,val=tok.split("=",1)
                if name in expected and val in ("0","1"):
                    assign_once(assignments,name,val=="1",conflicts,repeats); fmts.add("EQUALS"); continue
                bad.append(tok); continue
            if tok.startswith("-x") and tok[2:].isdigit():
                name="x"+tok[2:]
                if name in expected: assign_once(assignments,name,False,conflicts,repeats); fmts.add("ROUNDINGSAT_SIGNED_X")
                else: extras.append(name)
                continue
            if tok.startswith("~x") and tok[2:].isdigit():
                name="x"+tok[2:]
                if name in expected: assign_once(assignments,name,False,conflicts,repeats); fmts.add("TILDE_X")
                else: extras.append(name)
                continue
            if tok.startswith("x") and tok[1:].isdigit():
                if tok in expected: assign_once(assignments,tok,True,conflicts,repeats); fmts.add("POSITIVE_X")
                else: extras.append(tok)
                continue
            try: n=int(tok)
            except Exception:
                bad.append(tok); continue
            if n==0: continue
            name=f"x{abs(n)}"
            if name in expected: assign_once(assignments,name,n>0,conflicts,repeats); fmts.add("SIGNED_INTEGER")
            else: extras.append(name)
    missing=sorted(expected-set(assignments),key=lambda x:int(x[1:]))
    extra=sorted(set(extras)|(set(assignments)-expected),key=lambda x:int(x[1:]))
    receipt={"status":"COMPLETE" if not missing and not extra and not conflicts and not bad else "INVALID",
             "format":"+".join(sorted(fmts)) if fmts else None,"assignment_count":len(assignments),
             "expected_assignment_count":len(expected),"missing":missing,"extra":extra,
             "conflicts":conflicts,"repeats":repeats,"unrecognized_tokens":bad}
    return (assignments if receipt["status"]=="COMPLETE" else None),receipt


def parse_opb(path):
    cons=[]; vars_=set()
    for line in Path(path).read_text().splitlines():
        s=line.strip()
        if not s or s.startswith("*") or s.startswith(("min:","max:")): continue
        if not s.endswith(";"): raise ValueError("missing ;")
        s=s[:-1].strip()
        if ">=" in s: lhs,rhs=s.rsplit(">=",1); rel=">="
        elif "<=" in s: lhs,rhs=s.rsplit("<=",1); rel="<="
        elif "=" in s: lhs,rhs=s.rsplit("=",1); rel="="
        else: raise ValueError("relation missing")
        terms=[(int(c),n) for c,n in TERM_RE.findall(lhs)]
        for _,n in terms: vars_.add(n)
        residue=TERM_RE.sub("",lhs).strip()
        if residue not in ("","0"): raise ValueError(f"unparsed lhs {residue}")
        cons.append((terms,rel,int(rhs.strip())))
    return cons,vars_


def replay(cons,model):
    bad=[]
    for i,(terms,rel,rhs) in enumerate(cons):
        lhs=sum(c*(1 if model[n] else 0) for c,n in terms)
        ok=lhs>=rhs if rel==">=" else lhs<=rhs if rel=="<=" else lhs==rhs
        if not ok: bad.append({"constraint_index":i,"lhs":lhs,"relation":rel,"rhs":rhs})
    return bad


def decode(mp,model):
    B=[]; weights={}; states={}
    for sv,m in mp.items():
        true=[s for s,n in m.items() if model[n]]
        if len(true)!=1: raise ValueError(f"state cardinality {sv}:{true}")
        s=true[0]; v=int(sv); states[sv]=s
        if s=="D": B.append(v)
        elif s=="W0": weights[str(v)]=0; weights[str(-v)]=2
        elif s=="W1": weights[str(v)]=1; weights[str(-v)]=1
        elif s=="W2": weights[str(v)]=2; weights[str(-v)]=0
    return sorted(B),weights,states


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("query_audit"); ap.add_argument("generation_receipt"); ap.add_argument("pb24_audit")
    ap.add_argument("bracket_opb_audit"); ap.add_argument("opb"); ap.add_argument("solver_stdout")
    ap.add_argument("solver_receipt"); ap.add_argument("output")
    ns=ap.parse_args()
    qa=json.loads(Path(ns.query_audit).read_text()); gr=json.loads(Path(ns.generation_receipt).read_text())
    pa=json.loads(Path(ns.pb24_audit).read_text()); ba=json.loads(Path(ns.bracket_opb_audit).read_text())
    sr=json.loads(Path(ns.solver_receipt).read_text()); opb=Path(ns.opb); sout=Path(ns.solver_stdout)
    out={"schema":"janus.trump.stage6b4.sat_model_qhorn_authority.v1","index":qa["index"],
         "round":qa["stage6b4_query_binding"]["round"],"selected_k":qa["boundary_k"],
         "OPB_sha256":fsha(opb),"solver_stdout_sha256":fsha(sout),
         "PB_MODEL_REPLAY_VERIFIED":False,"QHORN_WITNESS_REPLAY_VERIFIED":False,
         "terminal_replay_verified":False}
    failures=[]
    if pa.get("PB24_SEMANTIC_AUDIT")!="PASS": failures.append("PB24_AUDIT_NOT_PASS")
    if ba.get("status")!="B4_BRACKET_OPB_AUDIT_PASS": failures.append("BRACKET_OPB_AUDIT_NOT_PASS")
    if sr.get("proof_producer_status")!="SAT": failures.append("SOLVER_STATUS_NOT_SAT")
    if sr.get("OPB_sha256")!=out["OPB_sha256"]: failures.append("SOLVER_OPB_HASH_MISMATCH")
    if sr.get("model_source_sha256")!=out["solver_stdout_sha256"]: failures.append("MODEL_HASH_MISMATCH")
    if sr.get("parser_rejection_markers"): failures.append("PARSER_REJECTION_PRESENT")
    mp=independent_mapping(qa["variable_set"])
    if gr.get("mapping")!=mp: failures.append("GENERATOR_MAPPING_MISMATCH")
    if failures: out["failure"]=failures
    else:
        cons,varset=parse_opb(opb)
        expected={n for m in mp.values() for n in m.values()}
        if varset!=expected:
            out["failure"]="OPB_VARIABLE_SET_MISMATCH"
        else:
            model,prec=parse_model(sout.read_text(errors="replace"),expected); out["model_parse_receipt"]=prec
            if model is None: out["failure"]="NO_COMPLETE_PB_MODEL"
            else:
                bad=replay(cons,model); out["PB_constraint_replay_failures"]=bad
                out["PB_MODEL_REPLAY_VERIFIED"]=not bad
                if bad: out["failure"]="PB_MODEL_REPLAY_FAIL"
                else:
                    try:
                        B,w,states=decode(mp,model); out["decoded_B"]=B; out["decoded_B_size"]=len(B)
                        out["decoded_B_sha256"]=stable(B); out["qhorn_weights_sha256"]=stable(w)
                        out["decoded_states_sha256"]=stable(states)
                        if len(B)>int(qa["boundary_k"]): out["failure"]="B_EXCEEDS_SELECTED_K"
                        else:
                            reduced=deletion_projection(qa["canonical_clauses"],set(B))
                            ok,detail=verify_weights(reduced,w); out["qhorn_certificate_verified"]=ok
                            if not ok: out["failure"]={"QHORN_WEIGHT_REPLAY_FAIL":detail}
                            else:
                                terminal=qhorn_terminal(reduced,detail["weights"]); out["terminal_replay"]=terminal
                                out["terminal_object_sha256"]=stable(terminal)
                                out["QHORN_WITNESS_REPLAY_VERIFIED"]=bool(terminal.get("terminal_replay_verified"))
                                out["terminal_replay_verified"]=out["QHORN_WITNESS_REPLAY_VERIFIED"]
                                if out["terminal_replay_verified"]:
                                    out["verdict"]="VERIFIED_SAT_QHORN_UPPER_WITNESS"
                                    out["verified_upper_bound"]=len(B)
                                else: out["failure"]="QHORN_TERMINAL_REPLAY_FAIL"
                    except Exception as e: out["failure"]=f"DECODE_OR_REPLAY_ERROR:{type(e).__name__}:{e}"
    Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"index":out["index"],"round":out["round"],"k":out["selected_k"],
                      "PB_MODEL_REPLAY_VERIFIED":out["PB_MODEL_REPLAY_VERIFIED"],
                      "QHORN_WITNESS_REPLAY_VERIFIED":out["QHORN_WITNESS_REPLAY_VERIFIED"],
                      "decoded_B_size":out.get("decoded_B_size"),"verdict":out.get("verdict"),
                      "failure":out.get("failure")},sort_keys=True))
    if out.get("verdict")!="VERIFIED_SAT_QHORN_UPPER_WITNESS": raise SystemExit(2)


if __name__=="__main__": main()
