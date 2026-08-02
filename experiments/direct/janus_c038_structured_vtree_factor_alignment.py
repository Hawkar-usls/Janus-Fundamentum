#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random
from dataclasses import dataclass

Clause=tuple[int,...]; CNF=tuple[Clause,...]; VTree=int|tuple['VTree','VTree']

def norm(f:CNF)->CNF:
    out=[]
    for c in f:
        s=set(c)
        if any(-x in s for x in s): continue
        q=tuple(sorted(s,key=lambda x:(abs(x),x<0)))
        if q not in out: out.append(q)
    out.sort(key=lambda c:(len(c),c)); keep=[]
    for c in out:
        if not any(set(d)<=set(c) for d in keep): keep.append(c)
    return tuple(keep)

def vars_of(f:CNF): return sorted({abs(x) for c in f for x in c})
def eval_cnf(f:CNF,a:dict[int,bool])->bool:
    return all(any(a[abs(l)]==(l>0) for l in c) for c in f)
def leaves(t:VTree)->tuple[int,...]:
    return (t,) if isinstance(t,int) else leaves(t[0])+leaves(t[1])
def nodes(t:VTree):
    yield t
    if not isinstance(t,int):
        yield from nodes(t[0]); yield from nodes(t[1])
def balanced(vs:list[int])->VTree:
    if len(vs)==1:return vs[0]
    k=len(vs)//2; return (balanced(vs[:k]),balanced(vs[k:]))
def blocked_eq_vtree(n:int)->VTree:return (balanced(list(range(1,n+1))),balanced(list(range(n+1,2*n+1))))
def paired_eq_vtree(n:int)->VTree:return balanced([(i,n+i) for i in range(1,n+1)])

def clause_weight(f:CNF,a:set[int],b:set[int])->int:
    return sum(bool(a & {abs(x) for x in c}) and bool(b & {abs(x) for x in c}) for c in f)
def greedy_vtree(f:CNF)->VTree:
    clusters=[(v,{v}) for v in vars_of(f)]
    if not clusters: raise ValueError('empty variable set')
    while len(clusters)>1:
        best=None
        for i in range(len(clusters)):
            for j in range(i+1,len(clusters)):
                w=clause_weight(f,clusters[i][1],clusters[j][1])
                key=(-w,len(clusters[i][1]|clusters[j][1]),min(clusters[i][1]|clusters[j][1]),i,j)
                if best is None or key<best[0]:best=(key,i,j)
        _,i,j=best; a,sa=clusters[i];b,sb=clusters[j]
        clusters=[x for k,x in enumerate(clusters) if k not in (i,j)] + [((a,b),sa|sb)]
    return clusters[0][0]

@dataclass
class Budget:
    limit:int; work:int=0
    def charge(self,n=1):
        self.work+=n
        if self.work>self.limit: raise RuntimeError('BUDGET')

def cut_rows(f:CNF,inside:tuple[int,...],allvars:tuple[int,...],budget:Budget):
    outside=tuple(v for v in allvars if v not in set(inside)); rows={}; reps={}
    outs=list(itertools.product((False,True),repeat=len(outside))); budget.charge(len(outs))
    for ib in itertools.product((False,True),repeat=len(inside)):
        ia=dict(zip(inside,ib)); vec=[]
        for ob in outs:
            budget.charge(); a=ia|dict(zip(outside,ob)); vec.append(eval_cnf(f,a))
        v=tuple(vec); rows[ib]=v; reps.setdefault(v,ib)
    seps=[]; vals=list(reps)
    for i in range(len(vals)):
        for j in range(i+1,len(vals)):
            budget.charge(); p=next(k for k,(x,y) in enumerate(zip(vals[i],vals[j])) if x!=y)
            seps.append({'row_a':reps[vals[i]],'row_b':reps[vals[j]],'outside_assignment':outs[p],'value_a':vals[i][p],'value_b':vals[j][p]})
    return {'inside':inside,'outside':outside,'assignments':2**len(inside),'classes':len(reps),'separators':seps}

