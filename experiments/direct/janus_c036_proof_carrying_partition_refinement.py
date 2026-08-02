#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random

Clause=tuple[int,...]
CNF=tuple[Clause,...]
Equation=tuple[int,int]  # bitmask, rhs


def canon_clause(c:Clause):
    s=set(c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))

def normalize(f:CNF)->CNF:
    cs=[]
    for c in f:
        q=canon_clause(c)
        if q is not None:cs.append(q)
    cs=sorted(set(cs),key=lambda c:(len(c),c))
    out=[]
    for c in cs:
        sc=set(c)
        if any(set(d)<=sc for d in out):continue
        out.append(c)
    return tuple(out)

def variables_horn(f:CNF):return sorted({abs(x) for c in f for x in c})
def eval_cnf(f:CNF,a:dict[int,bool]):return all(any(a.get(abs(x),False)==(x>0) for x in c) for c in f)
def is_horn(f:CNF):return all(sum(x>0 for x in c)<=1 for c in f)

def horn_solve(f:CNF):
    f=normalize(f)
    if not is_horn(f):return 'OPEN',None,[]
    vs=variables_horn(f);a={v:False for v in vs};trace=[]
    changed=True
    while changed:
        changed=False
        for i,c in enumerate(f):
            pos=[x for x in c if x>0];body=[-x for x in c if x<0]
            if all(a[v] for v in body):
                if not pos:return False,None,trace+[('conflict',i)]
                h=pos[0]
                if not a[h]:a[h]=True;trace.append(('set',h,i));changed=True
    return True,a,trace

def falsify_clause_units(c:Clause)->CNF:
    # To falsify x add -x; to falsify -x add x.
    return tuple(((-x if x>0 else -x),) for x in c)

def complete_assignment(a:dict[int,bool],n:int):return {i:a.get(i,False) for i in range(1,n+1)}

def horn_separator(f:CNF,g:CNF,n:int):
    f=normalize(f);g=normalize(g)
    if not is_horn(f) or not is_horn(g):return {'status':'OPEN'}
    checks=[]
    for direction,left,right in [('F_NOT_G',f,g),('G_NOT_F',g,f)]:
        for j,c in enumerate(right):
            trial=normalize(left+falsify_clause_units(c))
            sat,a,tr=horn_solve(trial)
            checks.append({'direction':direction,'clause':j,'sat':bool(sat)})
            if sat is True:
                a=complete_assignment(a,n)
                assert eval_cnf(left,a) and not eval_cnf(right,a)
                return {'status':'SEPARATED','language':'HORN','direction':direction,
                        'assignment':a,'target_clause':j,'trace':tr,'checks':checks}
    return {'status':'EQUIVALENT','language':'HORN','checks':checks}

def eval_affine(eqns:tuple[Equation,...],a:dict[int,bool]):
    for mask,rhs in eqns:
        z=0
        for i in range(1,max(2,mask.bit_length()+1)):
            if (mask>>(i-1))&1:z^=int(a.get(i,False))
        if z!=(rhs&1):return False
    return True

def gf2_solve(eqns:tuple[Equation,...],n:int):
    rows=[[m,r&1,1<<i] for i,(m,r) in enumerate(eqns)]
    rank=0;ops=[]
    for col in range(n-1,-1,-1):
        p=next((i for i in range(rank,len(rows)) if (rows[i][0]>>col)&1),None)
        if p is None:continue
        if p!=rank:rows[rank],rows[p]=rows[p],rows[rank];ops.append(('swap',rank,p))
        for i in range(len(rows)):
            if i!=rank and ((rows[i][0]>>col)&1):
                rows[i][0]^=rows[rank][0];rows[i][1]^=rows[rank][1];rows[i][2]^=rows[rank][2]
                ops.append(('xor',i,rank))
        rank+=1
    for m,r,prov in rows:
        if m==0 and r==1:return False,None,{'ops':ops,'contradiction_provenance':prov}
    a={i:False for i in range(1,n+1)}
    for m,r,_ in rows:
        if not m:continue
        p=m.bit_length()-1
        z=r
        for j in range(p):
            if (m>>j)&1:z^=int(a[j+1])
        a[p+1]=bool(z)
    assert eval_affine(eqns,a)
    return True,a,{'ops':ops}

