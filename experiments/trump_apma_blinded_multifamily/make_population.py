from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json, random, hashlib

ROOT=Path(__file__).resolve().parent

def stable(s):return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],'big')
def vars_of(cnf):return sorted({abs(x) for c in cnf for x in c})
def maxvar(cnf):return max(vars_of(cnf),default=0)

def rename_shuffle(cnf,seed):
    rng=random.Random(seed); vs=vars_of(cnf); labels=list(range(10001,10001+len(vs)));rng.shuffle(labels);mp=dict(zip(vs,labels));out=[]
    for c in cnf:
        z=[mp[abs(x)] if x>0 else -mp[abs(x)] for x in c];rng.shuffle(z);out.append(z)
    rng.shuffle(out);return out

def split_to3_v1(cnf,start):
    nxt=start;out=[]
    def lift(c):
        nonlocal nxt
        if len(c)>=3:return [list(c)]
        if len(c)==2:
            z=nxt;nxt+=1;return [list(c)+[z],list(c)+[-z]]
        if len(c)==1:
            z=nxt;nxt+=1;return lift(list(c)+[z])+lift(list(c)+[-z])
        raise ValueError('empty source clause not allowed')
    for c in cnf:out.extend(lift(list(c)))
    return out,nxt

def equivalent_copy(cnf,seed,start,rate=4):
    rng=random.Random(seed);vs=vars_of(cnf);chosen=vs[::max(2,rate)];nxt=start;mp={}
    for v in chosen:mp[v]=nxt;nxt+=1
    out=[]
    for c in cnf:
        z=[]
        for lit in c:
            v=abs(lit); w=mp.get(v,v); z.append(w if lit>0 else -w)
        out.append(z)
    for v,w in mp.items():out.extend([[-v,w],[-w,v]])
    rng.shuffle(out);return out,nxt

def redundant_supersets(cnf,start,every=5,positive=True):
    out=[list(c) for c in cnf];nxt=start
    for i,c in enumerate(list(cnf)):
        if len(c)==3 and i%every==0:
            z=nxt;nxt+=1;out.append(list(c)+([z] if positive else [-z]))
    return out,nxt

