from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from itertools import product

PAIR=(2,171)
EXPECTED_BOUNDARY=(17,120)
RAW_ASSIGNMENTS=tuple(product((0,1), repeat=2))
LANGUAGE_A="OR_OF_CANONICAL_RESIDUAL_CSP"
LANGUAGE_B="CANONICAL_ROBDD"


def sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def relation_key(c):
    return (tuple(int(v) for v in c["scope"]),tuple(sorted(set(tuple(int(b) for b in row) for row in c["allowed"]))))


def formula_counter(cs):
    return Counter(relation_key(c) for c in cs)


def renamed_key(c,a,b):
    old=[int(v) for v in c["scope"]]
    renamed=[b if v==a else a if v==b else v for v in old]
    new=sorted(renamed)
    rows=[]
    for row in c["allowed"]:
        amap={}
        for v,bit in zip(old,row,strict=True):
            nv=b if v==a else a if v==b else v
            amap[nv]=int(bit)
        rows.append(tuple(amap[v] for v in new))
    return tuple(new),tuple(sorted(set(rows)))


def exact_swap(cs,a,b):
    return formula_counter(cs)==Counter(renamed_key(c,a,b) for c in cs)


def residual(local,bits):
    fixed={PAIR[0]:int(bits[0]),PAIR[1]:int(bits[1])}
    out={}
    for c in local:
        scope=[int(v) for v in c["scope"]]
        remain=[v for v in scope if v not in fixed]
        rows=[]
        for row in c["allowed"]:
            amap={v:int(bit) for v,bit in zip(scope,row,strict=True)}
            if all(amap[v]==value for v,value in fixed.items() if v in amap):
                rows.append(tuple(amap[v] for v in remain))
        rows=sorted(set(rows))
        if not rows:
            return {"unsat":True,"constraints":[]}
        if len(rows)==(1<<len(remain)):
            continue
        k=(tuple(remain),tuple(rows))
        out[k]={"scope":list(remain),"allowed":[list(r) for r in rows]}
    return {"unsat":False,"constraints":[out[k] for k in sorted(out)]}


def symbol_count(cs):
    return sum(1+len(c["scope"])+sum(len(row) for row in c["allowed"]) for c in cs)


class BDD:
    def __init__(self):
        self.nodes={}; self.unique={}; self.next_id=2
        self.acache={}; self.rcache={}
        self.mk_calls=0; self.apply_calls=0
    def mk(self,v,l,h):
        self.mk_calls+=1
        if l==h:return l
        k=(int(v),int(l),int(h))
        if k in self.unique:return self.unique[k]
        i=self.next_id; self.next_id+=1; self.unique[k]=i; self.nodes[i]=k
        return i
    def var(self,v): return self.mk(v,0,1)
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
            self.acache[k]=r; return r
        vu=self.nodes[u][0] if u>=2 else None
        vv=self.nodes[v][0] if v>=2 else None
        top=vv if vu is None else vu if vv is None else min(vu,vv)
        if u>=2 and self.nodes[u][0]==top:_,ul,uh=self.nodes[u]
        else:ul=uh=u
        if v>=2 and self.nodes[v][0]==top:_,vl,vh=self.nodes[v]
        else:vl=vh=v
        r=self.mk(top,self.apply(op,ul,vl),self.apply(op,uh,vh))
        self.acache[k]=r; return r
    def neg(self,u): return self.apply("xor",u,1)
    def restrict(self,u,var,bit):
        k=(int(u),int(var),int(bit))
        if k in self.rcache:return self.rcache[k]
        if u<2:r=u
        else:
            nv,l,h=self.nodes[u]
            if nv==var:r=self.restrict(h if bit else l,var,bit)
            elif nv>var:r=u
            else:r=self.mk(nv,self.restrict(l,var,bit),self.restrict(h,var,bit))
        self.rcache[k]=r; return r
    def tuple_bdd(self,scope,row):
        r=1
        for v,b in zip(scope,row,strict=True):
            lit=self.var(v)
            if not b:lit=self.neg(lit)
            r=self.apply("and",r,lit)
        return r
    def constraint_bdd(self,c):
        r=0
        for row in c["allowed"]:
            r=self.apply("or",r,self.tuple_bdd([int(v) for v in c["scope"]],row))
        return r
    def residual_bdd(self,res):
        if res["unsat"]:return 0
        r=1
        for c in res["constraints"]:
            r=self.apply("and",r,self.constraint_bdd(c))
        return r
    def live(self,root):
        seen=set(); stack=[root]
        while stack:
            u=stack.pop()
            if u<2 or u in seen:continue
            seen.add(u); _,l,h=self.nodes[u]; stack.extend((l,h))
        return len(seen)
    def semhash(self,root):
        memo={0:"FALSE",1:"TRUE"}
        def rec(u):
            if u in memo:return memo[u]
            v,l,h=self.nodes[u]
            memo[u]=sha({"var":v,"low":rec(l),"high":rec(h)})
            return memo[u]
        return rec(root)


