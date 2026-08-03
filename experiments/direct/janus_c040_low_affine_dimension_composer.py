#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random
from typing import Any
from c039_affine_core import Equation, Row, Meter, project_rows, solve_rows, evaluate_equation, xor_original_equations

Clause=tuple[int,...]
CNF=tuple[Clause,...]

def cj(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(x:Any)->str:return hashlib.sha256(cj(x).encode()).hexdigest()
def cvars(f:CNF)->set[int]:return {abs(x) for c in f for x in c}
def avars(a:tuple[Equation,...])->set[int]:
    return {v for e in a for v in e.support()}

def norm(f:CNF)->CNF:
    cs=[]
    for c in f:
        s=set(c)
        if any(-x in s for x in s):continue
        q=tuple(sorted(s,key=lambda x:(abs(x),x<0)))
        if q not in cs:cs.append(q)
    cs.sort(key=lambda c:(len(c),c));out=[]
    for c in cs:
        if not any(set(d)<=set(c) for d in out):out.append(c)
    return tuple(out)

def horn(f:CNF)->bool:return all(sum(x>0 for x in c)<=1 for c in f)
def dual_horn(f:CNF)->bool:return all(sum(x<0 for x in c)<=1 for c in f)
def eval_cnf(f:CNF,w:dict[int,bool])->bool:
    return all(any(w.get(abs(x),False)==(x>0) for x in c) for c in f)
def eval_aff(a:tuple[Equation,...],w:dict[int,bool])->bool:
    return all(evaluate_equation(e,w) for e in a)

def dual_transform(f:CNF,a:tuple[Equation,...])->tuple[CNF,tuple[Equation,...]]:
    return norm(tuple(tuple(-x for x in c) for c in f)),tuple(
        Equation(e.mask,e.rhs^(e.mask.bit_count()&1)) for e in a)

def hsolve(f:CNF,n:int,fixed:dict[int,bool])->dict[str,Any]:
    f=norm(f+tuple((v,) if b else (-v,) for v,b in sorted(fixed.items())))
    if not horn(f):return {'status':'OPEN_LANGUAGE'}
    w={i:False for i in range(1,n+1)};tr=[];change=True
    while change:
        change=False
        for j,c in enumerate(f):
            pos=[x for x in c if x>0];body=[-x for x in c if x<0]
            if all(w[v] for v in body):
                if not pos:return {'status':'UNSAT','trace':tr+[{'op':'conflict','clause':j}]}
                if not w[pos[0]]:
                    w[pos[0]]=True;tr.append({'op':'set','var':pos[0],'clause':j});change=True
    assert eval_cnf(f,w)
    return {'status':'SAT','assignment':{str(v):w[v] for v in range(1,n+1)},'trace':tr}

def basis(rows:list[Row],vs:tuple[int,...])->dict[str,Any]:
    piv={((r.mask&-r.mask).bit_length()):r for r in rows}
    free=[v for v in vs if v not in piv]
    def sol(g:dict[int,bool])->dict[int,bool]:
        w={v:g.get(v,False) for v in vs}
        for p in sorted(piv,reverse=True):
            r=piv[p];z=r.rhs;rest=r.mask^(1<<(p-1))
            while rest:
                b=rest&-rest;z^=int(w[b.bit_length()]);rest^=b
            w[p]=bool(z)
        return w
    p=sol({});vec=[]
    for v in free:
        q=sol({v:True});vec.append({x:p[x]^q[x] for x in vs})
    return {'dimension':len(free),'free_vars':free,'particular':p,'vectors':vec}

def enum_basis(b:dict[str,Any],vs:tuple[int,...]):
    for bits in itertools.product((0,1),repeat=b['dimension']):
        w=dict(b['particular'])
        for bit,vec in zip(bits,b['vectors']):
            if bit:
                for v in vs:w[v]^=vec[v]
        yield bits,w

def length(f:CNF,a:tuple[Equation,...],n:int)->int:
    return max(2,n+len(f)+sum(map(len,f))+len(a)+sum(e.mask.bit_count() for e in a))
def rows(a:tuple[Equation,...])->list[Row]:
    return [Row(e.mask,e.rhs,1<<i) for i,e in enumerate(a)]

def compose(f:CNF,a:tuple[Equation,...],q:int=1,limit:int=1_000_000)->dict[str,Any]:
    f=norm(f);orig_f,orig_a=f,a;dual=False
    if horn(f):lang='HORN'
    elif dual_horn(f):lang='DUAL_HORN';dual=True;f,a=dual_transform(f,a)
    else:return {'schema':'janus.c040.low_affine_dimension.v1','status':'OPEN_LANGUAGE','p_vs_np':'OPEN'}
    n=max(cvars(f)|avars(a),default=0);allv=tuple(range(1,n+1));shared=tuple(sorted(cvars(f)&avars(a)))
    L=length(f,a,n);budget=min(limit,L**q)
    meter=Meter(max(10000,L**(q+3)),max(1000,L**(q+1)),max(10000,L**(q+3)))
    pr,contr=project_rows(rows(a),shared,allv,meter)
    if contr:
        assert xor_original_equations(contr.provenance,a)==(0,1)
        z={'schema':'janus.c040.low_affine_dimension.v1','status':'UNSAT',
           'reason':'AFFINE_CONTRADICTION','language':lang,'dual':dual,
           'shared':list(shared),'provenance':contr.provenance,'q':q,'L':L,
           'budget':budget,'p_vs_np':'OPEN'}
        z['integrity_sha256']=sha(z);return z
    b=basis(pr,shared);need=1<<b['dimension']
    if need>budget:return {'schema':'janus.c040.low_affine_dimension.v1',
        'status':'OPEN_DIMENSION_BUDGET','language':lang,'dual':dual,
        'shared':list(shared),'dimension':b['dimension'],'states_needed':need,
        'q':q,'L':L,'budget':budget,'p_vs_np':'OPEN'}
    rec=[]
    for bits,s in enum_basis(b,shared):
        aw=solve_rows(rows(a),allv,s,meter);assert aw is not None
        hr=hsolve(f,n,s)
        rec.append({'parameters':list(bits),'shared':{str(v):s[v] for v in shared},
                    'affine':{str(v):aw[v] for v in avars(a)},'horn':hr})
        if hr['status']=='SAT':
            hw={int(v):x for v,x in hr['assignment'].items() if int(v) in cvars(f)}
            ww=dict(aw);ww.update(hw);orig={v:(not x if dual else x) for v,x in ww.items()}
            assert eval_cnf(orig_f,orig) and eval_aff(orig_a,orig)
            z={'schema':'janus.c040.low_affine_dimension.v1','status':'SAT',
               'language':lang,'dual':dual,'shared':list(shared),
               'projected_rows':[{'mask':r.mask,'rhs':r.rhs,'provenance':r.provenance} for r in pr],
               'basis':{'dimension':b['dimension'],'free_vars':b['free_vars'],
                        'particular':{str(v):x for v,x in b['particular'].items()},
                        'vectors':[{str(v):x for v,x in t.items()} for t in b['vectors']]},
               'records':rec,'witness':{str(v):orig.get(v,False) for v in allv},
               'states_examined':len(rec),'states_needed':need,'q':q,'L':L,'budget':budget,
               'cost':{'work':meter.work,'row_xors':meter.row_xors,'projection_calls':meter.projection_calls,
                       'solve_calls':meter.solve_calls},'p_vs_np':'OPEN'}
            z['integrity_sha256']=sha(z);return z
    z={'schema':'janus.c040.low_affine_dimension.v1','status':'UNSAT',
       'reason':'ALL_PROJECTED_STATES_HORN_REFUTED','language':lang,'dual':dual,
       'shared':list(shared),'projected_rows':[{'mask':r.mask,'rhs':r.rhs,'provenance':r.provenance} for r in pr],
       'basis':{'dimension':b['dimension'],'free_vars':b['free_vars'],
                'particular':{str(v):x for v,x in b['particular'].items()},
                'vectors':[{str(v):x for v,x in t.items()} for t in b['vectors']]},
       'records':rec,'states_examined':len(rec),'states_needed':need,'q':q,'L':L,'budget':budget,
       'cost':{'work':meter.work,'row_xors':meter.row_xors,'projection_calls':meter.projection_calls,
               'solve_calls':meter.solve_calls},'p_vs_np':'OPEN'}
    z['integrity_sha256']=sha(z);return z

def verify(f:CNF,a:tuple[Equation,...],z:dict[str,Any])->bool:
    if z['status'].startswith('OPEN'):
        return compose(f,a,z.get('q',1),z.get('budget',1_000_000))['status']==z['status']
    q=z.get('q',1);b=z.get('budget',1_000_000)
    return compose(f,a,q,max(1,b))==z

def brute(f:CNF,a:tuple[Equation,...])->bool:
    n=max(cvars(f)|avars(a),default=0)
    for bits in itertools.product((False,True),repeat=n):
        w={i+1:bits[i] for i in range(n)}
        if eval_cnf(f,w) and eval_aff(a,w):return True
    return False

def rh(r:random.Random,n:int,m:int)->CNF:
    out=[]
    for _ in range(m):
        vs=r.sample(range(1,n+1),r.randint(0,min(4,n)));head=r.choice(vs) if vs and r.random()<.65 else None
        out.append(tuple(v if v==head else -v for v in vs))
    return norm(tuple(out))
def rd(r:random.Random,n:int,m:int)->CNF:return norm(tuple(tuple(-x for x in c) for c in rh(r,n,m)))
def ra(r:random.Random,n:int,m:int)->tuple[Equation,...]:
    return tuple(Equation(r.randrange(1,1<<n),r.getrandbits(1)) for _ in range(m))

def dense(n:int):
    return norm(tuple((i,j) for i in range(1,n+1) for j in range(i+1,n+1))),tuple(
        Equation((1<<(0))|(1<<(i-1)),0) for i in range(2,n+1))
def line_obstruction(n:int):
    p={i:bool(i&1) for i in range(1,n+1)}
    f=norm((tuple(-i for i in p if p[i]),tuple(-i for i in p if not p[i])))
    a=tuple(Equation(1|(1<<(i-1)),int(p[1]^p[i])) for i in range(2,n+1))
    return f,a
def hard_image(n:int):
    src=[(i,-(i%n+1),(i+1)%n+1) for i in range(1,n+1)];f=[]
    for c in src:
        false=[n+abs(x) if x>0 else abs(x) for x in c];f.append(tuple(-v for v in false))
    return norm(tuple(f)),tuple(Equation((1<<(i-1))|(1<<(n+i-1)),1) for i in range(1,n+1))

def pairwise_full(f:CNF,n:int)->bool:
    ms=[{i+1:b[i] for i in range(n)} for b in itertools.product((False,True),repeat=n)
        if eval_cnf(f,{i+1:b[i] for i in range(n)})]
    if any(len({w[v] for w in ms})<2 for v in range(1,n+1)):return False
    full={(0,0),(0,1),(1,0),(1,1)}
    return all({(int(w[x]),int(w[y])) for w in ms}==full
               for x in range(1,n+1) for y in range(x+1,n+1))

def audit(seed:int=400040)->dict[str,Any]:
    r=random.Random(seed);mis=wf=vf=sat=unsat=op=0
    for i in range(500):
        n=r.randint(1,8);f=(rh if i%2==0 else rd)(r,n,r.randint(0,10));a=ra(r,n,r.randint(0,7))
        z=compose(f,a,3,4096);truth=brute(f,a)
        if z['status'].startswith('OPEN'):op+=1;continue
        if (z['status']=='SAT')!=truth:mis+=1
        if z['status']=='SAT':
            sat+=1;w={int(v):x for v,x in z['witness'].items()}
            if not(eval_cnf(f,w) and eval_aff(a,w)):wf+=1
        else:unsat+=1
        if not verify(f,a,z):vf+=1
    f,a=dense(80);d=compose(f,a,1);assert d['status']=='SAT' and d['basis']['dimension']==1 and verify(f,a,d)
    of,oa=line_obstruction(10);o=compose(of,oa,1);assert o['status']=='UNSAT' and o['basis']['dimension']==1 and pairwise_full(of,10) and verify(of,oa,o)
    hf,ha=hard_image(24);h=compose(hf,ha,1);assert h['status']=='OPEN_DIMENSION_BUDGET' and h['dimension']==24
    bad=compose(((1,2,3),(-1,-2,-3)),(),1);assert bad['status']=='OPEN_LANGUAGE'
    corrupt=json.loads(json.dumps(o));corrupt['records'][0]['shared']['1']=not corrupt['records'][0]['shared']['1'];assert not verify(of,oa,corrupt)
    z={'artifact_id':'C040-JANUS-LOW-AFFINE-DIMENSION-HORN-COMPOSER','status':'PASS','p_vs_np':'OPEN',
       'seed':seed,'random_cases':500,'random_sat':sat,'random_unsat':unsat,'random_open':op,
       'mismatches':mis,'witness_failures':wf,'verification_failures':vf,
       'theorem':'Horn/dual-Horn plus affine is decidable with replayable evidence in O(2^d poly(L)), d the affine projection dimension on shared variables.',
       'dense_control':{'shared':80,'dimension':d['basis']['dimension'],'states_examined':d['states_examined'],'status':d['status']},
       'pairwise_fact_obstruction':{'variables':10,'dimension':o['basis']['dimension'],'states_examined':o['states_examined'],'pairwise_projections':'FULL','status':o['status']},
       'nand3_neq':{'variables':24,'dimension':h['dimension'],'status':h['status']},
       'corrupt_certificate':'REJECTED','new_gate':'CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION'}
    z['integrity_sha256']=sha(z);return z

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--output');p.add_argument('--seed',type=int,default=400040);x=p.parse_args()
    z=audit(x.seed)
    if x.output:
        with open(x.output,'w',encoding='utf-8') as f:json.dump(z,f,indent=2,sort_keys=True)
    print(json.dumps(z,indent=2,sort_keys=True))
    if x.self_test:assert z['status']=='PASS' and z['mismatches']==z['witness_failures']==z['verification_failures']==0
if __name__=='__main__':main()
