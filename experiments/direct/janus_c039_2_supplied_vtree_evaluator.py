#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping
import janus_c039_1_horn_projection_boundary as horn

CID='C039.2'; PROFILE='SINGLE_HEAD_HORN_V1'; SCHEMA='janus.c039.2.supplied-vtree-evaluation.v1'
FORBIDDEN={'assignments','assignment_rows','communication_rows','evaluation_vector','row_matrix','truth_table','truth_table_blob','raw_bitmap','assignment_index','lookup_table'}
CAP={'leaf':True,'join':True,'project':True,'merge':True,'separate':True,'general_horn_poly_projection':False,'vtree_discovery':False}
Clause=horn.Clause
class T(str,Enum): BUILT='FACTOR_BUILT'; OPEN_LANG='OPEN_LANGUAGE'; OPEN_BUDGET='OPEN_BUDGET'; OPEN_GROWTH='OPEN_REPRESENTATION_GROWTH'; INVALID='INVALID_CERTIFICATE'
class R(str,Enum): NONE='NONE'; LOST='SINGLE_HEAD_CLOSURE_LOST'; VOLUME='PROJECTION_VOLUME'; WORK='WORK_BUDGET'; CERT='CERTIFICATE_VOLUME'; SCOPE='INVALID_SCOPE'; VTREE='INVALID_VTREE'
@dataclass(frozen=True)
class Budget:
    clauses:int; literals:int; work:int; cert_bytes:int
    @property
    def digest(self): return dg('BUDGET',self.__dict__)
@dataclass(frozen=True)
class Node:
    node_id:str; boundary:tuple[int,...]; variable:int|None=None; left:'Node|None'=None; right:'Node|None'=None
    @property
    def leaf(self): return self.variable is not None
@dataclass(frozen=True)
class Op:
    terminal:T; reason:R; message:tuple[Clause,...]|None; work:int; receipt:Mapping[str,Any]; growth:Mapping[str,Any]|None=None
@dataclass(frozen=True)
class Evaluation:
    certificate:Mapping[str,Any]
    @property
    def terminal(self): return T(self.certificate['terminal'])
    @property
    def root_message_digest(self): return self.certificate.get('root_message_digest')

def safe(x:Any)->Any:
    if x is None or isinstance(x,(str,bool,int)): return x
    if isinstance(x,float): raise TypeError('float')
    if isinstance(x,(list,tuple)): return [safe(v) for v in x]
    if isinstance(x,dict):
        out={}
        for k,v in x.items():
            k=str(k)
            if k.lower() in FORBIDDEN: raise ValueError('enumerative payload')
            out[k]=safe(v)
        return out
    raise TypeError('json')
