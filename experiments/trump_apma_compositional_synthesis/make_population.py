from __future__ import annotations
from collections import defaultdict
from itertools import product
from pathlib import Path
import hashlib, json, random
ROOT=Path(__file__).resolve().parent

def parity_clause(vs,bits):
    return [(-v if b else v) for v,b in zip(vs,bits)]

def encode_relation(n,sat,seed):
    rng=random.Random(seed);m=n if sat else n+1;edges=set()
    if sat:
        edges|={(u,u) for u in range(n)}
    for u in range(m):
        cand=list(range(n));rng.shuffle(cand)
        for v in cand[:3]:edges.add((u,v))
    L=defaultdict(list);R=defaultdict(list)
    for u,v in sorted(edges):L[u].append(v);R[v].append(u)
    cnf=[];var={}
    k=1
    for u,v in sorted(edges):var[(u,v)]=k;k+=1
    for u in range(m):
        xs=[var[(u,v)] for v in sorted(L[u])];cnf.append(xs)
        for i,a in enumerate(xs):
            for b in xs[i+1:]:cnf.append([-a,-b])
    for v in range(n):
        xs=[var[(u,v)] for u in sorted(R[v])]
        for i,a in enumerate(xs):
            for b in xs[i+1:]:cnf.append([-a,-b])
    return cnf

def encode_binary(n,sat,seed):
    rng=random.Random(seed);cnf=[]
    if sat:
        planted={v:bool(rng.getrandbits(1)) for v in range(1,n+1)}
        while len(cnf)<2*n+4:
            a,b=rng.sample(range(1,n+1),2);sa=1 if rng.getrandbits(1) else -1;sb=1 if rng.getrandbits(1) else -1
            clause=[sa*a,sb*b]
            if any((x>0 and planted[abs(x)]) or (x<0 and not planted[abs(x)]) for x in clause):cnf.append(clause)
    else:
        cnf=[[ -1,2],[1,-2],[1,2],[-1,-2]]
        planted={v:bool(rng.getrandbits(1)) for v in range(1,n+1)}
        while len(cnf)<2*n+4:
            a,b=rng.sample(range(1,n+1),2);sa=1 if rng.getrandbits(1) else -1;sb=1 if rng.getrandbits(1) else -1
            clause=[sa*a,sb*b]
            if any((x>0 and planted[abs(x)]) or (x<0 and not planted[abs(x)]) for x in clause):cnf.append(clause)
    return cnf

def encode_forward(n,sat,seed):
    cnf=[[1],[2]]
    for i in range(3,n):cnf.append([-1,-(i-1),i])
    cnf.append([-n,-(n-1)] if sat else [-1,-(n-1)])
    return cnf

def eq_clauses(vs,rhs):
    out=[]
    for bits in product([0,1],repeat=len(vs)):
        if (sum(bits)&1)!=rhs:out.append(parity_clause(vs,bits))
    return out

def eq_clauses_hold(vs,rhs):
    bad=[bits for bits in product([1,0],repeat=len(vs)) if (sum(bits)&1)!=rhs]
    return [list(reversed(parity_clause(list(reversed(vs)),tuple(reversed(bits))))) for bits in bad]

def encode_rows(n,sat,seed,hold=False):
    rng=random.Random(seed);pl={v:int(rng.getrandbits(1)) for v in range(1,n+1)}
    b1=pl[1]^pl[2]^pl[3];b2=pl[1]^pl[2]^pl[4];b3=b1^b2
    rows=[((1,2,3),b1),((1,2,4),b2),((3,4),b3 if sat else 1-b3)]
    for i in range(5,n+1):rows.append(((1,i-1,i),pl[1]^pl[i-1]^pl[i]))
    enc=eq_clauses_hold if hold else eq_clauses;cnf=[]
    for vs,b in rows:cnf.extend(enc(list(vs),b))
    return cnf

def transport(cnf,seed,mode):
    rng=random.Random(seed);vs=sorted({abs(x) for c in cnf for x in c})
    if mode=='hold':
        new=[700000+13*i for i in range(len(vs),0,-1)]
    elif mode=='adm':
        new=[400000+17*i for i in range(1,len(vs)+1)];rng.shuffle(new)
    else:
        new=[100000+19*i for i in range(1,len(vs)+1)];rng.shuffle(new)
    mp=dict(zip(vs,new));out=[]
    for c in cnf:
        z=[mp[abs(x)] if x>0 else -mp[abs(x)] for x in c];rng.shuffle(z);out.append(z)
    rng.shuffle(out)
    if out:
        out.extend([list(out[i%len(out)]) for i in range(2 if mode=='cal' else 3)])
    if vs:
        z=max(new)+101;out.append([z,-z])
    if mode=='hold':out=list(reversed(out))
    return out

