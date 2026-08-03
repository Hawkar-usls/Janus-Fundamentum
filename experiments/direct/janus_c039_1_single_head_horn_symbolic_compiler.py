#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

CANONICAL_ID = "C039.1"
LANGUAGE_PROFILE = "SINGLE_HEAD_HORN_V1"
MESSAGE_SCHEMA = "janus.c039.1.single-head-horn-message.v1"
OP_SCHEMA = "janus.c039.1.single-head-horn-operation.v1"
EVALUATION_SCHEMA = "janus.c039.1.vtree-evaluation.v1"
SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
ATOM = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]*$")
FORBIDDEN_KEYS = {"assignments","assignment_rows","communication_rows","evaluation_vector",
                  "row_matrix","truth_table","truth_table_blob","raw_bitmap",
                  "assignment_index","lookup_table","models","rows"}

HORN_LEAF_IMPLEMENTED = True
HORN_JOIN_IMPLEMENTED = True
HORN_PROJECT_IMPLEMENTED = True
HORN_MERGE_IMPLEMENTED = False
HORN_SEPARATE_IMPLEMENTED = False
GENERAL_HORN_IMPLEMENTED = False
VTREE_DISCOVERY_IMPLEMENTED = False
CAPABILITY = {
    "schema":"janus.c039.1.capability.v1", "canonical_id":CANONICAL_ID,
    "language_profile":LANGUAGE_PROFILE,
    "HORN_LEAF_IMPLEMENTED":HORN_LEAF_IMPLEMENTED,
    "HORN_JOIN_IMPLEMENTED":HORN_JOIN_IMPLEMENTED,
    "HORN_PROJECT_IMPLEMENTED":HORN_PROJECT_IMPLEMENTED,
    "HORN_MERGE_IMPLEMENTED":HORN_MERGE_IMPLEMENTED,
    "HORN_SEPARATE_IMPLEMENTED":HORN_SEPARATE_IMPLEMENTED,
    "GENERAL_HORN_IMPLEMENTED":GENERAL_HORN_IMPLEMENTED,
    "VTREE_DISCOVERY_IMPLEMENTED":VTREE_DISCOVERY_IMPLEMENTED,
}

class Terminal(str, Enum):
    FACTOR_BUILT="FACTOR_BUILT"; CLOSED_POLY="CLOSED_POLY"
    OPEN_LANGUAGE="OPEN_LANGUAGE"; OPEN_BUDGET="OPEN_BUDGET"
    OPEN_REPRESENTATION_GROWTH="OPEN_REPRESENTATION_GROWTH"
    INVALID_CERTIFICATE="INVALID_CERTIFICATE"
class Reason(str, Enum):
    NONE="NONE"; SINGLE_HEAD_CLOSURE_LOST="SINGLE_HEAD_CLOSURE_LOST"
    PROJECTION_VOLUME="PROJECTION_VOLUME"; WORK_UNITS="WORK_UNITS"
    INVALID_RULE="INVALID_RULE"; INVALID_SCOPE="INVALID_SCOPE"
    INVALID_VTREE="INVALID_VTREE"; UNSUPPORTED_OPERATOR="UNSUPPORTED_OPERATOR"

DOM={k:(f"JANUS-C039.1-{k}-V1\0").encode() for k in
     ("RULE","MESSAGE","OP","EVALUATION","CAPABILITY","VTREE","FORMULA","BUDGET")}

def canonical_json(x: Any) -> bytes:
    def check(v: Any) -> None:
        if v is None or isinstance(v,(str,bool,int)): return
        if isinstance(v,float): raise TypeError("floats forbidden")
        if isinstance(v,list):
            for z in v: check(z)
            return
        if isinstance(v,dict) and all(isinstance(k,str) for k in v):
            for k,z in v.items():
                if k.lower() in FORBIDDEN_KEYS: raise ValueError("enumerative field")
                check(z)
            return
        raise TypeError("non-canonical JSON")
    check(x)
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def h(kind: str, x: Any) -> str:
    return "sha256:"+hashlib.sha256(DOM[kind]+canonical_json(x)).hexdigest()

def atom(x: Any) -> str:
    if not isinstance(x,str) or ATOM.fullmatch(x) is None: raise ValueError("invalid atom")
    return x

