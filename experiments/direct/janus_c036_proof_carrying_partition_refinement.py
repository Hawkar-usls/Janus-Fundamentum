#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random
Clause=tuple[int,...];CNF=tuple[Clause,...];Equation=tuple[int,int]

def norm(f:CNF)->CNF:
    out=[]
    for c in f:
        s=set(c)
        if any(-x in s for x in s):continue
        q=tuple(sorted(s,key=lambda x:(abs(x),x<0)))
        if q not in out:out.append(q)
    out.sort(key=lambda c:(len(c),c));keep=[]
    for c in out:
        if not any(set(d)<=set(c) for d in keep):keep.append(c)
    return tuple(keep)
def horn(f):return all(sum(x>0 for x in c)<=1 for c in f)
def eval_cnf(f,a):return all(any(a.get(abs(x),False)==(x>0) for x in c) for c in f)
def hsolve(f,n):
    f=norm(f)
    if not horn(f):return 'OPEN',None,[]
    a={i:False for i in range(1,n+1)};tr=[];change=True
    while change:
        change=False
        for j,c in enumerate(f):
            pos=[x for x in c if x>0];body=[-x for x in c if x<0]
            if all(a[v] for v in body):
                if not pos:return False,None,tr+[('conflict',j)]
                if not a[pos[0]]:a[pos[0]]=True;tr.append(('set',pos[0],j));change=True
    return True,a,tr
def falsify(c):return tuple((-x,) for x in c)
def hsep(f,g,n):
    f=norm(f);g=norm(g)
    if not horn(f) or not horn(g):return {'status':'OPEN'}
    checks=[]
    for direction,left,right in [('F_NOT_G',f,g),('G_NOT_F',g,f)]:
        for j,c in enumerate(right):
            sat,a,tr=hsolve(left+falsify(c),n);checks.append((direction,j,sat is True))
            if sat is True:
                assert eval_cnf(left,a) and not eval_cnf(right,a)
                return {'status':'SEPARATED','language':'HORN','direction':direction,'assignment':a,'target_clause':j,'trace':tr,'checks':checks}
    return {'status':'EQUIVALENT','language':'HORN','checks':checks}
def eval_aff(eq,a):
    for m,r in eq:
        z=0
        for i in range(1,m.bit_length()+1):
            if (m>>(i-1))&1:z^=int(a.get(i,False))
        if z!=(r&1):return False
    return True
def asolve(eq,n):
    rows=[[m,r&1,1<<i] for i,(m,r) in enumerate(eq)];rank=0;ops=[]
    for col in range(n-1,-1,-1):
        p=next((i for i in range(rank,len(rows)) if (rows[i][0]>>col)&1),None)
        if p is None:continue
        if p!=rank:rows[rank],rows[p]=rows[p],rows[rank];ops.append(('swap',rank,p))
        for i in range(len(rows)):
            if i!=rank and ((rows[i][0]>>col)&1):
                rows[i][0]^=rows[rank][0];rows[i][1]^=rows[rank][1];rows[i][2]^=rows[rank][2];ops.append(('xor',i,rank))
        rank+=1
    for m,r,p in rows:
        if not m and r:return False,None,{'ops':ops,'contradiction_provenance':p}
    a={i:False for i in range(1,n+1)}
    for m,r,_ in rows:
        if not m:continue
        p=m.bit_length()-1;z=r
        for j in range(p):
            if (m>>j)&1:z^=int(a[j+1])
        a[p+1]=bool(z)
    assert eval_aff(eq,a);return True,a,{'ops':ops}
def asep(a,b,n):
    checks=[]
    for direction,left,right in [('A_NOT_B',a,b),('B_NOT_A',b,a)]:
        for j,(m,r) in enumerate(right):
            sat,w,cert=asolve(tuple(left)+((m,r^1),),n);checks.append((direction,j,sat))
            if sat:
                assert eval_aff(left,w) and not eval_aff(right,w)
                return {'status':'SEPARATED','language':'AFFINE','direction':direction,'assignment':w,'target_row':j,'solver_certificate':cert,'checks':checks}
    return {'status':'EQUIVALENT','language':'AFFINE','checks':checks}
def verify(x,y,c):
    if c.get('status')!='SEPARATED' or x['language']!=y['language']:return False
    w={int(k):bool(v) for k,v in c['assignment'].items()}
    if x['language']=='HORN':return eval_cnf(x['object'],w)!=eval_cnf(y['object'],w)
    if x['language']=='AFFINE':return eval_aff(x['object'],w)!=eval_aff(y['object'],w)
    return False
