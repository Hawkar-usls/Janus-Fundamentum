#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, random
from collections import defaultdict, deque

Clause=tuple[int,...]
CNF=tuple[Clause,...]
Graph=dict[str,set[str]]

def edge(g:Graph,a:str,b:str)->None:
    g.setdefault(a,set()).add(b);g.setdefault(b,set()).add(a)

def incidence(f:CNF)->Graph:
    g:Graph={}
    for i,c in enumerate(f):
        q=f'C:{i}';g.setdefault(q,set())
        for x in c: edge(g,f'X:{abs(x)}',q)
    return g

def split(f:CNF,rng:random.Random):
    g:Graph={};copies=defaultdict(list);occ={}
    for i,c in enumerate(f):
        q=f'C:{i}';g.setdefault(q,set())
        for j,x in enumerate(c):
            v=abs(x);u=f'V:{v}@{i}:{j}';occ[(i,j)]=u;copies[v].append(u);edge(g,q,u)
    bs={}
    for v,ls in sorted(copies.items()):
        b=set(ls);order=list(ls);rng.shuffle(order)
        for i in range(1,len(order)):
            p=order[rng.randrange(i)];u=order[i]
            for z in ('a','b'):
                e=f'EQ:{v}:{i}:{z}';edge(g,p,e);edge(g,u,e);b.add(e)
        bs[f'X:{v}']=b
    for i in range(len(f)):bs[f'C:{i}']={f'C:{i}'}
    return g,bs,occ

def conn(g:Graph,s:set[str])->bool:
    if not s:return False
    r=next(iter(s));seen={r};q=deque([r])
    while q:
        u=q.popleft()
        for v in g.get(u,()):
            if v in s and v not in seen:seen.add(v);q.append(v)
    return seen==s

def verify(src:Graph,tgt:Graph,bs:dict[str,set[str]]):
    if set(src)!=set(bs):return False,'domain'
    used=set()
    for u,b in bs.items():
        if not b:return False,f'empty:{u}'
        if used & b:return False,f'overlap:{u}'
        used|=b
        if not conn(tgt,b):return False,f'disconnected:{u}'
    for u in src:
        for v in src[u]:
            if u>=v:continue
            if not any(y in tgt.get(x,set()) for x in bs[u] for y in bs[v]):return False,f'missing:{u}:{v}'
    return True,'PASS'

def fixture(rng:random.Random,n:int,m:int)->CNF:
    out=[]
    for _ in range(m):
        vs=rng.sample(range(1,n+1),min(3,n));out.append(tuple(v if rng.getrandbits(1) else -v for v in vs))
    for v in range(1,n+1):
        if all(all(abs(x)!=v for x in c) for c in out):out[rng.randrange(m)]+= (v,)
    return tuple(out)

def run(seed=290031,cases=600):
    rng=random.Random(seed);sv=tv=0
    for _ in range(cases):
        f=fixture(rng,rng.randint(1,8),rng.randint(1,12));s=incidence(f);t,b,_=split(f,rng);ok,msg=verify(s,t,b);assert ok,msg;sv+=len(s);tv+=len(t)
    f=((1,2),(-1,2));s=incidence(f);t,b,_=split(f,random.Random(1));bad={u:set(v) for u,v in b.items()};bad['X:1']={x for x in bad['X:1'] if not x.startswith('EQ:1:')};ok,msg=verify(s,t,bad);assert not ok and msg.startswith('disconnected')
    r={'artifact_id':'C029-JANUS-CONNECTED-OCCURRENCE-SPLITTING-MINOR','status':'PASS','p_vs_np':'OPEN','theorem':'Connected variable-local occurrence splitting preserves the source incidence graph as a minor.','consequence':'Treewidth cannot decrease under this compiler pattern.','seed':seed,'certificates':cases,'source_vertices':sv,'target_vertices':tv,'negative_control':msg,'claim_boundary':'Blocks only copying plus connected equality gadgets; does not exclude semantic compression or prove P!=NP.'}
    r['integrity_sha256']=hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest();return r

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args();r=run();print(json.dumps(r,indent=2,sort_keys=True));assert not a.self_test or r['status']=='PASS'
if __name__=='__main__':main()