@dataclass(frozen=True, order=True)
class Rule:
    body: tuple[str,...]
    head: str|None
    @property
    def literals(self)->int: return len(self.body)+(self.head is not None)
    def payload(self)->dict[str,Any]: return {"body":list(self.body),"head":self.head}
    @property
    def digest(self)->str: return h("RULE",self.payload())

@dataclass(frozen=True)
class Budget:
    max_message_rules:int; max_message_literals:int; max_total_work:int
    def __post_init__(self):
        if min(self.max_message_rules,self.max_message_literals,self.max_total_work)<0: raise ValueError("budget")
    def payload(self): return self.__dict__
    @property
    def digest(self): return h("BUDGET",self.payload())

@dataclass(frozen=True)
class Message:
    scope:tuple[str,...]; boundary:tuple[str,...]; rules:tuple[Rule,...]
    def payload(self):
        return {"schema":MESSAGE_SCHEMA,"language_profile":LANGUAGE_PROFILE,"payload_type":"HORN_CLOSURE",
                "scope":list(self.scope),"boundary":list(self.boundary),"rules":[r.payload() for r in self.rules]}
    @property
    def digest(self): return h("MESSAGE",self.payload())
    @property
    def rule_count(self): return len(self.rules)
    @property
    def literal_count(self): return sum(r.literals for r in self.rules)

@dataclass(frozen=True)
class Result:
    terminal:Terminal; reason_code:Reason; output_message:Message|None
    operation_certificate:Mapping[str,Any]; growth_certificate:Mapping[str,Any]|None=None
    @property
    def output_message_digest(self): return None if self.output_message is None else self.output_message.digest

@dataclass(frozen=True)
class VTreeNode:
    node_id:str; boundary:tuple[str,...]; variable:str|None=None
    left:"VTreeNode|None"=None; right:"VTreeNode|None"=None
    @property
    def leaf(self): return self.variable is not None

@dataclass(frozen=True)
class EvaluationResult:
    certificate:Mapping[str,Any]
    @property
    def terminal(self): return Terminal(self.certificate["terminal"])
    @property
    def root_message_digest(self): return self.certificate["root_message_digest"]

def normalize_rule(x: Rule|Mapping[str,Any])->Rule|None:
    body,head=(x.body,x.head) if isinstance(x,Rule) else (x.get("body"),x.get("head"))
    if not isinstance(body,(list,tuple)): raise ValueError("body")
    b=tuple(sorted({atom(a) for a in body})); hd=None if head is None else atom(head)
    return None if hd in b else Rule(b,hd)

def normalize_rules(xs:Iterable[Rule|Mapping[str,Any]])->tuple[Rule,...]:
    out:set[Rule]=set(); heads:dict[str,Rule]={}
    for x in xs:
        r=normalize_rule(x)
        if r is None: continue
        if r.head is not None and r.head in heads and heads[r.head]!=r: raise ValueError("single-head closure lost")
        if r.head is not None: heads[r.head]=r
        out.add(r)
    return tuple(sorted(out))

def make_message(scope:Iterable[str],boundary:Iterable[str],rules:Iterable[Rule|Mapping[str,Any]])->Message:
    s=tuple(sorted({atom(x) for x in scope})); b=tuple(sorted({atom(x) for x in boundary}))
    if not set(b)<=set(s): raise ValueError("boundary")
    rs=normalize_rules(rules)
    if any((set(r.body)|({r.head} if r.head else set()))-set(s) for r in rs): raise ValueError("scope")
    return Message(s,b,rs)

def cap_digest(): return h("CAPABILITY",CAPABILITY)
def cert(operator:str,terminal:Terminal,reason:Reason,inputs:list[str],output:Message|None,budget:Budget,work:int,proof:Any)->dict[str,Any]:
    c={"schema":OP_SCHEMA,"canonical_id":CANONICAL_ID,"operator":operator,"terminal":terminal.value,
       "reason_code":reason.value,"capability_digest":cap_digest(),"language_profile":LANGUAGE_PROFILE,
       "input_message_digests":inputs,"output_message_digest":None if output is None else output.digest,
       "work_units":work,"budget_digest":budget.digest,"proof_payload":proof}
    c["operation_digest"]=h("OP",c); return c

def bad(op:str,b:Budget,reason=Reason.INVALID_RULE)->Result:
    return Result(Terminal.INVALID_CERTIFICATE,reason,None,cert(op,Terminal.INVALID_CERTIFICATE,reason,[],None,b,0,{}))