def cj(x:Any)->bytes: return json.dumps(safe(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def dg(tag:str,x:Any)->str: return 'sha256:'+hashlib.sha256(b'JANUS-C039.2-'+tag.encode()+b'\0'+cj(x)).hexdigest()
def payload(f:Iterable[Clause]): return [[list(b),h] for b,h in horn.normalize(f)]
def md(f:Iterable[Clause]): return dg('MESSAGE',payload(f))
def lits(f:Iterable[Clause]): return sum(len(b)+(1 if h else 0) for b,h in horn.normalize(f))
def support(c:Clause): return set(c[0])|({c[1]} if c[1] else set())
def cap_digest(): return dg('CAPABILITY',{'schema':'janus.c039.2.capability.v1','profile':PROFILE,**CAP})
def receipt(op:str,t:T,r:R,inputs:list[str],msg,work:int,details:Mapping[str,Any]):
    q={'schema':'janus.c039.2.operation.v1','canonical_id':CID,'operator':op,'terminal':t.value,'reason_code':r.value,'capability_digest':cap_digest(),'input_message_digests':inputs,'output_message_digest':None if msg is None else md(msg),'work_units':work,'details':dict(details)}
    q['operation_digest']=dg('OP',q); return q
def replay_receipt(q):
    p=dict(q); d=p.pop('operation_digest',None); return q.get('capability_digest')==cap_digest() and d==dg('OP',p)
def result(op,t,r,inputs,msg,work,details,growth=None): return Op(t,r,msg,work,receipt(op,t,r,inputs,msg,work,details),growth)
def guard(op,msg,b,inputs,work):
    if work>b.work:return result(op,T.OPEN_BUDGET,R.WORK,inputs,None,work,{'bound':b.work})
    if len(msg)>b.clauses or lits(msg)>b.literals:
        g={'emitted_clauses':len(msg),'emitted_units':lits(msg),'declared_clause_bound':b.clauses,'declared_size_bound':b.literals,'charged_work':work,'partial_factor':None}
        return result(op,T.OPEN_GROWTH,R.VOLUME,inputs,None,work,g,g)
    return None

def leaf(rules:Iterable[Clause],scope:Iterable[int],b:Budget)->Op:
    f=horn.normalize(rules); s=set(scope)
    if any(not support(c)<=s for c in f): return result('LEAF',T.INVALID,R.SCOPE,[],None,0,{'scope':sorted(s)})
    if not horn.is_single_head(f): return result('LEAF',T.OPEN_LANG,R.LOST,[],None,0,{})
    try:
        m=horn.Meter(max(0,b.work),max(1,b.clauses),max(1,b.cert_bytes)); native=horn.horn_solve(f,{},m)
    except Exception as e:return result('LEAF',T.OPEN_BUDGET,R.WORK,[],None,getattr(m,'work',0),{'error':type(e).__name__})
    w=lits(f)+len(f)+m.work; g=guard('LEAF',f,b,[],w)
    return g or result('LEAF',T.BUILT,R.NONE,[],f,w,{'native_replay_digest':dg('NATIVE',native)})

def join(a,bmsg,local,ascope,bscope,outscope,b:Budget)->Op:
    A,B,O=set(ascope),set(bscope),set(outscope); inputs=[md(a),md(bmsg)]
    if A&B or O!=A|B:return result('JOIN',T.INVALID,R.SCOPE,inputs,None,0,{})
    f=horn.normalize((*a,*bmsg,*horn.normalize(local)))
    if any(not support(c)<=O for c in f):return result('JOIN',T.INVALID,R.SCOPE,inputs,None,0,{})
    if not horn.is_single_head(f):return result('JOIN',T.OPEN_LANG,R.LOST,inputs,None,len(f),{})
    w=lits(a)+lits(bmsg)+lits(f)+len(f); g=guard('JOIN',f,b,inputs,w)
    return g or result('JOIN',T.BUILT,R.NONE,inputs,f,w,{'scope_replay':True})

def project(source:Iterable[Clause],keep:Iterable[int],b:Budget)->Op:
    cur=list(horn.normalize(source)); keep=set(keep); inputs=[md(cur)]; work=emitted=0; eliminated=[]
    for x in sorted(set(horn.variables(cur))-keep):
        eliminated.append(x); prod=[c for c in cur if c[1]==x]
        if len(prod)>1:return result('PROJECT',T.OPEN_LANG,R.LOST,inputs,None,work,{'eliminated':eliminated})
        consumers=[c for c in cur if x in c[0]]; survivors=[c for c in cur if c[1]!=x and x not in c[0]]; generated=[]
        if prod:
            pb=set(prod[0][0])
            for c in sorted(consumers,key=lambda z:(z[1],len(z[0]),z[0])):
                nr=horn.clause((set(c[0])-{x})|pb,c[1]); work+=1+len(nr[0])+(1 if nr[1] else 0)
                tentative=horn.normalize((*survivors,*generated,nr))
                if work>b.work:return result('PROJECT',T.OPEN_BUDGET,R.WORK,inputs,None,work,{'eliminated':eliminated})
                if len(tentative)>b.clauses or lits(tentative)>b.literals:
                    g={'source_message_digest':inputs[0],'eliminated_variables':eliminated,'canonical_generation_order':'variable,consumer-clause','first_over_budget_rule_digest':dg('RULE',[list(nr[0]),nr[1]]),'emitted_before_stop':emitted,'emitted_units':lits(tentative),'declared_size_bound':b.literals,'declared_clause_bound':b.clauses,'charged_work':work,'partial_factor':None}
                    return result('PROJECT',T.OPEN_GROWTH,R.VOLUME,inputs,None,work,g,g)
                if nr in tentative: generated.append(nr); emitted+=1
        cur=list(horn.normalize((*survivors,*generated)))
        if not horn.is_single_head(cur):return result('PROJECT',T.OPEN_LANG,R.LOST,inputs,None,work,{'eliminated':eliminated})
    f=horn.normalize(cur); g=guard('PROJECT',f,b,inputs,work)
    return g or result('PROJECT',T.BUILT,R.NONE,inputs,f,work,{'eliminated_variables':eliminated,'exact_replay':True})
def replay_project(src,keep,b,res):
    q=project(src,keep,b); return cj(q.receipt)==cj(res.receipt) and q.growth==res.growth

def node_payload(n:Node): return {'node_id':n.node_id,'boundary':list(n.boundary),'variable':n.variable,'left':None if n.left is None else node_payload(n.left),'right':None if n.right is None else node_payload(n.right)}
def verify_tree(root:Node,vars:set[int]):
    ids=set(); leaves=set(); scopes={}
    def walk(n):
        if not n.node_id or n.node_id in ids:raise ValueError('id')
        ids.add(n.node_id)
        if tuple(sorted(set(n.boundary)))!=n.boundary:raise ValueError('boundary')
        if n.leaf:
            if n.left or n.right or n.variable in leaves:raise ValueError('leaf')
            leaves.add(n.variable); s={n.variable}
        else:
            if n.variable is not None or n.left is None or n.right is None:raise ValueError('binary')
            a,c=walk(n.left),walk(n.right)
            if a&c:raise ValueError('overlap')
            s=a|c
        if not set(n.boundary)<=s:raise ValueError('containment')
        scopes[n.node_id]=s; return s
    if walk(root)!=vars or leaves!=vars:raise ValueError('coverage')
    return scopes
def invalid(b):
    q={'schema':SCHEMA,'canonical_id':CID,'terminal':T.INVALID.value,'reason_code':R.VTREE.value,'formula_digest':None,'vtree_digest':None,'capability_digest':cap_digest(),'language_profile_digest':dg('LANG',PROFILE),'budget_digest':b.digest,'max_message_size':0,'total_representation_size':0,'leaf_work':0,'join_work':0,'projection_work':0,'proof_bytes':0,'closed_nodes':0,'open_nodes':1,'first_open_node_digest':None,'first_open_terminal':T.INVALID.value,'first_open_reason_code':R.VTREE.value,'root_message_digest':None}
    q['evaluation_certificate_digest']=dg('EVAL',q); return Evaluation(q)
def evaluate_supplied_vtree(formula,root,owners:Mapping[str,Iterable[Clause]],b:Budget):
    try:
        f=horn.normalize(formula); vs=set(horn.variables(f))
        if not vs or not horn.is_single_head(f):raise ValueError('language')
        scopes=verify_tree(root,vs); own={k:horn.normalize(v) for k,v in owners.items()}
        flat=[c for z in own.values() for c in z]
        if set(own)-set(scopes) or horn.normalize(flat)!=f or len(flat)!=len(f):raise ValueError('ownership')
        if any(not support(c)<=scopes[k] for k,z in own.items() for c in z):raise ValueError('scope')
    except Exception:return invalid(b)
    st={'max_message_size':0,'total_representation_size':0,'leaf_work':0,'join_work':0,'projection_work':0,'proof_bytes':0,'closed_nodes':0}; first=None
    def remain():return Budget(b.clauses,b.literals,max(0,b.work-st['leaf_work']-st['join_work']-st['projection_work']),b.cert_bytes)
    def acct(o,key):st[key]+=o.work;st['proof_bytes']+=len(cj(o.receipt))
    def walk(n):
        nonlocal first
        if first:return None
        if n.leaf:o=leaf(own.get(n.node_id,()),scopes[n.node_id],remain());acct(o,'leaf_work')
        else:
            lm,rm=walk(n.left),walk(n.right)
            if lm is None or rm is None:return None
            o=join(lm,rm,own.get(n.node_id,()),scopes[n.left.node_id],scopes[n.right.node_id],scopes[n.node_id],remain());acct(o,'join_work')
        if o.message is None:first=(n,o);return None
        p=project(o.message,n.boundary,remain());acct(p,'projection_work')
        if p.message is None:first=(n,p);return None
        size=lits(p.message);st['max_message_size']=max(st['max_message_size'],size);st['total_representation_size']+=size;st['closed_nodes']+=1;return p.message
    rootmsg=walk(root)
    q={'schema':SCHEMA,'canonical_id':CID,'terminal':T.BUILT.value if first is None else first[1].terminal.value,'reason_code':R.NONE.value if first is None else first[1].reason.value,'formula_digest':dg('FORMULA',payload(f)),'vtree_digest':dg('VTREE',node_payload(root)),'capability_digest':cap_digest(),'language_profile_digest':dg('LANG',PROFILE),'budget_digest':b.digest,**st,'open_nodes':0 if first is None else 1,'first_open_node_digest':None if first is None else dg('NODE',node_payload(first[0])),'first_open_terminal':None if first is None else first[1].terminal.value,'first_open_reason_code':None if first is None else first[1].reason.value,'root_message_digest':None if first or rootmsg is None else md(rootmsg)}
    q['evaluation_certificate_digest']=dg('EVAL',q)
    if len(cj(q))>b.cert_bytes:q.update(terminal=T.OPEN_BUDGET.value,reason_code=R.CERT.value,open_nodes=1,first_open_terminal=T.OPEN_BUDGET.value,first_open_reason_code=R.CERT.value,root_message_digest=None);q['evaluation_certificate_digest']=dg('EVAL',q)
    return Evaluation(q)
def replay_evaluation(f,t,o,b,c):return cj(evaluate_supplied_vtree(f,t,o,b).certificate)==cj(c)
def fanout(n):
    body=tuple(range(1,n+1));x=1000;rules=[horn.clause(body,x),*(horn.clause((x,),2000+i) for i in range(n))];keep=tuple(sorted((*body,*(2000+i for i in range(n)))));return horn.normalize(rules),keep

def self_test():
    C={};big=Budget(1000,10000,1000000,10000000)
    C['capability_boundary_frozen']=all(CAP[k] for k in ('leaf','join','project','merge','separate')) and not CAP['general_horn_poly_projection'] and not CAP['vtree_discovery']
    a=horn.normalize((horn.clause((1,),2),horn.clause((),1)));b=horn.normalize((horn.clause((),1),horn.clause((1,),2)));C['message_digest_deterministic']=md(a)==md(b)
    l=leaf(a,(1,2),big);C['leaf_native_replay']=l.terminal is T.BUILT and replay_receipt(l.receipt)
    C['join_scope_guarded']=join((),(),(),(1,),(1,),(1,),big).terminal is T.INVALID
    x=join((horn.clause((1,),3),),(horn.clause((2,),3),),(),(1,3),(2,),(1,2,3),big);C['join_single_head_loss_is_open_language']=x.terminal is T.OPEN_LANG and x.reason is R.LOST
    s=horn.normalize((horn.clause((1,),2),horn.clause((2,),3)));p=project(s,(1,3),big);C['project_exact_substitution']=p.message==horn.normalize((horn.clause((1,),3),)) and replay_project(s,(1,3),big,p)
    C['project_absent_producer_drops_consumers']=project((horn.clause((2,),3),),(3,),big).message==()
    counts={n:(len((q:=project(*fanout(n),big)).message),lits(q.message)) for n in (4,8)};C['single_head_projection_stays_polynomial']=counts=={4:(4,20),8:(8,72)}
    rules,keep=fanout(8);g=project(rules,keep,Budget(3,30,100000,1000000));C['projection_growth_stops_fail_closed']=g.terminal is T.OPEN_GROWTH and g.reason is R.VOLUME and g.message is None and g.growth['partial_factor'] is None and g.growth['emitted_before_stop']<8
    f=horn.normalize((horn.clause((),1),horn.clause((1,),2)));tree=Node('root',(),left=Node('l1',(1,),variable=1),right=Node('l2',(2,),variable=2));owners={'l1':(horn.clause((),1),),'root':(horn.clause((1,),2),)}
    e1=evaluate_supplied_vtree(f,tree,owners,big);e2=evaluate_supplied_vtree(f,tree,owners,big);C['supplied_vtree_evaluation_deterministic']=e1.terminal is T.BUILT and e1.root_message_digest is not None and e1.certificate['evaluation_certificate_digest']==e2.certificate['evaluation_certificate_digest'] and replay_evaluation(f,tree,owners,big,e1.certificate)
    oe=evaluate_supplied_vtree(f,tree,owners,Budget(1,1,0,1000000));C['open_evaluation_has_no_root_message']=oe.terminal in {T.OPEN_BUDGET,T.OPEN_GROWTH} and oe.root_message_digest is None
    bad=Node('root',(),left=Node('same',(1,),variable=1),right=Node('same',(2,),variable=2));iv=evaluate_supplied_vtree(f,bad,owners,big);C['invalid_vtree_fail_closed']=iv.terminal is T.INVALID and iv.root_message_digest is None
    try:cj({'truth_table':[0,1]});reject=False
    except ValueError:reject=True
    C['encoded_truth_tables_rejected']=reject
    assert len(C)==13 and all(C.values()),C
    return {'status':'PASS','canonical_id':CID,'language_profile':PROFILE,'acceptance_checks':len(C),**C,'p_vs_np':'OPEN'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');a=ap.parse_args()
    if a.self_test:print(json.dumps(self_test(),sort_keys=True,separators=(',',':')));return 0
    ap.error('use --self-test')
if __name__=='__main__':raise SystemExit(main())