def affine_separator(aeq:tuple[Equation,...],beq:tuple[Equation,...],n:int):
    checks=[]
    for direction,left,right in [('A_NOT_B',aeq,beq),('B_NOT_A',beq,aeq)]:
        for j,(m,r) in enumerate(right):
            sat,w,cert=gf2_solve(tuple(left)+((m,r^1),),n)
            checks.append({'direction':direction,'row':j,'sat':sat})
            if sat:
                assert eval_affine(left,w) and not eval_affine(right,w)
                return {'status':'SEPARATED','language':'AFFINE','direction':direction,
                        'assignment':w,'target_row':j,'solver_certificate':cert,'checks':checks}
    return {'status':'EQUIVALENT','language':'AFFINE','checks':checks}

def verify_separator(x,y,cert,n:int):
    if cert.get('status')!='SEPARATED':return False
    w={int(k):bool(v) for k,v in cert['assignment'].items()}
    if x['language']=='HORN' and y['language']=='HORN':
        ex,ey=eval_cnf(x['object'],w),eval_cnf(y['object'],w)
    elif x['language']=='AFFINE' and y['language']=='AFFINE':
        ex,ey=eval_affine(x['object'],w),eval_affine(y['object'],w)
    else:return False
    return ex!=ey

def extract(x,y,n:int):
    if x['language']!=y['language']:return {'status':'OPEN','reason':'NO_CROSS_LANGUAGE_EXTRACTOR'}
    if x['language']=='HORN':return horn_separator(x['object'],y['object'],n)
    if x['language']=='AFFINE':return affine_separator(x['object'],y['object'],n)
    return {'status':'OPEN','reason':'UNSUPPORTED_LANGUAGE'}

def refine(states:list[dict],n:int,budget:int):
    blocks=[list(range(len(states)))];splits=[];work=0
    changed=True
    while changed:
        changed=False;new=[]
        for block in blocks:
            if len(block)<=1:new.append(block);continue
            pivot=block[0];sep=None
            for q in block[1:]:
                work+=1
                if work>budget:return {'status':'OPEN','reason':'SEPARATOR_BUDGET','blocks':blocks,'splits':splits,'work':work}
                r=extract(states[pivot],states[q],n)
                if r['status']=='OPEN':return {'status':'OPEN','reason':r.get('reason'),'blocks':blocks,'splits':splits,'work':work}
                if r['status']=='SEPARATED':sep=r;break
            if sep is None:new.append(block);continue
            assert verify_separator(states[pivot],states[q],sep,n)
            w={int(k):bool(v) for k,v in sep['assignment'].items()}
            yes=[];no=[]
            for i in block:
                s=states[i]
                val=eval_cnf(s['object'],w) if s['language']=='HORN' else eval_affine(s['object'],w)
                (yes if val else no).append(i)
            assert yes and no
            new.extend([yes,no]);splits.append({'block':block,'separator':sep,'yes':yes,'no':no});changed=True
        blocks=new
    return {'status':'EXACT','blocks':blocks,'splits':splits,'work':work}

def truth_signature(state,n:int):
    out=[]
    for bits in itertools.product((False,True),repeat=n):
        w={i+1:bits[i] for i in range(n)}
        out.append(eval_cnf(state['object'],w) if state['language']=='HORN' else eval_affine(state['object'],w))
    return tuple(out)