def over(op:str,b:Budget,inputs:list[str],work:int,proof:Any)->Result:
    return Result(Terminal.OPEN_BUDGET,Reason.WORK_UNITS,None,cert(op,Terminal.OPEN_BUDGET,Reason.WORK_UNITS,inputs,None,b,work,proof))

def leaf(rules:Iterable[Rule|Mapping[str,Any]],scope:Iterable[str],boundary:Iterable[str],budget:Budget)->Result:
    try: m=make_message(scope,boundary,rules)
    except ValueError as e:
        reason=Reason.SINGLE_HEAD_CLOSURE_LOST if "single-head" in str(e) else Reason.INVALID_RULE
        t=Terminal.OPEN_LANGUAGE if reason is Reason.SINGLE_HEAD_CLOSURE_LOST else Terminal.INVALID_CERTIFICATE
        return Result(t,reason,None,cert("LEAF",t,reason,[],None,budget,0,{"error":str(e)}))
    work=m.rule_count+m.literal_count
    if work>budget.max_total_work: return over("LEAF",budget,[],work,{"native_replay":True})
    if m.rule_count>budget.max_message_rules or m.literal_count>budget.max_message_literals:
        return Result(Terminal.OPEN_REPRESENTATION_GROWTH,Reason.PROJECTION_VOLUME,None,
                      cert("LEAF",Terminal.OPEN_REPRESENTATION_GROWTH,Reason.PROJECTION_VOLUME,[],None,budget,work,{"native_replay":True}))
    return Result(Terminal.FACTOR_BUILT,Reason.NONE,m,cert("LEAF",Terminal.FACTOR_BUILT,Reason.NONE,[],m,budget,work,{"native_replay":True,"rules":[r.digest for r in m.rules]}))

def join(left:Message,right:Message,local_rules:Iterable[Rule|Mapping[str,Any]],output_scope:Iterable[str],budget:Budget)->Result:
    inputs=[left.digest,right.digest]
    if set(left.scope)&set(right.scope): return bad("JOIN",budget,Reason.INVALID_SCOPE)
    try:
        scope=tuple(sorted({atom(x) for x in output_scope}))
        if set(scope)!=set(left.scope)|set(right.scope): raise ValueError("scope")
        m=make_message(scope,tuple(sorted(set(left.boundary)|set(right.boundary))),(*left.rules,*right.rules,*local_rules))
    except ValueError as e:
        reason=Reason.SINGLE_HEAD_CLOSURE_LOST if "single-head" in str(e) else Reason.INVALID_SCOPE
        t=Terminal.OPEN_LANGUAGE if reason is Reason.SINGLE_HEAD_CLOSURE_LOST else Terminal.INVALID_CERTIFICATE
        return Result(t,reason,None,cert("JOIN",t,reason,inputs,None,budget,0,{"error":str(e)}))
    work=left.rule_count+right.rule_count+m.rule_count+m.literal_count
    if work>budget.max_total_work: return over("JOIN",budget,inputs,work,{"scope_replay":True})
    if m.rule_count>budget.max_message_rules or m.literal_count>budget.max_message_literals:
        return Result(Terminal.OPEN_REPRESENTATION_GROWTH,Reason.PROJECTION_VOLUME,None,
                      cert("JOIN",Terminal.OPEN_REPRESENTATION_GROWTH,Reason.PROJECTION_VOLUME,inputs,None,budget,work,{"scope_replay":True}))
    return Result(Terminal.FACTOR_BUILT,Reason.NONE,m,cert("JOIN",Terminal.FACTOR_BUILT,Reason.NONE,inputs,m,budget,work,{"scope_replay":True}))

