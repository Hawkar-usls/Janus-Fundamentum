from __future__ import annotations

import ast
import hashlib
import json
import sys
import time
from collections import Counter
from itertools import product

PAIR=(92,190)
BOUNDARY=(77,206)
RAW=tuple(product((0,1),repeat=2))
ALLOWED_IMPORT_ROOTS={"__future__","ast","hashlib","json","sys","time","collections","itertools"}


def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def key(c):
    return (tuple(int(v) for v in c["scope"]),tuple(sorted(set(tuple(int(b) for b in row) for row in c["allowed"]))))


def counter(cs): return Counter(key(c) for c in cs)


def swapped_key(c,a,b):
    old=[int(v) for v in c["scope"]]; renamed=[b if v==a else a if v==b else v for v in old]; new=sorted(renamed)
    rows=[]
    for row in c["allowed"]:
        amap={}
        for v,bit in zip(old,row,strict=True):
            nv=b if v==a else a if v==b else v; amap[nv]=int(bit)
        rows.append(tuple(amap[v] for v in new))
    return tuple(new),tuple(sorted(set(rows)))


def swap_ok(cs,a,b): return counter(cs)==Counter(swapped_key(c,a,b) for c in cs)


def residual(local,bits):
    fixed={PAIR[0]:bits[0],PAIR[1]:bits[1]}; out={}
    for c in local:
        scope=[int(v) for v in c["scope"]]; remain=[v for v in scope if v not in fixed]; rows=[]
        for row in c["allowed"]:
            amap={v:int(bit) for v,bit in zip(scope,row,strict=True)}
            if all(amap[v]==x for v,x in fixed.items() if v in amap):
                rows.append(tuple(amap[v] for v in remain))
        rows=sorted(set(rows))
        if not rows:return {"unsat":True,"constraints":[]}
        if len(rows)==(1<<len(remain)):continue
        k=(tuple(remain),tuple(rows)); out[k]={"scope":list(remain),"allowed":[list(r) for r in rows]}
    return {"unsat":False,"constraints":[out[k] for k in sorted(out)]}


def sat_constraint(c,assignment):
    scope=[int(v) for v in c["scope"]]
    tup=tuple(int(assignment[v]) for v in scope)
    return tup in {tuple(int(b) for b in row) for row in c["allowed"]}


def direct_truth_table(local):
    table={}
    for beta in RAW:
        ba={BOUNDARY[0]:beta[0],BOUNDARY[1]:beta[1]}
        ok=False
        for inner in RAW:
            a=dict(ba); a[PAIR[0]]=inner[0]; a[PAIR[1]]=inner[1]
            if all(sat_constraint(c,a) for c in local):
                ok=True; break
        table["".join(map(str,beta))]=ok
    return table


def residual_eval(res,beta):
    if res["unsat"]:return False
    a={BOUNDARY[0]:beta[0],BOUNDARY[1]:beta[1]}
    return all(sat_constraint(c,a) for c in res["constraints"])


class BDD:
    def __init__(self):
        self.nodes={}; self.unique={}; self.next_id=2; self.ac={}; self.rc={}; self.mk_calls=0; self.apply_calls=0
    def mk(self,v,l,h):
        self.mk_calls+=1
        if l==h:return l
        k=(int(v),int(l),int(h))
        if k in self.unique:return self.unique[k]
        i=self.next_id;self.next_id+=1;self.unique[k]=i;self.nodes[i]=k;return i
    def var(self,v):return self.mk(v,0,1)
    def apply(self,op,u,v):
        self.apply_calls+=1
        if u>v:u,v=v,u
        k=(op,int(u),int(v))
        if k in self.ac:return self.ac[k]
        if u<2 and v<2:
            r=int((bool(u) and bool(v)) if op=="and" else (bool(u) or bool(v)) if op=="or" else (bool(u)^bool(v)))
            self.ac[k]=r;return r
        vu=self.nodes[u][0] if u>=2 else None; vv=self.nodes[v][0] if v>=2 else None
        top=vv if vu is None else vu if vv is None else min(vu,vv)
        if u>=2 and self.nodes[u][0]==top:_,ul,uh=self.nodes[u]
        else:ul=uh=u
        if v>=2 and self.nodes[v][0]==top:_,vl,vh=self.nodes[v]
        else:vl=vh=v
        r=self.mk(top,self.apply(op,ul,vl),self.apply(op,uh,vh));self.ac[k]=r;return r
    def neg(self,u):return self.apply("xor",u,1)
    def restrict(self,u,var,bit):
        k=(u,var,bit)
        if k in self.rc:return self.rc[k]
        if u<2:r=u
        else:
            nv,l,h=self.nodes[u]
            if nv==var:r=self.restrict(h if bit else l,var,bit)
            elif nv>var:r=u
            else:r=self.mk(nv,self.restrict(l,var,bit),self.restrict(h,var,bit))
        self.rc[k]=r;return r
    def tb(self,scope,row):
        r=1
        for v,b in zip(scope,row,strict=True):
            lit=self.var(v)
            if not b:lit=self.neg(lit)
            r=self.apply("and",r,lit)
        return r
    def cb(self,c):
        r=0
        for row in c["allowed"]:r=self.apply("or",r,self.tb([int(v) for v in c["scope"]],row))
        return r
    def rb(self,res):
        if res["unsat"]:return 0
        r=1
        for c in res["constraints"]:r=self.apply("and",r,self.cb(c))
        return r
    def eval(self,root,beta):
        a={BOUNDARY[0]:beta[0],BOUNDARY[1]:beta[1]};u=root
        while u>=2:
            v,l,h=self.nodes[u];u=h if a[v] else l
        return bool(u)
    def semhash(self,root):
        memo={0:"FALSE",1:"TRUE"}
        def rec(u):
            if u in memo:return memo[u]
            v,l,h=self.nodes[u];memo[u]=sha({"var":v,"low":rec(l),"high":rec(h)});return memo[u]
        return rec(root)
    def live(self,root):
        seen=set();stack=[root]
        while stack:
            u=stack.pop()
            if u<2 or u in seen:continue
            seen.add(u);_,l,h=self.nodes[u];stack.extend((l,h))
        return len(seen)


