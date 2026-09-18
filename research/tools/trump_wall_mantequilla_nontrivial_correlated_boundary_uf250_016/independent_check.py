from __future__ import annotations

import ast
import hashlib
import json
import sys
import time
from collections import Counter
from itertools import product

CELL = (61, 91, 237)
GENERATORS = ((61, 91), (61, 237), (91, 237))
RAW = tuple(product((0, 1), repeat=3))
REPS = {0:(0,0,0),1:(0,0,1),2:(0,1,1),3:(1,1,1)}
ALLOWED_IMPORT_ROOTS = {
    "__future__", "ast", "hashlib", "json", "sys", "time", "collections", "itertools"
}


def sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def key(c):
    return (
        tuple(int(v) for v in c["scope"]),
        tuple(sorted(set(tuple(int(b) for b in row) for row in c["allowed"]))),
    )


def fcounter(constraints):
    return Counter(key(c) for c in constraints)


def swapped_key(c, a, b):
    old_scope=[int(v) for v in c["scope"]]
    renamed=[b if v==a else a if v==b else v for v in old_scope]
    new_scope=sorted(renamed)
    rows=[]
    for row in c["allowed"]:
        amap={}
        for v,bit in zip(old_scope,row,strict=True):
            nv=b if v==a else a if v==b else v
            amap[nv]=int(bit)
        rows.append(tuple(amap[v] for v in new_scope))
    return tuple(new_scope),tuple(sorted(set(rows)))


def swap_ok(constraints,a,b):
    return fcounter(constraints)==Counter(swapped_key(c,a,b) for c in constraints)


def residual(local,bits):
    fixed={CELL[i]:int(bits[i]) for i in range(3)}
    out={}
    for c in local:
        scope=[int(v) for v in c["scope"]]
        remain=[v for v in scope if v not in fixed]
        rows=[]
        for row in c["allowed"]:
            amap={v:int(bit) for v,bit in zip(scope,row,strict=True)}
            if all(amap[v]==x for v,x in fixed.items() if v in amap):
                rows.append(tuple(amap[v] for v in remain))
        rows=sorted(set(rows))
        if not rows:
            return {"unsat":True,"constraints":[]}
        if len(rows)==(1<<len(remain)):
            continue
        k=(tuple(remain),tuple(rows))
        out[k]={"scope":list(remain),"allowed":[list(r) for r in rows]}
    return {"unsat":False,"constraints":[out[k] for k in sorted(out)]}


def symbol_count(constraints):
    return sum(1+len(c["scope"])+sum(len(row) for row in c["allowed"]) for c in constraints)