def extract(x,y,n):
    if x['language']!=y['language']:return {'status':'OPEN','reason':'NO_CROSS_LANGUAGE_EXTRACTOR'}
    return hsep(x['object'],y['object'],n) if x['language']=='HORN' else asep(x['object'],y['object'],n) if x['language']=='AFFINE' else {'status':'OPEN','reason':'UNSUPPORTED_LANGUAGE'}
def value(s,w):return eval_cnf(s['object'],w) if s['language']=='HORN' else eval_aff(s['object'],w)
def refine(states,n,budget):
    blocks=[list(range(len(states)))];splits=[];work=0;changed=True
    while changed:
        changed=False;new=[]
        for block in blocks:
            if len(block)<2:new.append(block);continue
            p=block[0];sep=None;q=None
            for q0 in block[1:]:
                work+=1
                if work>budget:return {'status':'OPEN','reason':'SEPARATOR_BUDGET','blocks':blocks,'splits':splits,'work':work}
                r=extract(states[p],states[q0],n)
                if r['status']=='OPEN':return {'status':'OPEN','reason':r['reason'],'blocks':blocks,'splits':splits,'work':work}
                if r['status']=='SEPARATED':sep=r;q=q0;break
            if sep is None:new.append(block);continue
            assert verify(states[p],states[q],sep);w={int(k):bool(v) for k,v in sep['assignment'].items()};yes=[];no=[]
            for i in block:(yes if value(states[i],w) else no).append(i)
            assert yes and no;new.extend((yes,no));splits.append({'separator':sep,'yes':yes,'no':no});changed=True
        blocks=new
    return {'status':'EXACT','blocks':blocks,'splits':splits,'work':work}
def sig(s,n):
    return tuple(value(s,{i+1:b[i] for i in range(n)}) for b in itertools.product((False,True),repeat=n))
def rh(r,n,m):
    f=[]
    for _ in range(m):
        body=r.sample(range(1,n+1),r.randint(0,min(3,n)));rest=[x for x in range(1,n+1) if x not in body];head=r.choice(rest) if rest and r.getrandbits(1) else None
        f.append(tuple([-x for x in body]+([head] if head else [])))
    return norm(tuple(f))
def ra(r,n,m):return tuple((r.randrange(1,1<<n),r.getrandbits(1)) for _ in range(m))
def run(seed=360036):
    r=random.Random(seed);sep=eq=0
    for language in ('HORN','AFFINE'):
        for _ in range(400):
            n=r.randint(1,7 if language=='HORN' else 8)
            x=rh(r,n,r.randint(0,8)) if language=='HORN' else ra(r,n,r.randint(0,7));y=rh(r,n,r.randint(0,8)) if language=='HORN' else ra(r,n,r.randint(0,7))
            sx={'language':language,'object':x};sy={'language':language,'object':y};z=extract(sx,sy,n);same=sig(sx,n)==sig(sy,n)
            assert (z['status']=='EQUIVALENT')==same
            if same:eq+=1
            else:assert verify(sx,sy,z);sep+=1
    states=[]
    for k in range(1,65):states += [{'language':'HORN','object':norm(tuple([(1,)]*k))},{'language':'HORN','object':norm(tuple([(-1,)]*k))}]
    rr=refine(states,10,10000);assert rr['status']=='EXACT' and len(rr['blocks'])==2
    mixed=refine([{'language':'HORN','object':((1,),)},{'language':'AFFINE','object':((1,1),)}],1,10);assert mixed['status']=='OPEN'
    x={'language':'HORN','object':((1,),)};y={'language':'HORN','object':((1,2),)};bad=hsep(x['object'],y['object'],2);assert verify(x,y,bad)
    bad['assignment']={1:True,2:False};assert not verify(x,y,bad)
    out={'artifact_id':'C036-JANUS-PROOF-CARRYING-PARTITION-REFINEMENT','status':'PASS','p_vs_np':'OPEN','seed':seed,'horn_separator_cases':400,'affine_separator_cases':400,'verified_separators':sep,'verified_equivalences':eq,'easy_states':128,'easy_refined_blocks':2,'mixed_language_control':'OPEN','corrupt_separator_control':'REJECTED','theorem':'Horn and affine residual inequivalence admit deterministic polynomial-time explicit separator extraction; explicit same-language state sets can be refined only by replayable separators.','new_gate':'CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY','claim_boundary':'Restricted same-language refinement only; explicit state lists may already be exponential.'}
    out['integrity_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();return out
def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args();r=run();print(json.dumps(r,indent=2,sort_keys=True));assert not a.self_test or r['status']=='PASS'
if __name__=='__main__':main()