def project(source:Message,retained:Iterable[str],budget:Budget)->Result:
    keep=tuple(sorted({atom(x) for x in retained})); inputs=[source.digest]
    if not set(keep)<=set(source.scope): return bad("PROJECT",budget,Reason.INVALID_SCOPE)
    rules=list(source.rules); work=0; emitted=0
    for x in sorted(set(source.scope)-set(keep)):
        producer=next((r for r in rules if r.head==x),None)
        consumers=[r for r in rules if x in r.body]
        survivors=[r for r in rules if r.head!=x and x not in r.body]
        generated=[]
        if producer:
            for r in sorted(consumers):
                nr=normalize_rule(Rule(tuple(sorted((set(r.body)-{x})|set(producer.body))),r.head))
                work+=1+(0 if nr is None else nr.literals)
                if work>budget.max_total_work: return over("PROJECT",budget,inputs,work,{"eliminated":x})
                if nr is not None:
                    tentative=normalize_rules((*survivors,*generated,nr)); literals=sum(z.literals for z in tentative)
                    if len(tentative)>budget.max_message_rules or literals>budget.max_message_literals:
                        growth={"source_message_digest":source.digest,"eliminated_variables":[x],
                                "canonical_generation_order":"variable,consumer-rule-digest",
                                "first_over_budget_rule_digest":nr.digest,"emitted_before_stop":emitted,
                                "emitted_units":literals,"declared_size_bound":budget.max_message_literals,
                                "declared_rule_bound":budget.max_message_rules,"charged_work":work,"partial_factor":None}
                        return Result(Terminal.OPEN_REPRESENTATION_GROWTH,Reason.PROJECTION_VOLUME,None,
                            cert("PROJECT",Terminal.OPEN_REPRESENTATION_GROWTH,Reason.PROJECTION_VOLUME,inputs,None,budget,work,growth),growth)
                    generated.append(nr); emitted+=1
        try: rules=list(normalize_rules((*survivors,*generated)))
        except ValueError as e:
            return Result(Terminal.OPEN_LANGUAGE,Reason.SINGLE_HEAD_CLOSURE_LOST,None,
                          cert("PROJECT",Terminal.OPEN_LANGUAGE,Reason.SINGLE_HEAD_CLOSURE_LOST,inputs,None,budget,work,{"error":str(e)}))
    try: m=make_message(keep,tuple(x for x in source.boundary if x in keep),rules)
    except ValueError as e: return bad("PROJECT",budget,Reason.INVALID_RULE)
    return Result(Terminal.FACTOR_BUILT,Reason.NONE,m,
                  cert("PROJECT",Terminal.FACTOR_BUILT,Reason.NONE,inputs,m,budget,work,{"eliminated_variables":sorted(set(source.scope)-set(keep)),"exact_replay":True}))

def replay_operation(c:Mapping[str,Any])->bool:
    try:
        od=c["operation_digest"]; q=dict(c); q.pop("operation_digest")
        return SHA.fullmatch(od) is not None and od==h("OP",q) and c["capability_digest"]==cap_digest()
    except Exception: return False

def replay_project(source:Message,result:Result,retained:Iterable[str],budget:Budget)->bool:
    rerun=project(source,retained,budget)
    return canonical_json(rerun.operation_certificate)==canonical_json(result.operation_certificate) and rerun.growth_certificate==result.growth_certificate

def vtree_payload(n:VTreeNode)->dict[str,Any]:
    return {"node_id":n.node_id,"boundary":list(n.boundary),"variable":n.variable,
            "left":None if n.left is None else vtree_payload(n.left),"right":None if n.right is None else vtree_payload(n.right)}
def verify_vtree(root:VTreeNode,variables:set[str])->dict[str,set[str]]:
    ids:set[str]=set(); leaves:set[str]=set(); scopes:dict[str,set[str]]={}
    def visit(n:VTreeNode)->set[str]:
        if n.node_id in ids: raise ValueError("node id")
        ids.add(n.node_id)
        if n.leaf:
            if n.left or n.right or n.variable in leaves: raise ValueError("leaf")
            leaves.add(atom(n.variable)); s={n.variable}
        else:
            if n.left is None or n.right is None or n.variable is not None: raise ValueError("binary")
            a,b=visit(n.left),visit(n.right)
            if a&b: raise ValueError("overlap")
            s=a|b
        if not set(n.boundary)<=s: raise ValueError("boundary")
        scopes[n.node_id]=s; return s
    if visit(root)!=variables or leaves!=variables: raise ValueError("coverage")
    return scopes