class DD:
    def __init__(self):
        self.nodes={}
        self.unique={}
        self.next_id=2
        self.acache={}
        self.rcache={}
        self.apply_calls=0
        self.mk_calls=0

    def mk(self,v,l,h):
        self.mk_calls+=1
        if l==h:return l
        k=(int(v),int(l),int(h))
        if k in self.unique:return self.unique[k]
        i=self.next_id;self.next_id+=1
        self.unique[k]=i;self.nodes[i]=k
        return i

    def var(self,v):return self.mk(int(v),0,1)

    def apply(self,op,u,v):
        self.apply_calls+=1
        if u>v:u,v=v,u
        k=(op,int(u),int(v))
        if k in self.acache:return self.acache[k]
        if u<2 and v<2:
            if op=="and":r=int(bool(u) and bool(v))
            elif op=="or":r=int(bool(u) or bool(v))
            elif op=="xor":r=int(bool(u)^bool(v))
            else:raise ValueError(op)
            self.acache[k]=r;return r
        vu=self.nodes[u][0] if u>=2 else None
        vv=self.nodes[v][0] if v>=2 else None
        top=vv if vu is None else vu if vv is None else min(vu,vv)
        if u>=2 and self.nodes[u][0]==top:_,ul,uh=self.nodes[u]
        else:ul=uh=u
        if v>=2 and self.nodes[v][0]==top:_,vl,vh=self.nodes[v]
        else:vl=vh=v
        r=self.mk(top,self.apply(op,ul,vl),self.apply(op,uh,vh))
        self.acache[k]=r
        return r

    def neg(self,u):return self.apply("xor",u,1)

    def restrict(self,u,v,b):
        k=(int(u),int(v),int(b))
        if k in self.rcache:return self.rcache[k]
        if u<2:r=u
        else:
            nv,l,h=self.nodes[u]
            if nv==v:r=self.restrict(h if b else l,v,b)
            elif nv>v:r=u
            else:r=self.mk(nv,self.restrict(l,v,b),self.restrict(h,v,b))
        self.rcache[k]=r
        return r

    def tuple(self,scope,row):
        r=1
        for v,b in zip(scope,row,strict=True):
            lit=self.var(v)
            if not b:lit=self.neg(lit)
            r=self.apply("and",r,lit)
        return r

    def constraint(self,c):
        r=0
        for row in c["allowed"]:
            r=self.apply("or",r,self.tuple([int(v) for v in c["scope"]],row))
        return r

    def branch(self,res):
        if res["unsat"]:return 0
        r=1
        for c in res["constraints"]:
            r=self.apply("and",r,self.constraint(c))
        return r

    def live(self,root):
        seen=set();stack=[root]
        while stack:
            u=stack.pop()
            if u<2 or u in seen:continue
            seen.add(u)
            _,l,h=self.nodes[u];stack.extend((l,h))
        return len(seen)

    def semhash(self,root):
        memo={0:"FALSE",1:"TRUE"}
        def rec(u):
            if u in memo:return memo[u]
            v,l,h=self.nodes[u]
            memo[u]=sha({"var":v,"low":rec(l),"high":rec(h)})
            return memo[u]
        return rec(root)


def audit_candidate(path):
    text=open(path,"r",encoding="utf-8").read()
    tree=ast.parse(text)
    imports=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node,ast.ImportFrom):
            imports.append(node.module or "")
    roots={x.split(".",1)[0] for x in imports}
    forbidden=sorted(roots-ALLOWED_IMPORT_ROOTS)
    bad_tokens=[
        "subprocess","socket","requests","urllib","importlib",
        "research.tools","z3","pysat","ortools"
    ]
    hits=sorted(t for t in bad_tokens if t in text)
    return {
        "imports":sorted(imports),
        "forbidden_imports":forbidden,
        "forbidden_token_hits":hits,
        "pass":not forbidden and not hits,
    }