def add_noise(cnf,seed,start):
    rng=random.Random(seed);out=[list(c) for c in cnf];nxt=start
    for _ in range(max(1,len(cnf)//20)):
        z=nxt;nxt+=1;out.append([z,-z])
    if out:
        for _ in range(min(7,max(1,len(out)//10))):out.append(list(rng.choice(out)))
    rng.shuffle(out)
    for c in out:rng.shuffle(c)
    return out,nxt

def surface_v1(base,seed):
    a=rename_shuffle(base,seed);start=maxvar(a)+100
    if seed%3==0:a,start=equivalent_copy(a,seed^0xA5A5,start,5)
    a,start=split_to3_v1(a,start)
    a,start=redundant_supersets(a,start,every=7,positive=bool(seed&1))
    a,start=add_noise(a,seed^0x55AA,start)
    return a

def surface_v2_holdout(base,seed):
    # Independently ordered equivalent encoder: copies first, then a separate iterative lift, then redundant supersets.
    a=rename_shuffle(base,seed^0xBAD5EED);start=maxvar(a)+211
    a,start=equivalent_copy(a,seed^0x112233,start,3)
    out=[];nxt=start
    for c0 in a:
        stack=[list(c0)]
        while stack:
            c=stack.pop()
            if len(c)>=3:out.append(c);continue
            z=nxt;nxt+=1;stack.append(c+[-z]);stack.append(c+[z])
    a=out
    a,nxt=redundant_supersets(a,nxt,every=4,positive=bool((seed>>1)&1))
    a,nxt=add_noise(a,seed^0x778899,nxt)
    return a

def graph_edges(m,n,seed,sat):
    rng=random.Random(seed)
    if sat:
        e={(u,u) for u in range(n)}
        for u in range(n):
            choices=[v for v in range(n) if v!=u];rng.shuffle(choices)
            for v in choices[:2]:e.add((u,v))
        return sorted(e)
    for _ in range(500):
        e=set()
        for u in range(m):
            choices=list(range(n));rng.shuffle(choices)
            for v in choices[:3]:e.add((u,v))
        if len({v for _,v in e})==n:return sorted(e)
    raise RuntimeError('edge generation')

def make_slot0(n,seed,sat):
    m=n if sat else n+1;e=graph_edges(m,n,seed,sat);L=defaultdict(list);R=defaultdict(list)
    for u,v in e:L[u].append(v);R[v].append(u)
    cnf=[];var=lambda u,v:1000*u+v+1
    for u in range(m):
        xs=[var(u,v) for v in sorted(L[u])];cnf.append(xs)
        for i,a in enumerate(xs):
            for b in xs[i+1:]:cnf.append([-a,-b])
    for v in range(n):
        xs=[var(u,v) for u in sorted(R[v])]
        for i,a in enumerate(xs):
            for b in xs[i+1:]:cnf.append([-a,-b])
    return cnf

def make_slot1(n,seed,sat):
    rng=random.Random(seed);vs=list(range(1,n+1));cnf=[]
    planted={v:bool(rng.getrandbits(1)) for v in vs}
    planted[1]=True; planted[2]=True
    cnf.append([-1,2])
    while len(cnf)<2*n:
        a,b=rng.sample(vs,2);sa=1 if rng.getrandbits(1) else -1;sb=1 if rng.getrandbits(1) else -1
        c=[sa*a,sb*b]
        if sat and not any(planted[abs(x)] if x>0 else not planted[abs(x)] for x in c):c[0]*=-1
        cnf.append(c)
    if not sat:
        cnf.extend([[1,2],[-1,-2],[-1,2],[1,-2]])
    else:
        cnf.extend([[1,2],[-1,2],[1,-2]])
    return cnf

def make_slot2(n,seed,sat):
    rng=random.Random(seed);path=list(range(1,n+1));rng.shuffle(path);u=n+1;cnf=[[path[0]],[path[1]]]
    for i in range(n-2):cnf.append([-path[i],-path[i+1],path[i+2]])
    for i in range(0,n-3,3):cnf.append([-path[i],-path[i+2],path[min(n-1,i+3)]])
    cnf.append([-path[-2],-path[-1]] if not sat else [-path[-1],-u])
    return cnf

def xor3_clause_set(scope,rhs):
    a,b,c=scope;out=[]
    for bits in range(8):
        p=((bits>>0)&1)^((bits>>1)&1)^((bits>>2)&1)
        if p==rhs:continue
        out.append([a if not(bits&1) else -a,b if not(bits&2) else -b,c if not(bits&4) else -c])
    return out

def make_slot3(n,seed,sat):
    if n%2:n+=1
    rng=random.Random(seed);x=list(range(1,n+1));z=n+1;rhs=[rng.getrandbits(1) for _ in range(n)]
    parity=0
    for b in rhs[:-1]:parity^=b
    rhs[-1]=parity if sat else parity^1
    cnf=[]
    for i in range(n):cnf.extend(xor3_clause_set((x[i],x[(i+1)%n],z),rhs[i]))
    return cnf

def near_collision_pair(k):
    # Same scopes and raw coarse statistics, different exact structural relations.
    x=list(range(1,k+1));z=k+1;left=[];right=[];nxt=100000
    for i in range(k):
        sc=(x[i],x[(i+1)%k],z);a,b,c=sc
        h=[[-a,-b,-c],[a,-b,-c],[-a,b,-c],[-a,-b,c]]
        l=xor3_clause_set(sc,0)
        left.extend(h);right.extend(l)
        # Three width-4 redundant supersets of the common all-negative clause.
        for _ in range(3):
            left.append([-a,-b,-c,nxt]);right.append([-a,-b,-c,-nxt]);nxt+=1
    return left,right

def out_of_library(seed,n=18):
    rng=random.Random(seed);out=[]
    for i in range(33):
        a,b,c=rng.sample(range(1,n+1),3);signs=[1,-1,1] if i%2==0 else [-1,1,1];rng.shuffle(signs);out.append([signs[0]*a,signs[1]*b,signs[2]*c])
    return out

def decoy(seed):
    b=make_slot0(8,seed,True);vs=vars_of(b);b.append([vs[0],-vs[1],vs[2]])
    return b

def coarse(cnf):
    deg=defaultdict(int);wh=defaultdict(int);pos=neg=0
    for c in cnf:
        wh[len(c)]+=1
        for x in c:
            deg[abs(x)]+=1
            if x>0:pos+=1
            else:neg+=1
    return {'n':len(deg),'m':len(cnf),'width_hist':sorted(wh.items()),'degree_multiset':sorted(deg.values()),'pos':pos,'neg':neg}

def main():
    hidden=[];truth=[];idx=0;sizes=[8,10,12,14]
    makers=[make_slot0,make_slot1,make_slot2,make_slot3]
    for slot,maker in enumerate(makers):
        for j in range(32):
            n=sizes[(j//8)%len(sizes)];sat=(j%2==0);seed=stable(f'slot{slot}:{j}:{n}')
            base=maker(n,seed,sat);holdout=(j>=24);raw=surface_v2_holdout(base,seed) if holdout else surface_v1(base,seed)
            cid=f'H{idx:04d}';idx+=1;hidden.append({'case_id':cid,'cnf':raw});truth.append({'case_id':cid,'expected_slot':slot,'truth':'SAT' if sat else 'UNSAT','kind':'HIDDEN','holdout':holdout,'size':n})
    for j in range(8):
        cid=f'H{idx:04d}';idx+=1;raw=surface_v1(out_of_library(stable(f'out{j}')),stable(f'outsurf{j}'));hidden.append({'case_id':cid,'cnf':raw});truth.append({'case_id':cid,'expected_slot':None,'truth':None,'kind':'OUT_OF_LIBRARY','holdout':False})
    for j in range(8):
        cid=f'H{idx:04d}';idx+=1;raw=surface_v1(decoy(stable(f'dec{j}')),stable(f'decsurf{j}'));hidden.append({'case_id':cid,'cnf':raw});truth.append({'case_id':cid,'expected_slot':None,'truth':None,'kind':'CARRIER_DECOY','holdout':False})
    collision=[]
    for k in [6,8,10,12]:
        a,b=near_collision_pair(k)
        for slot,raw0 in [(2,a),(3,b)]:
            seed=stable(f'collision:{k}:{slot}');raw=rename_shuffle(raw0,seed)
            cid=f'H{idx:04d}';idx+=1;hidden.append({'case_id':cid,'cnf':raw});truth.append({'case_id':cid,'expected_slot':slot,'truth':'SAT','kind':'STRUCTURAL_NEAR_COLLISION','holdout':True,'pair':k});collision.append((k,slot,cid,coarse(raw)))
    rng=random.Random(20260914);order=list(range(len(hidden)));rng.shuffle(order);hidden=[hidden[i] for i in order]
    (ROOT/'hidden_inputs.json').write_text(json.dumps({'cases':hidden},separators=(',',':')),encoding='utf-8')
    (ROOT/'hidden_truth.json').write_text(json.dumps({'truth':truth,'collision':collision},indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'cases':len(hidden),'hidden':128,'controls':len(hidden)-128,'collision':collision},sort_keys=True))
if __name__=='__main__':main()