def random_horn(rng,n,m):
    f=[]
    for _ in range(m):
        body=rng.sample(range(1,n+1),rng.randint(0,min(3,n)))
        remain=[v for v in range(1,n+1) if v not in body]
        head=rng.choice(remain) if remain and rng.getrandbits(1) else None
        c=tuple([-v for v in body]+([head] if head else []));f.append(c)
    return normalize(tuple(f))

def random_affine(rng,n,m):
    return tuple((rng.randrange(1,1<<n),rng.getrandbits(1)) for _ in range(m))

def run(seed=360036):
    rng=random.Random(seed);horn_cases=aff_cases=sep_ok=eq_ok=0
    for _ in range(400):
        n=rng.randint(1,7);f=random_horn(rng,n,rng.randint(0,8));g=random_horn(rng,n,rng.randint(0,8))
        r=horn_separator(f,g,n);same=truth_signature({'language':'HORN','object':f},n)==truth_signature({'language':'HORN','object':g},n)
        assert (r['status']=='EQUIVALENT')==same
        if r['status']=='SEPARATED':assert verify_separator({'language':'HORN','object':f},{'language':'HORN','object':g},r,n);sep_ok+=1
        else:eq_ok+=1
        horn_cases+=1
    for _ in range(400):
        n=rng.randint(1,8);a=random_affine(rng,n,rng.randint(0,7));b=random_affine(rng,n,rng.randint(0,7))
        r=affine_separator(a,b,n);same=truth_signature({'language':'AFFINE','object':a},n)==truth_signature({'language':'AFFINE','object':b},n)
        assert (r['status']=='EQUIVALENT')==same
        if r['status']=='SEPARATED':assert verify_separator({'language':'AFFINE','object':a},{'language':'AFFINE','object':b},r,n);sep_ok+=1
        else:eq_ok+=1
        aff_cases+=1
    # Easy family: many syntactic duplicates collapse to two semantic Horn classes.
    n=10;states=[]
    for k in range(1,65):
        states.append({'language':'HORN','object':normalize(tuple([(1,)]*k))})
        states.append({'language':'HORN','object':normalize(tuple([(-1,)]*k))})
    rr=refine(states,n,10000);assert rr['status']=='EXACT' and len(rr['blocks'])==2
    # Mixed Horn/affine class is refused without a cross-language separator theorem.
    mixed=refine([{'language':'HORN','object':((1,),)},{'language':'AFFINE','object':((1,1),)}],1,10)
    assert mixed['status']=='OPEN' and mixed['reason']=='NO_CROSS_LANGUAGE_EXTRACTOR'
    # Corrupt separator must fail.
    bad=horn_separator(((1,),),((-1,),),1);bad['assignment']={1:True}
    assert verify_separator({'language':'HORN','object':((1,),)},{'language':'HORN','object':((-1,),)},bad,1)
    bad['assignment']={1:False};assert not verify_separator({'language':'HORN','object':((1,),)},{'language':'HORN','object':((-1,),)},bad,1)
    out={'artifact_id':'C036-JANUS-PROOF-CARRYING-PARTITION-REFINEMENT','status':'PASS','p_vs_np':'OPEN','seed':seed,
         'horn_separator_cases':horn_cases,'affine_separator_cases':aff_cases,'verified_separators':sep_ok,'verified_equivalences':eq_ok,
         'easy_states':len(states),'easy_refined_blocks':len(rr['blocks']),'mixed_language_control':'OPEN',
         'theorem':'Horn and affine residual inequivalence admit deterministic polynomial-time explicit separator extraction; supplied finite same-language state sets can be refined only by replayable separators.',
         'new_gate':'CROSS_LANGUAGE_SYMBOLIC_SEPARATOR_DISCOVERY',
         'claim_boundary':'Restricted same-language refinement only; explicit state lists may already be exponential and no unrestricted residual SAT/equivalence oracle is used.'}
    out['integrity_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args();r=run();print(json.dumps(r,indent=2,sort_keys=True));assert not a.self_test or r['status']=='PASS'
if __name__=='__main__':main()