def audit(path):
    text=open(path,encoding="utf-8").read();tree=ast.parse(text);imports=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
        elif isinstance(n,ast.ImportFrom):imports.append(n.module or "")
    roots={x.split(".",1)[0] for x in imports}
    forbidden=sorted(roots-ALLOWED_IMPORT_ROOTS)
    bad_tokens=[t for t in ["subprocess","socket","requests","urllib","research.tools","z3","pysat","boundary_truth_table"] if t in text]
    return {"imports":sorted(imports),"forbidden_imports":forbidden,"forbidden_token_hits":bad_tokens,"pass":not forbidden and not bad_tokens}


def symbols(cs):return sum(1+len(c["scope"])+sum(len(row) for row in c["allowed"]) for c in cs)


def main():
    if len(sys.argv)!=5:raise SystemExit("usage: independent_check.py SEALED CANDIDATE CANDIDATE_SOURCE OUTPUT")
    t0=time.perf_counter()
    bundle=json.load(open(sys.argv[1],encoding="utf-8"));cand=json.load(open(sys.argv[2],encoding="utf-8"));source_audit=audit(sys.argv[3])
    ph=bundle["payload_sha256"];payload=dict(bundle);payload.pop("payload_sha256",None);bundle_ok=sha(payload)==ph
    cs=list(bundle["reduced_csp"]["constraints"]);cell=set(PAIR)
    local=[c for c in cs if cell.intersection(map(int,c["scope"]))];ext=[c for c in cs if not cell.intersection(map(int,c["scope"]))]
    boundary=tuple(sorted({int(v) for c in local for v in c["scope"] if int(v) not in cell}))
    exact=swap_ok(cs,*PAIR)
    branches={bits:residual(local,bits) for bits in RAW}

    dd=BDD();roots={bits:dd.rb(branches[bits]) for bits in RAW};root=0
    for bits in RAW:root=dd.apply("or",root,roots[bits])
    unary={};prod=1
    for v in boundary:
        a0=dd.restrict(root,v,0)!=0;a1=dd.restrict(root,v,1)!=0;unary[str(v)]=[b for b,ok in ((0,a0),(1,a1)) if ok]
        if a0 and a1:continue
        if not a0 and not a1:prod=0;break
        lit=dd.var(v)
        if a0 and not a1:lit=dd.neg(lit)
        prod=dd.apply("and",prod,lit)
    if root==1:semantic="R_C_TRUE"
    elif root==0:semantic="R_C_FALSE"
    elif root==prod:semantic="R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS"
    else:semantic="R_C_CORRELATED"

    direct=direct_truth_table(local)
    orcsp_table={}
    robdd_table={}
    for beta in RAW:
        k="".join(map(str,beta))
        orcsp_table[k]=any(residual_eval(branches[inner],beta) for inner in RAW)
        robdd_table[k]=dd.eval(root,beta)

    local_symbols=symbols(local);raw_symbols=sum(1+symbols(branches[b]["constraints"]) for b in RAW)
    base=local_symbols+len(boundary)+2;node_bound=base**2;op_bound=base**4;live=dd.live(root);ops=dd.mk_calls+dd.apply_calls
    bounds=live<=node_bound and ops<=op_bound
    if not exact or len(local)!=2 or boundary!=BOUNDARY: expected="FAIL_NONLOCAL_INFORMATION_REQUIRED"
    elif semantic=="R_C_TRUE":expected="FAIL_TRIVIAL_ESCAPE__R_C_TRUE"
    elif semantic=="R_C_FALSE":expected="FAIL_TRIVIAL_ESCAPE__R_C_FALSE"
    elif semantic=="R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS":expected="FAIL_UNARY_FACTORIZATION"
    elif not bounds:expected="FAIL_CLOSURE_BLOWUP"
    else:expected="PASS_LOCAL_EXACT_INTERFACE_NONTRIVIAL_CORRELATED"

    expected_interface={
        "ORCSP":{"branches":[{"internal_assignment":list(bits),"residual":branches[bits],"residual_sha256":sha(branches[bits])} for bits in RAW],"semantic_definition":"OR over four exact residual CSP branches"},
        "ROBDD":{"variable_order":list(boundary),"semantic_sha256":dd.semhash(root),"unary_product_semantic_sha256":dd.semhash(prod)}
    }
    checks={
        "bundle_hash_ok":bundle_ok,
        "candidate_bundle_hash_matches":cand.get("sealed_bundle_payload_sha256")==ph,
        "pair_matches":cand.get("frozen_cell")==list(PAIR),
        "boundary_matches":cand.get("boundary_variables")==list(BOUNDARY),
        "local_count_two":cand.get("local_constraint_count")==2 and len(local)==2,
        "exact_swap_matches":cand.get("exact_swap_reproduced") is exact and exact,
        "interface_exact_match":cand.get("interface")==expected_interface,
        "semantic_class_matches":cand.get("semantic_class")==semantic,
        "unary_projection_matches":cand.get("unary_projections")==unary,
        "verdict_matches":cand.get("verdict")==expected,
        "direct_truth_equals_orcsp":direct==orcsp_table,
        "direct_truth_equals_robdd":direct==robdd_table,
        "orcsp_equals_robdd":orcsp_table==robdd_table,
        "constructor_cube_zero":cand.get("accounting",{}).get("constructor_boundary_cube_assignments_enumerated")==0,
        "sat_calls_zero":cand.get("accounting",{}).get("sat_solver_invocations")==0,
        "detector_imports_zero":cand.get("accounting",{}).get("detector_imports")==[],
        "wl_imports_zero":cand.get("accounting",{}).get("wl_imports")==[],
        "e3_imports_zero":cand.get("accounting",{}).get("e3_imports")==[],
        "orcsp_symbols_match":cand.get("accounting",{}).get("canonical_orcsp_symbol_count")==raw_symbols,
        "robdd_nodes_match":cand.get("accounting",{}).get("robdd_live_nonterminal_nodes")==live,
        "robdd_ops_match":cand.get("accounting",{}).get("robdd_total_operations")==ops,
        "robdd_bounds_match":cand.get("accounting",{}).get("robdd_bounds_hold") is bounds,
        "candidate_source_audit_pass":source_audit["pass"]
    }
    verified=all(checks.values())
    out={
        "artifact_id":"JANUS-TRUMP-WALL-MANTEQUILLA-UUF250-070-DEPTH-INDEPENDENT-CHECK-v1",
        "verdict":"PASS_INDEPENDENT_UUF250_070_MANTEQUILLA_VERIFICATION" if verified else "FAIL_INDEPENDENT_UUF250_070_MANTEQUILLA_VERIFICATION",
        "scientific_verdict":expected,
        "semantic_class":semantic,
        "checks":checks,
        "candidate_source_audit":source_audit,
        "checker_only_semantic_microscope":{
            "boundary_variable_order":list(BOUNDARY),
            "boundary_assignments_enumerated":4,
            "direct_local_existential_truth_table":direct,
            "orcsp_truth_table":orcsp_table,
            "robdd_truth_table":robdd_table,
            "constructor_did_not_use_this_cube":True,
            "no_scalability_inference":True
        },
        "independent_measurements":{
            "local_constraint_count":len(local),"exterior_constraint_count":len(ext),"boundary_variables":list(boundary),
            "local_input_symbol_count":local_symbols,"canonical_orcsp_symbol_count":raw_symbols,
            "robdd_live_nonterminal_nodes":live,"robdd_node_bound":node_bound,
            "robdd_total_operations":ops,"robdd_operation_bound":op_bound,"robdd_bounds_hold":bounds,
            "robdd_semantic_sha256":dd.semhash(root),"unary_product_semantic_sha256":dd.semhash(prod)
        },
        "claim_ceiling":"ONE_UNSEEN_FROZEN_K2_ACTIVE_EXACT_SYMMETRY_CELL_WITH_TWO_BIT_BOUNDARY",
        "independent_checker_runtime_seconds":time.perf_counter()-t0
    }
    out["independent_semantic_digest_sha256"]=sha({"scientific_verdict":expected,"semantic_class":semantic,"checks":checks,"truth_table":direct,"measurements":out["independent_measurements"]})
    json.dump(out,open(sys.argv[4],"w",encoding="utf-8"),indent=2,sort_keys=True);open(sys.argv[4],"a",encoding="utf-8").write("\n")
    print(json.dumps({"verdict":out["verdict"],"scientific_verdict":expected,"semantic_class":semantic,"truth_table":direct,"checks_passed":sum(bool(v) for v in checks.values()),"checks_total":len(checks)},sort_keys=True))
    if not verified:raise SystemExit(1)


if __name__=="__main__":
    main()