def compile_vtree(f:CNF,t:VTree,budget_limit:int):
    f=norm(f); av=tuple(vars_of(f));
    if set(leaves(t))!=set(av) or len(leaves(t))!=len(av):return {'status':'INVALID_VTREE'}
    b=Budget(budget_limit); cuts=[]
    try:
        for node in nodes(t):
            if isinstance(node,int):continue
            cuts.append(cut_rows(f,tuple(sorted(leaves(node))),av,b))
        witness=None
        for bits in itertools.product((False,True),repeat=len(av)):
            b.charge(); a=dict(zip(av,bits))
            if eval_cnf(f,a): witness=a;break
    except RuntimeError:
        return {'status':'OPEN','reason':'EXPLICIT_QUOTIENT_BUDGET','work':b.work,'completed_cuts':len(cuts),'max_classes':max([x['classes'] for x in cuts],default=0)}
    return {'status':'EXACT','work':b.work,'cuts':cuts,'max_classes':max([x['classes'] for x in cuts],default=1),'sat':witness is not None,'witness':witness,'unsat_certificate':None if witness else {'kind':'EXHAUSTIVE_VTREE_TABLE','assignments':2**len(av)}}

def eq_cnf(n:int)->CNF:
    return tuple(c for i in range(1,n+1) for c in ((-i,n+i),(i,-(n+i))))
def random_3cnf(r,n,m):
    return tuple(tuple(v if r.getrandbits(1) else -v for v in r.sample(range(1,n+1),3)) for _ in range(m))
def verify_separators(f:CNF,record):
    allv=tuple(vars_of(f))
    for c in record.get('cuts',[]):
        ins=c['inside'];out=c['outside']
        for s in c['separators']:
            a=dict(zip(ins,s['row_a']))|dict(zip(out,s['outside_assignment']))
            b=dict(zip(ins,s['row_b']))|dict(zip(out,s['outside_assignment']))
            if eval_cnf(f,a)==eval_cnf(f,b):return False
    return True

def run(seed=380038):
    eq=[]
    for n in range(2,9):
        f=eq_cnf(n); good=compile_vtree(f,paired_eq_vtree(n),20_000_000); bad=compile_vtree(f,blocked_eq_vtree(n),20_000_000); heur=compile_vtree(f,greedy_vtree(f),20_000_000)
        assert good['status']==bad['status']==heur['status']=='EXACT'; assert verify_separators(f,good) and verify_separators(f,bad)
        assert good['sat'] and eval_cnf(f,good['witness']); assert bad['max_classes']>=2**n
        eq.append({'n':n,'paired_max_classes':good['max_classes'],'blocked_max_classes':bad['max_classes'],'greedy_max_classes':heur['max_classes'],'greedy_vtree':greedy_vtree(f)})
    open_control=compile_vtree(eq_cnf(12),blocked_eq_vtree(12),250_000)
    assert open_control['status']=='OPEN'
    r=random.Random(seed); pressure=[]; exact=0;opened=0
    for _ in range(120):
        n=r.randint(4,9);f=random_3cnf(r,n,r.randint(n,3*n));t=greedy_vtree(f);z=compile_vtree(f,t,350_000)
        if z['status']=='EXACT':
            exact+=1;assert verify_separators(f,z)
            if z['sat']:assert eval_cnf(f,z['witness'])
            pressure.append(z['max_classes'])
        else:opened+=1
    out={'artifact_id':'C038-JANUS-STRUCTURED-VTREE-FACTOR-ALIGNMENT','status':'PASS','p_vs_np':'OPEN','seed':seed,'theorem':'For a supplied vtree, exact cut continuation rows, replayable separating assignments, SAT witnesses and exhaustive UNSAT tables are constructible in time polynomial in the explicitly enumerated table volume. The row count is an exact communication/factor-width quantity, not a new universal width parameter.','equality_order_control':eq,'blocked_n12_control':open_control,'random_3cnf_cases':120,'random_exact':exact,'random_open':opened,'random_max_classes':max(pressure,default=0),'new_gate':'POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION','claim_boundary':'The compiler is exact but enumerative. A supplied or greedily found vtree is not evidence that arbitrary CNF has polynomial factor width; budget exhaustion returns OPEN.'}
    out['integrity_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':'),default=list).encode()).hexdigest();return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args();z=run();print(json.dumps(z,indent=2,sort_keys=True,default=list));assert not a.self_test or z['status']=='PASS'
if __name__=='__main__':main()