def main():
    if len(sys.argv)!=5:
        raise SystemExit("usage: independent_check.py SEALED.json CANDIDATE.json CANDIDATE_SOURCE.py OUTPUT.json")
    t0=time.perf_counter()
    bundle=json.load(open(sys.argv[1],"r",encoding="utf-8"))
    candidate=json.load(open(sys.argv[2],"r",encoding="utf-8"))
    source_audit=audit_candidate(sys.argv[3])

    ph=bundle.get("payload_sha256")
    payload=dict(bundle);payload.pop("payload_sha256",None)
    bundle_ok=sha(payload)==ph

    reduced=bundle["reduced_csp"]
    constraints=list(reduced["constraints"])
    cell=set(CELL)
    local=[c for c in constraints if cell.intersection(map(int,c["scope"]))]
    exterior=[c for c in constraints if not cell.intersection(map(int,c["scope"]))]
    boundary=sorted({int(v) for c in local for v in c["scope"] if int(v) not in cell})

    gchecks={f"{a}_{b}":swap_ok(constraints,a,b) for a,b in GENERATORS}
    s3=all(gchecks.values())

    branches={bits:residual(local,bits) for bits in RAW}
    orbit_id={}
    for w in range(4):
        members=[bits for bits in RAW if sum(bits)==w]
        orbit_id[str(w)]=len({json.dumps(branches[b],sort_keys=True,separators=(",",":")) for b in members})==1

    dd=DD()
    roots={bits:dd.branch(branches[bits]) for bits in RAW}
    true_branch=any(r==1 for r in roots.values())

    root=0
    retained=[]
    for w in range(4):
        bits=REPS[w]
        br=roots[bits]
        root=dd.apply("or",root,br)
        retained.append({
            "hamming_weight":w,
            "representative":list(bits),
            "residual":branches[bits],
            "residual_sha256":sha(branches[bits]),
            "bdd_semantic_sha256":dd.semhash(br),
        })

    constant=root in (0,1)
    unary={}
    product_root=1
    for v in boundary:
        a0=dd.restrict(root,v,0)!=0
        a1=dd.restrict(root,v,1)!=0
        unary[str(v)]=[b for b,ok in ((0,a0),(1,a1)) if ok]
        if a0 and a1:continue
        if not a0 and not a1:
            product_root=0;break
        lit=dd.var(v)
        if a0 and not a1:lit=dd.neg(lit)
        product_root=dd.apply("and",product_root,lit)

    unary_factorized=root==product_root
    correlated=not unary_factorized

    local_symbols=symbol_count(local)
    base=local_symbols+len(boundary)+2
    node_bound=base**2
    op_bound=base**4
    live=dd.live(root)
    ops=dd.apply_calls+dd.mk_calls
    bounds=live<=node_bound and ops<=op_bound

    if not s3 or not all(orbit_id.values()):
        expected="FAIL_NONLOCAL_INFORMATION_REQUIRED"
    elif true_branch or len(boundary)<2 or constant:
        expected="FAIL_TRIVIAL_ESCAPE"
    elif not bounds:
        expected="FAIL_CLOSURE_BLOWUP"
    elif unary_factorized:
        expected="FAIL_UNARY_FACTORIZATION"
    else:
        expected="PASS_NONTRIVIAL_CORRELATED_BRIDGE"

    expected_interface={
        "semantics":"EXISTS_x61_x91_x237_LOCAL_CSP",
        "retained_orbit_branches":retained,
        "exactness_method":"STRUCTURAL_SHANNON_THREE_VAR_PLUS_EXACT_S3_WEIGHT_ORBIT_IDENTITY",
        "robdd_semantic_sha256":dd.semhash(root),
        "unary_product_robdd_semantic_sha256":dd.semhash(product_root),
    }
    accounting=candidate.get("accounting",{})
    audit=candidate.get("semantic_audit",{})

    checks={
        "bundle_hash_ok":bundle_ok,
        "candidate_bundle_hash_matches":candidate.get("sealed_bundle_payload_sha256")==ph,
        "frozen_cell_matches":candidate.get("frozen_cell")==list(CELL),
        "generator_checks_match":candidate.get("generator_checks")==gchecks,
        "s3_invariance_matches":candidate.get("full_s3_generator_invariance") is s3,
        "local_count_matches":candidate.get("local_constraint_count")==len(local),
        "exterior_count_matches":candidate.get("exterior_constraint_count")==len(exterior),
        "boundary_matches":candidate.get("boundary_variables")==boundary,
        "orbit_identity_matches":candidate.get("equal_weight_residual_identity")==orbit_id,
        "true_branch_matches":candidate.get("any_true_raw_branch") is true_branch,
        "raw_residual_hashes_match":candidate.get("raw_branch_residual_sha256")=={
            "".join(map(str,b)):sha(branches[b]) for b in RAW
        },
        "interface_exact_match":candidate.get("interface")==expected_interface,
        "constant_audit_matches":audit.get("interface_is_constant") is constant,
        "unary_projection_matches":audit.get("unary_projections")==unary,
        "unary_factorization_matches":audit.get("unary_factorized") is unary_factorized,
        "correlation_matches":audit.get("genuine_joint_correlation") is (correlated and not constant),
        "local_symbols_match":accounting.get("local_input_symbol_count")==local_symbols,
        "bdd_live_nodes_match":accounting.get("robdd_live_nonterminal_nodes")==live,
        "bdd_node_bound_matches":accounting.get("robdd_node_bound")==node_bound,
        "bdd_ops_match":accounting.get("robdd_total_operations")==ops,
        "bdd_op_bound_matches":accounting.get("robdd_operation_bound")==op_bound,
        "bdd_bounds_match":accounting.get("robdd_bounds_hold") is bounds,
        "eight_assignments_only":accounting.get("internal_assignments_constructed")==8,
        "boundary_cube_zero":accounting.get("boundary_cube_assignments_enumerated")==0,
        "sat_solver_zero":accounting.get("sat_solver_invocations")==0,
        "full_search_zero":accounting.get("full_transposition_searches")==0,
        "frozen_generator_checks_three":accounting.get("frozen_generator_checks")==3,
        "detector_imports_zero":accounting.get("detector_imports")==[],
        "wl_imports_zero":accounting.get("wl_imports")==[],
        "e3_imports_zero":accounting.get("e3_imports")==[],
        "candidate_source_audit_pass":source_audit["pass"],
        "candidate_verdict_matches":candidate.get("verdict")==expected,
    }
    verified=all(checks.values())

    out={
        "artifact_id":"JANUS-TRUMP-WALL-MANTEQUILLA-NONTRIVIAL-CORRELATED-BOUNDARY-UF250-016-INDEPENDENT-CHECK-v1",
        "verdict":"PASS_INDEPENDENT_MANTEQUILLA_NONTRIVIAL_CORRELATED_BOUNDARY_VERIFICATION" if verified else "FAIL_INDEPENDENT_MANTEQUILLA_NONTRIVIAL_CORRELATED_BOUNDARY_VERIFICATION",
        "scientific_verdict":expected,
        "candidate_imported":False,
        "checks":checks,
        "candidate_source_audit":source_audit,
        "independent_measurements":{
            "local_constraint_count":len(local),
            "exterior_constraint_count":len(exterior),
            "boundary_variable_count":len(boundary),
            "boundary_variables":boundary,
            "full_s3_generator_invariance":s3,
            "equal_weight_residual_identity":orbit_id,
            "any_true_raw_branch":true_branch,
            "interface_is_constant":constant,
            "unary_projections":unary,
            "unary_factorized":unary_factorized,
            "genuine_joint_correlation":correlated and not constant,
            "local_input_symbol_count":local_symbols,
            "robdd_live_nonterminal_nodes":live,
            "robdd_node_bound":node_bound,
            "robdd_total_operations":ops,
            "robdd_operation_bound":op_bound,
            "robdd_bounds_hold":bounds,
            "robdd_semantic_sha256":dd.semhash(root),
            "unary_product_robdd_semantic_sha256":dd.semhash(product_root),
        },
        "sealed_bundle_payload_sha256":ph,
        "claim_ceiling":"ONE_FROZEN_K3_EXACT_SYMMETRY_CELL__NONTRIVIAL_BOUNDARY_INTERFACE_ONLY",
        "independent_checker_runtime_seconds":time.perf_counter()-t0,
    }
    out["independent_semantic_digest_sha256"]=sha({
        "scientific_verdict":expected,
        "checks":checks,
        "independent_measurements":out["independent_measurements"],
        "sealed_bundle_payload_sha256":ph,
    })
    json.dump(out,open(sys.argv[4],"w",encoding="utf-8"),indent=2,sort_keys=True)
    open(sys.argv[4],"a",encoding="utf-8").write("\n")
    print(json.dumps({
        "verdict":out["verdict"],
        "scientific_verdict":expected,
        "checks_passed":sum(bool(v) for v in checks.values()),
        "checks_total":len(checks),
        "boundary_variable_count":len(boundary),
        "any_true_raw_branch":true_branch,
        "interface_is_constant":constant,
        "unary_factorized":unary_factorized,
        "genuine_joint_correlation":correlated and not constant,
        "robdd_live_nonterminal_nodes":live,
        "robdd_node_bound":node_bound,
        "independent_semantic_digest_sha256":out["independent_semantic_digest_sha256"],
    },sort_keys=True))
    if not verified:
        raise SystemExit(1)


if __name__=="__main__":
    main()