def main():
    if len(sys.argv)!=3:
        raise SystemExit("usage: candidate.py SEALED.json OUTPUT.json")
    t0=time.perf_counter()
    bundle=json.load(open(sys.argv[1],encoding="utf-8"))
    ph=bundle.get("payload_sha256")
    payload=dict(bundle); payload.pop("payload_sha256",None)
    if sha(payload)!=ph: raise RuntimeError("SEALED_HASH_MISMATCH")
    if tuple(bundle["frozen_witness"]["cell"])!=PAIR: raise RuntimeError("PAIR_MISMATCH")

    cs=list(bundle["reduced_csp"]["constraints"])
    cell=set(PAIR)
    local=[c for c in cs if cell.intersection(map(int,c["scope"]))]
    exterior=[c for c in cs if not cell.intersection(map(int,c["scope"]))]
    boundary=tuple(sorted({int(v) for c in local for v in c["scope"] if int(v) not in cell}))
    swap_ok=exact_swap(cs,*PAIR)
    structural_ok=len(local)==2 and boundary==EXPECTED_BOUNDARY

    branches={bits:residual(local,bits) for bits in RAW_ASSIGNMENTS}
    bdd=BDD()
    roots={bits:bdd.residual_bdd(branches[bits]) for bits in RAW_ASSIGNMENTS}
    interface_root=0
    for bits in RAW_ASSIGNMENTS:
        interface_root=bdd.apply("or",interface_root,roots[bits])

    unary={}
    product_root=1
    for v in boundary:
        a0=bdd.restrict(interface_root,v,0)!=0
        a1=bdd.restrict(interface_root,v,1)!=0
        unary[str(v)]=[b for b,ok in ((0,a0),(1,a1)) if ok]
        if a0 and a1:continue
        if not a0 and not a1:
            product_root=0; break
        lit=bdd.var(v)
        if a0 and not a1:lit=bdd.neg(lit)
        product_root=bdd.apply("and",product_root,lit)

    if interface_root==1: semantic_class="R_C_TRUE"
    elif interface_root==0: semantic_class="R_C_FALSE"
    elif interface_root==product_root: semantic_class="R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS"
    else: semantic_class="R_C_CORRELATED"

    local_symbols=symbol_count(local)
    raw_symbols=sum(1+symbol_count(branches[b]["constraints"]) for b in RAW_ASSIGNMENTS)
    orcsp_symbols=raw_symbols
    base=local_symbols+len(boundary)+2
    node_bound=base**2
    op_bound=base**4
    live=bdd.live(interface_root)
    ops=bdd.mk_calls+bdd.apply_calls
    bounds=live<=node_bound and ops<=op_bound

    if not swap_ok or not structural_ok:
        verdict="FAIL_NONLOCAL_INFORMATION_REQUIRED"
    elif semantic_class=="R_C_TRUE":
        verdict="FAIL_TRIVIAL_ESCAPE__R_C_TRUE"
    elif semantic_class=="R_C_FALSE":
        verdict="FAIL_TRIVIAL_ESCAPE__R_C_FALSE"
    elif semantic_class=="R_C_NONTRIVIAL_BUT_PRODUCT_OF_UNARY_PROJECTIONS":
        verdict="FAIL_UNARY_FACTORIZATION"
    elif not bounds:
        verdict="FAIL_CLOSURE_BLOWUP"
    else:
        verdict="PASS_LOCAL_EXACT_INTERFACE_NONTRIVIAL_CORRELATED"

    interface={
        "ORCSP":{
            "branches":[
                {"internal_assignment":list(bits),"residual":branches[bits],"residual_sha256":sha(branches[bits])}
                for bits in RAW_ASSIGNMENTS
            ],
            "semantic_definition":"OR over four exact residual CSP branches"
        },
        "ROBDD":{
            "variable_order":list(boundary),
            "semantic_sha256":bdd.semhash(interface_root),
            "unary_product_semantic_sha256":bdd.semhash(product_root)
        }
    }
    result={
        "artifact_id":"JANUS-TRUMP-WALL-MANTEQUILLA-UUF175-018-A-CANDIDATE-v1",
        "source":"UUF175_018",
        "verdict":verdict,
        "semantic_class":semantic_class,
        "sealed_bundle_payload_sha256":ph,
        "frozen_cell":list(PAIR),
        "boundary_variables":list(boundary),
        "local_constraint_count":len(local),
        "exterior_constraint_count":len(exterior),
        "exact_swap_reproduced":swap_ok,
        "structural_authority_reproduced":structural_ok,
        "interface":interface,
        "unary_projections":unary,
        "accounting":{
            "local_input_symbol_count":local_symbols,
            "raw_four_branch_residual_symbol_count":raw_symbols,
            "canonical_orcsp_symbol_count":orcsp_symbols,
            "robdd_live_nonterminal_nodes":live,
            "robdd_node_bound":node_bound,
            "robdd_mk_calls":bdd.mk_calls,
            "robdd_apply_calls":bdd.apply_calls,
            "robdd_total_operations":ops,
            "robdd_operation_bound":op_bound,
            "robdd_bounds_hold":bounds,
            "internal_assignments_constructed":4,
            "constructor_boundary_cube_assignments_enumerated":0,
            "sat_solver_invocations":0,
            "detector_imports":[],
            "wl_imports":[],
            "e3_imports":[]
        },
        "claim_ceiling":"ONE_UNSEEN_FROZEN_K2_ACTIVE_EXACT_SYMMETRY_CELL_WITH_TWO_BIT_BOUNDARY",
        "correlated_not_polynomial_bridge":True,
        "candidate_runtime_seconds":time.perf_counter()-t0
    }
    result["candidate_semantic_digest_sha256"]=sha({
        "verdict":verdict,"semantic_class":semantic_class,"sealed_bundle_payload_sha256":ph,
        "frozen_cell":result["frozen_cell"],"boundary_variables":result["boundary_variables"],
        "interface":interface,"unary_projections":unary,"accounting":result["accounting"]
    })
    json.dump(result,open(sys.argv[2],"w",encoding="utf-8"),indent=2,sort_keys=True)
    open(sys.argv[2],"a",encoding="utf-8").write("\n")
    print(json.dumps({
        "verdict":verdict,"semantic_class":semantic_class,"boundary_variables":list(boundary),
        "robdd_live_nonterminal_nodes":live,"robdd_total_operations":ops,
        "candidate_semantic_digest_sha256":result["candidate_semantic_digest_sha256"]
    },sort_keys=True))


if __name__=="__main__":
    main()