def evaluate_supplied_vtree(formula_rules:Iterable[Rule|Mapping[str,Any]],root:VTreeNode,
                            rule_owners:Mapping[str,Iterable[Rule|Mapping[str,Any]]],budget:Budget)->EvaluationResult:
    try:
        formula=normalize_rules(formula_rules); vars={a for r in formula for a in (*r.body,*([] if r.head is None else [r.head]))}
        scopes=verify_vtree(root,vars)
        owned={k:normalize_rules(v) for k,v in rule_owners.items()}
        if set(owned)-set(scopes) or sorted(r.digest for rs in owned.values() for r in rs)!=sorted(r.digest for r in formula): raise ValueError("ownership")
    except ValueError:
        base={"schema":EVALUATION_SCHEMA,"canonical_id":CANONICAL_ID,"terminal":Terminal.INVALID_CERTIFICATE.value,
              "reason_code":Reason.INVALID_VTREE.value,"formula_digest":None,"vtree_digest":None,
              "capability_digest":cap_digest(),"language_profile_digest":h("CAPABILITY",LANGUAGE_PROFILE),"budget_digest":budget.digest,
              "max_message_size":0,"total_representation_size":0,"leaf_work":0,"join_work":0,"projection_work":0,
              "proof_bytes":0,"closed_nodes":0,"open_nodes":1,"first_open_node_digest":None,
              "first_open_terminal":Terminal.INVALID_CERTIFICATE.value,"first_open_reason_code":Reason.INVALID_VTREE.value,
              "root_message_digest":None}
        base["evaluation_certificate_digest"]=h("EVALUATION",base); return EvaluationResult(base)
    stats={"max_message_size":0,"total_representation_size":0,"leaf_work":0,"join_work":0,"projection_work":0,"proof_bytes":0,"closed_nodes":0}
    first:tuple[VTreeNode,Result]|None=None
    def walk(n:VTreeNode)->Message|None:
        nonlocal first
        if first: return None
        if n.leaf: r=leaf(owned.get(n.node_id,()),scopes[n.node_id],n.boundary,budget); stats["leaf_work"]+=r.operation_certificate["work_units"]
        else:
            lm,rm=walk(n.left),walk(n.right)
            if lm is None or rm is None:return None
            r=join(lm,rm,owned.get(n.node_id,()),scopes[n.node_id],budget); stats["join_work"]+=r.operation_certificate["work_units"]
        stats["proof_bytes"]+=len(canonical_json(r.operation_certificate))
        if r.output_message is None: first=(n,r); return None
        if set(r.output_message.scope)!=set(n.boundary):
            p=project(r.output_message,n.boundary,budget); stats["projection_work"]+=p.operation_certificate["work_units"]; stats["proof_bytes"]+=len(canonical_json(p.operation_certificate)); r=p
        if r.output_message is None: first=(n,r); return None
        m=r.output_message; stats["closed_nodes"]+=1; stats["max_message_size"]=max(stats["max_message_size"],m.literal_count); stats["total_representation_size"]+=m.literal_count
        return m
    root_message=walk(root)
    base={"schema":EVALUATION_SCHEMA,"canonical_id":CANONICAL_ID,
          "terminal":Terminal.FACTOR_BUILT.value if first is None else first[1].terminal.value,
          "reason_code":Reason.NONE.value if first is None else first[1].reason_code.value,
          "formula_digest":h("FORMULA",[r.payload() for r in formula]),"vtree_digest":h("VTREE",vtree_payload(root)),
          "capability_digest":cap_digest(),"language_profile_digest":h("CAPABILITY",LANGUAGE_PROFILE),"budget_digest":budget.digest,
          **stats,"open_nodes":0 if first is None else 1,
          "first_open_node_digest":None if first is None else h("VTREE",vtree_payload(first[0])),
          "first_open_terminal":None if first is None else first[1].terminal.value,
          "first_open_reason_code":None if first is None else first[1].reason_code.value,
          "root_message_digest":None if first is not None or root_message is None else root_message.digest}
    base["evaluation_certificate_digest"]=h("EVALUATION",base); return EvaluationResult(base)

def replay_evaluation(formula,root,owners,budget,certificate):
    return canonical_json(evaluate_supplied_vtree(formula,root,owners,budget).certificate)==canonical_json(certificate)

def fanout(n:int):
    b=tuple(f"b{i}" for i in range(n)); rules=(Rule(b,"x"),*(Rule(("x",),f"h{i}") for i in range(n)))
    scope=tuple(sorted((*b,"x",*(f"h{i}" for i in range(n))))); keep=tuple(x for x in scope if x!="x")
    return rules,scope,keep