def metrics(cnf):
    real=[c for c in cnf if not any(-x in c for x in c)]
    vs=sorted({abs(x) for c in real for x in c});deg=defaultdict(int);wh=defaultdict(int);pos=neg=0
    for c in real:
        wh[len(c)]+=1
        for x in c:deg[abs(x)]+=1;pos+=x>0;neg+=x<0
    return {'n':len(vs),'m':len(real),'width_hist':sorted(wh.items()),'degree_multiset':sorted(deg.values()),'pos':pos,'neg':neg}

def collision(cnf):
    out=[list(c) for c in cnf]
    for i,a in enumerate(out):
        if any(-z in a for z in a):continue
        for ia,x in enumerate(a):
            if x<=0 or -x in a:continue
            for j,b in enumerate(out):
                if j==i:continue
                if any(-z in b for z in b):continue
                for ib,y in enumerate(b):
                    if y>=0 or -y in b:continue
                    aa=list(a);bb=list(b);aa[ia]=-x;bb[ib]=-y
                    if len(set(map(abs,aa)))==len(aa) and len(set(map(abs,bb)))==len(bb):
                        out[i]=aa;out[j]=bb;return out
    return out

def make(slot,n,sat,seed,mode):
    if slot==0:base=encode_relation(n,sat,seed)
    elif slot==1:base=encode_binary(n,sat,seed)
    elif slot==2:base=encode_forward(n,sat,seed)
    else:base=encode_rows(n,sat,seed,hold=(mode=='hold'))
    return transport(base,seed+991,mode)

def build():
    folds={};truth={};admission={};holdout={};controls={};counter=0
    names=['relation_resource','binary_reachability','forward_closure','local_linear_rows']
    for slot,fold in enumerate('ABCD'):
        cal=[];adm=[];hol=[];ctl=[]
        for split,count,start in [('cal',12,5),('adm',12,11),('hold',16,23)]:
            for j in range(count):
                sat=(j%2==0);n=start+(j//2);seed=10000*slot+1000*({'cal':1,'adm':2,'hold':3}[split])+j
                cnf=make(slot,n,sat,seed,split);cid=f'{fold}-{split}-{j:02d}'
                rec={'id':cid,'cnf':cnf,'encoder':f'{split}_encoder_v{1 if split=="cal" else 2 if split=="adm" else 3}','n_parameter':n}
                if split=='cal':rec['truth']='SAT' if sat else 'UNSAT';cal.append(rec)
                elif split=='adm':adm.append(rec)
                else:hol.append(rec)
                truth[cid]={'fold':fold,'slot':slot,'truth':'SAT' if sat else 'UNSAT','split':split,'semantic_family':names[slot]}
        for j in range(4):
            source=hol[j];bad=collision(source['cnf']);cid=f'{fold}-control-collision-{j:02d}'
            ctl.append({'id':cid,'cnf':bad,'control':'near_collision','source_id':source['id'],'source_metrics':metrics(source['cnf']),'control_metrics':metrics(bad)})
            truth[cid]={'fold':fold,'slot':slot,'truth':None,'split':'control','semantic_family':'out_of_family_or_exact_if_admitted'}
        for j in range(4):
            rng=random.Random(90000+slot*100+j);n=12+j;cnf=[]
            for _ in range(2*n):
                xs=rng.sample(range(1,n+1),3);cnf.append([(1 if rng.getrandbits(1) else -1)*x for x in xs])
            cnf=transport(cnf,91000+slot*100+j,'hold');cid=f'{fold}-control-random-{j:02d}'
            ctl.append({'id':cid,'cnf':cnf,'control':'out_of_family'})
            truth[cid]={'fold':fold,'slot':slot,'truth':None,'split':'control','semantic_family':'out_of_family'}
        folds[fold]=cal;admission[fold]=adm;holdout[fold]=hol;controls[fold]=ctl
    return folds,admission,holdout,controls,truth

if __name__=='__main__':
    cal,adm,hol,ctl,truth=build()
    (ROOT/'calibration.json').write_text(json.dumps({'folds':cal},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_admission.json').write_text(json.dumps({'folds':adm},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_holdout.json').write_text(json.dumps({'folds':hol},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_controls.json').write_text(json.dumps({'folds':ctl},indent=2,sort_keys=True),encoding='utf-8')
    (ROOT/'sealed_truth.json').write_text(json.dumps(truth,indent=2,sort_keys=True),encoding='utf-8')
    report={'calibration':sum(len(x) for x in cal.values()),'admission':sum(len(x) for x in adm.values()),'holdout':sum(len(x) for x in hol.values()),'controls':sum(len(x) for x in ctl.values()),'collision_metric_equal':[]}
    for f in 'ABCD':
        for c in ctl[f]:
            if c['control']=='near_collision':report['collision_metric_equal'].append([c['id'],c['source_metrics']==c['control_metrics']])
    print(json.dumps(report,sort_keys=True))