def self_test()->dict[str,Any]:
    C:dict[str,bool]={}; big=Budget(1000,10000,100000)
    C["capability_boundary_frozen"]=HORN_LEAF_IMPLEMENTED and HORN_JOIN_IMPLEMENTED and HORN_PROJECT_IMPLEMENTED and not any((HORN_MERGE_IMPLEMENTED,HORN_SEPARATE_IMPLEMENTED,GENERAL_HORN_IMPLEMENTED,VTREE_DISCOVERY_IMPLEMENTED))
    a=make_message(("b","a"),("b",),[Rule(("a",),"b"),Rule((),"a")]); b=make_message(("a","b"),("b",),[Rule((),"a"),Rule(("a",),"b")]); C["message_digest_deterministic"]=a.digest==b.digest
    r=leaf([Rule((),"a"),Rule(("a",),"b")],("a","b"),("a","b"),big); C["leaf_native_replay"]=r.terminal is Terminal.FACTOR_BUILT and replay_operation(r.operation_certificate)
    C["join_scope_guarded"]=join(make_message(("a",),("a",),[]),make_message(("a",),("a",),[]),[],("a",),big).terminal is Terminal.INVALID_CERTIFICATE
    conflict=join(make_message(("a","c"),("a","c"),[Rule(("a",),"c")]),make_message(("b",),("b",),[]),[Rule(("b",),"c")],("a","b","c"),big); C["join_single_head_loss_is_open_language"]=conflict.terminal is Terminal.OPEN_LANGUAGE and conflict.reason_code is Reason.SINGLE_HEAD_CLOSURE_LOST
    src=make_message(("a","x","y"),("a","y"),[Rule(("a",),"x"),Rule(("x",),"y")]); p=project(src,("a","y"),big); C["project_exact_substitution"]=p.output_message==make_message(("a","y"),("a","y"),[Rule(("a",),"y")]) and replay_project(src,p,("a","y"),big)
    src=make_message(("x","y"),("y",),[Rule(("x",),"y")]); p=project(src,("y",),big); C["project_absent_producer_drops_consumers"]=p.output_message is not None and not p.output_message.rules
    counts={}
    for n in (4,8):
        rs,s,k=fanout(n); q=project(make_message(s,k,rs),k,big); counts[n]=(q.output_message.rule_count,q.output_message.literal_count)
    C["single_head_projection_stays_polynomial"]=counts=={4:(4,20),8:(8,72)}
    rs,s,k=fanout(8); source=make_message(s,k,rs); tight=Budget(1000,30,100000); g=project(source,k,tight)
    C["projection_growth_stops_fail_closed"]=g.terminal is Terminal.OPEN_REPRESENTATION_GROWTH and g.reason_code is Reason.PROJECTION_VOLUME and g.output_message is None and g.growth_certificate["partial_factor"] is None and g.growth_certificate["emitted_before_stop"]<8 and replay_project(source,g,k,tight)
    formula=(Rule((),"a"),Rule(("a",),"b")); tree=VTreeNode("root",(),left=VTreeNode("la",("a",),variable="a"),right=VTreeNode("lb",("b",),variable="b")); owners={"la":[Rule((),"a")],"root":[Rule(("a",),"b")]}
    e1=evaluate_supplied_vtree(formula,tree,owners,big); e2=evaluate_supplied_vtree(formula,tree,owners,big)
    C["supplied_vtree_evaluation_deterministic"]=e1.terminal is Terminal.FACTOR_BUILT and e1.root_message_digest is not None and e1.certificate["evaluation_certificate_digest"]==e2.certificate["evaluation_certificate_digest"] and replay_evaluation(formula,tree,owners,big,e1.certificate)
    oe=evaluate_supplied_vtree(formula,tree,owners,Budget(1,1,1)); C["open_evaluation_has_no_root_message"]=oe.terminal in {Terminal.OPEN_BUDGET,Terminal.OPEN_REPRESENTATION_GROWTH} and oe.root_message_digest is None
    badtree=VTreeNode("root",(),left=VTreeNode("same",("a",),variable="a"),right=VTreeNode("same",("b",),variable="b")); iv=evaluate_supplied_vtree(formula,badtree,owners,big); C["invalid_vtree_fail_closed"]=iv.terminal is Terminal.INVALID_CERTIFICATE and iv.root_message_digest is None
    try: canonical_json({"truth_table":[0,1]}); rejected=False
    except ValueError: rejected=True
    C["encoded_truth_tables_rejected"]=rejected
    assert all(C.values()),C
    return {"status":"PASS","canonical_id":CANONICAL_ID,"language_profile":LANGUAGE_PROFILE,"acceptance_checks":len(C),**C,"p_vs_np":"OPEN"}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    if args.self_test: print(json.dumps(self_test(),sort_keys=True,separators=(",",":"))); return 0
    ap.error("use --self-test"); return 2
if __name__=="__main__": raise SystemExit(main())
